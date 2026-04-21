"""Launch AgriShield-TN using the venv Streamlit (always correct version)."""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
venv_streamlit = ROOT / "venv" / "Scripts" / "streamlit.exe"

if not venv_streamlit.exists():
    sys.exit("venv not found — run: python -m venv venv && venv\\Scripts\\pip install -r requirements.txt")

subprocess.run([str(venv_streamlit), "run", "app/streamlit_app.py"], cwd=ROOT)
