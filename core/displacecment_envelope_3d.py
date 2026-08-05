from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any, Mapping

from core.displacement_report_3d import calculate_story_drifts_3d


TRANSLATION_KEYS = ("ux", "uy", "uz")
ROTATION_KEYS = ("rx", "ry", "rz")
ALL_COMPONENT_KEYS = TRANSLATION_KEYS + ROTATION_KEYS

RESULTANT_DEFINITIONS = {
    "horizontal_resultant": {
        "keys": ("ux", "uy"),
        "formula": "sqrt(ux² + uy²)",
        "unit": "m",
    },
    "translation_resultant": {
        "keys": ("ux", "uy", "uz"),
        "formula": "sqrt(ux² + uy² + uz²)",
        "unit": "m",
    },
    "rotation_resultant": {
        "keys": ("rx", "ry", "rz"),
        "formula": "sqrt(rx² + ry² + rz²)",
        "unit": "rad",
    },
}


def create_displacement_envelope_3d(
    results_by_case: Mapping[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    Cria a envoltória de deslocamentos de várias análises frame3d.

    Mantém:
    - valores mínimo, máximo e máximo absoluto por componente;
    - resultantes máximas;
    - drift governante em cada intervalo de pavimento;
    - combinação e nó governantes.
    """

    if not results_by_case:
        raise ValueError(
            "Nenhum resultado fornecido para a envoltória "
            "de deslocamentos 3D."
        )

    component_envelopes = {}

    for component in ALL_COMPONENT_KEYS:
        records = _collect_component_records(
            results_by_case=results_by_case,
            component=component,
        )

        if records:
            component_envelopes[component] = _summarize_signed_records(
                records
            )

    resultant_envelopes = {}

    for resultant_name, definition in RESULTANT_DEFINITIONS.items():
        records = _collect_resultant_records(
            results_by_case=results_by_case,
            keys=definition["keys"],
            formula=definition["formula"],
        )

        if records:
            resultant_envelopes[resultant_name] = max(
                records,
                key=lambda item: item["value"],
            )

    story_drifts = _create_story_drift_envelope(results_by_case)

    return {
        "analysis_type": "frame3d",
        "limit_state": "ELS",
        "number_of_cases": len(results_by_case),
        "cases": list(results_by_case.keys()),
        "components": component_envelopes,
        "resultants": resultant_envelopes,
        "story_drifts": story_drifts,
    }


def save_displacement_envelope_3d_json(
    envelope: dict[str, Any],
    output_path: str | Path,
) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            envelope,
            file,
            indent=4,
            ensure_ascii=False,
        )


def write_displacement_envelope_3d_csv(
    envelope: dict[str, Any],
    output_path: str | Path,
) -> None:
    """
    Salva componentes, resultantes e drifts em um único CSV.
    """

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "category",
        "quantity",
        "criterion",
        "case",
        "node",
        "node_bottom",
        "node_top",
        "x",
        "y",
        "z",
        "z_bottom",
        "z_top",
        "height",
        "value",
        "abs_value",
        "drift_ratio",
        "unit",
    ]

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for component, summary in envelope.get(
            "components",
            {},
        ).items():
            unit = "m" if component in TRANSLATION_KEYS else "rad"

            for criterion in ("min", "max", "abs"):
                record = summary.get(criterion)

                if not record:
                    continue

                writer.writerow(
                    {
                        "category": "component",
                        "quantity": component,
                        "criterion": criterion,
                        "case": record.get("case"),
                        "node": record.get("node"),
                        "x": record.get("x"),
                        "y": record.get("y"),
                        "z": record.get("z"),
                        "value": record.get("value"),
                        "abs_value": record.get("abs_value"),
                        "unit": unit,
                    }
                )

        for name, record in envelope.get(
            "resultants",
            {},
        ).items():
            definition = RESULTANT_DEFINITIONS[name]

            writer.writerow(
                {
                    "category": "resultant",
                    "quantity": name,
                    "criterion": "max",
                    "case": record.get("case"),
                    "node": record.get("node"),
                    "x": record.get("x"),
                    "y": record.get("y"),
                    "z": record.get("z"),
                    "value": record.get("value"),
                    "abs_value": record.get("value"),
                    "unit": definition["unit"],
                }
            )

        for drift in envelope.get("story_drifts", []):
            writer.writerow(
                {
                    "category": "story_drift",
                    "quantity": "horizontal_drift",
                    "criterion": "max",
                    "case": drift.get("case"),
                    "node_bottom": drift.get("node_bottom"),
                    "node_top": drift.get("node_top"),
                    "x": drift.get("x"),
                    "y": drift.get("y"),
                    "z_bottom": drift.get("z_bottom"),
                    "z_top": drift.get("z_top"),
                    "height": drift.get("height"),
                    "value": drift.get("drift"),
                    "abs_value": drift.get("drift"),
                    "drift_ratio": drift.get("drift_ratio"),
                    "unit": "m",
                }
            )


def write_displacement_envelope_3d_report_txt(
    envelope: dict[str, Any],
    output_path: str | Path,
) -> None:
    text = format_displacement_envelope_3d(envelope)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")


def format_displacement_envelope_3d(
    envelope: dict[str, Any],
) -> str:
    lines: list[str] = []

    lines.append(
        "ENVOLTÓRIA DE DESLOCAMENTOS 3D - ELS - Estruturalis"
    )
    lines.append("=" * 70)
    lines.append("")

    cases = envelope.get("cases", [])

    lines.append(
        f"Número de combinações ELS: "
        f"{envelope.get('number_of_cases', len(cases))}"
    )
    lines.append(
        "Combinações consideradas: "
        + ", ".join(cases)
    )
    lines.append("")

    lines.append("Componentes governantes:")
    lines.append("-" * 70)

    labels = {
        "ux": "Deslocamento ux",
        "uy": "Deslocamento uy",
        "uz": "Deslocamento uz",
        "rx": "Rotação rx",
        "ry": "Rotação ry",
        "rz": "Rotação rz",
    }

    for component in ALL_COMPONENT_KEYS:
        summary = envelope.get(
            "components",
            {},
        ).get(component)

        if not summary:
            continue

        record = summary["abs"]
        unit = "m" if component in TRANSLATION_KEYS else "rad"

        lines.append(
            f"{labels[component]}: "
            f"{record['value']:.6e} {unit} | "
            f"|valor|={record['abs_value']:.6e} | "
            f"nó {record['node']} | "
            f"combinação {record['case']}"
        )

    lines.append("")
    lines.append("Resultantes governantes:")
    lines.append("-" * 70)

    resultant_labels = {
        "horizontal_resultant":
            "Deslocamento horizontal resultante",
        "translation_resultant":
            "Deslocamento translacional resultante",
        "rotation_resultant":
            "Rotação resultante",
    }

    for name, definition in RESULTANT_DEFINITIONS.items():
        record = envelope.get(
            "resultants",
            {},
        ).get(name)

        if not record:
            continue

        lines.append(
            f"{resultant_labels[name]}: "
            f"{record['value']:.6e} {definition['unit']} | "
            f"nó {record['node']} | "
            f"combinação {record['case']} | "
            f"{definition['formula']}"
        )

    lines.append("")
    lines.append("Drift governante por pavimento:")
    lines.append("-" * 70)

    story_drifts = envelope.get("story_drifts", [])

    if not story_drifts:
        lines.append("Nenhum drift de pavimento disponível.")
    else:
        for drift in story_drifts:
            lines.append(
                f"Z {drift['z_bottom']:.6g} -> "
                f"{drift['z_top']:.6g} m | "
                f"altura={drift['height']:.6e} m | "
                f"drift={drift['drift']:.6e} m | "
                f"razão={drift['drift_ratio']:.6e} | "
                f"combinação {drift['case']} | "
                f"nós {drift['node_bottom']} -> "
                f"{drift['node_top']}"
            )

    lines.append("")
    lines.append("Observações:")
    lines.append(
        "- A envoltória considera somente combinações "
        "classificadas como ELS."
    )
    lines.append(
        "- O drift é calculado entre nós com as mesmas "
        "coordenadas x e y em níveis consecutivos."
    )
    lines.append(
        "- Os resultados são preliminares e não constituem "
        "verificação normativa completa."
    )
    lines.append("")

    return "\n".join(lines)


def _collect_component_records(
    results_by_case: Mapping[str, dict[str, Any]],
    component: str,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    for case_name, results in results_by_case.items():
        for displacement in results.get("displacements", []):
            value = float(displacement.get(component, 0.0))

            records.append(
                {
                    "case": case_name,
                    "node": displacement.get("node"),
                    "x": float(displacement.get("x", 0.0)),
                    "y": float(displacement.get("y", 0.0)),
                    "z": float(displacement.get("z", 0.0)),
                    "component": component,
                    "value": value,
                    "abs_value": abs(value),
                }
            )

    return records


def _collect_resultant_records(
    results_by_case: Mapping[str, dict[str, Any]],
    keys: tuple[str, ...],
    formula: str,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    for case_name, results in results_by_case.items():
        for displacement in results.get("displacements", []):
            value = math.sqrt(
                sum(
                    float(displacement.get(key, 0.0)) ** 2
                    for key in keys
                )
            )

            records.append(
                {
                    "case": case_name,
                    "node": displacement.get("node"),
                    "x": float(displacement.get("x", 0.0)),
                    "y": float(displacement.get("y", 0.0)),
                    "z": float(displacement.get("z", 0.0)),
                    "keys": list(keys),
                    "formula": formula,
                    "value": value,
                }
            )

    return records


def _summarize_signed_records(
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    min_record = min(
        records,
        key=lambda item: item["value"],
    )
    max_record = max(
        records,
        key=lambda item: item["value"],
    )
    abs_record = max(
        records,
        key=lambda item: item["abs_value"],
    )

    return {
        "min": dict(min_record),
        "max": dict(max_record),
        "abs": dict(abs_record),
    }


def _create_story_drift_envelope(
    results_by_case: Mapping[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    records_by_interval: dict[
        tuple[float, float],
        list[dict[str, Any]],
    ] = {}

    for case_name, results in results_by_case.items():
        displacements = list(
            results.get("displacements", [])
        )

        if not displacements:
            continue

        case_drifts = calculate_story_drifts_3d(
            displacements
        )

        for drift in case_drifts:
            key = (
                float(drift["z_bottom"]),
                float(drift["z_top"]),
            )

            record = dict(drift)
            record["case"] = case_name

            records_by_interval.setdefault(
                key,
                [],
            ).append(record)

    envelope: list[dict[str, Any]] = []

    for key in sorted(records_by_interval):
        governing = max(
            records_by_interval[key],
            key=lambda item: item["drift"],
        )

        envelope.append(dict(governing))

    return envelope
