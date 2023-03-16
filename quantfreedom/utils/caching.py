from pathlib import Path
import os
dir_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../..'))

def delete_dir(p):
    for sub in p.iterdir():
        if sub.is_dir():
            delete_dir(sub)
        else:
            sub.unlink()
    p.rmdir()

def clear_cache():
    for p in Path(dir_path).parent.parent.rglob("numba_cache"):
        delete_dir(p)
    for p in Path(__file__).parent.parent.rglob("__pycache__"):
        delete_dir(p)
    for p in Path(__file__).parent.parent.rglob("*.py[co]"):
        p.unlink()