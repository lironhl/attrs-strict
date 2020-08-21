def is_newtype(type_):
    return (
        hasattr(type_, "__name__")
        and hasattr(type_, "__supertype__")
        and type_.__module__ == "typing"
    )


def is_typevar(type_):
    return (
        hasattr(type_, "__name__")
        and hasattr(type_, "__bound__")
        and hasattr(type_, "__constraints__")
        # and type_.__module__ == "typing"
    )


def format_type(type_):
    if is_newtype(type_):
        return "NewType({}, {})".format(type_.__name__, type_.__supertype__)
    elif is_typevar(type_):
        bound = type_.__bound__
        constraints = type_.__constraints__

        types_str = ""
        if bound is not None:
            types_str = ", bound={}".format(format_type(bound))
        elif len(constraints) != 0:
            types_str = ", {}".format(", ".join(format_type(c)
                                                for c in constraints))

        return "TypeVar({}{})".format(type_.__name__, types_str)

    return str(type_)
