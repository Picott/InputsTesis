import pandas as pd
import pyvista as pv
import numpy as np
from scipy.spatial import cKDTree
import os

# ==========================================
# 1. CARGA DE DATOS
# ==========================================
base_dir = os.path.dirname(os.path.abspath(__file__))
# Ajusta la ruta si es necesario
archivo = os.path.join(base_dir, '..', '..', 'Vshale', 'withID', 'pozos_segmentados.csv')

# Fallback por seguridad
if not os.path.exists(archivo):
    # Si no encuentra el archivo, intenta buscarlo en el directorio actual
    # Esto es solo para que no falle si mueves el script
    archivo = 'pozos_segmentados.csv'

print(f"📂 Cargando archivo: {archivo}")
try:
    df_raw = pd.read_csv(archivo)
except FileNotFoundError:
    print("❌ Error: No se encontró el archivo csv.")
    exit()

# Filtrar nulos esenciales
df_raw = df_raw.dropna(subset=['Vshale', 'X', 'Y', 'DEPTH', 'Segmento_ID'])

# ==========================================
# 2. PROCESO DE "BLOCKING" (UPSCALING)
# ==========================================
print("🔨 Realizando Blocking por Segmento_ID...")
df = df_raw.groupby(['Pozo_ID', 'Segmento_ID']).agg({
    'X': 'mean',
    'Y': 'mean',
    'DEPTH': 'mean',     
    'Vshale': 'mean'     
}).reset_index()

df['Z'] = -df['DEPTH'] # Z negativo

print(f"✅ Datos reducidos a {len(df)} bloques de control.")

# ==========================================
# 3. INTERPOLACIÓN ANISOTRÓPICA
# ==========================================
ANISOTROPY_FACTOR = 0.05 
grid_x, grid_y, grid_z = 50, 50, 100

x = np.linspace(df['X'].min(), df['X'].max(), grid_x)
y = np.linspace(df['Y'].min(), df['Y'].max(), grid_y)
z = np.linspace(df['Z'].min(), df['Z'].max(), grid_z)
X, Y, Z = np.meshgrid(x, y, z, indexing="ij")
grid_points = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])

print("🔄 Calculando modelo 3D...")

# Coordenadas escaladas para el cálculo
points_calc = df[['X', 'Y', 'Z']].values.copy()
points_calc[:, 2] *= (1 / ANISOTROPY_FACTOR)
grid_calc = grid_points.copy()
grid_calc[:, 2] *= (1 / ANISOTROPY_FACTOR)

# IDW
tree = cKDTree(points_calc)
distances, idx = tree.query(grid_calc, k=4) 
weights = 1 / (distances**2.5 + 1e-12)
weights /= weights.sum(axis=1, keepdims=True)
interpolated_values = np.sum(weights * df['Vshale'].values[idx], axis=1)

# Crear Grid
grid = pv.StructuredGrid(X, Y, Z)
grid["Vshale"] = interpolated_values

# ==========================================
# 4. VISUALIZACIÓN INTERACTIVA CON SLIDERS
# ==========================================
print("🎨 Generando interfaz interactiva...")

plotter = pv.Plotter()

# Límite de color
clim_range = [0, max(df['Vshale'].max(), 0.2)] 
cmap = "viridis"

# --- A) POZOS (Fijos) ---
cloud = pv.PolyData(df[['X', 'Y', 'Z']].values)
cloud['Vshale'] = df['Vshale']
plotter.add_mesh(cloud, scalars="Vshale", cmap=cmap, clim=clim_range, 
                 point_size=8, render_points_as_spheres=True, label="Segmentos")

# --- B) INICIALIZACIÓN DE MALLAS (Slices y Superficie) ---
center = grid.center
iso_init_val = (df['Vshale'].min() + df['Vshale'].max()) / 2

# 1. Crear malla inicial Isosurface (Transparente para ver pozos dentro)
mesh_iso = grid.contour(isosurfaces=[iso_init_val], scalars="Vshale")
plotter.add_mesh(mesh_iso, name="iso_mesh", color="lightblue", opacity=0.5, show_scalar_bar=False)

# 2. Inicializar cortes X e Y
# (Se añadirán en la primera llamada de la función, pero definimos los límites aquí)
pass 

# --- C) FUNCIONES DE ACTUALIZACIÓN ---

def update_iso(value):
    """Actualiza la Isosuperficie 3D"""
    new_mesh = grid.contour(isosurfaces=[value], scalars="Vshale")
    mesh_iso.shallow_copy(new_mesh)

def update_x_slice(value):
    """Actualiza el corte X"""
    slice_mesh = grid.slice(normal='x', origin=(value, center[1], center[2]))
    plotter.add_mesh(slice_mesh, name="corte_x", cmap=cmap, clim=clim_range, show_edges=False)

def update_y_slice(value):
    """Actualiza el corte Y"""
    slice_mesh = grid.slice(normal='y', origin=(center[0], value, center[2]))
    plotter.add_mesh(slice_mesh, name="corte_y", cmap=cmap, clim=clim_range, show_edges=False)

# --- D) CONFIGURAR SLIDERS ---

# 1. Slider SUPERIOR: Isosurface Value
plotter.add_slider_widget(
    callback=update_iso,
    rng=[df['Vshale'].min(), df['Vshale'].max()],
    value=iso_init_val,
    title="Valor Isosuperficie (VShale)",
    pointa=(0.3, 0.9), pointb=(0.7, 0.9),
    style='modern'
)

# 2. Slider INFERIOR 1: Corte X
plotter.add_slider_widget(
    update_x_slice, 
    [df['X'].min(), df['X'].max()], 
    value=center[0],
    title="Corte X (Este-Oeste)",
    pointa=(0.025, 0.1), pointb=(0.25, 0.1),
    style='modern'
)

# 3. Slider INFERIOR 2: Corte Y
plotter.add_slider_widget(
    update_y_slice, 
    [df['Y'].min(), df['Y'].max()], 
    value=center[1],
    title="Corte Y (Norte-Sur)",
    pointa=(0.025, 0.25), pointb=(0.25, 0.25),
    style='modern'
)

# Etiquetas de pozos
plotter.add_point_labels(df.groupby('Pozo_ID').first()[['X','Y','Z']].values, 
                         df.groupby('Pozo_ID').first().index, font_size=10, text_color='black', always_visible=True)

plotter.show_grid(color='black')
plotter.add_title("Isosuperficie 3D", font_size=14)
plotter.view_isometric()

# Inicializar visualización de cortes
update_x_slice(center[0])
update_y_slice(center[1])

plotter.show()