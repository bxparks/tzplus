# Changelog

* Unreleased
* 2023c.1 (2023-05-05, TZDB 2023c)
    * Add `DEVELOPER.md` and move internal developer notes there.
    * Rename `check_data.py` to `verify_data.py`
    * Add Installation section in README.md.
    * Make `develop` branch the default, reserving `master` for releases.
    * Makefile targets
        * Create consistent make targets in `./data/
            * `$ make verify`
            * `$ make list`
            * `$ make extract`
        * Create separate `$ make verify` target in `./geonames/`
    * ISO countries
        * Add fake `00 Nowhere` ISO country to `iso3166_xxx.txt` files.
        * Verify that `data/iso3166_xxx.txt` files match the original
          `tzdb/iso3166.tab` file.
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
