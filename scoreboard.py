import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BOARD = Path("scoreboard.json")
DATA = Path(__file__).parent / "data"

LEVEL_META = {
    "L1 Contract review": ("L1", 20),
    "L2 Test design": ("L2", 25),
    "L3 Safety + incident": ("L3", 30),
    "L4 Migration": ("L4", 25),
}


# ── Navigation bar (shared across pages) ─────────────────────────────────────

def _nav(active: str = "/") -> str:
    links = [("/", "Scoreboard"), ("/api/v1", "API v1"), ("/api/v2", "API v2")]
    items = "".join(
        f'<a href="{href}"{"  class=\"active\"" if href == active else ""}>{label}</a>'
        for href, label in links
    )
    return (
        '<nav>'
        '<span class="brand">API Hackathon</span>'
        f'{items}'
        '</nav>'
    )

_NAV_CSS = """
nav{background:#172033;padding:12px 24px;display:flex;gap:20px;align-items:center;
    border-bottom:1px solid #1e3a5f}
.brand{font-weight:700;color:#fff;margin-right:8px;font-size:.95rem}
nav a{color:#94a3b8;text-decoration:none;font-size:.9rem}
nav a:hover,nav a.active{color:#fff}
"""


# ── Swagger UI pages ──────────────────────────────────────────────────────────

def _swagger_page(version: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Orders API v{version}</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:system-ui,-apple-system,sans-serif}}
    {_NAV_CSS}
  </style>
</head>
<body>
  {_nav(f"/api/v{version}")}
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({{
      url: "/spec/v{version}.json",
      dom_id: "#swagger-ui",
      presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
      layout: "BaseLayout",
      deepLinking: true,
      defaultModelsExpandDepth: 1,
    }});
  </script>
</body>
</html>"""


# ── Scoreboard page ───────────────────────────────────────────────────────────

def _board_page() -> str:
    entries = json.loads(BOARD.read_text()) if BOARD.exists() else []

    rows = ""
    for rank, entry in enumerate(entries, 1):
        team = html.escape(entry["team"])
        score = entry["score"]
        updated = entry.get("updated", "")[:16].replace("T", " ") + " UTC"
        checks = entry.get("checks", [])

        # Mini progress bars for each level
        bars = ""
        for lname, (lshort, lmax) in LEVEL_META.items():
            pts = entry["levels"].get(lname, 0)
            pct = round(pts / lmax * 100) if lmax else 0
            bars += (
                f'<div class="lb">'
                f'<span class="lb-key">{lshort}</span>'
                f'<div class="lb-track"><div class="lb-fill" style="width:{pct}%"></div></div>'
                f'<span class="lb-val">{pts}</span>'
                f'</div>'
            )

        # Per-check detail (grouped by level)
        if checks:
            by_level: dict[str, list] = {}
            for c in checks:
                by_level.setdefault(c["level"], []).append(c)
            groups = ""
            for lk in ("L1", "L2", "L3", "L4"):
                lc = by_level.get(lk, [])
                if not lc:
                    continue
                items = ""
                for c in lc:
                    cls = "dp" if c["passed"] else "df"
                    icon = "✅" if c["passed"] else "❌"
                    note = (f' <span class="dn">— {html.escape(c["note"])}</span>'
                            if c.get("note") and not c["passed"] else "")
                    items += (
                        f'<div class="dc {cls}">'
                        f'{icon} {html.escape(c["name"])}'
                        f' <span class="dpts">{c["earned"]}/{c["max"]}</span>'
                        f'{note}'
                        f'</div>'
                    )
                groups += f'<div class="dg"><div class="dg-title">{lk}</div>{items}</div>'
            detail_inner = f'<div class="dcheck-grid">{groups}</div>'
        else:
            detail_inner = (
                '<p style="color:#94a3b8;font-size:.85rem">'
                'Re-run <code>python score.py</code> to see per-check detail.'
                '</p>'
            )

        rows += f"""
<tr class="tr" onclick="toggle(this)" data-id="d{rank}">
  <td class="rank">{rank}</td>
  <td class="tname">{team}</td>
  <td class="tscore"><strong>{score}</strong><span class="of">/100</span></td>
  <td class="tbars">{bars}</td>
  <td class="tup">{updated}</td>
  <td class="tarrow">▶</td>
</tr>
<tr id="d{rank}" class="detail-row" style="display:none">
  <td colspan="6" class="detail-cell">
    <div class="detail-inner">{detail_inner}</div>
  </td>
</tr>"""

    if not rows:
        rows = (
            '<tr><td colspan="6" class="empty">'
            'No scores yet — run <code>python score.py --all</code> or '
            '<code>python score.py --team "Your Team"</code>'
            '</td></tr>'
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta http-equiv="refresh" content="5">
  <title>API AI Hackathon – Scoreboard</title>
  <style>
    :root{{--bg:#0f172a;--card:#1e293b;--border:#334155;--text:#f1f5f9;--sub:#94a3b8;--accent:#3b82f6}}
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:system-ui,-apple-system,sans-serif;background:var(--bg);color:var(--text);min-height:100vh}}
    {_NAV_CSS}
    .wrap{{max-width:1120px;margin:0 auto;padding:32px 20px}}
    h1{{font-size:1.5rem;font-weight:700;margin-bottom:4px}}
    .sub{{color:var(--sub);font-size:.88rem;margin-bottom:28px}}
    .sub code{{background:#1e293b;padding:1px 5px;border-radius:4px;font-size:.82rem}}
    table{{width:100%;border-collapse:collapse}}
    th{{text-align:left;padding:10px 14px;font-size:.75rem;text-transform:uppercase;
        letter-spacing:.07em;color:var(--sub);border-bottom:1px solid var(--border)}}
    .tr td{{padding:14px;border-bottom:1px solid var(--border);vertical-align:middle;cursor:pointer}}
    .tr:hover td{{background:rgba(59,130,246,.06)}}
    .rank{{color:var(--sub);font-size:.9rem;width:36px}}
    .tname{{font-weight:600}}
    .tscore strong{{font-size:1.25rem;color:var(--accent)}}
    .of{{color:var(--sub);font-size:.85rem}}
    .tbars{{min-width:200px}}
    .lb{{display:flex;align-items:center;gap:6px;margin:2px 0}}
    .lb-key{{font-size:.7rem;color:var(--sub);width:18px;flex-shrink:0}}
    .lb-track{{flex:1;background:#0f172a;border-radius:999px;height:5px;overflow:hidden;
               border:1px solid var(--border);min-width:60px}}
    .lb-fill{{height:100%;border-radius:999px;background:var(--accent)}}
    .lb-val{{font-size:.72rem;color:var(--sub);width:20px;text-align:right}}
    .tup{{font-size:.78rem;color:var(--sub)}}
    .tarrow{{color:var(--sub);font-size:.75rem;width:20px;text-align:center;transition:transform .15s}}
    .tr.open .tarrow{{transform:rotate(90deg)}}
    .detail-row td{{padding:0}}
    .detail-inner{{padding:16px 20px 20px 56px;background:#090f1a;border-bottom:1px solid var(--border)}}
    .dcheck-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}}
    .dg{{display:flex;flex-direction:column;gap:5px}}
    .dg-title{{font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;
               color:var(--sub);font-weight:600;margin-bottom:2px}}
    .dc{{padding:7px 11px;border-radius:6px;font-size:.83rem;line-height:1.4}}
    .dp{{background:#0c2a1a;border:1px solid #166534}}
    .df{{background:#2a0c0c;border:1px solid #7f1d1d}}
    .dpts{{font-weight:700;color:var(--sub);margin-left:4px}}
    .dn{{color:#f87171;font-size:.76rem}}
    .empty{{text-align:center;color:var(--sub);padding:48px;font-size:.9rem}}
    .empty code{{background:#1e293b;padding:2px 6px;border-radius:4px}}
  </style>
  <script>
    function toggle(row) {{
      var id = row.getAttribute("data-id");
      var det = document.getElementById(id);
      var open = det.style.display !== "none";
      det.style.display = open ? "none" : "table-row";
      row.classList.toggle("open", !open);
    }}
  </script>
</head>
<body>
  {_nav("/")}
  <div class="wrap">
    <h1>Scoreboard</h1>
    <p class="sub">Click any row to expand per-check detail. Auto-refreshes every 5 s.</p>
    <table>
      <thead>
        <tr>
          <th>#</th><th>Team</th><th>Score</th>
          <th>Level breakdown</th><th>Last updated</th><th></th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
</body>
</html>"""


# ── HTTP handler ──────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]

        if path == "/":
            body = _board_page().encode()
            ctype = "text/html; charset=utf-8"
        elif path == "/api/v1":
            body = _swagger_page("1").encode()
            ctype = "text/html; charset=utf-8"
        elif path == "/api/v2":
            body = _swagger_page("2").encode()
            ctype = "text/html; charset=utf-8"
        elif path == "/spec/v1.json":
            try:
                body = (DATA / "openapi-v1.json").read_bytes()
                ctype = "application/json"
            except FileNotFoundError:
                self._send(404, b"Not found", "text/plain")
                return
        elif path == "/spec/v2.json":
            try:
                body = (DATA / "openapi-v2.json").read_bytes()
                ctype = "application/json"
            except FileNotFoundError:
                self._send(404, b"Not found", "text/plain")
                return
        else:
            self._send(404, b"Not found", "text/plain")
            return

        self._send(200, body, ctype)

    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):
        pass


if __name__ == "__main__":
    print("Scoreboard:  http://localhost:8080")
    print("API v1 docs: http://localhost:8080/api/v1")
    print("API v2 docs: http://localhost:8080/api/v2")
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
