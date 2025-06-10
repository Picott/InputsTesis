# 🧠 Modelado 3D de Vshale con Interpolación Geoestadística

**Autor:** Juan David Basto Picott  
**Proyecto de Grado – Escuela de Geología – Universidad Industrial de Santander**

---

## 🎯 Objetivo

Desarrollar un modelo 3D de **Vshale** a partir de registros de pozos utilizando **interpolación geoestadística**, permitiendo:

- Visualizar la variabilidad espacial de la arcillosidad en el subsuelo
- Mejorar la interpretación estratigráfica
- Caracterizar unidades geológicas como reservorios

---

## 🧰 Tecnologías y Librerías

El desarrollo se realizó completamente con **software libre**, empleando:

- `pandas`, `numpy`, `scipy`, `matplotlib`, `glob`, `os`
- `pyvista` para visualización 3D
- `lasio` para conversión de archivos `.LAS` a `.CSV`

---

## 🔁 Flujo de Trabajo

1. **[Conversión de Registros Originales](Logs/LasACsv/las_to_csv_Integrated.py)**
   - Conversión de `.LAS` → `.CSV`  
   - Repositorio de registros descargados desde [NOPIMS](https://nopims.dmp.wa.gov.au/Nopims/)

2. **[Normalización y Cálculo de Vshale](Logs/Normalizacion/normalizacion_vshale_well_id.py)**
   - Normalización del Gamma Ray
   - Cálculo de Vshale según la ecuación de **Larionov (formaciones modernas)**
   - Agrupación por `Pozo_ID`, y generación de gráficas individuales

3. **[Segmentación de Registros](Logs/Segmentacion/segmentacion.py)**
   - Identificación de cambios litológicos mediante segmentación por umbral
   - [Visualización por `Segmento_ID` en 3D](Logs/Segmentacion/visualizar_segmentacion.py)

4. **[Interpolación 3D (IDW)](Logs/Interpolacion3D/interpolacion_3d_with_wells.py)**
   - Generación de malla estructurada con `StructuredGrid`
   - Asignación de valores interpolados de Vshale
   - Superposición con nubes de pozos segmentados

5. **[Análisis Avanzado](Logs/Interpolacion3D/interpolacion_3d_with_wells_Isosurfaces_and_x_sections.py)**
   - Generación de isosuperficies de Vshale
   - Cortes en X/Y para análisis geoespacial
   - Visualización en PyVista

---

## 📁 Estructura del Repositorio

```

InputsTesis/
├── Documentation/     # Documentos de apoyo para uso de los scripts documentación paso a paso
├── Logs/              # Scripts Python para el procesamiento de la información, modelado y visualización.
├── Resources/         # Material base para test de los scrips (Archivos .LAS)
├── Vshale/            # Ejemplos de los resultados
├── README.md          # Este archivo
└── requirements.txt   # Librerías necesarias para reproducir el proyecto

```

---

## 📌 Archivos Clave

- `Logs/LasACsv/las_to_csv_Integrated.py` – Conversión masiva de registros `.LAS`
- `Logs/Normalizacion/normalizacion_vshale_well_id.py` – Cálculo de Vshale y GR normalizado
- `Logs/Segmentacion/segmentacion.py` – Segmentación por umbrales
- `Logs/Segmentacion/visualizar_segmentacion.py` – Visualización 3D de pozos
- `Logs/Interpolacion3D/interpolacion_3d_with_wells.py` - Interpolación de pozos en 3D
- `Logs/Interpolacion3D/interpolacion_3d_with_wells_Isosurfaces_and_x_sections.py` - Generación de isosuperficies de Vshale

---

## 📚 Segunda Fase Propuesta

> Para mejorar la calidad del modelo y evitar artefactos por fallas estructurales, se plantea:

- Delimitación de **topes formacionales**
- Separación de registros por **unidad geológica**
- Generación de modelos **estratigráficamente coherentes**
- Foco en el **overburden** para reducir ruido en la interpolación

---

## 📝 Licencia

Este proyecto se distribuye bajo licencia **MIT**. Puedes utilizar y modificar el código citando al autor original.

---

## ✍️ Notas Finales

- Este trabajo fue realizado con apoyo de herramientas de código abierto y motores de lenguaje predictivo (LLMs), pero toda la lógica, segmentación, parametrización e interpretación fue diseñada por el estudiante.
- Cualquier contribución o comentario académico es bienvenido.

---

**📄 Referencia completa del documento**: Ver [Documentación](Documentation)
