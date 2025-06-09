import pandas as pd

# Ruta del archivo antes de la segmentación
RUTA_INPUT = "C:/Users/Anjuli/Documents/Inputs/Vshale/withID/pozos_procesados_vis.csv"

# Cargar datos
df = pd.read_csv(RUTA_INPUT)

# Filtrar los pozos en cuestión
df_pozos = df[df['Pozo_ID'].isin(['Poseidon-1_GR-RES-DEN-POR', 'COP_Pharos-1_VISION Service_RM_482'])]

# Ver las coordenadas únicas de estos pozos
print("📌 Coordenadas únicas antes de la segmentación:")
print(df_pozos.groupby("Pozo_ID")[["X", "Y"]].nunique())

# Mostrar ejemplos de valores de X e Y para estos pozos
print("\n🔍 Muestras de X, Y por pozo:")
print(df_pozos.groupby("Pozo_ID")[["X", "Y"]].first())
