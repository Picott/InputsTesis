import pandas as pd
import pyvista as pv
import numpy as np
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

# === RUTA DEL ARCHIVO ===
RUTA_INPUT = os.path.join(base_dir, '..', '..', 'Vshale', 'withID','pozos_segmentados.csv')

# === Cargar datos ===
df = pd.read_csv(RUTA_INPUT)

# Verificar que las columnas necesarias estén en el archivo
columnas_necesarias = ['Pozo_ID', 'DEPTH', 'X', 'Y', 'Segmento_ID']
if not all(col in df.columns for col in columnas_necesarias):
    raise ValueError(f"⚠ ERROR: El archivo no contiene todas las columnas necesarias: {columnas_necesarias}")

# === Convertir DEPTH a Z (negativo para que profundidad sea "hacia abajo") ===
df['Z'] = -df['DEPTH']

# === Crear objeto de nube de puntos en PyVista ===
points = df[['X', 'Y', 'Z']].values
cloud = pv.PolyData(points)

# Asignar Segmento_ID como propiedad escalar para colorear
cloud['Segmento_ID'] = df['Segmento_ID']

# === Crear visualización con etiquetas ===
plotter = pv.Plotter()

# Añadir los puntos coloreados por Segmento_ID
plotter.add_mesh(cloud, scalars='Segmento_ID', cmap='viridis', point_size=5, render_points_as_spheres=True)

# Calcular el centro de la nube de puntos para ajustar la cámara
x_min, x_max = df['X'].min(), df['X'].max()
y_min, y_max = df['Y'].min(), df['Y'].max()
z_min, z_max = df['Z'].min(), df['Z'].max()
center = [(x_min + x_max) / 2, (y_min + y_max) / 2, (z_min + z_max) / 2]

# Ajustar cámara para incluir todos los pozos
plotter.camera_position = [
    (center[0] + 2000, center[1] + 2000, center[2] + 500),  # Posición de la cámara
    center,  # Punto de enfoque
    (0, 0, 1)  # Vector de orientación (Z hacia arriba)
]

# Añadir etiquetas con los nombres de los pozos en la superficie
pozos_unicos = df.groupby('Pozo_ID').first().reset_index()
for _, pozo in pozos_unicos.iterrows():
    plotter.add_point_labels(
        [pozo['X'], pozo['Y'], pozo['Z']],
        [pozo['Pozo_ID']],  # Debe ser una lista de etiquetas
        font_size=12,
        point_color='red',
        text_color='white',
    )

plotter.add_axes()
plotter.add_title("Segmentación de Pozos (Nube de Puntos 3D con Etiquetas)")
plotter.show()
