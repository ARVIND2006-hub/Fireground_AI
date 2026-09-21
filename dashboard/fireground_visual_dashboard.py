#!/usr/bin/env python3
"""
Fireground AI - Visual Dashboard
No Streamlit/Flask required.

Run:
    python3 dashboard/fireground_visual_dashboard.py

The dashboard reads:
    results/live_vnnx_fireground_result.json

and serves a local browser dashboard at:
    http://127.0.0.1:8765
"""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import json
import html
import os
import subprocess
import webbrowser

PROJECT = Path("/mnt/c/Users/Asus/Fireground_AI")
RESULT_FILE = PROJECT / "results/live_vnnx_fireground_result.json"
HOST = "127.0.0.1"
PORT = 8765
REFRESH_SECONDS = 2


def load_results():
    if not RESULT_FILE.exists():
        return None
    with RESULT_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def esc(value):
    return html.escape(str(value))


def cls(status):
    return {"NORMAL": "normal", "ELEVATED": "elevated", "HIGH": "high"}.get(str(status).upper(), "normal")


def confidence(value):
    try:
        return f"{max(0.0, min(1.0, float(value))) * 100:.1f}%"
    except Exception:
        return "—"


def render(data):
    if data is None:
        body = """
        <main class="empty">
          <div>
            <div class="spinner"></div>
            <h2>Waiting for Fireground AI results</h2>
            <p>Run <code>python3 src/live_vnnx_fireground_system.py</code>
            in the project terminal.</p>
          </div>
        </main>
        """
        return page("Fireground AI Visual Dashboard", body)

    stats = data.get("window_statistics", {})
    results = data.get("results", [])
    latest = results[-1] if results else {}
    ai = latest.get("ai_prediction", {})
    risk = latest.get("risk", {})
    zone = latest.get("zone", {})
    status = str(data.get("overall_status", "UNKNOWN")).upper()

    scores = [int(r.get("risk", {}).get("risk_score", 0)) for r in results]
    max_score = max(scores) if scores else 0

    # SVG risk timeline.
    W, H = 1000, 270
    L, R, T, B = 48, 24, 24, 40
    PW, PH = W-L-R, H-T-B
    n = len(results)
    bars = []
    points = []
    if n:
        for i, row in enumerate(results):
            x = L if n == 1 else L + PW * i / (n-1)
            s = int(row.get("risk", {}).get("risk_score", 0))
            y = T + PH - min(s, 5) / 5 * PH
            bar_w = max(2.5, PW / n - 1.2)
            y0 = T + PH
            bars.append(
                f'<rect class="bar {cls(row.get("risk", {}).get("local_status","NORMAL"))}" '
                f'x="{x-bar_w/2:.1f}" y="{y:.1f}" width="{bar_w:.1f}" '
                f'height="{y0-y:.1f}" rx="2"/>'
            )
            points.append(f"{x:.1f},{y:.1f}")
    grid = []
    for s in range(6):
        y = T + PH - s/5*PH
        grid.append(f'<line class="grid" x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}"/>')
        grid.append(f'<text class="axis" x="12" y="{y+4:.1f}">{s}</text>')
    xlabels = ""
    if n:
        xlabels = (
            f'<text class="axis" x="{L}" y="{H-10}">Window 1</text>'
            f'<text class="axis" x="{W-R-70}" y="{H-10}">Window {n}</text>'
        )
    timeline = (
        f'<svg viewBox="0 0 {W} {H}" aria-label="Risk score timeline">'
        + "".join(grid)
        + "".join(bars)
        + (f'<polyline class="line" points="{" ".join(points)}"/>' if points else "")
        + xlabels
        + "</svg>"
    )

    recent = []
    for row in results[-10:]:
        r_ai = row.get("ai_prediction", {})
        r_risk = row.get("risk", {})
        recent.append(
            "<tr>"
            f"<td>{esc(row.get('window',''))}</td>"
            f"<td>{esc(row.get('timestamp',''))}</td>"
            f"<td>{esc(r_ai.get('activity',''))}</td>"
            f"<td>{esc(r_ai.get('physiological_state',''))}</td>"
            f"<td>{esc(r_ai.get('environment',''))}</td>"
            f"<td>{esc(r_risk.get('risk_score',''))}</td>"
            f"<td><span class='pill {cls(r_risk.get('local_status','NORMAL'))}'>{esc(r_risk.get('local_status',''))}</span></td>"
            "</tr>"
        )

    body = f"""
    <div class="topbar">
      <div>
        <div class="eyebrow">MICROCHIP VECTORBLOX • VNNX SOFTWARE SIMULATION</div>
        <h1>Fireground AI <span>Visual Dashboard</span></h1>
      </div>
      <div class="tools">
        <button onclick="location.reload()">Refresh</button>
        <span class="live"><i></i> AUTO REFRESH {REFRESH_SECONDS}s</span>
      </div>
    </div>

    <section class="hero">
      <article class="card status-card {cls(status)}">
        <div class="label">OVERALL STATUS</div>
        <div class="status">{esc(status)}</div>
        <div class="muted">Alert priority: <b>{esc({"NORMAL":"LOW","ELEVATED":"MEDIUM","HIGH":"HIGH"}.get(status,"—"))}</b></div>
      </article>

      <article class="card gauge-card">
        <div class="label">MAX RISK SCORE</div>
        <div class="gauge" style="--p:{min(max_score,5)/5*100:.0f}%">
          <div class="gauge-inner"><strong>{max_score}</strong><span>/ 5</span></div>
        </div>
      </article>

      <article class="card meta-card">
        <div class="label">LATEST WINDOW</div>
        <div class="latest">Window {esc(latest.get("window","—"))} • {esc(latest.get("timestamp","—"))}</div>
        <div class="row"><span>Firefighter</span><b>{esc(data.get("firefighter","—"))}</b></div>
        <div class="row"><span>Zone</span><b>{esc(zone.get("zone_id","—"))}</b></div>
        <div class="row"><span>Event</span><b>{esc(risk.get("event_type","—"))}</b></div>
      </article>
    </section>

    <section class="stats">
      <div class="card stat"><strong>{data.get("sensor_samples",0)}</strong><span>Sensor Samples</span></div>
      <div class="card stat"><strong>{data.get("ai_windows_processed",0)}</strong><span>AI Windows</span></div>
      <div class="card stat normal"><strong>{stats.get("normal",0)}</strong><span>Normal</span></div>
      <div class="card stat elevated"><strong>{stats.get("elevated",0)}</strong><span>Elevated</span></div>
      <div class="card stat high"><strong>{stats.get("high",0)}</strong><span>High</span></div>
    </section>

    <section class="card panel">
      <div class="panel-head">
        <div><div class="label">LATEST MODEL OUTPUT</div><h2>Multitask AI Prediction</h2></div>
        <span class="muted">VNNX confidence</span>
      </div>
      <div class="pred-grid">
        <div class="pred"><span class="icon">A</span><div><small>ACTIVITY</small><strong>{esc(ai.get("activity","—"))}</strong></div><em>{confidence(ai.get("activity_confidence",0))}</em></div>
        <div class="pred"><span class="icon">P</span><div><small>PHYSIOLOGY</small><strong>{esc(ai.get("physiological_state","—"))}</strong></div><em>{confidence(ai.get("physiological_confidence",0))}</em></div>
        <div class="pred"><span class="icon">E</span><div><small>ENVIRONMENT</small><strong>{esc(ai.get("environment","—"))}</strong></div><em>{confidence(ai.get("environment_confidence",0))}</em></div>
      </div>
    </section>

    <section class="card panel">
      <div class="panel-head">
        <div><div class="label">RISK PROGRESSION</div><h2>Risk Score Across Sliding Windows</h2></div>
        <div class="legend"><span><i class="lg normal"></i>Normal</span><span><i class="lg elevated"></i>Elevated</span><span><i class="lg high"></i>High</span></div>
      </div>
      <div class="chart">{timeline}</div>
    </section>

    <section class="card panel">
      <div class="label">RECENT INFERENCE HISTORY</div>
      <h2>Latest 10 AI Windows</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>WIN</th><th>TIME</th><th>ACTIVITY</th><th>PHYSIOLOGY</th><th>ENV</th><th>SCORE</th><th>STATUS</th></tr></thead>
          <tbody>{"".join(recent)}</tbody>
        </table>
      </div>
    </section>

    <footer>
      <span><b>Model:</b> fireground_v2_V250_ncomp.vnnx</span>
      <span><b>Engine:</b> {esc(data.get("inference_engine",""))}</span>
      <span><b>Target:</b> Microchip PolarFire SoC Icicle Kit</span>
    </footer>
    """
    return page("Fireground AI Visual Dashboard", body)


def page(title, body):
    return f"""<!doctype html>
<html><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="{REFRESH_SECONDS}">
<title>{html.escape(title)}</title>
<style>
:root{{--bg:#08101f;--panel:#101a2e;--panel2:#0c1527;--border:#263554;--text:#eef4ff;--muted:#8e9bb5;--cyan:#5ed7ff;--green:#4fe0a0;--amber:#ffd166;--red:#ff6678}}
*{{box-sizing:border-box}} body{{margin:0;background:linear-gradient(180deg,#060a14,#08101f 45%,#07101d);color:var(--text);font-family:Segoe UI,Inter,Arial,sans-serif}}
.container{{max-width:1320px;margin:auto;padding:28px}} .topbar{{display:flex;justify-content:space-between;gap:20px;align-items:flex-start;margin-bottom:20px}}
.eyebrow,.label,small{{font-size:11px;letter-spacing:.12em;font-weight:800;color:var(--muted)}} h1{{margin:7px 0 0;font-size:34px}} h1 span{{color:var(--cyan);font-weight:600}} h2{{margin:6px 0 16px;font-size:21px}}
.tools{{display:flex;gap:12px;align-items:center}} button{{background:#162541;color:var(--text);border:1px solid var(--border);padding:10px 14px;border-radius:9px;cursor:pointer}} button:hover{{border-color:var(--cyan)}}
.live{{font-size:11px;color:var(--muted)}} .live i{{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--green);margin-right:6px}}
.hero{{display:grid;grid-template-columns:1.4fr .8fr 1fr;gap:15px}} .card{{background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid var(--border);border-radius:16px;box-shadow:0 15px 45px rgba(0,0,0,.18)}}
.status-card{{padding:23px;min-height:188px}} .status{{font-size:58px;font-weight:900;margin:18px 0 5px}} .status-card.normal{{border-color:rgba(79,224,160,.45)}} .status-card.elevated{{border-color:rgba(255,209,102,.55)}} .status-card.high{{border-color:rgba(255,102,120,.6)}}
.status-card.normal .status{{color:var(--green)}} .status-card.elevated .status{{color:var(--amber)}} .status-card.high .status{{color:var(--red)}} .muted{{color:var(--muted);font-size:12px}}
.gauge-card{{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:20px}} .gauge{{width:145px;height:145px;border-radius:50%;background:conic-gradient(var(--cyan) var(--p),#1e2b48 0);display:grid;place-items:center;margin-top:9px}}
.gauge-inner{{width:108px;height:108px;border-radius:50%;background:var(--panel);display:flex;flex-direction:column;align-items:center;justify-content:center}} .gauge-inner strong{{font-size:38px}} .gauge-inner span{{color:var(--muted);font-size:12px}}
.meta-card{{padding:22px}} .latest{{font-size:22px;font-weight:700;margin:17px 0}} .row{{display:flex;justify-content:space-between;padding:9px 0;border-bottom:1px solid var(--border);color:var(--muted)}} .row b{{color:var(--text)}}
.stats{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:15px 0}} .stat{{padding:17px}} .stat strong{{display:block;font-size:33px}} .stat span{{display:block;color:var(--muted);font-size:11px;margin-top:3px;text-transform:uppercase;letter-spacing:.1em;font-weight:700}} .stat.normal strong{{color:var(--green)}} .stat.elevated strong{{color:var(--amber)}} .stat.high strong{{color:var(--red)}}
.panel{{padding:22px;margin-top:15px}} .panel-head{{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin-bottom:18px}}
.pred-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}} .pred{{display:grid;grid-template-columns:42px 1fr auto;gap:12px;align-items:center;padding:16px;background:#0a1325;border:1px solid var(--border);border-radius:13px}}
.icon{{width:40px;height:40px;border-radius:11px;background:#172842;color:var(--cyan);display:grid;place-items:center;font-weight:900}} .pred strong{{display:block;font-size:20px;margin-top:5px}} .pred em{{font-style:normal;color:var(--cyan);font-weight:800}}
.chart{{background:#091223;border:1px solid var(--border);border-radius:12px;padding:10px;overflow:hidden}} svg{{width:100%;display:block}} .grid{{stroke:#22304a;stroke-width:1}} .axis{{fill:#68758f;font-size:11px}} .bar.normal{{fill:rgba(79,224,160,.38)}} .bar.elevated{{fill:rgba(255,209,102,.40)}} .bar.high{{fill:rgba(255,102,120,.44)}} .line{{fill:none;stroke:var(--cyan);stroke-width:2.2;stroke-linejoin:round;stroke-linecap:round}}
.legend{{display:flex;gap:15px;color:var(--muted);font-size:12px}} .lg{{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:5px}} .lg.normal{{background:var(--green)}} .lg.elevated{{background:var(--amber)}} .lg.high{{background:var(--red)}}
.table-wrap{{overflow:auto;border:1px solid var(--border);border-radius:12px;margin-top:14px}} table{{width:100%;border-collapse:collapse;min-width:760px}} th,td{{padding:11px 12px;border-bottom:1px solid var(--border);text-align:left;font-size:13px}} th{{font-size:10px;color:var(--muted);letter-spacing:.1em}} tr:last-child td{{border-bottom:0}}
.pill{{padding:5px 8px;border-radius:999px;font-weight:800;font-size:11px}} .pill.normal{{background:rgba(79,224,160,.1);color:var(--green)}} .pill.elevated{{background:rgba(255,209,102,.1);color:var(--amber)}} .pill.high{{background:rgba(255,102,120,.1);color:var(--red)}}
footer{{display:flex;gap:20px;flex-wrap:wrap;color:var(--muted);font-size:12px;padding:18px 2px}} footer b{{color:var(--text)}} .empty{{min-height:60vh;display:grid;place-items:center;text-align:center}} .spinner{{width:35px;height:35px;border:3px solid #22304a;border-top-color:var(--cyan);border-radius:50%;animation:spin 1s linear infinite;margin:auto}} .empty h2{{margin-top:20px}} code{{color:var(--cyan)}} @keyframes spin{{to{{transform:rotate(360deg)}}}}
@media(max-width:900px){{.hero{{grid-template-columns:1fr}}.stats{{grid-template-columns:repeat(2,1fr)}}.pred-grid{{grid-template-columns:1fr}}.topbar,.panel-head{{flex-direction:column;align-items:flex-start}}}}
</style></head>
<body><div class="container">{body}</div></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if urlparse(self.path).path not in ("/", "/index.html"):
            self.send_response(404)
            self.end_headers()
            return
        try:
            content = render(load_results()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(content)
        except Exception as exc:
            content = f"<pre>{html.escape(str(exc))}</pre>".encode()
            self.send_response(500)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

    def log_message(self, format, *args):
        pass


def main():
    url = f"http://{HOST}:{PORT}"
    print("=" * 64)
    print("FIREGROUND AI — VISUAL DASHBOARD")
    print("=" * 64)
    print(f"Results file : {RESULT_FILE}")
    print(f"Dashboard URL: {url}")
    print(f"Auto refresh : {REFRESH_SECONDS}s")
    print("Press Ctrl+C to stop.")

    server = ThreadingHTTPServer((HOST, PORT), Handler)

    try:
        if os.path.exists("/mnt/c/Windows/explorer.exe"):
            subprocess.Popen(["explorer.exe", url])
        else:
            webbrowser.open(url)
    except Exception:
        print("Open the URL manually in your Windows browser.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
