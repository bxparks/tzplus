#!/usr/bin/env python3

# Usage:
#
# $ check_timezone_files.py
#   --zones {file}
#   --links {file}
#   --classified_links {file}
#   --classified_zones {file}
#   --iso_long {file}
#   --iso_short {file}
#   --country_timezones country_timezones.txt

from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Set
from typing import TextIO
from typing import NamedTuple

# from pprint import pp
import argparse
import sys


class Entry(NamedTuple):
    target: str
    type: str  # 'Zone', 'Alias', 'Similar', 'Obsolete'


CountryTimezones = Dict[str, List[str]]


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Generate Country Code to Time Zone.')
    parser.add_argument('--zones', help='File of zones', required=True)
    parser.add_argument('--links', help='File of links', required=True)
    parser.add_argument(
        '--classified_links',
        help='File of classified links',
        required=True)
    parser.add_argument(
        '--classified_zones',
        help='File of classified zones',
        required=True)
    parser.add_argument(
        '--iso_long',
        help='Long country names',
        required=True)
    parser.add_argument(
        '--iso_short',
        help='Short country names',
        required=True)
    parser.add_argument(
        '--country_timezones',
        help='Country code to timezones',
        required=True)
    args = parser.parse_args()

    # Configure logging
    # logging.basicConfig(level=logging.INFO)

    # Read and check zones.
    zones = read_zones(args.zones)
    classified_zones = read_zones(args.classified_zones)
    check_zones(zones, classified_zones)

    # Read and check links.
    links = read_links(args.links)
    classified_links = read_classified_links(args.classified_links)
    check_links(links, classified_links)

    # Read and check ISO countries.
    iso_long = read_countries(args.iso_long)
    iso_short = read_countries(args.iso_short)
    check_iso_names(iso_long, iso_short)

    # Read country to timezones list, and verify.
    country_timezones = read_country_timezones(args.country_timezones)
    check_countries(country_timezones, iso_short)

    # Read zones, and check classified timezones.
    check_timezones(country_timezones, classified_zones, classified_links)


def read_zones(filename: str) -> Dict[str, Entry]:
    """Read Zone records of the form:
        Zone|Obsolete zone_name
    and return:
        {zone_name -> {target, 'Zone'}}
    """
    zones: Dict[str, Entry] = {}
    with open(filename, 'r', newline='', encoding='utf-8') as f:
        while True:
            line = read_line(f)
            if line is None:
                break
            tokens: List[str] = line.split()
            type = tokens[0]
            assert type in ['Zone', 'Obsolete']
            zone_name = tokens[1]
            zones[zone_name] = Entry(zone_name, type)
    return zones


def read_classified_zones(filename: str) -> Dict[str, Entry]:
    """Read classified links of the form:
        Zone zone_name -> target_name
        Obsolete zone_name -> target_name
    and return:
        {zone_name -> {target, type}}
    """
    links: Dict[str, Entry] = {}
    with open(filename, 'r', newline='', encoding='utf-8') as f:
        while True:
            line = read_line(f)
            if line is None:
                break
            tokens: List[str] = line.split()
            type = tokens[0]
            assert type in ['Zone', 'Obsolete']
            link_name = tokens[1]
            target_name = tokens[3]
            links[link_name] = Entry(target_name, type)
    return links


def read_links(filename: str) -> Dict[str, Entry]:
    """Read Link records of the form:
        Link link_name -> target_name
    and return:
        {link_name -> {target, type}}
    """
    links: Dict[str, Entry] = {}
    with open(filename, 'r', newline='', encoding='utf-8') as f:
        while True:
            line = read_line(f)
            if line is None:
                break
            tokens: List[str] = line.split()
            type = tokens[0]
            assert type == 'Link'
            link_name = tokens[1]
            target_name = tokens[3]
            links[link_name] = Entry(target_name, type)
    return links


def read_classified_links(filename: str) -> Dict[str, Entry]:
    """Read classified links of the form:
        Alias link_name -> target_name
        Similar link_name -> target_name
        Obsolete link_name -> target_name
    and return:
        {link_name -> {target, type}}
    """
    links: Dict[str, Entry] = {}
    with open(filename, 'r', newline='', encoding='utf-8') as f:
        while True:
            line = read_line(f)
            if line is None:
                break
            tokens: List[str] = line.split()
            type = tokens[0]
            assert type in ['Alias', 'Similar', 'Obsolete']
            link_name = tokens[1]
            target_name = tokens[3]
            links[link_name] = Entry(target_name, type)
    return links


def read_countries(filename: str) -> Dict[str, str]:
    """{code -> country name}"""
    countries: Dict[str, str] = {}
    with open(filename, 'r', newline='', encoding='utf-8') as f:
        while True:
            line = read_line(f)
            if line is None:
                break
            code = line[0:2]
            country_name = line[2:]
            country_name = country_name.strip()
            countries[code] = country_name
    return countries


def read_country_timezones(filename: str) -> CountryTimezones:
    """{country_code -> timezone}"""
    country_timezones: CountryTimezones = {}
    with open(filename, 'r', newline='', encoding='utf-8') as f:
        while True:
            line = read_line(f)
            if line is None:
                break
            tokens: List[str] = line.split()
            code = tokens[0]
            timezone = tokens[1]

            timezones = country_timezones.get(code)
            if not timezones:
                timezones = []
                country_timezones[code] = timezones
            timezones.append(timezone)
    return country_timezones


def read_line(input: TextIO) -> Optional[str]:
    """Return the next non-comment line. Return None if EOF reached.

    * Comment lines begin with a '#' character and are skipped.
    * Blank lines are skipped.
    * Trailing whitespaces are stripped.
    * Leading whitespaces are kepted.
    """
    while True:
        line = input.readline()

        # EOF returns ''. An empty line returns '\n'.
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


def check_zones(
    zones: Dict[str, Entry],
    classified_zones: Dict[str, Entry],
) -> None:
    if zones.keys() != classified_zones.keys():
        extra = classified_zones.keys() - zones.keys()
        if extra:
            error("Extra zones in classified_zones", extra)

        missing = zones.keys() - classified_zones.keys()
        if missing:
            error("Missing zones in classified zones", missing)


def check_links(
    links: Dict[str, Entry],
    classified_links: Dict[str, Entry],
) -> None:
    if links.keys() != classified_links.keys():
        extra = classified_links.keys() - links.keys()
        if extra:
            error("Extra links in classified_links", extra)

        missing = links.keys() - classified_links.keys()
        if missing:
            error("Missing links in classified links", missing)


def check_iso_names(
    iso_long: Dict[str, str],
    iso_short: Dict[str, str],
) -> None:
    # Check that the ISO codes are the same.
    if iso_long.keys() != iso_short.keys():
        print("ISO long and short files not equal")
        sys.exit(1)

    # Check the maximum length of the ISO country short names.
    MAX_LEN = 16
    max_len = max([len(x) for x in iso_short.values()])
    if max_len > MAX_LEN:
        print(f"ISO short names len ({max_len}) > {MAX_LEN}")
        sys.exit(1)


def check_countries(
    country_timezones: CountryTimezones,
    countries: Dict[str, str],
) -> None:
    if countries.keys() != country_timezones.keys():
        # There seem to be no timezones defined for BV and HM
        EXPECTED_MISSING = set(("BV", "HM"))
        # Check that (almost) all ISO countries has at least one timezone.
        missing = countries.keys() - country_timezones.keys()
        missing = missing - EXPECTED_MISSING
        if missing:
            error("Missing countries in country_timezones", missing)

        # Check that every timezone country exists in the ISO country file.
        # The pseudo ISO code "00" identifies timezones which don't correspond
        # to ISO countries. Example "UTC" or "Etc/UTC".
        EXPECTED_EXTRA = set(("00",))
        extra = country_timezones.keys() - countries.keys()
        extra = extra - EXPECTED_EXTRA
        if extra:
            error("Extra countries in country_timezones", extra)


def check_timezones(
    country_timezones: CountryTimezones,
    classified_zones: Dict[str, Entry],
    classified_links: Dict[str, Entry],
) -> None:
    expected: Set[str] = set()
    expected.update([
        name for name, entry in classified_zones.items()
        if entry.type == 'Zone'
    ])
    expected.update([
        name for name, entry in classified_links.items()
        if entry.type == 'Similar'
    ])

    selected: Set[str] = set()
    for z in country_timezones.values():
        selected.update(z)

    if selected != expected:
        extra = selected - expected
        if extra:
            error("Extra timezones in country_timezones", extra)

        missing = expected - selected
        if missing:
            error("Missing timezones from country_timezones", missing)


def error(msg: str, items: Iterable[str]) -> None:
    print(msg)
    for item in sorted(items):
        print(f'  {item}')
    sys.exit(1)


if __name__ == '__main__':
    main()
