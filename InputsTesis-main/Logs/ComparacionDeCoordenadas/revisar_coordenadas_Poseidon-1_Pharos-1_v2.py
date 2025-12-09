import pandas as pd
import glob

# Ruta donde están los archivos CSV de los pozos individuales
ruta_pozos = "C:/Users/Anjuli/Documents/Inputs/Logs/CSV/*.csv"

# Filtrar los archivos de Poseidon y Pharos
archivos_pozos = glob.glob(ruta_pozos)
archivos_revisar = [f for f in archivos_pozos if "Poseidon" in f or "Pharos" in f]

# Verificar las coordenadas de estos archivos
for archivo in archivos_revisar:
    df = pd.read_csv(archivo)
    print(f"\n📂 Archivo: {archivo}")
    
    # Mostrar si tiene columnas X, Y
    if 'X' in df.columns and 'Y' in df.columns:
        print(df[['X', 'Y']].drop_duplicates())  # Mostrar coordenadas únicas
    else:
        print("⚠ Este archivo no tiene coordenadas X, Y.")
