"""Run the whole Cyclistic workflow in order.

Stages: clean the raw monthly files, then validate the clean table. Each
stage is a module in this package with a main() function. An error or a
failed validation stops the run.

Run with: python -m cyclistic.run_pipeline
"""

import importlib
import time

STAGES = [
    "clean",
    "validate",
]


def main() -> None:
    for name in STAGES:
        print(f"\n>>> Stage: {name}")
        start = time.perf_counter()
        importlib.import_module(f"cyclistic.{name}").main()
        print(f"<<< {name} finished in {time.perf_counter() - start:.1f} s")


if __name__ == "__main__":
    main()
