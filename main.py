from pathlib import Path
import runpy


PROJECT_ROOT = Path(__file__).resolve().parent
TESTER = PROJECT_ROOT / "Controller Tester" / "controller_tester.py"


if __name__ == "__main__":
    runpy.run_path(str(TESTER), run_name="__main__")
