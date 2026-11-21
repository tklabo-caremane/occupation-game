// 『6駅先の職業』週間ベスト記録用 Worker
// KV binding: SCORES
// GET  /best          -> { week, best, plays }
// POST /score {total} -> 5ゲーム合計点を記録し、週の最高を返す
function weekKeyJST() {
  const now = new Date(Date.now() + 9 * 3600 * 1000);
  const d = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()));
  const day = (d.getUTCDay() + 6) % 7; // Mon=0
  d.setUTCDate(d.getUTCDate() - day + 3); // Thursday of this week
  const firstThu = new Date(Date.UTC(d.getUTCFullYear(), 0, 4));
  const fday = (firstThu.getUTCDay() + 6) % 7;
  firstThu.setUTCDate(firstThu.getUTCDate() - fday + 3);
  const week = 1 + Math.round((d - firstThu) / (7 * 24 * 3600 * 1000));
  return d.getUTCFullYear() + '-W' + String(week).padStart(2, '0');
}
const CORS = {
  'Access-Control-Allow-Origin': 'https://tklabo-caremane.github.io',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type'
};
export default {
  async fetch(req, env) {
    if (req.method === 'OPTIONS') return new Response(null, { headers: CORS });
    const url = new URL(req.url);
    const key = 'best:' + weekKeyJST();
    let rec = { best: 0, plays: 0 };
    const raw = await env.SCORES.get(key);
    if (raw) { try { rec = JSON.parse(raw); } catch (e) {} }
    if (url.pathname === '/score' && req.method === 'POST') {
      let total = NaN;
      try { total = (await req.json()).total; } catch (e) {}
      if (!Number.isInteger(total) || total < 250 || total > 640) {
        return Response.json({ ok: false }, { status: 400, headers: CORS });
      }
      rec.plays += 1;
      if (total > rec.best) rec.best = total;
      await env.SCORES.put(key, JSON.stringify(rec), { expirationTtl: 60 * 60 * 24 * 40 });
      return Response.json({ ok: true, week: key.slice(5), best: rec.best, plays: rec.plays }, { headers: CORS });
    }
    if (url.pathname === '/best' && req.method === 'GET') {
      return Response.json({ week: key.slice(5), best: rec.best, plays: rec.plays }, { headers: CORS });
    }
    return new Response('not found', { status: 404, headers: CORS });
  }
};
