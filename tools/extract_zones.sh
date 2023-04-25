#!/usr/bin/env bash
#
# Extract the Zones in the TZDB files inside the given tzdb directory.
#
# Usage:
#   $ ./extract_zones.sh tzdb
#
# Author: Brian Park
# License: Public Domain

set -eu

if [[ $# != 1 ]]; then
    echo 'Usage: extract_zones.sh tzdb > output.txt'
    exit 1
fi

cd $1

cat << END
# These are the 'Zone' entries extracted from TZDB raw files
# (https://github.com/eggert/tz), sorted by the Zone name.

END

cat \
africa \
antarctica \
asia \
australasia \
backward \
etcetera \
europe \
northamerica \
southamerica |
    grep '^Zone' | awk '{print "Zone", $2}' | sort
