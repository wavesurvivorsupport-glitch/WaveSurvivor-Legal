# WaveSurvivor official website

This public repository contains website content only. GitHub Pages publishes the docs/ folder from main. The legal URLs under docs/legal/ remain stable.

## Edit pages

The home, Media, Support and Updates shells are generated from fragments/*.html by build_site.py. Run "python build_site.py" after editing a fragment or the shared page template. The legal pages are maintained directly under docs/legal/.

## Publish patch notes

Add a real, approved entry to docs/data/updates.json. The home preview, Updates index and update detail view read the same data. Use this shape; replace every example value with a real public update:

    {
      "id": "unique-lowercase-slug",
      "version": "published game version",
      "date": "YYYY-MM-DD",
      "headline": "Public headline",
      "summary": "One short public summary.",
      "categories": [
        { "name": "Gameplay", "changes": ["A verified player-facing change."] }
      ],
      "image": "assets/media/approved-update-image.webp",
      "imageAlt": "Description of that image"
    }

The image and imageAlt fields are optional together. Add the entry to the updates array, validate JSON, and push to main. Its detail URL is /updates/article.html?id=unique-lowercase-slug. Do not remove the in-game Patch Notes menu until this public data flow and the game's navigation to it have been separately reviewed and tested.

## Add media

docs/data/media.json drives the gallery and media slots. Upload only authentic screenshots or approved artwork into docs/assets/media/.

- Add a gallery item to items with src, descriptive alt, caption, width and height.
- To replace a labeled layout slot, add an entry to slots keyed by its data-asset-path, with src and alt.
- To publish a trailer, set trailer to an object with src, optional poster, and label. The Media page will use a native video player. Keep video files small enough for static hosting and prefer a properly optimized MP4.

See ASSET_REQUESTS.md for exact filenames and recommended sizes.
