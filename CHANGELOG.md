
# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](http://semver.org/).

## [2.1.0] - 2026-11-23

### Added
- `jaro_distance`, `jaro_winkler`, and `porter_stem` work again, and the result field is named after the algorithm that you type, so searches written for 1.0.1 keep working.
- `metaphone`, `match_rating_codex`, and `match_rating_comparison` use the code of jellyfish 0.8.2 again, as in 1.0.1. jellyfish 1.2.1 returns a different `metaphone` code for 299 of 235,976 English words (for example `LKH` for "laugh" instead of `L`), and raises an error or returns no value for `match_rating_*` when a value has digits, punctuation, or non-ASCII letters, such as `svchost.exe`.
- `app.manifest`, third-party licence notices, and a binary file declaration for the compiled jellyfish module.
- Unit tests with pytest, and a smoke test that runs every algorithm on a Splunk instance.

### Changed
- The project moved from `splunk/jellyfisher-app` to `splunk-platform-apps/jellyfisher_app_for_splunk` and follows the organization structure and pipelines. The app ID is still `jellyfisher`, so the app upgrades in place from 1.0.1 and 2.0.0.
- The app is built with the UCC framework (`ucc-gen`). The jellyfish builds for each platform and Python version, and the Splunk SDK, are installed at build time and are no longer committed.
- The documentation is in `docs/readme.md`.
- Every algorithm that 1.0.1 had returns exactly the same value as 1.0.1, in a test of 2,546,672 calls. The only exception is the new name `jaro_winkler_similarity`, which follows jellyfish 1.x and gives a Winkler bonus to strings of up to three characters, as in 2.0.0.
- Tested on Splunk Enterprise 9.3.0 and 10.0.1 (Python 3.9) and 10.6.1.1 (Python 3.13), with a new install and with an update from 1.0.1 that keeps the files in `local`.

### Fixed
- The command no longer looks for its libraries in `$SPLUNK_HOME/etc/apps/jellyfisher/lib`. It finds them relative to the script, so it also works where the app directory differs, for example on indexers.
- The list of fields that the command reads no longer grows with every chunk of events.
- The libraries bundled with the app are used before any library of the same name that Splunk puts on the Python path.
- The knowledge objects of the app can be changed by the `sc_admin` role, the administrator role in Splunk Cloud.
