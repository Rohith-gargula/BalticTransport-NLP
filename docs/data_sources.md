# Data sources and rights checklist
This file is a source-planning checklist, not a statement that feeds have been verified or that content is licensed for redistribution.

Candidate discovery:
- LSM (Latvian Public Media): investigate language-specific RSS feeds and article reuse terms.
- Latvian public-sector/open-data portals: check dataset licenses and terms.
- Public transport operators: check announcement reuse permissions.
- Russian/English sources: select reputable Baltic-region transport publishers and verify feed, language, and license.

Before collecting/publishing each source:
- [ ] Confirm URL/feed works and language coverage.
- [ ] Review terms of service, copyright, robots policy, and license.
- [ ] Decide whether full text can be stored and redistributed; if not, retain permitted metadata/snippets and source links only.
- [ ] Record source name, URL, access date, license/terms URL, and collection method.
- [ ] Avoid personal data; remove irrelevant names/contact details where possible.
- [ ] Respect rate limits and use a descriptive user-agent.
## GTFS Public Transport Data

**Official publisher:** VSIA Autotransporta direkcija (ATD)

**Official source:** https://data.gov.lv/dati/eng/dataset/atd-gtfs

**Official archive:** https://www.atd.lv/sites/default/files/GTFS/gtfs-latvia-lv.zip

**Official source licence:** CC0 1.0 (as listed by the Latvian Open Data Portal).

**Format:** General Transit Feed Specification (GTFS).

**Geographical coverage:** Latvia.

**Time zone:** Europe/Riga.

**Project usage:** Route analysis, stop analysis, timetable analysis, service calendar analysis and data-quality assessment.

**Provenance status:** Three of the ten project GTFS files matched the archived 2018 source byte-for-byte. Seven differed. The exact source version and redistribution rights of the project copy require further verification.

**Important:** The CC0 licence of the official archive should not be assumed to cover every project file until its provenance is confirmed.