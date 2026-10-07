#!/usr/bin/env python3
"""Build a 6-month shift rota pack for Dal (3 staff, Mon-Fri early/late rotation
+ Saturday rotation).

Rules implemented (stated on the artifact):
  Mon-Fri : one early, one late, one rest day each week. The three rotate weekly on a
            3-week cycle so over three weeks everyone does one early week, one late week
            and one rest week.
  Saturday: one of the three on site each Saturday, rotating in order every 3 weeks.

Cover period: Thu 8 Oct 2026 -> Wed 7 Apr 2027 (six months).
"""
import datetime as dt
import json
import pathlib

STAFF = ["Ramish", "Brett Smith", "Darren Hopwood"]
START = dt.date(2026, 10, 8)          # tomorrow (Thu)
END = dt.date(2027, 4, 7)             # six calendar months later
# cycle anchor: the Monday of the week containing START
ANCHOR_MON = START - dt.timedelta(days=START.weekday())   # Mon 5 Oct 2026
FIRST_SAT = START + dt.timedelta(days=(5 - START.weekday()) % 7)  # first Saturday after START

CYCLE_WEEKDAY = [
    {"early": "Ramish",        "late": "Brett Smith",    "rest": "Darren Hopwood"},
    {"early": "Brett Smith",   "late": "Darren Hopwood", "rest": "Ramish"},
    {"early": "Darren Hopwood", "late": "Ramish",        "rest": "Brett Smith"},
]


def cycle_idx(d):
    return ((d - ANCHOR_MON).days // 7) % 3


# ---------------- weekday week-blocks ----------------
weekday_blocks = []
d = START
while d <= END:
    mon = d - dt.timedelta(days=d.weekday())
    fri = mon + dt.timedelta(days=4)
    row_start = max(mon, START)
    row_end = min(fri, END)
    if row_start > row_end:
        d = fri + dt.timedelta(days=3)
        continue
    c = CYCLE_WEEKDAY[cycle_idx(fri if fri <= END else END)]
    weekday_blocks.append({
        "week": ((mon - ANCHOR_MON).days // 7) + 1,
        "start": row_start, "end": row_end,
        "partial": row_start != mon or row_end != fri,
        "early": c["early"], "late": c["late"], "rest": c["rest"],
    })
    d = fri + dt.timedelta(days=3)

# ---------------- saturdays ----------------
saturdays = []
sat = FIRST_SAT
i = 0
while sat <= END:
    saturdays.append({"date": sat, "who": STAFF[i % 3]})
    i += 1
    sat += dt.timedelta(days=7)

data = {
    "start": START.isoformat(), "end": END.isoformat(),
    "weekday_blocks": [{**b, "start": b["start"].isoformat(), "end": b["end"].isoformat()}
                       for b in weekday_blocks],
    "saturdays": [{"date": s["date"].isoformat(), "who": s["who"]} for s in saturdays],
}
out = pathlib.Path("/root/outputs/shift-rota/rota_data.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(data, indent=2))

print("weekday week-blocks:", len(weekday_blocks))
print("saturdays:", len(saturdays))
print("first block:", weekday_blocks[0])
print("last block:", weekday_blocks[-1])
print("first sat:", saturdays[0], "last sat:", saturdays[-1])
# fairness check
from collections import Counter
print("early weeks:", Counter(b["early"] for b in weekday_blocks))
print("late  weeks:", Counter(b["late"] for b in weekday_blocks))
print("rest  weeks:", Counter(b["rest"] for b in weekday_blocks))
print("sat counts :", Counter(s["who"] for s in saturdays))
