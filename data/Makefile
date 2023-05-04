TOOLS_DIR := ../tools

TZDB_DIR := ../tzdb

#-----------------------------------------------------------------------------

.PHONY: country_timezones
country_timezones: zones.txt links.txt
	$(TOOLS_DIR)/check_data.py \
		--zones zones.txt \
		--links links.txt \
		--classified_zones classified_zones.txt \
		--classified_links classified_links.txt \
		--iso_long iso3166_long.txt \
		--iso_short iso3166_short.txt \
		--region regions.txt \
		--country_timezones country_timezones.txt

.PHONY: geonames
geonames: zones.txt links.txt
	$(TOOLS_DIR)/check_data.py \
		--zones zones.txt \
		--links links.txt \
		--classified_zones classified_zones.txt \
		--classified_links classified_links.txt \
		--iso_long iso3166_long.txt \
		--iso_short iso3166_short.txt \
		--region regions.txt \
		--geonames ../geonames/timeZones.txt

# List the timezones in a hierarchical menu that might match something used in
# a microcontroller environment.
.PHONY: list
list: regions.txt iso3166_short.txt country_timezones.txt
	$(TOOLS_DIR)/list_zones.py \
		--region regions.txt \
		--countries iso3166_short.txt \
		country_timezones.txt

# Extract Zones.
zones.txt: $(TOOLS_DIR)/extract_zones.sh $(TZDB_DIR)
	$(TOOLS_DIR)/extract_zones.sh $(TZDB_DIR) > $@

# Extract Links.
links.txt: $(TOOLS_DIR)/extract_links.sh $(TZDB_DIR)
	$(TOOLS_DIR)/extract_links.sh $(TZDB_DIR) > $@

#-----------------------------------------------------------------------------

clean:
	rm -rf zones.txt links.txt country_timezones.out
