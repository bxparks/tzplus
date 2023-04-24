TOOLS_DIR := ../tools

TZDB_DIR := ../tzdb

#-----------------------------------------------------------------------------

country_timezones: \
$(TOOLS_DIR)/check_timezone_files.py \
zones.txt \
links.txt \
resolved_links.txt \
country_timezones.txt \
$(TZDB_DIR)/iso3166.tab
	$(TOOLS_DIR)/check_timezone_files.py \
		--zones zones.txt \
		--links links.txt \
		--resolved_links resolved_links.txt \
		--iso_long iso3166_long.txt \
		--iso_short iso3166_short.txt \
		--country_timezones country_timezones.txt

# Extract Zones.
zones.txt: $(TOOLS_DIR)/extract_zones.sh $(TZDB_DIR)
	$(TOOLS_DIR)/extract_zones.sh $(TZDB_DIR) > $@

# Extract Links.
links.txt: $(TOOLS_DIR)/extract_links.sh $(TZDB_DIR)
	$(TOOLS_DIR)/extract_links.sh $(TZDB_DIR) > $@

#-----------------------------------------------------------------------------

clean:
	rm -rf zones.txt links.txt country_timezones.out
