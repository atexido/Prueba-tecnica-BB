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
url = "https://www.starz.com/us/en/view-all/blocks/892880447"
driver.get(url)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/starz-root/div/div[1]/section/starz-view-all/div/div/div/div/section/div/div/nav/ul/li[1]/span")))

sleep(3)

html = driver.execute_script('return document.documentElement.outerHTML')
dom = BS(html, 'html.parser')
link_peliculas = dom.find_all('article', attrs = {'class': "content-link"})

peliculas = []

count = 0

# Creo un for para recorrer cada pelicula dentro de la pagina y obtener sus metadatos a partir de los xpath principales

for i in range(len(link_peliculas)):
    try: 
        link_pelicula = link_peliculas[i].find('a')['href']
        link_pelicula_final = 'https://www.starz.com' + link_pelicula
        driver.get(link_pelicula_final)

        html = driver.execute_script('return document.documentElement.outerHTML')
        dom = BS(html, 'html.parser')

        count += 1

        sleep(2)

        parent_titulo = driver.find_element(By.XPATH, "/html/body/div/div/section/main/div/section[1]/div[2]/div")
        titulo = parent_titulo.find_element(By.TAG_NAME, "h1").text.strip()
        spans = parent_titulo.find_elements(By.TAG_NAME, "span")

        parent_spans = driver.find_element(By.XPATH, "/html/body/div/div/section/main/div/section[1]/div[2]/div/div[1]")
        spans_text = [span.text.strip() for span in spans]

        año = spans_text[3]
        genero = spans_text[2]
        duracion = spans_text[1]
        descripcion = spans_text[4]
        actores = driver.find_element(By.XPATH, "/html/body/div/div/section/main/div/section[1]/div[2]/div/p[2]").text.strip()
        tipo = "Pelicula"

        print("Pelicula: " + titulo + " | Duracion: " + duracion + " | Año: " + año + " | Sinopsis: " + descripcion + " | Genero: " + genero + " | Actores: " + actores + " | Link: " + link_pelicula_final)
    
    
    except:
        vacio = 'None'
        print(vacio)

    caracteristicas_peliculas = {'ID': count, 'titulo': titulo, 'Duracion' : duracion, 'Año' : año,  'Sinopsis' : descripcion,  'Genero' : genero,  'Actores' : actores,  'Tipo' : tipo, 'Link' : link_pelicula_final}
    peliculas.append(caracteristicas_peliculas) 
    
    print('\n------------------------------------------------------------')    
    print('Pelicula: ',titulo, ', Duracion:', duracion, ', Año:', año,  ', Sinopsis:', descripcion,  ', Genero:', genero,  ', Actores:', actores, ', Link: ',link_pelicula_final)
    print('\nFaltan: ', len(link_peliculas) - count, ' Peliculas')        
    print('--------------------------------------------------------------') 

# Guardo los datos obtenidos en un Json, luego lo paso a csv y por ultimo hago la conexcion a la base de datos.

with open('database/peliculas.json', 'w', encoding='utf-8') as archivo_json_peliculas:
    json.dump(peliculas, archivo_json_peliculas, ensure_ascii = False, indent = 2)


df = pd.read_json("database/peliculas.json")
df.to_csv("database/peliculas.csv", index=False)

print("El archivo CSV se ha creado correctamente.")

if not os.path.exists('database/peliculas.db'):

    conn = sqlite3.connect('database/peliculas.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS peliculas
                      (ID INTEGER, Titulo TEXT, Duracion TEXT, Año INTEGER, Sinopsis TEXT, Genero TEXT, Actores TEXT, Tipo TEXT, Link TEXT)''')

    conn.commit()
    conn.close()

conn = sqlite3.connect('database/peliculas.db')
cursor = conn.cursor()

for pelicula in peliculas:
    cursor.execute("INSERT INTO peliculas (ID, Titulo, Duracion, Año, Sinopsis, Genero, Actores, Tipo, Link) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (pelicula['ID'], pelicula['titulo'], pelicula['Duracion'], pelicula['Año'], pelicula['Sinopsis'], pelicula['Genero'], pelicula['Actores'], pelicula['Tipo'], pelicula['Link']))

conn.commit()

conn.close()

print("Los datos se han insertado en la base de datos correctamente.")
print('Fin del scrapping para las peliculas')

# Finalizo el proceso
driver.quit()