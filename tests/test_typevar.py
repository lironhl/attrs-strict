import typing

import pytest

from attrs_strict import AttributeTypeError, BadTypeError, type_validator, UnionLikeError

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import Mock as MagicMock


@pytest.mark.parametrize("test_type, correct", [(str, "foo"), (int, 42)])
def test_typing_typevar_bound_single_validation_success(test_type, correct):
    SomeTypeVar = typing.TypeVar("SomeTypeVar", bound=test_type)

    validator = type_validator()
    attr = MagicMock()
    attr.type = SomeTypeVar

    validator(None, attr, correct)


@pytest.mark.parametrize(
    "test_type, wrongs", [(str, [42, True]), (int, ["foo", ()])]
)
def test_typing_typevar_bound_single_validation_failure(test_type, wrongs):
    SomeTypeVar = typing.TypeVar("SomeTypeVar", bound=test_type)

    validator = type_validator()
    attr = MagicMock()
    attr.type = SomeTypeVar

    for wrong in wrongs:
        with pytest.raises(AttributeTypeError) as error:
            validator(None, attr, wrong)

    assert "must be TypeVar(SomeTypeVar, bound={})".format(str(test_type)) in str(
        error.value
    )


@pytest.mark.parametrize(
    "container, test_type, correct",
    [
        (typing.List, str, ["foo", "bar"]),
        (typing.Tuple, int, (0,)),
        (typing.Optional, str, None),
    ],

)
def test_typing_typevar_bound_within_container_validation_success(
        container, test_type, correct
):
    SomeTypeVar = typing.TypeVar("SomeTypeVar", bound=test_type)

    validator = type_validator()
    attr = MagicMock()
    attr.type = container[SomeTypeVar]

    validator(None, attr, correct)


@pytest.mark.parametrize(
    "container, test_type, wrongs",
    [
        (typing.List, str, [42, True, "foo", ("foo", "bar")]),
        (typing.Tuple, int, ["foo", 42, [0, 1, "2"]]),
        (typing.Optional, str, [42, (1, 2)]),
    ],
)
def test_typing_typevar_bound_within_container_validation_failure(
        container, test_type, wrongs
):
    SomeTypeVar = typing.TypeVar("SomeTypeVar", bound=test_type)

    validator = type_validator()
    attr = MagicMock()
    attr.type = container[SomeTypeVar]

    for wrong in wrongs:
        with pytest.raises(BadTypeError) as error:
            validator(None, attr, wrong)

    assert "must be {}".format(str(attr.type)) in str(
        error.value
    ) or "is not of type {}".format(str(attr.type)) in str(error.value)


@pytest.mark.parametrize("test_type1, correct1, test_type2, correct2",
                         [(str, "foo", int, 42), (float, 1.0, bool, True)])
def test_typing_typevar_constraints_single_validation_success(test_type1, correct1, test_type2, correct2):
    SomeTypeVar = typing.TypeVar("SomeTypeVar", test_type1, test_type2)

    validator = type_validator()
    attr = MagicMock()
    attr.type = SomeTypeVar

    validator(None, attr, correct1)
    validator(None, attr, correct2)


@pytest.mark.parametrize(
    "test_type1, test_type2, wrongs", [
        (str, tuple, [1.0, True]), (float, bool, ["foo", ()])]
)
def test_typing_typevar_constraints_single_validation_failure(test_type1, test_type2, wrongs):
    SomeTypeVar = typing.TypeVar("SomeTypeVar", test_type1, test_type2)

    validator = type_validator()
    attr = MagicMock()
    attr.type = SomeTypeVar

    for wrong in wrongs:
        with pytest.raises(UnionLikeError) as error:
            validator(None, attr, wrong)

    assert "is not of type TypeVar(SomeTypeVar, {}, {})".format(str(test_type1), str(test_type2)) in str(
        error.value
    )


@pytest.mark.parametrize(
    "container, test_type1, test_type2, correct",
    [
        (typing.List, str, int, ["foo", 5]),
        (typing.Tuple, str, int, ("foo",)),
        (typing.Tuple, str, int, (5,)),
        (typing.Optional, str, bool, None),
    ],

)
def test_typing_typevar_constraints_within_container_validation_success(
        container, test_type1, test_type2, correct
):
    SomeTypeVar = typing.TypeVar("SomeTypeVar", test_type1, test_type2)

    validator = type_validator()
    attr = MagicMock()
    attr.type = container[SomeTypeVar]

    validator(None, attr, correct)


@pytest.mark.parametrize(
    "container, test_type1, test_type2, wrongs",
    [
        (typing.List, int, str, [[(5,)], 5]),
        (typing.Tuple, str, int, [([],), "a"]),
        (typing.Optional, str, bytes, [1.0, (2,)]),
    ],
)
def test_typing_typevar_constraints_within_container_validation_failure(
        container, test_type1, test_type2, wrongs
):
    SomeTypeVar = typing.TypeVar("SomeTypeVar", test_type1, test_type2)

    validator = type_validator()
    attr = MagicMock()
    attr.type = container[SomeTypeVar]

    for wrong in wrongs:
        with pytest.raises(BadTypeError) as error:
            validator(None, attr, wrong)

    assert "must be {}".format(str(attr.type)) in str(
        error.value
    ) or "is not of type"


def test_typing_typevar_any_single_validation():
    SomeTypeVar = typing.TypeVar("SomeTypeVar")

    validator = type_validator()
    attr = MagicMock()
    attr.type = SomeTypeVar

    for correct in [1, "foo"]:
        validator(None, attr, correct)


def test_typing_typevar_any_container_validation():
    SomeTypeVar = typing.TypeVar("SomeTypeVar")

    validator = type_validator()
    attr = MagicMock()
    attr.type = typing.List[SomeTypeVar]

    for correct in [[1], ["foo"]]:
        validator(None, attr, correct)
