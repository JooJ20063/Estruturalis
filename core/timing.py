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
                    "elapsed_seconds": elapsed,
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

    def format_text(self) -> str:
        lines = [
            "RELATÓRIO DE TEMPO - Estruturalis",
            "=" * 60,
            "",
        ]

        for item in self.steps:
            name = str(item["name"])
            elapsed = float(item["elapsed_seconds"])
            lines.append(f"{name:<40} {elapsed:>12.3f} s")

        lines.extend(
            [
                "",
                "-" * 60,
                f"{'Tempo total':<40} {self.total_seconds:>12.3f} s",
                "",
            ]
        )

        return "\n".join(lines)

    def print_summary(self) -> None:
        print()
        print(self.format_text())

    def save(self, output_dir: Path) -> None:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        txt_path = output_dir / "relatorio_tempo.txt"
        json_path = output_dir / "relatorio_tempo.json"

        txt_path.write_text(self.format_text(), encoding="utf-8")

        json_path.write_text(
            json.dumps(self.as_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
