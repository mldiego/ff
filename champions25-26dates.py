import json

matchdays = [
    {"matchday": 1, "start_date": "2025-09-16", "end_date": "2025-09-18"},
    {"matchday": 2, "start_date": "2025-09-30", "end_date": "2025-10-01"},
    {"matchday": 3, "start_date": "2025-10-21", "end_date": "2025-10-22"},
    {"matchday": 4, "start_date": "2025-11-04", "end_date": "2025-11-05"},
    {"matchday": 5, "start_date": "2025-11-25", "end_date": "2025-11-26"},
    {"matchday": 6, "start_date": "2025-12-09", "end_date": "2025-12-10"},
    {"matchday": 7, "start_date": "2026-01-20", "end_date": "2026-01-21"},
    {"matchday": 8, "start_date": "2026-01-28", "end_date": "2026-01-28"},
    {"matchday": "Playoffs 1", "start_date": "2026-02-17", "end_date": "2026-02-18"},
    {"matchday": "Playoffs 2", "start_date": "2026-02-24", "end_date": "2026-02-25"},
    {"matchday": "R16 1", "start_date": "2026-03-10", "end_date": "2026-03-11"},
    {"matchday": "R16 2", "start_date": "2026-03-17", "end_date": "2026-03-18"},
    {"matchday": "QF 1", "start_date": "2026-04-07", "end_date": "2026-04-08"},
    {"matchday": "QF 2", "start_date": "2026-04-14", "end_date": "2026-04-15"},
    {"matchday": "SF 1", "start_date": "2026-04-28", "end_date": "2026-04-29"},
    {"matchday": "SF 2", "start_date": "2026-05-05", "end_date": "2026-05-06"},
    {"matchday": "Final", "start_date": "2026-05-30", "end_date": "2026-05-30"}
]

# Save as JSON
with open('matchdays.json', 'w', encoding='utf-8') as f:
    json.dump(matchdays, f, indent=2)

print("✅ Created matchdays.json")
