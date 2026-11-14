# Fox Hollow shot map

Plot a round at **Fox Hollow Golf Club** (Branchburg, NJ) shot by shot on a satellite map of the course, then see your scorecard and stats.

## Use it

**On your phone:** open https://jgadelugo.github.io/fox-hollow-golf/ and add it to your home screen (Safari: Share → Add to Home Screen; Chrome: ⋮ → Add to Home screen). It's served from this repo's `main` branch by GitHub Pages, so pushing a change updates it within a minute or two.

**On your computer:** open `index.html` in a browser (double-click works), or serve the folder:

```
python scripts/serve.py      # http://localhost:8765
```

1. **New round** → give it a name and date.
2. On each hole the map is turned so the hole plays bottom → top.
   - Tap the tee box you played from (or drag the **T**).
   - Tap where each shot finished. Each shot shows its length and the lie (fairway, rough, bunker, water, green), worked out from the course map.
   - Drag the red flag to where the pin was that day; drag any ball to fix its spot.
   - Pick the club for each shot. Tap **+0** to add penalty strokes (cycles 0/1/2).
   - Enter **Putts** once you're on the green (**Holed out (0)** for chip-ins).
   - On the course, **📍 Ball is here** adds a shot at your phone's GPS position (needs https or localhost).
3. **All holes** shows every shot on the whole course, plus round stats: score, putts, fairways hit, greens in regulation, average tee shot and distance per club.

Rounds are saved in this browser only. Use **⋯ → Export rounds** to keep a JSON backup (or to move rounds to your phone), and **Import** to load them back.

How stats are counted:
- **Fairway hit**: on a par 4 or 5, the tee shot finished on this hole's fairway with no penalty.
- **Green in regulation**: strokes before putting (including penalties) ≤ par − 2, and you putted at least once.

## Course data

Hole lines, par, tees, greens, fairways, bunkers and water come from OpenStreetMap (© OpenStreetMap contributors, ODbL). Satellite imagery is from Esri. Yardages are measured on the map and won't match the scorecard exactly. OSM lists the course as par 70 (35/35); check that against the real scorecard.

To refresh the course data:

```
sh scripts/fetch_osm.sh          # downloads data/osm_raw.json
python scripts/build_course.py   # writes course-data.js and data/fox-hollow.geojson (needs shapely)
```

`build_course.py` assigns each tee, green and fairway to its hole. Hole 16's green is mapped just outside the club's boundary in OSM, which is why the download uses a bounding box.
