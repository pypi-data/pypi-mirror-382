# Changelog

## Release v0.0.6 (2025-09-22)

### 🐛 Bug Fixes and Closed Issues

- Fixed `ImportError` when installing in editable mode by replacing `miniver` with `setuptools_scm`, adding a fallback version detection in `__init__.py`, and removing obsolete `setup.py` ([!61](https://gitlab.com/quantify-os/quantify/-/merge_requests/61) by [@Mahmut Cetin](https://gitlab.com/MahmutCetin)).
- Updated type hint in `set_setuptitle_from_dataset` to accept `SubFigure` ([!59](https://gitlab.com/quantify-os/quantify/-/merge_requests/59) by [@Timo van Abswoude](https://gitlab.com/Timo_van_Abswoude)).

### 🚀 Features

- Added optional `load_metadata` flag to `load_settings_onto_instrument`, allowing metadata to be reloaded for database-backed parameters while maintaining backward compatibility ([!60](https://gitlab.com/quantify-os/quantify/-/merge_requests/60) by [@Timo van Abswoude](https://gitlab.com/Timo_van_Abswoude)).
- Refined type hint for `BaseAnalysis.run` to return `Self` instead of `BaseAnalysis` ([!63](https://gitlab.com/quantify-os/quantify/-/merge_requests/63) by [@Timo van Abswoude](https://gitlab.com/Timo_van_Abswoude)).

### 🔧 Other

- Improved documentation UI/UX: removed duplicate search bar, aligned logo with navbar, unified OQS-doc icon link, added theme switching, renamed "Examples and how-to guides" to "Examples", and migrated from `RELEASE_NOTES` to `CHANGELOG.md` ([!58](https://gitlab.com/quantify-os/quantify/-/merge_requests/58) by [@Kristian Gogora](https://gitlab.com/kikigogo9-OQS)).

## Release v0.0.5 (2025-09-02)

### 🐛 Bug Fixes and Closed Issues

### 🚀 Features

- Added Pytest CI jobs for Windows and macOS across multiple Python versions ([!55](https://gitlab.com/quantify-os/quantify/-/merge_requests/55) by [@Mahmut Cetin](https://gitlab.com/MahmutCetin)).
- Introduced use of a static template for generating compilation files: moved generation logic to `device_element`, enabled child-class template overrides and extensions, improved `transmon_element` to reuse base logic from quantify ([!53](https://gitlab.com/quantify-os/quantify/-/merge_requests/53) by [@Dianto Bosman](https://gitlab.com/DiantoBosman)).
- Integrated Quantify-Core changes for ongoing compatibility: ported Merge Requests 566 and 568 into the `quantify` repository ([!56](https://gitlab.com/quantify-os/quantify/-/merge_requests/56), [!57](https://gitlab.com/quantify-os/quantify/-/merge_requests/57) by [@Mahmut Cetin](https://gitlab.com/MahmutCetin)).
- Expanded CI testing to support Python 3.10, 3.11, and 3.12; added parallel testing, Qt GUI support with ‘screen use’, pip and apt caching strategies ([!51](https://gitlab.com/quantify-os/quantify/-/merge_requests/51) by [@Mahmut Cetin](https://gitlab.com/MahmutCetin)).

### 🔧 Other

- Synced repository with upstream core changes to maintain consistency (#core-sync-july2025) ([!48](https://gitlab.com/quantify-os/quantify/-/merge_requests/48) by [@Olga Lebiga](https://gitlab.com/OlgaLebiga)).
- Resolved type-checking issues flagged by Pyright in the SCQT codebase ([!54](https://gitlab.com/quantify-os/quantify/-/merge_requests/54) by [@Mahmut Cetin](https://gitlab.com/MahmutCetin)).
