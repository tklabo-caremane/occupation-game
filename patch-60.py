#!/usr/bin/env python3
"""『6駅先の職業』50職 → 60職へ index.html を直接パッチする（patch-50.py の方式を踏襲）。
入力: jobs-60-new.json（新規10職のJOBS/EDGES/REASON）、imgs-60.json（職ID→画像ファイルパス）
出力: index-60.html（検証用。検証後に index.html へ上書きする）
"""
import base64
import io
import json
import re
from PIL import Image

GAME = "/home/hatch/workspace/occupation-game"
ORDER = ["ginkouin", "hotel", "shiikuin", "juku", "seitai",
         "sougiya", "kyuukyuu", "shinbun", "petshop", "cleaning"]

new = json.load(open(f"{GAME}/jobs-60-new.json", encoding="utf-8"))
imgs = json.load(open(f"{GAME}/imgs-60.json", encoding="utf-8"))
assert set(imgs.keys()) == set(ORDER), f"imgs keys mismatch: {set(imgs.keys()) ^ set(ORDER)}"
assert set(new["jobs"].keys()) == set(ORDER)
assert len(new["edges"]) == 25, len(new["edges"])
assert len(new["reasons"]) == 25, len(new["reasons"])

def b64(path):
    im = Image.open(path).convert("RGB")
    im.thumbnail((680, 680))
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=80)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()

html = open(f"{GAME}/index.html", encoding="utf-8").read()
orig_len = len(html)

# --- 1. IMG JSON: 最後のキー pilot の直後に10件追加 ---
img_parts = []
for k in ORDER:
    data = b64(imgs[k])
    print(f"img {k}: {imgs[k]} -> {len(data)//1024} KB")
    img_parts.append(f', "{k}": "{data}"')
m = re.search(r'("pilot": "data:image/webp;base64,[A-Za-z0-9+/=]+)"', html)
assert m, "pilot IMG entry not found"
html = html[:m.end()] + "".join(img_parts) + html[m.end():]

# --- 2. JOBS: pilot 行の直後に10件追加 ---
def esc(s):
    return s.replace("'", "\\'")
job_lines = []
for k in ORDER:
    j = new["jobs"][k]
    mo = ",".join(f"'{esc(x)}'" for x in j["motto"])
    job_lines.append(f"{k}: {{ name:'{esc(j['name'])}', desc:'{esc(j['desc'])}', pop:'{esc(j['pop'])}', motto:[{mo}]}}")
anchor = ("pilot: { name:'パイロット', desc:'飛行機を操縦する人。空の旅の安全は、この人の腕にかかっている。', "
          "pop:'全国に約7,000人 ― 約18,000人に1人', motto:['雲の上','空の旅路を','切り開く']}")
assert anchor in html, "pilot JOBS anchor not found"
html = html.replace(anchor, anchor + ",\n" + ",\n".join(job_lines), 1)

# --- 3. EDGES: 最終行 ['pilot','bus'] の直後に25本追加 ---
edge_str = ",".join(f"['{a}','{b}']" for a, b in new["edges"])
anchor_e = "['pilot','bus']\n];"
assert anchor_e in html, "EDGES anchor not found"
html = html.replace(anchor_e, "['pilot','bus'],\n" + edge_str + "\n];", 1)

# --- 4. REASON: 最終エントリの直後に25件追加 ---
reason_str = ", ".join(f"'{k}':'{v}'" for k, v in new["reasons"].items())
anchor_r = "'takuhaibin|yuubin':'届ける仲間'\n};"
assert anchor_r in html, "REASON anchor not found"
html = html.replace(anchor_r, "'takuhaibin|yuubin':'届ける仲間', " + reason_str + "\n};", 1)

# --- 5. 表記: 50 → 60 ---
assert html.count("職業50・5ゲーム勝負") == 1
html = html.replace("職業50・5ゲーム勝負", "職業60・5ゲーム勝負")
assert html.count("登場する50の職業") == 1
html = html.replace("登場する50の職業", "登場する60の職業")

# --- 6. 静的セクションの職業一覧に10件追加（ギャラリーページへのリンク付き） ---
items = "".join(
    f'<li><a href="https://tklabo-caremane.github.io/gallery/{k}.html">{new["jobs"][k]["name"]}</a>'
    f'：{new["jobs"][k]["desc"]}（{new["jobs"][k]["pop"]}）</li>'
    for k in ORDER)
anchor_s = "</ul></details>"
assert html.count(anchor_s) == 1, f"static list anchor count: {html.count(anchor_s)}"
html = html.replace(anchor_s, items + "</ul></details>", 1)

out = f"{GAME}/index-60.html"
open(out, "w", encoding="utf-8").write(html)
print(f"saved {out}: {orig_len//1024} KB -> {len(html)//1024} KB")
