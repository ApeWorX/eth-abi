import pytest
from hypothesis import (
    example,
    given,
)
from hypothesis import (
    strategies as st,
)

from eth_abi.exceptions import (
    ABITypeError,
    ParseError,
)
from eth_abi.grammar import (
    TYPE_ALIASES,
    BasicType,
    TupleType,
    normalize,
    parse,
)
from tests.core.common.strategies import (
    malformed_type_strs,
    type_strs,
)


@pytest.mark.parametrize(
    "type_str, expected_type",
    (
        ("custom", BasicType("custom")),
        ("Custom", BasicType("Custom")),
        ("CUSTOM", BasicType("CUSTOM")),
        ("Custom[2]", BasicType("Custom", None, ((2,),))),
        ("uint", BasicType("uint")),
        ("uint256", BasicType("uint", 256)),
        ("uint256[]", BasicType("uint", 256, ((),))),
        ("uint256[][1][23][]", BasicType("uint", 256, ((), (1,), (23,), ()))),
        ("uint[]", BasicType("uint", None, ((),))),
        ("int[2]", BasicType("int", None, ((2,),))),
        ("fixed128x19", BasicType("fixed", (128, 19))),
        ("ufixed128x19[][]", BasicType("ufixed", (128, 19), ((), ()))),
        (
            "(int,ufixed128x19[][])",
            TupleType(
                (
                    BasicType("int"),
                    BasicType("ufixed", (128, 19), ((), ())),
                )
            ),
        ),
        (
            "(int,(address,function))",
            TupleType(
                (
                    BasicType("int"),
                    TupleType(
                        (
                            BasicType("address"),
                            BasicType("function"),
                        )
                    ),
                )
            ),
        ),
        (
            "((address,(fixed,bool)),(uint256[][1][],fixed128x19))",
            TupleType(
                (
                    TupleType(
                        (
                            BasicType("address"),
                            TupleType(
                                (
                                    BasicType("fixed"),
                                    BasicType("bool"),
                                )
                            ),
                        )
                    ),
                    TupleType(
                        (
                            BasicType("uint", 256, ((), (1,), ())),
                            BasicType("fixed", (128, 19)),
                        )
                    ),
                )
            ),
        ),
        ("()", TupleType(tuple())),
        (
            "(int,(),())",
            TupleType((BasicType("int"), TupleType(tuple()), TupleType(tuple()))),
        ),
    ),
)
def test_parsing_with_parsimonious_grammar_and_node_visitor_works(
    type_str, expected_type
):
    assert parse(type_str) == expected_type


@pytest.mark.parametrize(
    "type_str, expected_type",
    (
        ("uint", BasicType("uint", 256)),
        ("uint256[]", BasicType("uint", 256, ((),))),
        ("function", BasicType("bytes", 24)),
        ("fixed", BasicType("fixed", (128, 18))),
        ("ufixed", BasicType("ufixed", (128, 18))),
    ),
)
def test_normalizing_and_parsing_works(type_str, expected_type):
    assert parse(normalize(type_str)) == expected_type


@given(malformed_type_strs, st.none())
@example("int0", 4)
@example("fixed128x0", 9)
@example("ufixed128x0", 10)
@example("int!", 4)
@example("(int, bool)", 6)
@example("(int,bool,)", 11)
@example("(int,(address,uint256[][])", 27)
def test_parsing_invalid_type_str_causes_parse_error(type_str, error_col):
    if error_col is not None:
        pattern = rf"Parse error at .* \(column {error_col}\)"
    else:
        pattern = r"Parse error at .*"

    with pytest.raises(ParseError, match=pattern):
        parse(type_str)


def test_parse_raises_type_error_for_wrong_data_type():
    with pytest.raises(TypeError):
        parse(b"uint256")


@given(type_strs)
def test_end_to_end_parsing_and_collapsing(type_str):
    assert parse(type_str).to_type_str() == type_str


@pytest.mark.parametrize(
    "type_str, pattern",
    (
        ("string1x1", "string type cannot have suffix"),
        ("string33", "string type cannot have suffix"),
        ("bytes1x1", "no suffix or a numerical"),
        ("bytes33", "maximum 32 bytes"),
        ("int", "must have numerical suffix"),
        ("int7", "size out of bounds"),
        ("int257", "size out of bounds"),
        ("int9", "must be multiple of 8"),
        ("uint", "must have numerical suffix"),
        ("uint7", "size out of bounds"),
        ("uint257", "size out of bounds"),
        ("uint9", "must be multiple of 8"),
        ("fixed", "must have suffix of form"),
        ("fixed8", "must have suffix of form"),
        ("fixed7x19", "fixed size out of bounds"),
        ("fixed257x19", "fixed size out of bounds"),
        ("fixed17x19", "must be multiple of 8"),
        ("fixed128x81", "exponent size out of bounds"),
        ("ufixed", "must have suffix of form"),
        ("ufixed8", "must have suffix of form"),
        ("ufixed7x19", "fixed size out of bounds"),
        ("ufixed257x19", "fixed size out of bounds"),
        ("ufixed17x19", "must be multiple of 8"),
        ("ufixed128x81", "exponent size out of bounds"),
        ("hash", "must have numerical suffix"),
        ("hash128x128", "must have numerical suffix"),
        ("address128", "cannot have suffix"),
        ("address128x128", "cannot have suffix"),
        (
            "(int256,(address,(ufixed7x19,fixed)))",
            "For 'ufixed7x19' type at column 19 "
            r"in '\(int256,\(address,\(ufixed7x19,fixed\)\)\)': "
            "fixed size out of bounds",
        ),
        (
            "(int256,(address,(ufixed128x19,fixed)))",
            "For 'fixed' type at column 32 "
            r"in '\(int256,\(address,\(ufixed128x19,fixed\)\)\)': "
            "fixed type must have suffix of form",
        ),
    ),
)
def test_invalid_abi_types(type_str, pattern):
    with pytest.raises(ABITypeError, match=pattern):
        parse(type_str).validate()


@pytest.mark.parametrize(
    "type_str",
    (
        "string",
        "bytes24",
        "int256",
        "uint128",
        "fixed128x19",
        "ufixed256x19",
        "hash256",
        "address",
        "(int256,(address,(ufixed128x19,fixed128x19)))",
    ),
)
def test_valid_abi_types(type_str):
    parse(type_str).validate()


@pytest.mark.parametrize(
    "type_str, normalized",
    tuple(TYPE_ALIASES.items())
    + (
        ("(int,uint,fixed,ufixed)", "(int256,uint256,fixed128x18,ufixed128x18)"),
        ("(function,function,(function,byte))", "(bytes24,bytes24,(bytes24,bytes1))"),
    ),
)
def test_normalize(type_str, normalized):
    assert normalize(type_str) == normalized


@pytest.mark.parametrize(
    "type_str",
    (
        "custom",
        "uint256",
        "bytes32",
        "(uint256,bytes32)",
    ),
)
def test_normalize_without_aliases_returns_type_str(type_str):
    assert normalize(type_str) == type_str


def test_basic_type_item_type_throws_errors():
    bt = parse("int256")

    pattern = "Cannot determine item type for non-array type 'int256'"
    with pytest.raises(ValueError, match=pattern):
        _ = bt.item_type


@pytest.mark.parametrize(
    "type_str",
    (
        "string",
        "bytes",
        "Custom[]",
        "(bool,Custom[])[2]",
        "int[]",
        "int[][2]",
        "((int[][2],bool),int)",
        "(bool,bool)[][2]",
    ),
)
def test_abi_type_dynamic_types(type_str):
    abi_type = parse(type_str)
    assert abi_type.is_dynamic


@pytest.mark.parametrize(
    "type_str",
    (
        "bytes2",
        "Custom",
        "int[2]",
        "int[2][2]",
        "((int[2][2],bool),int)",
        "(bool,bool)[1][2]",
    ),
)
def test_abi_type_static_types(type_str):
    abi_type = parse(type_str)
    assert not abi_type.is_dynamic


@pytest.mark.parametrize(
    "type_str",
    (
        "bytes[][2]",
        "bytes[]",
        "(bool,bool)[][2]",
        "(bool,bool)[]",
    ),
)
def test_abi_type_has_dynamic_arrlist(type_str):
    abi_type = parse(type_str)
    assert abi_type._has_dynamic_arrlist


@pytest.mark.parametrize(
    "type_str",
    (
        "bytes[2][2]",
        "bytes",
        "string",
        "(int[],bool)",
    ),
)
def test_abi_type_lacks_dynamic_arrlist(type_str):
    abi_type = parse(type_str)
    assert not abi_type._has_dynamic_arrlist


@pytest.mark.parametrize(
    "type_str",
    (
        "bytes[2]",
        "Custom[2]",
        "bytes[][]",
        "(int[],bool)[]",
        "(int[],bool)[][2]",
    ),
)
def test_abi_type_is_array(type_str):
    abi_type = parse(type_str)
    assert abi_type.is_array


@pytest.mark.parametrize(
    "type_str",
    (
        "Custom",
        "bytes",
        "bytes2",
        "(int[],bool)",
    ),
)
def test_abi_type_is_not_array(type_str):
    abi_type = parse(type_str)
    assert not abi_type.is_array
