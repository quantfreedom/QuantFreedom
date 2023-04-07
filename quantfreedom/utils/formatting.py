def pretty(object) -> None:
    try:
        object._fields[0]
        items = []
        indent = str("    ")
        for x in range(len(object)):
            items.append(indent + object._fields[x] + " = " + str(object[x]) + ",\n")
        print(type(object).__name__ + "(" + "\n" + "".join(items) + ")")
    except:
        print(object)
