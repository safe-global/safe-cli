import unittest

from eth_abi import encode as encode_abi
from hexbytes import HexBytes
from web3 import Web3

from safe_cli.tx_builder.exceptions import (
    InvalidContratMethodError,
    SoliditySyntaxError,
    TxBuilderEncodingError,
)
from safe_cli.tx_builder.tx_builder_file_decoder import (
    SafeProposedTx,
    _get_base_field_type,
    convert_to_proposed_transactions,
    encode_contract_method_to_hex_data,
    parse_array_of_values,
    parse_boolean_value,
    parse_input_value,
    parse_int_value,
    parse_string_to_array,
)

from .safe_cli_test_case_mixin import SafeCliTestCaseMixin


class TestTxBuilderFileDecoder(SafeCliTestCaseMixin, unittest.TestCase):
    def test_parse_boolean_value(self):
        self.assertTrue(parse_boolean_value("true"))
        self.assertTrue(parse_boolean_value("  TRUE  "))
        self.assertTrue(parse_boolean_value("1"))
        self.assertTrue(parse_boolean_value(" 1 "))
        self.assertFalse(parse_boolean_value("false"))
        self.assertFalse(parse_boolean_value("  FALSE  "))
        self.assertFalse(parse_boolean_value("0"))
        self.assertFalse(parse_boolean_value(" 0 "))
        with self.assertRaises(SoliditySyntaxError):
            parse_boolean_value("notabool")
        self.assertTrue(parse_boolean_value(True))
        self.assertFalse(parse_boolean_value(False))
        self.assertTrue(parse_boolean_value(1))
        self.assertFalse(parse_boolean_value(0))

    def test_parse_int_value(self):
        self.assertEqual(parse_int_value("123"), 123)
        self.assertEqual(parse_int_value("'789'"), 789)
        self.assertEqual(parse_int_value('" 101112 "'), 101112)
        self.assertEqual(parse_int_value("0x1A"), 26)
        self.assertEqual(parse_int_value("0X1a"), 26)
        self.assertEqual(parse_int_value("  0x123  "), 291)
        with self.assertRaises(SoliditySyntaxError):
            parse_int_value("   ")
        with self.assertRaises(SoliditySyntaxError):
            parse_int_value("0x1G")

    def test_parse_string_to_array(self):
        self.assertEqual(parse_string_to_array("[a,b,c]"), ["a", "b", "c"])
        self.assertEqual(parse_string_to_array("[1,2,3]"), ["1", "2", "3"])
        self.assertEqual(parse_string_to_array("[hello,world]"), ["hello", "world"])
        self.assertEqual(parse_string_to_array("[[a,b],[c,d]]"), ["[a,b]", "[c,d]"])
        self.assertEqual(parse_string_to_array("[ a , b , c ]"), ["a", "b", "c"])
        self.assertEqual(
            parse_string_to_array('["[hello,world]","[foo,bar]"]'),
            ['"[hello,world]"', '"[foo,bar]"'],
        )

    def test_get_base_field_type(self):
        self.assertEqual(_get_base_field_type("uint"), "uint")
        self.assertEqual(_get_base_field_type("int"), "int")
        self.assertEqual(_get_base_field_type("address"), "address")
        self.assertEqual(_get_base_field_type("bool"), "bool")
        self.assertEqual(_get_base_field_type("string"), "string")
        self.assertEqual(_get_base_field_type("uint[]"), "uint")
        self.assertEqual(_get_base_field_type("int[10]"), "int")
        self.assertEqual(_get_base_field_type("address[5][]"), "address")
        self.assertEqual(_get_base_field_type("bool[][]"), "bool")
        self.assertEqual(_get_base_field_type("string[3][4]"), "string")
        self.assertEqual(_get_base_field_type("uint256"), "uint256")
        self.assertEqual(_get_base_field_type("myCustomType[10][]"), "myCustomType")
        with self.assertRaises(SoliditySyntaxError):
            _get_base_field_type("[int]")
        with self.assertRaises(SoliditySyntaxError):
            _get_base_field_type("")

    def test_parse_array_of_values(self):
        self.assertEqual(parse_array_of_values("[1,2,3]", "uint[]"), [1, 2, 3])
        self.assertEqual(
            parse_array_of_values("[true,false,true]", "bool[]"), [True, False, True]
        )
        self.assertEqual(
            parse_array_of_values('["hello","world"]', "string[]"),
            ['"hello"', '"world"'],
        )
        self.assertEqual(
            parse_array_of_values("[hello,world]", "string[]"), ["hello", "world"]
        )
        self.assertEqual(
            parse_array_of_values("[[1,2],[3,4]]", "uint[][]"), [[1, 2], [3, 4]]
        )
        self.assertEqual(
            parse_array_of_values("[[true,false],[false,true]]", "bool[][]"),
            [[True, False], [False, True]],
        )
        self.assertEqual(
            parse_array_of_values('[["hello","world"],["foo","bar"]]', "string[][]"),
            [['"hello"', '"world"'], ['"foo"', '"bar"']],
        )
        self.assertEqual(
            parse_array_of_values("[0x123, 0x456]", "address[]"), ["0x123", "0x456"]
        )
        self.assertEqual(
            parse_array_of_values("[[0x123], [0x456]]", "address[][]"),
            [["0x123"], ["0x456"]],
        )
        with self.assertRaises(SoliditySyntaxError):
            parse_array_of_values("1,2,3", "uint[]")

    def test_parse_input_value(self):
        self.assertEqual(parse_input_value("tuple", "[1,2,3]"), (1, 2, 3))
        self.assertEqual(
            parse_input_value("string[]", '["a", "b", "c"]'), ["a", "b", "c"]
        )
        self.assertEqual(parse_input_value("uint[]", "[1, 2, 3]"), [1, 2, 3])
        self.assertEqual(
            parse_input_value("uint[2][2]", "[[1, 2], [3, 4]]"), [[1, 2], [3, 4]]
        )
        self.assertTrue(parse_input_value("bool", "true"))
        self.assertEqual(parse_input_value("int", "123"), 123)
        self.assertEqual(parse_input_value("bytes", "0x1234"), HexBytes("0x1234"))

    def test_encode_contract_method_to_hex_data(self):
        contract_method = {
            "name": "transfer",
            "inputs": [
                {"name": "to", "type": "address"},
                {"name": "value", "type": "uint256"},
            ],
        }
        contract_fields_values = {
            "to": "0x21C98F24ACC673b9e1Ad2C4191324701576CC2E5",
            "value": "1000",
        }
        expected_hex = HexBytes(
            Web3.keccak(text="transfer(address,uint256)")[:4]
            + encode_abi(
                ["address", "uint256"],
                ["0x21C98F24ACC673b9e1Ad2C4191324701576CC2E5", 1000],
            )
        )
        self.assertEqual(
            encode_contract_method_to_hex_data(contract_method, contract_fields_values),
            expected_hex,
        )

        # Test tuple type
        contract_method = {
            "name": "transfer",
            "inputs": [
                {"name": "to", "type": "address"},
                {
                    "components": [
                        {"name": "name", "type": "string"},
                        {"name": "age", "type": "uint8"},
                        {"name": "userAddress", "type": "address"},
                        {"name": "isNice", "type": "bool"},
                    ],
                    "name": "contractOwnerNewValue",
                    "type": "tuple",
                },
            ],
        }
        contract_fields_values = {
            "to": "0x21C98F24ACC673b9e1Ad2C4191324701576CC2E5",
            "contractOwnerNewValue": '["hola",12,"0x21C98F24ACC673b9e1Ad2C4191324701576CC2E5",true]',
        }
        expected_hex = HexBytes(
            Web3.keccak(text="transfer(address,(string,uint8,address,bool))")[:4]
            + encode_abi(
                ["address", "(string,uint8,address,bool)"],
                [
                    "0x21C98F24ACC673b9e1Ad2C4191324701576CC2E5",
                    ("hola", 12, "0x21C98F24ACC673b9e1Ad2C4191324701576CC2E5", True),
                ],
            )
        )
        self.assertEqual(
            encode_contract_method_to_hex_data(contract_method, contract_fields_values),
            expected_hex,
        )

        # Test invalid contrat method
        contract_method = {"name": "receive", "inputs": []}
        contract_fields_values = {}
        with self.assertRaises(InvalidContratMethodError):
            encode_contract_method_to_hex_data(contract_method, contract_fields_values)

        # Test invalid value
        contract_method = {
            "name": "transfer",
            "inputs": [
                {"name": "to", "type": "address"},
                {"name": "value", "type": "uint256"},
            ],
        }
        contract_fields_values = {"to": "0xRecipientAddress", "value": "invalidValue"}
        with self.assertRaises(TxBuilderEncodingError):
            encode_contract_method_to_hex_data(contract_method, contract_fields_values)

    def test_safe_proposed_tx_str(self):
        tx = SafeProposedTx(id=1, to="0xRecipientAddress", value=1000, data="0x1234")
        self.assertEqual(str(tx), "id=1 to=0xRecipientAddress value=1000 data=0x1234")

    def test_convert_to_proposed_transactions(self):
        batch_file = {
            "transactions": [
                {
                    "to": "0x21C98F24ACC673b9e1Ad2C4191324701576CC2E5",
                    "value": 1000,
                    "data": "0x1234",
                },
                {
                    "to": "0x21C98F24ACC673b9e1Ad2C4191324701576CC2E5",
                    "value": 2000,
                    "contractMethod": {
                        "name": "transfer",
                        "inputs": [
                            {"name": "to", "type": "address"},
                            {"name": "value", "type": "uint256"},
                        ],
                    },
                    "contractInputsValues": {
                        "to": "0x21C98F24ACC673b9e1Ad2C4191324701576CC2E5",
                        "value": "1000",
                    },
                },
            ]
        }
        expected = [
            SafeProposedTx(
                id=0,
                to="0x21C98F24ACC673b9e1Ad2C4191324701576CC2E5",
                value=1000,
                data="0x1234",
            ),
            SafeProposedTx(
                id=1,
                to="0x21C98F24ACC673b9e1Ad2C4191324701576CC2E5",
                value=2000,
                data="0xa9059cbb00000000000000000000000021c98f24acc673b9e1ad2c4191324701576cc2e500000000000000000000000000000000000000000000000000000000000003e8",
            ),
        ]
        result = convert_to_proposed_transactions(batch_file)
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
