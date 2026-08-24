# Team submissions

Drop each team's `workshop.py` here, then score everyone onto the shared board:

```text
submissions/
  Team Alpha/workshop.py
  Team Beta/workshop.py
  Reference/workshop.py      ← optional facilitator copy
```

```powershell
# Score every team folder and update scoreboard.json
python score.py --all

# Or score one file by hand
python score.py --team "Team Alpha" --file "submissions/Team Alpha/workshop.py"

# Keep the live board open for the room
python scoreboard.py
```

Open http://localhost:8081 — every scored team appears. Click a row for per-check detail.

Folder names become team names on the board. Folders starting with `.` or `_` are ignored.
