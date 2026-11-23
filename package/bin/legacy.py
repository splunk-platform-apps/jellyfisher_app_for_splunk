"""Functions of jellyfish 0.8.2 (MIT license), as used by JellyFisher 1.0.1.

jellyfish 1.x changed or dropped some of them. Searches written for 1.0.1 give exactly the same
results with these: jaro_distance, jaro_winkler, metaphone, match_rating_codex,
match_rating_comparison and porter_stem.
"""

import unicodedata
from itertools import zip_longest

from porter_stemmer import Stemmer


def _normalize(s):
    return unicodedata.normalize("NFKD", s)


def _check_type(s):
    if not isinstance(s, str):
        raise TypeError(f"expected str or unicode, got {type(s).__name__}")


def _jaro_winkler(s1, s2, long_tolerance, winklerize):
    _check_type(s1)
    _check_type(s2)

    s1_len = len(s1)
    s2_len = len(s2)

    if not s1_len or not s2_len:
        return 0.0

    min_len = max(s1_len, s2_len)
    search_range = (min_len // 2) - 1
    if search_range < 0:
        search_range = 0

    s1_flags = [False] * s1_len
    s2_flags = [False] * s2_len

    # looking only within search range, count & flag matched pairs
    common_chars = 0
    for i, s1_ch in enumerate(s1):
        low = max(0, i - search_range)
        hi = min(i + search_range, s2_len - 1)
        for j in range(low, hi + 1):
            if not s2_flags[j] and s2[j] == s1_ch:
                s1_flags[i] = s2_flags[j] = True
                common_chars += 1
                break

    # short circuit if no characters match
    if not common_chars:
        return 0.0

    # count transpositions
    k = trans_count = 0
    for i, s1_f in enumerate(s1_flags):
        if s1_f:
            for j in range(k, s2_len):
                if s2_flags[j]:
                    k = j + 1
                    break
            if s1[i] != s2[j]:
                trans_count += 1
    trans_count //= 2

    # adjust for similarities in nonmatched characters
    common_chars = float(common_chars)
    weight = (
        common_chars / s1_len + common_chars / s2_len + (common_chars - trans_count) / common_chars
    ) / 3

    # winkler modification: continue to boost if strings are similar
    if winklerize and weight > 0.7 and s1_len > 3 and s2_len > 3:
        # adjust for up to first 4 chars in common
        j = min(min_len, 4)
        i = 0
        while i < j and s1[i] == s2[i] and s1[i]:
            i += 1
        if i:
            weight += i * 0.1 * (1.0 - weight)

        # optionally adjust for long strings
        # after agreeing beginning chars, at least two or more must agree and
        # agreed characters must be > half of remaining characters
        if (
            long_tolerance
            and min_len > 4
            and common_chars > i + 1
            and 2 * common_chars >= min_len + i
        ):
            weight += (1.0 - weight) * (
                float(common_chars - i - 1) / float(s1_len + s2_len - i * 2 + 2)
            )

    return weight


def jaro_distance(s1, s2):
    return _jaro_winkler(s1, s2, False, False)


def jaro_winkler(s1, s2, long_tolerance=False):
    return _jaro_winkler(s1, s2, long_tolerance, True)


def match_rating_codex(s):
    _check_type(s)

    s = s.upper()
    codex = []

    prev = None
    for i, c in enumerate(s):
        # not a space OR
        # starting character & vowel
        # or consonant not preceded by same consonant
        if (c != " " and (i == 0 and c in "AEIOU")) or (c not in "AEIOU" and c != prev):
            codex.append(c)

        prev = c

    # just use first/last 3
    if len(codex) > 6:
        return "".join(codex[:3] + codex[-3:])
    else:
        return "".join(codex)


def match_rating_comparison(s1, s2):
    codex1 = match_rating_codex(s1)
    codex2 = match_rating_codex(s2)
    len1 = len(codex1)
    len2 = len(codex2)
    res1 = []
    res2 = []

    # length differs by 3 or more, no result
    if abs(len1 - len2) >= 3:
        return None

    # get minimum rating based on sums of codexes
    lensum = len1 + len2
    if lensum <= 4:
        min_rating = 5
    elif lensum <= 7:
        min_rating = 4
    elif lensum <= 11:
        min_rating = 3
    else:
        min_rating = 2

    # strip off common prefixes
    for c1, c2 in zip_longest(codex1, codex2):
        if c1 != c2:
            if c1:
                res1.append(c1)
            if c2:
                res2.append(c2)

    unmatched_count1 = unmatched_count2 = 0
    for c1, c2 in zip_longest(reversed(res1), reversed(res2)):
        if c1 != c2:
            if c1:
                unmatched_count1 += 1
            if c2:
                unmatched_count2 += 1

    return (6 - max(unmatched_count1, unmatched_count2)) >= min_rating


def metaphone(s):
    _check_type(s)

    result = []

    s = _normalize(s.lower())

    # skip first character if s starts with these
    if s.startswith(("kn", "gn", "pn", "wr", "ae")):
        s = s[1:]

    i = 0

    while i < len(s):
        c = s[i]
        next_char = s[i + 1] if i < len(s) - 1 else "*****"
        nextnext = s[i + 2] if i < len(s) - 2 else "*****"

        # skip doubles except for cc
        if c == next_char and c != "c":
            i += 1
            continue

        if c in "aeiou":
            if i == 0 or s[i - 1] == " ":
                result.append(c)
        elif c == "b":
            if (not (i != 0 and s[i - 1] == "m")) or next_char:
                result.append("b")
        elif c == "c":
            if (next_char == "i" and nextnext == "a") or next_char == "h":
                result.append("x")
                i += 1
            elif next_char in "iey":
                result.append("s")
                i += 1
            else:
                result.append("k")
        elif c == "d":
            if next_char == "g" and nextnext in "iey":
                result.append("j")
                i += 2
            else:
                result.append("t")
        elif c in "fjlmnr":
            result.append(c)
        elif c == "g":
            if next_char in "iey":
                result.append("j")
            elif next_char == "h" and nextnext and nextnext not in "aeiou":
                i += 1
            elif next_char == "n" and not nextnext:
                i += 1
            else:
                result.append("k")
        elif c == "h":
            if i == 0 or next_char in "aeiou" or s[i - 1] not in "aeiou":
                result.append("h")
        elif c == "k":
            if i == 0 or s[i - 1] != "c":
                result.append("k")
        elif c == "p":
            if next_char == "h":
                result.append("f")
                i += 1
            else:
                result.append("p")
        elif c == "q":
            result.append("k")
        elif c == "s":
            if next_char == "h":
                result.append("x")
                i += 1
            elif next_char == "i" and nextnext in "oa":
                result.append("x")
                i += 2
            else:
                result.append("s")
        elif c == "t":
            if next_char == "i" and nextnext in "oa":
                result.append("x")
            elif next_char == "h":
                result.append("0")
                i += 1
            elif next_char != "c" or nextnext != "h":
                result.append("t")
        elif c == "v":
            result.append("f")
        elif c == "w":
            if i == 0 and next_char == "h":
                i += 1
                result.append("w")
            elif next_char in "aeiou":
                result.append("w")
        elif c == "x":
            if i == 0:
                if next_char == "h" or (next_char == "i" and nextnext in "oa"):
                    result.append("x")
                else:
                    result.append("s")
            else:
                result.append("k")
                result.append("s")
        elif c == "y":
            if next_char in "aeiou":
                result.append("y")
        elif c == "z":
            result.append("s")
        elif c == " ":
            if len(result) > 0 and result[-1] != " ":
                result.append(" ")

        i += 1

    return "".join(result).upper()


def porter_stem(s):
    _check_type(s)

    return Stemmer(s).stem()
