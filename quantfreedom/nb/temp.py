def abc(
    a: int,
    c=[1, 2],
)-> int:
    
    if a > 10:
        raise AssertionError("a is more than 10")

    return c
