#!/usr/bin/env python
# -*- coding: utf-8 -*-
from builtins import str
from io import open
from pickle import dumps, loads
import unittest


from ahocorapy.keywordtree import KeywordTree


class TestAhocorapy(unittest.TestCase):

    def test_empty_tree(self):
        kwtree = KeywordTree()
        kwtree.finalize()

        result = kwtree.search('zef')
        self.assertIsNone(result)

    def test_empty_input(self):
        kwtree = KeywordTree()
        kwtree.add('bla')
        kwtree.finalize()

        result = kwtree.search('')
        self.assertIsNone(result)

    def test_empty_keyword(self):
        kwtree = KeywordTree()
        kwtree.add('')
        kwtree.finalize()

        result = kwtree.search('')
        self.assertIsNone(result)

    def test_readme_example(self):
        '''
        As used in the projects README. If you have to change this test case,
        please update the README accordingly.
        '''
        kwtree = KeywordTree(case_insensitive=True)
        kwtree.add('malaga')
        kwtree.add('lacrosse')
        kwtree.add('mallorca')
        kwtree.add('mallorca bella')
        kwtree.add('orca')
        kwtree.finalize()

        result = kwtree.search('My favorite islands are malaga and sylt.')
        self.assertEqual(('malaga', 24), result)

        result = kwtree.search(
            'idontlikewhitespaceswhereismalacrossequestionmark')
        self.assertEqual(('lacrosse', 29), result)

        results = kwtree.search_all('malheur on mallorca bellacrosse')
        self.assertIsNotNone(results)
        self.assertEqual(('mallorca', 11), next(results))
        self.assertEqual(('orca', 15), next(results))
        self.assertEqual(('mallorca bella', 11), next(results))
        self.assertEqual(('lacrosse', 23), next(results))
        with self.assertRaises(StopIteration):
            next(results)

    def test_suffix_stuff(self):
        kwtree = KeywordTree()
        kwtree.add('blaaaaaf')
        kwtree.add('bluez')
        kwtree.add('aaaamen')
        kwtree.add('uebergaaat')
        kwtree.finalize()

        result = kwtree.search('blaaaaamentada')
        self.assertEqual(('aaaamen', 3), result)

        result = kwtree.search('clueuebergaaameblaaaamenbluez')
        self.assertEqual(('aaaamen', 17), result)

    def test_text_end_situation(self):
        kwtree = KeywordTree()
        kwtree.add('blaaaaaf')
        kwtree.add('a')
        kwtree.finalize()

        result = kwtree.search_one('bla')
        self.assertEqual(('a', 2), result)

    def test_text_end_situation_2(self):
        kwtree = KeywordTree()
        kwtree.add('blaaaaaf')
        kwtree.add('la')
        kwtree.finalize()

        result = kwtree.search('bla')
        self.assertEqual(('la', 1), result)

    def test_simple(self):
        kwtree = KeywordTree()
        kwtree.add('bla')
        kwtree.add('blue')
        kwtree.finalize()

        result = kwtree.search('bl')
        self.assertIsNone(result)

        result = kwtree.search('')
        self.assertIsNone(result)

        result = kwtree.search('zef')
        self.assertIsNone(result)

        result = kwtree.search('blaaaa')
        self.assertEqual(('bla', 0), result)

        result = kwtree.search('red green blue grey')
        self.assertEqual(('blue', 10), result)

    def test_simple_back_to_zero_state_example(self):
        kwtree = KeywordTree()
        keyword_list = ['ab', 'bca']
        for keyword in keyword_list:
            kwtree.add(keyword)
        kwtree.finalize()

        result = kwtree.search('blbabca')
        self.assertEqual(('ab', 3), result)

    def test_domains(self):
        kwtree = KeywordTree()
        kwtree.add('searchenginemarketingfordummies.com')
        kwtree.add('linkpt.com')
        kwtree.add('fnbpeterstown.com')
        kwtree.finalize()

        result = kwtree.search('peterchen@linkpt.com')
        self.assertEqual(('linkpt.com', 10), result)

    def test_unicode(self):
        kwtree = KeywordTree()
        kwtree.add('bla')
        kwtree.add('blue')
        kwtree.add(u'颜到')
        kwtree.finalize()

        result = kwtree.search(u'春华变苍颜到处群魔乱')
        self.assertEqual((u'颜到', 4), result)

        result = kwtree.search(u'三年过')
        self.assertIsNone(result)

    def test_case_sensitivity(self):
        kwtree = KeywordTree()
        kwtree.add('bla')
        kwtree.add('blue')
        kwtree.add('blISs')
        kwtree.finalize()

        result = kwtree.search('bLa')
        self.assertIsNone(result)

        result = kwtree.search('BLISS')
        self.assertIsNone(result)

        result = kwtree.search('bliss')
        self.assertIsNone(result)

        result = kwtree.search('blISs')
        self.assertEqual(('blISs', 0), result)

    def test_case_insensitivity_mode(self):
        kwtree = KeywordTree(case_insensitive=True)
        kwtree.add('bla')
        kwtree.add('blue')
        kwtree.add('blISs')
        kwtree.finalize()

        result = kwtree.search('bLa')
        self.assertEqual(('bla', 0), result)

        result = kwtree.search('BLISS')
        self.assertEqual(('blISs', 0), result)

    def test_utility_calls(self):
        kwtree = KeywordTree(case_insensitive=True)
        kwtree.add('bla')
        kwtree.add('blue')
        kwtree.finalize()
        # Just test that there are no errors
        rep = repr(kwtree)
        self.assertGreater(len(rep), 0)
        tostring = str(kwtree)
        self.assertGreater(len(tostring), 0)

    def test_finalize_errors(self):
        kwtree = KeywordTree(case_insensitive=True)
        kwtree.add('bla')
        kwtree.add('blue')

        self.assertRaises(ValueError, kwtree.search, 'blueb')

        kwtree = KeywordTree(case_insensitive=True)
        kwtree.add('bla')
        kwtree.finalize()

        self.assertRaises(ValueError, kwtree.add, 'blueb')

        kwtree = KeywordTree(case_insensitive=True)
        kwtree.add('bla')
        kwtree.finalize()

        self.assertRaises(ValueError, kwtree.finalize)

    def test_many_keywords(self):
        kwtree = KeywordTree(case_insensitive=True)
        with open('tests/data/names.txt') as keyword_file:
            keyword_list = [line.strip() for line in keyword_file.readlines()]

        for kw in keyword_list:
            kwtree.add(kw)

        kwtree.finalize()
        with open('tests/data/textblob.txt') as keyword_file:
            textblob = keyword_file.read()

        result = kwtree.search(textblob)
        self.assertEqual(('Dawn Higgins', 34153), result)

        results = kwtree.search_all(textblob)
        self.assertIsNotNone(results)
        self.assertEqual(('Dawn Higgins', 34153), next(results))
        with self.assertRaises(StopIteration):
            next(results)

    def test_search_all_issue_1(self):
        text = '/foo/bar'
        words = ['/bar', '/foo/bar', 'bar']
        tree = KeywordTree(case_insensitive=True)
        for word in words:
            tree.add(word)
        tree.finalize()

        results = tree.search_all(text)

        self.assertEqual(('/foo/bar', 0), next(results))
        self.assertEqual(('/bar', 4), next(results))
        self.assertEqual(('bar', 5), next(results))

    def test_search_all_issue_1_similar(self):
        text = '/foo/bar'
        words = ['/bara', '/foo/barb', 'bar']
        tree = KeywordTree(case_insensitive=True)
        for word in words:
            tree.add(word)
        tree.finalize()

        results = tree.search_all(text)

        self.assertEqual(('bar', 5), next(results))

    def test_search_all_issue_3_similar(self):
        text = '/foo/bar'
        words = ['foo/', 'foo', '/foo/', '/bar']
        tree = KeywordTree(case_insensitive=True)
        for word in words:
            tree.add(word)
        tree.finalize()

        results = tree.search_all(text)

        self.assertEqual(('foo', 1), next(results))
        self.assertEqual(('/foo/', 0), next(results))
        self.assertEqual(('foo/', 1), next(results))
        self.assertEqual(('/bar', 4), next(results))

    def test_pickling_simple(self):
        words = ['peter', 'horst', 'gandalf', 'frodo']
        tree = KeywordTree(case_insensitive=True)
        for word in words:
            tree.add(word)
        tree.finalize()
        as_bytes = dumps(tree)

        self.assertIsNotNone(as_bytes)

        deserialized = loads(as_bytes)

        self.assertIsNotNone(deserialized)

        text = 'Gollum did not like frodo. But gandalf did.'

        results = deserialized.search_all(text)

        self.assertEqual(('frodo', 20), next(results))
        self.assertEqual(('gandalf', 31), next(results))

    def test_pickling_before_finalizing(self):
        words = ['peter', 'horst', 'gandalf', 'frodo']
        tree = KeywordTree(case_insensitive=True)
        for word in words:
            tree.add(word)
        as_bytes = dumps(tree)

        self.assertIsNotNone(as_bytes)

        deserialized = loads(as_bytes)

        self.assertIsNotNone(deserialized)

        deserialized.finalize()

        text = 'Gollum did not like frodo. But gandalf did.'

        results = deserialized.search_all(text)

        self.assertEqual(('frodo', 20), next(results))
        self.assertEqual(('gandalf', 31), next(results))

    def test_state_to_string(self):
        words = ['peter', 'horst', 'gandalf', 'frodo']
        tree = KeywordTree(case_insensitive=True)
        for word in words:
            tree.add(word)
        tree.finalize()
        as_string = str(tree._zero_state)
        self.assertIsNotNone(as_string)


if __name__ == '__main__':
    unittest.main()
