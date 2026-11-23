# Anemone Magazine

An independent literary magazine publishing fiction, nonfiction, poetry, and art by young creators.

## Edit and preview

- Update issue metadata, cover filenames, workshops, and Google form links in `site/magazine.json`.
- Keep general and themed issues in newest-to-oldest order within each series in `site/magazine.json`. End each published issue’s date with its four-digit year to include it in the corresponding archive filter. Issue pages use the series order for their newer and older links.
- Update page copy in `site/pages/`. Update calls and dates in `site/submission-calendar.json` and record the edit date in `updated`. Use `YYYY-MM-DD` for published dates and omit dates that are still to be announced. The build generates the calendar download and the homepage deadline from that same file.
- Edit the downloadable Word manuscript template in `docs/assets/downloads/anemone-manuscript-template.docx` when the submission formatting guidelines change.
- Keep site assets in `docs/assets/`. Issue covers belong in `docs/assets/covers/`.
- Run the following with Python 3.9 or later. Commit both the source edits and regenerated files in `docs/`.

```sh
python3 scripts/build_site.py
python3 scripts/check_links.py
python3 -m http.server 8000 --bind 127.0.0.1 --directory docs
```

Visit `http://127.0.0.1:8000/` to preview.

GitHub runs the internal link checker and checks that the generated pages match their source on each push and pull request.

## Update the Reach page

- Update `site/reach.json` with public, aggregate country codes such as `AU`, `GB`, and `US`, then rebuild the site. The map highlights each listed country once.
- The initial contributor countries come from locations people shared in their bios in Issues 2, 4, 5, and 6. Update the contributor note if you change the source or scope.
- The Readers map uses the country locations from the `Visits by Location` worksheet. The source workbook is saved locally as `data/Location_Visits.xlsx`. The public site displays the country list from `site/reach.json`.
- For future updates, use **Analytics → Traffic → Geography** in Squarespace. Record the report date range in the reader note when it’s available. These locations are estimates based on site visits.
- The bundled map uses [Natural Earth 1:50m map units, version 5.1.2](https://github.com/nvkelso/natural-earth-vector/blob/v5.1.2/geojson/ne_50m_admin_0_map_units.geojson). If the map data needs updating, download the GeoJSON and run `python3 scripts/make_world_map.py path/to/map-units.geojson`, then rebuild the site.

## Publish to GitHub Pages

1. Open the repository’s [Pages settings](https://github.com/audrikaoc/anemonemagazine/settings/pages). Under **Build and deployment**, choose **Deploy from a branch**, **main**, and **/docs**. Save and wait for `https://audrikaoc.github.io/anemonemagazine/` to serve the site. Future pushes to `main` will publish the updated `docs/` directory.
2. [Verify ownership with GitHub](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages), then enter `www.anemonemagazine.com` as the Pages custom domain. GitHub will add `docs/CNAME` to the publishing branch. Pull that commit before editing again.
3. At the DNS provider, replace the `www` CNAME for Squarespace with `audrikaoc.github.io`. To redirect the apex domain to `www`, replace the Squarespace apex A records with the four [GitHub Pages A records](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site#configuring-an-apex-domain). Preserve email and verification records.
4. Once the DNS check passes, enable **Enforce HTTPS**. Check the homepage, issue archive, an old issue URL, and both forms of the domain. Keep the Squarespace site active until the new domain is confirmed.

## Migration notes

- The 12 existing Canva readers and published covers are linked from individual issue pages. Issue 1 retains its contributor credits and table of contents. It and the July 2026 Pride issue need source files or fresh reading links from the editors.
- The Issue 11 submission and staff application forms request Google sign-in. Workshop registration and mentor application use the original Google Forms, and the workshop menu uses the original Google Doc.
- The homepage newsletter button links directly to the existing form on the magazine’s built-in Squarespace domain. It depends on that form staying online. Before retiring Squarespace, replace `newsletter_signup` in `site/magazine.json` with the public signup URL for the new mailing list and regenerate the site.
- The homepage flower image in `docs/assets/images/anemones-daylight.jpg` is an AI-edited version of the original image generated for the redesign. Issue covers are from the magazine’s public Canva readers. Font licenses are in `docs/assets/fonts/`.

### Homepage artwork

Prompt used with the built-in image generator

> Edit the attached homepage photograph for Anemone, an independent literary magazine. Keep its landscape crop, real anemone flowers with dark button centers, the strong main blossom just right of center, and the tactile fine-art film photography. Reimagine the light and color as a luminous spring morning outdoors. Lift the deep shadows substantially, replace the nearly black background with soft, fresh sage and light green out-of-focus foliage with round natural bokeh, and make the main petals luminous lavender with warm cream highlights. Give the red blossoms a lively coral-pink color and add one or two soft ivory anemones toward the left to balance the crop. Keep natural petal detail, attractive and deliberate asymmetry, soft clear daylight, and lively but natural color. A generous margin around the main bloom should keep it complete in a square or portrait crop. Photorealistic and polished, no text, logos, frames, people, artificial glitter, or watermarks.

### Anemone artwork series

The built-in image generator created these pieces. Set page artwork in `page_artwork` and issue artwork in each issue’s `artwork` field in `site/magazine.json`.

- [anemone-pressed.jpg](docs/assets/images/anemone-pressed.jpg)

  > A 3:2 landscape artwork for the issue archive of a contemporary teen literary magazine. Overhead photographic still life of four authentic pressed anemone coronaria flowers and their delicate stems on warm ivory handmade cotton paper, arranged as an artfully uneven, fan-like herbarium composition. Deep wine, washed violet, pale apricot and creamy white petals with naturally dark anemone centers, softly directional sunlight and subtle paper shadows. Tactile botanical archive with refined art-book styling. The flowers span the horizontal middle of the frame and the main blooms are comfortably away from the edges. No labels, lettering, lines of text, frames, hands, books, or watermarks.

- [anemone-linocut.jpg](docs/assets/images/anemone-linocut.jpg)

  > Wide 3:2 landscape artwork for a contemporary teen literary magazine’s submissions page. An exuberant original hand-printed linocut of three real anemone coronaria blooms, with deep ink-blue centers, overlapping coral and magenta petals, a restrained lavender accent, and loose dark olive stems on soft ivory uncoated paper. Playful gestural composition with bold but imperfect marks, artisanal ink texture and visible carved linework. Keep the most expressive blooms across the horizontal middle so the artwork can be gently cropped. Refined literary-journal illustration. No text, lettering, logos, frame, or watermark.

- [anemone-dawn.jpg](docs/assets/images/anemone-dawn.jpg)

  > Wide 3:2 landscape art photograph for a young writers’ literary magazine. Two rising anemone coronaria buds and one newly opening pale peach and warm cherry bloom against an apricot dawn sky and gauzy meadow tones. Curving green stems, soft golden directional light illuminating translucent petals, a gently grainy 35mm texture and lively negative space around the plant. Place the flowers mainly across the horizontal middle with an asymmetrical diagonal movement, safe for a wide crop. Artistic, real botanical detail, modest warm color. No text, logos, frame, or watermark.

- [anemone-watercolor.jpg](docs/assets/images/anemone-watercolor.jpg)

  > Wide 3:2 landscape illustration for a teen literary magazine's writing workshops page. An anemone flower study on textured warm white sketchbook paper made with loose periwinkle and ultramarine watercolor, ultrafine graphite contours, and restrained soft sage leaves. Three accurate dark-centered anemone blossoms at different stages of sketching, with pooled watery edges and overlapping pencil gestures. Compose the blooms across the middle, with tasteful blank paper around them, no visible binding or edges of the sketchbook. An intimate image of work in progress. No writing, lettering, labels, logos, or watermarks.

- [anemone-portraits.jpg](docs/assets/images/anemone-portraits.jpg)

  > Wide 3:2 landscape editorial still-life photograph for the masthead of an independent young writers’ magazine. A close group of five live anemone coronaria faces of plum, lavender, pink, and ivory, each characterfully different, arranged loosely together across the center at different heights. Paper backdrop in dusty antique rose, cheerful soft window light, gentle cast shadows, finely detailed dark button centers and crinkled petal texture. Contemporary editorial portrait of a group of flowers, fresh and independent-minded. No vase, text, labels, people, borders, or watermarks.

- [anemone-sky.jpg](docs/assets/images/anemone-sky.jpg)

  > Wide 3:2 landscape photograph for the world reach page of a contemporary literary magazine. A little meadow of white Japanese anemones and one blush-pink bloom seen from below against a clear powder-blue sky, loose leaves and curving stems, soft haze and distinctly dark anemone centers. High-key afternoon light with subtle fine film grain, airy composition, cyan and soft green color, visually gentle enough to sit next to a world map elsewhere on the page. Keep a few distinct flower heads across the horizontal center. No globe, geography, lettering, border, watermark, or people.

- [anemone-cyanotype.jpg](docs/assets/images/anemone-cyanotype.jpg)

  > Wide 3:2 landscape original botanical cyanotype from a contemporary literary magazine art series. Two delicate true anemone blooms with stems and fine leaves laid on slightly uneven Prussian-blue sensitized paper. Luminous off-white silhouettes against rich indigo, organic photographic emulsion texture and a few softer ghosted petals, composed diagonally across the middle. Fresh and textural, finely resolved flower outlines, no photographic objects other than the flowers and stems. Edge-to-edge print without frame or border. No names, lettering, logos, signs, or watermarks.

- [anemone-engraving.jpg](docs/assets/images/anemone-engraving.jpg)

  > Wide 3:2 landscape botanical engraving for a quiet page in a literary magazine. A single pale sage-green and muted gold anemone coronaria with visible dark seed center, a small bud, and lacy leaves engraved on warm cream textured paper. Archival copperplate fine hatching and restrained olive color wash with a few crisp fine stems, arranged horizontally and centered with quiet surrounding white space so it crops easily. Serene, honest, understated book-arts aesthetic. No labels, lettering, diagram lines, border, seals, logos, or watermarks.
