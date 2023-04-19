#!/usr/bin/env bash
#
# Extract the list of ISO 3166 country codes.
#
# Usage
#   $ ./extract_iso_codes.sh tzdir
#
# Author: Brian Park
# License: Public Domain

set -eu

if [[ $# != 1 ]]; then
    echo 'Usage: extract_zones.sh tzdir'
    exit 1
fi

cd $1

grep '^[^#]' iso3166.tab | awk '{print $1}' | sort
