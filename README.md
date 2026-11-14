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

## Group scorecard (for friends)

https://jgadelugo.github.io/fox-hollow-golf/group/ is a live scorecard for your group.

1. One person taps **Start a new round** and then **Invite**, which shares a link like `…/group/?r=K7Q2XM`.
2. Everyone opens the link and types their name. Use **Add** for someone without a phone.
3. Anyone can enter anyone's score. Tap **+** to start at par and **−** for a birdie. Everyone sees the leaderboard and scorecard update live.

**Using the shot map too?** After you join a group round on your phone, open the shot map and tap **Post my scores to group round …** under *Group round*. From then on, every hole you finish in the shot map (shots + penalties + putts) posts to the group leaderboard by itself, and corrections post too. Tap ✕ to stop.

Scores travel through [ntfy.sh](https://ntfy.sh), a free public message relay, under a topic named `fhgolf-<code>`. ntfy.sh keeps them for 12 hours, so latecomers catch up. Each phone also keeps its own copy and holds unsent scores until it has signal again. Anyone with the code can see and edit the round, so keep it to names and scores.

ntfy.sh allows 250 messages a day per network (IP address). The page saves up score taps for 2.5 seconds and sends them as one message, which works out to about one message per hole, so a full round uses roughly 20–40. If the limit is hit anyway, the page says so and keeps the scores on that phone until they can be sent.

## Course data

Hole lines, par, tees, greens, fairways, bunkers and water come from OpenStreetMap (© OpenStreetMap contributors, ODbL). Satellite imagery is from Esri. Yardages are measured on the map and won't match the scorecard exactly. OSM lists the course as par 70 (35/35); check that against the real scorecard.

To refresh the course data:

```
sh scripts/fetch_osm.sh          # downloads data/osm_raw.json
python scripts/build_course.py   # writes course-data.js and data/fox-hollow.geojson (needs shapely)
```

`build_course.py` assigns each tee, green and fairway to its hole. Hole 16's green is mapped just outside the club's boundary in OSM, which is why the download uses a bounding box.
