# in-sky.eu

Website for **IN-SKY.EU** – mc.in-sky.eu: a vanilla-style OneBlock server where every island is its own private world.

- Server address: `mc.in-sky.eu` (Minecraft Java Edition 26.3, open beta)
- Discord: https://discord.in-sky.eu
- Bug reports: https://feedback.in-sky.eu

The site is a single `index.html` served with GitHub Pages. `CNAME` sets the custom domain `in-sky.eu`.

## Adding an update post

1. Create `posts/<version>.html` (copy an existing post). Start it with the JSON header
   (`version`, `date`, `title`, `summary`), then write the player-facing changes in HTML.
   Leave out internal details (database, refactors, ticket numbers, links to the private repo).
2. Run `python3 tools/build.py`. It rebuilds `updates/`, `sitemap.xml` and `feed.xml`.
3. Update the "Latest update" link in `index.html`, then commit and push.

If you change the homepage, put today's date in `.home-lastmod` before building, so the sitemap shows it.
