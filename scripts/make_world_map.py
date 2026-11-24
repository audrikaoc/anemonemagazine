#!/usr/bin/env python3
"""Create the reusable SVG map from Natural Earth 1:50m map-unit GeoJSON."""

import json
import re
from collections import defaultdict
from itertools import groupby
from math import asin, cos, radians, sin, sqrt
from pathlib import Path
from sys import argv
from xml.sax.saxutils import escape

OUTPUT = Path(__file__).resolve().parents[1] / 'docs' / 'assets' / 'world-countries.svg'
COUNTRY_NAMES = {'CN': 'China', 'PS': 'Palestine', 'RS': 'Serbia', 'US': 'United States'}


def project(longitude, latitude):
    # Spherical Equal Earth projection, Šavrič, Patterson, and Jenny (2018).
    a1, a2, a3, a4 = 1.340264, -0.081106, 0.000893, 0.003796
    m = sqrt(3) / 2
    theta = asin(m * sin(radians(latitude)))
    theta2 = theta ** 2
    theta6 = theta ** 6
    x = radians(longitude) * cos(theta) / (m * (a1 + 3 * a2 * theta2 + theta6 * (7 * a3 + 9 * a4 * theta2)))
    y = theta * (a1 + a2 * theta2 + theta6 * (a3 + a4 * theta2))
    return 500 + 175 * x, 260 - 175 * y


def simplify(points):
    """Drop detail smaller than a fraction of a pixel at the map’s reference size."""
    if len(points) <= 2:
        return points
    x0, y0 = points[0]
    dx, dy = points[-1][0] - x0, points[-1][1] - y0
    length_squared = dx * dx + dy * dy
    distance_limit = .24 ** 2
    split = None
    for index, (x, y) in enumerate(points[1:-1], 1):
        fraction = ((x - x0) * dx + (y - y0) * dy) / length_squared if length_squared else 0
        fraction = max(0, min(1, fraction))
        distance = (x - x0 - dx * fraction) ** 2 + (y - y0 - dy * fraction) ** 2
        if distance > distance_limit:
            split = index
            distance_limit = distance
    if split is None:
        return [points[0], points[-1]]
    return simplify(points[:split + 1])[:-1] + simplify(points[split:])


def path_for(coordinates, close=False):
    points = [point for point, _ in groupby(tuple(round(v, 1) for v in project(*pair)) for pair in coordinates)]
    reduced = simplify(points)
    if not close or len(set(reduced)) >= 3:
        points = reduced
    if close and points[0] == points[-1]:
        points.pop()
    if len(points) < (3 if close else 2):
        return ''
    return 'M' + ' '.join(f'{x:g},{y:g}' for x, y in points) + ('Z' if close else '')


def land_shape(feature):
    geometry = feature['geometry']
    polygons = geometry['coordinates'] if geometry['type'] == 'MultiPolygon' else [geometry['coordinates']]
    return ''.join(path_for(ring, close=True) for polygon in polygons for ring in polygon)


def build_map(source):
    features = json.loads(source.read_text(encoding='utf-8'))['features']
    countries = defaultdict(list)
    other_regions = []
    for feature in features:
        code = feature['properties']['ISO_A2_EH']
        if re.fullmatch('[A-Z]{2}', code):
            countries[code].append(feature)
        else:
            other_regions.append(feature)

    paths = []
    markers = []
    for code, units in sorted(countries.items()):
        main_unit = max(units, key=lambda unit: unit['properties']['POP_EST'])['properties']
        default_name = main_unit['NAME_EN'] if len(units) == 1 else main_unit['SOVEREIGNT']
        name = COUNTRY_NAMES.get(code, default_name)
        outline = ''.join(land_shape(unit) for unit in units)
        x, y = project(main_unit['LABEL_X'], main_unit['LABEL_Y'])
        paths.append(f'      <path id="country-{code}" d="{outline}"><title>{escape(name)}</title></path>')
        # A minimum-size marker makes a highlighted small country visible on phones.
        if main_unit['TINY'] >= 0:
            markers.append(f'    <circle id="marker-{code}" cx="{x:.1f}" cy="{y:.1f}" r="3.5"/>')

    paths.extend(f'      <path d="{land_shape(feature)}"/>' for feature in other_regions)
    meridians = [path_for((lon, lat) for lat in range(-75, 86, 3)) for lon in range(-150, 151, 30)]
    parallels = [path_for((lon, lat) for lon in range(-180, 181, 3)) for lat in range(-60, 61, 30)]
    grid = ''.join(meridians + parallels)
    OUTPUT.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 12 1000 500">\n'
        '  <defs>\n'
        f'    <path id="world-graticule" d="{grid}"/>\n'
        '    <g id="world-land">\n' + '\n'.join(paths) + '\n    </g>\n'
        + '\n'.join(markers) + '\n  </defs>\n</svg>\n',
        encoding='utf-8',
    )


if __name__ == '__main__':
    if len(argv) != 2:
        raise SystemExit('Usage: python3 scripts/make_world_map.py <Natural Earth GeoJSON>')
    build_map(Path(argv[1]))
