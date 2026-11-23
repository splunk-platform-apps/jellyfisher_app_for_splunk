#!/usr/bin/env python
#
# Copyright © 2011-2015 Splunk, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import re
import sys

APP_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
LIB_DIR = os.path.join(APP_DIR, "lib")

# jellyfish ships a compiled module, so it is built per platform and Python version
PLATFORM_DIRS = {"win": "windows_x86_64", "linux": "linux_x86_64", "darwin": "darwin_x86_64"}
PYTHON_DIR = f"python{sys.version_info.major}{sys.version_info.minor}"

sys.path.insert(0, LIB_DIR)
for prefix, platform_dir in PLATFORM_DIRS.items():
    if sys.platform.startswith(prefix):
        sys.path.insert(0, os.path.join(LIB_DIR, "3rdparty", platform_dir, PYTHON_DIR))

import jellyfish  # noqa: E402
import legacy  # noqa: E402
from splunklib.searchcommands import Configuration, StreamingCommand, dispatch  # noqa: E402

# Algorithms with the results of JellyFisher 1.0.1 (jellyfish 0.8.2): jellyfish 1.x renamed or
# dropped some of them and changed the results of others, see legacy.py. The new names of the
# Jaro algorithms, jaro_similarity and jaro_winkler_similarity, come from jellyfish.
LEGACY = (
    "jaro_distance",
    "jaro_winkler",
    "metaphone",
    "match_rating_codex",
    "match_rating_comparison",
    "porter_stem",
)


def get_function(algorithm):
    if algorithm in LEGACY:
        return getattr(legacy, algorithm)
    return getattr(jellyfish, algorithm)


@Configuration()
class JellyfisherCommand(StreamingCommand):
    # distances, 2 words
    _distance_algorithms = (
        "levenshtein_distance",
        "damerau_levenshtein_distance",
        "jaro_similarity",
        "jaro_winkler_similarity",
        "match_rating_comparison",
        "hamming_distance",
        "jaro_distance",
        "jaro_winkler",
    )

    # phonetic, 1 word
    _phonetic_algorithms = (
        "soundex",
        "nysiis",
        "match_rating_codex",
        "metaphone",
        "porter_stem",
    )

    preg_t = re.compile(r"([^(]+)\(([^)]+)")

    def parse_args(self, strarg):
        ret = self.preg_t.search(strarg)
        self._algorithm = ret.group(1)
        self._arguments = [
            x.strip() for x in ret.group(2).split(",")
        ]  # e.g. ['yolo', 'lookup:bheh']
        self._n_arguments = len(self._arguments)
        self._uses_lookup = False
        self.req_fields = []
        self.logger.debug("JellyfisherCommand: %s", self._arguments)  # logs command line

        if self._algorithm in self._phonetic_algorithms and self._n_arguments != 1:
            raise ValueError("phonetic algorithms takes one argument as input")

        if self._algorithm in self._distance_algorithms and self._n_arguments != 2:
            raise ValueError("distance algorithms takes two arguments as input")

        if (
            self._algorithm not in self._distance_algorithms
            and self._algorithm not in self._phonetic_algorithms
        ):
            raise ValueError(f"{self._algorithm} is not a valid algorithm")

        for a in self._arguments:
            if a.startswith("lookup:"):
                self._uses_lookup = True
                continue
            self.req_fields.append(a)

        if self._algorithm in self._phonetic_algorithms and self._uses_lookup:
            raise ValueError(
                "unsupported branching: lookups cannot be used with phonetic algorithms"
            )

    def stream(self, records):
        self.logger.debug("JellyfisherCommand: %s", self)  # logs command line
        self.parse_args(",".join(self.fieldnames))
        function = get_function(self._algorithm)

        if self._n_arguments == 1:
            f = self.req_fields[0]

            for record in records:
                word = record[f]
                r = function(word)
                record.update({self._algorithm: r})
                yield record

        else:
            if self._uses_lookup:
                raise ValueError("unsupported yet")
            else:
                f1 = self.req_fields[0]
                f2 = self.req_fields[1]

                for record in records:
                    w1 = record[f1]
                    w2 = record[f2]

                    r = function(w1, w2)
                    record.update({self._algorithm: r})
                    yield record


dispatch(JellyfisherCommand, sys.argv, sys.stdin, sys.stdout, __name__)
