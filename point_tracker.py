from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import csv
import time
import re
import os

import os

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

def extract_players_by_competition(html):
    soup = BeautifulSoup(html, 'html.parser')
    comp_data = {'laliga': [], 'champions': [], 'uel': []}
    
    # Find all competition headers including aplazados
    headers = soup.find_all('strong', string=re.compile(r'Jornada \d+ - (LaLiga|Champions League|Europa League|Aplazados \d+ LaLiga)'))
    
    for header in headers:
        comp_text = header.get_text()
        if 'LaLiga' in comp_text or 'Aplazados' in comp_text:
            comp = 'laliga'
        elif 'Champions' in comp_text:
            comp = 'champions'
        elif 'Europa' in comp_text:
            comp = 'uel'
        else:
            continue
        
        # Find players in this section (until next header)
        section = header.find_parent('div', class_='col-12')
        if section:
            parent_section = section.find_parent('div', class_='row')
            if parent_section:
                point_spans = parent_section.find_all('span', class_=re.compile(r'icon-puntos'))
                
                for span in point_spans:
                    points_text = span.find('span', class_='m-auto')
                    if points_text:
                        pts = points_text.get_text(strip=True)
                        if pts.isdigit():
                            points = int(pts)
                            parent = span.parent
                            name_span = parent.find('span', style=re.compile(r'color:white.*bottom: 0.*position: absolute'))
                            if name_span:
                                name = name_span.get_text(strip=True)
                                if name:
                                    comp_data[comp].append({'player': name, 'points': points})
    
    return comp_data

def load_existing(filename):
    filepath = os.path.join('data', filename)
    if not os.path.exists(filepath):
        return {}
    
    data = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data[row['player']] = {
                'total_points': int(row['total_points']),
                'games_played': int(row['games_played'])
            }
    return data

def save_data(filename, data):
    filepath = os.path.join('data', filename)
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['player', 'total_points', 'games_played', 'unique_usage'])
        writer.writeheader()
        for player, stats in sorted(data.items()):
            writer.writerow({
                'player': player,
                'total_points': stats['total_points'],
                'games_played': stats['games_played'],
                'unique_usage': stats.get('unique_usage', 1)
            })

users = ['cmanzanas', 'manziyauskas', 'dieman95']
competitions = ['laliga', 'champions', 'uel']

for user in users:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    url = f"https://www.futbolfantasy.com/usuarios/{user}/participaciones/finalizadas"
    print(f"\nScraping {user}...")
    
    driver.get(url)
    time.sleep(20)
    
    comp_data = extract_players_by_competition(driver.page_source)
    driver.quit()
    
    # For each competition, rebuild data from scratch counting all appearances
    for comp in competitions:
        filename = f"{user}_{comp}.csv"
        player_stats = {}
        seen_unique = set()
        
        # Count every player appearance
        for p in comp_data[comp]:
            name = p['player']
            if name in player_stats:
                player_stats[name]['total_points'] += p['points']
                player_stats[name]['games_played'] += 1
            else:
                player_stats[name] = {
                    'total_points': p['points'],
                    'games_played': 1,
                    'unique_usage': 0
                }
            
            # Track unique usage
            if name not in seen_unique:
                seen_unique.add(name)
                player_stats[name]['unique_usage'] = 1
        
        save_data(filename, player_stats)
        print(f"✅ {filename}: {len(player_stats)} unique players, {len(comp_data[comp])} total appearances")

# Add extra LaLiga competitions at the end
print("\nAdding extra LaLiga competitions...")
for user in users:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    url = f"https://www.futbolfantasy.com/usuarios/{user}/participaciones/finalizadas"
    driver.get(url)
    time.sleep(20)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    
    # Find the 3 extra LaLiga sections
    extra_headers = soup.find_all('strong', class_='text-center d-block', string=re.compile(r'(Jornada 19 - LaLiga|Aplazados [12] - LaLiga)'))
    
    filename = f"{user}_laliga.csv"
    laliga_data = {}
    
    # First load the main LaLiga data we just created
    existing = load_existing(filename)
    for player, stats in existing.items():
        laliga_data[player] = stats.copy()
    
    for header in extra_headers:
        section = header.find_parent('div', class_='col-12')
        if section:
            parent_section = section.find_parent('div', class_='row')
            if parent_section:
                point_spans = parent_section.find_all('span', class_=re.compile(r'icon-puntos'))
                
                for span in point_spans:
                    points_text = span.find('span', class_='m-auto')
                    if points_text:
                        pts = points_text.get_text(strip=True)
                        if pts.isdigit():
                            points = int(pts)
                            parent = span.parent
                            name_span = parent.find('span', style=re.compile(r'color:white.*bottom: 0.*position: absolute'))
                            if name_span:
                                name = name_span.get_text(strip=True)
                                if name:
                                    if name in laliga_data:
                                        laliga_data[name]['total_points'] += points
                                        laliga_data[name]['games_played'] += 1
                                    else:
                                        laliga_data[name] = {'total_points': points, 'games_played': 1, 'unique_usage': 1}
    
    save_data(filename, laliga_data)
    print(f"✅ {filename}: Updated with extra competitions")

print("\n✅ All files updated")
