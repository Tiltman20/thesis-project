import sqlite3
import numpy as np

DB_PATH = "res\\test_results\\test1\\database.db"

MAX_IMAGE_ID = 2147483647

def pair_id_to_image_ids(pair_id):
    i = pair_id // MAX_IMAGE_ID
    j = pair_id % MAX_IMAGE_ID
    return i, j

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

images = cur.execute("SELECT image_id, name FROM images").fetchall()
image_names = {i: n for i, n in images}

print("\nAnzahl Bilder:", len(images))

geoms = cur.execute(
    "SELECT pair_id, rows FROM two_view_geometries"
).fetchall()

print("Anzahl two_view_geometries:", len(geoms))

geoms_sorted = sorted(geoms, key=lambda x: x[1])

print("\n=== Schlechteste Paare (wenig Matches) ===")
for pair_id, rows in geoms_sorted[:20]:
    i, j = pair_id_to_image_ids(pair_id)
    print(f"{image_names.get(i, i)}  <->  {image_names.get(j, j)}:  {rows} matches")


degrees = {img_id: 0 for img_id, _ in images}

for pair_id, rows in geoms:
    i, j = pair_id_to_image_ids(pair_id)
    degrees[i] += rows
    degrees[j] += rows

print("\n=== Bilder nach Anzahl der Gesamtmatches sortiert ===")
deg_sorted = sorted(degrees.items(), key=lambda x: x[1])

for img_id, score in deg_sorted:
    print(f"{image_names.get(img_id, img_id)}:  {score} total matches")


hist = {}
for _, rows in geoms:
    hist[rows] = hist.get(rows, 0) + 1

print("\n=== Match-Histogramm (rows -> Anzahl Paare) ===")
for rows in sorted(hist.keys()):
    print(f"{rows} matches: {hist[rows]} pairs")


conn.close()
print("\nFertig.")
