# tzplus

This repository contains data files which extend the functionality of the data
files of the [IANA TZDB](https://github.com/eggert/tz) timezone database.

The main purpose of this project is to generate the
[country_timezone.txt](data/country_timezones.txt) file which contains ~480
*significant* IANA timezones (out of a total of ~600 timezones in the raw TZDB
files) organized into regions (continents or oceans) and their respective ISO
3166 countries. The goal is to ensure that every ISO country has at least one
timezone, and every timezone is assigned to at least one ISO country. This
allows a user-interface to present timezones as a nested hierarchy of regions,
countries, and timezones.

The `country_timezones.txt` data was originally intended for user-interfaces
running on microcontrollers with limited memory, small displays, and restricted
input devices. (Although nothing prevents the file from being used in other
computer environments with far more resources.) These microcontrollers do not
support a POSIX-compatible libc library.

**Disclaimer**: This project is not related to the TZDB project, the IANA
organization, or any other government or quasi-government agency. A timezone may
be assigned to the wrong ISO country due to a typo or a clerical error. Please
submit a bug report to fix this. In a few rare cases, a subjective judgement
call was made. If you disagree with the result, you may try to convince the
maintainer of this project to make changes. If you are unsuccessful, you have
the option to fork this database and make the changes yourself. This project and
its data are published into the public domain.

**Version**: 0.0 (2023-05-03, TZDB 2023c)

**Changelog**: [CHANGELOG.md](CHANGELOG.md)

**See Also**:

* [IANA TZDB](https://github.com/eggert/tz)
* [AceTime](https://github.com/bxparks/AceTime) (Arduino C++)

## Table of Contents

* [Motivation](#Motivation)
* [TZDB Deficiencies](#TzdbDeficencies)
* [The Data Files](#DataFiles)
* [Validation](#Validation)
* [List Time Zones](#ListTimeZones)
* [Methodology](#Methodology)
* [Upgrading to New TZDB](#UpgradingTZDB)
* [Alternatives Considered](#AlternativesConsidered)
* [Appendix: Merged TZDB Timezones After 1970](#MergedTimezonesAfter1970)
* [Bugs and Limitations](#Bugs)
* [License](#License)
* [Feedback and Support](#FeedbackAndSupport)
* [Authors](#Authors)

<a name="Motivation"></a>
## Motivation

The driving motivation for this project is to allow the creation of
user-interfaces to select timezones which can be used by microcontrollers in
bare-metal environments without an underlying operation system. Such
environments can be resource constrained in many ways:

* limited RAM size (e.g. 2 kB - 256 kB)
* limited flash size (e.g. 32 kB - 4 MB)
* limited display size (e.g. seven-segment LED, 84x48 LCD, 128x64 OLED)
* limited input (e.g. micro buttons, rotary buttons)
* limited font (e.g. ASCII-only, no Unicode)

In these environments:

* there is no POSIX-compatible libc timezone library
* there is no underlying operating system or file system
* there is not enough memory to store a graphical world map
* the display may not support bit-mapped graphics
* the display supports only ASCII characters, no Unicode
* the display may be small and display only one or two timezones at a time
* a keyboard or mouse may not exist
* the input device may be only 1 or 2 buttons

Assuming that only short (about 10-15 characters or less) can be displayed at a
time, we want to present the timezones to the user, in a hierarchical structure,
starting from the largest geopolitical areas (continents, oceans), then the ISO
countries, then display the timezones which often map to cities. Ideally, the
cities would be sorted in a reasonable manner (alphabetically, geographically
(West to East), or by UTC time offset).

<a name="TzdbDeficencies"></a>
## TZDB Deficiencies

There are roughly 600 timezone identifiers in the TZDB (350 Zone entries and 246
Link entries in version 2023c). The identifiers have the form `{region}/{city}`,
where the `region` is usually a continent (e.g. `Asia`) or an ocean (e.g.
`Pacific`).

There are 3 problems with these IANA identifiers in the context of this project:

1)) The country is explicitly excluded for various reasons:

* city names are more stable than country names,
* cities often change countries due to redrawn borders after wars,
* the country of a city can be in dispute due to disputed borders.

The exclusion of the country makes the maintenance of the TZDB easier, but it
causes usability issues for the end users. Most end users still prefer to
categorize cities into countries, and countries into continents or regions.

2)) The `region` component of the timezone identifier uses a single `America`
identifier to identify timezones in both South America and North America. That
means about 170 timezones are under the `America/` prefix which is too large to
navigate over easily in a microcontroller environment. The TZDB provides no
obvious way to organize them in a sensible manner for the end users.

3)) Starting with TZDB 2021b in Sept 2021, unrelated timezones have been
progressively merged (converted into Link entries), if those timezones happen to
have the same DST transition rules since the year 1970. (See [Merged Timezones
After 1970](#MergedTimezonesAfter1970) below.) Many timezone libraries do not
distinguish between Zone and Link entries, so are not directly impacted by
these merges at the lowest level.

However, the [zone1970.tab](https://github.com/eggert/tz/blob/main/zone1970.tab)
file provided by the TZDB project is negatively impacted by these merges. It
organizes the time zones into countries, but it now maps the timezones of
certain countries into unrelated countries, simply because their timezones
happen to have the same transition rules since 1970. For example, `zone1970.tab`
says that Bahamas (ISO code BS) uses `America/Toronto`, but it would be more
accurate and useful to map Bahamas to `America/Nassau`. The result is that the
`zone1970.tab` is unsuitable for creating a timezone selector that corresponds
to how most people think about timezones.

<a name="DataFiles"></a>
## The Data Files

This project contains a set of both auto-generated and manually-curated data
files which build on top of the raw timezone files provided by the IANA TZDB.
The primary product is the [country_timezones.txt](data/country_timezones.txt)
file which contains a list of *significant* timezones, organized into regions
and ISO country codes. This file is intended to supersede the `zones1970.tab`
file from the TZDB.

The list of regions (continents and oceans) is somewhat arbitrary, and is guided
by ease of usability in the user-interface, instead of strict adherence to how
the world is divided geographically. For the purposes of this project, the
regions are defined in the [regions.txt](data/regions.txt) file. Currently, the
regions are:

* Africa
* Antarctica
* Asia
* Atlantic Ocean
* Australia
* Central America (includes the Caribbean islands)
* Etcetera (for timezones without an association with a region, e.g. `UTC`)
* Europe
* Indian Ocean
* North America
* Pacific Ocean
* South America

The [ISO 3166](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes)
list of countries was copied from the `iso3166.tab` file from the IANA TZDB,
then manually edited into [iso3166_long.txt](data/iso3166_long.txt) and
[iso3166_short.txt](data/iso3166_short.txt). All non-English names were
converted to their common English names. All non-ASCII characters were converted
to their approximate ASCII characters. This allows easier implementations on
microcontroller environments without support for Unicode.

The determination of which timezones are *significant* enough to be presented in
a user-interface is defined by:

* [classified_zones.txt](data/classified_zones.txt)
* [classified_links.txt](data/classified_links.txt)

Most of the work involved undoing the merging of unrelated timezones which
started with TZDB 2021b (see [Merged Timezones After
1970](#MergedTimezonesAfter1970) below). Another major effort was figuring out
which timezones are obsolete and no longer commonly used. Since I do not have
complete knowledge of every use of every timezone around the world, some of this
required guesswork.

The `country_timezones.txt` file is intended to have the property that every
timezone is assigned to at least one ISO country, and every ISO country has at
least one timezone. There are a few exceptions to those rules:

* Two ISO countries are currently uninhabited, therefore do not have a
  timezone, so are missing from that file:
    * `BV` Bouvet Island
    * `HM` Heard Island & McDonald Islands
* Two timezones are synthetic, and do not correspond to an ISO country. These
  are given the fake ISO code of `00`, and assigned to the region `Etcetera`:
    * `UTC`
    * `Etc/UTC`

Here is the quick description of some of the other files in this repository:

* [tools/](tools)
    * Bash and Python scripts for processing various text files.
* [tzdb/](tzdb)
    * The raw TZDB data files (without C code or scripts) extracted from a
      particular tagged version of the https://github.com/eggert/tz repository.
    * These are vendored into this project so that downstream derivative files
      can be regenerated even if the TZDB repository becomes unavailable.
    * [version.txt](tzdb/version.txt)
        * Contains the version string of the original TZDB files.
* [geonames/](geonames)
    * [timeZones.txt](geonames/timeZones.txt)
        * Vendored copy of
          https://download.geonames.org/export/dump/timeZones.txt
* [data/](data)
    * [links.txt](data/links.txt)
        * `Link` entries from the [tzdb/](tzdb) raw files, auto-extracted by a
          shell script.
    * [zones.txt](data/zones.txt)
        * `Zone` entries from the [tzdb/](tzdb) raw files, auto-extracted by a
          shell script.
    * [classified_zones.txt](data/classified_zones.txt)
        * Manually derived from `zones.txt`, each `Zone` entry is subclassified
          into a `Zone` or `ZoneObsolete` entry.
        * The `tools/check_data.py` script validates that every `zones.txt`
          entry exists in the `classified_zones.txt` file.
    * [classified_links.txt](data/classified_links.txt)
        * Manually derived from `links.txt`, each `Link` entry is subclassified
         into one of the following subcategories:
            * `Similar`
            * `Alternate`
            * `Alias`
            * `Obsolete`
        * The `tools/check_data.py` script validates that every `zones.txt`
          entry exists in the `classified_zones.txt` file.
    * [iso3166_long.txt](data/iso3166_long.txt)
        * List of [ISO 3166
          countries](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes)
          with their 2-letter codes and a long version of the country name.
    * [iso3166_short.txt](data/iso3166_short.txt)
        * Same as `iso3166_long.txt` but with country names shortened to be
          13 characters or less.
        * Suitable for small LCD or OLED displays.
    * [regions.txt](data/regions.txt)
        * List of the top-level continents and oceans.
    * [country_timezones.txt](data/country_timezones.txt)
        * The final list of regions, countries, and their timezones.

<a name="Validation"></a>
## Validation

The `make` command runs the [check_data.py](tools/check_data.py) script which
runs a series of validations on the various files. The output looks like this:

```
$ cd data
$ make
zones.txt: 350
links.txt: 246
classified_zones.txt: 350
classified_links.txt: 246
iso3166_long.txt: 249, maxlen: 42
iso3166_short.txt: 249, maxlen: 13
regions.txt: 12, maxlen: 15
country_timezones.txt: regions=12, countries=247, timezones=480
Timezones with multiple countries:
  America/Marigot: ['MF', 'SX']
  Europe/Simferopol: ['RU', 'UA']
  Indian/Chagos: ['MU', 'IO']
```

<a name="ListTimeZones"></a>
## List Time Zones

See visualize the hierarchical list of timezones encoded in the
`country_timezones.txt` file, you can run the
[list_zones.py](tools/list_zones.py) script. The easy way to run this is to use
the Makefile rule:

```
$ cd data
$ make list
Africa (AF)
    Angola (AO)
        Africa/Luanda
...
Antarctica (AN)
    Antarctica (AQ)
        Antarctica/Casey
        Antarctica/Davis
...
Atlantic Ocean (AO)
    Bermuda (BM)
        Atlantic/Bermuda
...
Asia (AS)
    UAE (AE)
        Asia/Dubai
...
Australia (AU)
    Australia (AU)
        Australia/Adelaide
        Australia/Brisbane
...
Central America (CA)
    Antigua (AG)
        America/Antigua
...
Etcetera (ET)
    None (00)
        Etc/UTC
        UTC
...
Europe (EU)
    Andorra (AD)
        Europe/Andorra
...
Indian Ocean (IO)
    Cocos Is (CC)
        Indian/Cocos
...
North America (NA)
    Canada (CA)
        America/Atikokan
        America/Blanc-Sablon
...
Pacific Ocean (PO)
    Am Samoa (AS)
        Pacific/Midway
        Pacific/Pago_Pago
...
South America (SA)
    Argentina (AR)
        America/Argentina/Buenos_Aires
        America/Argentina/Catamarca
...
```

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

<a name="TimezonesInMultipleCountries"></a>
## Timezones in Multiple Countries

There are a handful of timezones which are assigned to multiple countries. The
reasons for the multiple assignments are explained in the
[country_timezones.txt](data/country_timezones.txt) file.

<a name="UpgradingTZDB"></a>
## Upgrading to New TZDB

When a new TZDB version is released, here are the steps to generate the
`country_timezones.txt` file:

1. Update the `TZDB_VERSION` variable in the [Makefile](Makefile) to the latest
TZDB version
1. `$ make tzdb` to regenerate the `tzdb` directory
1. `$ cd data`
1. `$ make` to run `tools/check_data.py` to validate various files.
    * Edit `iso3166_long.txt` and `iso3166_short.txt` to add/remove countries.
    * Edit `classified_zones.txt` to add/remove Zone entries.
    * Edit `classified_links.txt` to add/remove Link entries.
    * Edit `country_timezones.txt` to add/remove timezones.
    * Repeat running `make` to check for errors.
1. Update version to something like `{tzversion}.N`
    * Update the `CHANGELOG.md`
    * Update the Version in `README.md`
1. `$ git add ....`
1. `$ git commit ....`
1. `$ git push`
1. Go to https://github.com/bxparks/tzplus
    * Create a new release with new tag of the form `{tzversion}.N`

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

<a name="MergedTimezonesAfter1970"></a>
## Appendix: Merged Timezones After 1970

Starting with [TZDB
2021b](https://mm.icann.org/pipermail/tz-announce/2021-September/000066.html),
in Sept 2021, many unrelated timezones have become merged together if they
happened to have the same DST transition rules since the year 1970. For example,
The Zone `America/Nassau` in the Bahamas was replaced with a Link to
`America/Toronto` because Nassau has the same timezone rules as Toronto since
1970, even through the Bahamas and Canada are 2 separate countries which
legislate their timezones independently.

These consolidations generated considerable controversy. See the IANA email
archives and the LWN.net article:

* https://mm.icann.org/pipermail/tz/2021-May/thread.html#30071: Avoid backward links in zone.tab
* https://mm.icann.org/pipermail/tz/2021-June/thread.html#30175: Merge timezones that are alike since 1970
* https://mm.icann.org/pipermail/tz/2021-June/thread.html#30220: Undoing the effect of the new alike-since-1970 patch
* https://mm.icann.org/pipermail/tz/2021-June/thread.html#30223: What data should TZDB offer
* https://mm.icann.org/pipermail/tz/2021-September/thread.html#30400: Preparing to fork tzdb
* https://mm.icann.org/pipermail/tz/2021-September/thread.html#30478: Replacing the TZ Coordinator
* https://mm.icann.org/pipermail/tz/2021-September/thread.html#30517: Issues with pre-1970 information in TZDB
* https://mm.icann.org/pipermail/tz/2021-September/thread.html#30535: proposal for new tzdb versions
* https://mm.icann.org/pipermail/tz/2021-September/thread.html#30659: Some thoughts about the way forward
* https://mm.icann.org/pipermail/tz/2021-November/thread.html#31023: Pre-1970 data
* https://mm.icann.org/pipermail/tz/2022-March/thread.html#31307: Announcing global-tz - 2022ag (beta)
* https://mm.icann.org/pipermail/tz/2022-July/thread.html#31631: Moving more zones to 'backzone'
* https://mm.icann.org/pipermail/tz/2022-August/thread.html#31752: Moving more zones to 'backzone'
* https://lwn.net/Articles/870478/: A fork for the time-zone database?

<a name="Bugs"></a>
## Bugs and Limitations

* The `Etc/UTC` and `UTC` timezones are assigned a fake ISO country code of
  `00`.
    * This code does *not* exist in either `iso3166_long.txt` or
      `iso3166_short.txt` files.
    * This fake ISO country code may be added to those files in the future to
      make downstream client code easier to write by eliminating special
      handling.
* In some microcontroller environments, even the short names provided by
  `iso3166_short.txt` may not be short enough.
    * It might be necessary to simply use the 2-letter ISO codes instead.
* There is no "short" version of the `regions.txt` file.
    * There are currently only 12 regions defined, so it should be relatively
      easy for client applications to create their own short versions of these
      regions.
* The region codes in `regions.txt` are 2-letter codes that look similar to ISO
  3166 2-letter codes.
    * It is possible that this might cause confusion if they are shown to the
      end users without clear context.

<a name="License"></a>
## License

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

[The Unlicense](https://unlicense.org/)

<a name="FeedbackAndSupport"></a>
## Feedback and Support

If you have any questions, comments, or feature requests for this project,
please use the [GitHub
Discussions](https://github.com/bxparks/tzplus/discussions). If you have bug
reports, please file a ticket in [GitHub
Issues](https://github.com/bxparks/tzplus/issues). Feature requests should go
into Discussions first because they often have alternative solutions which are
useful to remain visible, instead of disappearing from the default view of the
Issue tracker after the ticket is closed.

Please refrain from emailing me directly unless the content is sensitive. The
problem with email is that I cannot reference the email conversation when other
people ask similar questions later.

<a name="Authors"></a>
## Authors

* Created by Brian Park (brian@xparks.net)
