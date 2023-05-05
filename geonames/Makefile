TOOLS_DIR := ../tools

# Verify the timeZones.txt copied from
# https://download.geonames.org/export/dump/timeZones.txt.
.PHONY: verify
verify:
	$(TOOLS_DIR)/verify_data.py \
		--zones ../data/zones.txt \
		--links ../data/links.txt \
		--classified_zones ../data/classified_zones.txt \
		--classified_links ../data/classified_links.txt \
		--iso_orig ../tzdb/iso3166.tab \
		--iso_long ../data/iso3166_long.txt \
		--iso_short ../data/iso3166_short.txt \
		--regions ../data/regions.txt \
		--country_timezones timeZones.txt
