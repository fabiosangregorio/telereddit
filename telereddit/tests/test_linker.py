import unittest
from unittest.mock import patch
from parameterized import parameterized, param

from telereddit.linker import Linker


class TestLinker(unittest.TestCase):
    Linker.set_bot(None)
    linker = Linker(0)

    def test_get_args(self):
        args = self.linker.get_args()
        self.assertIn("chat_id", args)
        self.assertTrue(args["chat_id"] == 0)

    def test_get_args_override(self):
        self.assertIn("test", self.linker.get_args({"test": True}))
