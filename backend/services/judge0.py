import httpx
from backend.core.config import settings

# Judge0 language IDs (approximate, usually 71 for Python 3)
LANGUAGE_IDS = {
    "python": 71,
    "c": 50,
    "cpp": 54,
    "kotlin": 78
}

import subprocess
import tempfile
import os

async def submit_code_to_judge0(source_code: str, language: str, stdin: str) -> dict:
    lang = language.lower()
    
    if lang not in ["python", "python3", "javascript", "cpp", "c", "java"]:
        return {
            "stdout": "",
            "stderr": f"Language '{language}' is not supported in local fallback mode.",
            "compile_output": "",
            "time_ms": 0,
            "status_id": 13
        }

    # Determine suffix and execution command
    suffix = ".py"
    if lang == "javascript":
        suffix = ".js"
    elif lang == "cpp":
        suffix = ".cpp"
    elif lang == "c":
        suffix = ".c"
    elif lang == "java":
        suffix = ".java"

    # Write code to a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
        f.write(source_code)
        temp_file_path = f.name

    compile_output = ""
    run_cmd = []
    binary_path = ""

    try:
        if lang in ["python", "python3"]:
            run_cmd = ["python", temp_file_path]
        elif lang == "javascript":
            run_cmd = ["node", temp_file_path]
        elif lang == "cpp":
            binary_path = temp_file_path[:-4] + ".out"
            compile_process = subprocess.run(
                ["g++", "-O2", "-Wall", temp_file_path, "-o", binary_path],
                capture_output=True,
                text=True,
                timeout=10.0
            )
            if compile_process.returncode != 0:
                return {
                    "stdout": "",
                    "stderr": "",
                    "compile_output": compile_process.stderr,
                    "time_ms": 0,
                    "status_id": 6 # 6=Compilation Error
                }
            run_cmd = [binary_path]
        elif lang == "c":
            binary_path = temp_file_path[:-2] + ".out"
            compile_process = subprocess.run(
                ["gcc", "-O2", "-Wall", temp_file_path, "-o", binary_path],
                capture_output=True,
                text=True,
                timeout=10.0
            )
            if compile_process.returncode != 0:
                return {
                    "stdout": "",
                    "stderr": "",
                    "compile_output": compile_process.stderr,
                    "time_ms": 0,
                    "status_id": 6
                }
            run_cmd = [binary_path]
        elif lang == "java":
            run_cmd = ["java", temp_file_path]

        # Execute the code
        process = subprocess.run(
            run_cmd,
            input=stdin,
            text=True,
            capture_output=True,
            timeout=5.0
        )
        
        stdout = process.stdout
        stderr = process.stderr
        status_id = 3 if process.returncode == 0 else 11 # 3=Accepted, 11=Runtime Error
        
        return {
            "stdout": stdout,
            "stderr": stderr,
            "compile_output": compile_output,
            "time_ms": 10, # Mock time
            "status_id": status_id
        }
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": "Execution timed out (Limit: 5 seconds).",
            "compile_output": "",
            "time_ms": 5000,
            "status_id": 5 # 5=Time Limit Exceeded
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "compile_output": "",
            "time_ms": 0,
            "status_id": 13 # 13=Internal Error
        }
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        if binary_path and os.path.exists(binary_path):
            os.remove(binary_path)
