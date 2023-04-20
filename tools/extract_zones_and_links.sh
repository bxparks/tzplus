#!/usr/bin/env bash
#
# Extract the Zones and Links in the TZDB files inside the given directory.
#
# Usage:
#   $ ./extract_zones_and_links.sh tzdir
#
# Author: Brian Park
# License: Public Domain

set -eu

if [[ $# != 1 ]]; then
    echo 'Usage: extract_zones.sh tzdir'
    exit 1
fi

cd $1

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
    egrep '^(Zone|Link)' |
    awk '/^Zone/ {print "Zone", $2}
        /^Link/ {print "Link", $3, "->", $2}' |
    sort |
    uniq
