import unittest

import pyterato.checks as checks

class CheckTests(unittest.TestCase):

    def test_check_mente(self):
        checks.check_mente.oldwords=5

        oldwords_yes = ['a', 'a', 'a', 'facilmente', 'b', 'b', 'b']
        oldwords_no = ['a', 'a', 'a', 'x', 'b', 'b', 'b']

        assert(len(checks.check_mente('raramente', oldwords_yes)) == 1)
        assert(len(checks.check_mente('raramente', oldwords_no)) == 0)
        assert(len(checks.check_mente('bla', oldwords_yes)) == 0)

    def test_check_repetition(self):
        checks.check_repetition.oldwords=5

        oldwords_yes = ['la', 'la', 'la', 'repetida', 'su', 'su', 'su']
        oldwords_no = ['la', 'la', 'repetid', 'x', 'el', 'repe', 'repetidas']
        assert(len(checks.check_repetition('repetida', oldwords_yes)) == 1)
        assert(len(checks.check_repetition('repetida', oldwords_no)) == 0)
        assert(len(checks.check_repetition('bla', oldwords_yes)) == 0)

    def test_check_contained(self):
        checks.check_contained.oldwords=5

        oldwords_yes = ['la', 'la', 'la', 'repetida', 'su', 'su', 'su']
        oldwords_no = ['la', 'la', 'repetidos', 'x', 'el', 'que', 'repetides']

        assert(len(checks.check_contained('repetidas', oldwords_yes)) == 1)
        assert(len(checks.check_contained('repetidas', oldwords_no)) == 0)
        assert(len(checks.check_contained('bla', oldwords_yes)) == 0)

    def test_check_saywords(self):
        assert(len(checks.check_saywords("rebuznó")) == 1)
        assert(len(checks.check_saywords("dijo")) == 0)

    def test_check_verbs(self):
        pass

    def test_check_expressions(self):
        oldwords_yes = ["el", "veloz", "murcielago", "sacudia", "la", "cabeza"]
        oldwords_no = ["el", "veloz", "murcielago", "sacudia", "el", "cabeza"]

        assert(len(checks.check_expressions('cabeza', oldwords_yes)) == 1)
        assert(len(checks.check_expressions('cabeza', oldwords_no)) == 0)
