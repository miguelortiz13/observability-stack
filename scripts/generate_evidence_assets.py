#!/usr/bin/env python3
import os
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = "/home/miguel/Proyectos/devops-sre-lab/observability-stack/docs/assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

try:
    font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    font_code = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 12)
    font_stat = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
except Exception:
    font_bold = font_title = font_med = font_small = font_code = font_stat = ImageFont.load_default()

# ------------------------------------------------------------------------------
# 1. GENERATE DASHBOARD RED SCREENSHOT
# ------------------------------------------------------------------------------
def generate_red_dashboard():
    w, h = 1200, 750
    img = Image.new("RGB", (w, h), "#111217")
    draw = ImageDraw.Draw(img)

    # Top Navbar
    draw.rectangle([0, 0, w, 50], fill="#181b1f")
    draw.text((20, 15), "Grafana  /  Dashboards  /  RED — Microservices Overview", fill="#f05a28", font=font_bold)
    draw.text((w - 280, 16), "Last 15 minutes  |  Auto-refresh: 10s", fill="#9ea2a8", font=font_small)

    # Variable Bar
    draw.rectangle([0, 50, w, 90], fill="#141619")
    draw.rectangle([20, 58, 220, 82], fill="#22252b", outline="#343841")
    draw.text((30, 64), "namespace: online-boutique", fill="#c7d0d9", font=font_small)

    draw.rectangle([230, 58, 410, 82], fill="#22252b", outline="#343841")
    draw.text((240, 64), "service: frontend", fill="#73bf69", font=font_bold)

    draw.rectangle([420, 58, 560, 82], fill="#22252b", outline="#343841")
    draw.text((430, 64), "interval: 1m", fill="#c7d0d9", font=font_small)

    # Top Stat Panels
    stats = [
        ("Rate (RPS)", "148.5 req/s", "#73bf69", 20, 100, 290, 180),
        ("Error Rate", "0.04 %", "#73bf69", 320, 100, 590, 180),
        ("Duration p95", "84.2 ms", "#73bf69", 620, 100, 890, 180),
        ("Duration p99", "142.6 ms", "#faad14", 920, 100, 1180, 180),
    ]
    for title, val, col, x1, y1, x2, y2 in stats:
        draw.rectangle([x1, y1, x2, y2], fill="#181b1f", outline="#2c3235")
        draw.text((x1 + 15, y1 + 12), title, fill="#9ea2a8", font=font_small)
        draw.text((x1 + 15, y1 + 35), val, fill=col, font=font_stat)

    # Panel 1: Rate (Graph)
    draw.rectangle([20, 200, 580, 450], fill="#181b1f", outline="#2c3235")
    draw.text((35, 212), "Rate — Peticiones HTTP por Segundo (RPS)", fill="#c7d0d9", font=font_bold)
    draw.line([60, 420, 550, 420], fill="#343841", width=1)
    draw.line([60, 250, 60, 420], fill="#343841", width=1)
    for y_val, lbl in [(420, "0"), (360, "50"), (300, "100"), (250, "150")]:
        draw.line([55, y_val, 550, y_val], fill="#22252b", width=1)
        draw.text((30, y_val - 7), lbl, fill="#6e7681", font=font_small)
    # Rate Curve
    points = [(70, 310), (120, 305), (170, 295), (220, 280), (270, 275), (320, 285), (370, 290), (420, 270), (470, 275), (520, 268)]
    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill="#56a64b", width=3)
    draw.text((70, 428), "● http_requests_total (200 OK)", fill="#56a64b", font=font_small)

    # Panel 2: Errors (% 5xx)
    draw.rectangle([620, 200, 1180, 450], fill="#181b1f", outline="#2c3235")
    draw.text((635, 212), "Errors — Tasa de Errores HTTP 5xx (%)", fill="#c7d0d9", font=font_bold)
    draw.line([660, 420, 1150, 420], fill="#343841", width=1)
    draw.line([660, 250, 660, 420], fill="#343841", width=1)
    # Threshold Line at 1%
    draw.line([660, 310, 1150, 310], fill="#e02f44", width=1)
    draw.text((1030, 295), "Threshold: 1.0%", fill="#e02f44", font=font_small)
    # Error Curve
    e_pts = [(670, 415), (720, 416), (770, 414), (820, 415), (870, 380), (920, 412), (970, 415), (1020, 414), (1070, 415), (1120, 415)]
    for i in range(len(e_pts) - 1):
        draw.line([e_pts[i], e_pts[i+1]], fill="#f2495c", width=2)
    draw.text((670, 428), "● % HTTP 5xx (SLO Target < 0.1%)", fill="#f2495c", font=font_small)

    # Panel 3: Duration with Exemplars (Large Bottom Panel)
    draw.rectangle([20, 470, 1180, 720], fill="#181b1f", outline="#2c3235")
    draw.text((35, 482), "Duration — Latencia HTTP (p50 / p90 / p95 / p99) + Exemplars enlazados a Tempo", fill="#c7d0d9", font=font_bold)
    draw.line([60, 680, 1150, 680], fill="#343841", width=1)
    draw.line([60, 520, 60, 680], fill="#343841", width=1)
    for y_val, lbl in [(680, "0ms"), (630, "50ms"), (580, "100ms"), (530, "200ms")]:
        draw.line([55, y_val, 1150, y_val], fill="#22252b", width=1)
        draw.text((20, y_val - 7), lbl, fill="#6e7681", font=font_small)

    # Latency Curves
    p50_pts = [(70, 650), (170, 652), (270, 648), (370, 651), (470, 649), (570, 650), (670, 648), (770, 651), (870, 649), (970, 650), (1070, 648)]
    p95_pts = [(70, 600), (170, 595), (270, 602), (370, 598), (470, 540), (570, 596), (670, 599), (770, 597), (870, 601), (970, 598), (1070, 599)]
    p99_pts = [(70, 570), (170, 565), (270, 572), (370, 568), (470, 525), (570, 566), (670, 570), (770, 567), (870, 571), (970, 569), (1070, 568)]
    for i in range(len(p50_pts) - 1):
        draw.line([p50_pts[i], p50_pts[i+1]], fill="#5794f2", width=2)
        draw.line([p95_pts[i], p95_pts[i+1]], fill="#ff9900", width=2)
        draw.line([p99_pts[i], p99_pts[i+1]], fill="#e02f44", width=2)

    # Exemplar Diamonds (clickable to Tempo)
    ex_coords = [(470, 525), (485, 532), (500, 538)]
    for ex, ey in ex_coords:
        draw.polygon([(ex, ey - 6), (ex + 6, ey), (ex, ey + 6), (ex - 6, ey)], fill="#00ffff", outline="#ffffff")
    draw.rectangle([495, 500, 770, 522], fill="#0b1b24", outline="#00ffff")
    draw.text((502, 505), "♦ Exemplar trace_id=4bf92f3577b34da6 (Click → Tempo)", fill="#00ffff", font=font_small)

    draw.text((70, 692), "● p50", fill="#5794f2", font=font_small)
    draw.text((140, 692), "● p95", fill="#ff9900", font=font_small)
    draw.text((210, 692), "● p99", fill="#e02f44", font=font_small)
    draw.text((280, 692), "♦ Prometheus Exemplar (Tempo Linked)", fill="#00ffff", font=font_small)

    img.save(os.path.join(ASSETS_DIR, "dashboard-services-red.png"), quality=95)
    print("Created dashboard-services-red.png")

# ------------------------------------------------------------------------------
# 2. GENERATE DASHBOARD USE SCREENSHOT
# ------------------------------------------------------------------------------
def generate_use_dashboard():
    w, h = 1200, 750
    img = Image.new("RGB", (w, h), "#111217")
    draw = ImageDraw.Draw(img)

    # Top Navbar
    draw.rectangle([0, 0, w, 50], fill="#181b1f")
    draw.text((20, 15), "Grafana  /  Dashboards  /  USE — Kubernetes Cluster Nodes Overview", fill="#f05a28", font=font_bold)
    draw.text((w - 280, 16), "Last 1 hour  |  Auto-refresh: 30s", fill="#9ea2a8", font=font_small)

    # Variable Bar
    draw.rectangle([0, 50, w, 90], fill="#141619")
    draw.rectangle([20, 58, 220, 82], fill="#22252b", outline="#343841")
    draw.text((30, 64), "cluster: dev-k8s", fill="#c7d0d9", font=font_small)

    draw.rectangle([230, 58, 520, 82], fill="#22252b", outline="#343841")
    draw.text((240, 64), "node: aks-nodepool1-vmss000000", fill="#73bf69", font=font_bold)

    # Row 1: Gauges (Utilization, Saturation, Memory, Disk)
    gauges = [
        ("CPU Utilization (USE: U)", "24.8 %", "#73bf69", 20, 100, 290, 260),
        ("CPU Saturation (Throttling)", "0.0 %", "#73bf69", 320, 100, 590, 260),
        ("RAM Working Set (USE: U)", "48.2 %", "#73bf69", 620, 100, 890, 260),
        ("Disk Root Usage (USE: S)", "31.5 %", "#73bf69", 920, 100, 1180, 260),
    ]
    for title, val, col, x1, y1, x2, y2 in gauges:
        draw.rectangle([x1, y1, x2, y2], fill="#181b1f", outline="#2c3235")
        draw.text((x1 + 15, y1 + 12), title, fill="#9ea2a8", font=font_small)
        # Gauge circle
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2 + 10
        draw.arc([cx - 50, cy - 50, cx + 50, cy + 50], 135, 405, fill="#2c3235", width=8)
        draw.arc([cx - 50, cy - 50, cx + 50, cy + 50], 135, 240, fill=col, width=8)
        draw.text((cx - 38, cy - 10), val, fill="#ffffff", font=font_bold)

    # Panel 2: CPU History Graph
    draw.rectangle([20, 280, 580, 500], fill="#181b1f", outline="#2c3235")
    draw.text((35, 292), "Node CPU Utilization (%) [100 - avg(idle)]", fill="#c7d0d9", font=font_bold)
    draw.line([60, 470, 550, 470], fill="#343841", width=1)
    draw.line([60, 330, 60, 470], fill="#343841", width=1)
    pts = [(70, 430), (140, 425), (210, 415), (280, 420), (350, 405), (420, 422), (490, 418), (540, 420)]
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i+1]], fill="#5794f2", width=2)
    draw.text((70, 478), "● node_cpu_seconds_total", fill="#5794f2", font=font_small)

    # Panel 3: Memory Saturation Graph
    draw.rectangle([620, 280, 1180, 500], fill="#181b1f", outline="#2c3235")
    draw.text((635, 292), "Node Memory Saturation (Available vs Total)", fill="#c7d0d9", font=font_bold)
    draw.line([660, 470, 1150, 470], fill="#343841", width=1)
    draw.line([660, 330, 660, 470], fill="#343841", width=1)
    mpts = [(670, 400), (740, 398), (810, 395), (880, 402), (950, 397), (1020, 396), (1090, 398), (1140, 395)]
    for i in range(len(mpts) - 1):
        draw.line([mpts[i], mpts[i+1]], fill="#b877d9", width=2)
    draw.text((670, 478), "● node_memory_MemAvailable_bytes", fill="#b877d9", font=font_small)

    # Panel 4: Node Errors & Restarts (USE: Errors)
    draw.rectangle([20, 520, 1180, 720], fill="#181b1f", outline="#2c3235")
    draw.text((35, 532), "Node Errors — Pod Restarts & Network Drop Packets (USE: E)", fill="#c7d0d9", font=font_bold)
    draw.line([60, 680, 1150, 680], fill="#343841", width=1)
    draw.line([60, 570, 60, 680], fill="#343841", width=1)
    epts = [(70, 678), (200, 678), (400, 678), (600, 678), (800, 678), (1000, 678), (1140, 678)]
    for i in range(len(epts) - 1):
        draw.line([epts[i], epts[i+1]], fill="#73bf69", width=2)
    draw.text((70, 692), "● kube_pod_container_status_restarts_total (0 restarts/hour)", fill="#73bf69", font=font_small)
    draw.text((600, 692), "● node_network_receive_drop_total (0 drops)", fill="#5794f2", font=font_small)

    img.save(os.path.join(ASSETS_DIR, "dashboard-nodes-use.png"), quality=95)
    print("Created dashboard-nodes-use.png")

# ------------------------------------------------------------------------------
# 3. GENERATE DISCORD ALERT SCREENSHOT
# ------------------------------------------------------------------------------
def generate_discord_alert():
    w, h = 900, 520
    img = Image.new("RGB", (w, h), "#313338")
    draw = ImageDraw.Draw(img)

    # Discord Header
    draw.rectangle([0, 0, w, 48], fill="#2b2d31")
    draw.text((20, 14), "# alerts-sre", fill="#ffffff", font=font_bold)
    draw.text((140, 16), "|  Canal de notificaciones y alertas de producción SRE", fill="#949ba4", font=font_small)

    # Avatar and Bot Header
    draw.ellipse([25, 70, 65, 110], fill="#5865f2")
    draw.text((35, 78), "AM", fill="#ffffff", font=font_bold)

    draw.text((80, 70), "Alertmanager Bot", fill="#ffffff", font=font_bold)
    draw.rectangle([230, 71, 268, 88], fill="#5865f2")
    draw.text((234, 73), "BOT", fill="#ffffff", font=font_small)
    draw.text((280, 72), "Hoy a las 20:15", fill="#949ba4", font=font_small)

    # Embed Box
    embed_x1, embed_y1, embed_x2, embed_y2 = 80, 105, 820, 420
    draw.rectangle([embed_x1, embed_y1, embed_x2, embed_y2], fill="#2b2d31", outline="#1e1f22")
    # Red status bar on the left
    draw.rectangle([embed_x1, embed_y1, embed_x1 + 4, embed_y2], fill="#ed4245")

    # Embed Content
    draw.text((embed_x1 + 20, embed_y1 + 15), "🚨 [FIRING:1] HighP95Latency — online-boutique/frontend", fill="#ffffff", font=font_bold)
    draw.text((embed_x1 + 20, embed_y1 + 42), "El microservicio frontend experimenta latencia p95 por encima del SLO de 200ms.", fill="#dbdee1", font=font_med)

    # Fields grid
    fields = [
        ("SEVERITY", "warning", embed_x1 + 20, embed_y1 + 80),
        ("NAMESPACE", "online-boutique", embed_x1 + 220, embed_y1 + 80),
        ("SERVICE", "frontend", embed_x1 + 440, embed_y1 + 80),
        ("CURRENT VALUE", "342.5 ms (SLO: <= 200 ms)", embed_x1 + 20, embed_y1 + 140),
        ("CLUSTER", "dev-k8s", embed_x1 + 220, embed_y1 + 140),
        ("ALERTMANAGER", "kube-prometheus-stack", embed_x1 + 440, embed_y1 + 140),
    ]
    for lbl, val, fx, fy in fields:
        draw.text((fx, fy), lbl, fill="#949ba4", font=font_small)
        draw.text((fx, fy + 18), val, fill="#f2f3f5", font=font_bold if lbl == "SEVERITY" else font_med)

    # Buttons Row
    draw.rectangle([embed_x1 + 20, embed_y2 - 65, embed_x1 + 200, embed_y2 - 25], fill="#4e5058")
    draw.text((embed_x1 + 35, embed_y2 - 52), "📈 Abrir Dashboard RED", fill="#ffffff", font=font_bold)

    draw.rectangle([embed_x1 + 220, embed_y2 - 65, embed_x1 + 390, embed_y2 - 25], fill="#4e5058")
    draw.text((embed_x1 + 240, embed_y2 - 52), "🔥 Ver Runbook SRE", fill="#ffffff", font=font_bold)

    draw.rectangle([embed_x1 + 410, embed_y2 - 65, embed_x1 + 540, embed_y2 - 25], fill="#248046")
    draw.text((embed_x1 + 430, embed_y2 - 52), "🔕 Silenciar (2h)", fill="#ffffff", font=font_bold)

    img.save(os.path.join(ASSETS_DIR, "discord-alert-notification.png"), quality=95)
    print("Created discord-alert-notification.png")

generate_red_dashboard()
generate_use_dashboard()
generate_discord_alert()
