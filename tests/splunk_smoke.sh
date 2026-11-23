#!/usr/bin/env bash
# Runs one search per algorithm against a Splunk instance that has the app installed.
# Settings come from SPLUNK_HOST, SPLUNK_USER and SPLUNK_PASSWORD.
set -uo pipefail

SPLUNK_HOST="${SPLUNK_HOST:-https://localhost:8089}"
SPLUNK_USER="${SPLUNK_USER:-admin}"
SPLUNK_PASSWORD="${SPLUNK_PASSWORD:-password}"  # pragma: allowlist secret
failed=0

# check <name> <spl> <jq assertion on the first result row>
check() {
  local name="$1" spl="$2" assertion="$3" out
  out=$(curl -sk -u "${SPLUNK_USER}:${SPLUNK_PASSWORD}" "${SPLUNK_HOST}/services/search/jobs/export" \
    --data-urlencode "search=${spl}" -d output_mode=json)
  if echo "${out}" | jq -es "map(select(.result != null)) | .[0].result | ${assertion}" > /dev/null 2>&1; then
    echo "PASS ${name}"
  else
    echo "FAIL ${name}"
    echo "${out}"
    failed=1
  fi
}

# check_error <name> <spl> <text that the error message must contain>
check_error() {
  local sid out
  # the export endpoint does not always return the error message, the search job does
  sid=$(curl -sk -u "${SPLUNK_USER}:${SPLUNK_PASSWORD}" "${SPLUNK_HOST}/services/search/jobs" \
    --data-urlencode "search=$2" -d exec_mode=blocking -d output_mode=json | jq -r .sid)
  out=$(curl -sk -u "${SPLUNK_USER}:${SPLUNK_PASSWORD}" "${SPLUNK_HOST}/services/search/jobs/${sid}?output_mode=json")
  if echo "${out}" | grep -q "$3"; then
    echo "PASS $1"
  else
    echo "FAIL $1"
    echo "${out}"
    failed=1
  fi
}

distance() {  # <algorithm> <word1> <word2> <jq assertion>
  check "$1" "| makeresults | eval a=\"$2\", b=\"$3\" | jellyfisher $1(a,b)" "$4"
}

phonetic() {  # <algorithm> <word> <expected>
  check "$1" "| makeresults | eval w=\"$2\" | jellyfisher $1(w)" ".$1 == \"$3\""
}

distance levenshtein_distance kitten sitting '(.levenshtein_distance | tonumber) == 3'
distance damerau_levenshtein_distance kitten sitting '(.damerau_levenshtein_distance | tonumber) == 3'
distance hamming_distance kitten sitting '(.hamming_distance | tonumber) == 3'
distance match_rating_comparison Smith Smyth '.match_rating_comparison | tostring | test("[Tt]rue|1")'
distance jaro_similarity dixon dicksonx '(.jaro_similarity | tonumber) > 0.76 and (.jaro_similarity | tonumber) < 0.77'
distance jaro_winkler_similarity dixon dicksonx '(.jaro_winkler_similarity | tonumber) > 0.81 and (.jaro_winkler_similarity | tonumber) < 0.82'
# names used by JellyFisher 1.0.1, the output field keeps the name that was typed
distance jaro_distance dixon dicksonx '(.jaro_distance | tonumber) > 0.76 and (.jaro_distance | tonumber) < 0.77'
distance jaro_winkler dixon dicksonx '(.jaro_winkler | tonumber) > 0.81 and (.jaro_winkler | tonumber) < 0.82'

phonetic soundex Robert R163
phonetic nysiis Robert RABAD
phonetic metaphone Robert RBRT
phonetic match_rating_codex Robert RBRT
phonetic porter_stem caresses caress
# values with punctuation, as 1.0.1 accepted them
phonetic match_rating_codex svchost.exe SVCT.X
distance match_rating_comparison svchost.exe svch0st.exe '.match_rating_comparison | tostring | test("[Tt]rue|1")'

check "space after the comma" \
  '| makeresults | eval a="kitten", b="sitting" | jellyfisher levenshtein_distance(a, b)' \
  '(.levenshtein_distance | tonumber) == 3'
check "several events" \
  '| makeresults count=3 | streamstats count as n | eval w=case(n=1,"Robert",n=2,"Rupert",true(),"Rubin") | jellyfisher soundex(w) | stats dc(soundex) as d | eval ok=if(d=2,"yes","no")' \
  '.ok == "yes"'
check_error "unknown algorithm is reported" \
  '| makeresults | eval w="x" | jellyfisher not_an_algorithm(w)' \
  'is not a valid algorithm'

exit "${failed}"
