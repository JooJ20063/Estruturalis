from __future__ import annotations

import json
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class TimingReport:
    """Simple execution timing collector for Estruturalis analysis steps."""

    def __init__(self) -> None:
        self.steps: list[dict[str, float | str]] = []
        self._total_start = time.perf_counter()

    @contextmanager
    def step(self, name: str) -> Iterator[None]:
        start = time.perf_counter()

        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            self.steps.append(
                {
                    "name": name,
                    "status": "executed",
                    "elapsed_seconds": elapsed,
                }
            )

    def skip(self, name: str, reason: str) -> None:
        """
        Registra uma etapa que não foi executada deliberadamente.
        """

        self.steps.append(
            {
                "name": name,
                "status": "skipped",
                "reason": reason,
            }
        )

    @property
    def total_seconds(self) -> float:
        return time.perf_counter() - self._total_start

    def as_dict(self) -> dict:
        return {
            "total_seconds": self.total_seconds,
            "steps": self.steps,
        }

    def format_text(self, report: dict | None = None) -> str:
        report = report or self.as_dict()
        lines = [
            "RELATÓRIO DE TEMPO - Estruturalis",
            "=" * 60,
            "",
        ]

        for item in report["steps"]:
            name = str(item["name"])
            status = str(item.get("status", "executed"))

            if status == "skipped":
                reason = str(item.get("reason", ""))
                message = "IGNORADO"

                if reason:
                    message = f"{message} - {reason}"

                lines.append(f"{name:<40} {message}")
                continue

            elapsed = float(item.get("elapsed_seconds", 0.0))
            lines.append(f"{name:<40} {elapsed:>12.3f} s")
        total_seconds = float(report["total_seconds"])

        lines.extend(
            [
                "",
                "-" * 60,
                f"{'Tempo total':<40} {total_seconds:>12.3f} s",
                "",
            ]
        )

        return "\n".join(lines)

    def print_summary(self, report: dict | None = None) -> None:
        print()
        print(self.format_text())

    def save(self, output_dir: Path) -> None:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        txt_path = output_dir / "relatorio_tempo.txt"
        json_path = output_dir / "relatorio_tempo.json"

        report = self.as_dict()

        txt_path.write_text(self.format_text(), encoding="utf-8")

        json_path.write_text(
            json.dumps(self.as_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
