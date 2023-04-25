#!/usr/bin/env bash
#
# Extract the Links in the TZDB files inside the given tzdb directory.
#
# Usage:
#   $ ./extract_links.sh tzdb
#
# Author: Brian Park
# License: Public Domain

set -eu

if [[ $# != 1 ]]; then
    echo 'Usage: extract_links.sh tzdb > output.txt'
    exit 1
fi

cd $1

cat << END
# These are the 'Link' entries extracted from TZDB raw files
# (https://github.com/eggert/tz), sorted by target link (i.e. the second
# argument of the 'Link' tag).

END

# Sort using native ASCII bytes, instead of Unicode
export LC_ALL=C

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
    grep '^Link' | awk '{print "Link", $2, $3}' | sort -t ' ' -k 3
