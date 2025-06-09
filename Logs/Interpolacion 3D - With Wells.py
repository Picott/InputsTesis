import pandas as pd
import pyvista as pv
import numpy as np
from scipy.spatial import cKDTree

# === RUTA DEL ARCHIVO ===
RUTA_INPUT = "C:/Users/Anjuli/Documents/Inputs/Vshale/withID/pozos_segmentados.csv"

# === Cargar datos ===
df = pd.read_csv(RUTA_INPUT)

# Verificar que las columnas necesarias estén en el archivo
columnas_necesarias = ['Pozo_ID', 'DEPTH', 'X', 'Y', 'Vshale', 'Segmento_ID']
if not all(col in df.columns for col in columnas_necesarias):
    raise ValueError(f"⚠ ERROR: El archivo no contiene todas las columnas necesarias: {columnas_necesarias}")

# === Convertir DEPTH a Z (negativo para que profundidad sea "hacia abajo") ===
df['Z'] = -df['DEPTH']

# === Crear grid 3D ===
grid_size = 50  # Ajusta esto según el tamaño de tu modelo
x_min, x_max = df['X'].min(), df['X'].max()
y_min, y_max = df['Y'].min(), df['Y'].max()
z_min, z_max = df['Z'].min(), df['Z'].max()

# Crear malla regular en el espacio 3D
x = np.linspace(x_min, x_max, grid_size)
y = np.linspace(y_min, y_max, grid_size)
z = np.linspace(z_min, z_max, grid_size)
X, Y, Z = np.meshgrid(x, y, z, indexing="ij")

# Aplanar las coordenadas de la malla
grid_points = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])

# === Aplicar interpolación IDW (Inverse Distance Weighting) ===
tree = cKDTree(df[['X', 'Y', 'Z']].values)
distances, idx = tree.query(grid_points, k=5)  # Usamos los 5 puntos más cercanos

# Pesos IDW
weights = 1 / (distances + 1e-10)  # Evitamos división por cero
weights /= weights.sum(axis=1, keepdims=True)

# Interpolar valores de Vshale
interpolated_values = np.sum(weights * df['Vshale'].values[idx], axis=1)

# Crear objeto StructuredGrid de PyVista
structured_grid = pv.StructuredGrid(X, Y, Z)

# 🔴 VERIFICACIÓN DE DIMENSIONES 🔴
if interpolated_values.shape[0] != structured_grid.n_points:
    raise ValueError(f"⚠ ERROR: La cantidad de valores interpolados ({interpolated_values.shape[0]}) "
                     f"no coincide con el número de puntos en la malla ({structured_grid.n_points}).")

structured_grid["Vshale"] = interpolated_values  # Asignar valores corregidos

# === Crear nube de puntos de los pozos ===
points = df[['X', 'Y', 'Z']].values
cloud = pv.PolyData(points)
cloud['Segmento_ID'] = df['Segmento_ID']  # Asignar colores por segmento

# === Crear visualización en PyVista ===
plotter = pv.Plotter()

# Añadir la interpolación 3D como volumen
plotter.add_mesh(structured_grid, scalars="Vshale", cmap="viridis", opacity=0.5)

# Añadir los pozos como nube de puntos
plotter.add_mesh(cloud, scalars="Segmento_ID", cmap="rainbow", point_size=5, render_points_as_spheres=True)

# Añadir etiquetas con los nombres de los pozos
pozos_unicos = df.groupby('Pozo_ID').first().reset_index()
for _, pozo in pozos_unicos.iterrows():
    plotter.add_point_labels(
        [pozo['X'], pozo['Y'], pozo['Z']],  # Coordenadas en 3D
        [pozo['Pozo_ID']],  # Etiqueta con el nombre del pozo
        font_size=12,
        point_color='black',
        text_color='white',
        always_visible=True,
    )

# Calcular el centro de la nube de puntos para ajustar la cámara
center = [(x_min + x_max) / 2, (y_min + y_max) / 2, (z_min + z_max) / 2]

# Ajustar cámara para incluir todo
plotter.camera_position = [
    (center[0] + 2000, center[1] + 2000, center[2] + 500),  # Posición de la cámara
    center,  # Punto de enfoque
    (0, 0, 1)  # Vector de orientación (Z hacia arriba)
]

plotter.add_axes()
plotter.add_title("Interpolación 3D de Vshale con Pozos y Nombres")
plotter.show()
