import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BOARD = Path("scoreboard.json")
DATA = Path(__file__).parent / "data"

LEVEL_META = {
    "L1 Contract review": ("L1", 20),
    "L2 Test design": ("L2", 25),
    "L3 Incident diagnosis": ("L3", 30),
    "L4 Migration": ("L4", 25),
}


# ── Navigation bar (shared across pages) ─────────────────────────────────────

def _nav(active: str = "/") -> str:
    links = [("/", "Progress"), ("/guide", "Getting Started"), ("/api/v1", "API v1"), ("/api/v2", "API v2")]
    items = "".join(
        f'<a data-path="{href}"{" class=\"active\"" if href == active else ""}>{label}</a>'
        for href, label in links
    )
    # navBase() detects the app's URL prefix regardless of how it is served:
    #   direct localhost:8081 → base = "/"
    #   nginx /scoreboard/ prefix → base = "/scoreboard/"
    #   VS Code /proxy/8081/ forwarding → base = "/proxy/8081/"
    # It strips any known page suffix from the path to find the root.
    fix = (
        "<script>"
        "function navBase(){"
        "var p=window.location.pathname;"
        "var K=['/guide','/api/v1','/api/v2'];"
        "for(var i=0;i<K.length;i++){"
        "if(p.slice(-K[i].length)===K[i])"
        "return p.slice(0,p.length-K[i].length+1)||'/';"
        "}"
        "return p.endsWith('/')?p:p+'/';"
        "}"
        "(function(){"
        "var b=navBase();"
        "document.querySelectorAll('nav a[data-path]').forEach(function(a){"
        "var dp=a.getAttribute('data-path');"
        "var base=dp==='/'?b:b+dp.slice(1);"
        "a.href=base+'?v='+Date.now();"
        "});"
        "})();"
        "</script>"
    )
    return (
        '<nav>'
        '<span class="brand">Workshop</span>'
        f'{items}'
        '</nav>'
        + fix
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
    .notice{{background:#1e3a5f;color:#93c5fd;font-size:.82rem;padding:10px 24px;
             border-bottom:1px solid #2563eb;display:flex;align-items:center;gap:8px}}
    .notice strong{{color:#bfdbfe}}
  </style>
</head>
<body>
  {_nav(f"/api/v{version}")}
  <div class="notice">
    <span>ℹ️</span>
    <span><strong>Reference only</strong> — this API is not running.
    Use the spec below to understand which endpoints exist,
    then verify AI findings against it in <code>workshop.py</code>.
    "Try it out" will not work.</span>
  </div>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({{
      url: navBase()+"spec/v{version}.json",
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
    entries.sort(key=lambda e: e["team"].lower())
    max_score = sum(lmax for _, lmax in LEVEL_META.values())

    rows = ""
    for idx, entry in enumerate(entries):
        team = html.escape(entry["team"])
        score = entry["score"]
        pct = round(score / max_score * 100) if max_score else 0
        updated = entry.get("updated", "")[:16].replace("T", " ") + " UTC"
        checks = entry.get("checks", [])

        # Mini progress bars for each level
        bars = ""
        for lname, (lshort, lmax) in LEVEL_META.items():
            pts = entry["levels"].get(lname, 0)
            lpct = round(pts / lmax * 100) if lmax else 0
            bars += (
                f'<div class="lb">'
                f'<span class="lb-key">{lshort}</span>'
                f'<div class="lb-track"><div class="lb-fill" style="width:{lpct}%"></div></div>'
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
                    items += (
                        f'<div class="dc {cls}">'
                        f'{icon} {html.escape(c["name"])}'
                        f' <span class="dpts">{c["earned"]}/{c["max"]}</span>'
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
<tr class="tr" onclick="toggle(this)" data-id="d{idx}">
  <td class="tname">{team}</td>
  <td class="tprogress">
    <div class="pct-val">{pct}%</div>
    <div class="pbar-wrap"><div class="pbar-fill" style="width:{pct}%"></div></div>
  </td>
  <td class="tbars">{bars}</td>
  <td class="tup">{updated}</td>
  <td class="tarrow">▶</td>
</tr>
<tr id="d{idx}" class="detail-row" style="display:none">
  <td colspan="5" class="detail-cell">
    <div class="detail-inner">{detail_inner}</div>
  </td>
</tr>"""

    if not rows:
        rows = (
            '<tr><td colspan="5" class="empty">'
            'No progress yet — run <code>python score.py --all</code> or '
            '<code>python score.py --team "Your Team"</code>'
            '</td></tr>'
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta http-equiv="refresh" content="30">
  <title>API Workshop – Progress Dashboard</title>
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
    .tname{{font-weight:600}}
    .tprogress{{min-width:110px}}
    .pct-val{{font-size:1.1rem;font-weight:700;color:var(--accent);margin-bottom:4px}}
    .pbar-wrap{{background:#0f172a;border-radius:999px;height:6px;border:1px solid var(--border);overflow:hidden;min-width:80px}}
    .pbar-fill{{height:100%;border-radius:999px;background:var(--accent)}}
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
    .detail-inner{{padding:16px 20px 20px 40px;background:#090f1a;border-bottom:1px solid var(--border)}}
    .dcheck-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}}
    .dg{{display:flex;flex-direction:column;gap:5px}}
    .dg-title{{font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;
               color:var(--sub);font-weight:600;margin-bottom:2px}}
    .dc{{padding:7px 11px;border-radius:6px;font-size:.83rem;line-height:1.4}}
    .dp{{background:#0c2a1a;border:1px solid #166534}}
    .df{{background:#2a0c0c;border:1px solid #7f1d1d}}
    .dpts{{font-weight:700;color:var(--sub);margin-left:4px}}
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
      var saved = JSON.parse(sessionStorage.getItem("open") || "[]");
      if (open) {{ saved = saved.filter(function(x){{ return x !== id; }}); }}
      else if (!saved.includes(id)) {{ saved.push(id); }}
      sessionStorage.setItem("open", JSON.stringify(saved));
    }}
    document.addEventListener("DOMContentLoaded", function() {{
      var saved = JSON.parse(sessionStorage.getItem("open") || "[]");
      saved.forEach(function(id) {{
        var det = document.getElementById(id);
        if (!det) return;
        det.style.display = "table-row";
        var row = det.previousElementSibling;
        if (row) row.classList.add("open");
      }});
    }});
  </script>
</head>
<body>
  {_nav("/")}
  <div class="wrap">
    <h1>Workshop Progress</h1>
    <p class="sub">Click any row to expand per-check detail. Auto-refreshes every 30 s.</p>
    <table>
      <thead>
        <tr>
          <th>Team</th><th>Progress</th>
          <th>Level breakdown</th><th>Last updated</th><th></th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
</body>
</html>"""


# ── Getting-started guide ─────────────────────────────────────────────────────

def _guide_page() -> str:
    # Uses placeholder substitution to avoid f-string brace escaping in CSS/JS.
    nav_css = _NAV_CSS
    nav_bar = _nav("/guide")
    return _GUIDE_TEMPLATE.replace("<<<NAV_CSS>>>", nav_css).replace("<<<NAV>>>", nav_bar)


_GUIDE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>API Workshop — Getting Started</title>
  <style>
    <<<NAV_CSS>>>
    :root{--bg:#0f172a;--card:#1e293b;--border:#334155;--text:#f1f5f9;--sub:#94a3b8;--accent:#3b82f6;--green:#22c55e}
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:system-ui,-apple-system,sans-serif;background:var(--bg);color:var(--text);min-height:100vh}
    .wrap{max-width:800px;margin:0 auto;padding:32px 20px}
    h1{font-size:1.4rem;font-weight:700;margin-bottom:4px}
    .sub{color:var(--sub);font-size:.88rem;margin-bottom:24px}
    .progress{display:flex;gap:6px;align-items:center;margin-bottom:22px}
    .dot{width:9px;height:9px;border-radius:50%;background:var(--border);transition:background .25s;flex-shrink:0}
    .dot.active{background:var(--accent)}
    .dot.done{background:var(--green)}
    .prog-label{font-size:.8rem;color:var(--sub);margin-left:10px}
    .term{background:#020817;border:1px solid var(--border);border-radius:10px;overflow:hidden;margin-bottom:18px}
    .tbar{background:#1e293b;padding:9px 14px;display:flex;gap:7px;align-items:center;border-bottom:1px solid var(--border)}
    .tc{width:11px;height:11px;border-radius:50%}
    .tc-r{background:#ef4444}.tc-y{background:#f59e0b}.tc-g{background:#22c55e}
    .ttitle{font-size:.73rem;color:var(--sub);margin-left:6px}
    .tbody{padding:16px 20px;font-family:"SF Mono",Monaco,Consolas,monospace;font-size:.8rem;line-height:1.75;min-height:200px;max-height:340px;overflow-y:auto;color:#e2e8f0;white-space:pre-wrap;word-break:break-word}
    .p{color:var(--green)}
    .c{color:#f1f5f9}
    .o{color:#94a3b8}
    .cursor{display:inline-block;width:7px;height:.9em;background:var(--accent);vertical-align:text-bottom;animation:blink .75s step-end infinite}
    @keyframes blink{0%,100%{opacity:1}50%{opacity:0}}
    .stitle{font-size:1.05rem;font-weight:600;margin-bottom:6px}
    .shint{color:var(--sub);font-size:.88rem;line-height:1.6;margin-bottom:22px}
    .nav{display:flex;gap:10px;align-items:center}
    .btn{padding:8px 18px;border-radius:7px;border:none;font-size:.88rem;font-weight:500;cursor:pointer;transition:opacity .15s}
    .btn:disabled{opacity:.3;cursor:not-allowed}
    .bs{background:var(--card);color:var(--text);border:1px solid var(--border)}
    .bp{background:var(--accent);color:#fff}
    .bs:not(:disabled):hover{background:#253347}
    .bp:not(:disabled):hover{opacity:.85}
    .sc{color:var(--sub);font-size:.82rem;margin-left:auto}
  </style>
</head>
<body>
  <<<NAV>>>
  <div class="wrap">
    <h1>Getting Started</h1>
    <p class="sub">Follow these steps to complete the workshop. Use ← → arrow keys to navigate.</p>
    <div class="progress" id="prog"></div>
    <div class="term">
      <div class="tbar">
        <div class="tc tc-r"></div><div class="tc tc-y"></div><div class="tc tc-g"></div>
        <span class="ttitle">bash — /environment/api-ai-hackathon-public</span>
      </div>
      <div class="tbody" id="term"></div>
    </div>
    <div class="stitle" id="stitle"></div>
    <div class="shint" id="shint"></div>
    <div class="nav">
      <button class="btn bs" id="bprev" onclick="go(-1)">&#8592; Previous</button>
      <button class="btn bp" id="bnext" onclick="go(1)">Next &#8594;</button>
      <span class="sc" id="sc"></span>
    </div>
  </div>
<script>
const S=[
  {title:"1 — Set up your environment",
   hint:"In AWS Workshop Studio, activate the pre-built venv (that path only exists there). On your own machine you do not need it — use Python 3.10+ and install boto3. A local venv is optional.",
   lines:[
    {k:"out",v:"# AWS Workshop Studio only"},
    {k:"cmd",v:"source /environment/.venv/bin/activate"},
    {k:"cmd",v:"cd /environment/api-ai-hackathon-public"},
    {k:"out",v:"# Personal machine — clone of the team fork"},
    {k:"cmd",v:"cd api-ai-hackathon-public"},
    {k:"cmd",v:"pip install boto3"},
  ]},
  {title:"2 — Start the interactive assistant",
   hint:"python interact.py opens an AI-powered menu. It shows which functions you have started and lets you explore each level with real AI feedback.",
   lines:[
    {k:"cmd",v:"python interact.py"},
    {k:"out",v:`════════════════════════════════════════════════
   API AI Workshop — Interactive Assistant
   Functions started: 0/4
════════════════════════════════════════════════

   Which level do you want to work on?

     1  Contract review       [    ]  0/1 started
     2  Negative tests        [    ]  0/1 started
     3  Incident response     [    ]  0/1 started
     4  Migration review      [    ]  0/1 started

     q  Quit

   Enter a number: `},
  ]},
  {title:"3 — Pick a level",
   hint:"Type a number to enter a level. The AI streams its findings — some may be hallucinations. Your job is to find which ones.",
   lines:[
    {k:"inp",v:"1"},
    {k:"out",v:`
   The AI reviewed the OpenAPI v1 spec. Keep only
   findings whose path and method exist in the spec.

  [not started]  review_contract

──────────────────────────────────────────────
  Level 1 — Contract review
──────────────────────────────────────────────

I found four potential issues in this API contract:

[
  {"id":"AUTH-001",      "path":"/orders",    "method":"get"},
  {"id":"PAGE-001",      "path":"/orders",    "method":"get"},
  {"id":"ERR-001",       "path":"/orders",    "method":"post"},
  {"id":"HALLUCINATION", "path":"/customers", "method":"delete"}
]`},
  ]},
  {title:"4 — Ask the AI for help",
   hint:"You can ask anything about the current level. The AI will guide you without giving away the answer. Type a level number (1–4) to switch levels at any time.",
   lines:[
    {k:"you",v:"how do I check if an endpoint exists in the spec?"},
    {k:"out",v:`
AI: Check spec["paths"]. If the path is not a key
    in that dict, the endpoint does not exist.

    For each finding, verify both:
      path   in spec["paths"]
      method in spec["paths"][path]

    If either check fails, remove the finding.`},
  ]},
  {title:"5 — Edit workshop.py",
   hint:"Add your verification logic to the relevant function. This is the only file you need to edit. Each function corresponds to one level.",
   lines:[
    {k:"out",v:`# api_hackathon/workshop.py — Level 1

def review_contract(spec: dict, ai) -> list[dict]:
    findings = ai.ask("contract_review", spec)

    verified = []
    for f in findings:
        path   = f.get("path", "")
        method = f.get("method", "")
        if (path in spec["paths"] and
                method in spec["paths"][path]):
            verified.append(f)
    return verified`},
  ]},
  {title:"6 — Check your progress",
   hint:"Run the scorer any time. It opens an HTML report in your browser showing exactly which checks passed or failed.",
   lines:[
    {k:"cmd",v:'python score.py --team "Team Alpha" --open'},
    {k:"out",v:`Team Alpha: 20/100
  L1 Contract review: 20
  L2 Test design: 0
  L3 Incident diagnosis: 0
  L4 Migration: 0
  report → report.html`},
  ]},
  {title:"7 — Jump between levels",
   hint:"From within any level's chat, type a level number to switch directly. You can work on levels in any order.",
   lines:[
    {k:"you",v:"2"},
    {k:"out",v:`
   Some tests target endpoints that do not exist.
   Your job: keep only tests whose path and method
   exist in the spec.

  [not started]  design_negative_tests

──────────────────────────────────────────────
  Level 2 — Negative tests
──────────────────────────────────────────────`},
  ]},
  {title:"8 — Track your progress",
   hint:"Type 'done' to return to the menu. The menu re-reads workshop.py each time, so it always shows your latest progress.",
   lines:[
    {k:"you",v:"done"},
    {k:"out",v:`
════════════════════════════════════════════════
   API AI Workshop — Interactive Assistant
   Functions started: 1/4
════════════════════════════════════════════════

   Which level do you want to work on?

     1  Contract review       [done]  1/1 started
     2  Negative tests        [    ]  0/1 started
     3  Incident response     [    ]  0/1 started
     4  Migration review      [    ]  0/1 started

   Enter a number: `},
  ]},
];

let cur=0, gen=0;

function mkProg(){
  var el=document.getElementById("prog");
  var dots="";
  for(var i=0;i<S.length;i++) dots+='<div class="dot" id="d'+i+'"></div>';
  el.innerHTML=dots+'<span class="prog-label" id="pl"></span>';
}
function updProg(){
  for(var i=0;i<S.length;i++){
    var d=document.getElementById("d"+i);
    d.className="dot"+(i<cur?" done":i===cur?" active":"");
  }
  document.getElementById("pl").textContent="Step "+(cur+1)+" of "+S.length;
  document.getElementById("sc").textContent=(cur+1)+" / "+S.length;
}
function setNav(ok){
  document.getElementById("bprev").disabled=(cur===0);
  document.getElementById("bnext").disabled=!ok;
  document.getElementById("bnext").textContent=cur===S.length-1?"Done ✓":"Next →";
}
function esc(s){return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}

function showStep(idx){
  gen++;
  var myGen=gen;
  var s=S[idx];
  document.getElementById("stitle").textContent=s.title;
  document.getElementById("shint").textContent=s.hint;
  setNav(false);
  var term=document.getElementById("term");
  term.innerHTML="";
  var cursor=document.createElement("span");
  cursor.className="cursor";
  term.appendChild(cursor);
  updProg();
  runLine(s.lines,0,term,cursor,myGen);
}

function runLine(lines,i,term,cursor,myGen){
  if(myGen!==gen) return;
  if(i>=lines.length){ setNav(true); return; }
  var ln=lines[i];
  function next(){ runLine(lines,i+1,term,cursor,myGen); }
  if(ln.k==="cmd"||ln.k==="inp"||ln.k==="you"){
    var row=document.createElement("div");
    var lbl=ln.k==="you"?"You: ":"$ ";
    row.innerHTML='<span class="p">'+esc(lbl)+'</span><span class="c"></span>';
    term.insertBefore(row,cursor);
    var tt=row.querySelector(".c");
    var spd=ln.k==="cmd"?14:28;
    typeChars(tt,ln.v,0,spd,myGen,function(){ setTimeout(next,140); });
  } else {
    setTimeout(function(){
      if(myGen!==gen) return;
      var row=document.createElement("div");
      row.className="o"; row.textContent=ln.v;
      term.insertBefore(row,cursor);
      term.scrollTop=term.scrollHeight;
      setTimeout(next,150);
    },80);
  }
}

function typeChars(el,text,i,speed,myGen,done){
  if(myGen!==gen) return;
  el.textContent=text.slice(0,i);
  if(i>=text.length){ done(); return; }
  setTimeout(function(){ typeChars(el,text,i+1,speed,myGen,done); },speed);
}

function go(dir){
  if(dir>0&&cur===S.length-1) return;
  if(dir<0&&cur===0) return;
  cur=Math.max(0,Math.min(S.length-1,cur+dir));
  showStep(cur);
}
document.addEventListener("keydown",function(e){
  if(e.key==="ArrowRight"||e.key==="Enter") go(1);
  if(e.key==="ArrowLeft") go(-1);
});
mkProg(); showStep(0);
</script>
</body>
</html>"""


# ── HTTP handler ──────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]

        if path == "/":
            body = _board_page().encode()
            ctype = "text/html; charset=utf-8"
        elif path == "/guide":
            body = _guide_page().encode()
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
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):
        pass


if __name__ == "__main__":
    import argparse as _ap
    _p = _ap.ArgumentParser()
    _p.add_argument("--port", type=int, default=8081)
    _port = _p.parse_args().port
    print(f"Scoreboard:      http://localhost:{_port}")
    print(f"Getting started: http://localhost:{_port}/guide")
    print(f"API v1 docs:     http://localhost:{_port}/api/v1")
    print(f"API v2 docs:     http://localhost:{_port}/api/v2")
    ThreadingHTTPServer(("0.0.0.0", _port), Handler).serve_forever()
