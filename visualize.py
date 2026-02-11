import csv
import json
from datetime import datetime

# Read CSV data
csv_file = 'user_competitions_history.csv'
data = []

with open(csv_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        data.append(row)

# Parse data for visualization
users = ['cmanzanas', 'Manziyauskas', 'dieman95']
competitions = {'laliga': 'LaLiga', 'champions': 'Champions', 'uel': 'Europa League'}

# Get timestamps (exclude first 3 columns)
timestamps = [col for col in data[0].keys() if col not in ['user', 'competition', 'metric']]
dates = [datetime.strptime(ts, '%Y-%m-%d %H:%M').strftime('%Y-%m-%d') for ts in timestamps]

# Organize data by competition and user
chart_data = {}
for comp_key, comp_name in competitions.items():
    chart_data[comp_key] = {}
    for user in users:
        positions = []
        points = []
        for ts in timestamps:
            pos_row = next((r for r in data if r['user'] == user and r['competition'] == comp_key and r['metric'] == 'position'), None)
            pts_row = next((r for r in data if r['user'] == user and r['competition'] == comp_key and r['metric'] == 'points'), None)
            
            positions.append(int(pos_row[ts]) if pos_row and pos_row.get(ts) else 0)
            points.append(int(pts_row[ts]) if pts_row and pts_row.get(ts) else 0)
        
        chart_data[comp_key][user] = {'positions': positions, 'points': points}

# Generate HTML
html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Fantasy Football Rankings</title>
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
    <h1>🏆 Fantasy Football Rankings Progression</h1>
    
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
        const dates = {json.dumps(dates)};
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
                data: chartData[competition][user].positions,
                borderColor: colors[user],
                backgroundColor: colors[user] + '33',
                tension: 0.3,
                fill: false
            }}));

            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: dates,
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
                            title: {{ display: true, text: 'Date' }}
                        }}
                    }},
                    plugins: {{
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const user = context.dataset.label;
                                    const position = context.parsed.y;
                                    const points = chartData[competition][user].points[context.dataIndex];
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

# Save HTML
with open('rankings_visualization.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ Visualization created: rankings_visualization.html")
