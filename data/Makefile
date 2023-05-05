TOOLS_DIR := ../tools

TZDB_DIR := ../tzdb

#-----------------------------------------------------------------------------

# Verify the various data files, in particular, country_timezones.txt.
.phony: verify
verify: zones.txt links.txt
	$(TOOLS_DIR)/verify_data.py \
		--zones zones.txt \
		--links links.txt \
		--classified_zones classified_zones.txt \
		--classified_links classified_links.txt \
		--iso_long iso3166_long.txt \
		--iso_short iso3166_short.txt \
		--regions regions.txt \
		--region_country_timezones country_timezones.txt

# List the timezones in a hierarchical menu that could be used in a
# microcontroller environment.
.PHONY: list
list: regions.txt iso3166_short.txt country_timezones.txt
	$(TOOLS_DIR)/list_zones.py \
		--region regions.txt \
		--countries iso3166_short.txt \
		country_timezones.txt

# Extract the Zone and Link entries from ../tzdb into zones.txt and links.txt.
.phony: extract
extract: zones.txt links.txt

#-----------------------------------------------------------------------------

# Extract Zones.
zones.txt: $(TOOLS_DIR)/extract_zones.sh $(TZDB_DIR)
	$(TOOLS_DIR)/extract_zones.sh $(TZDB_DIR) > $@

# Extract Links.
links.txt: $(TOOLS_DIR)/extract_links.sh $(TZDB_DIR)
	$(TOOLS_DIR)/extract_links.sh $(TZDB_DIR) > $@

#-----------------------------------------------------------------------------

clean:
	rm -rf zones.txt links.txt country_timezones.out
