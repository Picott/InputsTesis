import pandas as pd
import numpy as np
import glob
import os

# Ruta donde están los archivos CSV de los pozos
ruta_pozos = r"C:/Users/Anjuli/Documents/Inputs/Logs/CSV/*.csv"
ruta_salida = r"C:/Users/Anjuli/Documents/Inputs/Vshale"  # Carpeta de salida
os.makedirs(ruta_salida, exist_ok=True)  # Asegurar que la carpeta existe

# Lista de archivos CSV en la carpeta
archivos_pozos = glob.glob(ruta_pozos)

# Inicializar lista para almacenar datos
lista_datos = []

# Leer y procesar cada archivo CSV
for archivo in archivos_pozos:
    data_pozos = pd.read_csv(archivo)
    
    print(f"📂 {archivo} - Columnas detectadas: {list(data_pozos.columns)}")  # Ver columnas antes de renombrar
    
    # Normalizar nombres de columnas en caso de que tengan nombres alternativos
    column_map = {
        'DEPTH': ['DEPTH', 'DEPT', 'MD', 'Measured Depth'],
        'GR': ['GR', 'Gamma Ray', 'GR_ARC', 'GR_IMP', 'GR:1', 'GR:2', 'GR:3']
    }
    
    for key, possible_names in column_map.items():
        for name in possible_names:
            if name in data_pozos.columns:
                data_pozos.rename(columns={name: key}, inplace=True)
                break
    
    # Asegurar que X e Y existen (si no, crearlas vacías).
    # Así mantenemos el mismo esquema y evitamos errores de columnas faltantes.
    for coord_col in ['X', 'Y']:
        if coord_col not in data_pozos.columns:
            data_pozos[coord_col] = pd.NA
    
    print(f"🔄 {archivo} - Columnas después de renombrar: {list(data_pozos.columns)}")  # Ver columnas después de renombrar
    
    # Verificar si el archivo contiene las columnas necesarias
    if 'GR' in data_pozos.columns and 'DEPTH' in data_pozos.columns:
        
        # Normalización Min-Max del Gamma Ray
        GR_min = data_pozos['GR'].min()
        GR_max = data_pozos['GR'].max()
        # Evitar división por cero si GR_min == GR_max
        if GR_min == GR_max:
            data_pozos['GR_norm'] = 0.0
        else:
            data_pozos['GR_norm'] = (data_pozos['GR'] - GR_min) / (GR_max - GR_min)
        
        # Cálculo del Vshale con la ecuación de Larionov para formaciones modernas
        data_pozos['Vshale'] = 0.083 * (2 ** (3.7 * data_pozos['GR_norm']) - 1)
        
        # Agregar el DataFrame procesado a la lista
        lista_datos.append(data_pozos)
        
        print(f"✅ {archivo} procesado correctamente.")
    else:
        print(f"⚠ {archivo} omitido, no contiene GR o DEPTH.")

# Unir todos los DataFrames en uno solo y guardar
if lista_datos:
    data_final = pd.concat(lista_datos, ignore_index=True)
    output_file = os.path.join(ruta_salida, "pozos_procesados.csv")
    
    # Exportar solo las columnas clave
    # (Si deseas incluir más columnas, agrégalas a la lista)
    data_final[['DEPTH', 'GR', 'GR_norm', 'Vshale', 'X', 'Y']].to_csv(output_file, index=False)
    
    print(f"✅ Datos guardados en {output_file}")
else:
    print("❌ No se encontraron datos válidos.")
