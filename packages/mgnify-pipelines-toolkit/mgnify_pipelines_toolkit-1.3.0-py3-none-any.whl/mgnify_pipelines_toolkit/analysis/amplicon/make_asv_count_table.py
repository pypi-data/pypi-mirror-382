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
from collections import defaultdict
import logging

import pandas as pd

from mgnify_pipelines_toolkit.constants.tax_ranks import (
    _SILVA_TAX_RANKS,
    _PR2_TAX_RANKS,
)

logging.basicConfig(level=logging.DEBUG)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-t", "--taxa", required=True, type=str, help="Path to taxa file"
    )
    parser.add_argument(
        "-f", "--fwd", required=True, type=str, help="Path to DADA2 forward map file"
    )
    parser.add_argument(
        "-r", "--rev", required=False, type=str, help="Path to DADA2 reverse map file"
    )
    parser.add_argument(
        "-a",
        "--amp",
        required=True,
        type=str,
        help="Path to extracted amp_region reads from inference subworkflow",
    )
    parser.add_argument(
        "-hd", "--headers", required=True, type=str, help="Path to fastq headers"
    )
    parser.add_argument("-s", "--sample", required=True, type=str, help="Sample ID")

    args = parser.parse_args()

    taxa = args.taxa
    fwd = args.fwd
    rev = args.rev
    amp = args.amp
    headers = args.headers
    sample = args.sample

    return taxa, fwd, rev, amp, headers, sample


def order_df(taxa_df):
    if len(taxa_df.columns) == 9:
        taxa_df = taxa_df.sort_values(_SILVA_TAX_RANKS, ascending=True)
    elif len(taxa_df.columns) == 10:
        taxa_df = taxa_df.sort_values(_PR2_TAX_RANKS, ascending=True)
    else:
        logging.error("Data frame not the right size, something wrong.")
        exit(1)

    return taxa_df


def make_tax_assignment_dict_silva(taxa_df, asv_dict):
    tax_assignment_dict = defaultdict(int)

    for i in range(len(taxa_df)):
        sorted_index = taxa_df.index[i]
        asv_num = taxa_df.iloc[i, 0]
        asv_count = asv_dict[asv_num]

        if asv_count == 0:
            continue

        sk = taxa_df.loc[sorted_index, "Superkingdom"]
        k = taxa_df.loc[sorted_index, "Kingdom"]
        p = taxa_df.loc[sorted_index, "Phylum"]
        c = taxa_df.loc[sorted_index, "Class"]
        o = taxa_df.loc[sorted_index, "Order"]
        f = taxa_df.loc[sorted_index, "Family"]
        g = taxa_df.loc[sorted_index, "Genus"]
        s = taxa_df.loc[sorted_index, "Species"]

        tax_assignment = ""

        while True:

            if sk != "0":
                sk = "_".join(sk.split(" "))
                tax_assignment += sk
            else:
                break

            if k != "0":
                k = "_".join(k.split(" "))
                tax_assignment += f"\t{k}"
            elif sk != "0":
                tax_assignment += "\tk__"
            else:
                break

            if p != "0":
                p = "_".join(p.split(" "))
                tax_assignment += f"\t{p}"
            else:
                break

            if c != "0":
                c = "_".join(c.split(" "))
                tax_assignment += f"\t{c}"
            else:
                break

            if o != "0":
                o = "_".join(o.split(" "))
                tax_assignment += f"\t{o}"
            else:
                break

            if f != "0":
                f = "_".join(f.split(" "))
                tax_assignment += f"\t{f}"
            else:
                break

            if g != "0":
                g = "_".join(g.split(" "))
                tax_assignment += f"\t{g}"
            else:
                break

            if s != "0":
                s = "_".join(s.split(" "))
                tax_assignment += f"\t{s}"
            break

        if tax_assignment == "":
            continue

        tax_assignment_dict[tax_assignment] += asv_count

    return tax_assignment_dict


def make_tax_assignment_dict_pr2(taxa_df, asv_dict):
    tax_assignment_dict = defaultdict(int)

    for i in range(len(taxa_df)):
        sorted_index = taxa_df.index[i]
        asv_num = taxa_df.iloc[i, 0]
        asv_count = asv_dict[asv_num]

        if asv_count == 0:
            continue

        d = taxa_df.loc[sorted_index, "Domain"]
        sg = taxa_df.loc[sorted_index, "Supergroup"]
        dv = taxa_df.loc[sorted_index, "Division"]
        sdv = taxa_df.loc[sorted_index, "Subdivision"]
        c = taxa_df.loc[sorted_index, "Class"]
        o = taxa_df.loc[sorted_index, "Order"]
        f = taxa_df.loc[sorted_index, "Family"]
        g = taxa_df.loc[sorted_index, "Genus"]
        s = taxa_df.loc[sorted_index, "Species"]

        tax_assignment = ""

        while True:
            if d != "0":
                d = "_".join(d.split(" "))
                tax_assignment += d
            else:
                break

            if sg != "0":
                sg = "_".join(sg.split(" "))
                tax_assignment += f"\t{sg}"
            else:
                break

            if dv != "0":
                dv = "_".join(dv.split(" "))
                tax_assignment += f"\t{dv}"
            else:
                break

            if sdv != "0":
                sdv = "_".join(sdv.split(" "))
                tax_assignment += f"\t{sdv}"
            else:
                break

            if c != "0":
                c = "_".join(c.split(" "))
                tax_assignment += f"\t{c}"
            else:
                break

            if o != "0":
                o = "_".join(o.split(" "))
                tax_assignment += f"\t{o}"
            else:
                break

            if f != "0":
                f = "_".join(f.split(" "))
                tax_assignment += f"\t{f}"
            else:
                break

            if g != "0":
                g = "_".join(g.split(" "))
                tax_assignment += f"\t{g}"
            else:
                break

            if s != "0":
                s = "_".join(s.split(" "))
                tax_assignment += f"\t{s}"
            break

        if tax_assignment == "":
            continue

        tax_assignment_dict[tax_assignment] += asv_count

    return tax_assignment_dict


def generate_asv_count_dict(asv_dict):

    res_dict = defaultdict(list)

    for asv_id, count in asv_dict.items():

        if count == 0:
            continue

        res_dict["asv"].append(asv_id)
        res_dict["count"].append(count)

    res_df = pd.DataFrame.from_dict(res_dict)
    res_df = res_df.sort_values(by="asv", ascending=True)
    res_df = res_df.sort_values(by="count", ascending=False)

    return res_df


def main():
    taxa, fwd, rev, amp, headers, sample = parse_args()

    fwd_fr = open(fwd, "r")
    paired_end = True

    if rev is None:
        paired_end = False
        rev_fr = [True]
    else:
        rev_fr = open(rev, "r")

    taxa_df = pd.read_csv(taxa, sep="\t", dtype=str)
    taxa_df = taxa_df.fillna("0")
    taxa_df = order_df(taxa_df)

    asv_list = taxa_df.ASV.to_list()

    amp_reads = [read.strip() for read in list(open(amp, "r"))]
    headers = [read.split(" ")[0][1:] for read in list(open(headers, "r"))]
    amp_region = ".".join(amp.split(".")[1:3])

    asv_dict = defaultdict(int)

    counter = -1
    for line_fwd in fwd_fr:
        counter += 1
        line_fwd = line_fwd.strip()

        if line_fwd == "0" or f"seq_{line_fwd}" not in asv_list:
            continue

        if headers[counter] in amp_reads:
            asv_dict[f"seq_{line_fwd}"] += 1

    fwd_fr.close()
    if paired_end:
        rev_fr.close()

    if asv_dict:  # if there are matches between taxonomic and ASV annotations
        ref_db = ""

        if len(taxa_df.columns) == 9:
            tax_assignment_dict = make_tax_assignment_dict_silva(taxa_df, asv_dict)
            ref_db = "silva"
        elif len(taxa_df.columns) == 10:
            tax_assignment_dict = make_tax_assignment_dict_pr2(taxa_df, asv_dict)
            ref_db = "pr2"

        with open(f"./{sample}_{amp_region}_{ref_db}_asv_krona_counts.txt", "w") as fw:
            for tax_assignment, count in tax_assignment_dict.items():
                fw.write(f"{count}\t{tax_assignment}\n")

        asv_count_df = generate_asv_count_dict(asv_dict)
        asv_count_df.to_csv(
            f"./{sample}_{amp_region}_asv_read_counts.tsv", sep="\t", index=False
        )


if __name__ == "__main__":
    main()
