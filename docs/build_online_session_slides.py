"""Generate a widescreen PDF slide deck of the online session guide."""

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

W, H = 13.333 * inch, 7.5 * inch
BG = HexColor("#0f172a")
CARD = HexColor("#1e293b")
BORDER = HexColor("#334155")
TEXT = HexColor("#f1f5f9")
SUB = HexColor("#94a3b8")
ACCENT = HexColor("#3b82f6")
WARN_BG = HexColor("#3b2a12")
WARN = HexColor("#fbbf24")
INFO_BG = HexColor("#172554")
CODE_BG = HexColor("#020817")


def new_slide(c):
    c.showPage()
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)


def footer(c, page, total):
    c.setFillColor(SUB)
    c.setFont("Helvetica", 9)
    c.drawString(0.6 * inch, 0.28 * inch, "API AI Workshop  ·  Online session")
    c.drawRightString(W - 0.6 * inch, 0.28 * inch, f"{page}  /  {total}")
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.line(0.6 * inch, 0.48 * inch, W - 0.6 * inch, 0.48 * inch)


def heading(c, number, title):
    y = H - 0.7 * inch
    if number:
        c.setFillColor(ACCENT)
        c.circle(0.85 * inch, y - 4, 12, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(0.85 * inch, y - 8, str(number))
        c.setFillColor(TEXT)
        c.setFont("Helvetica-Bold", 22)
        c.drawString(1.2 * inch, y - 10, title)
    else:
        c.setFillColor(TEXT)
        c.setFont("Helvetica-Bold", 26)
        c.drawString(0.7 * inch, y - 10, title)
    return y - 0.45 * inch


def wrap(c, text, x, y, max_w, font="Helvetica", size=13, color=TEXT, leading=18):
    c.setFont(font, size)
    c.setFillColor(color)
    words = text.split()
    line = ""
    for word in words:
        trial = f"{line} {word}".strip()
        if c.stringWidth(trial, font, size) <= max_w:
            line = trial
        else:
            c.drawString(x, y, line)
            y -= leading
            line = word
    if line:
        c.drawString(x, y, line)
        y -= leading
    return y


def bullet(c, text, x, y, max_w, size=13):
    c.setFillColor(ACCENT)
    c.circle(x + 4, y + 4, 3, fill=1, stroke=0)
    return wrap(c, text, x + 16, y, max_w - 16, size=size, leading=18)


def card(c, x, y, w, h):
    c.setFillColor(CARD)
    c.setStrokeColor(BORDER)
    c.setLineWidth(1)
    c.roundRect(x, y, w, h, 8, fill=1, stroke=1)


def callout(c, title, body, x, y, w, warn=False):
    bg = WARN_BG if warn else INFO_BG
    accent = WARN if warn else ACCENT
    c.setFillColor(bg)
    c.setStrokeColor(accent)
    c.setLineWidth(1)
    # estimate height after wrap — draw after measuring
    text_w = w - 32
    # rough height
    c.setFont("Helvetica", 11)
    words = body.split()
    lines, line = 1, ""
    for word in words:
        trial = f"{line} {word}".strip()
        if c.stringWidth(trial, "Helvetica", 11) <= text_w:
            line = trial
        else:
            lines += 1
            line = word
    h = 28 + 16 + lines * 15
    c.roundRect(x, y - h, w, h, 6, fill=1, stroke=1)
    c.setFillColor(accent)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x + 14, y - 20, title)
    wrap(c, body, x + 14, y - 38, text_w, size=11, color=TEXT, leading=15)
    return y - h - 12


def code_block(c, lines, x, y, w):
    h = 18 + len(lines) * 16
    c.setFillColor(CODE_BG)
    c.setStrokeColor(BORDER)
    c.roundRect(x, y - h, w, h, 6, fill=1, stroke=1)
    c.setFont("Courier", 11)
    c.setFillColor(HexColor("#e2e8f0"))
    ty = y - 22
    for line in lines:
        c.drawString(x + 14, ty, line)
        ty -= 16
    return y - h - 14


def stat_boxes(c, items, y):
    n = len(items)
    gap = 14
    box_w = (W - 1.4 * inch - gap * (n - 1)) / n
    x = 0.7 * inch
    for value, label in items:
        card(c, x, y - 78, box_w, 78)
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(x + box_w / 2, y - 38, value)
        c.setFillColor(SUB)
        c.setFont("Helvetica", 11)
        c.drawCentredString(x + box_w / 2, y - 58, label)
        x += box_w + gap


def numbered(c, items, x, y, max_w):
    for i, text in enumerate(items, 1):
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x, y, f"{i}.")
        y = wrap(c, text, x + 22, y, max_w - 22, size=13, leading=18) - 6
    return y


def build(path):
    c = canvas.Canvas(path, pagesize=(W, H))
    total = 12

    # 1 Title
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(ACCENT)
    c.rect(0, 0, 10, H, fill=1, stroke=0)
    c.setFillColor(SUB)
    c.setFont("Helvetica", 13)
    c.drawString(0.9 * inch, H - 1.6 * inch, "Getting set up before the workshop")
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 36)
    c.drawString(0.9 * inch, H - 2.3 * inch, "API AI Workshop")
    c.setFont("Helvetica-Bold", 28)
    c.drawString(0.9 * inch, H - 2.85 * inch, "Online session")
    wrap(
        c,
        "A 30-minute walkthrough: environment access, team fork, shared credentials, and the interactive assistant.",
        0.9 * inch,
        H - 3.5 * inch,
        9 * inch,
        size=14,
        color=SUB,
        leading=20,
    )
    wrap(
        c,
        "AWS Workshop Studio environment is open Friday 21 August, 3:00 pm to Monday 24 August, 3:00 pm (Pacific).",
        0.9 * inch,
        H - 4.2 * inch,
        9 * inch,
        size=14,
        color=TEXT,
        leading=20,
    )
    wrap(
        c,
        "Dry run: do not open api_hackathon/reference_solution.py if you want a genuine workshop experience later.",
        0.9 * inch,
        H - 4.85 * inch,
        9 * inch,
        size=13,
        color=WARN,
        leading=18,
    )
    footer(c, 1, total)

    # 2 Overview
    new_slide(c)
    y = heading(c, None, "Session overview")
    y = wrap(
        c,
        "This call happens before the main workshop. You will leave with a working environment and a shared team repo.",
        0.7 * inch,
        y,
        12 * inch,
        size=14,
        color=SUB,
    )
    y = wrap(
        c,
        "AWS environment window: Friday 21 August, 3:00 pm to Monday 24 August, 3:00 pm (Pacific).",
        0.7 * inch,
        y - 4,
        12 * inch,
        size=13,
        color=TEXT,
    )
    stat_boxes(
        c,
        [
            ("30 min", "Session length"),
            ("4", "Workshop levels"),
            ("100 pts", "Workshop points"),
            ("1 file", "You edit: workshop.py"),
        ],
        H - 3.1 * inch,
    )
    y = H - 4.5 * inch
    numbered(
        c,
        [
            "Join the video call and Workshop Studio",
            "Copy team AWS credentials and fork the repo",
            "Clone the fork, set credentials, run interact.py",
            "Open the Guide tab and the progress page",
        ],
        0.7 * inch,
        y,
        12 * inch,
    )
    footer(c, 2, total)

    # 3 Join
    new_slide(c)
    y = heading(c, 1, "Join the online session")
    y = wrap(
        c,
        "Your facilitator will share a video call link (Zoom or Teams). Join at the scheduled time. Keep the call open — you will run commands live.",
        0.7 * inch,
        y,
        12 * inch,
        size=15,
        leading=22,
    )
    y -= 10
    y = callout(
        c,
        "What happens in this session",
        "Facilitators walk you through environment access, repository setup, and the interactive assistant. Ask any questions before the day-of workshop begins.",
        0.7 * inch,
        y,
        12 * inch,
    )
    footer(c, 3, total)

    # 4 Studio
    new_slide(c)
    y = heading(c, 2, "Access Workshop Studio")
    y = wrap(
        c,
        "For this dry run, everyone joins the same Workshop Studio event with this link. You do not need to type an access code.",
        0.7 * inch,
        y,
        12 * inch,
        size=14,
        leading=20,
    )
    y = code_block(
        c,
        ["https://catalog.us-east-1.prod.workshops.aws/join?access-code=3c26-0d1d02-f5"],
        0.7 * inch,
        y,
        12 * inch,
    )
    y = numbered(
        c,
        [
            "Open the join link above",
            "Sign in if prompted",
            "Accept the terms and open the environment",
        ],
        0.7 * inch,
        y,
        12 * inch,
    )
    y -= 8
    y = callout(
        c,
        "The environment is shareable — the editor is not",
        "Every teammate can join the same Workshop Studio environment. The VS Code instance cannot be used by more than one person at a time. Share credentials (to access Bedrock via activity scripts), then edit on your own machines via a team fork. If you need VS Code on your laptop: https://code.visualstudio.com/download",
        0.7 * inch,
        y,
        12 * inch,
    )
    callout(
        c,
        "Environment window",
        "The AWS Workshop Studio environment is available from Friday 21 August, 3:00 pm to Monday 24 August, 3:00 pm (Pacific). Credentials and Bedrock only work inside that window.",
        0.7 * inch,
        y,
        12 * inch,
        warn=True,
    )
    footer(c, 4, total)

    # 5 Credentials
    new_slide(c)
    y = heading(c, 3, "Copy your AWS credentials")
    y = wrap(
        c,
        "These are team credentials. Anyone on the team can use them to call Bedrock from interact.py — in Studio or on their own laptop.",
        0.7 * inch,
        y,
        12 * inch,
        size=14,
        leading=20,
    )
    y -= 8
    y = numbered(
        c,
        [
            "In Workshop Studio, click Get AWS CLI credentials in the left panel",
            "Choose the PowerShell tab",
            "Copy all four $env: lines and share them with every teammate",
        ],
        0.7 * inch,
        y,
        12 * inch,
    )
    y -= 8
    callout(
        c,
        "Credentials last as long as the environment",
        "The Studio CLI credentials stay valid for the environment window: Friday 21 August, 3:00 pm to Monday 24 August, 3:00 pm (Pacific). You do not need to refresh them during the dry run. Do not commit them to the fork.",
        0.7 * inch,
        y,
        12 * inch,
        warn=True,
    )
    footer(c, 5, total)

    # 6 Fork
    new_slide(c)
    y = heading(c, 4, "Create a team fork")
    y = wrap(
        c,
        "Studio VS Code is single-user. One teammate forks the public kit; everyone else works on that fork. The fork URL is also the hand-in.",
        0.7 * inch,
        y,
        12 * inch,
        size=14,
        leading=20,
    )
    y -= 6
    y = wrap(
        c,
        "One person: click Fork on GitHub, or run this (YOUR-ORG becomes your GitHub username):",
        0.7 * inch,
        y,
        12 * inch,
        size=13,
        leading=18,
    )
    y = code_block(
        c,
        ["gh repo fork UBCDigitalExperienceLab/api-ai-hackathon-public --clone=false"],
        0.7 * inch,
        y,
        12 * inch,
    )
    y = numbered(
        c,
        [
            "Invite every teammate as a collaborator (Settings → Collaborators)",
            "Share https://github.com/YOUR-ORG/api-ai-hackathon-public with the team and facilitators",
        ],
        0.7 * inch,
        y,
        12 * inch,
    )
    y -= 4
    y = callout(
        c,
        "Shared environment + fork = everyone can use Bedrock",
        "Set the team's Workshop Studio credentials in your local terminal, then run interact.py from anywhere. You are using the same AWS environment, just not the same VS Code window.",
        0.7 * inch,
        y,
        12 * inch,
    )
    y = callout(
        c,
        "Dry run — do not open reference_solution.py",
        "The repo includes api_hackathon/reference_solution.py. Do not open, copy, or use that file during the dry run — especially if you want a genuine workshop experience later. Work only in api_hackathon/workshop.py.",
        0.7 * inch,
        y,
        12 * inch,
        warn=True,
    )
    callout(
        c,
        "Keep the git workflow small",
        "Work on main. Push only api_hackathon/workshop.py. Do not commit credentials or .env files.",
        0.7 * inch,
        y,
        12 * inch,
        warn=True,
    )
    footer(c, 6, total)

    # 7 Clone
    new_slide(c)
    y = heading(c, 5, "Clone the team fork")
    y = wrap(
        c,
        "Every teammate clones the fork, not the upstream public repo. Do this in Studio if you are the editor, and on your own machine if you are contributing in parallel.",
        0.7 * inch,
        y,
        12 * inch,
        size=14,
        leading=20,
    )
    y = callout(
        c,
        "YOUR-ORG is a placeholder — replace it",
        "YOUR-ORG is not a real GitHub name. Replace it with the GitHub username or organization that created the fork. Example: if teammate alex-lee clicked Fork, everyone runs git clone https://github.com/alex-lee/api-ai-hackathon-public.git. Copy the URL from the fork page's green Code button if you are unsure.",
        0.7 * inch,
        y,
        12 * inch,
    )
    y = code_block(
        c,
        [
            "# Replace YOUR-ORG with the fork owner's GitHub name",
            "git clone https://github.com/YOUR-ORG/api-ai-hackathon-public.git",
            "cd api-ai-hackathon-public",
            "",
            "# Or clone into a folder you choose",
            "git clone https://github.com/YOUR-ORG/api-ai-hackathon-public.git C:\\path\\to\\your-team-folder",
            "cd C:\\path\\to\\your-team-folder",
        ],
        0.7 * inch,
        y,
        12 * inch,
    )
    files = [
        ("workshop.py", "The only file you edit — push this to the fork"),
        ("interact.py", "Interactive AI assistant — start here"),
        ("score.py", "Run this to see your progress at any time"),
        ("TASKS.md", "Level descriptions and tips"),
    ]
    for name, desc in files:
        c.setFillColor(ACCENT)
        c.setFont("Courier-Bold", 11)
        c.drawString(0.7 * inch, y, name)
        c.setFillColor(SUB)
        c.setFont("Helvetica", 12)
        c.drawString(2.4 * inch, y, desc)
        y -= 18
    y -= 8
    callout(
        c,
        "Skip the Studio venv on your own machine",
        "source /environment/.venv/bin/activate exists only inside AWS Workshop Studio. On a personal machine use Python 3.10+ and pip install boto3. A local venv is optional.",
        0.7 * inch,
        y,
        12 * inch,
        warn=True,
    )
    footer(c, 7, total)

    # 8 Set credentials
    new_slide(c)
    y = heading(c, 6, "Set AWS credentials on every machine")
    y = wrap(
        c,
        "Paste the team's four credential lines into your terminal — Studio or local — before running interact.py. Everyone uses the same shared environment credentials.",
        0.7 * inch,
        y,
        12 * inch,
        size=14,
        leading=20,
    )
    y = code_block(
        c,
        [
            '$env:AWS_DEFAULT_REGION="us-west-2"',
            '$env:AWS_ACCESS_KEY_ID="ASIA..."',
            '$env:AWS_SECRET_ACCESS_KEY="..."',
            '$env:AWS_SESSION_TOKEN="..."',
        ],
        0.7 * inch,
        y,
        12 * inch,
    )
    callout(
        c,
        "PowerShell syntax — common mistake",
        'set VAR=value is CMD syntax and silently does nothing in PowerShell. Always use $env:VAR="value".',
        0.7 * inch,
        y,
        12 * inch,
        warn=True,
    )
    footer(c, 8, total)

    # 9 interact.py
    new_slide(c)
    y = heading(c, 7, "Launch the interactive assistant")
    y = wrap(
        c,
        "This works from Studio or from any teammate's laptop — you are calling the same Bedrock environment.",
        0.7 * inch,
        y,
        12 * inch,
        size=14,
        leading=20,
    )
    y = code_block(c, ["python interact.py"], 0.7 * inch, y, 12 * inch)
    y = callout(
        c,
        "Activity instructions live on the Guide tab",
        "After you start the progress page, open http://localhost:8081/guide. That Getting Started page walks through the activity: pick a level, ask the AI, edit workshop.py, then check your progress.",
        0.7 * inch,
        y,
        12 * inch,
    )
    for title, desc in [
        ("Level menu", "Pick a level (1–4). Each shows your current implementation status."),
        ("Ask follow-up questions", "The AI guides without giving away the answer."),
        ("Jump between levels", "Type a level number to switch. Type menu to return."),
    ]:
        c.setFillColor(TEXT)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(0.7 * inch, y, title)
        c.setFillColor(SUB)
        c.setFont("Helvetica", 12)
        c.drawString(3.3 * inch, y, desc)
        y -= 20
    footer(c, 9, total)

    # 10 Progress page
    new_slide(c)
    y = heading(c, 8, "Start the progress page")
    y = wrap(
        c,
        "In a second terminal window, start the local progress page. Keep it running throughout the workshop.",
        0.7 * inch,
        y,
        12 * inch,
        size=14,
        leading=20,
    )
    y = code_block(c, ["python scoreboard.py"], 0.7 * inch, y, 12 * inch)
    urls = [
        ("http://localhost:8081/guide", "Getting Started — activity instructions (Guide tab)"),
        ("http://localhost:8081", "Progress page — updates every 5 seconds"),
        ("http://localhost:8081/api/v1", "Orders API v1 spec in Swagger UI"),
        ("http://localhost:8081/api/v2", "Orders API v2 spec in Swagger UI"),
    ]
    for url, desc in urls:
        c.setFillColor(ACCENT)
        c.setFont("Courier", 11)
        c.drawString(0.7 * inch, y, url)
        c.setFillColor(SUB)
        c.setFont("Helvetica", 12)
        c.drawString(4.5 * inch, y, desc)
        y -= 20
    y -= 8
    callout(
        c,
        "Swagger is reference only",
        'The API is not running. Use the spec to verify AI findings in workshop.py. "Try it out" will return 404.',
        0.7 * inch,
        y,
        12 * inch,
    )
    footer(c, 10, total)

    # 11 Levels
    new_slide(c)
    y = heading(c, None, "Workshop overview")
    y = wrap(
        c,
        "Each level follows the same pattern: AI produces output → your code verifies it → only proven results survive.",
        0.7 * inch,
        y,
        12 * inch,
        size=14,
        color=SUB,
        leading=20,
    )
    y -= 8
    rows = [
        ("L1  Contract review", "20", "Filter hallucinated OpenAPI findings"),
        ("L2  Negative tests", "25", "Filter hallucinated test cases"),
        ("L3  Incident diagnosis", "30", "Verify a diagnosis against the actual log file"),
        ("L4  Migration review", "25", "Filter fabricated breaking changes"),
    ]
    row_h = 52
    for i, (name, pts, task) in enumerate(rows):
        top = y - i * (row_h + 8)
        card(c, 0.7 * inch, top - row_h, 12 * inch, row_h)
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(0.95 * inch, top - 22, name)
        c.setFillColor(SUB)
        c.setFont("Helvetica", 12)
        c.drawString(0.95 * inch, top - 40, task)
        c.setFillColor(TEXT)
        c.setFont("Helvetica-Bold", 16)
        c.drawRightString(12.4 * inch, top - 30, f"{pts} pts")
    footer(c, 11, total)

    # 12 Commands
    new_slide(c)
    y = heading(c, None, "Key commands")
    y = wrap(
        c,
        "Use these throughout the workshop. Command names stay the same; they check progress, they do not rank teams.",
        0.7 * inch,
        y,
        12 * inch,
        size=14,
        color=SUB,
        leading=20,
    )
    y = callout(
        c,
        "Dry run — do not open reference_solution.py",
        "Do not open or use api_hackathon/reference_solution.py. It is a facilitator file. Looking at it will spoil the workshop if you want to try the real experience later.",
        0.7 * inch,
        y,
        12 * inch,
        warn=True,
    )
    cmds = [
        ("python interact.py", "Explore any level with live AI guidance"),
        ('python score.py --team "Team Name"', "Check your workshop.py progress"),
        ("git push", "Share workshop.py on the team fork"),
        ("python scoreboard.py", "Progress page at http://localhost:8081"),
    ]
    for cmd, desc in cmds:
        card(c, 0.7 * inch, y - 62, 12 * inch, 58)
        c.setFillColor(HexColor("#e2e8f0"))
        c.setFont("Courier-Bold", 13)
        c.drawString(0.95 * inch, y - 28, cmd)
        c.setFillColor(SUB)
        c.setFont("Helvetica", 12)
        c.drawString(0.95 * inch, y - 48, desc)
        y -= 72
    footer(c, 12, total)

    c.save()


if __name__ == "__main__":
    out = __file__.replace("build_online_session_slides.py", "online-session-slides.pdf")
    try:
        build(out)
    except PermissionError:
        out = __file__.replace("build_online_session_slides.py", "online-session-slides-updated.pdf")
        build(out)
    print(out)
