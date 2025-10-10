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

FORMAT_REGEX_MAP = {
    "uniprotkb": r"^(?P<db>\w+)\|(?P<unique_identifier>\w+)\|(?P<entry_name>\w+)\s(?P<protein_name>.+)\sOS=(?P<organism_name>.+)\sOX=(?P<organism_identifier>\d+)(\sGN=(?P<gene_name>.+))?\sPE=(?P<protein_existence>\d+)\sSV=(?P<sequence_version>\d+)",  # noqa: E501
    "rpxx": r"^(?P<unique_identifier>\S+)\s(?P<entry_name>\S+)\^\|\^.*\^\|\^(?P<protein_name>.+)\^\|\^.*\^\|\^.*\^\|\^(?P<organism_name>.+)\^\|\^(?P<organism_identifier>\d+)\^\|\^(?P<common_tax_name>.+)\^\|\^(?P<common_tax_identifier>\d+)",  # noqa: E501
}
