import dataclasses
import json
import re
from typing import Any, Dict, List

from eth_abi import encode as encode_abi
from hexbytes import HexBytes
from web3 import Web3

from safe_cli.tx_builder.exceptions import (
    InvalidContratMethodError,
    SoliditySyntaxError,
    TxBuilderEncodingError,
)

NON_VALID_CONTRACT_METHODS = ["receive", "fallback"]


def encode_contract_method_to_hex_data(
    contract_method, contract_fields_values
) -> HexBytes:
    contract_method_name = contract_method.get("name") if contract_method else None
    contract_fields = contract_method.get("inputs", []) if contract_method else []

    is_valid_contract_method = (
        contract_method_name and contract_method_name not in NON_VALID_CONTRACT_METHODS
    )

    if is_valid_contract_method:
        try:
            method_types = [field["type"] for field in contract_fields]
            encoding_types = parse_type_values(contract_fields)
            values = [
                parse_input_value(
                    field["type"], contract_fields_values.get(field["name"], "")
                )
                for field in contract_fields
            ]

            function_signature = f"{contract_method_name}({','.join(method_types)})"
            function_selector = Web3.keccak(text=function_signature)[:4]
            encoded_parameters = encode_abi(encoding_types, values)
            hex_encoded_data = HexBytes(function_selector + encoded_parameters)
            return hex_encoded_data
        except Exception as error:
            raise TxBuilderEncodingError(
                "Error encoding current form values to hex data:", error
            )
    else:
        raise InvalidContratMethodError(
            f"Invalid contract method {contract_method_name}"
        )


def parse_boolean_value(value) -> bool:
    if isinstance(value, str):
        if value.strip().lower() in ["true", "1"]:
            return True

        if value.strip().lower() in ["false", "0"]:
            return False

        raise SoliditySyntaxError("Invalid Boolean value")

    return bool(value)


def parse_int_value(value) -> int:
    trimmed_value = value.replace('"', "").replace("'", "").strip()

    if trimmed_value == "":
        raise SoliditySyntaxError("Invalid empty strings for integers")

    if not trimmed_value.isdigit() and bool(
        re.fullmatch(r"0[xX][0-9a-fA-F]+|[0-9a-fA-F]+$", trimmed_value)
    ):
        return int(trimmed_value, 16)

    return int(trimmed_value)


def parse_string_to_array(value) -> List[Any]:
    number_of_items = 0
    number_of_other_arrays = 0
    result = []
    value = value.strip()[1:-1]  # remove the first "[" and the last "]"

    for char in value:
        if char == "," and number_of_other_arrays == 0:
            number_of_items += 1
            continue

        if char == "[":
            number_of_other_arrays += 1
        elif char == "]":
            number_of_other_arrays -= 1

        if len(result) <= number_of_items:
            result.append("")

        result[number_of_items] += char.strip()

    return result


def get_base_field_type(field_type) -> str:
    base_field_type_regex = re.compile(
        r"^([a-zA-Z0-9]*)(((\[\])|(\[[1-9]+[0-9]*\]))*)?$"
    )
    match = base_field_type_regex.match(field_type)
    base_field_type = match.group(1)

    if not base_field_type:
        raise SoliditySyntaxError(
            f"Unknown base field type {base_field_type} from {field_type}"
        )

    return base_field_type


def is_array(values) -> bool:
    trimmed_value = values.strip()

    return trimmed_value.startswith("[") and trimmed_value.endswith("]")


def parse_array_of_values(values, field_type) -> List[Any]:
    if not is_array(values):
        raise SoliditySyntaxError("Invalid Array value")

    parsed_values = parse_string_to_array(values)
    return [
        (
            parse_array_of_values(item_value, field_type)
            if is_array(item_value)
            else parse_input_value(get_base_field_type(field_type), item_value)
        )
        for item_value in parsed_values
    ]


def is_boolean_field_type(field_type) -> bool:
    return field_type == "bool"


def is_int_field_type(field_type) -> bool:
    return field_type.startswith("uint") or field_type.startswith("int")


def is_tuple_field_type(field_type) -> bool:
    return field_type.startswith("tuple")


def is_bytes_field_type(field_type) -> bool:
    return field_type.startswith("bytes")


def is_array_of_strings_field_type(field_type) -> bool:
    return field_type.startswith("string[")


def is_array_field_type(field_type) -> bool:
    pattern = re.compile(r"\[\d*\]$")
    return bool(pattern.search(field_type))


def is_multi_dimensional_array_field_type(field_type) -> bool:
    return field_type.count("[") > 1


def parse_type_values(contract_fields: List[Dict[str, Any]]) -> List[Any]:
    types = []

    for field in contract_fields:
        if is_tuple_field_type(field["type"]):
            component_types = ",".join(
                component["type"] for component in field["components"]
            )
            types.append(f"({component_types})")
        else:
            types.append(field["type"])

    return types


def parse_input_value(field_type, value) -> Any:
    trimmed_value = value.strip() if isinstance(value, str) else value

    if is_tuple_field_type(field_type):
        return tuple(json.loads(trimmed_value))

    if is_array_of_strings_field_type(field_type):
        return json.loads(trimmed_value)

    if is_array_field_type(field_type) or is_multi_dimensional_array_field_type(
        field_type
    ):
        return parse_array_of_values(trimmed_value, field_type)

    if is_boolean_field_type(field_type):
        return parse_boolean_value(trimmed_value)

    if is_int_field_type(field_type):
        return parse_int_value(trimmed_value)

    if is_bytes_field_type(field_type):
        return HexBytes(trimmed_value)

    return trimmed_value


@dataclasses.dataclass
class SafeProposedTx:
    id: int
    to: str
    value: int
    data: str

    def __str__(self):
        return f"id={self.id} to={self.to} value={self.value} data={self.data.hex()}"


def convert_to_proposed_transactions(
    batch_file: Dict[str, Any]
) -> List[SafeProposedTx]:
    proposed_transactions = []
    for index, transaction in enumerate(batch_file["transactions"]):
        proposed_transactions.append(
            SafeProposedTx(
                id=index,
                to=transaction.get("to"),
                value=transaction.get("value"),
                data=transaction.get("data")
                or encode_contract_method_to_hex_data(
                    transaction.get("contractMethod"),
                    transaction.get("contractInputsValues"),
                ).hex()
                or "0x",
            )
        )
    return proposed_transactions
