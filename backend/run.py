"""
STTS Backend Entry Point
─────────────────────────
Run the FastAPI server with: python run.py
"""

import os
import sys
import subprocess


def ensure_venv():
    """Check if running inside the project venv. If not, re-exec with venv Python."""
    venv_dir = os.path.join(os.path.dirname(__file__), "venv")

    # Determine venv python path
    if sys.platform == "win32":
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        venv_python = os.path.join(venv_dir, "bin", "python")

    # Check if we're already in the venv
    if os.path.exists(venv_python) and sys.executable != os.path.abspath(venv_python):
        print(f"Re-launching with venv Python: {venv_python}")
        result = subprocess.call([venv_python, __file__] + sys.argv[1:])
        sys.exit(result)


def ensure_mongodb():
    """Ensure MongoDB container is running with a persistent volume."""
    import shutil
    if not shutil.which("docker"):
        print("⚠️  Docker not found — skipping MongoDB auto-start. Ensure MongoDB is running manually.")
        return

    # Check if container already running
    result = subprocess.run(
        ["docker", "inspect", "-f", "{{.State.Running}}", "stts-mongodb"],
        capture_output=True, text=True
    )
    if result.returncode == 0 and "true" in result.stdout.strip():
        print("✅ MongoDB container already running.")
        return

    # Stop and remove any stopped container
    subprocess.call(["docker", "stop", "stts-mongodb"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    subprocess.call(["docker", "rm", "stts-mongodb"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

    # Start with persistent volume (unifying with docker-compose naming)
    print("📦 Starting MongoDB with persistent volume: stts-mongo-data...")
    result = subprocess.call([
        "docker", "run", "-d",
        "--name", "stts-mongodb",
        "-p", "27017:27017",
        "-v", "stts-mongo-data:/data/db",
        "mongo:7"
    ])
    if result != 0:
        print("❌ Failed to start MongoDB container! Please ensure Docker Desktop is running.")
        print("   You can start Docker Desktop manually, then re-run this script.")
    else:
        print("✅ MongoDB container started successfully.")


def main():
    """Start the STTS API server."""
    ensure_mongodb()

    import uvicorn
    from app.config import get_settings

    settings = get_settings()

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )


if __name__ == "__main__":
    ensure_venv()
    main()
