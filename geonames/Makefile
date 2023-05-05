TOOLS_DIR := ../tools

# Verify the timeZones.txt copied from
# https://download.geonames.org/export/dump/timeZones.txt.
.PHONY: verify
verify:
	$(TOOLS_DIR)/check_data.py \
		--zones ../data/zones.txt \
		--links ../data/links.txt \
		--classified_zones ../data/classified_zones.txt \
		--classified_links ../data/classified_links.txt \
		--iso_long ../data/iso3166_long.txt \
		--iso_short ../data/iso3166_short.txt \
		--region ../data/regions.txt \
		--geonames ../geonames/timeZones.txt
