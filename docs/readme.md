# JellyFisher App for Splunk

This app provides a Splunk custom search command, `jellyfisher`, that uses the [jellyfish](https://pypi.org/project/jellyfish/) Python library. It computes a distance between two fields, or a phonetic encoding of one field; for example, the Levenshtein distance between "kitten" and "sitting" is 3, and the Soundex code of both "Robert" and "Rupert" is `R163`.

It is a search-time app with no user interface.

👉 Typical use cases include detecting values that are close to a known one, such as a process name one character away from `svchost.exe`, or a domain that imitates another one.

## Features

- Computes the distance between two fields with six algorithms, and encodes one field with five phonetic or stemming algorithms.
- Runs as a chunked (SCP v2) command, so events are processed in batches.
- Works with the algorithm names used by JellyFisher 1.0.1; see [Upgrading](#upgrading).

### Algorithms

The command takes the algorithm and its fields as one argument, as in `jellyfisher levenshtein_distance(field1, field2)`. The result is added to each event in a field with the name of the algorithm. All other fields of the event are kept.

| Algorithm | Fields | Result |
| --- | --- | --- |
| `levenshtein_distance` | 2 | Number of insertions, deletions, and substitutions to turn one value into the other. |
| `damerau_levenshtein_distance` | 2 | Like Levenshtein, and also counts the swap of two adjacent characters as one change. |
| `hamming_distance` | 2 | Number of positions with different characters, plus the difference in length. |
| `jaro_similarity` | 2 | Similarity from 0 (nothing in common) to 1 (identical). `jaro_distance` is the name that 1.0.1 used for the same result. |
| `jaro_winkler_similarity` | 2 | Jaro similarity with a bonus for a common prefix. `jaro_winkler` is the name that 1.0.1 used. It does not give the bonus to strings of up to three characters, as in 1.0.1, and `jaro_winkler_similarity` does. |
| `match_rating_comparison` | 2 | `true` if the Match Rating Approach considers the values similar, `false` otherwise, and no value when the codes differ in length by 3 or more. It accepts values with digits and punctuation, as in 1.0.1. |
| `soundex` | 1 | American Soundex code. |
| `nysiis` | 1 | NYSIIS (New York State Identification and Intelligence System) code. |
| `metaphone` | 1 | Metaphone code, as in 1.0.1. |
| `match_rating_codex` | 1 | Match Rating Approach code. It accepts values with digits and punctuation, as in 1.0.1. |
| `porter_stem` | 1 | Stem of an English word, according to the Porter stemming algorithm. |

## Getting Started

### Requirements

- Splunk Enterprise 9.3 or later, or Splunk Cloud with Python 3.9 or 3.13.
- A platform that has a build of the jellyfish library: Linux x86_64, Windows x86_64, or macOS x86_64, with Python 3.9 or 3.13. The app declares `python.required = 3.9,3.13`.

### Installation

Install the app from [Splunkbase](https://splunkbase.splunk.com/app/3626) on Splunk **search heads**. In Splunk Cloud, install it from Splunkbase with the app browser or ACS.

> [!IMPORTANT]
> In a distributed deployment, the app replicates its `lib` folder to the indexers with the knowledge bundle (see `package/default/distsearch.conf`), because the command can also run on them.

### Usage

```
... | jellyfisher <algorithm>(<field>[, <field>])
```

Distance algorithms take two fields, and phonetic algorithms take one. A field must hold a string. The command stops with an error when the algorithm is unknown or when the number of fields is wrong.

## Upgrading

The app ID is `jellyfisher`, as for the app on Splunkbase. Update the installed app instead of uninstalling it first, because an uninstall also removes the files in its `local` folder.

| You have | What to do |
| --- | --- |
| JellyFisher 1.0.1 from Splunkbase | Update the app. Your searches keep working, including the ones that use `jaro_distance`, `jaro_winkler`, and `porter_stem`. |
| JellyFisher 2.0.0 | Update the app. The results of `metaphone`, `match_rating_codex`, and `match_rating_comparison` change for the values listed in [Compatibility](#compatibility). |
| A private copy with another app ID, such as `jellyfisher_app`, `jellyfisher_cloud`, or `rj_jellyfisher` | Uninstall the private copy, then install this app. A private copy does not update, and two apps that define the `jellyfisher` command conflict. |

### Compatibility

Searches that use the names of 1.0.1 return the same results as in 1.0.1. The app uses the code of jellyfish 0.8.2, the library of 1.0.1, for `jaro_distance`, `jaro_winkler`, `metaphone`, `match_rating_codex`, `match_rating_comparison`, and `porter_stem`, and jellyfish 1.2.1 for the other algorithms. In a test of 2,546,672 calls (all 235,976 words of an English word list, and 195,256 pairs of words with typos, short strings, and values with digits and punctuation), every algorithm of 1.0.1 returned exactly the same value as 1.0.1.

Compared with 2.0.0, which used jellyfish 1.2.1 for everything:

- `metaphone` returns a different code for 299 of the 235,976 words. 140 of them end in "gh", for which jellyfish 1.2.1 adds a spurious `KH`, for example `LKH` for "laugh" instead of `L`.
- `match_rating_codex` and `match_rating_comparison` accept values with digits, punctuation, and non-ASCII letters, such as `svchost.exe`. 2.0.0 stopped the search with an error or returned no value.
- `porter_stem`, `jaro_distance`, and `jaro_winkler` work again.
- `jaro_winkler_similarity` is the same as in 2.0.0. It differs from `jaro_winkler` for strings of up to three characters. For example, "0" and "00" score 0.85 with `jaro_winkler_similarity` and 0.8333 with `jaro_winkler`.

## Troubleshooting

- `<name> is not a valid algorithm`: the algorithm name has a typo, or the name is not in the [table](#algorithms).
- `distance algorithms takes two arguments as input` and `phonetic algorithms takes one argument as input`: the number of fields does not fit the algorithm.
- `No module named 'jellyfish'` or an error about `_rustyfish`: the platform or the Python version has no build of the jellyfish library. See [Requirements](#requirements).
- To see more, open the job inspector of the search and check `search.log`.

## Examples

Distance between two fields:

```
index=sysmon EventCode=1
| jellyfisher jaro_similarity(process_name, Image)
| where jaro_similarity < 0.5
| table _time, Computer, User, process_name, Image, jaro_similarity
```

Phonetic code of a field:

```
... | jellyfisher soundex(user)
```

The lookup `processNames.csv` of the app holds a few process names. This search compares each of them with the process names of Windows events:

```
| inputlookup processNames.csv
| map search="search index=windows | stats count by process | eval known=\"$processName$\" | jellyfisher levenshtein_distance(known, process)"
| table known, process, levenshtein_distance
```

## Tests

To run the unit tests locally:

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -r tests/test-requirements.txt
python -m pytest tests
```

To run one search per algorithm against a Splunk instance with the app installed, run `tests/splunk_smoke.sh`.

The [Tests workflow](../.github/workflows/tests.yml) runs both unit and smoke tests on every pull request.

## Versions Tested

| Splunk Enterprise | Python used | Tested |
| --- | --- | --- |
| 9.3.0 | 3.9 | Yes |
| 10.0.1 | 3.9 | Yes |
| 10.6.1.1 | 3.13 | Yes |

Each version was tested with a new install, and with an update from 1.0.1 that keeps the files in `local`. The searches written for 1.0.1 return the same results after the update.

The table above lists the Splunk Enterprise versions tested; it does not list Splunk Cloud stack versions. Splunk Cloud is supported when the stack provides Python 3.9 or 3.13, but Cloud upgrade testing for this release is pending.

## Credits & Acknowledgements

- Cedric Le Roux, author of the app.
- The [jellyfish](https://github.com/jamesturk/jellyfish) library by James Turk.
- The icon was made by [Freepik](https://www.freepik.com) from [www.flaticon.com](https://www.flaticon.com/).

## Contributing
See the [CONTRIBUTING.md](https://github.com/splunk-platform-apps/.github/blob/main/.github/CONTRIBUTING.md) file for details.
