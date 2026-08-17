import sys
import io
import traceback
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any


def execute_python_code_and_tests(code: str, tests: str) -> Dict[str, Any]:
    """
    Executes Python code and tests in an isolated subprocess and captures stdout, stderr, and exit status.
    """
    combined_script = f"""
# ---- Generated Solution Code ----
{code}

# ---- Generated Unit Tests ----
{tests}
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as tmp:
        tmp_path = Path(tmp.name)
        tmp.write(combined_script)

    try:
        result = subprocess.run(
            [sys.executable, str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=15
        )
        success = result.returncode == 0
        return {
            "success": success,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "error": None if success else (result.stderr or "Non-zero exit code")
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Execution timed out (15s limit)",
            "exit_code": -1,
            "error": "Execution timed out"
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "exit_code": -1,
            "error": traceback.format_exc()
        }
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass
