TZ_REPO := ../tz

TOOLS := tools

TZDB_VERSION := 2023c

all: data/zones.txt data/links.txt

# Extract Zones.
data/zones.txt: $(TOOLS)/extract_zones.sh tzdb
	$(TOOLS)/extract_zones.sh tzdb > $@

# Extract Links.
data/links.txt: $(TOOLS)/extract_links.sh tzdb
	$(TOOLS)/extract_links.sh tzdb > $@

# Copy the TZDB data files into the ./tzdb/ directory.
tzdb: $(TOOLS)/copytz.sh $(TZ_REPO)
	$(TOOLS)/copytz.sh --tag $(TZDB_VERSION) $(TZ_REPO) $@

clean:
	rm -rf tzdb data/zones.txt data/links.txt
