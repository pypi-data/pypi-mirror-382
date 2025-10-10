#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2024-2025 EMBL - European Bioinformatics Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
from collections import Counter, defaultdict
import gzip
import re
import os
import logging
import json
import time
import numpy as np

from mgnify_pipelines_toolkit.constants.thresholds import (
    MIN_OVERLAP,
    MIN_SEQ_COUNT,
    MAX_ERROR_PROPORTION,
)
from mgnify_pipelines_toolkit.constants.var_region_coordinates import (
    REGIONS_16S_BACTERIA,
    REGIONS_16S_ARCHAEA,
    REGIONS_18S,
)

raw_f_regex = re.compile(
    r"([A-z0-9\.\-\:]+)\s+-\s+(\w+)\s+(\w+)\s+(\w+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([-+])\s+([-+])\s+(\d+)\s+(\d+[\.\d]*)\s+(\d+[\.\d]*)\s+(\d+[\.\d]*)\s+(.+)\s!\s+.*"  # noqa: E501
)

logging.basicConfig(level=logging.DEBUG)


def calc_overlap(read, reg):
    read_s, read_f = read
    reg_s, reg_f = reg
    overlap = max(min(read_f, reg_f) - max(read_s, reg_s), 0)
    total = max(reg_f - reg_s, 0)
    try:
        return overlap / total
    except ZeroDivisionError:
        return 0


def get_multiregion(raw_sequence_coords, regions):
    """Identify which variable regions were amplified.

    Args:
        raw_sequence_coords: Match coordinates.
        regions: Variable region coordinates.

    Returns:
        amplified_region: Amplified variable regions.
        region_coverages: Coverage of all detected variable regions

    """

    region_coverages = defaultdict(float)

    for region, limits in regions.items():
        overlap = calc_overlap(raw_sequence_coords, limits)
        region_coverages[region] = overlap

    # check if any of the coords are inside the region
    matched_regions = [
        region
        for region, limits in regions.items()
        if calc_overlap(raw_sequence_coords, limits) >= MIN_OVERLAP
    ]
    if len(matched_regions) > 1:
        amplified_region = "{}-{}".format(min(matched_regions), max(matched_regions))
    elif len(matched_regions) == 1:
        amplified_region = matched_regions[0]
    else:
        amplified_region = ""
    return amplified_region, region_coverages


def check_primer_position(raw_sequence_coords, regions):
    """Checks if the sequence starts and/or ends inside a variable region.

    Args:
        raw_sequence_coords: Match coordinates.

    Returns:
        True or False.

    """
    result_flag = False
    margin = 10  # allowed margin of error
    for coord in raw_sequence_coords:
        for region in regions.values():
            if coord in range(region[0] + margin, region[1] - margin):
                result_flag = True
    return result_flag


# Parse, filter empty lines and unpack into 2D array
def load_data(filename):
    read_function = gzip.open if filename.endswith(".gz") else open
    with read_function(filename, "rt") as f:
        return [l[0] for l in [raw_f_regex.findall(l) for l in f] if bool(l)]


def unsplit_region(long_region):
    interval = [int(var_reg.replace("V", "")) for var_reg in long_region.split("-")]
    if len(interval) == 1:
        interval = interval * 2
    return interval


def check_inclusiveness(more_frequent, less_frequent):
    unsplit_more_frequent, unsplit_less_frequent = [
        unsplit_region(region) for region in [more_frequent, less_frequent]
    ]
    return (
        unsplit_more_frequent[0] <= unsplit_less_frequent[0]
        and unsplit_more_frequent[1] >= unsplit_less_frequent[1]
    )


def normalise_results(region_matches):
    """Calculate region frequencies and output all regions that pass the threshold.

    Args:
        region_matches: List of regions matched by the amplicons in a file.

    Returns:
        Filtered dictionary where key = region, value = proportion of amplicons that map to the region.

    """
    counter = Counter(region_matches)
    logging.debug(counter)

    var_region_proportions = [
        # [region, round(count / len(region_matches), 4)]
        [region, count / len(region_matches)]
        for region, count in counter.items()
        if count / len(region_matches) >= MAX_ERROR_PROPORTION and region != ""
    ]
    # sort by frequency in reverse order
    var_region_proportions = sorted(
        var_region_proportions, key=lambda x: x[1], reverse=True
    )

    if len(var_region_proportions) == 1:
        return dict(var_region_proportions)
    elif len(var_region_proportions) == 2:
        more_frequent = var_region_proportions[0]
        less_frequent = var_region_proportions[1]
        if check_inclusiveness(more_frequent[0], less_frequent[0]):
            if less_frequent[1] < 0.04:
                return {more_frequent[0]: more_frequent[1]}
            else:
                return None
        else:
            if min(
                more_frequent[1], less_frequent[1]
            ) > 0.1 and not check_inclusiveness(less_frequent[0], more_frequent[0]):
                return dict(var_region_proportions)
            else:
                return None
    else:
        return None


def identify_run(infile_name):
    """
    Args:
        infile_name: The name of the tblout file.
    Return:
        run: Run ID ERR*|SRR*
    """
    run = os.path.basename(infile_name).split("_")[0]
    return run


def determine_cm(cm_detected):
    """Returns the coordinates of variable regions for the model that the query sequence matched.
    Args:
        cm_detected: The name of the model the sequence matched.

    Returns:
        model: A dictionary containing the coordinates of the variable regions for the matched model.
    """
    if cm_detected == "RF00177":
        model = REGIONS_16S_BACTERIA
    elif cm_detected == "RF01959":
        model = REGIONS_16S_ARCHAEA
    elif cm_detected == "RF01960":
        model = REGIONS_18S
    else:
        model = "unsupported"
    return model


def determine_domain(cm_detected):
    if cm_detected == "RF00177":
        return "Bacteria"
    elif cm_detected == "RF01959":
        return "Archaea"
    elif cm_detected == "RF01960":
        return "Eukaryotes"


def determine_marker_gene(domain):
    if domain in ["Bacteria", "Archaea"]:
        return "16S"
    elif domain == "Eukaryotes":
        return "18S"


def print_stats(
    run_id, num_sequences, num_unsupported, num_inside_vr, run_result, stats_out
):
    summary_num = dict()
    for cm in run_result:
        summary_num[cm] = dict()
        stats = Counter(run_result[cm])
        summary_num[cm]["empty"] = stats[""]
        summary_num[cm]["total regions"] = len(stats)
        del stats[""]
        summary_num[cm]["regions"] = ", ".join(stats.keys())
        summary_num[cm]["freqs"] = ", ".join(
            [
                (
                    "{0:.4f}".format(val / len(run_result[cm]))
                    if len(run_result[cm]) > 0
                    else "0"
                )
                for val in stats.values()
            ]
        )

    print_str = ""
    models = ["RF00177", "RF01959", "RF01960"]
    for model in models:
        if model in summary_num:
            print_str += ("{}\t" * 3).format(
                summary_num[model].get("empty", 0),
                summary_num[model].get("regions", ""),
                summary_num[model].get("freqs", 0),
            )
        else:
            print_str += " \t \t \t"
    if num_sequences > 0:
        stats_out.write(
            ("{}\t" * 7 + "{}\n").format(
                run_id,
                num_sequences,
                "{0:.3f}".format(num_unsupported / num_sequences),
                "{0:.3f}".format(num_inside_vr / num_sequences),
                "{0:.3f}".format(len(run_result.get("RF00177", [])) / num_sequences),
                "{0:.3f}".format(len(run_result.get("RF01959", [])) / num_sequences),
                "{0:.3f}".format(len(run_result.get("RF01960", [])) / num_sequences),
                print_str,
            )
        )


def print_to_table(tsv_out, results, per_read_info):
    """Prints the variable regions to a tsv file.
    Args:
        tsv_out: The name of the tsv outfile.
        results: The dictionary that contains a list of variable regions for a run and their match proportions.
    """
    # logging.info(results)

    prefix = tsv_out.split(".tsv")[0]

    f = open(tsv_out, "w")
    fw = open(f"{prefix}_regions.txt", "w")
    # print the table header to file
    f.write("Run\tAssertionEvidence\tAssertionMethod\tMarker gene\tVariable region\n")
    gene_hv_to_write = []
    for run, amplified_region_dict in results.items():
        records = set()
        records_regions = set()
        for domain, amplified_regions in amplified_region_dict.items():
            marker_gene = determine_marker_gene(domain)
            for vr in amplified_regions.keys():
                if not vr == "":
                    record = "{}\tECO_0000363\tautomatic assertion\t{}\t{}\n".format(
                        run, determine_marker_gene(domain), vr
                    )
                    records.add(record)
                    records_regions.add(f"{marker_gene}.{vr}\n")
                    gene_hv_to_write.append(f"{marker_gene}.{vr}")
        for record_to_print in records:
            f.write(record_to_print)

        for record_to_print in records_regions:
            fw.write(record_to_print)

    for key in per_read_info.keys():
        if key in gene_hv_to_write:
            per_read_filename = "{}.{}.txt".format(prefix, key)
            with open(per_read_filename, "w") as f_hv:
                f_hv.write("\n".join(per_read_info[key]))

    f.close()
    fw.close()


def retrieve_regions(
    tblout_file_list,
    outfile_prefix,
    stats_out,
    condensed_out,
    missing_out,
    seq_count_out,
):
    file_counter = 0  # count how many files were analyzed
    sequence_counter_total = 0  # count how many sequences in total were analyzed
    sequence_counter_useful = 0  # count how many sequences an output was generated for
    normalised_matches = dict()  # dictionary that will contain results for all runs
    failed_run_counter = (
        0  # total number of excluded runs for any reason (except non-existing files)
    )
    run_counters = {k: 0 for k in ["one", "two", "ambiguous"]}  # counters
    seq_per_variable_region_count = dict()

    for tblout_file in tblout_file_list:
        if not os.path.isfile(tblout_file):
            unzipped_filename = tblout_file.replace(".gz", "")
            if os.path.isfile(unzipped_filename):
                tblout_file = unzipped_filename
            else:
                logging.info("File {} does not exist".format(tblout_file))
                missing_out.write("{}\n".format(tblout_file))
                continue
        data = load_data(tblout_file)
        run_id = identify_run(tblout_file)
        multiregion_matches = dict()
        unsupported_matches = (
            0  # tracks the number of sequences that map to unsupported models
        )
        primer_inside_vr = 0  # tracks the number of sequences that start and/or end inside a variable region
        per_read_info = (
            dict()
        )  # dictionary will contain read names for each variable region
        all_region_coverages = defaultdict(lambda: defaultdict(list))
        for read in data:
            # Example structure of `read`
            # ('ERR14650515.1', 'SSU_rRNA_archaea', 'RF01959', 'hmm', '3', '525', '1', '518', '+', '-', '6', '0.55', '0.6', '363.6', '7.8e-107')
            regions = determine_cm(read[2])
            sequence_counter_total += 1
            limits = list(map(int, read[4:6]))
            domain = determine_domain(read[2])
            marker_gene = determine_marker_gene(domain)
            if not regions == "unsupported":
                matches, coverages = get_multiregion(limits, regions)

                [
                    all_region_coverages[domain][region].append(coverage)
                    for region, coverage in coverages.items()
                ]

                multiregion_matches.setdefault(read[2], []).append(matches)
                if check_primer_position(limits, regions):
                    primer_inside_vr += 1
                sequence_counter_useful += 1
                per_read_info.setdefault(marker_gene + "." + matches, []).append(
                    read[0]
                )
            else:
                unsupported_matches += 1

        print_stats(
            run_id,
            len(data),
            unsupported_matches,
            primer_inside_vr,
            multiregion_matches,
            stats_out,
        )
        if not data:
            failed_run_counter += 1
            logging.info("No output will be produced - no data")
            continue

        unsupported_fract = unsupported_matches / len(data)
        if unsupported_fract >= MAX_ERROR_PROPORTION:
            failed_run_counter += 1
            logging.info("No output will be produced - too many unsupported models")
            logging.info(
                "Excluded\t{}\t{}\t{}\n".format(
                    tblout_file, "{0:.2f}".format(unsupported_fract), len(data)
                )
            )
            continue

        normalised_matches[run_id] = dict()
        region_counter = defaultdict(int)

        regions_to_remove = []
        for model, value in multiregion_matches.items():
            marker_gene = determine_marker_gene(determine_domain(model))
            for region in value:
                region_counter[f"{marker_gene}.{region}"] += 1
        for region, count in region_counter.items():
            if count < MIN_SEQ_COUNT:
                regions_to_remove.append(region)

        if len(regions_to_remove) == len(region_counter.keys()):
            failed_run_counter += 1
            logging.info("No output will be produced - too few sequences in a domain")
            continue

        models_to_remove = []

        for model, value in multiregion_matches.items():
            new_value = []
            for region in value:
                if region == "":
                    continue
                marker_gene = determine_marker_gene(determine_domain(model))
                full_region = f"{marker_gene}.{region}"
                if full_region not in regions_to_remove:
                    new_value.append(region)
            if not new_value:
                models_to_remove.append(model)
            elif len(new_value) < MIN_SEQ_COUNT:
                models_to_remove.append(model)
            multiregion_matches[model] = new_value

        [multiregion_matches.pop(model) for model in models_to_remove]

        run_status = "one"
        run_result = dict()
        total_useful_sequences = 0.0
        temp_seq_counter = dict()
        for model, model_regions in multiregion_matches.items():
            result = normalise_results(model_regions)
            if result is None:
                run_status = "ambiguous"
                break
            elif len(result) == 2:
                run_status = "two"
            run_result[determine_domain(model)] = result
            for reg, freq in result.items():
                total_useful_sequences += len(model_regions) * freq
                temp_seq_counter[determine_domain(model) + " " + reg] = (
                    len(model_regions) * freq
                )
        if total_useful_sequences / len(data) < 0.75 and run_status != "ambiguous":
            failed_run_counter += 1
            logging.info("No output will be produced - too few useful sequences")
            continue

        file_counter += 1
        run_counters[run_status] += 1

        if run_status != "ambiguous":
            normalised_matches[run_id] = run_result
            for key, value in temp_seq_counter.items():
                seq_per_variable_region_count.setdefault(key, 0)
                seq_per_variable_region_count[key] += value
        else:
            logging.info("No output will be produced - the run is ambiguous.")
            continue

    coverage_fw = open(f"{outfile_prefix}_all_coverages.txt", "w")

    for domain, regions in all_region_coverages.items():
        for region in regions:
            if len(regions[region]) < MIN_SEQ_COUNT:
                continue
            region_coverage = float(np.mean(regions[region]))
            if region_coverage > 0:
                coverage_fw.write(f"{domain}:{region}: {region_coverage}\n")

    json_outfile = "{}.json".format(outfile_prefix)
    tsv_outfile = "{}.tsv".format(outfile_prefix)
    with open(json_outfile, "w") as f:
        json.dump(normalised_matches, f)
    print_to_table(tsv_outfile, normalised_matches, per_read_info)
    condensed_out.write(
        "\t".join(
            [
                "Total number of files failed",
                "Total number of files analyzed",
                "Number of runs with one region",
                "Number of runs with two regions",
                "Number of runs with too many regions or unbalanced 2 region runs",
            ]
        )
        + "\n"
    )
    condensed_out.write(
        "{}\t{}\t{}\t{}\t{}\n".format(
            failed_run_counter,
            file_counter,
            run_counters["one"],
            run_counters["two"],
            run_counters["ambiguous"],
        )
    )
    for key, value in seq_per_variable_region_count.items():
        seq_count_out.write("{}\t{}\n".format(key, int(value)))

    logging.info(
        "Analyzed {} files and {} sequences. Output generated for {} sequences".format(
            file_counter, sequence_counter_total, sequence_counter_useful
        )
    )


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Tool to determine which regions were amplified in 16S data"
    )
    parser.add_argument("files", nargs="+", help="A list of overlapped tblout files")
    parser.add_argument(
        "-d",
        "--output_dir",
        default="variable-region-inference",
        help="Directory to which results will be saved",
    )
    parser.add_argument(
        "-o",
        "--output_prefix",
        default="amplified_regions",
        help="Prefix for all outputs",
    )
    parser.add_argument(
        "--statistics", action="store_true", help="Print statistics files"
    )
    return parser.parse_args(argv)


def main(argv=None):
    t_start = time.perf_counter()  # time the run
    args = parse_args(argv)
    if not os.path.isdir(args.output_dir):
        os.mkdir(args.output_dir)
    prefix = os.path.join(args.output_dir, args.output_prefix)
    stats_file = "{}.stats".format(
        prefix
    )  # detailed stats for each run before filtration steps
    condensed_stats_file = "{}.condensed_stats".format(
        prefix
    )  # basic stats for the batch of runs
    missing_files_log = "{}.missing_files.txt".format(
        prefix
    )  # the names of non-existent files
    seq_count_log = "{}.seq_count.txt".format(
        prefix
    )  # the number of sequences per domain/VR in the batch
    stats_out = open(stats_file, "w")
    condensed_out = open(condensed_stats_file, "w")
    missing_out = open(missing_files_log, "w")
    seq_count_out = open(seq_count_log, "w")
    stats_out.write(
        "Run ID\tTotal # sequences\tFraction unsupported seq (map unsupported CM)\t"
        "Fraction of sequences with start and/or end inside a VR\tFraction bacteria\t"
        "Fraction archaea\tFraction eukaryotes\tUnidentified bact\tRegions bact\tFreqs bact\t"
        "Unidentified arch\tRegions arch\tFreqs arch\tUnidentified euk\tRegions euk\tFreqs euk\n"
    )
    retrieve_regions(
        args.files, prefix, stats_out, condensed_out, missing_out, seq_count_out
    )
    stats_out.close()
    condensed_out.close()
    missing_out.close()
    seq_count_out.close()
    if not args.statistics:
        for s_file in (
            stats_file,
            condensed_stats_file,
            missing_files_log,
            seq_count_log,
        ):
            os.remove(s_file)
    t_stop = time.perf_counter()
    t_fact = t_stop - t_start
    logging.info("Elapsed time: {0:.2f} seconds".format(t_fact))


if __name__ == "__main__":
    main()
