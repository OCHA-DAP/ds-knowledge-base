---
content_type: infrastructure
last_reviewed: "2026-11-20"   # bump when a human verifies the page is still accurate
---

# datascience.unocha.org: the team site's addresses and names

> **Proposed on 2026-11-20 (D126), for the team to review. Nothing is built yet.**
> The team's sites move here from GitHub Pages (`ocha-dap.github.io/<repo>/`) over time.

One Azure Front Door profile holds the `datascience.unocha.org` name and its certificate,
and sends each path to an Azure Static Web App (Standard plan). OCHA's IT team (TSS) keeps
the DNS records in the `unocha.org` zone. This page sets the addresses and the Azure names.
How each site is built stays in [static-data-apps.md](../methods/static-data-apps.md).

This covers the 49 public repos in the [pages registry](pages-registry.md). Seven more team
repos have Pages switched on (five private, two old `pa-` repos); they are not part of this
plan yet.

## Addresses

### Public sites: one path per repo

- `datascience.unocha.org/` is the team landing page: the hub the KB already generates.
  The KB's own pages move under `/knowledge-base/`.
- `datascience.unocha.org/<slug>/` holds one repo's site. `<slug>` is the repo name
  without its `ds-` prefix. Repos without that prefix keep their name.
- Each repo's products keep their place under it, as on GitHub Pages today:
  `/<slug>/<product>/`. The [landing-page
  convention](../methods/static-data-apps.md#one-repo-one-pages-site--the-landing-page-convention)
  carries over unchanged.
- Slugs must be unique; the registry's check should fail on a duplicate (to add).
  `knowledge-base` and `hub` (the hub's own files) are taken at the root.

| Today | On the new site |
|---|---|
| `ocha-dap.github.io/ds-seas5-skill/app/` | `datascience.unocha.org/seas5-skill/app/` |
| `ocha-dap.github.io/ds-aa-hti-hurricanes/2026/` | `datascience.unocha.org/aa-hti-hurricanes/2026/` |
| `ocha-dap.github.io/pa-aa-fji-storms/` | `datascience.unocha.org/pa-aa-fji-storms/` |
| `ocha-dap.github.io/ds-knowledge-base/` | `datascience.unocha.org/` |
| `ocha-dap.github.io/ds-knowledge-base/db-erd/` | `datascience.unocha.org/knowledge-base/db-erd/` |

### Old addresses

GitHub Pages can't send a real redirect, so each old page gets a small page that forwards
the reader to the new address, by the mapping in the table above. Password pages are
skipped (next section).

- **Data files that programs read** (JSON, CSV, `llms.txt`) stay published at the old
  address as well for a transition period: a forwarding page breaks a program that
  expects data. The KB's own AA tools read the AA tracker's open files this way, and the
  KB's generators and MCP tools that name `ocha-dap.github.io` addresses get updated in
  the same change.
- **Links inside the sites** that use the full `ocha-dap.github.io` address of their own
  site get changed to the new address, so they don't bounce through a forwarding page.

### Password pages stay on GitHub Pages for now

Pages that have a password today stay on GitHub Pages until Entra ID sign-in is set up for
the team. Six repos stay whole: three are password sites, and three have nothing open
apart from a landing page. At least seven other repos mix open and password pages. For those:

- Before the repo moves, it lists its password paths in the repo itself. Its deploy (or
  the assembly job, for the shared app) leaves them out of the new site.
- The forwarding pages skip them.
- Moved pages link to them by their full `ocha-dap.github.io` address.

The last column of the [table below](#every-repo-today) shows the password pages the
pages registry declares. The registry misses some, so the repo's own list is the one
that counts.

### Signed-in sites: one hostname each (later)

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

## Which Static Web App serves each site

A Static Web App is deployed as one unit: each deploy replaces everything in it. On the
Standard plan it holds at most 500 MB in its live copy, 2 GB across the live copy and its
preview copies, and 15,000 files
([Microsoft's quota page](https://learn.microsoft.com/en-us/azure/static-web-apps/quotas)).
One app for every site would therefore be redeployed whole each time any site publishes,
and the sites that would move already measure about 440 MB, with 13 of them unmeasured.
So:

- **The main app** holds the landing page and the KB's own pages. It also serves any
  address that belongs to no repo. A missing page inside a repo's path gets that repo's
  app's 404 page.
- **A repo gets its own app** when a scheduled job republishes its site at least weekly,
  or its site is over 100 MB. Its own workflow publishes it, and it keeps its own preview
  copies if they still open behind Front Door (to test, below).
- **Every other repo goes in one shared app**, published by an assembly job. Each repo
  uploads its built site to blob storage, and the job puts the latest of each together
  and deploys them as one. On every run the job checks the total size and file count
  and refuses an upload that would pass the limit, keeping the last good copy. If the
  shared app passes about 400 MB, the AA framework sites move to a second shared app.
  The 11 shared sites not yet measured get measured before the move.

Which repos get their own app is decided once, at the move, and reviewed on request. A
burst of development pushes doesn't move a repo; it means that many deploys of the
shared app.

Front Door passes the path through unchanged, so each app holds its files under its
path: an own app keeps its site in `<slug>/` inside the app, and the main app keeps the
hub at its root and the KB's pages in `knowledge-base/`. Public apps switch off the
built-in sign-in addresses (`/.auth/login/…`) in their configuration.

On 2026-11-20 these rules give 14 public apps: the main app, 12 apps of their own and the
shared app. The Standard plan's list price is USD 9 a month per app, and Front Door
Standard has a base fee of USD 35 a month.

The main app and the repos that would get an app of their own:

| Repo | New address | App | Publish schedule | Size | Note |
|---|---|---|---|---|---|
| `ds-knowledge-base` | `/` and `/knowledge-base/` | `chd-ds-web-main` | daily, by another job | 3.1 MB (build) | The team landing page (the hub) at the root; KB pages under /knowledge-base/ |
| `ds-aa-eth-flooding` | `/aa-eth-flooding/` | `chd-ds-web-aa-eth-flooding` | daily, by another job | 0.3 MB |  |
| `ds-aa-hti-hurricanes` | `/aa-hti-hurricanes/` | `chd-ds-web-aa-hti-hurricanes` | 4 times a day | not measured |  |
| `ds-aa-nga-flooding` | `/aa-nga-flooding/` | `chd-ds-web-aa-nga-flooding` | twice a day | 34.4 MB (build) |  |
| `ds-aa-som-floods` | `/aa-som-floods/` | `chd-ds-web-aa-som-floods` | daily | 22.9 MB (build) |  |
| `ds-aa-tracking` | `/aa-tracking/` | `chd-ds-web-aa-tracking` | daily | 8.4 MB | Open site only (8.4 MB); dev/ and admin/ have passwords and stay on GitHub Pages |
| `ds-cerf-supplement` | `/cerf-supplement/` | `chd-ds-web-cerf-supplement` | daily | under 0.1 MB (build) |  |
| `ds-fewsnet-mirror` | `/fewsnet-mirror/` | `chd-ds-web-fewsnet-mirror` | daily | 4.9 MB (build) |  |
| `ds-geospatial-impact-estimates` | `/geospatial-impact-estimates/` | `chd-ds-web-geospatial-impact-estimates` | daily | not measured |  |
| `ds-google-flood-hub` | `/google-flood-hub/` | `chd-ds-web-google-flood-hub` | daily | under 0.1 MB (build) |  |
| `ds-hnrp-mirror` | `/hnrp-mirror/` | `chd-ds-web-hnrp-mirror` | daily | 9.1 MB (build) |  |
| `ds-ipc-mirror` | `/ipc-mirror/` | `chd-ds-web-ipc-mirror` | daily | 6.8 MB (build) |  |
| `ds-regional-forecasts` | `/regional-forecasts/` | `chd-ds-web-regional-forecasts` | none | 144.1 MB | Own app for its size (144 MB) |

## Azure names

| Thing | Name |
|---|---|
| Static Web App, main | `chd-ds-web-main` |
| Static Web App, a repo's own | `chd-ds-web-<slug>` (`chd-ds-web-aa-tracking`) |
| Static Web App, shared | `chd-ds-web-shared` (a second one: `chd-ds-web-shared-aa`) |
| Static Web App, signed-in | `chd-ds-web-<hostname label>` (`chd-ds-web-staff`, `chd-ds-web-tracker`) |
| Front Door profile | `chd-ds-frontdoor` |
| Front Door endpoint | `chd-ds` |
| Front Door origin group | the app's name |
| Front Door route | `route-<slug>`; `route-main` for the default route |
| Front Door custom domain | the hostname with hyphens for dots (`datascience-unocha-org`) |
| Tags on every app | `tier` (`public`, `staff` or `restricted`) and `repo` |

`chd-ds-` follows the team's existing Azure names (`chd-ds-demos`, `chd-ds-token-issuer`).
`web` marks the site's apps apart from the App Service apps. The shared app needs one
route that lists all its paths, each with and without the trailing slash; Front Door
Standard allows 100 routes, 100 origin groups and 100 path patterns per route in a
profile.

## The AA tracker

- Its open site (8.4 MB) moves to `datascience.unocha.org/aa-tracking/`, on its own app
  (`chd-ds-web-aa-tracking`). The build already puts the open site at the top and
  `dev/` and `admin/` below it, so only the top is published there.
- `dev/` and `admin/` stay on GitHub Pages with their passwords until sign-in exists. They
  then move to `tracker.datascience.unocha.org`. That hostname stays the same if the
  tracker later becomes an App Service app.

## The two Static Web Apps that exist today

- `dsci-monitor`: the old pipelines-status dashboard. Its deploy workflow was removed on
  2026-09-30. To delete.
- `chd-ds-satellite-impact-viewer`: stays as it is. Whether it joins the site is its
  owner's decision; joining means the Standard plan and a path.

## To test before any site moves

1. Two apps behind `datascience.unocha.org` at two paths, including the address without
   its trailing slash (`/seas5-skill`).
2. Whether a pull request's preview copy can still be opened once the app accepts
   requests only from our Front Door.
3. Moving one repo from the shared app to an app of its own, with its address unchanged.
4. One deploy of the shared app by the assembly job, with its size check.

## Open questions for the team

- The slug rule: drop the `ds-` prefix (proposed), keep the repo names as they are, or
  group by area (for example `/aa/<country>-<hazard>/`)?
- When a repo gets its own app: a scheduled publish at least weekly, or over 100 MB.
- `staff` and `tracker` as hostname labels.
- Which sites move at all. Old one-off analyses could stay on GitHub Pages; the
  superseded pipeline status page and `ocha-lens` (Pages serves a package's branch there) could
  switch Pages off.

## Every repo today

Snapshot of 2026-11-20 for the 49 public repos in the pages registry; 48 answer at their
root (`ocha-lens` returns 404). After the move, [pages-registry.md](pages-registry.md) is
the record of what is published where.

- **Publish schedule:** a cron workflow in the repo that publishes Pages, or "by another
  job" when the site was deployed nearly every day of the last 30 with no such workflow.
- **Deploys:** every Pages deploy in the last 30 days, including the ones made while a
  site was being built (100+ means at least 100).
- **Size:** the files in the Pages source folder, or the last kept build (compressed,
  marked "build"). Sizes are not measured for 15 repos.

<details>
<summary>All 49 repos: new address, app, publish schedule, size, password pages</summary>

| Repo | New address | App | Publish schedule | Deploys, 30 days | Size | Password pages (registry) |
|---|---|---|---|---|---|---|
| `ds-aa-bfa-drought` | `/aa-bfa-drought/` | `chd-ds-web-shared` |  | 9 | not measured | `hnrp-2027/` |
| `ds-aa-bfa-flooding` | `/aa-bfa-flooding/` | `chd-ds-web-shared` |  | 0 | 0.6 MB |  |
| `ds-aa-caf-flooding` | `/aa-caf-flooding/` | stays on GitHub Pages |  | 0 | 8 MB | whole site |
| `ds-aa-cub-hurricanes` | `/aa-cub-hurricanes/` | `chd-ds-web-shared` |  | 0 | 9 MB |  |
| `ds-aa-drought-indicators` | `/aa-drought-indicators/` | `chd-ds-web-shared` |  | 0 | not measured |  |
| `ds-aa-eth-flooding` | `/aa-eth-flooding/` | `chd-ds-web-aa-eth-flooding` | daily, by another job | 67 | 0.3 MB |  |
| `ds-aa-hti-hurricanes` | `/aa-hti-hurricanes/` | `chd-ds-web-aa-hti-hurricanes` | 4 times a day | 47 | not measured |  |
| `ds-aa-lac-dry-corridor` | `/aa-lac-dry-corridor/` | `chd-ds-web-shared` |  | 0 | 78.9 MB |  |
| `ds-aa-mli-drought` | `/aa-mli-drought/` | stays on GitHub Pages |  | 6 | 0.2 MB (build) | `trigger-review/` |
| `ds-aa-ner-drought` | `/aa-ner-drought/` | `chd-ds-web-shared` |  | 0 | 32.9 MB |  |
| `ds-aa-nga-flooding` | `/aa-nga-flooding/` | `chd-ds-web-aa-nga-flooding` | twice a day | 65 | 34.4 MB (build) |  |
| `ds-aa-npl-flooding` | `/aa-npl-flooding/` | `chd-ds-web-shared` |  | 0 | 3.9 MB |  |
| `ds-aa-som-floods` | `/aa-som-floods/` | `chd-ds-web-aa-som-floods` | daily | 40 | 22.9 MB (build) |  |
| `ds-aa-tcd-drought` | `/aa-tcd-drought/` | `chd-ds-web-shared` |  | 4 | 7.6 MB | `evaluation_villages_2026/`, `w3_resultat_2026/` |
| `ds-aa-tracking` | `/aa-tracking/` | `chd-ds-web-aa-tracking` | daily | 100+ | 8.4 MB | `admin/`, `dev/` |
| `ds-aa-uga-flooding` | `/aa-uga-flooding/` | `chd-ds-web-shared` |  | 0 | not measured | `partner/`, `triggers/` |
| `ds-aa-vut-cyclones` | `/aa-vut-cyclones/` | `chd-ds-web-shared` |  | 1 | 1.6 MB |  |
| `ds-acled-trends` | `/acled-trends/` | stays on GitHub Pages |  | 0 | not measured | whole site |
| `ds-afro-cholera` | `/afro-cholera/` | `chd-ds-web-shared` |  | 0 | 7.2 MB |  |
| `ds-asap-trends` | `/asap-trends/` | `chd-ds-web-shared` |  | 0 | not measured |  |
| `ds-c3s-viz` | `/c3s-viz/` | `chd-ds-web-shared` |  | 0 | under 0.1 MB |  |
| `ds-cerf-supplement` | `/cerf-supplement/` | `chd-ds-web-cerf-supplement` | daily | 63 | under 0.1 MB (build) |  |
| `ds-eri-drought` | `/eri-drought/` | `chd-ds-web-shared` |  | 0 | not measured |  |
| `ds-external-aa-frameworks` | `/external-aa-frameworks/` | stays on GitHub Pages |  | 0 | 2.2 MB | whole site |
| `ds-fewsnet-mirror` | `/fewsnet-mirror/` | `chd-ds-web-fewsnet-mirror` | daily | 31 | 4.9 MB (build) |  |
| `ds-flood-gfm` | `/flood-gfm/` | `chd-ds-web-shared` |  | 1 | 13.4 MB |  |
| `ds-fts` | `/fts/` | `chd-ds-web-shared` |  | 0 | not measured |  |
| `ds-geospatial-impact-estimates` | `/geospatial-impact-estimates/` | `chd-ds-web-geospatial-impact-estimates` | daily | 27 | not measured | `experimental/`, `manuscript/`, `story-v2/`, `story-v3/`, `story/` |
| `ds-geospatial-impact-exposure` | `/geospatial-impact-exposure/` | `chd-ds-web-shared` |  | 0 | not measured |  |
| `ds-google-flood-hub` | `/google-flood-hub/` | `chd-ds-web-google-flood-hub` | daily | 31 | under 0.1 MB (build) |  |
| `ds-heat-exposure` | `/heat-exposure/` | stays on GitHub Pages | daily | 25 | 7.8 MB (build) | `dashboard/` |
| `ds-hnrp-mirror` | `/hnrp-mirror/` | `chd-ds-web-hnrp-mirror` | daily | 31 | 9.1 MB (build) |  |
| `ds-ipc-mirror` | `/ipc-mirror/` | `chd-ds-web-ipc-mirror` | daily | 31 | 6.8 MB (build) |  |
| `ds-knowledge-base` | `/` and `/knowledge-base/` | `chd-ds-web-main` | daily, by another job | 100+ | 3.1 MB (build) | `systems-map/` |
| `ds-longterm-outlook` | `/longterm-outlook/` | stays on GitHub Pages |  | 5 | not measured | `outlook/` |
| `ocha-lens` | none | retire? |  | 0 | 56.5 MB |  |
| `ocha-mailchimp` | `/ocha-mailchimp/` | `chd-ds-web-shared` |  | 0 | under 0.1 MB |  |
| `ds-onegms-public` | `/onegms-public/` | `chd-ds-web-shared` |  | 0 | 0.1 MB |  |
| `pa-aa-fji-storms` | `/pa-aa-fji-storms/` | `chd-ds-web-shared` |  | 0 | 23.5 MB |  |
| `ds-pipelines-status` | none | retire? | daily, by another job | 31 | 0.8 MB |  |
| `ds-precip-intercomparison` | `/precip-intercomparison/` | `chd-ds-web-shared` |  | 2 | not measured |  |
| `ds-raster-stats` | `/raster-stats/` | `chd-ds-web-shared` |  | 0 | 5.8 MB |  |
| `ds-regional-forecasts` | `/regional-forecasts/` | `chd-ds-web-regional-forecasts` |  | 0 | 144.1 MB |  |
| `ds-rosea-thresholds` | `/rosea-thresholds/` | `chd-ds-web-shared` |  | 3 | 0.8 MB |  |
| `ds-seas5-skill` | `/seas5-skill/` | `chd-ds-web-shared` | monthly | 7 | not measured |  |
| `ds-storm-impact-harmonisation` | `/storm-impact-harmonisation/` | `chd-ds-web-shared` |  | 1 | not measured |  |
| `ds-storms-alerts` | `/storms-alerts/` | `chd-ds-web-shared` |  | 3 | 16.1 MB |  |
| `ds-storms-pipeline` | `/storms-pipeline/` | `chd-ds-web-shared` |  | 0 | 1.2 MB |  |
| `ds-teleconnections` | `/teleconnections/` | `chd-ds-web-shared` |  | 38 | not measured |  |

</details>
