import pandas as pd
import pyvista as pv
import numpy as np
from scipy.spatial import cKDTree

# === RUTA DEL ARCHIVO ===
RUTA_INPUT = "C:/Users/Anjuli/Documents/Inputs/Vshale/withID/pozos_segmentados.csv"

# === Cargar datos ===
df = pd.read_csv(RUTA_INPUT)

# Verificar que las columnas necesarias estén en el archivo
columnas_necesarias = ['Pozo_ID', 'DEPTH', 'X', 'Y', 'Vshale']
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

# === Visualizar en PyVista ===
plotter = pv.Plotter()
plotter.add_mesh(structured_grid, scalars="Vshale", cmap="viridis", opacity=0.5)
plotter.add_axes()
plotter.add_title("Interpolación 3D de Vshale (IDW)")
plotter.show()
