from __future__ import annotations
from pathlib import Path

def _compute_project_root() -> Path:
    # 1) Anchor relative to this file (src/jpower/paths.py → repo root)
    try:
        here = Path(__file__).resolve()
        repo_root = here.parents[2]
        if (repo_root / "pyproject.toml").exists() or (repo_root / ".git").exists():
            return repo_root
    except Exception:
        pass

    # 2) Fallback: climb from CWD looking for markers
    markers = (".git", "pyproject.toml", "src")
    p = Path.cwd().resolve()
    for cand in (p, *p.parents):
        if any((cand / m).exists() for m in markers):
            return cand
    return p  # last resort

ROOT = _compute_project_root()
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
