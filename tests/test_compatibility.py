"""Results of JellyFisher 1.0.1 (jellyfish 0.8.2) that must not change.

The expected values come from running the library of the 1.0.1 package.
"""

import jellyfish
import jellyfisher
import pytest


def run(argument, records):
    command = jellyfisher.JellyfisherCommand()
    command._fieldnames = [argument]
    return list(command.stream(iter(records)))


@pytest.mark.parametrize(
    ("algorithm", "a", "b", "expected"),
    [
        ("jaro_distance", "dixon", "dicksonx", 0.7666666666666666),
        ("jaro_winkler", "dixon", "dicksonx", 0.8133333333333332),
        ("jaro_winkler", "martha", "marhta", 0.9611111111111111),
        # 1.0.1 gave no Winkler bonus to strings of up to three characters, jellyfish 1.x does
        ("jaro_winkler", "0", "00", 0.8333333333333334),
        ("jaro_winkler", "a", "ab", 0.8333333333333334),
        ("match_rating_comparison", "svchost.exe", "svch0st.exe", True),
        ("match_rating_comparison", "O'Brien", "OBrien", True),
        ("match_rating_comparison", "Smith", "Smyth", True),
    ],
)
def test_distance_results_of_1_0_1(algorithm, a, b, expected):
    (row,) = run(f"{algorithm}(a,b)", [{"a": a, "b": b}])
    assert row[algorithm] == expected


@pytest.mark.parametrize(
    ("algorithm", "word", "expected"),
    [
        ("metaphone", "laugh", "L"),  # jellyfish 1.2.1 returns LKH
        ("metaphone", "align", "ALKN"),  # jellyfish 1.x returns AL
        ("metaphone", "straße", "STR"),
        ("metaphone", "Thompson", "0MPSN"),
        ("match_rating_codex", "svchost.exe", "SVCT.X"),  # jellyfish 1.x raises an error
        ("match_rating_codex", "O'Brien", "O'BRN"),
        ("match_rating_codex", "0", "0"),
        ("match_rating_codex", "Robert", "RBRT"),
        ("porter_stem", "relational", "relat"),
    ],
)
def test_phonetic_results_of_1_0_1(algorithm, word, expected):
    (row,) = run(f"{algorithm}(w)", [{"w": word}])
    assert row[algorithm] == expected


def test_new_name_follows_jellyfish():
    # jaro_winkler_similarity is the name of jellyfish 1.x, so it keeps the Winkler bonus for short strings
    (row,) = run("jaro_winkler_similarity(a,b)", [{"a": "0", "b": "00"}])
    assert row["jaro_winkler_similarity"] == jellyfish.jaro_winkler_similarity("0", "00")
    assert row["jaro_winkler_similarity"] == 0.8500000000000001


@pytest.mark.parametrize("name", ["metaphone", "match_rating_codex", "porter_stem"])
def test_one_word_functions_reject_non_strings(name):
    with pytest.raises(TypeError):
        jellyfisher.get_function(name)(5)


@pytest.mark.parametrize("name", ["jaro_distance", "jaro_winkler", "match_rating_comparison"])
def test_two_word_functions_reject_non_strings(name):
    with pytest.raises(TypeError):
        jellyfisher.get_function(name)(5, "a")
