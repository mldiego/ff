import csv
import json
from datetime import datetime
import os

# Load matchday schedules
with open('config/laliga_matchdays.json', 'r') as f:
    laliga_matchdays = json.load(f)
with open('config/champions_matchdays.json', 'r') as f:
    champions_matchdays = json.load(f)
with open('config/uel_matchdays.json', 'r') as f:
    uel_matchdays = json.load(f)

matchday_schedules = {
    'laliga': laliga_matchdays,
    'champions': champions_matchdays,
    'uel': uel_matchdays
}

# Load CSV data
with open('data/user_competitions_history.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    data = list(reader)

# Get timestamps
timestamps = [col for col in data[0].keys() if col not in ['user', 'competition', 'metric']]

# Match timestamps to matchdays
def find_matchday(timestamp_str, competition):
    ts_date = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M').date()
    schedule = matchday_schedules[competition]
    
    for md in schedule:
        end_date = datetime.strptime(md['end_date'], '%Y-%m-%d').date()
        if ts_date >= end_date:
            last_matchday = md['matchday']
    
    return last_matchday if 'last_matchday' in locals() else None

# Organize data by competition
users = ['cmanzanas', 'Manziyauskas', 'dieman95']
competitions = {'laliga': 'LaLiga', 'champions': 'Champions', 'uel': 'Europa League'}

chart_data = {}
for comp_key, comp_name in competitions.items():
    matchdays = []
    chart_data[comp_key] = {'matchdays': [], 'users': {}}
    
    for user in users:
        chart_data[comp_key]['users'][user] = {'positions': [], 'points': []}
    
    # Process each timestamp
    seen_matchdays = set()
    for ts in timestamps:
        matchday = find_matchday(ts, comp_key)
        if matchday and matchday not in seen_matchdays:
            seen_matchdays.add(matchday)
            chart_data[comp_key]['matchdays'].append(f"MD {matchday}")
            
            for user in users:
                pos_row = next((r for r in data if r['user'] == user and r['competition'] == comp_key and r['metric'] == 'position'), None)
                pts_row = next((r for r in data if r['user'] == user and r['competition'] == comp_key and r['metric'] == 'points'), None)
                
                chart_data[comp_key]['users'][user]['positions'].append(int(pos_row[ts]) if pos_row and pos_row.get(ts) else 0)
                chart_data[comp_key]['users'][user]['points'].append(int(pts_row[ts]) if pts_row and pts_row.get(ts) else 0)

# Generate HTML
html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Fantasy Football Rankings by Matchday</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .chart-container {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ text-align: center; color: #333; }}
        h2 {{ color: #555; margin-top: 0; }}
        canvas {{ max-height: 400px; }}
    </style>
</head>
<body>
    <h1>🏆 Fantasy Football Rankings by Matchday</h1>
    
    <div class="chart-container">
        <h2>LaLiga</h2>
        <canvas id="laliga"></canvas>
    </div>
    
    <div class="chart-container">
        <h2>Champions League</h2>
        <canvas id="champions"></canvas>
    </div>
    
    <div class="chart-container">
        <h2>Europa League</h2>
        <canvas id="uel"></canvas>
    </div>

    <script>
        const chartData = {json.dumps(chart_data)};
        const users = {json.dumps(users)};
        const colors = {{
            'cmanzanas': '#FF6384',
            'Manziyauskas': '#36A2EB',
            'dieman95': '#FFCE56'
        }};

        function createChart(canvasId, competition) {{
            const ctx = document.getElementById(canvasId).getContext('2d');
            const datasets = users.map(user => ({{
                label: user,
                data: chartData[competition].users[user].positions,
                borderColor: colors[user],
                backgroundColor: colors[user] + '33',
                tension: 0.3,
                fill: false,
                pointRadius: 5,
                pointHoverRadius: 7
            }}));

            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: chartData[competition].matchdays,
                    datasets: datasets
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {{
                        y: {{
                            reverse: true,
                            title: {{ display: true, text: 'Position (lower is better)' }}
                        }},
                        x: {{
                            title: {{ display: true, text: 'Matchday' }}
                        }}
                    }},
                    plugins: {{
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const user = context.dataset.label;
                                    const position = context.parsed.y;
                                    const points = chartData[competition].users[user].points[context.dataIndex];
                                    return user + ': Position ' + position + ' (' + points + ' pts)';
                                }}
                            }}
                        }}
                    }}
                }}
            }});
        }}

        createChart('laliga', 'laliga');
        createChart('champions', 'champions');
        createChart('uel', 'uel');
    </script>
</body>
</html>'''

os.makedirs('visualization', exist_ok=True)
with open('visualization/rankings_by_matchday.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ Visualization created: visualization/rankings_by_matchday.html")
