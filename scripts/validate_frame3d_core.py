from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


STEPS = [
    (
        "Compilação Python",
        [
            sys.executable,
            "-m",
            "compileall",
            "app",
            "core",
            "io_module",
            "plots",
            "scripts",
        ],
    ),
    (
        "Integração Frame3D",
        [
            sys.executable,
            "scripts/validate_frame3d_examples.py",
        ],
    ),
    (
        "Validação analítica Frame3D",
        [
            sys.executable,
            "scripts/validate_frame3d_analytical.py",
        ],
    ),
    (
        "Robustez e falhas Frame3D",
        [
            sys.executable,
            "scripts/validate_frame3d_failures.py",
        ],
    ),
]


def main() -> None:
    print()
    print("=" * 60)
    print("ESTRUTURALIS — VALIDAÇÃO CONSOLIDADA DO CORE FRAME3D")
    print("=" * 60)
    print()

    passed = 0

    for name, command in STEPS:
        print()
        print("-" * 60)
        print(name)
        print("-" * 60)

        completed = subprocess.run(
            command,
            cwd=ROOT,
            check=False,
        )

        if completed.returncode != 0:
            print()
            print("=" * 60)
            print(f"FAIL: {name}")
            print("=" * 60)
            raise SystemExit(
                completed.returncode
            )

        passed += 1

        print()
        print(f"PASS: {name}")

    print()
    print("=" * 60)
    print(
        f"CORE FRAME3D VALIDADO: "
        f"{passed}/{len(STEPS)} blocos aprovados"
    )
    print("=" * 60)

    print()
    print(
        "Etapa de validação estrutural básica "
        "do Frame3D concluída."
    )


if __name__ == "__main__":
    main()