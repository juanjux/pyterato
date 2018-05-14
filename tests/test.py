import unittest

import pyterato.checks as checks

class CheckTests(unittest.TestCase):

    def test_check_mente(self):
        oldwords_yes = ['a', 'a', 'a', 'facilmente', 'b', 'b', 'b']
        oldwords_no = ['a', 'a', 'a', 'x', 'b', 'b', 'b']

        assert(len(checks.MenteFind.check('raramente', oldwords_yes)) == 1)
        assert(len(checks.MenteFind.check('raramente', oldwords_no)) == 0)
        assert(len(checks.MenteFind.check('bla', oldwords_yes)) == 0)

    def test_check_repetition(self):
        oldwords_yes = ['la', 'la', 'la', 'repetida', 'su', 'su', 'su']
        oldwords_no = ['la', 'la', 'repetid', 'x', 'el', 'repe', 'repetidas']
        assert(len(checks.RepetitionFind.check('repetida', oldwords_yes)) == 1)
        assert(len(checks.RepetitionFind.check('repetida', oldwords_no)) == 0)
        assert(len(checks.RepetitionFind.check('bla', oldwords_yes)) == 0)

    def test_check_contained(self):
        oldwords_yes = ['la', 'la', 'la', 'repetida', 'su', 'su', 'su']
        oldwords_no = ['la', 'la', 'repetidos', 'x', 'el', 'que', 'repetides']

        assert(len(checks.ContainedFind.check('repetidas', oldwords_yes)) == 1)
        assert(len(checks.ContainedFind.check('repetidas', oldwords_no)) == 0)
        assert(len(checks.ContainedFind.check('bla', oldwords_yes)) == 0)

    def test_check_saywords(self):
        assert(len(checks.SayWordsFind.check("rebuznó", [])) == 1)
        assert(len(checks.SayWordsFind.check("dijo", [])) == 0)

    def test_check_verbs(self):
        pass

    def test_check_expressions(self):
        oldwords_yes = ["el", "veloz", "murcielago", "sacudia", "la", "cabeza"]
        oldwords_no = ["el", "veloz", "murcielago", "sacudia", "el", "cabeza"]

        assert(len(checks.MisusedExpressionFind.check('cabeza', oldwords_yes)) == 1)
        assert(len(checks.MisusedExpressionFind.check('cabeza', oldwords_no)) == 0)
