from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app" / "main.py"
EXAMPLES = ROOT / "examples"


FAILURE_CASES: list[dict[str, Any]] = [
    {
        "name": "zero_length_element",
        "example": "invalid_frame3d_zero_length.json",
        "expected_messages": [
            "comprimento nulo",
        ],
    },
    {
        "name": "insufficient_restraints",
        "example": "invalid_frame3d_unstable.json",
        "expected_messages": [
            "poucos vínculos",
            "frame3d",
        ],
    },
    {
        "name": "invalid_section_area",
        "example": "invalid_frame3d_section.json",
        "expected_messages": [
            "área A <= 0",
        ],
    },
    {
        "name": "invalid_load_combination",
        "example": "invalid_frame3d_combination.json",
        "expected_messages": [
            "NAO_EXISTE",
            "não encontrado",
        ],
    },
    {
        "name": "invalid_material_E",
        "example": "invalid_frame3d_material_E.json",
        "expected_messages": [
            "módulo de elasticidade E <= 0",
        ],
    },
    {
        "name": "invalid_section_J",
        "example": "invalid_frame3d_section_J.json",
        "expected_messages": [
            "J <= 0",
        ],
    },
    {
        "name": "zero_nodal_load",
        "example": "invalid_frame3d_zero_load.json",
        "expected_messages": [
            "todos os valores iguais a zero",
        ],
    },
    {
        "name": "invalid_coordinate_system",
        "example": "invalid_frame3d_coordinate_system.json",
        "expected_messages": [
            "coordinate_system",
            "galactico",
            "inválido",
        ],
    },
    {
        "name": "invalid_reference",
        "example": "invalid_frame3d_reference.json",
        "expected_messages": [
            "nó 99",
            "não existe",
        ],
    },
]


def main() -> None:
    print()
    print("==============================================")
    print("VALIDAÇÃO DE FALHAS FRAME3D")
    print("==============================================")
    print()

    if not APP.exists():
        raise FileNotFoundError(
            f"Aplicação não encontrada: {APP}"
        )

    passed = 0
    failed = 0

    for case in FAILURE_CASES:
        try:
            run_failure_case(case)

            passed += 1

            print(
                f"{case['name']:<36} PASS"
            )

        except Exception as error:
            failed += 1

            print(
                f"{case['name']:<36} FAIL"
            )

            print(
                f"    {error}"
            )

    print()
    print("----------------------------------------------")
    print(
        f"Casos aprovados: {passed}/{len(FAILURE_CASES)}"
    )
    print(
        f"Casos reprovados: {failed}/{len(FAILURE_CASES)}"
    )
    print("----------------------------------------------")
    print()

    if failed:
        raise SystemExit(1)

    print(
        "Validação de falhas frame3d concluída "
        "com sucesso."
    )


def run_failure_case(
    case: dict[str, Any],
) -> None:

    example_path = (
        EXAMPLES
        / case["example"]
    )

    if not example_path.exists():
        raise FileNotFoundError(
            f"Exemplo não encontrado: {example_path}"
        )

    command = [
        sys.executable,
        str(APP),
        str(example_path),
    ]

    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    output = (
        completed.stdout
        + "\n"
        + completed.stderr
    )

    # ----------------------------------------------------------
    # O caso inválido NÃO pode terminar com sucesso.
    # ----------------------------------------------------------
    if completed.returncode == 0:
        raise AssertionError(
            "o modelo inválido terminou com código de saída 0"
        )

    # ----------------------------------------------------------
    # Além de falhar, deve explicar corretamente por quê.
    # ----------------------------------------------------------
    expected_messages = case.get(
        "expected_messages",
        [],
    )

    missing_messages = [
        message
        for message in expected_messages
        if message.lower() not in output.lower()
    ]

    if missing_messages:
        raise AssertionError(
            "mensagem de erro inesperada. "
            "Não foram encontrados: "
            + ", ".join(
                repr(message)
                for message in missing_messages
            )
        )

    # ----------------------------------------------------------
    # Um caso inválido jamais pode anunciar conclusão normal.
    # ----------------------------------------------------------
    forbidden_messages = [
        "Análise concluída com sucesso!",
        "Validação frame3d concluída com sucesso.",
    ]

    for message in forbidden_messages:
        if message.lower() in output.lower():
            raise AssertionError(
                "o programa anunciou sucesso para "
                f"um modelo inválido: {message!r}"
            )


if __name__ == "__main__":
    main()