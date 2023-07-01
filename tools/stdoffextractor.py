# Copyright 2018 Brian T. Park
#
# MIT License.

"""
Parses the zone info files in the TZ Database to extract the STDOFF of each
zone. This is a simplified version of the
src/acetimetools/extractor/extractor.py module in the AceTimeTools project

The following files are used:

    africa
    antarctica
    asia
    australasia
    backward
    etcetera
    europe
    northamerica
    southamerica

The following zone files are not used:

    backzone - contains zones differing before 1970
    systemv - 'SystemV' zones

"""

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import TextIO
from typing import TypedDict
from typing import Tuple
import logging
import os


class ZoneEraRaw(TypedDict, total=False):
    """Represents the 'ZONE' line and its associated STDOFF field from the TZDB
    files. Those entries look like this:

    # Zone  NAME                STDOFF      RULES   FORMAT  [UNTIL]
    Zone    America/Chicago     -5:50:36    -       LMT     1883 Nov 18 12:09:24
                                -6:00       US      C%sT    1920
                                ...
                                -6:00       US      C%sT

    Only the NAME and STDOFF field is extracted here, because the other fields
    are not used.
    """
    stdoff: str  # STDOFF columnfrom UTC/GMT
    until_year: int  # UNTIL year, or MAX_UNTIL_YEAR if empty
    raw_line: str  # original ZONE line in TZ file


class ZoneInfoRaw(TypedDict, total=False):
    """Represents a single zoneinfo record after parsing and processing the
    TZDB raw data files.
    """
    eras: List[ZoneEraRaw]


# Indicate +Infinity UNTIL year (represented by empty field).
MAX_UNTIL_YEAR: int = 32767

# Map of zoneName -> ZoneInfo. Created by extractor.py. Updated by
# transformer.py.
ZonesMap = Dict[str, ZoneInfoRaw]

# Map of linkName -> zoneName. Created by extractor.py. Updated by
# transformer.py.
LinksMap = Dict[str, str]


class Extractor:
    """Reads each test data section from the given file-like object (e.g.
    sys.stdin).

    Usage:

        extractor = Extractor(input_dir)
        zones_map, links_map = extractor.parse()
        ...
    """

    ZONE_FILES: List[str] = [
        'africa',
        'antarctica',
        'asia',
        'australasia',
        'backward',
        'etcetera',
        'europe',
        'northamerica',
        'southamerica',
    ]

    def __init__(self, input_dir: str):
        self.input_dir: str = input_dir

        self.zone_lines: Dict[str, List[str]] = {}  # zoneName to lines[]
        self.link_lines: Dict[str, List[str]] = {}  # linkName to zoneName[]
        self.zones_map: ZonesMap = {}
        self.links_map: LinksMap = {}

    def parse(self) -> Tuple[ZonesMap, LinksMap]:
        """Read the zoneinfo files from TZ Database and create the 'zones_map'
        and 'policies_map'.
        * zones_map contains a map of (zone_name -> ZoneEraRaw[]).
        * rules contains a map of (policy_name -> ZoneRuleRaw[]).
        """
        self._parse_zone_files()
        self._process_zones()
        self._process_links()
        return self.zones_map, self.links_map

    def _parse_zone_files(self) -> None:
        logging.basicConfig(level=logging.INFO)
        for file_name in self.ZONE_FILES:
            full_filename = os.path.join(self.input_dir, file_name)
            logging.info('Processing %s', full_filename)
            with open(full_filename, 'r', encoding='utf-8') as f:
                self._parse_zone_file(f)

    def _parse_zone_file(self, input: TextIO) -> None:
        """Read the 'input' file and collect all 'Rule' lines into
        self.rule_lines and all 'Zone' lines into self.zone_lines.
        """
        in_zone_mode: bool = False
        # prev_tag: str = ''
        prev_name: str = ''
        while True:
            line: Optional[str] = _read_line(input)
            if line is None:
                break

            tag: str = line[:4]
            if tag == 'Link':
                tokens = line.split()
                link_name: str = tokens[2]
                _add_item(self.link_lines, link_name, tokens[1])
                in_zone_mode = False
            elif tag == 'Zone':
                tokens = line.split()
                zone_name: str = tokens[1]
                _add_item(self.zone_lines, zone_name, ' '.join(tokens[2:]))
                in_zone_mode = True
                # prev_tag = tag
                prev_name = zone_name
            elif tag[0] == '\t' and in_zone_mode:
                # Collect subsequent lines that begin with a TAB character into
                # the current 'Zone' entry.
                _add_item(self.zone_lines, prev_name, line)

    def _process_zones(self) -> None:
        name: str
        lines: List[str]
        for name, lines in self.zone_lines.items():
            line: str
            for line in lines:
                zone_era: ZoneEraRaw = _process_zone_line(line)
                if zone_era:
                    _add_zones_map(self.zones_map, name, zone_era)

    def _process_links(self) -> None:
        link_name: str
        lines: List[str]
        for link_name, lines in self.link_lines.items():
            num_lines = len(lines)
            if num_lines > 1:
                raise ValueError(
                    f"{link_name}: Too many Link lines: {num_lines}")
            self.links_map[link_name] = lines[0]


def _read_line(input: TextIO) -> Optional[str]:
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


def _add_item(table: Dict[str, List[Any]], name: str, line: Any) -> None:
    array: Optional[List[Any]] = table.get(name)
    if not array:
        array = []
        table[name] = array
    array.append(line)


def _add_zones_map(zones_map: ZonesMap, name: str, era: ZoneEraRaw) -> None:
    info = zones_map.get(name)
    if not info:
        info = {
            'eras': [],
        }
        zones_map[name] = info
    info['eras'].append(era)


def _process_zone_line(line: str) -> ZoneEraRaw:
    """Normalize an zone era from dictionary that represents one line of
    a 'Zone' record. The columns are:
    STDOFF   RULES  FORMAT  [UNTIL]
    0        1      2       3
    -5:50:36 -      LMT     1883 Nov 18 12:09:24
    -6:00    US     C%sT    1920
    """
    tokens: List[str] = line.split()

    # STDOFF
    stdoff: str = tokens[0]

    # check 'until' year
    if len(tokens) >= 4:
        until_year: int = int(tokens[3])
    else:
        until_year = MAX_UNTIL_YEAR

    # Return map corresponding to a ZoneEra instance
    return {
        'stdoff': stdoff,
        'until_year': until_year,
        'raw_line': line,
    }
