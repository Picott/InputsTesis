import pandas as pd

# Ruta del archivo segmentado
RUTA_INPUT = "C:/Users/Anjuli/Documents/Inputs/Vshale/withID/pozos_segmentados.csv"

# Cargar datos
df = pd.read_csv(RUTA_INPUT)

# Ver cuántos pozos hay
print("📌 Lista de pozos en el archivo:", df['Pozo_ID'].unique())
print(f"🔢 Total de pozos: {df['Pozo_ID'].nunique()}")
