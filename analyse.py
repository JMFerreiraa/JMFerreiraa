import requests
from bs4 import BeautifulSoup
import sqlite3


connection = sqlite3.connect("oddsData.db")
connection.row_factory = lambda cursor, row: row[0]
cursor = connection.cursor()


cursor.execute("SELECT region FROM games")

a = cursor.fetchall()

countries = sorted(list(set(a)))

for country in countries:
	print("--------------------------------- // -------------------------------------------------")

	cursor.execute("SELECT league FROM games WHERE region = '{}'".format(country))
	a = cursor.fetchall()
	leagues = sorted(list(set(a)))
	for league in leagues:
		print("---> ", league, "(", country, ")")
		cursor.execute("SELECT COUNT(*) FROM games WHERE region = '{}' AND league = '{}'".format(country, league))
		a = cursor.fetchone()
		print("\t Total de jogos ---->" , a)
		cursor.execute("SELECT COUNT(*) FROM games WHERE region = '{}' AND league = '{}' AND (resultMID = '1:1' OR resultMID = '2:2' OR resultMID = '3:3')".format(country, league))
		a = cursor.fetchone()
		print("\t Empates ---->" , a)
		cursor.execute("SELECT COUNT(*) FROM games WHERE region = '{}' AND league = '{}' AND odd1 > odd2 AND odd2 > 2 AND odd2 < 3 and odd1 > 2 and odd1 < 3".format(country, league))
		a = cursor.fetchone()
		print("\t Requirements ---->" , a)
		cursor.execute("SELECT COUNT(*) FROM games WHERE region = '{}' AND league = '{}' AND odd1 > odd2 AND odd2 > 2 AND odd2 < 3 and odd1 > 2 and odd1 < 3 AND (resultMID = '1:1' OR resultMID = '2:2' OR resultMID = '3:3')".format(country, league))
		a = cursor.fetchone()
		print("\t Requirements + Empates ---->" , a)