# Changelog

* Unreleased
    * Create consistent make targets in `./data/` into:
        * `$ make verify`
        * `$ make list`
        * `$ make extract`
    * Create separate `$ make verify` target in `./geonames/`
    * Rename `check_data.py` to `verify_data.py`
    * Add `DEVELOPER.md` and move internal developer notes there.
* 2023c.0 (2023-05-04, TZDB 2023c)
    * Add `regions.txt` and a `region` column to `country_timezones.txt`.
    * Add `list_zones.py` which prints out `country_timezones.txt` in as a
      hierarchical list of (region, country, timezones).
    * Create README.md, CHANGELOG.md.
    * Create initial version of `country_timezones.txt` without continent or
      region mapping.
    * First initial release.
* 0.0 (2023-04-19)
    * Create project
