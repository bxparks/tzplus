#!/usr/bin/env python3
#
# List the timezones organized by region, then country, then timezone.
#
# Usage:
# $ list_zones.py
#   [--regions {file}]
#   [--countries {file}]
#   country_timezones.txt

from typing import Dict
from typing import List
import argparse

from verify_data import read_line
from verify_data import read_countries
from verify_data import read_regions
from verify_data import error

CountryTimezones = Dict[str, List[str]]
RegionCountryTimezones = Dict[str, CountryTimezones]
Regions = Dict[str, str]
Countries = Dict[str, str]


def main() -> None:
    parser = argparse.ArgumentParser(
        description='List Time Zones.')
    parser.add_argument(
        '--regions', help='Region code to name', required=False)
    parser.add_argument(
        '--countries', help='Country code to name', required=False)
    parser.add_argument('timezones', help='Timezone file')
    args = parser.parse_args()
    if not args.timezones:
        error("Must provide timezones file")

    regions: Regions = {}
    if args.regions:
        regions = read_regions(args.regions)

    countries: Countries = {}
    if args.countries:
        countries = read_countries(args.countries)

    region_country_timezones = read_region_country_timezones(args.timezones)
    print_nested_timezones(regions, countries, region_country_timezones)


def print_nested_timezones(
    regions: Regions,
    countries: Countries,
    zones: RegionCountryTimezones
) -> None:
    for region, country_timezones in sorted(zones.items()):
        if regions:
            region = f"{regions.get(region)} ({region})"
        print(f"{region}")
        for country, timezones in sorted(country_timezones.items()):
            if countries:
                country = f"{countries.get(country)} ({country})"
            print(f"    {country}")
            for timezone in sorted(timezones):
                print(f"        {timezone}")


def read_region_country_timezones(filename: str) -> RegionCountryTimezones:
    """Read file with lines of form {region country timezone}"""
    region_country_timezones: RegionCountryTimezones = {}
    with open(filename, 'r', newline='', encoding='utf-8') as f:
        while True:
            line = read_line(f)
            if line is None:
                break
            tokens: List[str] = line.split()
            region = tokens[0]
            country = tokens[1]
            timezone = tokens[2]

            # Add to region->country_timezones
            country_timezones = region_country_timezones.get(region)
            if not country_timezones:
                country_timezones = {}
                region_country_timezones[region] = country_timezones

            # Add to country->timezones
            timezones = country_timezones.get(country)
            if not timezones:
                timezones = []
                country_timezones[country] = timezones
            timezones.append(timezone)

    return region_country_timezones


if __name__ == '__main__':
    main()
