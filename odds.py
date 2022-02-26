import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import sqlite3

#Creates new table on tb only if did not exist before
def addRegionItem(cursor, name, leaguesN):
	cursor.execute("SELECT * FROM regions WHERE name = ?", (name,))
	exists = cursor.fetchall()
	if len(exists) >= 1:
		print("Region {} already inserted in db...".format(name))
	else:
		cursor.execute("SELECT MAX(ID) from regions")
		maxID = cursor.fetchone()
		print("New Region {} inserted in db!".format(name))
		#cursor.execute("INSERT INTO regions VALUES (?, ?, ?)", (0, name, leaguesN))

def createGameTable(cursor):
	cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='games' ''')

	if cursor.fetchone()[0]==1 : 
		print('Game Table already exists.')
	else :
		print('Game Table created.')
		cursor.execute("CREATE TABLE games (name TEXT, league TEXT, region TEXT, data TEXT, odd1 INTEGER, oddx INTEGER, odd2 INTEGER, resultMID TEXT, resultFINAL TEXT)")


def addGameItem(cursor, league, region, data, name, odd1, oddX, odd2, resultadoMID, resultadoFIM):
	cursor.execute("SELECT * FROM games WHERE name = ? AND league = ? AND data = ?", (name, league, data))
	exists = cursor.fetchall()
	if len(exists) >= 1:
		print("game {} already inserted in db...".format(name))
	else:
		print("New game {} inserted in db!".format(name))
		cursor.execute("INSERT INTO games VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, league, region, data, odd1, oddX, odd2, resultadoMID, resultadoFIM))

def checkGameExists(cursor, name, league, year):
	cursor.execute("SELECT * FROM games WHERE name = ? AND league = ? AND data = ?", (name, league, year))
	exists = cursor.fetchall()
	if len(exists) >= 1:
		return 1
	else:
		return 0




connection = sqlite3.connect("oddsData.db")
cursor = connection.cursor()

options = Options()
options.add_argument("--headless")

headers = { 'Accept-Language' : 'en-US,en;q=0.5',
            'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0',
            'Referer':'https://www.oddsportal.com/'}

page = requests.get('http://www.oddsportal.com/soccer', headers=headers)

createGameTable(cursor)
connection.commit()

soup = BeautifulSoup(page.content, 'html.parser')
mainLigas = soup.find_all("tr", class_="center")[2:]

for entry, liga in enumerate(mainLigas):
	mainLigas[entry] = str(mainLigas[entry].text)[1:].replace(' ', '-')

t = soup.find_all('a', {"foo": "f"})

ligas = {}
print(mainLigas)
for country in mainLigas[14:]:
	#print(country)
	ligas_tmp = []
	for i in t:
		if country.lower() in i['href']:
			#print("--->", str(i.text))
			ligas_tmp.append(i['href'])

	ligas[country.lower()] = ligas_tmp

for entry, lst in ligas.items():
	print("+", entry)
	for league in lst:
		print("\t--", league[len("/soccer/") + len(entry) + 1:])
		print(league)
		print('ttps://www.oddsportal.com' + str(league) + "/results/")
		ser = Service("/usr/lib/chromium-browser/chromedriver")
		driver = webdriver.Chrome(options=options, service=ser)
		driver.get('https://www.oddsportal.com' + str(league) + "/results/")
		soup = BeautifulSoup(driver.page_source, 'html.parser')
		allYears = [x.text for x in soup.find_all('ul', class_='main-filter')[1].find_all('li')]
		allYearsHrefs = [x.find('a')['href'] for x in soup.find_all('ul', class_='main-filter')[1].find_all('li')]

		for idx, year in enumerate(allYears):
			page = 1
			print("Info for year ", allYearsHrefs[idx])
			while True: #Ver todas as páginas
				print("Scrapping page {}".format(page))
				ser = Service("/usr/lib/chromium-browser/chromedriver")
				driver = webdriver.Chrome(options=options, service=ser)
				print('https://www.oddsportal.com' + str(allYearsHrefs[idx]) + "#/page/{}/".format(page))
				driver.get('https://www.oddsportal.com' + str(allYearsHrefs[idx]) + "#/page/{}/".format(page))
				soup = BeautifulSoup(driver.page_source, 'html.parser')
				page+=1
				try:
					leagueName = soup.find('th', class_='first2').find_all('a')[-1].text
				except:
					break
				table = soup.find('table').find('tbody')

				game_list = table.find_all('tr')
				not_wanted = table.find_all('tr', class_="table-dummyrow") + table.find_all('tr', class_="center")

				for item in not_wanted:
					if item in game_list:
						game_list.remove(item)

				print(len(game_list))

				for game in game_list:
					try:
						print("\t\t+++++++++")
						info_game = game.find_all('td')
						jogo = info_game[1].text
						print("\t\t--->",jogo)	
						referencia = info_game[1].find('a')['href']
						res_fim = info_game[2].text
						print("\t\t--->",res_fim)
						odd1 = info_game[3].text
						oddX = info_game[4].text
						odd2 = info_game[5].text
						print("\t\t--->",odd1)
						print("\t\t--->",oddX)
						print("\t\t--->",odd2)

						driver = webdriver.Chrome(options=options, service=ser)
						if checkGameExists(cursor, jogo, leagueName, year):
							print("Game already exists... continuing...")
							continue
						driver.get('https://www.oddsportal.com' + str(referencia))
						soup = BeautifulSoup(driver.page_source, 'html.parser')
						driver.quit()
						res_meio = soup.find('p', class_="result").text[18:21]
						print("\t\t----->",res_meio)

						current_regionID = addGameItem(cursor, leagueName, entry, year, jogo,odd1, oddX, odd2, res_meio, res_fim)
						connection.commit()
					except:
						pass