#!/usr/bin/env python3
#
# Validate various data files under data/
#
# Usage:
# $ verify_data.py
#   --zones {file}
#   --links {file}
#   --classified_zones {file}
#   --classified_links {file}
#   --iso_orig {file}
#   --iso_long {file}
#   --iso_short {file}
#   --regions {file}
#   (--region_country_timezones country_timezones.txt |
#       --country_timezones geonames.txt)
#   --airport_timezones file.txt


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
#   * Alternate target link
#   * Obsolete target link
#   * Similar target link
class Entry(NamedTuple):
    target: Optional[str]  # Set to None for zones
    tag: str  # 'Zone', 'ZoneObsolete', 'Alias', 'Similar', 'Obsolete'


# ISO country to [timezones].
CountryTimezones = Dict[str, List[str]]

# Region to [timezones].
RegionTimezones = Dict[str, List[str]]

# Airport code to [timezones]
AirportTimezones = Dict[str, str]


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
        '--iso_orig',
        help='Original ISO countries',
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
    parser.add_argument(  # Required only for --region_country_timezones
        '--airport_timezones',
        help='Airport to timezones')
    parser.add_argument(
        '--region_country_timezones',
        help='Region-Country-Timezone file')
    parser.add_argument(
        '--country_timezones',
        help='Country-Timezone file')

    args = parser.parse_args()
    if args.region_country_timezones is None and args.country_timezones is None:
        error(
            "Must provide one of "
            "--region_country_timezones or --country_timezones")
    if args.region_country_timezones is not None:
        if args.airport_timezones is None:
            error("Must provide --airport_timezones")

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
    iso_orig = read_countries(args.iso_orig)
    iso_long = read_countries(args.iso_long)
    iso_short = read_countries(args.iso_short)
    check_iso_names(
        args.iso_orig, args.iso_long, args.iso_short,
        iso_orig, iso_long, iso_short)

    # Read regions
    regions = read_regions(args.regions)

    if args.region_country_timezones:
        # Read and check region_country_timezones.txt.
        country_timezones, region_timezones = \
            read_region_country_timezones(args.region_country_timezones)
        check_countries(
            args.region_country_timezones, country_timezones, iso_short)
        check_regions(args.region_country_timezones, region_timezones, regions)
        check_timezones(
            args.region_country_timezones, country_timezones, classified_zones,
            classified_links)

        # Print timezones with multiple countries.
        poly_timezones = get_poly_timezones(country_timezones)
        if poly_timezones:
            print("Timezones with multiple countries:")
            for timezone, countries in poly_timezones.items():
                print(f"  {timezone}: {countries}")

        # Read airport timezones. Check that the airport_timezones are identical
        # to region_country_timezones.
        airport_timezones = read_airport_timezones(args.airport_timezones)
        check_airport_and_country_timezones(
            args.airport_timezones, airport_timezones, country_timezones)
    else:
        # Read and verify the country-timezone file from geonames.org
        country_timezones = read_country_timezones(args.country_timezones)
        check_countries(args.country_timezones, country_timezones, iso_short)
        check_timezones(
            args.country_timezones, country_timezones, classified_zones,
            classified_links)


# -----------------------------------------------------------------------------
# File read functions.
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

    print(f"{filename}: {len(zones)}")
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

    print(f"{filename}: {len(links)}")
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

    maxlen = max([len(v) for v in countries.values()])
    print(f"{filename}: {len(countries)}, maxlen: {maxlen}")
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

    maxlen = max([len(v) for v in regions.values()])
    print(f"{filename}: {len(regions)}, maxlen: {maxlen}")
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

    # Print region_country_timezones summary.
    num_regions = len(region_timezones)
    num_countries = len(country_timezones)
    num_timezones = sum([
        len(entry)
        for entry in country_timezones.values()
    ])
    unique_tz: Set[str] = set()
    for z in country_timezones.values():
        unique_tz.update(z)
    print(
        f"{filename}: "
        f"regions={num_regions}, "
        f"countries={num_countries}, "
        f"timezones={num_timezones}, "
        f"unique={len(unique_tz)}"
    )

    return country_timezones, region_timezones


def read_country_timezones(filename: str) -> CountryTimezones:
    """Read {country_code -> timezone}"""
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

    # Print summary
    num_countries = len(country_timezones)
    num_timezones = sum([
        len(entry)
        for entry in country_timezones.values()
    ])
    unique_tz: Set[str] = set()
    for z in country_timezones.values():
        unique_tz.update(z)
    print(
        f"{filename}: "
        f"countries={num_countries}, "
        f"timezones={num_timezones}, "
        f"unique={len(unique_tz)}"
    )

    return country_timezones


def read_airport_timezones(filename: str) -> AirportTimezones:
    """Read {airport_code -> timezone}"""
    airport_timezones: AirportTimezones = {}
    with open(filename, 'r', newline='', encoding='utf-8') as f:
        while True:
            line = read_line(f)
            if line is None:
                break
            tokens: List[str] = line.split()
            airport = tokens[0]
            timezone = tokens[1]

            if airport in airport_timezones:
                error(f"Duplicate airport code '{airport}'")
            airport_timezones[airport] = timezone

    print(f"{filename}: {len(airport_timezones)}")
    return airport_timezones


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
# Validation functions.
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
    filename_orig: str,
    filename_long: str,
    filename_short: str,
    iso_orig: Dict[str, str],
    iso_long: Dict[str, str],
    iso_short: Dict[str, str],
) -> None:
    # Collect expected ISO codes
    expected = set(iso_orig.keys())
    expected.add('00')

    # Verify iso3166_long.txt matches expection.
    observed = set(iso_long)
    if expected != observed:
        missing = expected - observed
        if missing:
            error(f"Missing countries in {filename_long}", missing)
        extra = observed - expected
        if extra:
            error(f"Extra countries in {filename_long}", extra)

    # Verify iso3166_short.txt matches expection.
    observed = set(iso_short)
    if expected != observed:
        missing = expected - observed
        if missing:
            error(f"Missing countries in {filename_short}", missing)
        extra = observed - expected
        if extra:
            error(f"Extra countries in {filename_short}", extra)

    # Check the maximum length of the ISO country short names.
    MAX_ISO_SHORT_LEN = 13
    max_len = max([len(x) for x in iso_short.values()])
    if max_len > MAX_ISO_SHORT_LEN:
        error(f"ISO short names len ({max_len}) > {MAX_ISO_SHORT_LEN}")


def check_countries(
    filename: str,
    country_timezones: CountryTimezones,
    countries: Dict[str, str],
) -> None:
    # Expected ISO countries, with the exception of (BV and HM) which
    # don't have timezone because there are uninhabited.
    expected = set(countries.keys())
    expected.remove('BV')
    expected.remove('HM')
    expected.discard('00')  # fake country '00' is not required

    # Observed ISO countries in the country_timezones map.
    observed = set(country_timezones.keys())
    observed.discard('00')  # fake country '00' is not required

    print("Ignoring uninhabited countries: 'BV', 'HM'")
    print("Ignoring fake country: '00'")

    if expected != observed:
        # Check that each ISO countries has at least one timezone.
        missing = expected - observed
        if missing:
            error(f"Missing countries in {filename}", missing)

        # Check that every timezone country exists in the ISO country file.
        extra = observed - expected
        if extra:
            error(f"Extra countries in {filename}", extra)


def check_regions(
    filename: str,
    region_timezones: RegionTimezones,
    regions: Dict[str, str],
) -> None:
    """Check that every region in country_timezones.txt is defined in
    regions.txt.
    """
    expected = set(regions.keys())
    observed = set(region_timezones.keys())
    if expected != observed:
        extra = observed - expected
        if extra:
            error(f"Extra regions in {filename}", extra)

        missing = expected - observed
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
    observed: Set[str] = set()
    for z in country_timezones.values():
        observed.update(z)

    # Check that they are equal.
    if observed != expected:
        extra = observed - expected
        if extra:
            error(f"Extra timezones in {filename}", extra)

        missing = expected - observed
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


def check_airport_and_country_timezones(
    filename: str,
    airport_timezones: AirportTimezones,
    country_timezones: CountryTimezones,
) -> None:
    airport_tzs: Set[str] = set(airport_timezones.values())

    # Create a set from the list of lists. This can probably be done using a
    # single, set-comprehension expression, but I'm not able to find that
    # information in the python docs right now.
    country_tzs: Set[str] = set()
    for tzs in country_timezones.values():
        country_tzs.update(tzs)

    missing = country_tzs - airport_tzs
    if missing:
        error(f"Missing timezones in {filename}", missing)

    extra = airport_tzs - country_tzs
    if extra:
        error(f"Extra timezones in {filename}", extra)


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
    """Print error msg, with an optional list of items that produced the error,
    then exit with status code 1.
    """
    print(msg)
    for item in sorted(items):
        print(f'  {item}')
    sys.exit(1)

# -----------------------------------------------------------------------------


if __name__ == '__main__':
    main()
