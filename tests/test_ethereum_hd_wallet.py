import unittest

from eth_utils import ValidationError

from safe_cli.ethereum_hd_wallet import get_account_from_words, get_address_from_words


class TestEthereumHdWallet(unittest.TestCase):
    def test_get_account_from_words(self):
        words = (
            "loan satoshi action taste party limit cat elder powder dress link decline"
        )

        expected = [
            (
                "0x9c8a7003407957Adee0e70f3094aDA208FDd4CF1",
                b"\x9e!\xaf\xeaoe\xc5l\xf0\x8c\xde~s\xaa\xb3O\x14\xb0&\x97|N\xf5l\x8a#\x14\xe9\xcc\xd2\x86%",
            ),
            (
                "0x09A512D5ecfF9492Cb0f50AFF853dFD8B4ec3EB1",
                b"\xdd\xb7\xf84\xa2\xea\x03Cd\xce\xcf3i\xcb\xf1\xa7\xe0\xa5\x0b\xc3-\xc0\xc1 D\xe0&!\xbb\xa9\x85\xf9",
            ),
            (
                "0x58A0494D85E36f7DFc7d3BA56681ab6efDEf0A19",
                b"\xf8\xfd*\x95\t\x0e\xff\x9c?\rc\x8f*\xb2x\xe7<\xb5\xaa\xf87\xba\xe8PT\x0b\xcf(\xa42\xc7O",
            ),
            (
                "0xa955FBEFe163C6BeAb64A7E854612639782b797F",
                b"h<\xa0\xdf\xec\xf7\xe9\xfe!!z\xfav\xd1(\xa4;\x03V\x84\xb5\x0fE\x06\x90\x8a\x1a\x01\xd8\x7f\xf8o",
            ),
            (
                "0x38DF5615C090Ca80930986295B9bbFCc36a0Ae7B",
                b"h\xdb-\xc1\xbf\xc3\xf0\x02\xb3\x18\xd7\x81BE~"
                b"\xb6\x1d\xa9\x88@\xfd\x80\x82~\xcf\x1c\x08\x17\x96\x1f\xf0\xed",
            ),
        ]

        for index in range(len(expected)):
            account = get_account_from_words(words, index=index)
            self.assertEqual(account.address, expected[index][0])
            self.assertEqual(account.key, expected[index][1])

    def test_get_account_from_words_exception(self):
        words = "loan satoshi action taste party limit cat elder powder decline"  # Not valid
        with self.assertRaises(ValidationError):
            get_account_from_words(words)

        with self.assertRaises(ValidationError):
            get_account_from_words("")

    def test_get_address_from_words(self):
        words = (
            "loan satoshi action taste party limit cat elder powder dress link decline"
        )

        expected = [
            "0x9c8a7003407957Adee0e70f3094aDA208FDd4CF1",
            "0x09A512D5ecfF9492Cb0f50AFF853dFD8B4ec3EB1",
            "0x58A0494D85E36f7DFc7d3BA56681ab6efDEf0A19",
            "0xa955FBEFe163C6BeAb64A7E854612639782b797F",
            "0x38DF5615C090Ca80930986295B9bbFCc36a0Ae7B",
        ]

        for index in range(len(expected)):
            self.assertEqual(
                get_address_from_words(words, index=index), expected[index]
            )


if __name__ == "__main__":
    unittest.main()
