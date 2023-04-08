from IPython import get_ipython


def is_notebook() -> bool:
    try:
        shell = get_ipython()
        if shell == "ZMQInteractiveShell":
            print("Jupyter notebook or qtconsole")  # Jupyter notebook or qtconsole
        elif shell == "TerminalInteractiveShell":
            print("Terminal running IPython")  # Terminal running IPython
        else:
            print("Other type (?)")  # Other type (?)
    except NameError:
        print(
            "Probably standard Python interpreter"
        )  # Probably standard Python interpreter


is_notebook()
