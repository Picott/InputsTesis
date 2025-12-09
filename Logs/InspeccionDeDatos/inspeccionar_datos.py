import pandas as pd

# Ruta del archivo segmentado
RUTA_INPUT = "C:/Users/Anjuli/Documents/Inputs/Vshale/withID/pozos_segmentados.csv"

# Cargar datos
df = pd.read_csv(RUTA_INPUT)

# Verificar si hay valores nulos o extraños en las columnas clave
print("📌 Resumen de datos por pozo:")
print(df.groupby("Pozo_ID")[["X", "Y", "DEPTH"]].agg(["min", "max", "count"]))

# Verificar si hay NaN en X, Y, DEPTH
print("\n🔍 Filas con valores NaN:")
print(df[df[["X", "Y", "DEPTH"]].isna().any(axis=1)])
