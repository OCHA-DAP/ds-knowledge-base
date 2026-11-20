---
content_type: infrastructure
last_reviewed: "2026-11-20"   # bump when a human verifies the page is still accurate
---

# datascience.unocha.org: the team site's structure and names

> **Proposed on 2026-11-20 (D126), for the team to review. Nothing is built yet.**
> Only part of the team's work moves here from GitHub Pages (`ocha-dap.github.io/<repo>/`);
> the rest stays where it is.

One Azure Front Door profile holds the `datascience.unocha.org` name and its certificate,
and sends each path to an Azure Static Web App (Standard plan). OCHA's IT team (TSS) keeps
the DNS records in the `unocha.org` zone. This page sets what goes on the site, the
addresses and the Azure names. How each site is built stays in
[static-data-apps.md](../methods/static-data-apps.md).

## What goes on the site

| Address | What is there | Static Web App |
|---|---|---|
| `datascience.unocha.org/` | The landing page: the flagships first, then the analyses by topic | `chd-ds-web-main` |
| `datascience.unocha.org/<name>/` | A flagship: one of a few products the team keeps up to date for people outside the team | its own, `chd-ds-web-<name>` |
| `datascience.unocha.org/analyses/` | The list of analyses, by topic | `chd-ds-web-main` |
| `datascience.unocha.org/analyses/<slug>/` | One analysis: a repo's site the team wants public and listed | `chd-ds-web-main` (an app of its own if over 100 MB) |
| `ocha-dap.github.io/<repo>/` | Everything else stays on GitHub Pages: team tools and documentation, sites a schedule republishes that are not flagships, password pages, work in progress | none |

- **Flagships** are chosen by the team, a few at a time. Each gets a short product name
  picked by hand, not derived from the repo (`ds-aa-tracking` becomes `/aa-tracker/`).
- **Analyses** keep their repo name without the `ds-` prefix
  (`ds-aa-ner-drought` becomes `/analyses/aa-ner-drought/`). Repos without the prefix keep
  their name. The topics on the landing page and the list are labels on the page, not part
  of the address, so an analysis can change topic without changing address.
- An analysis is **not republished on a schedule**. A site that a scheduled job republishes
  is either a flagship or stays on GitHub Pages: the analyses share one app, and every
  deploy replaces the whole app (next section).
- Each repo's products keep their place under its address, as on GitHub Pages today
  (`/analyses/aa-ner-drought/app/`). The [landing-page
  convention](../methods/static-data-apps.md#one-repo-one-pages-site--the-landing-page-convention)
  carries over unchanged.
- Names must be unique. `analyses`, the flagship names and the landing page's own folders
  are taken at the root; the list of what is on the site should fail on a duplicate (to add).

The knowledge base stays on GitHub Pages: it is the team's working reference and deploys
many times a day. The landing page links to it.

| Today | On the new site |
|---|---|
| `ocha-dap.github.io/ds-aa-tracking/` | `datascience.unocha.org/aa-tracker/` |
| `ocha-dap.github.io/ds-seas5-skill/app/` | `datascience.unocha.org/seas5-alerts/app/` (if a flagship) |
| `ocha-dap.github.io/ds-aa-ner-drought/app/` | `datascience.unocha.org/analyses/aa-ner-drought/app/` |
| `ocha-dap.github.io/pa-aa-fji-storms/` | `datascience.unocha.org/analyses/pa-aa-fji-storms/` |
| `ocha-dap.github.io/ds-aa-som-floods/` | stays |
| `ocha-dap.github.io/ds-knowledge-base/` | stays |

## Which Static Web App serves each part

A Static Web App is deployed as one unit: each deploy replaces everything in it. On the
Standard plan it holds at most 500 MB in its live copy, 2 GB across the live copy and its
preview copies, and 15,000 files
([Microsoft's quota page](https://learn.microsoft.com/en-us/azure/static-web-apps/quotas)).
So:

- **Each flagship has an app of its own**, published by its own repo's workflow on its own
  schedule. It keeps its own preview copies if they still open behind Front Door (to test,
  below).
- **The main app holds the landing page, the list and every analysis.** An assembly job
  builds it: each analysis repo uploads its built site to blob storage, and the job puts
  the latest of each together with the landing page and the list, and deploys them as one.
  On every run it checks the total size and file count and refuses an upload that would
  pass the limit, keeping the last good copy. Analyses are not republished on a schedule,
  so the main app is deployed when someone publishes an analysis; a burst of pushes to
  one analysis means that many deploys of the main app.
- **An analysis over 100 MB gets an app of its own at the same address.** Front Door sends
  `/analyses/<slug>/` to that app, because the most specific path wins over the main app's
  default route. The same move is open to any analysis later (for example if the main app
  passes about 400 MB), and its address does not change.

Front Door passes the path through unchanged, so each app holds its files under its
path: a flagship's app keeps its site in `<name>/`, and the main app keeps the landing
page at its root and each analysis in `analyses/<slug>/`. Public apps switch off the
built-in sign-in addresses (`/.auth/login/…`) in their configuration. The main app also
answers any address that belongs to nothing else, with its 404 page.

With the first cut below, that is 6 apps: the main app, 4 flagships and 1 large
analysis. The Standard plan's list price is USD 9 a month per app, and Front Door Standard
has a base fee of USD 35 a month: about USD 89 a month. Each further flagship adds USD 9.
The analyses in the main app measure 179 MB in 1,496 files, with
10 not measured; they get measured before the move.

## Old addresses

Only the repos that move need anything. GitHub Pages can't send a real redirect, so each
old page of a moved repo gets a small page that forwards the reader to its new address,
looked up from the list of what is on the site. Password pages are skipped (next section).

- **Data files that programs read** (JSON, CSV, `llms.txt`) stay published at the old
  address as well for a transition period: a forwarding page breaks a program that
  expects data. The KB's own AA tools read the AA tracker's open files this way, and the
  KB's generators and MCP tools that name `ocha-dap.github.io` addresses of moved repos
  get updated in the same change.
- **Links inside the sites** that use the full `ocha-dap.github.io` address of their own
  site get changed to the new address, so they don't bounce through a forwarding page.
  Links to sites that stay on GitHub Pages don't change.

## Password pages stay on GitHub Pages for now

Pages that have a password today stay on GitHub Pages until Entra ID sign-in is set up for
the team. Six repos stay whole: three are password sites, and three have nothing open
apart from a landing page. At least five of the repos that move mix open and
password pages. For those:

- Before the repo moves, it lists its password paths in the repo itself. Its deploy (or
  the assembly job, for an analysis) leaves them out of the new site.
- The forwarding pages skip them.
- Moved pages link to them by their full `ocha-dap.github.io` address.

The last column of the [table below](#first-cut-every-repo-today) shows the password
pages the pages registry declares. The registry misses some, so the repo's own list is the
one that counts.

## Signed-in sites: one hostname each (later)

Once sign-in exists, each signed-in site gets its own hostname under
`datascience.unocha.org`. Static Web Apps and App Service run their built-in sign-in at
`/.auth/` on the root of the host, so one hostname can carry only one signed-in app.

| Hostname | For |
|---|---|
| `staff.datascience.unocha.org/<product>/` | Pages any UN account may open (sign-in limited to the UN tenant, which needs the Standard plan's own Entra registration) |
| `tracker.datascience.unocha.org` | The AA tracker's development and admin pages |
| `<neutral-name>.datascience.unocha.org` | One per restricted audience (one Entra group) |

Every hostname that has a certificate appears in public certificate logs. Restricted
hostnames therefore get neutral names that say nothing about their content.

## Azure names

| Thing | Name |
|---|---|
| Static Web App, main (landing page and analyses) | `chd-ds-web-main` |
| Static Web App, a flagship | `chd-ds-web-<name>`, after its address (`chd-ds-web-aa-tracker`) |
| Static Web App, an analysis of its own | `chd-ds-web-<slug>` (`chd-ds-web-regional-forecasts`) |
| Static Web App, signed-in | `chd-ds-web-<hostname label>` (`chd-ds-web-staff`, `chd-ds-web-tracker`) |
| Front Door profile | `chd-ds-frontdoor` |
| Front Door endpoint | `chd-ds` |
| Front Door origin group | the app's name |
| Front Door route | `route-<name or slug>`; `route-main` for the default route |
| Front Door custom domain | the hostname with hyphens for dots (`datascience-unocha-org`) |
| Tags on every app | `tier` (`public`, `staff` or `restricted`) and `repo` (the repo name, `ds-aa-tracking`) |

`chd-ds-` follows the team's existing Azure names (`chd-ds-demos`, `chd-ds-token-issuer`).
`web` marks the site's apps apart from the App Service apps. App names follow the address,
not the repo, so the `repo` tag records where the site is built. The main app takes the
default route (`/*`); each flagship and each analysis with an app of its own takes one
route for its path with and without the trailing slash. Front Door Standard allows 100
routes and 100 origin groups in a profile.

## The AA tracker

- Its open site (8.4 MB) moves to `datascience.unocha.org/aa-tracker/`, on its own app
  (`chd-ds-web-aa-tracker`). The build already puts the open site at the top and
  `dev/` and `admin/` below it, so only the top is published there.
- `dev/` and `admin/` stay on GitHub Pages with their passwords until sign-in exists. They
  then move to `tracker.datascience.unocha.org`. That hostname stays the same if the
  tracker later becomes an App Service app.

## The two Static Web Apps that exist today

- `dsci-monitor`: the old pipelines-status dashboard. Its deploy workflow was removed on
  2026-09-30. To delete.
- `chd-ds-satellite-impact-viewer`: stays as it is. Whether it joins the site is its
  owner's decision; joining means the Standard plan and an address.

## To test before any site moves

1. A flagship app and the main app behind `datascience.unocha.org`, including the
   flagship's address without its trailing slash (`/aa-tracker`).
2. One analysis on an app of its own at `/analyses/<slug>/` while the main app keeps the
   rest of `/analyses/`, with the address unchanged.
3. Whether a pull request's preview copy can still be opened once the app accepts
   requests only from our Front Door.
4. One deploy of the main app by the assembly job, with its size check.

## Open questions for the team

- **Hosted or listed.** Proposed: analyses move to `/analyses/<slug>/`. The other way:
  they stay on GitHub Pages and `/analyses/` only lists them, with links out. That moves
  far less and costs nothing extra, but leaves most addresses on `github.io`.
- **Which flagships, and their names.** The first cut takes the AA tracker and guesses
  three more: the SEAS5 precipitation alerts, the geospatial impact estimates and the
  storm alerts sign-up.
- **Sites republished on a schedule that are not flagships**: the AA monitoring sites for
  Ethiopia, Haiti, Nigeria and Somalia, Google Flood Hub, the CERF supplement review and
  the three mirror explorers. Proposed: they stay on GitHub Pages, and the AA tracker
  links to the AA ones. Any of them could instead get an app of its own under
  `/analyses/` for USD 9 a month.
- **The folder name**: `/analyses/` (proposed) or `/projects/`, since a repo's site often
  mixes reports, apps and monitoring pages.
- **Where the list of what is on the site lives**, with the landing page and the assembly
  job: a small site repo (proposed), so that what goes public is one reviewed change, or
  the KB, next to the pages registry.
- `staff` and `tracker` as hostname labels.
- The superseded pipeline status page and `ocha-lens` (Pages serves a package's branch
  there) could switch Pages off.

## First cut: every repo today

Snapshot of 2026-11-20 for the 49 public repos in the [pages registry](pages-registry.md);
48 answer at their root (`ocha-lens` returns 404). Seven more team repos have Pages
switched on (five private, two old `pa-` repos); they are not part of this plan yet. After
the move, [pages-registry.md](pages-registry.md) is the record of what is published where.

The first cut, for the team to change: 4 flagships, 23 analyses,
20 repos that stay on GitHub Pages (9 republished on a schedule,
5 team tools and documentation, 6 behind passwords), and
2 that could switch Pages off.

- **Publish schedule:** a cron workflow in the repo that publishes Pages, or "by another
  job" when the site was deployed nearly every day of the last 30 with no such workflow.
- **Deploys:** every Pages deploy in the last 30 days, including the ones made while a
  site was being built (100+ means at least 100).
- **Size:** the files in the Pages source folder, or the last kept build (compressed,
  marked "build"). Sizes are not measured for 15 repos.

<details>
<summary>All 49 repos: first cut, new address, app, publish schedule, size, password pages</summary>

| Repo | First cut | New address | App | Publish schedule | Deploys, 30 days | Size | Password pages (registry) | Note |
|---|---|---|---|---|---|---|---|---|
| `ds-aa-tracking` | Flagship | `/aa-tracker/` | `chd-ds-web-aa-tracker` | daily | 100+ | 8.4 MB | `admin/`, `dev/` | Open site only (8.4 MB); dev/ and admin/ have passwords and stay on GitHub Pages |
| `ds-geospatial-impact-estimates` | Flagship | `/impact-estimates/` | `chd-ds-web-impact-estimates` | daily | 27 | not measured | `experimental/`, `manuscript/`, `story-v2/`, `story-v3/`, `story/` |  |
| `ds-seas5-skill` | Flagship | `/seas5-alerts/` | `chd-ds-web-seas5-alerts` | monthly | 7 | not measured |  |  |
| `ds-storms-alerts` | Flagship | `/storm-alerts/` | `chd-ds-web-storm-alerts` |  | 3 | 16.1 MB |  |  |
| `ds-aa-bfa-drought` | Analysis | `/analyses/aa-bfa-drought/` | `chd-ds-web-main` |  | 9 | not measured | `hnrp-2027/` |  |
| `ds-aa-bfa-flooding` | Analysis | `/analyses/aa-bfa-flooding/` | `chd-ds-web-main` |  | 0 | 0.6 MB |  |  |
| `ds-aa-cub-hurricanes` | Analysis | `/analyses/aa-cub-hurricanes/` | `chd-ds-web-main` |  | 0 | 9 MB |  |  |
| `ds-aa-drought-indicators` | Analysis | `/analyses/aa-drought-indicators/` | `chd-ds-web-main` |  | 0 | not measured |  |  |
| `ds-aa-lac-dry-corridor` | Analysis | `/analyses/aa-lac-dry-corridor/` | `chd-ds-web-main` |  | 0 | 78.9 MB |  |  |
| `ds-aa-ner-drought` | Analysis | `/analyses/aa-ner-drought/` | `chd-ds-web-main` |  | 0 | 32.9 MB |  |  |
| `ds-aa-npl-flooding` | Analysis | `/analyses/aa-npl-flooding/` | `chd-ds-web-main` |  | 0 | 3.9 MB |  |  |
| `ds-aa-tcd-drought` | Analysis | `/analyses/aa-tcd-drought/` | `chd-ds-web-main` |  | 4 | 7.6 MB | `evaluation_villages_2026/`, `w3_resultat_2026/` |  |
| `ds-aa-uga-flooding` | Analysis | `/analyses/aa-uga-flooding/` | `chd-ds-web-main` |  | 0 | not measured | `partner/`, `triggers/` |  |
| `ds-aa-vut-cyclones` | Analysis | `/analyses/aa-vut-cyclones/` | `chd-ds-web-main` |  | 1 | 1.6 MB |  |  |
| `ds-afro-cholera` | Analysis | `/analyses/afro-cholera/` | `chd-ds-web-main` |  | 0 | 7.2 MB |  |  |
| `ds-asap-trends` | Analysis | `/analyses/asap-trends/` | `chd-ds-web-main` |  | 0 | not measured |  |  |
| `ds-c3s-viz` | Analysis | `/analyses/c3s-viz/` | `chd-ds-web-main` |  | 0 | under 0.1 MB |  |  |
| `ds-eri-drought` | Analysis | `/analyses/eri-drought/` | `chd-ds-web-main` |  | 0 | not measured |  |  |
| `ds-flood-gfm` | Analysis | `/analyses/flood-gfm/` | `chd-ds-web-main` |  | 1 | 13.4 MB |  |  |
| `ds-fts` | Analysis | `/analyses/fts/` | `chd-ds-web-main` |  | 0 | not measured |  |  |
| `ds-geospatial-impact-exposure` | Analysis | `/analyses/geospatial-impact-exposure/` | `chd-ds-web-main` |  | 0 | not measured |  |  |
| `ds-onegms-public` | Analysis | `/analyses/onegms-public/` | `chd-ds-web-main` |  | 0 | 0.1 MB |  |  |
| `pa-aa-fji-storms` | Analysis | `/analyses/pa-aa-fji-storms/` | `chd-ds-web-main` |  | 0 | 23.5 MB |  |  |
| `ds-precip-intercomparison` | Analysis | `/analyses/precip-intercomparison/` | `chd-ds-web-main` |  | 2 | not measured |  |  |
| `ds-regional-forecasts` | Analysis | `/analyses/regional-forecasts/` | `chd-ds-web-regional-forecasts` |  | 0 | 144.1 MB |  | An app of its own for its size (144 MB), at the same address |
| `ds-storm-impact-harmonisation` | Analysis | `/analyses/storm-impact-harmonisation/` | `chd-ds-web-main` |  | 1 | not measured |  |  |
| `ds-teleconnections` | Analysis | `/analyses/teleconnections/` | `chd-ds-web-main` |  | 38 | not measured |  |  |
| `ds-aa-caf-flooding` | Stays on GitHub Pages |  |  |  | 0 | 8 MB | whole site | Password site |
| `ds-aa-eth-flooding` | Stays on GitHub Pages |  |  | daily, by another job | 67 | 0.3 MB |  | Republished on a schedule, not a flagship |
| `ds-aa-hti-hurricanes` | Stays on GitHub Pages |  |  | 4 times a day | 47 | not measured |  | Republished on a schedule, not a flagship |
| `ds-aa-mli-drought` | Stays on GitHub Pages |  |  |  | 6 | 0.2 MB (build) | `trigger-review/` | Only its landing page is open |
| `ds-aa-nga-flooding` | Stays on GitHub Pages |  |  | twice a day | 65 | 34.4 MB (build) |  | Republished on a schedule, not a flagship |
| `ds-aa-som-floods` | Stays on GitHub Pages |  |  | daily | 40 | 22.9 MB (build) |  | Republished on a schedule, not a flagship |
| `ds-acled-trends` | Stays on GitHub Pages |  |  |  | 0 | not measured | whole site | Password site |
| `ds-cerf-supplement` | Stays on GitHub Pages |  |  | daily | 63 | under 0.1 MB (build) |  | Republished on a schedule, not a flagship |
| `ds-external-aa-frameworks` | Stays on GitHub Pages |  |  |  | 0 | 2.2 MB | whole site | Password site |
| `ds-fewsnet-mirror` | Stays on GitHub Pages |  |  | daily | 31 | 4.9 MB (build) |  | Republished on a schedule, not a flagship |
| `ds-google-flood-hub` | Stays on GitHub Pages |  |  | daily | 31 | under 0.1 MB (build) |  | Republished on a schedule, not a flagship |
| `ds-heat-exposure` | Stays on GitHub Pages |  |  | daily | 25 | 7.8 MB (build) | `dashboard/` | Only its landing page is open |
| `ds-hnrp-mirror` | Stays on GitHub Pages |  |  | daily | 31 | 9.1 MB (build) |  | Republished on a schedule, not a flagship |
| `ds-ipc-mirror` | Stays on GitHub Pages |  |  | daily | 31 | 6.8 MB (build) |  | Republished on a schedule, not a flagship |
| `ds-knowledge-base` | Stays on GitHub Pages |  |  | daily, by another job | 100+ | 3.1 MB (build) | `systems-map/` | The team's working reference; the landing page links to it |
| `ds-longterm-outlook` | Stays on GitHub Pages |  |  |  | 5 | not measured | `outlook/` | Only its landing page is open |
| `ocha-mailchimp` | Stays on GitHub Pages |  |  |  | 0 | under 0.1 MB |  | Library documentation |
| `ds-raster-stats` | Stays on GitHub Pages |  |  |  | 0 | 5.8 MB |  | Pipeline documentation |
| `ds-rosea-thresholds` | Stays on GitHub Pages |  |  |  | 3 | 0.8 MB |  | Internal tool under development |
| `ds-storms-pipeline` | Stays on GitHub Pages |  |  |  | 0 | 1.2 MB |  | The pipeline's own dashboard |
| `ocha-lens` | Switch Pages off? |  |  |  | 0 | 56.5 MB |  | Pages serves a Python package's branch root; no page at its root. Switch Pages off? |
| `ds-pipelines-status` | Switch Pages off? |  |  | daily, by another job | 31 | 0.8 MB |  | Superseded by the pipeline registry: switch Pages off? |

</details>
