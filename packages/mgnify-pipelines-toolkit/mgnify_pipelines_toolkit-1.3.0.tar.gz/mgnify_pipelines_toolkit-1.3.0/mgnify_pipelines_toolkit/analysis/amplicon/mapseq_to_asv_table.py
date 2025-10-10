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

logging.basicConfig(level=logging.DEBUG)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input", required=True, type=str, help="Input from MAPseq output"
    )
    parser.add_argument(
        "-l",
        "--label",
        choices=["DADA2-SILVA", "DADA2-PR2"],
        required=True,
        type=str,
        help="Database label - either DADA2-SILVA or DADA2-PR2",
    )
    parser.add_argument("-s", "--sample", required=True, type=str, help="Sample ID")

    args = parser.parse_args()

    input = args.input
    label = args.label
    sample = args.sample

    return input, label, sample


def parse_label(label):
    silva_short_ranks = ["sk__", "k__", "p__", "c__", "o__", "f__", "g__", "s__"]
    pr2_short_ranks = [
        "d__",
        "sg__",
        "dv__",
        "sdv__",
        "c__",
        "o__",
        "f__",
        "g__",
        "s__",
    ]

    silva_long_ranks = [
        "Superkingdom",
        "Kingdom",
        "Phylum",
        "Class",
        "Order",
        "Family",
        "Genus",
        "Species",
    ]
    pr2_long_ranks = [
        "Domain",
        "Supergroup",
        "Division",
        "Subdivision",
        "Class",
        "Order",
        "Family",
        "Genus",
        "Species",
    ]

    chosen_short_ranks = ""
    chosen_long_ranks = ""

    if label == "DADA2-SILVA":
        chosen_short_ranks = silva_short_ranks
        chosen_long_ranks = silva_long_ranks
    elif label == "DADA2-PR2":
        chosen_short_ranks = pr2_short_ranks
        chosen_long_ranks = pr2_long_ranks
    else:
        logging.error("Incorrect database label - exiting.")
        exit(1)

    return chosen_short_ranks, chosen_long_ranks


def parse_mapseq(mseq_df, short_ranks, long_ranks):
    res_dict = defaultdict(list)

    for i in range(len(mseq_df)):
        asv_id = mseq_df.iloc[i, 0]

        if pd.isna(mseq_df.iloc[i, 1]):
            tax_ass = [short_ranks[0]]
        else:
            tax_ass = mseq_df.iloc[i, 1].split(";")

        res_dict["ASV"].append(asv_id)

        for j in range(len(short_ranks)):
            curr_rank = long_ranks[j]

            if j >= len(tax_ass):
                # This would only be true if the assigned taxonomy is shorter than the total reference database taxononmy
                # so fill each remaining rank with its respective short rank blank
                curr_tax = short_ranks[j]
            else:
                curr_tax = tax_ass[j]

            res_dict[curr_rank].append(curr_tax)
    res_df = pd.DataFrame.from_dict(res_dict)

    return res_df


def process_blank_tax_ends(res_df, ranks):
    # Necessary function as we want to replace consecutive blank assignments that start at the last rank as NAs
    # while avoiding making blanks in the middle as NAs

    for i in range(len(res_df)):
        last_empty_rank = ""
        currently_empty = False
        for j in reversed(
            range(len(ranks))
        ):  # Parse an assignment backwards, from Species all the way to Superkingdom/Domain
            curr_rank = res_df.iloc[i, j + 1]
            if curr_rank in ranks:
                if (
                    last_empty_rank == ""
                ):  # Last rank is empty, start window of consecutive blanks
                    last_empty_rank = j + 1
                    currently_empty = True
                elif (
                    currently_empty
                ):  # If we're in a window of consecutive blank assignments that started at the beginning
                    last_empty_rank = j + 1
                else:
                    break
            else:
                break
        if last_empty_rank != "":
            res_df.iloc[i, last_empty_rank:] = "NA"
        if last_empty_rank == 1:
            res_df.iloc[i, 1] = ranks[0]

    return res_df


def main():
    input, label, sample = parse_args()

    mseq_df = pd.read_csv(input, header=0, delim_whitespace=True, usecols=[0, 12])

    short_ranks, long_ranks = parse_label(label)
    res_df = parse_mapseq(mseq_df, short_ranks, long_ranks)
    final_res_df = process_blank_tax_ends(res_df, short_ranks)

    final_res_df.to_csv(f"./{sample}_{label}_asv_taxa.tsv", sep="\t", index=False)


if __name__ == "__main__":
    main()
