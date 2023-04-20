TZ_REPO := ../tz

TOOLS := tools

TZDB_VERSION := 2023c

# Generate list of Zones and Links.
data/zones_and_links.txt: $(TOOLS)/extract_zones_and_links.sh tzdb
	$(TOOLS)/extract_zones_and_links.sh tzdb > $@

# Copy the TZDB data files into the ./tzdb/ directory.
tzdb: $(TOOLS)/copytz.sh $(TZ_REPO)
	$(TOOLS)/copytz.sh --tag $(TZDB_VERSION) $(TZ_REPO) $@

clean:
	rm -rf tzdb
