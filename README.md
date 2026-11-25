# Anemone Magazine

An independent literary magazine publishing fiction, nonfiction, poetry, and art by young creators.

## Edit and preview

- Update issue metadata, cover filenames, workshops, and Google form links in `site/magazine.json`.
- Keep general and themed issues in newest-to-oldest order within each series in `site/magazine.json`. End each published issue’s date with its four-digit year to include it in the corresponding archive filter. Issue pages use the series order for their newer and older links.
- Update page copy in `site/pages/`. Update calls and dates in `site/submission-calendar.json` and record the edit date in `updated`. Use `YYYY-MM-DD` for published dates and omit dates that are still to be announced. The build generates the calendar download and the homepage deadline from that same file.
- Edit the downloadable Word manuscript template in `docs/assets/downloads/anemone-manuscript-template.docx` when the submission formatting guidelines change.
- Update `site/editors-picks.json` to change the selections. Use the contributor’s published byline, issue slug, reader page number, and public reading link. Set `spotlight_pick` in `site/magazine.json` to the slug of the pick you want to feature below the homepage hero. Up to three other picks appear below the mission statement.
- Regenerate the downloadable Editor’s Picks graphics after changing a title, byline, or selection. Run `python3 scripts/make_share_graphics.py --browser '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'`, then rebuild the site. The resulting PNGs in `docs/assets/share/` also power the link previews.
- Edit guide text in `site/resources/`. Set each guide’s title, summary, topic, and artwork in `site/writing-resources.json`.
- Keep site assets in `docs/assets/`. Issue covers belong in `docs/assets/covers/`.
- Run the following with Python 3.9 or later. Commit both the source edits and regenerated files in `docs/`.

```sh
python3 scripts/build_site.py
python3 scripts/check_links.py
python3 scripts/preview_site.py
```

Visit `http://127.0.0.1:8017/` to preview. The local server serves fresh files on each reload.

GitHub runs the internal link checker and checks that the generated pages match their source on each push and pull request.

## Google Analytics

- Set `analytics_measurement_id` in `site/magazine.json` to the Anemone GA4 web stream Measurement ID, then rebuild the site. [Find your Measurement ID](https://support.google.com/analytics/answer/12270356)
- The tag measures views automatically on published magazine pages. The local preview stays out of the reports.
- After deployment, open the site and confirm the page view in the GA4 **Realtime** report. [Realtime report guide](https://support.google.com/analytics/answer/9271392)

| Event | When it fires |
| --- | --- |
| `issue_open` | A reader opens an issue page on Anemone. Includes `issue_slug`. |
| `submission_form_click` | A reader follows an issue submission form link from the calendar. Includes `submission_call`. |
| `newsletter_signup_request` | The browser completes the newsletter form request. Google Forms records subscriptions separately. |

In **Realtime**, use **Event count by Event name** to check the events. To break counts down by edition or call, add `issue_slug` and `submission_call` as event-scoped custom dimensions. These events use public issue and call IDs. Newsletter email addresses and form answers stay out of the event data. [GA4 custom dimensions](https://support.google.com/analytics/answer/14240153)

## Connect the newsletter signup

- Publish a Google Form with one required short-answer email question and set its response validation to email format. Give anyone with the link responder access. Keep **Collect email addresses**, **Limit to 1 response**, and **View results summary** off. [Google Forms publishing guide](https://support.google.com/docs/answer/2839588)
- Use **Pre-fill form** with `sample@example.com` to find the question name in the link, such as `entry.123456789`. Set `newsletter_google_form` in `site/magazine.json` to an object with `url` set to the full public `/viewform` URL and `email_field` set to the question name.
- The homepage shows an inline message when it sends the signup request. Google Forms returns an opaque response to the site, so use the form’s **Responses** tab to confirm that a test signup was recorded. [Google Forms response guide](https://support.google.com/docs/answer/139706)

### Activate newsletter email delivery

1. Sign in to the Google account that should send Anemone’s newsletter. In [Google Forms](https://docs.google.com/forms/), open **newsletter-email-submission**, the form with the question **Provide subscriber email address**. From its **More (⋮)** menu, open **Apps Script**.
2. Copy [the newsletter script](newsletter/Code.gs) into a script file in that project. Save it, select **setupNewsletter**, and click **Run**. Authorize Google Forms, email sending, external requests, and the scheduled trigger. Always use the same sending account for setup. [Google’s trigger guide](https://developers.google.com/apps-script/guides/triggers/installable)
3. In Apps Script’s **Triggers** tab, check that **runNewsletter** runs every 15 minutes.
4. After setup, submit a fresh address you control using the [newsletter Google Form](https://docs.google.com/forms/d/e/1FAIpQLSfwA0-jYPud2Pz6Bd5UZkFeaNdPcUe_hGrZxQ61xbNeLQSTXQ/viewform). The redesigned homepage also submits to this form. The legacy Squarespace signup uses its own list.
5. In the form editor, open **Responses → Individual** and confirm your test submission is present. In Apps Script, select **runNewsletter** and click **Run**, or wait for the scheduled check. Look for **Welcome to Anemone Magazine**. Reply with **Unsubscribe** to verify the reply reaches the sending account.

If the email does not arrive, open **Apps Script → Executions** and select the **runNewsletter** entry after the signup. A failed run shows its error there. A completed run may have skipped the address, for example if it was already on the list before setup. In the receiving Gmail account, search `in:anywhere subject:"Welcome to Anemone Magazine"` to include Spam and Trash.

The welcome email opens the featured Editor’s Pick on Anemone. The pick page can link to its exact page in the original Canva issue. To add that button, set `canva_page_id` in `site/editors-picks.json` to the part after `#page-` in the Canva page link. Test the resulting link in a private browser window. [Canva’s page sharing guide](https://www.canva.com/en_au/help/share-via-link-or-email/#share-a-specific-page-via-links)

Readers who signed up before activation receive future issues. Each newsletter goes to one reader and invites them to reply to unsubscribe. Links in earlier emails still work through the original unsubscribe form. Repeat signups do not generate another welcome or undo an unsubscribe.

To process an unsubscribe reply, open **Apps Script → Project Settings → Script Properties** and find the `reader.` row whose value contains the subscriber’s email address. Keep the key and replace its value with `{"stopped":true}`, then save. This removes the email address from that delivery record and suppresses future sends.

To announce an issue, publish its archive entry with a reader link or table of contents and keep its slug stable. The announcement opens the issue page on Anemone. Archive entries present at setup, later copy edits, and submission calls do not trigger mail.

The build generates `docs/newsletter.json`. The script prefers the custom domain and uses the published GitHub Pages site if that is where the feed is available. Signups can accumulate before launch. Welcome and issue emails wait for a public site so their links work for recipients.

Google MailApp sends under the account that installed the trigger. When the account reaches its daily recipient limit, later checks pick up outstanding mail as quota becomes available. This setup is intended for a small list. Subscriber state is stored privately in the Apps Script project and is subject to Google’s script-property storage limit. [MailApp reference](https://developers.google.com/apps-script/reference/mail/mail-app) · [Google quotas](https://developers.google.com/apps-script/guides/services/quotas)

If an execution reports an uncertain delivery, the script holds that reader’s pending message to prevent a duplicate. In **Project Settings → Script Properties**, locate the `reader.` key ending in the six characters shown in the execution log. After verifying delivery, remove the `pending` field from its JSON value and set `welcomed` to `true` for a welcome or `lastIssue` to the issue sequence number from `pending` (for example, `issue-2` means sequence 2). If you confirm it was never sent, remove only `pending` to retry. Keep subscriber records, addresses, and unsubscribe links private.

## Connect the feedback form

- Set `feedback_google_form` in `site/magazine.json` to the published Google Form’s `url` and paragraph question `response_field`. Rebuild and confirm a test message submitted from `/feedback/` appears in the form’s **Responses** tab.

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

- Published Canva editions and their covers appear on the individual issue pages. Issue 1 retains its contributor credits and table of contents and still needs a public reader link.
- The Issue 11 submission and staff application forms request Google sign-in. Workshop registration and mentor application use the original Google Forms, and the workshop menu uses the original Google Doc.
- Issue covers are from the magazine’s public Canva readers. Font licenses are in `docs/assets/fonts/`.

## Anemone photography

The site’s flower photographs come from Wikimedia Commons. The [Photo credits page](docs/photo-credits/index.html) gives each photographer, original image, and license. The share graphics carry photo credits as well.

Store licensed photos in `docs/assets/images/` and record their source, photographer, and license in `site/photo-credits.json`. Use a 3:2 crop. General artwork uses 960 × 640 images, and the homepage lead uses 1440 × 960. Set artwork for pages and issues in `site/magazine.json` and for features in their respective JSON files. Regenerate the share graphics when changing an Editor’s Pick photograph.
