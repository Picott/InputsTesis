import pandas as pd
import numpy as np
import glob
import os
import matplotlib.pyplot as plt

base_dir = os.path.dirname(os.path.abspath(__file__))

# Ruta donde están los archivos CSV de los pozos
ruta_pozos = os.path.join(base_dir, '..', '..', 'Resources', 'csv', '*.csv')
ruta_salida = os.path.join(base_dir, '..', '..', 'Vshale', 'withID')  # Carpeta de salida
os.makedirs(ruta_salida, exist_ok=True)  # Asegurar que la carpeta existe

# Lista de archivos CSV en la carpeta
archivos_pozos = glob.glob(ruta_pozos)

# Inicializar lista para almacenar datos
lista_datos = []

# Leer y procesar cada archivo CSV
for archivo in archivos_pozos:
    # Extraer el nombre del pozo desde el nombre del archivo
    nombre_pozo = os.path.basename(archivo).split('.')[0]  # Elimina la extensión .csv

    data_pozos = pd.read_csv(archivo)
    
    print(f"📂 {archivo} - Columnas detectadas: {list(data_pozos.columns)}")  # <-- Ver columnas antes de renombrar
    
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
    
    # Asegurarnos de que X e Y existan en el DataFrame
    if 'X' not in data_pozos.columns or 'Y' not in data_pozos.columns:
        print(f"⚠ Advertencia: {nombre_pozo} no tiene X, Y. Se descarta.")
        continue  # Saltamos este pozo si no tiene coordenadas

    # 🔍 Verificar si hay más de una coordenada X, Y en el pozo
    x_unique = data_pozos['X'].nunique()
    y_unique = data_pozos['Y'].nunique()
    
    if x_unique > 1 or y_unique > 1:
        print(f"⚠ Advertencia: {nombre_pozo} tiene múltiples coordenadas X, Y. Se usará la más frecuente.")
        # Seleccionamos la coordenada más frecuente
        data_pozos['X'] = data_pozos['X'].mode()[0]
        data_pozos['Y'] = data_pozos['Y'].mode()[0]
    
    # Verificar si el archivo contiene las columnas necesarias
    if 'GR' in data_pozos.columns and 'DEPTH' in data_pozos.columns:
        
        # Normalización Min-Max del Gamma Ray
        GR_min = data_pozos['GR'].min()
        GR_max = data_pozos['GR'].max()
        
        if GR_min == GR_max:
            # Si todo el GR es igual, se asigna 0.0 para evitar dividir por cero
            data_pozos['GR_norm'] = 0.0
        else:
            data_pozos['GR_norm'] = (data_pozos['GR'] - GR_min) / (GR_max - GR_min)
        
        # Cálculo del Vshale con la ecuación de Larionov para formaciones modernas
        data_pozos['Vshale'] = 0.083 * (2 ** (3.7 * data_pozos['GR_norm']) - 1)
        
        # Asignar Pozo_ID basado en el nombre del archivo
        data_pozos['Pozo_ID'] = nombre_pozo

        # Guardar cada pozo con Vshale en un gráfico
        plt.figure(figsize=(5, 8))
        plt.plot(data_pozos['Vshale'], data_pozos['DEPTH'], label='Vshale', color='brown')
        plt.gca().invert_yaxis()
        plt.xlabel("Vshale")
        plt.ylabel("DEPTH (m)")
        plt.title(f"Perfil de Vshale - {nombre_pozo}")
        plt.legend()
        plt.grid()
        
        # Guardar figura como PNG
        grafico_salida = os.path.join(ruta_salida, f"{nombre_pozo}_Vshale.png")
        plt.savefig(grafico_salida)
        plt.close()
        
        # Agregar el DataFrame procesado a la lista
        lista_datos.append(data_pozos)
        
        print(f"✅ {archivo} procesado correctamente.")
    else:
        print(f"⚠ {archivo} omitido, no contiene GR o DEPTH.")

# Unir todos los DataFrames en uno solo y guardar
if lista_datos:
    data_final = pd.concat(lista_datos, ignore_index=True)
    output_file = os.path.join(ruta_salida, "pozos_procesados_vis.csv")
    
    # Exportar columnas claves, incluyendo Pozo_ID, X y Y
    data_final[['Pozo_ID', 'DEPTH', 'GR', 'GR_norm', 'Vshale', 'X', 'Y']].to_csv(output_file, index=False)
    print(f"✅ Datos guardados en {output_file}")
else:
    print("❌ No se encontraron datos válidos.")
