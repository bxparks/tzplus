#!/usr/bin/env python3

# Usage:
#
# $ check_timezone_files.py
#   --zones {file}
#   --links {file}
#   --resolved_links {file}
#   --iso_long {file}
#   --iso_short {file}
#   --country_timezones country_timezones.txt

from typing import Dict
from typing import List
from typing import Optional
from typing import TextIO
from typing import NamedTuple

# from pprint import pp
import argparse
import logging
# import sys


class ZoneEntry(NamedTuple):
    name: str
    type: str  # 'Zone', 'Alias', 'Similar', 'Obsolete'


CountryTimezones = Dict[str, List[str]]


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Generate Country Code to Time Zone.')
    parser.add_argument('--zones', help='File of zones', required=True)
    parser.add_argument('--links', help='File of links', required=True)
    parser.add_argument(
        '--resolved_links',
        help='File of resolved links',
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
    logging.basicConfig(level=logging.INFO)

    # zones = read_zones(args.zones)

    # Read and check links.
    links = read_links(args.links)
    resolved_links = read_resolved_links(args.resolved_links)
    check_links(links, resolved_links)

    # Read and check ISO countries.
    iso_long = read_countries(args.iso_long)
    iso_short = read_countries(args.iso_short)
    check_iso_names(iso_long, iso_short)

    # Read country to timezones list, and verify.
    country_timezones = read_country_timezones(args.country_timezones)
    check_countries(country_timezones, iso_short)
    # pp(country_timezones)


def read_zones(filename: str) -> Dict[str, bool]:
    """Read Zone records of the form:
        Zone zone_name
    and return:
        {zone_name -> True}
    """
    zones: Dict[str, ZoneEntry] = {}
    with open(filename, 'r', newline='', encoding='utf-8') as f:
        while True:
            line = read_line(f)
            if line is None:
                break
            tokens: List[str] = line.split()
            type = tokens[0]
            assert type == 'Zone'
            zone_name = tokens[1]
            zones[zone_name] = (zone_name, 'Zone')
    return zones


def read_links(filename: str) -> Dict[str, str]:
    """Read Link records of the form:
        Link link_name -> target_name
    and return:
        {link_name -> target_name}
    """
    links: Dict[str, ZoneEntry] = {}
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
            links[link_name] = (target_name, type)
    return links


def read_resolved_links(filename: str) -> Dict[str, str]:
    """Read Resolved records of the form:
        Alias link_name -> target_name
        Similar link_name -> target_name
        Obsolete link_name -> target_name
    and return:
        {link_name -> target_name}
    """
    links: Dict[str, ZoneEntry] = {}
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
            links[link_name] = (target_name, type)
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


def read_country_timezones(filename: str) -> Dict[str, str]:
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


def check_links(
    links: Dict[str, ZoneEntry],
    resolved_links: Dict[str, ZoneEntry],
) -> None:
    if links.keys() != resolved_links.keys():
        excess_links = links.keys() - resolved_links.keys()
        if excess_links:
            raise Exception(f"Excess links: {excess_links}")
        excess_resolved_links = resolved_links.keys() - links.keys()
        if excess_resolved_links:
            raise Exception(f"Excess links: {excess_resolved_links}")


def check_iso_names(
    iso_long: Dict[str, str],
    iso_short: Dict[str, str],
) -> None:
    # Check that the ISO codes are the same.
    if iso_long.keys() != iso_short.keys():
        raise Exception("ISO long and short files not equal")

    # Check the maximum length of the ISO country short names.
    MAX_LEN = 16
    max_len = max([len(x) for x in iso_short.values()])
    if max_len > MAX_LEN:
        raise Exception(f"ISO short names len ({max_len}) > {MAX_LEN}")


def check_countries(
    country_timezones: Dict[str, str],
    countries: Dict[str, str],
) -> None:
    if countries.keys() != country_timezones.keys():
        # There seem to be no timezones defined for BV and HM
        EXPECTED_MISSING = set(("BV", "HM"))
        # Check that (almost) all ISO countries has at least one timezone.
        missing = countries.keys() - country_timezones.keys()
        missing = missing - EXPECTED_MISSING
        if missing:
            raise Exception(f"Unmatched ISO countries: {missing}")

        # Check that every timezone country exists in the ISO country file.
        # The pseudo ISO code "00" identifies timezones which don't correspond
        # to ISO countries. Example "UTC" or "Etc/UTC".
        EXPECTED_EXTRAS = set(("00",))
        extras = country_timezones.keys() - countries.keys()
        extras = extras - EXPECTED_EXTRAS
        if extras:
            raise Exception(
                f"Unexpected countries with timezones: {extras}")


if __name__ == '__main__':
    main()
