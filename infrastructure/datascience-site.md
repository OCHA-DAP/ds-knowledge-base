---
content_type: infrastructure
last_reviewed: "2026-11-23"   # bump when a human verifies the page is still accurate
---

# datascience.unocha.org: the team site's structure and names

> **Proposed on 2026-11-20 (D126), revised 2026-11-23, for the team to review. Nothing is
> built yet.** Sites stay on GitHub Pages (`ocha-dap.github.io/<repo>/`) by default: it costs
> nothing, and it is fine for most of them. A site would move here only when it needs more
> reliable availability or access than GitHub Pages gives.

One Azure Front Door profile would hold the `datascience.unocha.org` name and its
certificate and send each path to an Azure Static Web App (Standard plan); whether it comes
at the start is an open question (below). OCHA's IT team (TSS) keeps
the DNS records in the `unocha.org` zone. This page proposes what goes on the site, the
addresses and the Azure names. How each site is built stays in
[static-data-apps.md](../methods/static-data-apps.md).

## What goes on the site

In the addresses below, `<name>` is a product name picked by hand, such as a flagship's, and
`<slug>` is the repo name without its `ds-` prefix (repos without the prefix keep their
name).

| Address | What is there | Static Web App |
|---|---|---|
| `datascience.unocha.org/` | The landing page: lists the team's sites wherever they are, the flagships first, then the analyses by topic | `chd-ds-web-main` |
| `datascience.unocha.org/<name>/` | A flagship that moved: one of a few products the team keeps up to date for people outside the team | its own, `chd-ds-web-<name>` |
| `datascience.unocha.org/analyses/` | The list of analyses, by topic, linking out to the ones still on GitHub Pages | `chd-ds-web-main` |
| `datascience.unocha.org/analyses/<slug>/` | An analysis that moved: a repo's site that needs more reliable availability or access | `chd-ds-web-main` (its own app if over 100 MB) |
| `ocha-dap.github.io/<repo>/` | Every other site: the default (below) | none |
| `api.datascience.unocha.org/<name>/…` | MCP servers and APIs, for programs ([below](#programs-mcp-servers-and-apis)) | none (App Service) |

- **Flagships** are chosen by the team, a few at a time. Each gets a short product name
  picked by hand: `ds-aa-tracking` would become `/aa-tracker/`.
- **Analyses** keep their slug: `ds-aa-ner-drought` would become `/analyses/aa-ner-drought/`.
  The topics on the landing page and the list are labels on those pages. The address has
  no topic in it, so an analysis can change topic and keep its address.
- **What stays on GitHub Pages:** every site, until it needs to move. Team tools and
  documentation and work in progress stay in any case, and password pages until sign-in
  exists (below). The landing page and the list link to sites that stay, such as the
  Somalia flood trigger or Haiti's 2026 framework page.
- **An analysis is not republished on a daily or weekly schedule** (monthly is fine). The
  analyses share one app, and every deploy replaces the whole app (next section).
  Proposed: a scheduled site that needs to move gets an app of its own at an `/analyses/`
  address, for USD 9 a month (the applications question below would give it a top-level
  name instead). An analysis that later gains a daily or weekly schedule gets an app of its own and keeps
  its address.
- Each repo's products keep their place under its address, as on GitHub Pages today
  (`/analyses/aa-ner-drought/app/`). The [landing-page
  convention](../methods/static-data-apps.md#one-repo-one-pages-site--the-landing-page-convention)
  carries over unchanged.
- Names must be unique. At the root, `analyses`, `apps`, `api`, `mcp`, the flagship names
  and any folder the landing page uses itself (such as `assets`) are taken. `/api` also
  because a Static Web App sends it to its API backend. A check on the list of what is
  on the site should refuse a product name that takes one, or a duplicate (to add).

Proposed: the knowledge base stays on GitHub Pages. It is the team's working reference and
deploys many times a day. Its hub stays the full index of every team site, and the landing
page links to it; the landing page lists only what the team chooses.

| Today | Where it would go |
|---|---|
| `ocha-dap.github.io/ds-aa-tracking/` | `datascience.unocha.org/aa-tracker/` |
| `ocha-dap.github.io/ds-seas5-skill/app/` | `datascience.unocha.org/seas5-alerts/app/` (as a flagship) |
| `ocha-dap.github.io/ds-aa-ner-drought/app/` | `datascience.unocha.org/analyses/aa-ner-drought/app/` |
| `ocha-dap.github.io/pa-aa-fji-storms/` | `datascience.unocha.org/analyses/pa-aa-fji-storms/` |
| `ocha-dap.github.io/ds-aa-som-floods/` | proposed: `datascience.unocha.org/analyses/aa-som-floods/` on an app of its own, since it is republished daily (see the open questions) |
| `ocha-dap.github.io/ds-knowledge-base/` | stays |

## Which Static Web App serves each part

A Static Web App is deployed as one unit: each deploy replaces everything in it. On the
Standard plan it holds at most 500 MB in its published copy, 2 GB across the published
copy and its pull-request preview copies, and 15,000 files
([Microsoft's quota page](https://learn.microsoft.com/en-us/azure/static-web-apps/quotas)).
So:

- **Each flagship that moves has an app of its own**, published by its own repo's
  workflow on its own schedule. Whether its pull-request preview copies still open behind
  Front Door is to test (below).
- **The main app holds the landing page, the list and every analysis that moves.** An
  assembly job builds it: a workflow that collects the latest files of every analysis that
  moved, adds the landing
  page and the list, and deploys them together. On every run it checks the total size and
  file count, and if one analysis would take the app past the limit it leaves that one at
  its last good copy. Publishing an analysis redeploys the main app, so a burst of pushes
  to one analysis means that many deploys of the main app.
- **An analysis over 100 MB that moves gets an app of its own at the same address.** Front Door
  sends `/analyses/<slug>/` to that app, because a more specific path wins over the main
  app's catch-all route. The same move is open to any analysis later (for example if the
  main app passes about 400 MB), and its address does not change.

Where each analysis's files come from: 13 of the 23 analyses in the first cut are served by
GitHub Pages straight from a folder in a branch, 6 of them from a branch other than `main`;
once one moves, the assembly job copies that folder. The other 10 are built by a workflow,
which gets one more step that uploads the built site to blob storage for the job. Once a
repo moves, its
GitHub Pages serves only the forwarding pages (below), and its content stays where it is.

Front Door passes the path through unchanged, so each app holds its files under its
path: a flagship's app keeps its site in `<name>/`, and the main app keeps the landing
page at its root and each analysis in `analyses/<slug>/`. The main app also answers any
address that belongs to nothing else, with its 404 page. Every app's configuration:

- sets `trailingSlash` to `auto`, so a folder address typed without its last slash
  (`/aa-tracker`) redirects to the slash form, as GitHub Pages does today. Without it the
  page loads at the wrong level and its relative links break. The same setting removes
  `.html` from page addresses with a redirect, which the AA tracker's page-view counter
  must allow for;
- lists `datascience.unocha.org` as an allowed forwarded host, so redirects use the public
  name;
- switches off the built-in sign-in addresses (`/.auth/login/…`) on public apps.

Front Door's caching stays off at first, so a deploy shows at once. If it is turned on
later, each deploy purges its path.

**What it costs.** The Standard plan is priced per app per month
([pricing](https://azure.microsoft.com/en-us/pricing/details/app-service/static/)), at a
list price of USD 9; the app's size only sets the limits above.
So an analysis that moves into the main app adds nothing to the bill, and a site with an
app of its own adds USD 9. Traffic is the other cost: 100 GB a month is included per Azure
subscription, then USD 0.20 per GB, plus Front Door's own traffic charges. Front Door
Standard has a base fee of USD 35 a month.

- With nothing moved, the main app and Front Door: about USD 44 a month.
- With the AA tracker moved: 2 apps, about USD 53.
- If every flagship and analysis in the first cut moved: 6 apps (the main app,
  4 flagships and 1 large analysis), about USD 89.

What a move costs is mostly work: forwarding pages, the services that check an address,
password paths (below), and a deploy of the main app for every update of an analysis.

If every analysis in the first cut moved, the main app's share measures 179 MB in
1,496 files so far, with 10 not measured. If those are like the
measured ones, it would hold about 330 MB, and the active ones are probably larger. Every
site gets measured before it moves.

## Old addresses

Only the repos that move need anything. GitHub Pages can't send a real redirect, so each
old page of a moved repo gets a small page that forwards the reader to its new address,
looked up from the list of what is on the site. Password pages are skipped (next section).

- **The forwarding pages stay for good.** Sent emails (the storm alerts link to
  `ocha-dap.github.io` pages) and endorsed framework documents keep the old addresses.
- **Data files that programs read** (JSON, CSV, `llms.txt`) stay published at the old
  address as well for a transition period: a forwarding page breaks a program that
  expects data. The KB's AA tools read the AA tracker's open files this way; they take
  the tracker's address from one setting (`KB_AA_TRACKER_BASE`). The KB's generators that
  name `ocha-dap.github.io` addresses of moved repos get updated in the same change.
- **Links inside the sites** that use the full `ocha-dap.github.io` address of their own
  site get changed to the new address, so they don't bounce through a forwarding page.
- **Services that check the site's address** need the new one:
  - The AA tracker's page-view counter and its proxy accept only the `ocha-dap.github.io`
    address today; after a move, counts would drop to zero with no error. Its
    `llms.txt` writes the old address unless `SITE_URL` is set.
  - The token issuer's list of allowed callers, and the storage's CORS setting, name the
    regional forecasts site and the geospatial impact estimates flood-labels page
    ([token-issuer.md](token-issuer.md)).
  - GitHub Pages sends `access-control-allow-origin: *` on every file; a Static Web App
    sends it only if its configuration says so. A page on another site that reads a
    moved site's data needs that header set.

## Password pages stay on GitHub Pages for now

Pages that have a password today stay on GitHub Pages until Entra ID sign-in is set up for
the team. Six repos stay whole: three are password sites, and three have nothing open
apart from a landing page. At least six of the first cut's flagships and analyses mix
open and password pages. If one moves:

- Before the repo moves, it lists its password paths in the repo itself. Its deploy (or
  the assembly job, for an analysis) leaves them out of the new site.
- The forwarding pages skip them.
- Moved pages link to them by their full `ocha-dap.github.io` address.

The last column of the [table below](#every-repo-today-and-where-it-would-go) shows the password pages
the pages registry declares or a fetch of each page found. Both miss some, so the repo's
own list is the one that counts.

## Signed-in sites: one hostname each (later)

Once sign-in exists, each signed-in site gets its own hostname under
`datascience.unocha.org`. Static Web Apps and App Service run their built-in sign-in at
`/.auth/` on the root of the host, so one hostname can carry only one signed-in app.
Proposed hostnames:

| Hostname | For |
|---|---|
| `staff.datascience.unocha.org/<product>/` | Pages any UN account may open (sign-in limited to the UN tenant, which needs the Standard plan's own Entra registration) |
| `tracker.datascience.unocha.org` | The AA tracker's development and admin pages |
| `<neutral-name>.datascience.unocha.org` | One per restricted audience (one Entra group) |

Every hostname that has a certificate appears in public certificate logs. Restricted
hostnames therefore get neutral names that say nothing about their content.

A server app that people sign in to in a browser (a chat assistant, an admin screen)
follows the same rule: a hostname of its own.

## Programs: MCP servers and APIs

Proposed: one hostname for public endpoints that programs call,
`api.datascience.unocha.org`, with the product's name first in the path: its name on the
site where it has one (`aa-tracker`), otherwise a short name picked by hand (the KB).

| Address | For |
|---|---|
| `api.datascience.unocha.org/<name>/mcp` | A product's MCP server, such as the AA tracker's (`/aa-tracker/mcp`, experimental today) |
| `api.datascience.unocha.org/<name>/v1/…` | A product's API, with its version in the path |

- **Data files a site publishes stay with the site.** The AA tracker's JSON, CSV and
  `llms.txt` stay with the site (under `/aa-tracker/` if it moves). They are files, not an
  API.
- **These run on App Service.** A Static Web App's own API backend is fixed at `/api` and
  limited to 45 seconds a request, which rules out a streamed MCP server at `/<name>/mcp`.
  Front Door sends `api.datascience.unocha.org` to the App Service app if MCP's streamed
  answers pass through it (test 6 below); if not, the hostname points straight at the app
  and the address stays the same.
- **Why a hostname of its own.** Programs never get the site's HTML 404 page or its slash
  redirects (the site's catch-all route is attached to `datascience.unocha.org` only), and
  the hostname can point at Front Door or straight at the app without changing. A page on
  `datascience.unocha.org` that calls it from the browser needs CORS headers from the app.
- **The address is picked once.** Connectors, scripts and allow-lists hard-code it, and an
  API keeps its old version answering while callers move to a new one.
- **Only public endpoints go here.** An endpoint for UN staff or the team gets a hostname of
  its own, like a signed-in site: sign-in adds addresses at the root of the host
  (`/.well-known/…`), which is simpler on a host of its own.

Today the team's public MCP server (`chd-ds-kb-mcp`) answers at its Azure address, on
`/mcp` for the KB and `/aa-tracker/mcp` for the AA tracker
([mcp-connectors.md](mcp-connectors.md)). If it moves, in this order:

1. A Front Door route and the custom domain's DNS records. The server refuses a host name
   it doesn't know with a 421, so `KB_MCP_ALLOWED_HOSTS` gets the name Front Door sends.
2. The KB's endpoint gets a name: the app answers on both `/mcp` and `/<name>/mcp` while
   callers move.
3. Every caller moves to the new address: connectors, the KB's MCP staleness check, the
   docs ([USING.md](../docs/USING.md)) and the team chatbot.
4. Last, the app accepts requests only from Front Door, and its Azure address stops
   answering.

## Azure names

| Thing | Name |
|---|---|
| Static Web App, main (landing page and analyses) | `chd-ds-web-main` |
| Static Web App, a flagship | `chd-ds-web-<name>` (`chd-ds-web-aa-tracker`) |
| Static Web App, an analysis with its own app | `chd-ds-web-<slug>` (`chd-ds-web-regional-forecasts`) |
| Static Web App, signed-in | `chd-ds-web-<hostname label>` (`chd-ds-web-staff`, `chd-ds-web-tracker`) |
| Front Door profile | `chd-ds-frontdoor` |
| Front Door endpoint (where the DNS record points) | `chd-ds` |
| Front Door origin group (Front Door's name for the app behind a route) | the app's name |
| Front Door route (which paths go to which app) | `route-<name or slug>`; `route-main` for the catch-all route; `route-api-<name>` on `api.` |
| Front Door custom domain | the hostname with hyphens for dots (`datascience-unocha-org`) |
| Tags on every app | `tier` (`public`, `staff` or `restricted`) and `repo` (the repo name, `ds-aa-tracking`) |

`chd-ds-` follows the team's existing Azure names (`chd-ds-demos`, `chd-ds-token-issuer`).
`web` marks the site's apps apart from the App Service apps. An app is named after its
address, and the `repo` tag records the repo that builds it. The main app takes the
catch-all route (`/*`). Each flagship and each analysis with its own app takes one route
with three patterns, for example `/aa-tracker`, `/aa-tracker/` and `/aa-tracker/*`.
Front Door Standard allows 100 routes and 100 origin groups in a profile.

## The AA tracker

- The first candidate to move. Its open site (8.4 MB) would go to
  `datascience.unocha.org/aa-tracker/`, on its own app (`chd-ds-web-aa-tracker`). The build already puts the open site at the top and
  `dev/` and `admin/` below it, so only the top is published there.
- `dev/` and `admin/` stay on GitHub Pages with their passwords until sign-in exists. They
  then move to the proposed `tracker.datascience.unocha.org`. That hostname stays the same
  if the tracker later becomes an App Service app.

## The two Static Web Apps that exist today

- `dsci-monitor`: the old pipelines-status dashboard. Its deploy workflow was removed on
  2026-09-30, so it could be deleted.
- `chd-ds-satellite-impact-viewer`: stays as it is. Whether it joins the site is its
  owner's decision; joining means the Standard plan and an address.

## Before any site moves

The team's Azure role can't create Static Web Apps today
([static-data-apps.md](../methods/static-data-apps.md)). The main app and the Front Door
profile are a request to OCHA's IT team, and so is each later app of its own (a flagship
or an analysis) and each new hostname.

Work in the KB: the pages registry's generator knows only `ocha-dap.github.io`
addresses. It has to learn the new addresses and record a moved repo's old pages as
forwarding pages, and the hub has to link to the new addresses.

To test:

1. A flagship app and the main app behind `datascience.unocha.org`: the flagship's
   address without its last slash (`/aa-tracker`), a nested folder without its last slash
   (`/analyses/aa-ner-drought/app`), and a page ending in `.html`.
2. One analysis on an app of its own at `/analyses/<slug>/` while the main app keeps the
   rest of `/analyses/`, including that analysis's address without its last slash.
3. Whether a pull request's preview copy can still be opened once the app accepts
   requests only from our Front Door.
4. One deploy of the main app by the assembly job, with its size check.
5. A deploy shows at once through Front Door (caching off).
6. An MCP server behind Front Door on `api.datascience.unocha.org`: a streamed answer, a
   tool call that sends nothing for over a minute, and an open stream left idle are not
   cut off.

## Open questions for the team

- **Front Door at the start, or with the first app of its own.** Proposed: at the start,
  so the set-up is one request to OCHA's IT team, the DNS record never changes, and the
  `api.` hostname can use it. Without it, the main app takes `datascience.unocha.org`
  directly with its own certificate, for USD 9 a month, until the first site needs an app
  of its own.
- **What makes a site move, and which go first.** Proposed: a site moves when it needs
  more reliable availability or access than GitHub Pages gives, decided site by site. The
  AA tracker is the first candidate. The first cut guesses three more flagships: the SEAS5
  precipitation alerts, the geospatial impact estimates and the storm alerts sign-up.
  Their names here are placeholders.
- **Scheduled sites that are not flagships**: the AA monitoring sites for Ethiopia,
  Haiti, Nigeria and Somalia, Google Flood Hub, the CERF supplement review and the three
  mirror explorers. They stay on GitHub Pages like the rest, and the landing page or the
  AA tracker links to them. Proposed: one that needs to move gets an app of its own under
  `/analyses/` for USD 9 a month; the next question would give it a top-level name
  instead.
- **Applications and analyses.** Another way to sort: by upkeep, not by whether a site is
  interactive (several analyses have an explorer). Applications are the flagships and the
  sites with a running publish schedule: 13 today, the 4
  flagships and the 9 scheduled sites that have no place in the first
  cut. The analyses have no running schedule. 16 of the 23 had
  no deploy in the last 30 days, and a few are updated by hand: teleconnections (38
  deploys in 30 days as studies are added) and the Burkina Faso and Chad drought sites in
  season. What it would change:
  - The rule and the address change, not the cost. An application that moves has an app
    of its own and an analysis shares the main app (a busy one, such as teleconnections,
    can still get its own): "a running schedule" replaces "monthly is fine" as the line
    between them. An application gets a name at the top level instead of an `/analyses/`
    address. Either way, each site that moves to an app of its own costs USD 9 a month.
  - "Flagship" becomes a label on the landing page instead of a level. Every application
    that moves gets a name at the top level, and the flagships are the ones the landing
    page leads with, so promoting one doesn't change its address. The other way,
    `/apps/<name>/`, keeps the top level for flagships, but a promotion then changes an
    address, and forwarding pages stay for good.
  - The AA framework sites split. Of the 16 AA framework repos, 10 are analyses, 4 are
    republished at least daily in season and would be applications, and 2 stay behind
    passwords. The AA tracker links to all of them either way.

  The first cut below is not re-sorted.
- **The knowledge base**: stays on GitHub Pages with its hub (proposed), or its pages move
  to `/knowledge-base/`.
- **The folder name**: `/analyses/` (proposed) or `/projects/`, since a repo's site often
  mixes reports, apps and monitoring pages.
- **Where the list of what is on the site lives**, with the landing page and the assembly
  job: a small site repo (proposed), so that what goes public is one reviewed change, or
  the KB, next to the pages registry.
- `staff`, `tracker` and `api` as hostname labels.
- The superseded pipeline status page and `ocha-lens` (Pages serves a package's branch
  there) could switch Pages off.

## Every repo today, and where it would go

Snapshot of 2026-11-20 for the 49 public repos in the [pages registry](pages-registry.md);
48 answer at their root (`ocha-lens` returns 404). Seven more team repos have Pages
switched on (five private, two old `pa-` repos); they are not part of this plan yet. As
sites move, [pages-registry.md](pages-registry.md) stays the record of what is published
where.

All of them are on GitHub Pages and stay there by default. The first cut, for the team to
change, sorts them into flagships and analyses, with the address each would get if it
moved, and repos with no place on the new site yet: 4 flagships (3 of them
guesses), 23 analyses, 20 with no place (9
republished on a schedule, 5 team tools and documentation,
6 behind passwords), and 2 that could switch Pages off.

- **Publish schedule:** a cron workflow in the repo that publishes Pages, or "by another
  job" when the site was deployed nearly every day of the last 30 with no such workflow.
- **Deploys:** every Pages deploy in the last 30 days, including the ones made while a
  site was being built (100+ means at least 100).
- **Size:** the files in the Pages source folder, or the last kept build (compressed,
  marked "build"). Sizes are not measured for 15 repos.
- **Password pages:** declared in the pages registry, or found by fetching each page on
  2026-11-20 and looking for a password field.

<details>
<summary>All 49 repos: first cut, address if it moves, app, publish schedule, size, password pages</summary>

| Repo | First cut | Address if it moves | App | Publish schedule | Deploys, 30 days | Size | Password pages | Note |
|---|---|---|---|---|---|---|---|---|
| `ds-aa-tracking` | Flagship | `/aa-tracker/` | `chd-ds-web-aa-tracker` | daily | 100+ | 8.4 MB | `admin/`, `dev/` | Open site only (8.4 MB); dev/ and admin/ have passwords and stay on GitHub Pages |
| `ds-geospatial-impact-estimates` | Flagship (guess) | `/impact-estimates/` | `chd-ds-web-impact-estimates` | daily | 27 | not measured | `brief/`, `experimental/`, `manuscript/`, `story-v2/`, `story-v3/`, `story/` |  |
| `ds-seas5-skill` | Flagship (guess) | `/seas5-alerts/` | `chd-ds-web-seas5-alerts` | monthly | 7 | not measured |  |  |
| `ds-storms-alerts` | Flagship (guess) | `/storm-alerts/` | `chd-ds-web-storm-alerts` |  | 3 | 16.1 MB |  |  |
| `ds-aa-bfa-drought` | Analysis | `/analyses/aa-bfa-drought/` | `chd-ds-web-main` |  | 9 | not measured | `hnrp-2027/` |  |
| `ds-aa-bfa-flooding` | Analysis | `/analyses/aa-bfa-flooding/` | `chd-ds-web-main` |  | 0 | 0.6 MB |  |  |
| `ds-aa-cub-hurricanes` | Analysis | `/analyses/aa-cub-hurricanes/` | `chd-ds-web-main` |  | 0 | 9 MB |  |  |
| `ds-aa-drought-indicators` | Analysis | `/analyses/aa-drought-indicators/` | `chd-ds-web-main` |  | 0 | not measured |  |  |
| `ds-aa-lac-dry-corridor` | Analysis | `/analyses/aa-lac-dry-corridor/` | `chd-ds-web-main` |  | 0 | 78.9 MB | `book/` |  |
| `ds-aa-ner-drought` | Analysis | `/analyses/aa-ner-drought/` | `chd-ds-web-main` |  | 0 | 32.9 MB |  |  |
| `ds-aa-npl-flooding` | Analysis | `/analyses/aa-npl-flooding/` | `chd-ds-web-main` |  | 0 | 3.9 MB |  |  |
| `ds-aa-tcd-drought` | Analysis | `/analyses/aa-tcd-drought/` | `chd-ds-web-main` |  | 4 | 7.6 MB | `evaluation_villages_2026/`, `w3_resultat_2026/` |  |
| `ds-aa-uga-flooding` | Analysis | `/analyses/aa-uga-flooding/` | `chd-ds-web-main` |  | 0 | not measured | `partner/`, `triggers/` |  |
| `ds-aa-vut-cyclones` | Analysis | `/analyses/aa-vut-cyclones/` | `chd-ds-web-main` |  | 1 | 1.6 MB |  |  |
| `ds-afro-cholera` | Analysis | `/analyses/afro-cholera/` | `chd-ds-web-main` |  | 0 | 7.2 MB |  | Its daily workflow is switched off (GitHub disabled it for inactivity); turned back on, it needs an app of its own |
| `ds-asap-trends` | Analysis | `/analyses/asap-trends/` | `chd-ds-web-main` | monthly | 0 | not measured |  | Its monthly workflow is switched off (GitHub disabled it for inactivity) |
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
| `ds-teleconnections` | Analysis | `/analyses/teleconnections/` | `chd-ds-web-main` |  | 38 | not measured |  | 38 of the analyses' 56 deploys in 30 days; each would redeploy the main app. Could have an app of its own |
| `ds-aa-caf-flooding` | No place in the first cut |  |  |  | 0 | 8 MB | whole site | Password site |
| `ds-aa-eth-flooding` | No place in the first cut |  |  | daily, by another job | 67 | 0.3 MB |  | Republished on a schedule, not a flagship |
| `ds-aa-hti-hurricanes` | No place in the first cut |  |  | 4 times a day | 47 | not measured |  | Republished on a schedule, not a flagship |
| `ds-aa-mli-drought` | No place in the first cut |  |  |  | 6 | 0.2 MB (build) | `trigger-review/` | Only its landing page is open |
| `ds-aa-nga-flooding` | No place in the first cut |  |  | twice a day | 65 | 34.4 MB (build) |  | Republished on a schedule, not a flagship |
| `ds-aa-som-floods` | No place in the first cut |  |  | daily | 40 | 22.9 MB (build) |  | Republished on a schedule, not a flagship |
| `ds-acled-trends` | No place in the first cut |  |  |  | 0 | not measured | whole site | Password site |
| `ds-cerf-supplement` | No place in the first cut |  |  | daily | 63 | under 0.1 MB (build) |  | Republished on a schedule, not a flagship |
| `ds-external-aa-frameworks` | No place in the first cut |  |  |  | 0 | 2.2 MB | whole site | Password site |
| `ds-fewsnet-mirror` | No place in the first cut |  |  | daily | 31 | 4.9 MB (build) |  | Republished on a schedule, not a flagship |
| `ds-google-flood-hub` | No place in the first cut |  |  | daily | 31 | under 0.1 MB (build) |  | Republished on a schedule, not a flagship |
| `ds-heat-exposure` | No place in the first cut |  |  | daily | 25 | 7.8 MB (build) | `dashboard/` | Only its landing page is open |
| `ds-hnrp-mirror` | No place in the first cut |  |  | daily | 31 | 9.1 MB (build) |  | Republished on a schedule, not a flagship |
| `ds-ipc-mirror` | No place in the first cut |  |  | daily | 31 | 6.8 MB (build) |  | Republished on a schedule, not a flagship |
| `ds-knowledge-base` | No place in the first cut |  |  | daily, by another job | 100+ | 3.1 MB (build) | `systems-map/` | The team's working reference; the landing page links to it |
| `ds-longterm-outlook` | No place in the first cut |  |  |  | 5 | not measured | `outlook/` | Only its landing page is open |
| `ocha-mailchimp` | No place in the first cut |  |  |  | 0 | under 0.1 MB |  | Library documentation |
| `ds-raster-stats` | No place in the first cut |  |  |  | 0 | 5.8 MB |  | Pipeline documentation |
| `ds-rosea-thresholds` | No place in the first cut |  |  |  | 3 | 0.8 MB |  | Internal tool under development |
| `ds-storms-pipeline` | No place in the first cut |  |  |  | 0 | 1.2 MB |  | The pipeline's own dashboard |
| `ocha-lens` | Switch Pages off? |  |  |  | 0 | 56.5 MB |  | Pages serves a Python package's branch root; no page at its root. Switch Pages off? |
| `ds-pipelines-status` | Switch Pages off? |  |  | daily, by another job | 31 | 0.8 MB |  | Superseded by the pipeline registry: switch Pages off? |

</details>
