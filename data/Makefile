TOOLS_DIR := ../tools

TZDB_DIR := ../tzdb

#-----------------------------------------------------------------------------

.PHONY: country_timezones
country_timezones:
	$(TOOLS_DIR)/check_data.py \
		--zones zones.txt \
		--links links.txt \
		--classified_zones classified_zones.txt \
		--classified_links classified_links.txt \
		--iso_long iso3166_long.txt \
		--iso_short iso3166_short.txt \
		--country_timezones country_timezones.txt

.PHONY: geonames
geonames:
	$(TOOLS_DIR)/check_data.py \
		--zones zones.txt \
		--links links.txt \
		--classified_zones classified_zones.txt \
		--classified_links classified_links.txt \
		--iso_long iso3166_long.txt \
		--iso_short iso3166_short.txt \
		--country_timezones ../geonames/timeZones.txt

# Extract Zones.
zones.txt: $(TOOLS_DIR)/extract_zones.sh $(TZDB_DIR)
	$(TOOLS_DIR)/extract_zones.sh $(TZDB_DIR) > $@

# Extract Links.
links.txt: $(TOOLS_DIR)/extract_links.sh $(TZDB_DIR)
	$(TOOLS_DIR)/extract_links.sh $(TZDB_DIR) > $@

#-----------------------------------------------------------------------------

clean:
	rm -rf zones.txt links.txt country_timezones.out
