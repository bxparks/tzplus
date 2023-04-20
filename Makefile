TZDB := ../tz

TOOLS := tools

TZDB_VERSION := 2023c

# Generate list of Zones and Links.
data/zones_and_links.txt: $(TOOLS)/extract_zones_and_links.sh tzfiles
	$(TOOLS)/extract_zones_and_links.sh tzfiles > $@

# Copy the TZDB data files into tzfiles directory.
tzfiles: $(TOOLS)/copytz.sh $(TZDB)
	$(TOOLS)/copytz.sh --tag $(TZDB_VERSION) $(TZDB) $@

clean:
	rm -rf tzfiles
