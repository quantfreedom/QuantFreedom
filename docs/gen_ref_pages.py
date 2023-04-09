import mkdocs_gen_files
from pathlib import Path

for path in Path('../quantfreedom').rglob("*.py"):
    module_path = path.relative_to('../quantfreedom').with_suffix("")  # 
    doc_path = path.relative_to('../quantfreedom').with_suffix(".md")  # 
    full_doc_path = Path('api', doc_path)  # 
    parts = list(module_path.parts)

    if parts[-1] == "__init__":  # 
        parts = parts[:-1]
    elif parts[-1] == "__main__":
        continue

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:  # 
        identifier = ".".join(parts)  # 
        print("::: " + identifier, file=fd)  # 

    mkdocs_gen_files.set_edit_path(full_doc_path, 'gen_ref_pages.py')