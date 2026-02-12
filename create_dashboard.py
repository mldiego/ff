import csv
import json
import os

# Read all player data
users = ['cmanzanas', 'Manziyauskas', 'dieman95']
competitions = {'laliga': 'LaLiga', 'champions': 'Champions', 'uel': 'Europa League'}

data = {}
for user in users:
    data[user] = {}
    for comp_key, comp_name in competitions.items():
        filepath = f'data/{user}_{comp_key}.csv'
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                players = []
                for row in reader:
                    players.append({
                        'player': row['player'],
                        'total_points': int(row['total_points']),
                        'games_played': int(row['games_played']),
                        'unique_usage': int(row.get('unique_usage', 1)),
                        'avg_points': round(int(row['total_points']) / int(row['games_played']), 2)
                    })
                data[user][comp_key] = players

# Generate HTML dashboard
html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Player Analysis Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
        h1 {{ text-align: center; color: #333; margin-bottom: 30px; }}
        .controls {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .control-group {{ display: inline-block; margin-right: 20px; margin-bottom: 10px; }}
        label {{ font-weight: bold; margin-right: 10px; }}
        select, input {{ padding: 8px; border: 1px solid #ddd; border-radius: 4px; }}
        table {{ width: 100%; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        th {{ background: #36A2EB; color: white; padding: 12px; text-align: left; cursor: pointer; user-select: none; }}
        th:hover {{ background: #2891d9; }}
        td {{ padding: 12px; border-bottom: 1px solid #eee; }}
        tr:hover {{ background: #f9f9f9; }}
        .highlight {{ background: #fff3cd !important; }}
    </style>
</head>
<body>
    <h1>⚽ Player Analysis Dashboard</h1>
    
    <div class="controls">
        <div class="control-group">
            <label>User:</label>
            <select id="userSelect" onchange="updateData()">
                {' '.join(f'<option value="{u}">{u}</option>' for u in users)}
            </select>
        </div>
        <div class="control-group">
            <label>Competition:</label>
            <select id="compSelect" onchange="updateData()">
                {' '.join(f'<option value="{k}">{v}</option>' for k, v in competitions.items())}
            </select>
        </div>
        <div class="control-group">
            <label>Min Games:</label>
            <input type="number" id="minGames" value="1" min="1" onchange="updateData()">
        </div>
        <div class="control-group">
            <label>Sort By:</label>
            <select id="sortBy" onchange="updateData()">
                <option value="avg_points">Best Average</option>
                <option value="total_points">Most Points</option>
                <option value="games_played">Most Games</option>
            </select>
        </div>
    </div>
    
    <table>
        <thead>
            <tr>
                <th onclick="sortTable('player')">Player</th>
                <th onclick="sortTable('total_points')">Total Points</th>
                <th onclick="sortTable('games_played')">Games Played</th>
                <th onclick="sortTable('avg_points')">Avg Points/Game</th>
            </tr>
        </thead>
        <tbody id="tableBody"></tbody>
    </table>

    <script>
        const data = {json.dumps(data)};
        let currentData = [];
        let currentSort = 'avg_points';
        let sortAsc = false;

        function updateData() {{
            const user = document.getElementById('userSelect').value;
            const comp = document.getElementById('compSelect').value;
            const minGames = parseInt(document.getElementById('minGames').value);
            currentSort = document.getElementById('sortBy').value;
            
            currentData = data[user][comp].filter(p => p.games_played >= minGames);
            sortData(currentSort);
            renderTable();
        }}

        function sortData(field) {{
            currentData.sort((a, b) => {{
                if (sortAsc) return a[field] - b[field];
                return b[field] - a[field];
            }});
        }}

        function sortTable(field) {{
            if (currentSort === field) {{
                sortAsc = !sortAsc;
            }} else {{
                currentSort = field;
                sortAsc = false;
            }}
            sortData(field);
            renderTable();
        }}

        function renderTable() {{
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = currentData.map((p, i) => `
                <tr class="${{i < 3 ? 'highlight' : ''}}">
                    <td>${{p.player}}</td>
                    <td>${{p.total_points}}</td>
                    <td>${{p.games_played}}</td>
                    <td>${{p.avg_points}}</td>
                </tr>
            `).join('');
        }}

        updateData();
    </script>
</body>
</html>'''

os.makedirs('visualization', exist_ok=True)
with open('visualization/player_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ Dashboard created: visualization/player_dashboard.html")
