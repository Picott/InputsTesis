import os
import pandas as pd
import numpy as np

base_dir = os.path.dirname(os.path.abspath(__file__))

# === Rutas de archivos ===

RUTA_INPUT = os.path.join(base_dir, '..', '..', 'Vshale', 'withID','pozos_procesados_vis.csv')
RUTA_SALIDA = os.path.join(base_dir, '..', '..', 'Vshale', 'withID','pozos_segmentados.csv')

# === Parámetros de segmentación ===
UMBRAL = 0.05        # Diferencia mínima para detectar cambio de segmento
WINDOW_SIZE = 5      # Tamaño del suavizado (si no quieres, pon 1)

# === Verificar que el archivo existe antes de cargarlo ===
if not os.path.exists(RUTA_INPUT):
    raise FileNotFoundError(f"⚠ ERROR: No se encontró el archivo en {RUTA_INPUT}")

# === Cargar el archivo unificado ===
df = pd.read_csv(RUTA_INPUT)
print(f"✅ Archivo cargado correctamente desde: {RUTA_INPUT}")

# Verificar que las columnas necesarias estén en el archivo
columnas_necesarias = ['Pozo_ID', 'DEPTH', 'Vshale', 'X', 'Y']
if not all(col in df.columns for col in columnas_necesarias):
    raise ValueError(f"⚠ ERROR: El archivo no contiene todas las columnas necesarias: {columnas_necesarias}")

# Ordenar por pozo y profundidad
df.sort_values(by=['Pozo_ID', 'DEPTH'], inplace=True)

# Aplicar segmentación **por cada pozo**
df['Segmento_ID'] = 1  # Inicializar columna
df['Vshale_smooth'] = df.groupby('Pozo_ID')['Vshale'].transform(lambda x: x.rolling(window=WINDOW_SIZE, min_periods=1).mean())
df['Delta'] = df.groupby('Pozo_ID')['Vshale_smooth'].diff().abs()

# Asignar segmentos dentro de cada pozo
segmento_actual = 1
for i in range(1, len(df)):
    # Si es un nuevo pozo, reiniciar el contador de segmentos
    if df.iloc[i]['Pozo_ID'] != df.iloc[i - 1]['Pozo_ID']:
        segmento_actual = 1
    # Si Delta supera el umbral, creamos un nuevo segmento
    elif df.iloc[i]['Delta'] > UMBRAL:
        segmento_actual += 1
    df.at[df.index[i], 'Segmento_ID'] = segmento_actual

# Guardar el resultado en un solo archivo CSV
df.drop(columns=['Vshale_smooth', 'Delta'], inplace=True)  # Eliminar columnas auxiliares
df.to_csv(RUTA_SALIDA, index=False)

print(f"✅ Segmentación completada. Archivo guardado en: {RUTA_SALIDA}")
