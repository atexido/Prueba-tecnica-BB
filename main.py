import subprocess

#Ejecuto los scripts en orden

print("Leyendo las peliculas...")
subprocess.run(["python", "scripts/peliculas.py"])


print("Leyendo las series...")
subprocess.run(["python", "scripts/series.py"])


print("Leyendo las temporadas...")
subprocess.run(["python", "scripts/temporadas_capitulos.py"])

print('SCRAPPING FINALIZADO')