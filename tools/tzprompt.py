#!/usr/bin/env python3
#
# Copyright 2023 Brian T. Park
#
# MIT License.

"""
Proof of concept of a text-based, interactive, hierarchical menu of timezones,
organized by region (continent), country, and timezones. The timezones are
sorted by their STDOFF fields.

This script depends on the normalized timezone, airport, and stdoff files in the
./data/ directory.
"""

import argparse
import logging
import sys
# from pprint import pp

from typing import Dict
from typing import List
from typing import Tuple
from typing import Optional
from typing import TextIO


# Country code-> Country name
CountryNames = Dict[str, str]

# Region code -> name
RegionNames = Dict[str, str]

# Country code -> timezones[]
CountryTimezones = Dict[str, List[str]]

# Region code -> CountryMap
RegionCountryTimezones = Dict[str, CountryTimezones]

# Airport code -> TimeZone
AirportTimezones = Dict[str, str]

# Timezone -> stdoff(int)
Stdoffs = Dict[str, int]

# {region -> {country -> {index -> (timezone, stdoff)}}}
TimezoneMenu = Dict[str, Dict[str, Dict[int, Tuple[str, int]]]]


def main() -> None:
    parser = argparse.ArgumentParser(description='Prompt for timezone.')

    # Extractor flags.
    parser.add_argument(
        '--db_dir',
        help='Location of the timezone datanase files',
        required=True)

    # Parse the command line arguments
    args = parser.parse_args()

    # Configure logging. This should normally be executed after the
    # parser.parse_args() because it allows us set the logging.level using a
    # flag.
    logging.basicConfig(level=logging.INFO)

    # How the script was invoked
    # invocation = ' '.join(sys.argv)

    regions = read_regions(args.db_dir)
    countries = read_countries(args.db_dir)
    stdoffs = read_stdoffs(args.db_dir)
    region_country_timezones = read_region_country_timezones(args.db_dir)
    airport_timezones = read_airport_timezones(args.db_dir)
    menu = create_timezone_menu(region_country_timezones, stdoffs)

    while True:
        select_timezone(regions, countries, stdoffs, menu, airport_timezones)
        print()


# -----------------------------------------------------------------------------
# Select timezone
# -----------------------------------------------------------------------------


def create_timezone_menu(
    region_country_timezones: RegionCountryTimezones,
    stdoffs: Stdoffs,
) -> TimezoneMenu:
    menu: TimezoneMenu = {}
    for region, country_timezones in sorted(region_country_timezones.items()):
        ctz = menu.get(region)
        if ctz is None:
            ctz = {}
            menu[region] = ctz

        for country, timezones in sorted(country_timezones.items()):
            tzmenu = ctz.get(country)
            if tzmenu is None:
                tzmenu = {}
                ctz[country] = tzmenu

            # Create index of timezones, sorted by their STDOFF
            tzbystdoff: List[Tuple[str, int]] = [
                (name, stdoffs[name])
                for name in timezones
            ]
            tzbystdoff.sort(key=lambda item: item[1])
            i = 0
            for item in tzbystdoff:
                tzmenu[i] = item
                i += 1

    return menu


def select_timezone(
    regions: RegionNames,
    countries: CountryNames,
    stdoffs: Stdoffs,
    menu: TimezoneMenu,
    airport_timezones: AirportTimezones,
) -> str:
    while True:
        print("Select region:")
        for region, _ in menu.items():
            name = regions.get(region)
            print(f"{region} - {name}")
        region = input('region (q to quit)> ')
        if region == 'q':
            sys.exit(0)
        country_timezones = menu.get(region)
        if country_timezones is not None:
            break
        print(f"ERROR: Unknown region {region}")
    region_name = regions.get(region)

    while True:
        print(f"Select country for {region} - {region_name}:")
        for country, _ in country_timezones.items():
            name = countries.get(country)
            print(f"{country} - {name}")
        country = input('country (q to quit)> ')
        if country == 'q':
            sys.exit(0)
        timezones = country_timezones.get(country)
        if timezones is not None:
            break
        print(f"ERROR: Unknown country {country}")
    country_name = countries.get(country)

    while True:
        print("Select timezone:")
        for index, timezone in timezones.items():
            print(f"[{index}] {timezone}")
        selection = input('timezone [selection] (q to quit)> ')
        if selection == 'q':
            sys.exit(0)

        try:
            i = int(selection)
        except ValueError:
            print(f"ERROR: Invalid index {selection}")
            continue
        if i in timezones:
            break
        print(f"ERROR: Unknown index {i}")

    tz = timezones[i]
    name = tz[0]
    print(f"Selected '{name}' in '{region_name}'/'{country_name}'")

    return name


# -----------------------------------------------------------------------------
# Read files
# -----------------------------------------------------------------------------


def read_regions(db_dir: str) -> RegionNames:
    filename = db_dir + "/regions.txt"
    regions: RegionNames = {}
    with open(filename, "r", encoding='utf-8') as f:
        while True:
            line = read_line(f)
            if line is None:
                break

            tokens = line.split()
            if len(tokens) > 3:
                raise ValueError(
                    f"Expected 2 or 3 tokens but got {len(tokens)}")

            code = tokens[0]
            name = ' '.join(tokens[1:])

            regions[code] = name

    return regions


def read_countries(db_dir: str) -> CountryNames:
    filename = db_dir + "/iso3166_short.txt"
    countries: CountryNames = {}
    with open(filename, "r", encoding='utf-8') as f:
        while True:
            line = read_line(f)
            if line is None:
                break

            tokens = line.split()
            code = tokens[0]
            name = ' '.join(tokens[1:])

            countries[code] = name

    return countries


def read_stdoffs(db_dir: str) -> Stdoffs:
    filename = db_dir + "/stdoffs.txt"
    stdoffs: Stdoffs = {}
    with open(filename, "r", encoding='utf-8') as f:
        while True:
            line = read_line(f)
            if line is None:
                break

            tokens = line.split()
            timezone = tokens[0]
            stdoff = tokens[1]

            if timezone in stdoffs:
                raise ValueError(f"Timezone {timezone} already exists")
            stdoffs[timezone] = int(stdoff)

    return stdoffs


def read_region_country_timezones(db_dir: str) -> RegionCountryTimezones:
    filename = db_dir + "/country_timezones.txt"
    rct: RegionCountryTimezones = {}
    with open(filename, "r", encoding='utf-8') as f:
        while True:
            line = read_line(f)
            if line is None:
                break

            tokens = line.split()
            if len(tokens) != 3:
                raise ValueError(f"Expected 3 tokens but got {len(tokens)}")

            region = tokens[0]
            country = tokens[1]
            timezone = tokens[2]

            # Find entry for region, or create new entry
            ct = rct.get(region)
            if ct is None:
                ct = {}
                rct[region] = ct

            # Find entry for country, or create new entry
            tzlist = ct.get(country)
            if tzlist is None:
                tzlist = []
                ct[country] = tzlist

            tzlist.append(timezone)

    return rct


def read_airport_timezones(db_dir: str) -> AirportTimezones:
    filename = db_dir + "/airport_timezones.txt"
    airport_timezones: AirportTimezones = {}
    with open(filename, "r", encoding='utf-8') as f:
        while True:
            line = read_line(f)
            if line is None:
                break

            tokens = line.split()
            airport = tokens[0]
            timezone = tokens[1]

            if airport in airport_timezones:
                raise ValueError(f"Airport code {airport} already exists")
            airport_timezones[airport] = timezone

    return airport_timezones


def read_line(input: TextIO) -> Optional[str]:
    """Return the next line. Return None if EOF reached.

    * Comment lines beginning with a '#' character are skipped.
    * Trailing comment lines beginning with '#' are stripped.
    * Trailing whitespaces are stripped.
    * Blank lines are skipped.
    * Leading whitespaces are kept.
    """
    while True:
        line = input.readline()

        # EOF returns ''. A blank line returns '\n'.
        if line == '':
            return None

        # remove trailing comments
        i = line.find('#')
        if i >= 0:
            line = line[:i]

        # strip any trailing whitespaces
        line = line.rstrip()

        # skip any blank lines after stripping
        if not line:
            continue

        return line


if __name__ == '__main__':
    main()
