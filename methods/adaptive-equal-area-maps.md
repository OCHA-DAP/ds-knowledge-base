---
content_type: method
last_reviewed: "2026-11-09"   # bump when a human verifies the page is still accurate
---

# Adaptive equal-area web maps (proposal)

> **Status: proposal, not adopted.** Proposed as the team's default way to show global and
> regional thematic data on the web. One reference implementation so far:
> the ENSO season map, live since 2026-11-09 at
> <https://ocha-dap.github.io/ds-teleconnections/enso-map/> (code in `ds-teleconnections`,
> [pipelines/teleconnections.md](../pipelines/teleconnections.md)).

## In short

An interactive map that is **equal-area at every scale you normally look at**, turns like a globe,
and looks like a normal map when you zoom in:

- **Whole world in view: Equal Earth.** The equal-area world projection the UN General Assembly
  encouraged in September 2026. Africa, South America and South Asia appear at their true size
  relative to Europe and North America.
- **Dragging turns the globe.** The projection's central meridian follows the middle of the view, so
  any place, including the Pacific across 180°, can be brought to the centre in one piece.
- **Zooming in changes the projection gradually** to a Lambert azimuthal equal-area projection
  centred on the middle of the view. The area you look at keeps its true shape, with north up,
  wherever on the globe it is.
- **Zooming out stops at the whole world.**

Try it (each link opens the live map at that view):

| View | Link |
|---|---|
| Whole world (Equal Earth) | [world](https://ocha-dap.github.io/ds-teleconnections/enso-map/#s=OND&c=classes) |
| Mid zoom, the projection part-way between the two | [Indian Ocean and Asia](https://ocha-dap.github.io/ds-teleconnections/enso-map/#s=OND&c=classes&m=3.3/15/100) |
| Across 180°, in one piece | [Fiji, Vanuatu, Samoa](https://ocha-dap.github.io/ds-teleconnections/enso-map/#s=NDJ&c=classes&m=5.25/-16.5/178.5) |
| High latitude, true shape | [Scandinavia](https://ocha-dap.github.io/ds-teleconnections/enso-map/#s=OND&c=classes&m=5.5/62/15) |

## Why

**Area matters in humanitarian maps.** We map how large an area is affected, where a hazard
covers more ground, and how regions compare. Web Mercator, the projection of almost every web
map, inflates area with latitude: Greenland looks the size of Africa, which is 14 times larger.
An equal-area projection removes that bias from every comparison a reader makes by eye.

**The UN position.** On 4 September 2026 the UN General Assembly adopted a resolution (164 in
favour, 1 against, 6 abstentions) encouraging wider use of equal-area projections, in particular
Equal Earth. It was led by Togo for the African Union. It is not binding and does not ban Mercator.
Using it aligns our public products with that position.

**Static Equal Earth is not enough for an interactive map.** The first version of the reference
map used a fixed Equal Earth projection in Leaflet. It was correct when zoomed out, but zoomed in
near the edges of the world the meridians slanted, high latitudes were stretched east–west
(about 1.3 times at 60°N, 1.7 times out of shape), and countries across 180° (Fiji, Kiribati) were
split between the two edges. The adaptive projection keeps the zoomed-out view and fixes those
three things.

### The options compared

| Option | Equal-area | Pan across 180° | Shapes when zoomed in | Basemap tiles available |
|---|---|---|---|---|
| Web Mercator (Leaflet, MapLibre, most web maps) | no (area grows with latitude) | yes (world copies) | true (conformal) | yes (OSM, Esri, …) |
| Fixed Equal Earth (Leaflet + custom CRS) | yes | no (split at the edges) | slanted and stretched away from the centre | no |
| MapLibre globe | no (a perspective globe, then Mercator) | yes | true | yes |
| **Adaptive equal-area (this page)** | **yes when zoomed out and zoomed in; close in between** | **yes (the globe turns)** | **true at the centre, north up** | **no (own basemap)** |

## How it works

**Two projections and a blend.** The map position of a place is a weighted mix of its position in
two projections, both centred on the middle of the view:

1. **Equal Earth** (Šavrič, Patterson and Jenny 2019) with its central meridian on the view centre.
   It is a pseudocylindrical projection: parallels are straight, the poles are flat lines, and the
   world has a fixed oval outline whatever the rotation.
2. **Lambert azimuthal equal-area** (Snyder 1987) centred on the view centre (an oblique aspect when
   the centre is off the equator). It is equal-area everywhere and free of distortion at its
   centre.

The weight *t* of the azimuthal part grows as you zoom in. It depends on the share of the world's
width that is in view: 0 (pure Equal Earth) while more than 55% of the world is in view, 1 (pure
azimuthal) once less than 15% is, with a smooth step between. On tall screens (phones) the blend
also waits until the poles have left the frame. This follows Jenny's *adaptive composite map
projections* (2012), which change the projection with the scale of the map.

**Constraints that make it behave.**

- **Zoom out stops at the whole world** fitting the frame.
- **The view centre's latitude is limited at low and mid zoom** so that Equal Earth's pole line
  stays at or beyond the edge of the frame. Without this, Equal Earth's seam at the back of the
  globe opens into a blank gap over the pole while the blend is in progress. In practice: the whole
  world is centred on the equator, and high latitudes can be centred once zoomed in (70°N from
  about zoom 6).
- **The far side of the globe is never drawn** while the azimuthal part is in use (it is singular
  at the point opposite the centre). The blend schedule ensures the far side is out of view by then.

**How equal-area is it?** Both ends are exactly equal-area. In between, the blend is not exactly
equal-area: near the middle of the view areas are within about 1%, but towards the corners at mid
zoom they can be off by up to about a third, most at high latitudes (measured: area scale 0.61 in
the top corners of a 1400×700 frame at zoom 3.7 centred on 38.5°N). Pages using this should say
so; the reference map does, in its methods text.

## Building one: what matters

The reference implementation is about 1,000 lines of plain JavaScript and WebGL 2 in one page, with
no map library. The code-level detail lives with the code (the `ds-teleconnections` README, section
"ENSO season map"). These are the design rules that made it work. Each was learnt the hard way,
mostly through two independent code reviews.

- **One projection function.** Everything goes through the same JavaScript projection: hover,
  zoom-around-the-cursor, dragging, labels, borders, fitting a country. The GPU shader is a
  line-for-line port of it, tested against it numerically. The inverse (screen point to place) is
  exact at either end and solved numerically (Newton's method) in between.
- **Cells as GPU quads.** Each data cell (0.25°, 264,000 land cells in the reference map) is one
  instanced quad whose corners the shader projects. Corners are computed from exact degree values
  so that neighbouring cells share bit-identical edges (no hairline cracks).
- **The seam is handled per shape, not per vertex.** Each cell or line segment carries its own
  reference point. A corner that falls across the seam at the back of the globe is cut at the edge
  on its reference's side; otherwise a cell straddling the seam is drawn stretched across the whole
  map.
- **No web tiles, so the basemap is drawn by the page.** Web Mercator tiles (OSM, Esri, CARTO) cannot
  be used. Ocean, land, a graticule, country borders and names are drawn from Natural Earth data.
  Long straight edges in the source data must be densified so they follow the curved meridians.
  Natural Earth's cuts along 180° must not be stroked, or they show as false borders once the globe
  turns.
- **Dragging must not jump.** Keeping the grabbed place under the pointer is an iterative fit.
  Accept a step only if it brings the place closer. Where the map cannot follow (the latitude limit,
  the world's edge), take whatever is now under the pointer as the grabbed place, so no error builds
  up to be released later as a jump.
- **Fit a country by its projected outline,** at the centre the latitude limit will actually allow.
  Fitting by two corners of the latitude–longitude box misjudges it when meridians curve.
- **Performance.** On a laptop a frame (264,000 cells, 90,000 border vertices, 1,500 labels) takes
  1–5 ms. Border vertices carry precomputed trigonometry, so each frame costs only multiplications.
- **Requirements.** WebGL 2 (every current browser) and, for the gzip data files of the reference
  map, `DecompressionStream`. The page shows a plain message when either is missing.

**Checks worth repeating for any new implementation** (all run on the reference map):

- projection round trips (screen → place → screen) agree to within 1e-8 px at every blend weight;
- the shader port agrees with the JavaScript to 1e-10 px, including centres at 180° and zoom 8;
- shared cell edges are identical, and no shape smears across the seam;
- zoom-to-country keeps the whole country in frame for all 241 countries, on a desktop and a phone-sized frame;
- 38,000 simulated drags give no reversals or jumps;
- no pole fold or blank gap on tall frames.

These checks were run as throwaway scripts during review and are not yet in a repository (see
the next steps).

## Limits and open questions before adopting it

- **Boundaries.** The reference map draws Natural Earth 1:50m boundaries and carries the standard UN
  disclaimer. The team convention ([disputed-territories-mapping.md](disputed-territories-mapping.md))
  is UN Geoportal boundaries following OCHA's brand guidance on disputed territories. A standard
  version should switch to those.
- **Not for street-level maps.** There are no tiles, roads or settlements. This suits thematic maps
  from country to world scale (gridded data, admin-level choropleths, points). Maps that need a
  detailed basemap should stay on Web Mercator tiles.
- **Custom code to maintain.** Leaflet or MapLibre come with years of fixes; this comes with one
  reference page. Before others can use it, it should become a small shared module with its tests.
- **The blend is not exactly equal-area** at mid zoom (see above). Exact alternatives exist (an
  oblique Equal Earth, or switching projection without blending), but they look worse while zooming.
- **Not yet checked:** touch gestures on real phones (implemented, tested only in code) and
  keyboard panning (not implemented; the season controls are keyboard-accessible).
- **Static figures.** For PNG figures in reports and slides the matching convention would simply
  be Equal Earth (Cartopy `ccrs.EqualEarth()`, D3 `geoEqualEarth`). No blending is needed for a
  fixed view.

## If adopted: next steps

1. Extract the projection, renderer and interaction code from the reference page into a shared
   JavaScript module, with the checks above as its tests.
2. Switch its boundaries to the UN Geoportal layer per the disputed-territories convention.
3. Point the `pages-site` skill and [static-data-apps.md](static-data-apps.md) to it as the default
   for global and regional thematic maps, and to Equal Earth for static figures.
4. Record the decision in `docs/DESIGN.md`.

## References

- Šavrič, B., Patterson, T. and Jenny, B. (2019). The Equal Earth map projection. *International
  Journal of Geographical Information Science* 33(3), 454–465.
  <https://doi.org/10.1080/13658816.2018.1504949>
- Jenny, B. (2012). Adaptive composite map projections. *IEEE Transactions on Visualization and
  Computer Graphics* 18(12), 2575–2582. <https://doi.org/10.1109/TVCG.2012.192>
- Snyder, J. P. (1987). *Map Projections: A Working Manual.* US Geological Survey Professional
  Paper 1395. <https://doi.org/10.3133/pp1395>
- UN General Assembly vote of 4 September 2026 encouraging equal-area projections, in particular
  Equal Earth (non-binding; 164–1–6), as reported by
  [Engineering News](https://engineeringnews.co.za/article/the-un-general-assembly-endorses-use-of-relative-size-more-accurate-map-projection-2026-09-07).
