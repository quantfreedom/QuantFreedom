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

    # if parts[-1] == "__init__":
    #     parts = parts[:-1]
    #     init_module = data[parts[1:]] if len(parts) > 1 else data
    #     if not init_module.has_docstring:
    #         continue
    # elif not data[parts[1:]].has_docstrings:
    #     continue
    
    if parts[-1] == "__init__":
        # We're currently handling an __init__.py file.
        # Remove "__init__" suffix for accessing Griffe object in data.
        parts = parts[:-1]

        # Get Griffe object. If there's only one item in `parts`,
        # it's the package name, so it's simply `data` (which is the package collected by Griffe).
        # If there are more parts, we access the object by removing the first part, which is the package name,
        # because `data` is already the package.
        init_module = data[parts[1:]] if len(parts) > 1 else data

        # We consider the __init__ module "has docstrings" if:
        # - it has a module docstring
        # - or any of its members has a docstring
        # (attributes, functions, classes, but not modules or objects imported from other modules)
        has_docstrings = init_module.has_docstring or any(
            member.has_docstrings for member in init_module.members.values()
            if not (member.is_alias or member.is_module)
        ) 
    else:
        # If it's another module, simply use `has_docstrings` as a non-init module cannot have submodules anyway.
        has_docstrings = data[parts[1:]].has_docstrings

    # If we didn't find docstrings, continue to the next module file.
    if not has_docstrings:
        continue

    doc_path = path.relative_to(src.parent).with_suffix(".md")

    nav[parts] = doc_path.as_posix()
    with mkdocs_gen_files.open(doc_path, "w") as fd:
        ident = ".".join(parts)
        fd.write(f"::: {ident}")

    mkdocs_gen_files.set_edit_path(doc_path, Path("../") / path)

with mkdocs_gen_files.open("summary.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
