import os
import lasio
import pandas as pd
import traceback

# Rutas de entrada y salida
ruta_las = r"C:\Users\Anjuli\Documents\Inputs\Logs\LAS"
ruta_csv = r"C:\Users\Anjuli\Documents\Inputs\Logs\CSV"

# Mensajes de depuración iniciales
print("Iniciando script...")
print(f"Ruta de entrada: {ruta_las}")
print(f"Ruta de salida: {ruta_csv}")

# Crear carpeta CSV si no existe
os.makedirs(ruta_csv, exist_ok=True)

# Buscar archivos terminados en .las (insensible a mayúsculas)
archivos_las = [f for f in os.listdir(ruta_las) if f.lower().endswith(".las")]
print("Archivos LAS encontrados:", archivos_las)

# Iterar sobre los archivos encontrados
for archivo in archivos_las:
    print(f"\n=== Procesando: {archivo} ===")
    try:
        ruta_archivo = os.path.join(ruta_las, archivo)

        # Lectura del archivo LAS
        las = lasio.read(ruta_archivo)
        df = las.df()  # DataFrame con las curvas

        # Añadir información de cabecera (well header) como columnas
        for mnemonic, item in las.well.items():
            if mnemonic not in df.columns:
                df[mnemonic] = item.value

        # Manejo de columna de profundidad
        if "DEPTH" not in df.columns and "DEPT" not in df.columns:
            df.insert(0, "DEPT", las.index)
            print("   - Columna de profundidad 'DEPT' creada a partir del índice LAS.")
        else:
            print("   - Se detectó columna de profundidad (DEPTH o DEPT).")

        # Reemplazar valores nulos convencionales (-999.25) por NA de pandas
        df.replace(-999.25, pd.NA, inplace=True)
        print("   - Reemplazados -999.25 con NA.")

        # Identificación o creación de columnas X e Y
        posibles_x = ["X", "FL2", "EASTING", "XCOORD"]
        posibles_y = ["Y", "FL1", "NORTHING", "YCOORD"]

        x_col = None
        y_col = None

        # Detectar la columna X en df
        for col in posibles_x:
            if col in df.columns:
                x_col = col
                break

        # Detectar la columna Y en df
        for col in posibles_y:
            if col in df.columns:
                y_col = col
                break

        # Si no se encuentra X
        if not x_col:
            print("   - No se encontró columna X. Se pedirá manualmente.")
            valor_x = input("Ingrese la coordenada X: ")
            df["X"] = valor_x
            x_col = "X"
        else:
            if x_col != "X":
                df.rename(columns={x_col: "X"}, inplace=True)
                print(f"   - Columna '{x_col}' renombrada a 'X'.")

        # Si no se encuentra Y
        if not y_col:
            print("   - No se encontró columna Y. Se pedirá manualmente.")
            valor_y = input("Ingrese la coordenada Y: ")
            df["Y"] = valor_y
            y_col = "Y"
        else:
            if y_col != "Y":
                df.rename(columns={y_col: "Y"}, inplace=True)
                print(f"   - Columna '{y_col}' renombrada a 'Y'.")

        # Construir nombre de archivo de salida y exportar a CSV
        nombre_salida = os.path.splitext(archivo)[0] + ".csv"
        ruta_salida_csv = os.path.join(ruta_csv, nombre_salida)

        df.to_csv(ruta_salida_csv, index=False)
        print(f"✅ Generado: {ruta_salida_csv}")
        print("   Primeras filas del DataFrame resultante:")
        print(df.head())

    except Exception as e:
        traceback.print_exc()
        print(f"❌ Error al convertir {archivo}: {e}")

print("Script finalizado.")
