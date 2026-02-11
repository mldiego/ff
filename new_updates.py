from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import csv
import time
from datetime import datetime
import os

# Set web browser options
chrome_options = Options()
chrome_options.add_argument("--headless")  
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.265 Safari/537.36"
)
chrome_options.add_argument("window-size=1200x600")

# Initialize webdriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def extract_user_competitions(html):
    """Extract current position and points for LaLiga, Champions, and Europa League"""
    soup = BeautifulSoup(html, 'html.parser')
    
    competitions = {}
    blocks = soup.find_all('div', class_='block-element')
    
    for block in blocks:
        comp_name_tag = block.find('strong')
        if not comp_name_tag:
            continue
        
        comp_name = comp_name_tag.get_text(strip=True)
        text = block.get_text()
        
        points_match = re.search(r'25/26[^:]*:\s*(\d+)\s*puntos', text)
        points = int(points_match.group(1)) if points_match else 0
        
        position_match = re.search(r'Posición[^:]*:\s*(\d+)º', text)
        position = int(position_match.group(1)) if position_match else 0
        
        if comp_name in ['LaLiga', 'Champions', 'Europa League']:
            competitions[comp_name] = {
                'points': points,
                'position': position
            }
    
    return competitions

def scrape_user(username):
    """Scrape competition data for a user"""
    url = f"http://futbolfantasy.com/usuarios/{username}/perfil"
    print(f"\nFetching {username}...")
    
    driver.get(url)
    time.sleep(2)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    
    html = driver.page_source
    data = extract_user_competitions(html)
    
    print(f"{username}:")
    for comp, stats in data.items():
        print(f"  {comp}: Position {stats['position']}, Points {stats['points']}")
    
    return data

# Scrape all users
users = ['cmanzanas', 'Manziyauskas', 'dieman95']
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
new_data = {}

for user in users:
    try:
        competitions = scrape_user(user)
        new_data[user] = competitions
    except Exception as e:
        print(f"Error scraping {user}: {e}")

driver.quit()

# Read existing CSV
csv_file = 'user_competitions_history.csv'
existing_data = {}

# if os.path.exists(csv_file):
#     with open(csv_file, 'r', encoding='utf-8') as f:
#         reader = csv.DictReader(f)
#         for row in reader:
#             key = (row['user'], row['competition'], row['metric'])
#             existing_data[key] = row

# Build new column
col = []
col.append(timestamp)
for user in users:
    for comp in ['LaLiga', 'Champions', 'Europa League']:
        for metric_type in ['points', 'position']:
            key = (user, comp, metric_type)
            row = existing_data.get(key, {'username': user, 'competition': comp, 'metric': metric_type})
            
            # Add new timestamp column
            value = new_data.get(user, {}).get(comp, {}).get(metric_type, 0)
            col.append(value)

def add_col_to_csv(csvfile,fileout,new_list):
    with open(csvfile, 'r') as read_f, \
        open(fileout, 'w', newline='') as write_f:
        csv_reader = csv.reader(read_f)
        csv_writer = csv.writer(write_f)
        i = 0
        for row in csv_reader:
            row.append(new_list[i])
            csv_writer.writerow(row)
            i += 1 

add_col_to_csv(csv_file,'temporary.csv', col)

print(f"\n✅ Data saved to {csv_file} with timestamp: {timestamp}")

os.replace('temporary.csv', csv_file)