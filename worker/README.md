# 週間ベスト記録 Worker（2026-11-22 稼働開始）
- Worker名: rokuji-scores
- URL: https://rokuji-scores.tac09280317.workers.dev （GET /best, POST /score {total}）
- Cloudflare アカウントID: a768e902673cb67db48caa3298e58d5f / workers.dev サブドメイン: tac09280317
- KV: ROKUJI_SCORES (id: ecf979c6f9db4277974ad2f6673b5490), binding 名 SCORES
- トークン「runo」に Workers（編集＋管理）と Workers KV Storage（編集）を追加済み（2026-11-22 本人が実施）
- デプロイ: multipart PUT /accounts/{ACC}/workers/scripts/rokuji-scores（metadata main_module=worker.js + KV binding）。スクリプトは scores-worker.js
- 検証範囲: total 250〜640 の整数のみ（現行の満点は610）
- 週キー: JST の ISO 週（月曜始まり）、TTL 40日
