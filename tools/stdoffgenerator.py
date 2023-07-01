# Copyright 2023 Brian T. Park
#
# MIT License

"""
Generate the stdoff.txt file which contains a list of timzones and its STDOFF.
By default the STDOFF of the current year is extracted.

# Comments
ZoneName Stdoff(seconds)
"""

import logging
import os
from typing import Dict
from typing import Tuple

from stdoffextractor import ZoneInfoRaw
from stdoffextractor import ZonesMap
from stdoffextractor import LinksMap


INVALID_SECONDS = 999999


class StdoffGenerator:
    """Generate Go lang files (zone_infos.go, zone_policies.go) which are
    used by the ZoneProcessor class.
    """

    STDOFF_FILE_NAME = 'stdoff.txt'

    def __init__(
        self,
        invocation: str,
        tz_version: str,
        year: int,
        zones_map: ZonesMap,
        links_map: LinksMap,
    ):
        wrapped_invocation = '\n//     --'.join(invocation.split(' --'))
        self.invocation = wrapped_invocation
        self.year = year

        self.tz_version = tz_version
        self.zones_map = zones_map
        self.links_map = links_map

    def generate_files(self, output_dir: str) -> None:
        self._write_file(
            output_dir, self.STDOFF_FILE_NAME, self._generate_file_string())

    def _write_file(self, output_dir: str, filename: str, content: str) -> None:
        full_filename = os.path.join(output_dir, filename)
        with open(full_filename, 'w', encoding='utf-8') as output_file:
            print(content, end='', file=output_file)
        logging.info("Created %s", full_filename)

    def _generate_file_string(self) -> str:
        string = f"""\
# This file was generated by the following script:
#
#   $ {self.invocation}
#
# from https://github.com/eggert/tz/releases/tag/{self.tz_version}
#
# The STDOFF for each timezone was extracted for the year {self.year}.
#
# DO NOT EDIT

# zone stdoff(int) stdoff(string)
"""

        offset_map = self._generate_stdoff_map()
        for zone, offset in sorted(offset_map.items()):
            string += f"{zone} {offset[0]} {offset[1]}\n"
        return string

    def _generate_stdoff_map(self) -> Dict[str, Tuple[int, str]]:
        offset_map: Dict[str, Tuple[int, str]] = {}
        for zone, info in self.zones_map.items():
            offset, string = self._find_stdoff_for_year(info, self.year)
            offset_map[zone] = (offset, string)

        for link, zone in self.links_map.items():
            info = self.zones_map[zone]
            seconds, string = self._find_stdoff_for_year(info, self.year)
            offset_map[link] = (seconds, string)
        return offset_map

    def _find_stdoff_for_year(
        self, info: ZoneInfoRaw, year: int
    ) -> Tuple[int, str]:
        for era in info['eras']:
            if year < era['until_year']:
                stdoff = era['stdoff']
                stdoff_seconds = time_string_to_seconds(stdoff)
                return stdoff_seconds, stdoff
        return 0, "00:00"  # not found, should never happen, return 0


def time_string_to_seconds(time_string: str) -> int:
    """Converts the '[-]hh:mm:ss' string into +/- total seconds from 00:00.
    Returns INVALID_SECONDS if there is a parsing error.
    Copied from AceTimeTools/src/acetimetools/transformer/transformer.py.
    """
    sign = 1
    if time_string[0] == '-':
        sign = -1
        time_string = time_string[1:]

    try:
        elems = time_string.split(':')
        if len(elems) == 0:
            return INVALID_SECONDS
        hour = int(elems[0])
        minute = int(elems[1]) if len(elems) > 1 else 0
        second = int(elems[2]) if len(elems) > 2 else 0
        if len(elems) > 3:
            return INVALID_SECONDS
    except Exception:
        return INVALID_SECONDS

    # A number of countries use 24:00, and Japan uses 25:00(!).
    # Rule  Japan   1948    1951  -     Sep Sat>=8  25:00   0   	S
    if hour > 25:
        return INVALID_SECONDS
    if minute > 59:
        return INVALID_SECONDS
    if second > 59:
        return INVALID_SECONDS
    return sign * ((hour * 60 + minute) * 60 + second)