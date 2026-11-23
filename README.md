# Anemone Magazine

An independent literary magazine publishing fiction, nonfiction, poetry, and art by young creators.

## Edit and preview

- Update issue metadata, cover filenames, workshops, and Google form links in `site/magazine.json`.
- Update page copy in `site/pages/`. The submission dates and issue call are in `site/pages/upcoming-issues.html`.
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
