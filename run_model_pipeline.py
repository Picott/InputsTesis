from __future__ import annotations

import argparse
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

REPO_ROOT = Path(__file__).resolve().parent


@dataclass
class PipelineStep:
    name: str
    description: str
    command: List[str]
    prereqs: Iterable[Path]

    def missing_prereqs(self) -> List[Path]:
        return [path for path in self.prereqs if not path.exists()]


def run_command(command: List[str]) -> int:
    result = subprocess.run(command, cwd=REPO_ROOT)
    return result.returncode


def build_steps(skip_conversion: bool) -> List[PipelineStep]:
    steps: List[PipelineStep] = []

    conversion_dir = REPO_ROOT / "Resources" / "las"
    csv_output_dir = REPO_ROOT / "Resources" / "csv"
    vshale_dir = REPO_ROOT / "Vshale" / "withID"

    if not skip_conversion:
        steps.append(
            PipelineStep(
                name="Conversión LAS → CSV",
                description=(
                    "Convierte los registros LAS ubicados en Resources/las a CSV "
                    "dentro de Resources/csv. El script pedirá coordenadas X/Y si el archivo no las incluye."
                ),
                command=["python", "Logs/LasACsv/las_to_csv_Integrated.py", str(conversion_dir)],
                prereqs=[conversion_dir],
            )
        )

    steps.append(
        PipelineStep(
            name="Normalización y cálculo de Vshale",
            description=(
                "Lee los CSV en Resources/csv, normaliza GR, calcula Vshale y genera "
                "pozos_procesados_vis.csv y gráficas en Vshale/withID."
            ),
            command=["python", "Logs/Normalizacion/normalizacion_vshale_well_id.py"],
            prereqs=[csv_output_dir],
        )
    )

    steps.append(
        PipelineStep(
            name="Segmentación de pozos",
            description=(
                "Segmenta cada pozo usando umbral y guarda pozos_segmentados.csv en Vshale/withID."
            ),
            command=["python", "Logs/Segmentacion/segmentacion.py"],
            prereqs=[vshale_dir / "pozos_procesados_vis.csv"],
        )
    )

    steps.append(
        PipelineStep(
            name="Interpolación 3D",
            description=(
                "Aplica interpolación IDW en 3D y abre la visualización interactiva en PyVista."
            ),
            command=["python", "Logs/Interpolacion3D/interpolacion_3d_with_wells.py"],
            prereqs=[vshale_dir / "pozos_segmentados.csv"],
        )
    )

    return steps


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Asistente para ejecutar los scripts del flujo de modelado. Por defecto solo imprime los pasos; "
            "agrega --execute para correrlos."
        )
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Ejecuta cada paso en lugar de solo mostrarlos.",
    )
    parser.add_argument(
        "--skip-conversion",
        action="store_true",
        help="Omite la conversión de LAS a CSV (útil si ya cuentas con los CSV).",
    )
    args = parser.parse_args()

    steps = build_steps(skip_conversion=args.skip_conversion)

    print("📍 Directorio del repositorio:", REPO_ROOT)
    print("🔄 Pasos configurados:")

    for index, step in enumerate(steps, start=1):
        print(f"\n{index}. {step.name}")
        print(f"   ➜ {step.description}")
        print("   🔗 Comando:", " ".join(step.command))

        missing = step.missing_prereqs()
        if missing:
            print("   ⚠️  Prerrequisitos faltantes:")
            for path in missing:
                print("      -", path)
            if args.execute:
                print("   ⏭️  Se omite este paso por faltante de insumos.")
                continue

        if args.execute:
            print("   ▶️  Ejecutando...")
            exit_code = run_command(step.command)
            if exit_code != 0:
                print(f"   ❌ Paso detenido con código {exit_code}.")
                break
            print("   ✅ Paso completado.")

    if not args.execute:
        print("\nℹ️ Usa --execute para correr automáticamente los pasos mostrados.")


if __name__ == "__main__":
    main()
