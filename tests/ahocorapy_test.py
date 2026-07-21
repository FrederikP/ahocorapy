#!/usr/bin/env python
# -*- coding: utf-8 -*-
from io import open
from pickle import dumps, loads
import sys
import unittest

try:
    text_type = unicode  # Python 2
except NameError:
    text_type = str  # Python 3


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
        tostring = text_type(kwtree)
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
        as_string = text_type(tree._zero_state)
        self.assertIsNotNone(as_string)

    def test_tuples_of_ints(self):
        '''
        Keywords and search input can be any sequence of hashable symbols,
        not just strings. Here we use tuples of integers.
        '''
        kwtree = KeywordTree()
        kwtree.add((1, 2, 3))
        kwtree.add((2, 3, 4))
        kwtree.add((8,))
        kwtree.finalize()

        result = kwtree.search((9, 1, 2, 3, 4, 8))
        self.assertEqual(((1, 2, 3), 1), result)

        result = kwtree.search((5, 6, 7))
        self.assertIsNone(result)

    def test_search_all_tuples_of_ints(self):
        kwtree = KeywordTree()
        kwtree.add((1, 2, 3))
        kwtree.add((2, 3, 4))
        kwtree.add((8,))
        kwtree.finalize()

        results = kwtree.search_all((9, 1, 2, 3, 4, 8))
        self.assertEqual(((1, 2, 3), 1), next(results))
        self.assertEqual(((2, 3, 4), 2), next(results))
        self.assertEqual(((8,), 5), next(results))
        with self.assertRaises(StopIteration):
            next(results)

    def test_bytes(self):
        '''
        Bytes objects work as sequences of symbols, including non-ascii byte
        values. This works on both python 2 and 3, even though the symbol type
        differs between them (see test_bytes_yields_integers_py3 for details).
        '''
        kwtree = KeywordTree()
        kwtree.add(b'abc')
        kwtree.add(b'\xff\x00')
        kwtree.finalize()

        result = kwtree.search(b'xxabc')
        self.assertEqual((b'abc', 2), result)

        result = kwtree.search(b'\x01\xff\x00\x02')
        self.assertEqual((b'\xff\x00', 1), result)

    @unittest.skipIf(sys.version_info[0] < 3,
                     'In python 2 bytes is an alias for str, so iterating a '
                     'bytes object yields 1-char str symbols instead of the '
                     'integers this test relies on.')
    def test_bytes_yields_integers_py3(self):
        '''
        In python 3 iterating over a bytes object yields integers. Because the
        tree only cares about the individual symbols, an integer-based keyword
        matches a bytes input. This is python 3 specific and therefore skipped
        on python 2, where bytes symbols are 1-char strings.
        '''
        kwtree = KeywordTree()
        # keyword built from the integer byte values of b'abc' (97, 98, 99)
        kwtree.add((97, 98, 99))
        kwtree.finalize()

        result = kwtree.search(b'xxabc')
        self.assertEqual(((97, 98, 99), 2), result)

    def test_list_of_tokens(self):
        '''
        Using lists of string tokens enables word-level (rather than
        character-level) matching. Symbols must be hashable; the keyword and
        input sequences themselves need only support iteration and len().
        '''
        kwtree = KeywordTree()
        kwtree.add(['hello', 'world'])
        kwtree.add(['foo', 'bar', 'baz'])
        kwtree.finalize()

        result = kwtree.search(['say', 'hello', 'world', 'now'])
        self.assertEqual((['hello', 'world'], 1), result)

        result = kwtree.search(['helloworld'])
        self.assertIsNone(result)

    def test_pickling_arbitrary_sequence(self):
        kwtree = KeywordTree()
        kwtree.add((1, 2, 3))
        kwtree.add((2, 3, 4))
        kwtree.finalize()

        deserialized = loads(dumps(kwtree))

        results = deserialized.search_all((0, 1, 2, 3, 4))
        self.assertEqual(((1, 2, 3), 1), next(results))
        self.assertEqual(((2, 3, 4), 2), next(results))
        with self.assertRaises(StopIteration):
            next(results)


if __name__ == '__main__':
    unittest.main()
