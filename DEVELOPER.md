# Developer Notes

Information which are useful for developers and maintainers of the `tzplus`
repository.

## Table of Contents

* [Prerequisites](#Prerequisites)
* [Methodology](#Methodology)
* [Upgrading to New TZDB](#UpgradingTZDB)

<a name="Prerequisites"></a>
## Prerequisites

* Operating System
    * Ubuntu Linux, probably 18.04 or greater
    * I use Linux Mint 21.1 (Ubuntu 22.04)
* Python 3.7 or greater
    * `flake8` to run syntax linting
    * `mypy` to run type checking
* `make` (GNU Make)
* `git`
* `git clone https://github.com/eggert/tz` as a sibling directory to `tzplus`

<a name="Methodology"></a>
## Methodology

The following steps were used to create the final `country_timezones.txt` file:

1. Zone entries were programmatically extracted into
   [zones.txt](data/zones.txt).
1. Link entries were programmatically extracted into
   [links.txt](data/links.txt).
1. Zone entries were categorized as either `Zone` or `ZoneObsolete`.
    * Saved into [classified_zones.txt](data/classified_zones.txt).
1. Link entries were reorganized to undo the effects of the post-1970 merging.
    * Each `Link` entry was reclassified as `Similar`, `Alternate`, `Alias`,
      `Obsolete`
    * Saved into [classified_links.txt](data/classified_links.txt).
1. ISO 3166 country codes and names were reformatted from `iso3166.tab`:
    * [iso3166_long.txt](data/iso3166_long.txt) contain long, usually the full,
      names of countries.
    * [iso3166_short.txt](data/iso3166_short.txt) contain short abbreviated
      names of countries.
    * Non-English names (e.g. French, Dutch, Portuguese) names were converted
      into their common English names.
    * Non-ASCII characters were mapped to their approximate ASCII characters.
1. Timezone to Country mapping
    * Timezones of significance (defined as `Zone`, `Similar`, and `Alternate`)
      were copied into [country_timezones.txt](data/country_timezones.txt)
      into a (country, timezone) pair.
    * Each timezone was assigned an ISO 3166 country code.
1. Regions (continents and oceans) were defined in
   [regions.txt](data/regions.txt).
    * The single identifier `America` was split into 3: North America, Central
      America, and South America.
1. Region mapping
    * Each (country, timezone) pair was assigned a `region` into a (region,
      country, timezone) triplet.
    * Some countries (e.g. France, Britain, US) spanned multiple regions
      because of their historical territorial holdings. Therefore, the region
      assignment had to be done against the (country, timezone) pair, instead of
      just to the country.

Here is a rough diagram of the data processing pipeline:

```
         github.com/eggert/tz
                 |
                 | (make tzdb)
                 v
               tzdb/
(make extract) /    \
              /      \
             v        v
      zones.txt     iso3166_long.txt
      links.txt     iso3166_short.txt
         |              |
         |              |
         v              |
classified_zones.txt    |
classified_links.txt    |       regions.txt
                \       |          /
                 \      |         /
                  v     v        v
              country_timezones.txt
                  /         \
     (make list) /           \ (make verify)
                v             v
        list_zones.py      verify_data.py
```

<a name="UpgradingTZDB"></a>
## Upgrading to New TZDB

When a new TZDB version is released, here are the steps to generate the
`country_timezones.txt` file:

1. Update the `TZDB_VERSION` variable in the [Makefile](Makefile) to the latest
TZDB version
1. `$ make clean` to remove the `./tzdb/` directory
1. `$ make tzdb` to regenerate the `tzdb` directory
1. `$ cd data`
1. `$ make extract` to extract the Zone and Link entries into `zones.txt` and
   `links.txt`
1. `$ make verify` to run `tools/verify_data.py` to validate various files.
1. If there are any warning or errors, edit various files to bring them into
   compliance:
    * Edit `iso3166_long.txt` and `iso3166_short.txt` to add/remove countries.
    * Edit `classified_zones.txt` to add/remove Zone entries.
    * Edit `classified_links.txt` to add/remove Link entries.
    * Edit `country_timezones.txt` to add/remove timezones.
    * Repeat `make verify` to check for errors.
1. Update version in the form of `{tzversion}.N`
    * Update the `CHANGELOG.md`
    * Update the Version in `README.md`
1. `$ git add ....`
1. `$ git commit ....`
1. `$ git push`
1. Go to https://github.com/bxparks/tzplus
    * Create a new release with new tag of the form `{tzversion}.N`
1. `$ git pull` to retrieve new tag created by GitHub

<a name="AlternativesConsidered"></a>
## Alternatives Considered

* [GeoNames database](https://www.geonames.org/)
    * organizes geographical names and provides downloadable files
    * [timeZones.txt](https://download.geonames.org/export/dump/timeZones.txt)
      contains timezones assigned to an ISO 3166 country.
    * but it is unclear how this file was created, how it is maintained,
      and how quickly it is updated when a new TZDB version is released.
* [CLDR](https://cldr.unicode.org/) - Unicode Common Locale Data Repository
    * This project is complex, and I cannot figure out what it provides and
      how to use it.
    * For the purposes of creating a user-interface for microcontroller
    * environments, I did not want to depend on another large, complex project.
* [ICU](https://icu.unicode.org/) - International Components for Unicode
    * Provides libraries suitable for desktop class machines,
      not resource-constrained microcontrollers
    * Similar to CLDR, I did not want to depend on another large, complex
      project.
