import jellyfish
import jellyfisher
import pytest


def run(argument, records):
    command = jellyfisher.JellyfisherCommand()
    command._fieldnames = [argument]
    return list(command.stream(iter(records)))


@pytest.mark.parametrize(
    ("old", "new"),
    [("jaro_distance", "jaro_similarity"), ("jaro_winkler", "jaro_winkler_similarity")],
)
def test_old_names_give_the_same_result_as_the_new_names(old, new):
    (old_row,) = run(f"{old}(a,b)", [{"a": "dixon", "b": "dicksonx"}])
    (new_row,) = run(f"{new}(a,b)", [{"a": "dixon", "b": "dicksonx"}])
    assert old_row[old] == new_row[new] == getattr(jellyfish, new)("dixon", "dicksonx")


def test_output_field_is_named_after_the_algorithm_that_was_typed():
    (row,) = run("jaro_distance(a,b)", [{"a": "x", "b": "x"}])
    assert row["jaro_distance"] == 1.0
    assert "jaro_similarity" not in row


@pytest.mark.parametrize(
    ("word", "stem"),
    [
        ("caresses", "caress"),
        ("ponies", "poni"),
        ("cats", "cat"),
        ("hopping", "hop"),
        ("relational", "relat"),
    ],
)
def test_porter_stem(word, stem):
    (row,) = run("porter_stem(w)", [{"w": word}])
    assert row["porter_stem"] == stem


def test_porter_stem_rejects_non_strings():
    with pytest.raises(TypeError):
        jellyfisher.get_function("porter_stem")(42)


@pytest.mark.parametrize(
    ("argument", "expected"),
    [
        ("levenshtein_distance(a,b)", 3),
        ("damerau_levenshtein_distance(a,b)", 3),
        ("hamming_distance(a,b)", 3),
    ],
)
def test_distance_algorithms(argument, expected):
    (row,) = run(argument, [{"a": "kitten", "b": "sitting"}])
    assert row[argument.split("(")[0]] == expected


@pytest.mark.parametrize(
    ("algorithm", "expected"),
    [
        ("soundex", "R163"),
        ("nysiis", "RABAD"),
        ("metaphone", "RBRT"),
        ("match_rating_codex", "RBRT"),
    ],
)
def test_phonetic_algorithms(algorithm, expected):
    (row,) = run(f"{algorithm}(w)", [{"w": "Robert"}])
    assert row[algorithm] == expected


def test_soundex_matches_for_similar_names():
    rows = run("soundex(w)", [{"w": "Robert"}, {"w": "Rupert"}])
    assert rows[0]["soundex"] == rows[1]["soundex"] == "R163"


def test_other_fields_of_the_record_are_kept():
    (row,) = run("soundex(w)", [{"w": "Robert", "host": "h1"}])
    assert row["host"] == "h1"


@pytest.mark.parametrize(
    ("argument", "message"),
    [
        ("not_an_algorithm(a,b)", "is not a valid algorithm"),
        ("soundex(a,b)", "phonetic algorithms takes one argument"),
        ("jaro_distance(a)", "distance algorithms takes two arguments"),
        ("soundex(lookup:x)", "lookups cannot be used with phonetic"),
    ],
)
def test_invalid_arguments(argument, message):
    with pytest.raises(ValueError, match=message):
        run(argument, [{"a": "x", "b": "y"}])


def test_distance_with_a_lookup_is_not_supported_yet():
    with pytest.raises(ValueError, match="unsupported yet"):
        run("levenshtein_distance(a,lookup:b)", [{"a": "x"}])


def test_fields_do_not_accumulate_between_chunks():
    command = jellyfisher.JellyfisherCommand()
    command._fieldnames = ["levenshtein_distance(a,b)"]
    for _ in range(3):
        list(command.stream(iter([{"a": "x", "b": "y"}])))
    assert command.req_fields == ["a", "b"]
