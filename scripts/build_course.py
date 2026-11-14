"""Turn the raw OpenStreetMap download for Fox Hollow Golf Club into the
course data the web page uses.

Input : data/osm_raw.json   (Overpass "out geom" response)
Output: data/fox-hollow.geojson  (plain GeoJSON, for inspection / reuse)
        course-data.js           (same data as `window.COURSE = {...}` so the
                                  page works when opened straight from disk)

Each feature gets a `kind` (tee, green, fairway, bunker, water, hole, ...).
Tees, greens and fairways also get `holes` — the hole number(s) they belong
to — so the page can tell "on the green" and "fairway hit" for each hole.

Re-download the raw data with scripts/fetch_osm.sh if the OSM map changes.
"""
import json
import math
from pathlib import Path

from shapely.geometry import LineString, Point, Polygon, mapping, shape
from shapely.ops import linemerge, polygonize, transform, unary_union

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "osm_raw.json"

# Local flat projection (metres) centred on the course: plenty accurate
# over a ~2 km area and avoids a pyproj dependency.
LAT0 = 40.617
M_PER_DEG_LAT = 111_132.0
M_PER_DEG_LON = 111_320.0 * math.cos(math.radians(LAT0))


def to_m(x, y, z=None):
    return (x * M_PER_DEG_LON, y * M_PER_DEG_LAT)


def m(geom):
    return transform(to_m, geom)


KIND = {
    "tee": "tee",
    "green": "green",
    "fairway": "fairway",
    "bunker": "bunker",
    "water_hazard": "water",
    "lateral_water_hazard": "water",
    "rough": "rough",
    "cartpath": "cartpath",
    "clubhouse": "clubhouse",
    "driving_range": "driving_range",
    "hole": "hole",
    "pin": "pin",
}


def element_kind(tags):
    if tags.get("leisure") == "golf_course":
        return "course"
    if tags.get("golf") in KIND:
        return KIND[tags["golf"]]
    if tags.get("natural") == "water":
        return "water"
    return None


def way_geom(el, kind):
    pts = [(p["lon"], p["lat"]) for p in el["geometry"]]
    closed = len(pts) >= 4 and pts[0] == pts[-1]
    if kind in ("hole", "cartpath") or not closed:
        return LineString(pts)
    return Polygon(pts)


def relation_geom(el):
    outers, inners = [], []
    for mem in el.get("members", []):
        if mem.get("type") != "way" or "geometry" not in mem:
            continue
        line = LineString([(p["lon"], p["lat"]) for p in mem["geometry"]])
        (inners if mem.get("role") == "inner" else outers).append(line)
    outer = unary_union(list(polygonize(linemerge(outers))))
    if inners:
        outer = outer.difference(unary_union(list(polygonize(linemerge(inners)))))
    return outer


def main():
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    feats = []
    for el in raw["elements"]:
        tags = el.get("tags", {})
        kind = element_kind(tags)
        if not kind:
            continue
        if el["type"] == "node":
            geom = Point(el["lon"], el["lat"])
        elif el["type"] == "way":
            geom = way_geom(el, kind)
        else:
            geom = relation_geom(el)
        if geom.is_empty:
            continue
        feats.append({"kind": kind, "osm": f"{el['type']}/{el['id']}", "tags": tags, "geom": geom})

    holes = sorted((f for f in feats if f["kind"] == "hole"), key=lambda f: int(f["tags"]["ref"]))
    hole_m = {int(h["tags"]["ref"]): m(h["geom"]) for h in holes}

    def nearest_hole(pt_m, which):
        """Hole whose tee end (which=0) or green end (which=-1) is closest."""
        best = min(hole_m.items(), key=lambda kv: Point(kv[1].coords[which]).distance(pt_m))
        return best[0], Point(best[1].coords[which]).distance(pt_m)

    report = []
    for f in feats:
        g = m(f["geom"])
        if f["kind"] == "green":
            n, d = nearest_hole(g.centroid, -1)
            # A green far from any hole end is the practice green.
            f["holes"] = [n] if d < 40 else []
            if d >= 40:
                f["kind"] = "practice_green"
            report.append(("green", f["holes"], round(d)))
        elif f["kind"] == "tee":
            n, d = nearest_hole(g.centroid, 0)
            f["holes"] = [n] if d < 120 else []
        elif f["kind"] == "fairway":
            hs = [n for n, line in hole_m.items() if line.intersection(g).length > 25]
            if not hs:
                hs = [min(hole_m, key=lambda n: hole_m[n].distance(g))]
            f["holes"] = hs
            report.append(("fairway", hs, None))

    hole_info = []
    for h in holes:
        n = int(h["tags"]["ref"])
        line = h["geom"]
        hole_info.append({
            "number": n,
            "par": int(h["tags"].get("par", 0)),
            "handicap": int(h["tags"]["handicap"]) if h["tags"].get("handicap", "").isdigit() else None,
            "yards": round(hole_m[n].length / 0.9144),
            "line": [list(c) for c in line.coords],
            "tees": sum(1 for f in feats if f["kind"] == "tee" and n in f.get("holes", [])),
            "green": any(f["kind"] == "green" and n in f.get("holes", []) for f in feats),
            "fairway": any(f["kind"] == "fairway" and n in f.get("holes", []) for f in feats),
        })

    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": mapping(f["geom"]),
                "properties": {
                    "kind": f["kind"],
                    "osm": f["osm"],
                    **({"holes": f["holes"]} if "holes" in f else {}),
                    **({"ref": int(f["tags"]["ref"])} if f["kind"] == "hole" else {}),
                },
            }
            for f in feats
        ],
    }
    # Trim coordinates to ~1 cm to keep the file small.
    def rnd(o):
        if isinstance(o, float):
            return round(o, 7)
        if isinstance(o, (list, tuple)):
            return [rnd(x) for x in o]
        if isinstance(o, dict):
            return {k: rnd(v) for k, v in o.items()}
        return o

    geojson = rnd(geojson)
    course = {
        "name": "Fox Hollow Golf Club",
        "location": "Branchburg, NJ",
        "source": "OpenStreetMap contributors (ODbL)",
        "holes": rnd(hole_info),
        "features": geojson,
    }
    (ROOT / "data" / "fox-hollow.geojson").write_text(json.dumps(geojson), encoding="utf-8")
    (ROOT / "course-data.js").write_text(
        "// Generated by scripts/build_course.py from OpenStreetMap data (ODbL). Do not edit.\n"
        "window.COURSE = " + json.dumps(course) + ";\n",
        encoding="utf-8",
    )

    print(f"{len(feats)} features")
    for h in hole_info:
        print(f"hole {h['number']:2d} par {h['par']} {h['yards']:4d} yds  tees={h['tees']} green={h['green']} fairway={h['fairway']} hcp={h['handicap']}")
    print("par total", sum(h["par"] for h in hole_info))
    for r in report:
        print(*r)


if __name__ == "__main__":
    main()
