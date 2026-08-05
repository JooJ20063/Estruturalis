# app/main.py

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import argparse
import sys

# Adiciona a raiz do projeto ao caminho de importação do Python
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from core.version import __version__

class ExecutionMode(str, Enum):
    FULL = "full"
    FAST = "fast"
    SOLVER_ONLY = "solver_only"
    SUMMARY_ONLY = "summary_only"
    REPORTS_ONLY = "reports_only"

@dataclass(frozen=True)
class ExecutionOptions:
    """
    Controla o nível de processamento e as saídas geradas.
    """

    mode: ExecutionMode = ExecutionMode.FULL
    generate_plots: bool = True
    generate_html: bool = True
    validate_only: bool = False

    @property
    def generate_summaries(self) -> bool:
        """
        Indica se os resumos textuais devem ser gerados.
        """

        return self.mode != ExecutionMode.SOLVER_ONLY

    @property
    def generate_detailed_reports(self) -> bool:
        """
        Indica se relatórios detalhados, CSVs e memoriais
        devem ser gerados.
        """

        return self.mode in {
            ExecutionMode.FULL,
            ExecutionMode.FAST,
            ExecutionMode.REPORTS_ONLY,
        }

    @property
    def solver_only(self) -> bool:
        return self.mode == ExecutionMode.SOLVER_ONLY

    @classmethod
    def from_cli_args(cls, args: argparse.Namespace) -> "ExecutionOptions":
        """
        Converte os argumentos da CLI para uma configuração normalizada.
        """

        if args.solver_only:
            mode = ExecutionMode.SOLVER_ONLY
        elif args.summary_only:
            mode = ExecutionMode.SUMMARY_ONLY
        elif args.reports_only:
            mode = ExecutionMode.REPORTS_ONLY
        elif args.fast:
            mode = ExecutionMode.FAST
        else:
            mode = ExecutionMode.FULL

        graphics_enabled = mode == ExecutionMode.FULL and not args.validate_only

        return cls(
            mode=mode,
            generate_plots=graphics_enabled and not args.no_plots,
            generate_html=graphics_enabled and not args.no_html,
            validate_only=args.validate_only
        )

def run_single_analysis(model, output_dir: Path, options: ExecutionOptions | None = None, ) -> dict:
    """
    Executa uma análise individual:
    - valida modelo;
    - escolhe solver conforme analysis_type;
    - salva JSON;
    - gera diagramas apenas para frame2d.
    """
    options = options or ExecutionOptions()
    from core.timing import TimingReport

    timing = TimingReport()

    if getattr(model, "analysis_type", "frame2d") == "frame3d":
        return run_single_analysis_3d(model, output_dir, timing=timing, options=options,)

    return run_single_analysis_2d(model, output_dir, timing=timing, options=options,)

def run_single_analysis_2d(model, output_dir: Path, timing=None, options: ExecutionOptions | None = None) -> dict:
    """
    Executa uma análise 2D.
    """

    options = options or ExecutionOptions()

    from core.validation import validate_model
    from core.solver import solve_structure
    from core.postprocess import enrich_results, print_analysis_summary
    from io_module.results_writer import write_results_json
    from core.deflection import write_preliminary_deflection_summary_txt
    from core.timing import TimingReport

    timing = timing or TimingReport()

    output_dir.mkdir(parents=True, exist_ok=True)

    print("[3/5] Validando e resolvendo modelo estrutural...")

    with timing.step("Validação do modelo 2D"):
        validate_model(model)

    with timing.step("Solver 2D"):
        results = solve_structure(model)

    with timing.step("Pós-processamento 2D"):
        results = enrich_results(model, results)

    if options.generate_summaries:
        with timing.step("Resumos 2D"):
            print_analysis_summary(results)

            write_preliminary_deflection_summary_txt(
                model=model,
                results=results,
                file_path=output_dir / "resumo_flechas.txt",
            )
    else:
        print("Resumos 2D ignorados pelas opções de execução.")

        timing.skip(
            "Resumos 2D",
            f"desativados no modo {options.mode.value}",
        )

    print("[4/5] Salvando resultados...")

    with timing.step("Salvamento resultados 2D"):
        write_results_json(results, output_dir / "resultados.json")

    if options.generate_plots:
        print("[5/5] Gerando resultados gráficos...")
        from plots.diagrams import generate_all_diagrams

        with timing.step("Gráficos 2D"):
            generate_all_diagrams(model, results, output_dir)
    else:
        print("[5/5] Gráficos 2D ignorados pelas opções de execução.")

        timing.skip("Gráficos 2D", "desativados pelas opções de execução",)

    timing_report = timing.save(output_dir)
    timing.print_summary()

    return results


def run_single_analysis_3d(model, output_dir: Path, timing=None, options: ExecutionOptions | None = None,) -> dict:
    """
    Executa uma análise 3D.

    Nesta etapa:
    - reolve com solver_3d;
    - salva JSON;
    - não gera diagramas;
    - não roda pós-processamento 2D.
    """

    options = options or ExecutionOptions()

    limit_state = str(
       getattr(model, "limit_state", "GENERIC")
    ).strip().upper()

    if limit_state not in {"ELU", "ELS", "GENERIC"}:
         raise ValueError(
            f"Estado limite inválido no modelo: {limit_state}"
         )

    generate_strength_reports = limit_state in {"ELU", "GENERIC"}

    from core.validation import validate_model
    from core.solver_3d import solve_structure_3d
    from io_module.results_writer import write_results_json
    from core.deflection import write_preliminary_deflection_summary_txt
    from core.envelope_3d import create_envelope_3d, save_envelope_3d_json
    from core.envelope_csv_3d import write_envelope_3d_csv
    from core.envelope_report_3d import write_envelope_3d_report_txt
    from core.displacement_report_3d import write_displacement_summary_3d_txt
    from core.displacement_csv_3d import write_displacements_3d_csv
    from core.beam_design_3d import design_frame3d_beams_preliminary
    from core.beam_design_csv_3d import write_beam_design_3d_csv
    from core.beam_design_report_3d import write_beam_design_3d_report_txt
    from core.beam_shear_torsion_3d import create_beam_shear_torsion_report_3d
    from core.beam_shear_torsion_csv_3d import write_beam_shear_torsion_3d_csv
    from core.beam_shear_torsion_report_3d import write_beam_shear_torsion_3d_report_txt
    from core.column_critical_3d import create_column_critical_forces_3d
    from core.column_critical_csv_3d import write_column_critical_forces_3d_csv
    from core.column_critical_report_3d import write_column_critical_forces_3d_report_txt
    from core.design_summary_3d import write_frame3d_memorial_txt
    from core.timing import TimingReport


    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Estado limite: {limit_state}")

    timing = timing or TimingReport()

    print("[3/5] Validando e resolvendo modelo estrutural 3D...")

    with timing.step("Validação do modelo 3D"):
        validate_model(model)

    with timing.step("Solver 3D"):
        results = solve_structure_3d(model)

    if options.generate_summaries:
        with timing.step("Resumo e flechas 3D"):
            print_analysis_summary_3d(results)

            write_preliminary_deflection_summary_txt(model=model, results=results, file_path=output_dir / "resumo_flechas.txt",)
    else:
        print("Resumos 3D ignorados pelas opções de execução.")

        timing.skip("Resumo e flechas 3D", f"desativados no modo {options.mode.value}")
    print("[4/5] Salvando resultados...")

    with timing.step("Salvamento resultados 3D"):
        write_results_json(results, output_dir / "resultados.json")


    if not options.generate_detailed_reports:
        reason = f"desativados no modo {options.mode.value}"

        skipped_steps = (
            "Envoltória 3D",
            "Deslocamentos 3D",
            "Dimensionamento preliminar vigas 3D",
            "Cortante e torção vigas 3D",
            "Pilares 3D",
            "Memorial 3D",
        )

        for step_name in skipped_steps:
            timing.skip(step_name, reason)

        timing.skip(
            "Gráficos PNG 3D",
            reason,
        )

        timing.skip(
            "HTML interativo 3D",
            reason,
        )

        timing_report = timing.save(output_dir)
        timing.print_summary(timing_report)

        return results

    with timing.step("Envoltória 3D"):
        envelope = create_envelope_3d({"ANALISE_UNICA": results})

        save_envelope_3d_json(
            envelope,
            Path(output_dir) / "envoltoria_3d.json",
        )

        write_envelope_3d_csv(
            envelope,
            Path(output_dir) / "envoltoria_3d.csv",
        )

        write_envelope_3d_report_txt(
            envelope,
            Path(output_dir) / "resumo_envoltoria_3d.txt",
        )

    with timing.step("Deslocamentos 3D"):
        write_displacement_summary_3d_txt(
            results,
            Path(output_dir) / "resumo_deslocamentos_3d.txt",
        )

        write_displacements_3d_csv(
            results,
            Path(output_dir) / "deslocamentos_3d.csv",
        )

    if generate_strength_reports:

        with timing.step("Dimensionamento preliminar vigas 3D"):
            beam_design_3d = design_frame3d_beams_preliminary(
                model=model,
                envelope=envelope,
            )

            write_beam_design_3d_csv(
                beam_design_3d,
                Path(output_dir) / "dimensionamento_vigas_3d.csv",
            )

            write_beam_design_3d_report_txt(
                beam_design_3d,
                Path(output_dir) / "resumo_dimensionamento_vigas_3d.txt",
            )

        with timing.step("Cortante e torção vigas 3D"):
            beam_shear_torsion_3d = create_beam_shear_torsion_report_3d(
                model=model,
                envelope=envelope,
            )

            write_beam_shear_torsion_3d_csv(
                beam_shear_torsion_3d,
                Path(output_dir) / "vigas_cortante_torcao_3d.csv",
            )

            write_beam_shear_torsion_3d_report_txt(
                beam_shear_torsion_3d,
                Path(output_dir) / "resumo_vigas_cortante_torcao_3d.txt",
            )

        with timing.step("Pilares 3D"):
            column_forces_3d = create_column_critical_forces_3d(
                model=model,
                envelope=envelope,
            )

            write_column_critical_forces_3d_csv(
                column_forces_3d,
                Path(output_dir) / "pilares_3d.csv",
            )

            write_column_critical_forces_3d_report_txt(
                column_forces_3d,
                Path(output_dir) / "resumo_pilares_3d.txt",
            )

        with timing.step("Memorial 3D"):
            write_frame3d_memorial_txt(
                model=model,
                results=results,
                envelope=envelope,
                beam_design=beam_design_3d,
                column_report=column_forces_3d,
                output_path=Path(output_dir) / "memorial_3d.txt",
            )

    else:
        reason = (
            "não aplicável à combinação ELS; "
            "relatórios de resistência usam combinações ELU"
        )

        timing.skip(
            "Dimensionamento preliminar vigas 3D",
            reason,
        )
        timing.skip(
            "Cortante e torção vigas 3D",
            reason,
        )
        timing.skip(
            "Pilares 3D",
            reason,
        )
        timing.skip(
            "Memorial 3D",
            reason,
        )

        print()
        print(
            "Combinação ELS: verificação e relatórios de resistência "
            "foram ignorados. Resultados de análise, deslocamentos e "
            "saídas gráficas continuam sendo gerados."
        )

    print("[5/5] Processando saídas gráficas 3D...")

    if options.generate_plots:
        from plots.diagrams_3d import generate_all_diagrams_3d

        with timing.step("Gráficos PNG 3D"):
            generate_all_diagrams_3d(model, results, output_dir)
    else:
        print("Gráficos PNG 3D ignorados pelas opções de execução.")

        timing.skip("Gráficos PNG 3D", "desativados pelas opções de execução",)

    if options.generate_html:
        from plots.interactive_3d import generate_all_interactive_diagrams_3d

        with timing.step("HTML interativo 3D"):
            interactive_outputs = generate_all_interactive_diagrams_3d(
                model=model,
                results=results,
                output_dir=output_dir,
            )

        if interactive_outputs.get("structure_html"):
            print(
                "Visual interativo salvo em: "
                f"{interactive_outputs['structure_html']}"
            )
    else:
        print("HTML interativo 3D ignorado pelas opções de execução.")

        timing.skip("HTML interativo 3D", "desativado pelas opções de execução",)

    if options.validate_only:
        from core.validation import validate_model

        validate_model(model)

        print()
        print("=" * 60)
        print("Validação concluída com sucesso.")
        print("=" * 60)
        print("O modelo estrutural é válido.")
        print("O solver não foi executado.")
        print("Nenhum arquivo de saída foi criado.")
        return

    timing_report = timing.save(output_dir)
    timing.print_summary()

    return results


def print_analysis_summary_3d(results: dict) -> None:
    """
    Imprime um resumo da análise 3D.
    """

    print()
    print("-" * 60)
    print("Resumo da análise 3D")
    print("-" * 60)
    print(f"Nós:                {results['number_of_nodes']}")
    print(f"Elementos:          {results['number_of_elements']}")
    print(f"Graus de liberdade: {results['number_of_dofs']}")

    displacement_entry = find_max_abs_result_entry(
        rows=results["displacements"],
        keys=("ux", "uy", "uz"),
    )

    rotation_entry = find_max_abs_result_entry(
        rows=results["displacements"],
        keys=("rx", "ry", "rz"),
    )

    reaction_force_entry = find_max_abs_result_entry(
        rows=results["reactions"],
        keys=("fx", "fy", "fz"),
    )

    reaction_moment_entry = find_max_abs_result_entry(
        rows=results["reactions"],
        keys=("mx", "my", "mz"),
    )

    print()
    print("Deslocamentos máximos:")

    if displacement_entry:
        print(
            f"  |{displacement_entry['key']}|max = "
            f"{displacement_entry['value']:.6e} m no nó {displacement_entry['node']}"
        )

    if rotation_entry:
        print(
            f"  |{rotation_entry['key']}|max = "
            f"{rotation_entry['value']:.6e} rad no nó {rotation_entry['node']}"
        )

    print()
    print("Reações máximas:")

    if reaction_force_entry:
        print(
            f"  |{reaction_force_entry['key']}|max = "
            f"{reaction_force_entry['value']:.6e} kN no nó {reaction_force_entry['node']}"
        )

    if reaction_moment_entry:
        print(
            f"  |{reaction_moment_entry['key']}|max = "
            f"{reaction_moment_entry['value']:.6e} kN.m no nó {reaction_moment_entry['node']}"
        )

    print()
    print("Esforços internos máximos locais:")
    print("  Observação: os esforços abaixo estão no sistema local de cada barra.")

    print_max_element_force_3d(
        results,
        label="Normal",
        keys=("normal_i", "normal_j"),
        unit="kN",
    )

    print_max_element_force_3d(
        results,
        label="Cortante local y",
        keys=("shear_y_i", "shear_y_j"),
        unit="kN",
    )

    print_max_element_force_3d(
        results,
        label="Cortante local z",
        keys=("shear_z_i", "shear_z_j"),
        unit="kN",
    )

    print_max_element_force_3d(
        results,
        label="Torção local x",
        keys=("torsion_i", "torsion_j"),
        unit="kN.m",
    )

    print_max_element_force_3d(
        results,
        label="Momento local y",
        keys=("moment_y_i", "moment_y_j"),
        unit="kN.m",
    )

    print_max_element_force_3d(
        results,
        label="Momento local z",
        keys=("moment_z_i", "moment_z_j"),
        unit="kN.m",
    )

    print_global_equilibrium_3d(results)

def print_global_equilibrium_3d(results: dict) -> None:
    """
    Imprime o equilíbrio global 3D.
    """

    equilibrium = results.get("equilibrium")

    if not equilibrium:
        return

    sum_forces = equilibrium["sum_forces"]
    sum_moments = equilibrium["sum_moments"]

    print()
    print("Equilíbrio global 3D:")
    print(f"  ΣFx = {sum_forces['fx']:.6e}")
    print(f"  ΣFy = {sum_forces['fy']:.6e}")
    print(f"  ΣFz = {sum_forces['fz']:.6e}")
    print(f"  ΣMx = {sum_moments['mx']:.6e}")
    print(f"  ΣMy = {sum_moments['my']:.6e}")
    print(f"  ΣMz = {sum_moments['mz']:.6e}")
    print(f"  Norma forças:   {equilibrium['force_norm']:.6e}")
    print(f"  Norma momentos: {equilibrium['moment_norm']:.6e}")
    print(f"  Tolerância:     {equilibrium['tolerance']:.6e}")
    print(f"  Status: {equilibrium['status']}")


def print_max_element_force_3d(
    results: dict,
    label: str,
    keys: tuple[str, ...],
    unit: str,
) -> None:
    """
    Imprime o maior esforço local de um grupo de chaves.
    """

    entry = find_max_abs_element_force_entry(
        elements=results["elements"],
        keys=keys,
    )

    if entry is None:
        return

    print(
        f"  |{label}|max = {entry['value']:.6e} {unit} "
        f"no elemento {entry['element']}, chave {entry['key']}"
    )


def find_max_abs_result_entry(rows, keys):
    """
    Procura o maior valor absoluto em uma lista de dicionários.
    """

    best = None

    for row in rows:
        for key in keys:
            value = float(row.get(key, 0.0))

            candidate = {
                "node": row.get("node"),
                "key": key,
                "value": value,
                "abs_value": abs(value),
            }

            if best is None or candidate["abs_value"] > best["abs_value"]:
                best = candidate

    return best


def find_max_abs_element_force_entry(elements, keys):
    """
    Procura o maior valor absoluto nos esforços locais dos elementos 3D.
    """

    best = None

    for element in elements:
        local_end_forces = element.get("local_end_forces", {})

        for key in keys:
            value = float(local_end_forces.get(key, 0.0))

            candidate = {
                "element": element.get("id"),
                "key": key,
                "value": value,
                "abs_value": abs(value),
            }

            if best is None or candidate["abs_value"] > best["abs_value"]:
                best = candidate

    return best


def group_combination_results_by_limit_state(
    combination_results: dict,
    combination_limit_states: dict[str, str],
) -> dict[str, dict]:
    """
    Separa resultados de combinações em ELU, ELS e GENERIC.
    """

    grouped_results = {
        "ELU": {},
        "ELS": {},
        "GENERIC": {},
    }

    for combination_name, results in combination_results.items():
        limit_state = str(
            combination_limit_states.get(
                combination_name,
                "GENERIC",
            )
        ).strip().upper()

        if limit_state not in grouped_results:
            raise ValueError(
                f"Estado limite inválido na combinação "
                f"'{combination_name}': {limit_state}"
            )

        grouped_results[limit_state][combination_name] = results

    return grouped_results

def write_frame3d_limit_state_outputs(
    model,
    grouped_results: dict[str, dict],
    output_dir: Path,
) -> dict[str, dict]:
    """
    Gera envoltórias 3D consolidadas e saídas de resistência por estado limite.

    ELU:
    - envoltória de esforços;
    - vigas;
    - cortante/torção;
    - pilares.

    ELS:
    - envoltória de esforços.

    A envoltória consolidada de deslocamentos será tratada separadamente.
    """

    from core.envelope_3d import (
        create_envelope_3d,
        save_envelope_3d_json,
    )
    from core.envelope_csv_3d import write_envelope_3d_csv
    from core.envelope_report_3d import write_envelope_3d_report_txt

    generated_envelopes = {}

    # ======================================================
    # ELU
    # ======================================================

    elu_results = grouped_results.get("ELU", {})

    if elu_results:
        print()
        print("=" * 60)
        print("Gerando envoltória consolidada 3D - ELU")
        print("=" * 60)

        envelope_elu = create_envelope_3d(elu_results)
        generated_envelopes["ELU"] = envelope_elu

        save_envelope_3d_json(
            envelope_elu,
            output_dir / "envoltoria_3d_elu.json",
        )

        write_envelope_3d_csv(
            envelope_elu,
            output_dir / "envoltoria_3d_elu.csv",
        )

        write_envelope_3d_report_txt(
            envelope_elu,
            output_dir / "resumo_envoltoria_3d_elu.txt",
        )

        from core.beam_design_3d import (
            design_frame3d_beams_preliminary,
        )
        from core.beam_design_csv_3d import (
            write_beam_design_3d_csv,
        )
        from core.beam_design_report_3d import (
            write_beam_design_3d_report_txt,
        )

        beam_design_elu = design_frame3d_beams_preliminary(
            model=model,
            envelope=envelope_elu,
        )

        write_beam_design_3d_csv(
            beam_design_elu,
            output_dir / "dimensionamento_vigas_3d_elu.csv",
        )

        write_beam_design_3d_report_txt(
            beam_design_elu,
            output_dir / "resumo_dimensionamento_vigas_3d_elu.txt",
        )

        from core.beam_shear_torsion_3d import (
            create_beam_shear_torsion_report_3d,
        )
        from core.beam_shear_torsion_csv_3d import (
            write_beam_shear_torsion_3d_csv,
        )
        from core.beam_shear_torsion_report_3d import (
            write_beam_shear_torsion_3d_report_txt,
        )

        beam_shear_elu = create_beam_shear_torsion_report_3d(
            model=model,
            envelope=envelope_elu,
        )

        write_beam_shear_torsion_3d_csv(
            beam_shear_elu,
            output_dir / "vigas_cortante_torcao_3d_elu.csv",
        )

        write_beam_shear_torsion_3d_report_txt(
            beam_shear_elu,
            output_dir / "resumo_vigas_cortante_torcao_3d_elu.txt",
        )

        from core.column_critical_3d import (
            create_column_critical_forces_3d,
        )
        from core.column_critical_csv_3d import (
            write_column_critical_forces_3d_csv,
        )
        from core.column_critical_report_3d import (
            write_column_critical_forces_3d_report_txt,
        )

        columns_elu = create_column_critical_forces_3d(
            model=model,
            envelope=envelope_elu,
        )

        write_column_critical_forces_3d_csv(
            columns_elu,
            output_dir / "pilares_3d_elu.csv",
        )

        write_column_critical_forces_3d_report_txt(
            columns_elu,
            output_dir / "resumo_pilares_3d_elu.txt",
        )

        print(
            f"Combinações ELU consolidadas: "
            f"{', '.join(elu_results.keys())}"
        )

    else:
        print()
        print("Nenhuma combinação ELU encontrada.")

    # ======================================================
    # ELS
    # ======================================================

    els_results = grouped_results.get("ELS", {})

    if els_results:
        print()
        print("=" * 60)
        print("Gerando envoltória consolidada 3D - ELS")
        print("=" * 60)

        envelope_els = create_envelope_3d(els_results)
        generated_envelopes["ELS"] = envelope_els

        save_envelope_3d_json(
            envelope_els,
            output_dir / "envoltoria_3d_els.json",
        )

        write_envelope_3d_csv(
            envelope_els,
            output_dir / "envoltoria_3d_els.csv",
        )

        write_envelope_3d_report_txt(
            envelope_els,
            output_dir / "resumo_envoltoria_3d_els.txt",
        )

        from core.displacement_envelope_3d import (
            create_displacement_envelope_3d,
            save_displacement_envelope_3d_json,
            write_displacement_envelope_3d_csv,
            write_displacement_envelope_3d_report_txt,
        )

        displacement_envelope_els = (
            create_displacement_envelope_3d(
                els_results
            )
        )

        save_displacement_envelope_3d_json(
            displacement_envelope_els,
            output_dir
            / "envoltoria_deslocamentos_3d_els.json",
        )

        write_displacement_envelope_3d_csv(
            displacement_envelope_els,
            output_dir
            / "envoltoria_deslocamentos_3d_els.csv",
        )

        write_displacement_envelope_3d_report_txt(
            displacement_envelope_els,
            output_dir
            / "resumo_envoltoria_deslocamentos_3d_els.txt",
        )


        print(
            f"Combinações ELS consolidadas: "
            f"{', '.join(els_results.keys())}"
        )

    else:
        print()
        print("Nenhuma combinação ELS encontrada.")

    generic_results = grouped_results.get("GENERIC", {})

    if generic_results:
        print()
        print(
            "Aviso: combinações sem estado limite declarado "
            "não foram incluídas nas envoltórias ELU ou ELS:"
        )

        for combination_name in generic_results:
            print(f"  - {combination_name}")

    return generated_envelopes

def run_analysis(input_file: Path, output_dir: Path, options: ExecutionOptions | None = None) -> None:
    """
    Executa a análise estrutural a partir de um arquivo JSON.

    Suporta:
    - modelo simples com nodal_loads/distributed_loads;
    - load_cases;
    - combinations.
    """

    options = options or ExecutionOptions()

    if not input_file.exists():
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {input_file}")

    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Estruturalis - Análise Estrutural")
    print("=" * 60)
    print(f"Arquivo de entrada: {input_file}")

    if options.validate_only:
        print("Modo de execução:     somente validação")
    else:
        print(f"Pasta de saída:      {output_dir}")

    print()

    if options.validate_only:
        print("[1/1] Lendo e validando modelo estrutural...")
    else:
        print("[1/5] Lendo modelo estrutural...")

    from io_module.json_reader import read_model_from_json

    model = read_model_from_json(input_file)

    print(f"Tipo de análise: {model.analysis_type}")

    frame3d_only_modes = {
        ExecutionMode.SOLVER_ONLY,
        ExecutionMode.SUMMARY_ONLY,
        ExecutionMode.REPORTS_ONLY,
    }

    if (
        model.analysis_type != "frame3d"
        and options.mode in frame3d_only_modes
    ):
        raise ValueError(
            f"O modo --{options.mode.value.replace('_', '-')} "
            "está disponível somente para análises frame3d."
        )

    if options.generate_summaries:
        from core.normative_report import write_normative_summary_txt

        normative_summary_path = output_dir / "resumo_normativo.txt"
        write_normative_summary_txt(model, normative_summary_path)

        print(f"Resumo normativo salvo em: {normative_summary_path}")
    else:
        print(
            "Resumo normativo ignorado no modo "
            f"{options.mode.value}."
        )

    print()


    print("[2/5] Preparando análises...")

    from core.load_cases import (
        has_combinations,
        has_load_cases,
        build_model_for_combination,
        build_model_for_load_case,
    )

    if has_combinations(model):
        print(f"Foram encontradas {len(model.combinations)} combinações.")
        print()

        combination_results = {}
        combination_limit_states = {}

        for combination in model.combinations:
            print("=" * 60)
            print(f"Analisando combinação: {combination.name}")
            print("=" * 60)

            combined_model = build_model_for_combination(
                model,
                combination,
            )

            combination_output_dir = output_dir / combination.name

            results = run_single_analysis(
                combined_model,
                combination_output_dir,
                options=options,
            )

            combination_results[combination.name] = results
            combination_limit_states[combination.name] = (
                combination.limit_state
            )

            print()
            print(
                "Resultados da combinação salvos em: "
                f"{combination_output_dir}"
            )
            print()

        if model.analysis_type == "frame3d":
            grouped_results = group_combination_results_by_limit_state(
                combination_results=combination_results,
                combination_limit_states=combination_limit_states,
            )

            if options.generate_detailed_reports:
                write_frame3d_limit_state_outputs(
                    model=model,
                    grouped_results=grouped_results,
                    output_dir=output_dir,
                )
            else:
                print()
                print(
                    "Envoltórias consolidadas 3D ignoradas no modo "
                    f"{options.mode.value}."
                )

            print()
            print(
                "Análise 3D com combinações concluída com sucesso!"
            )
            print(f"Resultados salvos em: {output_dir}")

            return

        print("=" * 60)
        print("Gerando envoltória de esforços")
        print("=" * 60)

        from core.envelope import create_element_force_envelope
        from core.envelope_report import write_envelope_summary_txt
        from core.envelope_csv import write_envelope_csv
        from core.beam_design import design_beams_from_envelope
        from io_module.results_writer import write_results_json

        envelope = create_element_force_envelope(
            combination_results
        )

        envelope_json_path = output_dir / "envoltoria.json"
        envelope_summary_path = (
            output_dir / "resumo_envoltoria.txt"
        )
        envelope_csv_path = (
            output_dir / "envoltoria_elementos.csv"
        )

        beam_design_csv_path = (
            output_dir / "dimensionamento_vigas.csv"
        )
        beam_design_summary_path = (
            output_dir / "resumo_dimensionamento_vigas.txt"
        )

        write_results_json(
            envelope,
            envelope_json_path,
        )

        write_envelope_summary_txt(
            envelope,
            envelope_summary_path,
        )

        write_envelope_csv(
            envelope,
            envelope_csv_path,
        )

        design_beams_from_envelope(
            model=model,
            envelope=envelope,
            csv_path=beam_design_csv_path,
            txt_path=beam_design_summary_path,
        )

        print(f"Envoltória salva em: {envelope_json_path}")
        print(
            "Resumo da envoltória salvo em: "
            f"{envelope_summary_path}"
        )
        print(
            "CSV da envoltória salvo em: "
            f"{envelope_csv_path}"
        )
        print(
            "Dimensionamento preliminar de vigas salvo em: "
            f"{beam_design_csv_path}"
        )
        print(
            "Resumo do dimensionamento de vigas salvo em: "
            f"{beam_design_summary_path}"
        )
        print()

    elif has_load_cases(model):
        print(f"Foram encontrados {len(model.load_cases)} casos de carregamento.")
        print()

        for load_case in model.load_cases:
            print("=" * 60)
            print(f"Analisando caso de carregamento: {load_case.name}")
            print("=" * 60)

            case_model = build_model_for_load_case(model, load_case.name)
            case_output_dir = output_dir / load_case.name

            run_single_analysis(case_model, case_output_dir, options=options,)

            print()
            print(f"Resultados do caso salvos em: {case_output_dir}")
            print()

    else:
        print("Modelo sem load_cases/combinations. Rodando análise única.")
        print()

        run_single_analysis(model, output_dir, options=options)

    print()
    print("Análise concluída com sucesso!")
    print(f"Resultados salvos em: {output_dir}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="Estruturalis",
        description="Mini software didático de análise estrutural 2D."
    )

    parser.add_argument(
        "input",
        type=str,
        help="Caminho para o arquivo JSON do modelo estrutural."
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="results",
        help="Pasta onde os resultados serão salvos. Padrão: results"
    )

    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Não gera gráficos estáticos PNG."
    )

    parser.add_argument(
        "--no-html",
        action="store_true",
        help="Não gera a visualização HTML interativa"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"Estruturalis {__version__}",
    )

    execution_mode_group = parser.add_mutually_exclusive_group()

    execution_mode_group.add_argument(
        "--fast",
        action="store_true",
        help=(
            "Executa em modo rápido, sem gráficos PNG "
            "e sem HTML interativo."
        ),
    )

    execution_mode_group.add_argument(
        "--solver-only",
        action="store_true",
        help=(
            "No frame3d, executa somente validação, solver "
            "e salvamento dos resultados essenciais."
        ),
    )

    execution_mode_group.add_argument(
        "--summary-only",
        action="store_true",
        help=(
            "No frame3d, gera resultados essenciais e "
            "os principais resumos textuais."
        ),
    )

    execution_mode_group.add_argument(
        "--reports-only",
        action="store_true",
        help=(
            "No frame3d, gera resultados e relatórios, "
            "sem saídas gráficas."
        ),
    )

    execution_mode_group.add_argument(
        "--validate-only",
        action="store_true",
        help=(
            "Valida o arquivo de entrada sem executar o solver "
            "ou gerar arquivos de saída."
        ),
    )


    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    input_file = Path(args.input)
    output_dir = Path(args.output)
    options = ExecutionOptions.from_cli_args(args)

    try:
        run_analysis(input_file, output_dir, options=options)
        return 0

    except Exception as error:
        print()
        print("Erro durante a análise:")
        print(error)
        return 1


if __name__ == "__main__":
    sys.exit(main())
