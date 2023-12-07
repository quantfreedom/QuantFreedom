from pathlib import Path
import griffe
import mkdocs_gen_files

from quantfreedom.utils import delete_dir

nav = mkdocs_gen_files.Nav()

try:
    Path(Path(__file__).parent / "docs/summary.md").unlink()
    delete_dir(Path(__file__).parent / "docs" / "quantfreedom")
except:
    pass
src = Path(__file__).parent / "quantfreedom"
data = griffe.load("quantfreedom")

for path in sorted(src.rglob("*.py")):
    if "_github" in str(path):
        continue

    module_path = path.relative_to(src.parent).with_suffix("")

    parts = tuple(module_path.parts)

    try:
        if parts[-1] == "__init__":
            parts = parts[:-1]
            if not data[parts[1:]].has_docstring:
                continue
        if not data[parts[1:]].has_docstrings:
            continue
    except:
        if not data.has_docstring:
            continue
    doc_path = path.relative_to(src.parent).with_suffix(".md")

    nav[parts] = doc_path.as_posix()
    with mkdocs_gen_files.open(doc_path, "w") as fd:
        ident = ".".join(parts)
        fd.write(f"::: {ident}")

    mkdocs_gen_files.set_edit_path(doc_path, Path("../") / path)

with mkdocs_gen_files.open("summary.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
