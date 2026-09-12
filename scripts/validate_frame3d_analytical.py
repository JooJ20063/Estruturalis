from __future__ import annotations

import json
import math
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app" / "main.py"
EXAMPLES = ROOT / "examples"
OUTPUT_ROOT = ROOT / "results" / "validation_frame3d_analytical"


ABS_TOL = 1.0e-8
REL_TOL = 1.0e-6


VALIDATION_CASES = [
    {
        "name": "cantilever_tip_load",
        "example": "viga_3d_console.json",
        "checks": [
            {
                "kind": "displacement",
                "node": 2,
                "key": "uz",
                "expected": -0.0256,
                "abs_tol": 1.0e-10,
            },
            {
                "kind": "displacement",
                "node": 2,
                "key": "ry",
                "expected": 0.0096,
                "abs_tol": 1.0e-10,
            },
            {
                "kind": "reaction",
                "node": 1,
                "key": "fz",
                "expected": 10.0,
            },
            {
                "kind": "reaction",
                "node": 1,
                "key": "my",
                "expected": -40.0,
            },
            {
                "kind": "element_force_any_abs",
                "element": 1,
                "keys": (
                    "shear_y_i",
                    "shear_y_j",
                    "shear_z_i",
                    "shear_z_j",
                ),
                "expected_abs": 10.0,
            },
            {
                "kind": "element_force_any_abs",
                "element": 1,
                "keys": (
                    "moment_y_i",
                    "moment_y_j",
                    "moment_z_i",
                    "moment_z_j",
                ),
                "expected_abs": 40.0,
            },
        ],
    },

    {
        "name": "cantilever_uniform_load",
        "example": "viga_3d_console_q.json",
        "checks": [
            {
                "kind": "displacement",
                "node": 2,
                "key": "uz",
                "expected": -0.0384,
                "abs_tol": 1.0e-10,
            },
            {
                "kind": "displacement",
                "node": 2,
                "key": "ry",
                "expected": 0.0128,
                "abs_tol": 1.0e-10,
            },
            {
                "kind": "reaction",
                "node": 1,
                "key": "fz",
                "expected": 40.0,
            },
            {
                "kind": "reaction",
                "node": 1,
                "key": "my",
                "expected": -80.0,
            },
            {
                "kind": "element_force_any_abs",
                "element": 1,
                "keys": (
                    "shear_y_i",
                    "shear_y_j",
                    "shear_z_i",
                    "shear_z_j",
                ),
                "expected_abs": 40.0,
            },
            {
                "kind": "element_force_any_abs",
                "element": 1,
                "keys": (
                    "moment_y_i",
                    "moment_y_j",
                    "moment_z_i",
                    "moment_z_j",
                ),
                "expected_abs": 80.0,
            },
        ],
    },

    {
        "name": "pure_torsion",
        "example": "viga_3d_console_torcao.json",
        "checks": [
            {
                "kind": "displacement",
                "node": 2,
                "key": "rx",
                "expected": 0.0015889655172413794,
                "abs_tol": 1.0e-10,
            },
            {
                "kind": "reaction",
                "node": 1,
                "key": "mx",
                "expected": -10.0,
            },
            {
                "kind": "element_force_abs",
                "element": 1,
                "key": "torsion_i",
                "expected_abs": 10.0,
            },
        ],
    },

    {
        "name": "pure_axial",
        "example": "viga_3d_console_axial.json",
        "checks": [
            {
                "kind": "displacement",
                "node": 2,
                "key": "ux",
                "expected": 0.00016,
                "abs_tol": 1.0e-12,
            },
            {
                "kind": "reaction",
                "node": 1,
                "key": "fx",
                "expected": -100.0,
            },
            {
                "kind": "element_force_abs",
                "element": 1,
                "key": "normal_i",
                "expected_abs": 100.0,
            },
        ],
    },

    {
        "name": "inclined_global_uniform_load",
        "example": "viga_3d_console_inclinada_q_global.json",
        "checks": [
            {
                "kind": "displacement",
                "node": 2,
                "key": "uz",
                "expected": -0.1087580,
                "abs_tol": 1.0e-6,
            },
            {
                "kind": "displacement",
                "node": 2,
                "key": "ry",
                "expected": 0.0232,
                "abs_tol": 1.0e-8,
            },
            {
                "kind": "reaction",
                "node": 1,
                "key": "fz",
                "expected": 53.85164807134504,
                "abs_tol": 1.0e-6,
            },
            {
                "kind": "reaction",
                "node": 1,
                "key": "my",
                "expected": -107.70329614269008,
                "abs_tol": 1.0e-6,
            },
            {
                "kind": "element_force_abs",
                "element": 1,
                "key": "normal_i",
                "expected_abs": 20.0,
                "abs_tol": 1.0e-7,
            },
            {
                "kind": "element_force_abs",
                "element": 1,
                "key": "shear_y_i",
                "expected_abs": 50.0,
                "abs_tol": 1.0e-7,
            },
            {
                "kind": "element_force_abs",
                "element": 1,
                "key": "moment_z_i",
                "expected_abs": 134.6291201783626,
                "abs_tol": 1.0e-6,
            },
        ],
    },
]


def main() -> None:
    print()
    print("==============================================")
    print("VALIDAÇÃO ANALÍTICA FRAME3D")
    print("==============================================")
    print()

    if not APP.exists():
        raise FileNotFoundError(
            f"Aplicação não encontrada: {APP}"
        )

    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)

    OUTPUT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    passed = 0
    failed = 0
    maximum_relative_error = 0.0

    for case in VALIDATION_CASES:
        try:
            case_error = run_validation_case(case)

            maximum_relative_error = max(
                maximum_relative_error,
                case_error,
            )

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
        f"Casos aprovados: {passed}/{len(VALIDATION_CASES)}"
    )

    print(
        f"Casos reprovados: {failed}/{len(VALIDATION_CASES)}"
    )

    print(
        "Maior erro relativo observado: "
        f"{maximum_relative_error:.6e}"
    )
    print("----------------------------------------------")
    print()

    if failed:
        raise SystemExit(1)

    print(
        "Validação analítica frame3d concluída "
        "com sucesso."
    )


def run_validation_case(
    case: dict[str, Any],
) -> float:

    example_path = EXAMPLES / case["example"]

    if not example_path.exists():
        raise FileNotFoundError(
            f"Exemplo não encontrado: {example_path}"
        )

    output_dir = (
        OUTPUT_ROOT
        / case["name"]
    )

    command = [
        sys.executable,
        str(APP),
        str(example_path),
        "-o",
        str(output_dir),
    ]

    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    if completed.returncode != 0:
        raise RuntimeError(
            "Falha ao executar o Estruturalis.\n"
            f"{completed.stderr}"
        )

    results_path = (
        output_dir
        / "resultados.json"
    )

    if not results_path.exists():
        raise FileNotFoundError(
            f"resultados.json não foi gerado "
            f"para {case['name']}"
        )

    results = json.loads(
        results_path.read_text(
            encoding="utf-8"
        )
    )

    if (
        results.get("analysis_type")
        != "frame3d"
    ):
        raise AssertionError(
            "analysis_type diferente de frame3d"
        )

    assert_equilibrium_ok(
        results,
        case["name"],
    )

    maximum_relative_error = 0.0

    for check in case.get(
        "checks",
        [],
    ):

        error = run_check(
            results,
            check,
            case["name"],
        )

        maximum_relative_error = max(
            maximum_relative_error,
            error,
        )

    return maximum_relative_error


def run_check(
    results: dict[str, Any],
    check: dict[str, Any],
    case_name: str,
) -> float:

    kind = check["kind"]

    if kind == "displacement":
        record = find_node_record(
            results,
            "displacements",
            int(check["node"]),
        )

        value = float(
            record[check["key"]]
        )

        return assert_close(
            value=value,
            expected=float(
                check["expected"]
            ),
            case_name=case_name,
            label=(
                f"deslocamento nó "
                f"{check['node']} "
                f"{check['key']}"
            ),
            abs_tol=float(
                check.get(
                    "abs_tol",
                    ABS_TOL,
                )
            ),
        )

    if kind == "reaction":
        record = find_node_record(
            results,
            "reactions",
            int(check["node"]),
        )

        value = float(
            record[check["key"]]
        )

        return assert_close(
            value=value,
            expected=float(
                check["expected"]
            ),
            case_name=case_name,
            label=(
                f"reação nó "
                f"{check['node']} "
                f"{check['key']}"
            ),
            abs_tol=float(
                check.get(
                    "abs_tol",
                    ABS_TOL,
                )
            ),
        )

    if kind == "element_force_abs":
        element = find_element_result(
            results,
            int(check["element"]),
        )

        forces = element.get(
            "local_end_forces",
            {},
        )

        key = check["key"]

        if key not in forces:
            raise AssertionError(
                f"{case_name}: esforço "
                f"{key} ausente"
            )

        value = abs(
            float(forces[key])
        )

        return assert_close(
            value=value,
            expected=float(
                check["expected_abs"]
            ),
            case_name=case_name,
            label=(
                f"|{key}| elemento "
                f"{check['element']}"
            ),
            abs_tol=float(
                check.get(
                    "abs_tol",
                    ABS_TOL,
                )
            ),
        )

    if kind == "element_force_any_abs":
        element = find_element_result(
            results,
            int(check["element"]),
        )

        forces = element.get(
            "local_end_forces",
            {},
        )

        expected = float(
            check["expected_abs"]
        )

        candidates = []

        for key in check["keys"]:
            if key in forces:
                candidates.append(
                    (
                        key,
                        abs(
                            float(
                                forces[key]
                            )
                        ),
                    )
                )

        if not candidates:
            raise AssertionError(
                f"{case_name}: nenhum esforço "
                "candidato encontrado"
            )

        best_key, best_value = min(
            candidates,
            key=lambda item: abs(
                item[1] - expected
            ),
        )

        return assert_close(
            value=best_value,
            expected=expected,
            case_name=case_name,
            label=(
                f"{best_key} elemento "
                f"{check['element']}"
            ),
            abs_tol=float(
                check.get(
                    "abs_tol",
                    ABS_TOL,
                )
            ),
        )

    raise ValueError(
        f"Tipo de verificação desconhecido: {kind}"
    )


def find_node_record(
    results: dict[str, Any],
    collection_name: str,
    node: int,
) -> dict[str, Any]:

    for record in results.get(
        collection_name,
        [],
    ):
        if int(
            record.get("node")
        ) == node:
            return record

    raise AssertionError(
        f"Nó {node} não encontrado em "
        f"{collection_name}"
    )


def find_element_result(
    results: dict[str, Any],
    element_id: int,
) -> dict[str, Any]:

    for element in results.get(
        "elements",
        [],
    ):
        if int(
            element.get("id")
        ) == element_id:
            return element

    raise AssertionError(
        f"Elemento {element_id} não encontrado"
    )


def assert_equilibrium_ok(
    results: dict[str, Any],
    case_name: str,
) -> None:

    equilibrium = results.get(
        "equilibrium"
    )

    if not equilibrium:
        raise AssertionError(
            f"{case_name}: equilíbrio ausente"
        )

    if (
        equilibrium.get("status")
        != "OK"
    ):
        raise AssertionError(
            f"{case_name}: equilíbrio não OK"
        )

    force_norm = float(
        equilibrium.get(
            "force_norm",
            0.0,
        )
    )

    moment_norm = float(
        equilibrium.get(
            "moment_norm",
            0.0,
        )
    )

    tolerance = float(
        equilibrium.get(
            "tolerance",
            0.0,
        )
    )

    if force_norm > tolerance:
        raise AssertionError(
            f"{case_name}: resíduo de forças "
            f"{force_norm:.6e} > "
            f"{tolerance:.6e}"
        )

    if moment_norm > tolerance:
        raise AssertionError(
            f"{case_name}: resíduo de momentos "
            f"{moment_norm:.6e} > "
            f"{tolerance:.6e}"
        )


def assert_close(
    value: float,
    expected: float,
    case_name: str,
    label: str,
    abs_tol: float = ABS_TOL,
    rel_tol: float = REL_TOL,
) -> float:

    difference = abs(
        value - expected
    )

    denominator = max(
        abs(expected),
        abs_tol,
    )

    relative_error = (
        difference
        / denominator
    )

    if not math.isclose(
        value,
        expected,
        abs_tol=abs_tol,
        rel_tol=rel_tol,
    ):
        raise AssertionError(
            f"{case_name}: {label} "
            "fora da tolerância. "
            f"valor={value:.12e}, "
            f"esperado={expected:.12e}, "
            f"erro_rel={relative_error:.6e}"
        )

    return relative_error


if __name__ == "__main__":
    main()