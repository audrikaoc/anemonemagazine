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

## Publish to GitHub Pages

1. Open the repository’s [Pages settings](https://github.com/audrikaoc/anemonemagazine/settings/pages). Under **Build and deployment**, choose **Deploy from a branch**, **main**, and **/docs**. Save and wait for `https://audrikaoc.github.io/anemonemagazine/` to serve the site. Future pushes to `main` will publish the updated `docs/` directory.
2. [Verify ownership with GitHub](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages), then enter `www.anemonemagazine.com` as the Pages custom domain. GitHub will add `docs/CNAME` to the publishing branch. Pull that commit before editing again.
3. At the DNS provider, replace the `www` CNAME for Squarespace with `audrikaoc.github.io`. To redirect the apex domain to `www`, replace the Squarespace apex A records with the four [GitHub Pages A records](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site#configuring-an-apex-domain). Preserve email and verification records.
4. Once the DNS check passes, enable **Enforce HTTPS**. Check the homepage, issue archive, an old issue URL, and both forms of the domain. Keep the Squarespace site active until the new domain is confirmed.

## Migration notes

- The 12 existing Canva readers and published covers are linked from individual issue pages. Issue 1 retains its contributor credits and table of contents. It and the July 2026 Pride issue need source files or fresh reading links from the editors.
- The Issue 11 submission and staff application forms request Google sign-in. Workshop registration and mentor application use the original Google Forms, and the workshop menu uses the original Google Doc.
- Newsletter sign-up previously ran through Squarespace. It can be added to this site once the magazine has a hosted signup form and has migrated its subscriber list.
- The homepage flower image in `docs/assets/images/anemones.jpg` is an original image generated for the redesign. Issue covers are from the magazine’s public Canva readers. Font licenses are in `docs/assets/fonts/`.

### Homepage artwork

Prompt used with the built-in image generator

> Landscape 3:2 botanical editorial photograph for the homepage of a literary magazine for young writers. A small arrangement of real anemone coronaria flowers, dominant pale violet/lilac blooms with nearly black centers and a few deep crimson blooms and winding stems, emerging from a shadowy deep olive forest-green background. A dominant large pale flower just right of center, with smaller blossoms scattered asymmetrically. Look like an experimental 35mm film photograph, directional natural light grazing the delicate petals, tactile light analogue grain, art-book polish, dramatic contrast and natural botany. Fill the frame tastefully for a responsive crop; a deep dark left and outer edges. No lettering, border, graphics, vases or watermark.
