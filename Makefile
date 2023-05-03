TZ_REPO := ../tz

TOOLS_DIR := tools

TZDB_VERSION := 2023c

#-----------------------------------------------------------------------------

# Copy the TZDB data files into the ./tzdb/ directory.
tzdb: $(TOOLS_DIR)/copytz.sh $(TZ_REPO)
	$(TOOLS_DIR)/copytz.sh --tag $(TZDB_VERSION) $(TZ_REPO) $@
	echo $(TZDB_VERSION) > $@/version.txt

#-----------------------------------------------------------------------------

clean:
	rm -rf tzdb data/zones.txt data/links.txt
