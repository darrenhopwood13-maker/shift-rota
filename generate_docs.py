#!/usr/bin/env python3
"""Render the shift rota pack: index.html (hosted + printable), rota.pdf, rota.xlsx."""
import datetime as dt
import json
import pathlib

BASE = pathlib.Path("/root/outputs/shift-rota")
data = json.loads((BASE / "rota_data.json").read_text())
D = lambda s: dt.date.fromisoformat(s)


def fmt(d, with_day=True):
    d = D(d) if isinstance(d, str) else d
    return d.strftime("%a %-d %b %Y") if with_day else d.strftime("%-d %b %Y")


def short(d):
    d = D(d) if isinstance(d, str) else d
    return d.strftime("%-d %b")


wb = data["weekday_blocks"]
sats = data["saturdays"]
start, end = data["start"], data["end"]
issued = "Tue 6 Oct 2026" if False else dt.date(2026, 10, 7).strftime("%a %-d %b %Y")

ST = {"Ramish": "ram", "Brett Smith": "bre", "Darren Hopwood": "dar"}


def name_cell(n):
    return f'<span class="nm {ST[n]}">{n}</span>'


rows_wd = []
for b in wb:
    dr = fmt(b["start"]) if b["start"] == b["end"] else f'{fmt(b["start"])} &ndash; {fmt(b["end"])}'
    partial = ' <span class="tag">part week</span>' if b["partial"] else ""
    rows_wd.append(
        f'<tr><td class="wk">{b["week"]}</td><td class="dt">{dr}{partial}</td>'
        f'<td>{name_cell(b["early"])}</td><td>{name_cell(b["late"])}</td>'
        f'<td class="off">{b["rest"]}</td></tr>'
    )

rows_sat = []
for i, s in enumerate(sats, 1):
    rows_sat.append(
        f'<tr><td class="wk">{i}</td><td class="dt">{fmt(s["date"])}</td>'
        f'<td>{name_cell(s["who"])}</td></tr>'
    )

html = f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Shift Rota &ndash; {fmt(start)} to {fmt(end)}</title>
<style>
  :root {{
    --ink:#0e1626; --ink2:#33415c; --line:#d7dde8; --bg:#f5f7fa;
    --navy:#12305e; --accent:#e8720c; --green:#0f7b4f;
    --ram:#12305e; --bre:#0f7b4f; --dar:#8a4b0b;
  }}
  * {{ box-sizing:border-box; }}
  html,body {{ margin:0; padding:0; }}
  body {{
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
    color:var(--ink); background:#e9edf3; font-size:15px; line-height:1.45;
    -webkit-font-smoothing:antialiased;
  }}
  .sheet {{ max-width:840px; margin:0 auto; background:#fff; }}
  header {{
    background:linear-gradient(150deg,#12305e 0%,#0b2144 100%);
    color:#fff; padding:26px 34px 20px;
  }}
  .eyebrow {{ font-size:11px; letter-spacing:.18em; text-transform:uppercase; color:#ffb877; font-weight:700; }}
  h1 {{ font-size:34px; margin:6px 0 2px; letter-spacing:-.01em; }}
  h1 span {{ color:#ffb877; }}
  .sub {{ color:#c6d4e8; font-size:14px; }}
  .meta {{
    display:flex; flex-wrap:wrap; gap:0; border-bottom:1px solid var(--line);
    font-size:12.5px; color:var(--ink2); background:var(--bg);
  }}
  .meta div {{ padding:9px 34px 9px 0; margin-left:34px; border-right:1px solid var(--line); }}
  .meta div:last-child {{ border-right:0; }}
  .meta b {{ color:var(--ink); display:block; font-size:12px; letter-spacing:.04em; text-transform:uppercase; }}
  main {{ padding:22px 34px 30px; }}
  h2 {{ font-size:16px; margin:26px 0 10px; letter-spacing:.01em; }}
  h2 .num {{
    display:inline-block; background:var(--navy); color:#fff; border-radius:4px;
    font-size:12px; padding:1px 7px; margin-right:8px; vertical-align:2px;
  }}
  p {{ margin:0 0 10px; }}
  ul {{ margin:0 0 10px 18px; padding:0; }}
  li {{ margin:0 0 4px; }}
  .rules {{ background:var(--bg); border-left:4px solid var(--accent); padding:14px 16px; margin:0 0 6px; }}
  .rules li {{ font-size:14px; }}
  table {{ width:100%; border-collapse:collapse; margin:0 0 6px; }}
  th {{
    background:#0e1626; color:#fff; text-align:left; font-size:11px;
    letter-spacing:.1em; text-transform:uppercase; padding:8px 10px;
  }}
  td {{ padding:8px 10px; border-bottom:1px solid var(--line); font-size:14px; vertical-align:middle; }}
  tbody tr:nth-child(even) {{ background:#f7f9fc; }}
  tr {{ page-break-inside:avoid; break-inside:avoid; }}
  thead {{ display:table-header-group; }}
  td.wk {{ color:#8794ab; font-variant-numeric:tabular-nums; width:42px; font-size:12.5px; }}
  td.dt {{ white-space:nowrap; font-weight:600; }}
  .nm {{ font-weight:700; }}
  .nm.ram {{ color:var(--ram); }} .nm.bre {{ color:var(--bre); }} .nm.dar {{ color:var(--dar); }}
  .off {{ color:#8794ab; }}
  .tag {{
    background:#fff2e3; color:#a04d00; border:1px solid #ffd9b0; border-radius:3px;
    font-size:10px; padding:1px 5px; letter-spacing:.05em; text-transform:uppercase;
    font-weight:700; margin-left:5px; white-space:nowrap;
  }}
  .cols {{ display:flex; gap:18px; align-items:flex-start; }}
  .cols > div {{ flex:1; min-width:0; }}
  .note {{ font-size:12.5px; color:var(--ink2); background:#fff8ef; border:1px solid #ffe3c2; padding:12px 14px; margin-top:24px; }}
  .note b {{ color:#a04d00; }}
  footer {{ background:#0e1626; color:#8ea0bd; font-size:11.5px; padding:14px 34px; border-top:3px solid var(--accent); }}
  .dl {{ display:flex; gap:10px; flex-wrap:wrap; margin:0 0 4px; }}
  .dl a {{
    display:inline-block; text-decoration:none; font-size:13px; font-weight:700;
    color:#fff; background:var(--navy); border-radius:5px; padding:9px 14px;
  }}
  .dl a.alt {{ background:#fff; color:var(--navy); border:1.5px solid var(--navy); }}
  @page {{ size:A4; margin:11mm 10mm; }}
  @media print {{
    body {{ background:#fff; font-size:11.5px; }}
    .sheet {{ max-width:none; }}
    header {{ padding:16px 0 12px; background:#12305e !important; -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
    h1 {{ font-size:26px; }}
    .meta div {{ margin-left:0; padding:5px 14px 5px 0; }}
    main {{ padding:0; }}
    .no-print {{ display:none !important; }}
    h2 {{ margin:16px 0 7px; page-break-after:avoid; break-after:avoid; }}
    td {{ padding:4.6px 8px; font-size:11px; }}
    th {{ padding:5px 8px; font-size:9.5px; -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
    body, td, th, .nm, th, footer, .rules, .note {{ -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
    footer {{ padding:10px 0; }}
  }}
</style>
</head>
<body>
<div class="sheet">
  <header>
    <div class="eyebrow">Site staffing &middot; 3 staff</div>
    <h1>Shift <span>Rota</span></h1>
    <div class="sub">{fmt(start)} &ndash; {fmt(end)} &nbsp;&bull;&nbsp; Monday to Friday, plus Saturdays</div>
  </header>

  <div class="meta">
    <div><b>Issued</b>{issued}</div>
    <div><b>Covers</b>{fmt(start, False)} &ndash; {fmt(end, False)} (6 months)</div>
    <div><b>Staff</b>Ramish &middot; Brett Smith &middot; Darren Hopwood</div>
    <div><b>Status</b>Issued</div>
  </div>

  <main>
    <div class="dl no-print">
      <a href="rota.pdf">Download PDF</a>
      <a class="alt" href="rota.xlsx">Download spreadsheet (.xlsx)</a>
    </div>

    <h2><span class="num">1</span>How the rotation works</h2>
    <div class="rules">
      <ul>
        <li><b>Monday to Friday:</b> two on shift each day &ndash; <b>one early</b>, <b>one late</b>. The third person is off shift that week.</li>
        <li>The three rotate <b>weekly</b>, on a <b>3-week cycle</b>. So over three weeks each person does one early week, one late week and one rest week &ndash; then it starts again.</li>
        <li><b>Cycle week 1:</b> Ramish early &middot; Brett late &middot; Darren off.<br>
            <b>Cycle week 2:</b> Brett early &middot; Darren late &middot; Ramish off.<br>
            <b>Cycle week 3:</b> Darren early &middot; Ramish late &middot; Brett off.</li>
        <li><b>Saturdays:</b> one of the three on site, alternating in order &ndash; Ramish, then Brett, then Darren, then back to Ramish. One Saturday in three for each.</li>
        <li>Shift times are left blank on purpose &ndash; add them once agreed (see the note at the foot of this sheet).</li>
      </ul>
    </div>

    <h2><span class="num">2</span>Monday to Friday rota</h2>
    <table>
      <thead><tr><th>Wk</th><th>Dates</th><th>Early shift</th><th>Late shift</th><th>Off shift</th></tr></thead>
      <tbody>{''.join(rows_wd)}</tbody>
    </table>

    <h2><span class="num">3</span>Saturday rota</h2>
    <div class="cols">
      <div>
        <table>
          <thead><tr><th>#</th><th>Saturday</th><th>On shift</th></tr></thead>
          <tbody>{''.join(rows_sat[:13])}</tbody>
        </table>
      </div>
      <div>
        <table>
          <thead><tr><th>#</th><th>Saturday</th><th>On shift</th></tr></thead>
          <tbody>{''.join(rows_sat[13:])}</tbody>
        </table>
      </div>
    </div>

    <div class="note">
      <b>Read this before you pin it up.</b>
      <ul>
        <li><b>Shift times are not on this sheet.</b> Early and late start/finish times were not given, so no times have been invented &ndash; tell me the times and I will add them and reissue.</li>
        <li><b>Swaps:</b> any swap between two people is fine as long as the shift is still covered and it is agreed in advance &ndash; write it on the sheet.</li>
        <li><b>Balance over the six months:</b> 27 rota weeks &ndash; each person gets 9 early weeks, 9 late weeks and 9 rest weeks. Saturdays: Ramish 9, Brett 9, Darren 8 (26 Saturdays does not divide by three, so one person has one fewer).</li>
        <li><b>Bank holidays</b> are not marked on this sheet. Ask if you want them flagged.</li>
      </ul>
    </div>

    <footer>
      Shift Rota &middot; {fmt(start, False)} &ndash; {fmt(end, False)} &middot; issued {issued} &middot; 3-week weekday cycle, 3-week Saturday cycle
    </footer>
  </main>
</div>
</body>
</html>
"""

(BASE / "index.html").write_text(html, encoding="utf-8")

# ---------------- xlsx ----------------
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

wbk = Workbook()
ws = wbk.active
ws.title = "Mon-Fri rota"
hdr = Font(bold=True, color="FFFFFF", size=11)
fill = PatternFill("solid", fgColor="0E1626")
thin = Border(bottom=Side(style="thin", color="D7DDE8"))
ws.append(["Week", "From", "To", "Early shift", "Late shift", "Off shift"])
for c in ws[1]:
    c.font = hdr
    c.fill = fill
    c.alignment = Alignment(vertical="center")
for b in wb:
    ws.append([b["week"], D(b["start"]).strftime("%a %d %b %Y"), D(b["end"]).strftime("%a %d %b %Y"),
               b["early"], b["late"], b["rest"]])
for w, col in zip([6, 14, 14, 18, 18, 18], "ABCDEF"):
    ws.column_dimensions[col].width = w
ws.freeze_panes = "A2"

ws2 = wbk.create_sheet("Saturdays")
ws2.append(["#", "Saturday", "On shift"])
for c in ws2[1]:
    c.font = hdr
    c.fill = fill
for i, s in enumerate(sats, 1):
    ws2.append([i, D(s["date"]).strftime("%a %d %b %Y"), s["who"]])
for w, col in zip([6, 18, 18], "ABC"):
    ws2.column_dimensions[col].width = w
ws2.freeze_panes = "A2"

ws3 = wbk.create_sheet("Cover")
for r in [
    ["Shift rota", ""],
    ["From", fmt(start)],
    ["To", fmt(end)],
    ["Staff", "Ramish, Brett Smith, Darren Hopwood"],
    ["Mon-Fri pattern", "1 early + 1 late + 1 off, rotating weekly on a 3-week cycle"],
    ["Saturday pattern", "1 on shift, rotating Ramish -> Brett -> Darren"],
    ["Shift times", "NOT SET - add once agreed"],
    ["Issued", issued],
]:
    ws3.append(r)
ws3.column_dimensions["A"].width = 20
ws3.column_dimensions["B"].width = 64
for row in ws3.iter_rows(min_row=1, max_row=1):
    for c in row:
        c.font = Font(bold=True, size=13)
wbk.save(BASE / "rota.xlsx")
print("index.html + rota.xlsx written")
