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
import re

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

temporadas = []

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

        # Creo un if para identificar si la serie tiene el div particular de las temporadas

        if driver.find_elements(By.XPATH, "/html/body/div/div/section/main/div/section[4]/div/div/div[1]/div/a/div[3]"):

            divs = driver.find_elements(By.XPATH, "/html/body/div/div/section/main/div/section[4]/div/div/div")
            cantidad_divs = len(divs)
            print("La serie ", titulo, " tiene ", cantidad_divs ," temporadas")

            tempos = cantidad_divs

            # Una vez que obtengo la cantidad de temporadas que tiene hago un for para entrar a cada temporada y obtener los metadatos de cada capitulo para cada temporada

            for i in range(cantidad_divs):

                tempo = driver.find_element(By.XPATH, f"/html/body/div/div/section/main/div/section[4]/div/div/div[{i+1}]/div/a")
                tempo.click()

                sleep(2)

                temporadas_selec = driver.find_element(By.XPATH, "/html/body/div[1]/div/section/main/div/section[4]/div[1]/div")

                texto = temporadas_selec.text.strip()
                numeros = re.findall(r'\d+', texto)
                texto = ''.join(numeros)
                caps = texto

                print("La temporada ", i+1 , " tiene ", caps, " capitulos")

                sleep(2)

                for j in range(int(texto)):

                    nom_xpath = f"/html/body/div[1]/div/section/main/div/section[4]/div/div[2]/div/div[{j+1}]/div[2]/button"
                    dura_xpath = f"/html/body/div[1]/div/section/main/div/section[4]/div/div[2]/div/div[{j+1}]/div[3]"
                    desc_xpath = f"/html/body/div[1]/div/section/main/div/section[4]/div/div[2]/div/div[{j+1}]/span"

                    nom = driver.find_element(By.XPATH, nom_xpath)
                    nom_text = nom.text.strip()

                    dura = driver.find_element(By.XPATH, dura_xpath)
                    dura_text = dura.text.strip()

                    desc = driver.find_element(By.XPATH, desc_xpath)
                    desc_text = desc.text.strip()

                    print("Nombre del capitulo", j+1, " :", nom_text)
                    print("Duracion:", dura_text)
                    print("Descripcion:", desc_text)

                driver.back()
                
                sleep(2)

        else:    
            
            # En el caso que no se identificque el div para las temporadas quiere decir que la serie consta de una unica temporada entonces paso a obtener los metadatas de los capitulos directamente
            
            parent_titulo = driver.find_element(By.XPATH, "/html/body/div/div/section/main/div/section[1]/div[2]/div")
            titulo = parent_titulo.find_element(By.TAG_NAME, "h1").text.strip()

            temporadas_selec = driver.find_element(By.XPATH, "/html/body/div[1]/div/section/main/div/section[4]/div[1]/div")
            texto = temporadas_selec.text.strip()
            numeros = re.findall(r'\d+', texto)
            texto = ''.join(numeros)
            caps = str(texto)

            print("La serie ", titulo, " tiene una temporada de ", caps, " capitulos")

            for z in range(int(texto)):
                nom_xpath = f"/html/body/div[1]/div/section/main/div/section[4]/div[2]/div/div[{z+1}]/div[2]/button"
                dura_xpath = f"/html/body/div[1]/div/section/main/div/section[4]/div[2]/div/div[{z+1}]/div[3]"
                desc_xpath = f"/html/body/div[1]/div/section/main/div/section[4]/div[2]/div/div[{z+1}]/span"
                nom = driver.find_element(By.XPATH, nom_xpath)
                nom_text = nom.text.strip()
                dura = driver.find_element(By.XPATH, dura_xpath)
                dura_text = dura.text.strip()
                desc = driver.find_element(By.XPATH, desc_xpath)
                desc_text = desc.text.strip()
                tempos = "1"
                print("Nombre del capitulo", z+1, ":", nom_text)
                print("Duracion:", dura_text)
                print("Descripcion:", desc_text)

        print('\n------------------------------------------------------------')    
        print('Serie: ',titulo, ', Capitulos:', caps, ', Nombre del capitulo:', nom_text,  ', Duracion y Fecha:', dura_text,  ', Sinopsis del capitulo:', desc_text,  ', Link:', link_serie_final)
        print('Datos de ',titulo, ' cargados')
        print('\nRestan: ', len(link_series) - count, ' series')        
        print('------------------------------------------------------------') 

    except:
        print("No se encontro el elemento")
    
    caracteristicas_temporadas = {'Titulo': titulo, 'Temporadas': tempos, 'Capitulos' : caps, 'Nombre del capitulo' : nom_text, 'Duracion y Fecha' : dura_text,  'Sinopsis del capitulo' : desc_text, 'Link' : link_serie_final}
    temporadas.append(caracteristicas_temporadas)

# Guardo los datos obtenidos en un Json, luego lo paso a csv y por ultimo hago la conexcion a la base de datos.

with open('database/temporadas.json', 'w', encoding='utf-8') as archivo_json_temporadas:
    json.dump(temporadas, archivo_json_temporadas, ensure_ascii=False, indent=2)

df = pd.read_json("database/temporadas.json")
df.to_csv("database/temporadas.csv", index=False)

print("El archivo CSV se ha creado correctamente.")

if not os.path.exists('database/temporadas.db'):

    conn = sqlite3.connect('database/temporadas.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS temporadas
                      (Titulo TEXT, Temporadas TEXT, Capitulos INTEGER, Ultimo_Cap TEXT, Dura_Fecha TEXT, Sinopsis TEXT, Link TEXT)''')

    conn.commit()
    conn.close()

conn = sqlite3.connect('database/temporadas.db')
cursor = conn.cursor()

for temporada in temporadas:
    cursor.execute("INSERT INTO temporadas (Titulo, Temporadas, Capitulos, Ultimo_Cap, Dura_Fecha, Sinopsis, Link) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (temporada['Titulo'], temporada['Temporadas'], temporada['Capitulos'], temporada['Nombre del capitulo'], temporada['Duracion y Fecha'], temporada['Sinopsis del capitulo'], temporada['Link']))

conn.commit()
conn.close()


# Lo que va a pasar en esta parte cuando se guarden los datos en la base de datos es que se va a guardar el ultimo metadata que se leyó
# Es decir, que si la serie tiene 10 capitulos se va a guardar en la tabla de la base de datos el nombre, año y descripcion del ultimo capitulo y no todos
# Ya que no estoy metiendo los textos en de todos los capitulos en una lista. De todas maneras opté por dejarlo de esta forma ya que si lo hacia enlistando los capitulos 
# Deberia hacer una base de datos donde las tablas tengan foreign key para poder referencias los capitulos a las temporadas y a las series. Pero como estoy optando por usar sqlite3 
# Y crear un archivo .db eso se complica por lo que decidí dejarlo de esta manera pero aclarar eso ya que entiendo que lo importante es mostrar la obtencion de los datos.


print("Los datos se han insertado en la base de datos correctamente.")
print('Fin del scrapping para las temporadas y capitulos')

# Finalizo el proceso
driver.quit()