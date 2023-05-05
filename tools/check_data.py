#!/usr/bin/env python3
#
# Validate various data files under data/
#
# Usage:
# $ check_data.py
#   --zones {file}
#   --links {file}
#   --classified_zones {file}
#   --classified_links {file}
#   --iso_long {file}
#   --iso_short {file}
#   --regions {file}
#   [--region_country_timezones country_timezones.txt]
#   [--country_timezones geonames.txt]


from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Set
from typing import TextIO
from typing import Tuple
from typing import NamedTuple

# from pprint import pp
import argparse
import sys


# Both Zones and Links are stored in a Dict[str, Entry], where the Entry
# tracks the meta property of the zone or link.
#
# * Zones (target == None)
#   * Zone name
#   * ZoneObsolete name
# * Links
#   * Alias target link
#   * Similar target link
#   * Obsolete target link
class Entry(NamedTuple):
    target: Optional[str]  # Set to None for zones
    tag: str  # 'Zone', 'ZoneObsolete', 'Alias', 'Similar', 'Obsolete'


# ISO country to [timezones].
CountryTimezones = Dict[str, List[str]]

# Region to [timezones].
RegionTimezones = Dict[str, List[str]]


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Generate Country Code to Time Zone.')
    parser.add_argument('--zones', help='File of zones', required=True)
    parser.add_argument('--links', help='File of links', required=True)
    parser.add_argument(
        '--classified_zones',
        help='File of classified zones',
        required=True)
    parser.add_argument(
        '--classified_links',
        help='File of classified links',
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
        '--regions',
        help='Region names',
        required=True)
    parser.add_argument(
        '--region_country_timezones',
        help='Region-Country-Timezone file')
    parser.add_argument(
        '--country_timezones',
        help='Country-Timezone file')
    args = parser.parse_args()
    if not args.region_country_timezones and not args.country_timezones:
        error(
            "Must provide one of "
            "--region_country_timezones or --country_timezones")

    # Configure logging
    # logging.basicConfig(level=logging.INFO)

    # Read and check zones.
    zones = read_zones(args.zones)
    classified_zones = read_zones(args.classified_zones)
    check_zones(args.zones, zones, classified_zones)

    # Read and check links.
    links = read_links(args.links)
    check_cycle(args.links, links)
    classified_links = read_links(args.classified_links)
    check_cycle(args.classified_links, classified_links)
    check_links(args.links, links, classified_links)
    check_link_targets(classified_links, links, zones)

    # Read and check ISO countries.
    iso_long = read_countries(args.iso_long)
    iso_short = read_countries(args.iso_short)
    check_iso_names(iso_long, iso_short)

    # Read regions
    regions = read_regions(args.regions)

    # Print summary of input files.
    max_long_country = max([len(v) for v in iso_long.values()])
    max_short_country = max([len(v) for v in iso_short.values()])
    max_region = max([len(v) for v in regions.values()])
    print(f"{args.zones}: {len(zones)}")
    print(f"{args.links}: {len(links)}")
    print(f"{args.classified_zones}: {len(classified_zones)}")
    print(f"{args.classified_links}: {len(classified_links)}")
    print(f"{args.iso_long}: {len(iso_long)}, maxlen: {max_long_country}")
    print(f"{args.iso_short}: {len(iso_short)}, maxlen: {max_short_country}")
    print(f"{args.regions}: {len(regions)}, maxlen: {max_region}")

    if args.region_country_timezones:
        # Read and check region_country_timezones.txt.
        country_timezones, region_timezones = \
            read_region_country_timezones(args.region_country_timezones)
        check_countries(country_timezones, iso_short)
        check_regions(args.region_country_timezones, region_timezones, regions)
        check_timezones(
            args.region_country_timezones, country_timezones, classified_zones,
            classified_links)

        num_countries = len(country_timezones) - 1  # remove "00" country code
        num_timezones = sum([
            len(entry)
            for _, entry in country_timezones.items()
        ])

        # Print region_country_timezones summary.
        num_regions = len(region_timezones)
        print(
            f"{args.region_country_timezones}: "
            f"regions={num_regions}, "
            f"countries={num_countries}, "
            f"timezones={num_timezones}"
        )

        # Print timezones with multiple countries.
        poly_timezones = get_poly_timezones(country_timezones)
        if poly_timezones:
            print("Timezones with multiple countries:")
            for timezone, countries in poly_timezones.items():
                print(f"  {timezone}: {countries}")
    else:
        # Read and verify the country-timezone file
        country_timezones = read_country_timezones(args.country_timezones)
        check_countries(country_timezones, iso_short)
        check_timezones(
            args.country_timezones, country_timezones, classified_zones,
            classified_links)

        num_countries = len(country_timezones) - 1  # remove "00" country code
        num_timezones = sum([
            len(entry)
            for _, entry in country_timezones.items()
        ])

        # Print summary
        print(
            f"{args.country_timezones}: "
            f"countries={num_countries}, "
            f"timezones={num_timezones}"
        )

# -----------------------------------------------------------------------------


def read_zones(filename: str) -> Dict[str, Entry]:
    """Read Zone records of the form:
        Zone|ZoneObsolete zone_name
    and return:
        {zone_name -> {target, tag}}
    where
        tag: Zone|ZoneObsolete
    """
    zones: Dict[str, Entry] = {}
    with open(filename, 'r', newline='', encoding='utf-8') as f:
        while True:
            line = read_line(f)
            if line is None:
                break
            tokens: List[str] = line.split()
            tag = tokens[0]
            if tag not in ['Zone', 'ZoneObsolete']:
                error(f"Invalid Zone tag '{tag}'")
            zone_name = tokens[1]
            zones[zone_name] = Entry(None, tag)
    return zones


def read_links(filename: str) -> Dict[str, Entry]:
    """Read Link records of the form:
        (Link|Alias|Similar|Obsolete) source target
    and return:
        {target -> {source, tag}}
    where
        tag: Link|Alias|Similar|Obsolete
    """
    links: Dict[str, Entry] = {}
    with open(filename, 'r', newline='', encoding='utf-8') as f:
        while True:
            line = read_line(f)
            if line is None:
                break
            tokens: List[str] = line.split()
            tag = tokens[0]
            if tag not in ['Link', 'Alias', 'Alternate', 'Similar', 'Obsolete']:
                error(f"Invalid Link tag '{tag}'")
            source = tokens[1]
            target = tokens[2]
            links[target] = Entry(source, tag)
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


def read_regions(filename: str) -> Dict[str, str]:
    """{regionCode -> regionName}"""
    regions: Dict[str, str] = {}
    with open(filename, 'r', newline='', encoding='utf-8') as f:
        while True:
            line = read_line(f)
            if line is None:
                break
            tokens: List[str] = line.split()
            code = tokens[0]
            name = line[len(code):].strip()
            regions[code] = name
    return regions


def read_region_country_timezones(
    filename: str
) -> Tuple[CountryTimezones, RegionTimezones]:
    """Read {region country_code timezone} triplets"""
    country_timezones: CountryTimezones = {}
    region_timezones: RegionTimezones = {}
    with open(filename, 'r', newline='', encoding='utf-8') as f:
        while True:
            line = read_line(f)
            if line is None:
                break
            tokens: List[str] = line.split()
            region = tokens[0]
            country = tokens[1]
            timezone = tokens[2]

            # Add to country->timezones
            timezones = country_timezones.get(country)
            if not timezones:
                timezones = []
                country_timezones[country] = timezones
            timezones.append(timezone)

            # Add to region->timezones
            timezones = region_timezones.get(region)
            if not timezones:
                timezones = []
                region_timezones[region] = timezones
            timezones.append(timezone)

    return country_timezones, region_timezones


def read_country_timezones(filename: str) -> CountryTimezones:
    """Read {country_code timezone}"""
    country_timezones: CountryTimezones = {}
    with open(filename, 'r', newline='', encoding='utf-8') as f:
        while True:
            line = read_line(f)
            if line is None:
                break
            tokens: List[str] = line.split()
            country = tokens[0]
            timezone = tokens[1]

            # Add to country->timezones
            timezones = country_timezones.get(country)
            if not timezones:
                timezones = []
                country_timezones[country] = timezones
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

# -----------------------------------------------------------------------------


def check_zones(
    filename: str,
    zones: Dict[str, Entry],
    classified_zones: Dict[str, Entry],
) -> None:
    """Check that classified_zones and zones have identical entries."""
    if zones.keys() != classified_zones.keys():
        extra = classified_zones.keys() - zones.keys()
        if extra:
            error(f"Extra zones in {filename}", extra)

        missing = zones.keys() - classified_zones.keys()
        if missing:
            error(f"Missing zones in {filename}", missing)


def check_links(
    filename: str,
    links: Dict[str, Entry],
    classified_links: Dict[str, Entry],
) -> None:
    """Check that classified_links and links have identical entries."""
    if links.keys() != classified_links.keys():
        extra = classified_links.keys() - links.keys()
        if extra:
            error(f"Extra links in {filename}", extra)

        missing = links.keys() - classified_links.keys()
        if missing:
            error(f"Missing links in {filename}", missing)


def check_link_targets(
    classified_links: Dict[str, Entry],
    links: Dict[str, Entry],
    zones: Dict[str, Entry]
) -> None:
    """Check that every Link target in classified_links is an existing Link or
    Zone. This checks for typos.
    """
    for link, entry in classified_links.items():
        if entry.target not in links and entry.target not in zones:
            error(f"Invalid Link target '{entry.target}'")


def check_iso_names(
    iso_long: Dict[str, str],
    iso_short: Dict[str, str],
) -> None:
    # Check that the ISO codes are the same.
    if iso_long.keys() != iso_short.keys():
        error("ISO long and short files not equal")

    # Check the maximum length of the ISO country short names.
    MAX_LEN = 16
    max_len = max([len(x) for x in iso_short.values()])
    if max_len > MAX_LEN:
        error(f"ISO short names len ({max_len}) > {MAX_LEN}")


def check_countries(
    country_timezones: CountryTimezones,
    countries: Dict[str, str],
) -> None:
    # Set of expected ISO countries, with the exception of (BV and HM) which
    # don't have timezone because there are uninhabited.
    expected = set(countries.keys())
    expected.remove('BV')
    expected.remove('HM')

    # Set of classified ISO countries. The exception is the pseudo "00" country
    # which is assigned to timezones such as "UTC" or "Etc/UTC".
    selected = set(country_timezones.keys())
    selected.discard('00')

    if expected != selected:
        # Check that each ISO countries has at least one timezone.
        missing = expected - selected
        if missing:
            error("Missing countries in country_timezones", missing)

        # Check that every country in the country_timezones.txt exists in the
        # ISO country file.
        extra = country_timezones.keys() - countries.keys()
        if extra:
            error("Extra countries in country_timezones", extra)


def check_regions(
    filename: str,
    region_timezones: RegionTimezones,
    regions: Dict[str, str],
) -> None:
    """Check that every region in country_timezones.txt is defined in
    regions.txt.
    """
    expected = set(regions.keys())
    selected = set(region_timezones.keys())
    if expected != selected:
        extra = selected - expected
        if extra:
            error(f"Extra regions in {filename}", extra)

        missing = expected - selected
        if missing:
            error(f"Missing regions in {filename}", missing)


def check_timezones(
    filename: str,
    country_timezones: CountryTimezones,
    classified_zones: Dict[str, Entry],
    classified_links: Dict[str, Entry],
) -> None:
    # Collect only 'Zone', 'Similar', and 'Alternate' timezones. They are the
    # only timezones which should appear. 'Alias' and 'Obsolete' should not
    # appear to avoid duplicates or old timezones.
    expected: Set[str] = set()
    expected.update([
        name for name, entry in classified_zones.items()
        if entry.tag == 'Zone'
    ])
    expected.update([
        name for name, entry in classified_links.items()
        if entry.tag in ['Similar', 'Alternate']
    ])

    # Collect the timezones which appear in country_timezones.txt.
    selected: Set[str] = set()
    for z in country_timezones.values():
        selected.update(z)

    # Check that they are equal.
    if selected != expected:
        extra = selected - expected
        if extra:
            error(f"Extra timezones in {filename}", extra)

        missing = expected - selected
        if missing:
            error(f"Missing timezones from {filename}", missing)


def get_poly_timezones(
    country_timezones: CountryTimezones,
) -> Dict[str, List[str]]:
    """Return the timezones that belong to multiple countries."""
    timezone_countries: Dict[str, List[str]] = {}  # timezone -> [countries]
    for country, timezones in country_timezones.items():
        for z in timezones:
            countries = timezone_countries.get(z)
            if not countries:
                countries = []
                timezone_countries[z] = countries
            countries.append(country)
    poly_timezones = {
        k: v
        for k, v in timezone_countries.items()
        if len(v) > 1
    }
    return poly_timezones

# -----------------------------------------------------------------------------


def check_cycle(filename: str, links: Dict[str, Entry]) -> None:
    for name, entry in links.items():
        if has_cycle(name, links):
            target = links[name].target
            error(f"{filename}: Link cycle for '{name}' -> '{target}'")


def has_cycle(name: str, links: Dict[str, Entry]) -> bool:
    """Determine if 'name' is a cycle in the links map. This uses the "two
    pointer" algorithm:
    * Advance p1 one step
    * Advance p2 two steps
    * If p1 == p2, we have a cycle
    """
    p1: Optional[str] = name
    p2: Optional[str] = name
    while True:
        # Take a single step for p1.
        assert p1 is not None
        e1 = links.get(p1)
        if not e1:
            return False
        p1 = e1.target
        if not p1:
            return False

        # Take 2 steps for p2.
        assert p2 is not None
        e2 = links.get(p2)
        if not e2:
            return False
        p2 = e2.target
        if not p2:
            return False

        assert p2 is not None
        e2 = links.get(p2)
        if not e2:
            return False
        p2 = e2.target
        if not p2:
            return False

        if p1 == p2:
            return True

# -----------------------------------------------------------------------------


def error(msg: str, items: Iterable[str] = []) -> None:
    print(msg)
    for item in sorted(items):
        print(f'  {item}')
    sys.exit(1)

# -----------------------------------------------------------------------------


if __name__ == '__main__':
    main()
