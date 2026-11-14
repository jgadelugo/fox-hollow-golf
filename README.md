# Fox Hollow shot map

Plot a round at **Fox Hollow Golf Club** (Branchburg, NJ) shot by shot on a satellite map of the course, then see your scorecard and stats.

## Use it

**On your phone:** open https://jgadelugo.github.io/fox-hollow-golf/ and add it to your home screen (Safari: Share → Add to Home Screen; Chrome: ⋮ → Add to Home screen). It's served from this repo's `main` branch by GitHub Pages, so pushing a change updates it within a minute or two.

**Without signal:** once you have opened the page with a connection, it opens again without one (`sw.js` keeps a copy of the pages, the map library and the satellite tiles you have looked at). Holes you haven't viewed yet show the course outlines without the satellite photo, so flick through the holes before you head out if you want the imagery everywhere.

**On your computer:** open `index.html` in a browser (double-click works), or serve the folder:

```
python scripts/serve.py      # http://localhost:8765
```

1. **New round**. To name it or change its date, open **⋯**.
2. On each hole the map is turned so the hole plays bottom → top.
   - Tap the tee box you played from (or drag the **T**).
   - Tap where each shot finished. Each shot shows its length and the lie (fairway, rough, bunker, water, green), worked out from the course map.
   - Drag the red flag to where the pin was that day; drag any ball to fix its spot.
   - Pick the club for each shot. Tap **+0** to add penalty strokes (cycles 0/1/2). **✕** deletes a shot; **Undo** on the message that follows puts it back.
   - Tap your number of **Putts** once you're on the green (**0** if you holed out from off the green). That finishes the hole: it now counts in your score, and **Next: Hole …** takes you on. Putts unlock once the hole has a shot. A finished hole takes no more shots, so a stray tap on the map can't change the score: tap **Clear putts** first if you need to add one.
   - On the course, **📍 Ball is here** adds a shot at your phone's GPS position (needs https or localhost).
   - **⛳ Green** zooms in on the green and shows its slopes: blue is low and red is high, arrows point downhill (longer = steeper), and lines mark every few inches of height. Mark where your ball is on the green and it reads the putt like a caddy: where to aim ("2 cups outside the left edge"), how hard to hit it ("like a 24 ft putt on flat ground") and which way it breaks, with the predicted roll drawn on the map. Pick the green speed (Slow 8 / Medium 10 / Fast 12). **Read from a spot** gives a read from anywhere you tap, or from your GPS position with 📍, without adding a shot. The read rolls a ball over the slopes from a USGS lidar survey at the speed you picked, so treat it as a guide to the main breaks and read the putt yourself too: the survey is about 1 m resolution and a few years old, and the green speed is a guess. Putts over 60 ft get no aim point, and where the survey shows a slope too steep for a ball to stop by the hole the read says so instead of counting cups.
3. **All holes** shows every shot on the whole course, plus round stats: score, putts, fairways hit, greens in regulation, average tee shot and distance per club.

Rounds are saved in this browser only, along with the hole each round was last on, so reopening the page mid-round brings you back to that hole. Use **⋯ → Export rounds** to keep a JSON backup (or to move rounds to your phone), and **Import** to load them back.

How stats are counted:
- **Score**: only finished holes (putts entered) count toward your total and "thru". A hole in progress shows its strokes so far, like `3…`.
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

Green slopes come from the [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) lidar elevation service (1 m, public domain). After rebuilding the course data, refresh them with:

```
python scripts/build_greens.py   # writes green-data.js (needs numpy, shapely, Pillow)
```

The home-screen icons in `icons/` are drawn by `python scripts/make_icons.py icons` (needs Pillow).

`build_course.py` assigns each tee, green and fairway to its hole. Hole 16's green is mapped just outside the club's boundary in OSM, which is why the download uses a bounding box.
