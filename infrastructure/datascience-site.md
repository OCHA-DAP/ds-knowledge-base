---
content_type: infrastructure
last_reviewed: "2026-11-20"   # bump when a human verifies the page is still accurate
---

# datascience.unocha.org: the team site's addresses and names

> **Proposed on 2026-11-20 (D126), for the team to review. Nothing is built yet.**
> The team's sites move here from GitHub Pages (`ocha-dap.github.io/<repo>/`) over time.

One Azure Front Door profile holds the `datascience.unocha.org` name and its certificate,
and sends each path to an Azure Static Web App (Standard plan). OCHA's TSS keeps the DNS
records in the `unocha.org` zone. This page sets the addresses and the Azure names.
How each site is built and published stays in
[static-data-apps.md](../methods/static-data-apps.md).

## Addresses

### Public sites: one path per repo

- `datascience.unocha.org/` is the team landing page: the hub the KB already generates.
- `datascience.unocha.org/<slug>/` holds one repo's site. `<slug>` is the repo name
  without its `ds-` prefix. Repos without that prefix keep their name.
- Each repo's products keep their place under it, as on GitHub Pages today:
  `/<slug>/<product>/`. The [landing-page
  convention](../methods/static-data-apps.md#one-repo-one-pages-site--the-landing-page-convention)
  carries over unchanged.

| Today | On the new site |
|---|---|
| `ocha-dap.github.io/ds-seas5-skill/app/` | `datascience.unocha.org/seas5-skill/app/` |
| `ocha-dap.github.io/ds-aa-hti-hurricanes/2026/` | `datascience.unocha.org/aa-hti-hurricanes/2026/` |
| `ocha-dap.github.io/pa-aa-fji-storms/` | `datascience.unocha.org/pa-aa-fji-storms/` |
| `ocha-dap.github.io/ds-knowledge-base/db-erd/` | `datascience.unocha.org/knowledge-base/db-erd/` |

Old links keep working through a redirect page left on each GitHub Pages site. It maps
`ocha-dap.github.io/ds-<x>/<rest>` to `datascience.unocha.org/<x>/<rest>`.

### Signed-in sites: one hostname each (later)

Pages that sign people in wait until Entra ID sign-in is set up for the team. Until then,
the pages that have a password today stay on GitHub Pages as they are (the last column of
the [table below](#every-repo-today)).

Each signed-in site then gets its own hostname under `datascience.unocha.org`. Static Web
Apps and App Service run their built-in sign-in at `/.auth/` on the root of the host, so
one hostname can carry only one signed-in app.

| Hostname | For |
|---|---|
| `staff.datascience.unocha.org/<product>/` | Pages any UN account may open |
| `tracker.datascience.unocha.org` | The AA tracker's development and admin pages |
| `<neutral-name>.datascience.unocha.org` | One per restricted audience (one Entra group) |

Every hostname that has a certificate appears in public certificate logs. Restricted
hostnames therefore get neutral names that say nothing about their content.

## How many Static Web Apps

A Static Web App is deployed as one unit: each deploy replaces everything in it. On the
Standard plan it holds at most 500 MB per environment, 2 GB across its environments and
15,000 files ([Microsoft's quota page](https://learn.microsoft.com/en-us/azure/static-web-apps/quotas)).
Today's sites already measure more than one app holds, and 15 repos publish most days. So:

- **The main app** holds the landing page and the KB's own pages. It also answers any path
  that no route claims, so its 404 page is the site's 404 page.
- **A repo gets its own app** when it publishes most days (25 or more Pages deploys in the
  last 30 days) or its site is over 100 MB. It deploys itself with its own deployment token
  and keeps its own preview environments.
- **Every other repo goes in one shared app.** An assembly job deploys it: each repo uploads
  its built site to blob storage, and the job puts the latest of each together and deploys
  them as one. If the shared app passes about 400 MB, the AA framework sites move to a
  second shared app.

On 2026-11-20 these rules give 17 public apps: the main app, 15 apps of their own and the
shared app. That is 16 if the superseded pipeline status page is retired instead of moved.
The Standard plan's list price is USD 9 a month per app. Front Door sends each path to its
app, so a repo can move between the shared app and an app of its own without its address
changing (to test, below).

The repos that get their own app today:

| Repo | New address | App | Deploys in the last 30 days | Size | Note |
|---|---|---|---|---|---|
| `ds-knowledge-base` | `/` and `/knowledge-base/` | `chd-ds-web-main` | 100+ | 3.1 MB, last build compressed | The team landing page (the hub) at the root; KB pages under /knowledge-base/ |
| `ds-aa-tracking` | `/aa-tracking/` | `chd-ds-web-aa-tracking` | 100+ | 159.9 MB, last build compressed | Open site only; dev/ and admin/ have passwords and stay on GitHub Pages |
| `ds-aa-eth-flooding` | `/aa-eth-flooding/` | `chd-ds-web-aa-eth-flooding` | 67 | 0.3 MB |  |
| `ds-aa-nga-flooding` | `/aa-nga-flooding/` | `chd-ds-web-aa-nga-flooding` | 65 | 34.4 MB, last build compressed |  |
| `ds-cerf-supplement` | `/cerf-supplement/` | `chd-ds-web-cerf-supplement` | 63 | under 0.1 MB, last build compressed |  |
| `ds-aa-hti-hurricanes` | `/aa-hti-hurricanes/` | `chd-ds-web-aa-hti-hurricanes` | 47 | not measured | Seasonal: deploys daily in the hurricane season |
| `ds-aa-som-floods` | `/aa-som-floods/` | `chd-ds-web-aa-som-floods` | 40 | 22.9 MB, last build compressed |  |
| `ds-teleconnections` | `/teleconnections/` | `chd-ds-web-teleconnections` | 38 | not measured |  |
| `ds-fewsnet-mirror` | `/fewsnet-mirror/` | `chd-ds-web-fewsnet-mirror` | 31 | 4.9 MB, last build compressed |  |
| `ds-google-flood-hub` | `/google-flood-hub/` | `chd-ds-web-google-flood-hub` | 31 | under 0.1 MB, last build compressed |  |
| `ds-hnrp-mirror` | `/hnrp-mirror/` | `chd-ds-web-hnrp-mirror` | 31 | 9.1 MB, last build compressed |  |
| `ds-ipc-mirror` | `/ipc-mirror/` | `chd-ds-web-ipc-mirror` | 31 | 6.8 MB, last build compressed |  |
| `ds-pipelines-status` | `/pipelines-status/` | `chd-ds-web-pipelines-status` | 31 | 0.8 MB | Superseded by the pipeline registry: retire rather than move? |
| `ds-geospatial-impact-estimates` | `/geospatial-impact-estimates/` | `chd-ds-web-geospatial-impact-estimates` | 27 | not measured |  |
| `ds-heat-exposure` | `/heat-exposure/` | `chd-ds-web-heat-exposure` | 25 | 7.8 MB, last build compressed |  |
| `ds-regional-forecasts` | `/regional-forecasts/` | `chd-ds-web-regional-forecasts` | 0 | 144.1 MB |  |

Deploy counts come from GitHub's Pages deployments and include development pushes. Sizes
are the files on the Pages branch, or the last build when that is kept (compressed, and
for the AA tracker it includes the `dev/` and `admin/` copies).

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
route that lists all its paths; Front Door Standard allows 100 routes, 100 origin groups
and 100 path patterns per route in a profile.

## The AA tracker

- Its open site moves to `datascience.unocha.org/aa-tracking/`, on its own app
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

1. Two apps behind `datascience.unocha.org` at two paths.
2. Preview environments still open while the app accepts requests only from our Front Door.
3. One deploy of the shared app by the assembly job.

## Open questions for the team

- The slug rule: drop the `ds-` prefix (proposed), keep the repo names as they are, or
  group by area (for example `/aa/<country>-<hazard>/`)?
- The thresholds for an app of its own: 25 deploys in 30 days, 100 MB.
- `staff` and `tracker` as hostname labels.
- Which sites move at all. Old one-off analyses could stay on GitHub Pages.

## Every repo today

Snapshot of 2026-11-20. 49 repos have Pages switched on; 48 answer at their root
(`ocha-lens` returns 404). The last column lists pages that had a password field when
fetched on that day. After the move, [pages-registry.md](pages-registry.md) is the record
of what is published where.

<details>
<summary>All 49 repos: today's address, new address, app</summary>

| Repo | New address | App | Deploys in the last 30 days | Size | Pages with a password today |
|---|---|---|---|---|---|
| `ds-aa-bfa-drought` | `/aa-bfa-drought/` | `chd-ds-web-shared` | 9 | not measured | `hnrp-2027/` |
| `ds-aa-bfa-flooding` | `/aa-bfa-flooding/` | `chd-ds-web-shared` | 0 | 0.6 MB |  |
| `ds-aa-caf-flooding` | `/aa-caf-flooding/` | stays on GitHub Pages | 0 | 8 MB | whole site |
| `ds-aa-cub-hurricanes` | `/aa-cub-hurricanes/` | `chd-ds-web-shared` | 0 | 9 MB |  |
| `ds-aa-drought-indicators` | `/aa-drought-indicators/` | `chd-ds-web-shared` | 0 | not measured |  |
| `ds-aa-eth-flooding` | `/aa-eth-flooding/` | `chd-ds-web-aa-eth-flooding` | 67 | 0.3 MB |  |
| `ds-aa-hti-hurricanes` | `/aa-hti-hurricanes/` | `chd-ds-web-aa-hti-hurricanes` | 47 | not measured |  |
| `ds-aa-lac-dry-corridor` | `/aa-lac-dry-corridor/` | `chd-ds-web-shared` | 0 | 78.9 MB |  |
| `ds-aa-mli-drought` | `/aa-mli-drought/` | `chd-ds-web-shared` | 6 | 0.2 MB, last build compressed | `trigger-review/` |
| `ds-aa-ner-drought` | `/aa-ner-drought/` | `chd-ds-web-shared` | 0 | 32.9 MB |  |
| `ds-aa-nga-flooding` | `/aa-nga-flooding/` | `chd-ds-web-aa-nga-flooding` | 65 | 34.4 MB, last build compressed |  |
| `ds-aa-npl-flooding` | `/aa-npl-flooding/` | `chd-ds-web-shared` | 0 | 3.9 MB |  |
| `ds-aa-som-floods` | `/aa-som-floods/` | `chd-ds-web-aa-som-floods` | 40 | 22.9 MB, last build compressed |  |
| `ds-aa-tcd-drought` | `/aa-tcd-drought/` | `chd-ds-web-shared` | 4 | 7.6 MB | `evaluation_villages_2026/`, `w3_resultat_2026/` |
| `ds-aa-tracking` | `/aa-tracking/` | `chd-ds-web-aa-tracking` | 100+ | 159.9 MB, last build compressed | `admin/`, `dev/` |
| `ds-aa-uga-flooding` | `/aa-uga-flooding/` | `chd-ds-web-shared` | 0 | not measured | `partner/`, `triggers/` |
| `ds-aa-vut-cyclones` | `/aa-vut-cyclones/` | `chd-ds-web-shared` | 1 | 1.6 MB |  |
| `ds-acled-trends` | `/acled-trends/` | stays on GitHub Pages | 0 | not measured | whole site |
| `ds-afro-cholera` | `/afro-cholera/` | `chd-ds-web-shared` | 0 | 7.2 MB |  |
| `ds-asap-trends` | `/asap-trends/` | `chd-ds-web-shared` | 0 | not measured |  |
| `ds-c3s-viz` | `/c3s-viz/` | `chd-ds-web-shared` | 0 | under 0.1 MB |  |
| `ds-cerf-supplement` | `/cerf-supplement/` | `chd-ds-web-cerf-supplement` | 63 | under 0.1 MB, last build compressed |  |
| `ds-eri-drought` | `/eri-drought/` | `chd-ds-web-shared` | 0 | not measured |  |
| `ds-external-aa-frameworks` | `/external-aa-frameworks/` | stays on GitHub Pages | 0 | 2.2 MB | whole site |
| `ds-fewsnet-mirror` | `/fewsnet-mirror/` | `chd-ds-web-fewsnet-mirror` | 31 | 4.9 MB, last build compressed |  |
| `ds-flood-gfm` | `/flood-gfm/` | `chd-ds-web-shared` | 1 | 13.4 MB |  |
| `ds-fts` | `/fts/` | `chd-ds-web-shared` | 0 | not measured |  |
| `ds-geospatial-impact-estimates` | `/geospatial-impact-estimates/` | `chd-ds-web-geospatial-impact-estimates` | 27 | not measured | `experimental/`, `manuscript/`, `story-v2/`, `story-v3/`, `story/` |
| `ds-geospatial-impact-exposure` | `/geospatial-impact-exposure/` | `chd-ds-web-shared` | 0 | not measured |  |
| `ds-google-flood-hub` | `/google-flood-hub/` | `chd-ds-web-google-flood-hub` | 31 | under 0.1 MB, last build compressed |  |
| `ds-heat-exposure` | `/heat-exposure/` | `chd-ds-web-heat-exposure` | 25 | 7.8 MB, last build compressed | `dashboard/` |
| `ds-hnrp-mirror` | `/hnrp-mirror/` | `chd-ds-web-hnrp-mirror` | 31 | 9.1 MB, last build compressed |  |
| `ds-ipc-mirror` | `/ipc-mirror/` | `chd-ds-web-ipc-mirror` | 31 | 6.8 MB, last build compressed |  |
| `ds-knowledge-base` | `/` and `/knowledge-base/` | `chd-ds-web-main` | 100+ | 3.1 MB, last build compressed | `systems-map/` |
| `ds-longterm-outlook` | `/longterm-outlook/` | `chd-ds-web-shared` | 5 | not measured | `outlook/` |
| `ocha-lens` | `/ocha-lens/` | `chd-ds-web-shared` | 0 | 56.5 MB |  |
| `ocha-mailchimp` | `/ocha-mailchimp/` | `chd-ds-web-shared` | 0 | under 0.1 MB |  |
| `ds-onegms-public` | `/onegms-public/` | `chd-ds-web-shared` | 0 | 0.1 MB |  |
| `pa-aa-fji-storms` | `/pa-aa-fji-storms/` | `chd-ds-web-shared` | 0 | 23.5 MB |  |
| `ds-pipelines-status` | `/pipelines-status/` | `chd-ds-web-pipelines-status` | 31 | 0.8 MB |  |
| `ds-precip-intercomparison` | `/precip-intercomparison/` | `chd-ds-web-shared` | 2 | not measured |  |
| `ds-raster-stats` | `/raster-stats/` | `chd-ds-web-shared` | 0 | 5.8 MB |  |
| `ds-regional-forecasts` | `/regional-forecasts/` | `chd-ds-web-regional-forecasts` | 0 | 144.1 MB |  |
| `ds-rosea-thresholds` | `/rosea-thresholds/` | `chd-ds-web-shared` | 3 | 0.8 MB |  |
| `ds-seas5-skill` | `/seas5-skill/` | `chd-ds-web-shared` | 7 | not measured |  |
| `ds-storm-impact-harmonisation` | `/storm-impact-harmonisation/` | `chd-ds-web-shared` | 1 | not measured |  |
| `ds-storms-alerts` | `/storms-alerts/` | `chd-ds-web-shared` | 3 | 16.1 MB |  |
| `ds-storms-pipeline` | `/storms-pipeline/` | `chd-ds-web-shared` | 0 | 1.2 MB |  |
| `ds-teleconnections` | `/teleconnections/` | `chd-ds-web-teleconnections` | 38 | not measured |  |

</details>
