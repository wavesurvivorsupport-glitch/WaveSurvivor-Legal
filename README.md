# WaveSurvivor official website

This public repository contains website content only. GitHub Pages publishes the docs/ folder from main. The legal URLs under docs/legal/ remain stable.

## Edit pages

The home, Media, Support and Updates shells are generated from fragments/*.html by build_site.py. Run "python build_site.py" after editing a fragment or the shared page template. The legal pages are maintained directly under docs/legal/.

## Publish patch notes

`docs/data/updates.json` is the public website source. The site builder generates the homepage preview, newest-first Updates index, a permanent HTML page for each note, the sitemap, and `docs/updates.xml` from that one file. Every versioned release must also be added to the game's `Assets/scripts/Resources/UI/Menu/PatchNotes.json` catalog. Keep the version, date, and player-facing changes consistent between both feeds. Publish only verified player-facing changes. Do not create Steam notes unless explicitly requested.

For the next release:

1. Add one entry to the `updates` array in `docs/data/updates.json` using the format below. Put the newest note first for easy editing; the builder sorts by date and version.
2. Run `python build_site.py` and `python qa_site.py` from the repository root. The first command regenerates every update page and feed; the second checks links, data, and feed consistency.
3. Preview with `python -m http.server 8000 --directory docs`, then open `http://localhost:8000/updates/` and the new article. Stop the preview server when finished.
4. Commit the JSON and generated website files, then push to `main`. GitHub Pages publishes `main` / `docs`. Players can read the note at `https://wavesurvivorsupport-glitch.github.io/WaveSurvivor-Legal/updates/` without launching or rebuilding the game.

Example entry (replace every example value with a real public update):

    {
      "id": "v0-2-0",
      "version": "0.2.0",
      "date": "YYYY-MM-DD",
      "headline": "Update v0.2.0",
      "summary": "One short summary of verified changes.",
      "categories": [
        { "name": "Gameplay", "changes": ["A verified player-facing change."] }
      ],
      "image": "assets/media/approved-update-image.webp",
      "imageAlt": "Description of that image"
    }

Required fields: a unique lowercase `id` using letters, numbers, and hyphens; `headline`; `summary`; and at least one category with a name and nonempty `changes` list. Include `version` and an ISO `date` whenever known. Omit or use `null` for a genuinely unknown historical version/date; never guess one. `image` and `imageAlt` are optional together. Keep change descriptions complete. Each article URL is `/updates/<id>.html`; never reuse an existing id for a different note.

The public RSS feed at `/updates.xml` is generated from the same JSON. Services such as PatchBot can use the feed if their current product supports that URL and format; configure such a service only after checking its official requirements. The game's Main Menu also contains a Patch Notes page. Its displayed build version comes from Unity's application version and is changed only as part of a deliberate game release.

## Add media

docs/data/media.json drives the gallery and media slots. Upload only authentic screenshots or approved artwork into docs/assets/media/.

- Add a gallery item to items with src, descriptive alt, caption, width and height.
- To replace a labeled layout slot, add an entry to slots keyed by its data-asset-path, with src and alt.
- The scroll sequence reads the same slots map using the data-scene-path values in fragments/home.html. Its first two scenes reuse the Story images; the third uses endless-wave.webp.
- To publish a trailer, set trailer to an object with src, optional poster, and label. The Media page will use a native video player. Keep video files small enough for static hosting and prefer a properly optimized MP4.

See ASSET_REQUESTS.md for exact filenames and recommended sizes.
