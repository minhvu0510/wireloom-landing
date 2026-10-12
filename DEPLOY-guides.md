# Deploy: guides + SEO files (seeglance.com, the static landing site)

Upload to the ROOT of the landing project (same place as landing.html / logo.jpeg):

- `guides/` (13 files: 11 new + the 2 old ones, whose canonical now points to seeglance.com; plus `index.html`)
- `sitemap.xml`, `robots.txt`
- `landing.html` (adds 4 guide cards + "See all guides" link in the #guides section)

Then, once live:
1. Open https://seeglance.com/guides/ and one guide; check the logo shows and links work.
2. Google Search Console: add property seeglance.com -> Sitemaps -> submit `sitemap.xml` -> "Request indexing" for /guides/ and 3 guides.
3. Bing Webmaster Tools: import from Search Console.
4. Deploy the app zips + week11/12/13.sql BEFORE promoting: the guides describe features that exist only after that.

Editing later: `guides-src/` holds the generator (python3 build.py). Bodies are in `guides-src/src/*.html`, metadata in `guides.py`. Change OUT paths at the top of build.py to your own folder.
