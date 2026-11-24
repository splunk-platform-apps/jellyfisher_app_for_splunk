
# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](http://semver.org/).

## [2.1.0] - 2026-11-23

### Added
- `app.manifest`, third-party licence notices, and a binary file declaration for the compiled jellyfish module.
- Unit tests with pytest, and a smoke test that runs every algorithm on a Splunk instance.

### Changed
- The app is built with the UCC framework (`ucc-gen`). The jellyfish builds for each platform and Python version, and the Splunk SDK, are installed at build time and are no longer committed.
- `metaphone`, `match_rating_codex`, and `match_rating_comparison` use the code of jellyfish 0.8.2 again, as in 1.0.1. This restores the 1.0.1 results for `metaphone` and allows `match_rating_*` to handle values with digits, punctuation, or non-ASCII letters, such as `svchost.exe`.

### Fixed
- `jaro_distance`, `jaro_winkler`, and `porter_stem` work again, and the result field is named after the algorithm typed, so searches written for 1.0.1 keep working.
- The command no longer looks for its libraries in `$SPLUNK_HOME/etc/apps/jellyfisher/lib`. It finds them relative to the script, so it also works where the app directory differs, for example on indexers.
- The list of fields that the command reads no longer grows with every chunk of events.
- The libraries bundled with the app are used before any library of the same name that Splunk puts on the Python path.
- The knowledge objects of the app can be changed by the `sc_admin` role, the administrator role in Splunk Cloud.
