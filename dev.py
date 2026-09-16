"""Small, dependency-free local runner for Mesa247."""
from __future__ import annotations

import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"


def command(name: str) -> str:
    path = shutil.which(name) or shutil.which(f"{name}.cmd")
    if not path:
        raise SystemExit(f"Falta el requisito '{name}'. Instala Python y Node.js/npm y vuelve a intentarlo.")
    return path


def run(args: list[str], cwd: Path) -> None:
    try:
        subprocess.run(args, cwd=cwd, check=True)
    except subprocess.CalledProcessError as error:
        command_text = " ".join(args[:3])
        raise SystemExit(f"Falló el comando '{command_text}' (código {error.returncode}). Revisa el mensaje anterior.") from error


def setup() -> None:
    command("node"); command("npm")
    run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], BACKEND)
    run([sys.executable, "-m", "alembic", "upgrade", "head"], BACKEND)
    run([sys.executable, "-m", "app.seed"], BACKEND)
    run([command("npm"), "install"], FRONTEND)


def test() -> None:
    run([sys.executable, "-m", "pytest"], BACKEND)
    run([command("npm"), "test"], FRONTEND)


def serve() -> None:
    python = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"], cwd=BACKEND)
    npm = subprocess.Popen([command("npm"), "run", "dev"], cwd=FRONTEND)
    print("Backend: http://localhost:8000 | Frontend: http://localhost:5173")
    try:
        while python.poll() is None and npm.poll() is None:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        for process in (python, npm):
            if process.poll() is None:
                process.terminate()


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "run"
    if action == "setup": setup()
    elif action == "test": test()
    elif action == "run": serve()
    else: raise SystemExit("Uso: python dev.py [setup|run|test]")
