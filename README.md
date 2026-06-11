# JellyFisher

JellyFisher is a Splunk custom search command that leverage the excellent jellyfish library for python [1]. JellyFisher aims to a) compute a distance between 2 given words, and b) compute a phonetic encoding of a given word.


Ex:
- The Levenshtein distance between "kitten" and "sitting" is 3.
- The soundex representation of both "Robert" and "Rupert" is "R163"


JellyFisher uses Chunked Protocol for custom search commands, meaning that decent performances should be achieved (but no testing were performed to confirm that or not).

## Supported algorithms

**Distance algorithms:**
* Levenshtein Distance - `levenshtein_distance`
* Damerau-Levenshtein Distance - `damerau_levenshtein_distance`
* Jaro Distance - `jaro_similarity`
* Jaro-Winkler Distance - `jaro_winkler_similarity`
* Match Rating Approach Comparison - `match_rating_comparison`
* Hamming Distance - `hamming_distance`

**Phonetic algorithms:**
* American Soundex - `soundex`
* Metaphone - `metaphone`
* NYSIIS (New York State Identification and Intelligence System) - `nysiis`
* Match Rating Codex - `match_rating_codex`

## ⚠️ v2.0 Breaking Changes

Version `2.0.0` comes with a **major jellyfish library upgrade** (v0.8.2 → v1.2.1). By default the bundled algorithms  use **rust** instead of the **deprecated python** implementations, meaning the library has become platform and environment dependent [2].

Please be aware of the following breaking changes.

### Removed Functions

`jellyfish.porter_stem()` has been removed in v1.2.1. If your code relies on this function, you will need to replace it with an alternative stemming library.

### Renamed Functions

The following functions have been renamed for clarity:

| v0.8.2 (old)                | v1.2.1 (new)                          |
|-----------------------------|---------------------------------------|
| `jellyfish.jaro_distance()` | `jellyfish.jaro_similarity()`         |
| `jellyfish.jaro_winkler()`  | `jellyfish.jaro_winkler_similarity()` |


Using the old function names will raise an `AttributeError` at runtime.

## Usage

The generic usage is straightforward:

```
... | jellyfisher <algorithm>(<arguments>)
```

Examples:

```
... | jellyfisher levensthein_distance(sourcetype,source)
... | jellyfisher jaro_similarity(user,sourcetype)
... | jellyfisher soundex(sourcetype)

```


## Inputlookup

The following search is given as demonstration purpose to load a bunch of words (process names) from a CSV lookup file and then compute their distances using the map() command. This is not the perfect implementation, but a good example to start from :)

```
| inputlookup processNames.csv
| map search="search index=windows | head 10 | stats count by process | eval pName = $processName$ | jellyfisher levenshtein_distance($processName$, process)"
| table process, pName, levenshtein_distance
```



## References

[1] https://pypi.python.org/pypi/jellyfish
[2] https://www.jpt.sh/projects/jellyfish/#implementations


## Credits

Icon made by <a href="https://www.freepik.com" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a>