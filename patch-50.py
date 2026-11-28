#!/usr/bin/env python3
"""『6駅先の職業』40職 → 50職へ index.html を直接パッチする。
build-occupation-40.py から再生成しない（index.html はその後 ogタグ・記録ボード・遊び方画面などが追加されており、再生成すると退行するため）。
入力: jobs-50-new.json（新規10職のJOBS/EDGES/REASON）、imgs-50.json（職ID→画像ファイルパス）
出力: index-50.html（検証用。検証後に index.html へ上書きする）
"""
import base64
import io
import json
import re
import sys
from PIL import Image

GAME = "/home/hatch/workspace/occupation-game"
ORDER = ["densha", "trimmer", "niwashi", "seisouin", "wedding",
         "hikkoshi", "takuhaibin", "keibiin", "honya", "pilot"]

new = json.load(open(f"{GAME}/jobs-50-new.json", encoding="utf-8"))
imgs = json.load(open(f"{GAME}/imgs-50.json", encoding="utf-8"))
assert set(imgs.keys()) == set(ORDER), f"imgs keys mismatch: {set(imgs.keys()) ^ set(ORDER)}"
assert set(new["jobs"].keys()) == set(ORDER)
assert len(new["edges"]) == 27, len(new["edges"])
assert len(new["reasons"]) == 27, len(new["reasons"])

def b64(path):
    im = Image.open(path).convert("RGB")
    im.thumbnail((680, 680))
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=80)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()

html = open(f"{GAME}/index.html", encoding="utf-8").read()
orig_len = len(html)

# --- 1. IMG JSON: 最後のキー haikankou の直後に10件追加（他はバイト単位で不変） ---
img_parts = []
for k in ORDER:
    data = b64(imgs[k])
    print(f"img {k}: {imgs[k]} -> {len(data)//1024} KB")
    img_parts.append(f', "{k}": "{data}"')
m = re.search(r'("haikankou": "data:image/webp;base64,[A-Za-z0-9+/=]+)"', html)
assert m, "haikankou IMG entry not found"
html = html[:m.end()] + "".join(img_parts) + html[m.end():]

# --- 2. JOBS: haikankou 行の直後に10件追加 ---
def esc(s):
    return s.replace("'", "\\'")
job_lines = []
for k in ORDER:
    j = new["jobs"][k]
    mo = ",".join(f"'{esc(x)}'" for x in j["motto"])
    job_lines.append(f"{k}: {{ name:'{esc(j['name'])}', desc:'{esc(j['desc'])}', pop:'{esc(j['pop'])}', motto:[{mo}]}}")
anchor = ("haikankou: { name:'配管工', desc:'水道の配管を直す職人。水漏れも、詰まりも、この人がいれば安心。', "
          "pop:'全国に約20万人 ― 約600人に1人', motto:['見えぬ場所','水の命を','守り抜く']}")
assert anchor in html, "haikankou JOBS anchor not found"
html = html.replace(anchor, anchor + ",\n" + ",\n".join(job_lines), 1)

# --- 3. EDGES: 最終行の直後に27本追加 ---
edge_str = ",".join(f"['{a}','{b}']" for a, b in new["edges"])
anchor_e = "['eiyoushi','isha'],['eiyoushi','kangoshi']\n];"
assert anchor_e in html, "EDGES anchor not found"
html = html.replace(anchor_e, "['eiyoushi','isha'],['eiyoushi','kangoshi'],\n" + edge_str + "\n];", 1)

# --- 4. REASON: 最終エントリの直後に27件追加 ---
reason_str = ", ".join(f"'{k}':'{v}'" for k, v in new["reasons"].items())
anchor_r = "'eiyoushi|kangoshi':'食事の見守り'\n};"
assert anchor_r in html, "REASON anchor not found"
html = html.replace(anchor_r, "'eiyoushi|kangoshi':'食事の見守り', " + reason_str + "\n};", 1)

# --- 5. 表記: 40 → 50 ---
assert html.count("職業40・5ゲーム勝負") == 1
html = html.replace("職業40・5ゲーム勝負", "職業50・5ゲーム勝負")
assert html.count("登場する40の職業") == 1
html = html.replace("登場する40の職業", "登場する50の職業")

# --- 6. 静的セクションの職業一覧に10件追加（ギャラリーページへのリンク付き） ---
items = "".join(
    f'<li><a href="https://tklabo-caremane.github.io/gallery/{k}.html">{new["jobs"][k]["name"]}</a>'
    f'：{new["jobs"][k]["desc"]}（{new["jobs"][k]["pop"]}）</li>'
    for k in ORDER)
anchor_s = "</ul></details>"
assert html.count(anchor_s) == 1, f"static list anchor count: {html.count(anchor_s)}"
html = html.replace(anchor_s, items + "</ul></details>", 1)

out = f"{GAME}/index-50.html"
open(out, "w", encoding="utf-8").write(html)
print(f"saved {out}: {orig_len//1024} KB -> {len(html)//1024} KB")
