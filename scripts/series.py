from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from time import sleep
import pandas as pd
import sqlite3
import json
import os

# Inicializar el navegador y hago el proceso para ingresar al link de starz de las peliculas

driver = webdriver.Chrome()
driver.maximize_window()
url = "https://www.starz.com/us/en/view-all/blocks/118535307"
driver.get(url)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/starz-root/div/div[1]/section/starz-view-all/div/div/div/div/section/div/div/nav/ul/li[1]/span")))

sleep(3)

html = driver.execute_script('return document.documentElement.outerHTML')
dom = BS(html, 'html.parser')
link_series = dom.find_all('article', attrs = {'class': "content-link"})

series = []

count = 0

# Creo un for para recorrer cada serie dentro de la pagina y obtener sus metadatos a partir de los xpath principales

for i in range(len(link_series)):
    try: 
        link_serie = link_series[i].find('a')['href']
        link_serie_final = 'https://www.starz.com' + link_serie
        driver.get(link_serie_final)

        html = driver.execute_script('return document.documentElement.outerHTML')
        dom = BS(html, 'html.parser')

        count += 1

        sleep(2)

        parent_titulo = driver.find_element(By.XPATH, "/html/body/div/div/section/main/div/section[1]/div[2]/div")
        titulo = parent_titulo.find_element(By.TAG_NAME, "h1").text.strip()
        spans = parent_titulo.find_elements(By.TAG_NAME, "span")

        parent_caps = driver.find_element(By.XPATH, "/html/body/div/div/section/main/div/section[1]/div[2]/div/div[2]/div")
        caps = parent_caps.find_element(By.TAG_NAME, "h2").text.strip()
        
        spans_text = [span.text.strip() for span in spans]

        año = spans_text[2]
        genero = spans_text[1]
        
        spans_text = [span.text.strip() for span in spans]

        descripcion = spans_text[3]
        actores = driver.find_element(By.XPATH, "/html/body/div/div/section/main/div/section[1]/div[2]/div/p[2]").text.strip()
        tipo = "Serie"

        print("Serie: " + titulo + " | Capitulos: " + caps + " | Año: " + año + " | Sinopsis: " + descripcion + " | Genero: " + genero + " | Actores: " + actores + " | Link: " + link_serie_final)
    
    
    except:
        print("No se encontro el elemento")
        

    caracteristicas_series = {'ID': count, 'Titulo': titulo, 'Capitulos' : caps, 'Año' : año,  'Sinopsis' : descripcion,  'Genero' : genero,  'Actores' : actores, 'Tipo' : tipo, 'Link' : link_serie_final}
    series.append(caracteristicas_series) 
    
    print('\n------------------------------------------------------------')    
    print('Serie: ',titulo, ', Capitulos:', caps, ', Año:', año,  ', Sinopsis:', descripcion,  ', Genero:', genero,  ', Actores:', actores, ', Tipo:', tipo,', Link: ',link_serie_final)
    print('Datos de ',titulo, ' cargados')
    print('\nRestan: ', len(link_series) - count, ' series')        
    print('------------------------------------------------------------') 


# Guardo los datos obtenidos en un Json, luego lo paso a csv y por ultimo hago la conexcion a la base de datos.

with open('database/series.json', 'w', encoding='utf-8') as archivo_json_series:
    json.dump(series, archivo_json_series, ensure_ascii = False, indent = 2)


df = pd.read_json("database/series.json")
df.to_csv("database/series.csv", index=False)

print("El archivo CSV se ha creado correctamente.")
        
if not os.path.exists('database/series.db'):

    conn = sqlite3.connect('database/series.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS series
                      (ID INTEGER, Titulo TEXT, Capitulos INTEGER, Año TEXT, Sinopsis TEXT, Genero TEXT, Actores TEXT, Tipo TEXT, Link TEXT)''')

    conn.commit()

    conn.close()

conn = sqlite3.connect('database/series.db')
cursor = conn.cursor()

for serie in series:
    (cursor.execute("INSERT INTO series (ID, Titulo, Capitulos, Año, Sinopsis, Genero, Actores, Tipo, Link) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (serie['ID'], serie['Titulo'], serie['Capitulos'], serie['Año'], serie['Sinopsis'], serie['Genero'], serie['Actores'], serie['Tipo'], serie['Link'])))

conn.commit()

conn.close()

print("Los datos se han insertado en la base de datos correctamente.")
print('Fin del scrapping para las series')

# Finalizo el proceso
driver.quit()