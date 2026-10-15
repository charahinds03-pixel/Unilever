# Phase 1: Source discovery

Status as of 15 Oct 2026. Checkpoint 1: waiting for your go-ahead.

## Two blockers

1. **Nothing is downloaded yet.** The environment's network policy returns 403 for every source host. That covers unilever.com, sec.gov, eur-lex, uscourts.gov, fda.gov and the rest. WebFetch can't reach them either. Only web search works. I used search to find and confirm URLs. I have not used search-result text as evidence, and nothing goes in the tracker until its file is saved.
2. **`brief.md` is missing.** It isn't in this repo, the other two repos, or your Google Drive. Phase 1 used the targets in the prompt. Phase 3 needs the brief's five fixes and regional panel framework.

When network access opens, `python -m src.fetch` downloads all 56 auto/resolve rows in `data/source_candidates.csv`. It checks robots.txt, sends a descriptive User-Agent, sleeps 2 to 3 s between requests and caches results. It saves to `sources/raw/` with publisher and date in each filename.

Hosts to allow (28): `blogs.duanemorris.com bmv.com.mx cms.law dev.uschamber.com eur-lex.europa.eu iclg.com judicialhellholes.org marathonstrategies.com oag.ca.gov ocdistrictattorney.gov practiceguides.chambers.com www.catribunal.org.uk www.consumentenbond.nl www.duanemorris.com www.eerstekamer.nl www.fda.gov www.grocerygazette.co.uk www.investegate.co.uk www.investing.com www.jpml.uscourts.gov www.leagle.com www.rechtspraak.nl www.sec.gov www.simmons-simmons.com www.swissre.com www.taylorwessing.com www.unilever.com www.uschamber.com`. Likely needed later: `www.gov.uk`, `www.acm.nl`, and `www.courtlistener.com` if you approve it.

## What I found, by slide

Fetch mode `auto` means a direct URL confirmed by search. `resolve` means a landing page confirmed, with the file link picked up at fetch time. Full detail is in `data/source_candidates.csv`.

### Slide 1: global footprint

| ID | Source | Type | Access | Note |
|---|---|---|---|---|
| C001 | Annual Report and Accounts 2025 (PDF 6.16 MB, 12 Mar 2026) | company | open (resolve) | Segment note by geography and business group |
| C002 | Form 20-F FY2025 (SEC EDGAR) | company | open | Same figures plus legal provisions. SEC needs a contact in the User-Agent |
| C003 | Historical financials excluding Ice Cream | company | open | Restated quarterly turnover by geography, 2023 to 2025 |
| C004 | Unilever charts 2016-2025 | company | open | Regional split with and without Ice Cream |
| C005-C008 | Business group overviews (PC, B&W, HC, Foods) | company | open | FY25 top-5 markets per business group |
| C009 | Q1 2026 trading statement (RNS) | company | open | |
| C010-C011 | H1 2026 results announcement and 6-K | company | open | |
| C012 | Q3 2026 trading statement | company | pending | Not out yet. Search cites 28 Oct 2026 |
| C013-C014 | Ice Cream demerger completion (BMV filing copy, Reuters) | company, news | open | |
| C015 | Foods + McCormick combination release (31 Mar 2026) | company | open | |

### Slide 2: regional comparison

| ID | Source | Type | Access |
|---|---|---|---|
| C020 | Directive (EU) 2020/1828, OJ text | regulator | open |
| C021-C022 | Directive (EU) 2024/2853 and May 2026 corrigendum | regulator | open |
| C023 | CMS European Class Action Report 2026 (published 8 Oct 2026) | law firm research | landing open; PDF may need a form |
| C024-C025 | CAT judgments (s47B filter) and Simmons & Simmons tracker | court, law firm | open |
| C026-C027 | Rechtspraak WAMCA recommendations; WODC five-year WAMCA evaluation (Nov 2025) | court, government research | open |
| C030-C041 | Chambers 2026 and ICLG 2026 product liability chapters: India, Brazil, China, Indonesia, Mexico, South Africa | law firm guides | Chambers China and ICLG India confirmed. The rest are unconfirmed |

The RoW country list is provisional. It comes from Unilever's FY25 business group top-5 markets in C005 to C008: India, Brazil, China, Indonesia, Mexico and South Africa. I'll confirm it against the annual report before pulling guides.

### Slides 3 and 4: US landscape and drivers

| ID | Source | Type | Access |
|---|---|---|---|
| C050-C052 | Judicial Hellholes executive summaries 2025-26, 2024-25, 2023-24 | **advocacy** | open (web pages, no PDF) |
| C053-C055 | JPML pending MDLs by district and by actions (Aug 2026; latest resolved at fetch) | court | open |
| C056 | JPML order denying an MDL for Unilever benzene cases (MDL 3068, 2023) | court | open |
| C057 | Marathon Strategies 2026 report (2025 verdicts) | industry research | **download form: manual** |
| C058-C059 | Marathon 2026 press release; 2025 edition PDF (2024 verdicts) | industry research | open |
| C060-C061 | Swiss Re sigma 4/2024 (social inflation); "Verdicts on trial" (2025) | reinsurer research | open |
| C062-C064 | Duane Morris Class Action Review 2026, mid-year 2026, privacy review | law firm research | open; full Review may need a form |
| C065-C066 | US Chamber ILR nuclear verdicts (2024); commercial auto tort costs (2025) | **advocacy** | open |
| C070 | FDA posting of Unilever's dry shampoo benzene recall (21 Oct 2022) | regulator | open |
| C074-C075 | CA Attorney General Prop 65 notices naming Unilever entities (2021, 2024) | regulator | open |
| C077-C079 | UK CMA probe closure (news); Netherlands ACM intervention (Consumentenbond, Taylor Wessing) | news, advocacy, law firm | open |
| C082 | Orange County DA settlement with Unilever (2015, Axe packaging) | regulator | open |
| C083 | Suave Keratin kit settlement opinion (Leagle) | court | match to confirm |

### Slide 5: nuclear verdict pathways

This slide uses C057 to C061 and C065 to C066. The split by line of business (personal care chemical, food and labeling, fleet/auto, premises) needs the full Marathon report (C057).

## Couldn't get or couldn't confirm

All 23 items are in `data/gaps.csv`. The main ones:

- **No PFAS suit naming Unilever** turned up. Nor did a US greenwashing class action (2024 to 2026), a BIPA suit, or a state AG action since 2020. Themes 4 and 5 may need labeled industry examples rather than Unilever cases.
- **Court records for the benzene class actions** turned up only on HarrisMartin and Law360, which are paywalled and off limits. That covers the D. Conn. dry shampoo cases (proposed $3.6M, preliminary approval reported denied) and the N.D. Ill. Suave $2M settlement.
- **FDA notice for the March 2022 Suave antiperspirant recall**: not found. Only local TV coverage.
- The **CMA gov.uk case page** and **ACM's own release** weren't found.
- **Swiss Re**: no sigma newer than 4/2024 on this topic.
- **2026 chapters** for Brazil, Indonesia, Mexico and South Africa: not confirmed in either guide.

## Needs manual download (to `sources/manual/`)

- **C057** Marathon Strategies 2026 report (download form): https://marathonstrategies.com/corporate-verdicts-go-thermonuclear/
- These may need a form; I'll confirm once fetched: CMS European Class Action Report 2026 PDF (C023) and the full Duane Morris Class Action Review 2026 (C062).

## Corrections to the brief from discovery

1. **The dry shampoo recall was October 2022, not 2021.** FDA posted it on 21 Oct 2022. It covered products made before October 2021.
2. **There is a second portfolio change.** On 31 Mar 2026 Unilever agreed to combine Foods with McCormick, with completion expected by mid-2027. The FY2025 "continuing operations" basis excludes Ice Cream only.
3. **The Ice Cream demerger** completed in early December 2025. Sources differ on 5 versus 6 Dec. Shares listed on 8 Dec 2025 in Amsterdam, London and New York. The Q4 and FY2025 accounts report Ice Cream as discontinued.
4. **The UK CMA closed its Unilever green claims probe in November 2024** with no finding on compliance. It was not a 2025 outcome.
5. **No MDL exists for the Unilever benzene cases.** The JPML denied centralization (MDL 3068). Slide 3's MDL markers will show industry MDLs relevant to Unilever's lines, not Unilever's own.
6. **Judicial Hellholes is published as web pages.** Coverage names both ATRF and ATRA as publisher. I'll cite ATRF as the site does and label it advocacy everywhere.

## Decisions I need from you

1. **Network**: allow the hosts above, or switch the environment to full access.
2. **brief.md**: add it to the repo.
3. **CourtListener**: OK to use it for the benzene case dockets? It's a free, no-login public archive of federal court filings. It mirrors documents first bought from PACER, which is why I'm asking.
4. **User-Agent contact**: SEC EDGAR refuses requests without one. Give me an email or URL to set as `SCRAPER_CONTACT`, or I'll skip sec.gov and use the unilever.com PDF.
5. **Slide 1 basis**: my default is FY2025 as reported (Ice Cream excluded, Foods included), with a footnote on the McCormick deal. The alternative is to also show a home and personal care only view. That view would rest on Unilever's FY2025 figure of about €39bn excluding Foods, which is still unconfirmed.
