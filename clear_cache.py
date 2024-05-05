from pathlib import Path
from IPython.paths import get_ipython_cache_dir


def delete_dir(p: Path):
    for sub in p.iterdir():
        if sub.is_dir():
            delete_dir(sub)
        else:
            sub.unlink()
    p.rmdir()


def clear_cache():
    for p in Path(get_ipython_cache_dir() + "\\numba_cache").rglob("*.nb*"):
        p.unlink()
    for p in Path(__file__).parent.parent.rglob("numba_cache"):
        delete_dir(p)
    for p in Path(__file__).parent.parent.rglob("__pycache__"):
        delete_dir(p)
    for p in Path(__file__).parent.parent.rglob("cdk.out"):
        delete_dir(p)
    for p in Path(__file__).parent.parent.rglob("*.py[co]"):
        p.unlink()


if __name__ == "__main__":
    clear_cache()
