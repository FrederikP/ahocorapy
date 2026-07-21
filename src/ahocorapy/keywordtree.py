'''
Ahocorasick implementation entirely written in python.
Supports unicode.

Quite optimized, the code may not be as beautiful as you like,
since inlining and so on was necessary

Created on Jan 5, 2016

@author: Frederik Petersen (frederik@the-imperfection.de)
'''

import re

try:
    _TEXT_TYPES = (str, unicode)  # Python 2
except NameError:
    _TEXT_TYPES = (str,)  # Python 3


class State(object):
    __slots__ = ['identifier', 'symbol', 'success', 'transitions', 'parent',
                 'matched_keyword', 'longest_strict_suffix', 'outputs']

    def __init__(self, identifier, symbol=None,  parent=None, success=False):
        self.symbol = symbol
        self.identifier = identifier
        self.transitions = {}
        self.parent = parent
        self.success = success
        self.matched_keyword = None
        self.longest_strict_suffix = None

    def __str__(self):
        transitions_as_string = ','.join(
            ['{0} -> {1}'.format(key, value.identifier) for key, value in self.transitions.items()])
        return "State {0}. Transitions: {1}".format(self.identifier, transitions_as_string)


class KeywordTree(object):

    def __init__(self, case_insensitive=False):
        '''
        @param case_insensitive: If true, case will be ignored when searching.
                                 Setting this to true will have a positive
                                 impact on performance.
                                 Defaults to false.
        @param over_allocation: Determines how big initial transition arrays
                                are and how much space is allocated in addition
                                to what is essential when array needs to be
                                resized. Default value 2 seemed to be sweet
                                spot for memory as well as cpu.
        '''
        self._zero_state = State(0)
        self._counter = 1
        self._finalized = False
        self._case_insensitive = case_insensitive
        self._skip_pattern = None
        self._skip_pattern_type = None

    def add(self, keyword):
        '''
        Add a keyword to the tree.
        Can only be used before finalize() has been called.
        Keyword can be any sequence of hashable symbols (e.g. str, bytes,
        tuple or list). Its symbols must be hashable and the keyword must
        support len(). Note that case_insensitive mode only works with strings.
        '''
        if self._finalized:
            raise ValueError('KeywordTree has been finalized.' +
                             ' No more keyword additions allowed')
        original_keyword = keyword
        if self._case_insensitive:
            keyword = keyword.lower()
        if len(keyword) <= 0:
            return
        current_state = self._zero_state
        for char in keyword:
            try:
                current_state = current_state.transitions[char]
            except KeyError:
                next_state = State(self._counter, parent=current_state,
                                   symbol=char)
                self._counter += 1
                current_state.transitions[char] = next_state
                current_state = next_state
        current_state.success = True
        current_state.matched_keyword = original_keyword

    def search(self, text):
        '''
        Alias for the search_one method
        '''
        return self.search_one(text)

    def search_one(self, text):
        '''
        Search a text for any occurence of any added keyword.
        Returns when one keyword has been found.
        Can only be called after finalized() has been called.
        O(n) with n = len(text)
        @return: 2-Tuple with keyword and startindex in text.
                 Or None if no keyword was found in the text.
        '''
        result_gen = self.search_all(text)
        try:
            return next(result_gen)
        except StopIteration:
            return None

    def search_all(self, text):
        '''
        Search a text for all occurences of the added keywords.
        Can only be called after finalized() has been called.
        O(n) with n = len(text)
        @return: Generator used to iterate over the results.
        '''
        if not self._finalized:
            raise ValueError('KeywordTree has not been finalized.' +
                             ' No search allowed. Call finalize() first.')
        if self._case_insensitive:
            text = text.lower()
        if self._skip_pattern is not None and \
                isinstance(text, self._skip_pattern_type):
            return self._search_all_string(text)
        return self._search_all_generic(text)

    def _search_all_generic(self, text):
        '''
        Search loop for any sequence of hashable symbols.
        The zero state gets special treatment because on texts that
        contain few matches the search spends most symbols idling there.
        '''
        zero_state = self._zero_state
        zero_transitions_get = zero_state.transitions.get
        current_state = zero_state
        for idx, symbol in enumerate(text):
            if current_state is zero_state:
                next_state = zero_transitions_get(symbol)
                if next_state is None:
                    continue
            else:
                next_state = current_state.transitions.get(symbol)
                if next_state is None:
                    next_state = zero_transitions_get(symbol)
                    if next_state is None:
                        current_state = zero_state
                        continue
            current_state = next_state
            outputs = current_state.outputs
            if outputs:
                for keyword, keyword_length in outputs:
                    yield (keyword, idx + 1 - keyword_length)

    def _search_all_string(self, text):
        '''
        Search loop for string input. Stretches of text in which no
        keyword can start are skipped with a precompiled regex character
        class of all keyword start symbols, which scans at C speed.
        '''
        zero_transitions = self._zero_state.transitions
        zero_transitions_get = zero_transitions.get
        pattern_search = self._skip_pattern.search
        text_length = len(text)
        match = pattern_search(text)
        if match is None:
            return
        pos = match.start()
        current_state = zero_transitions[text[pos]]
        while True:
            outputs = current_state.outputs
            if outputs:
                for keyword, keyword_length in outputs:
                    yield (keyword, pos + 1 - keyword_length)
            pos += 1
            if pos >= text_length:
                return
            symbol = text[pos]
            next_state = current_state.transitions.get(symbol)
            if next_state is None:
                next_state = zero_transitions_get(symbol)
                if next_state is None:
                    # No keyword can start at pos. Check the next symbol
                    # inline before paying for a regex call, so that texts
                    # alternating between skippable and non-skippable
                    # symbols don't get slower than the generic loop.
                    pos += 1
                    if pos >= text_length:
                        return
                    next_state = zero_transitions_get(text[pos])
                    if next_state is None:
                        match = pattern_search(text, pos + 1)
                        if match is None:
                            return
                        pos = match.start()
                        next_state = zero_transitions[text[pos]]
            current_state = next_state

    def finalize(self):
        '''
        Needs to be called after all keywords have been added and
        before any searching is performed.
        '''
        if self._finalized:
            raise ValueError('KeywordTree has already been finalized.')
        self._zero_state.longest_strict_suffix = self._zero_state
        self.search_lss_for_children(self._zero_state)
        self._precompute_outputs()
        self._compile_skip_pattern()
        self._finalized = True

    def _precompute_outputs(self):
        '''
        Stores on every state the matches to report when the search
        reaches it: its own keyword plus the keywords of all success
        states on its longest_strict_suffix chain, each paired with the
        keyword's length. This replaces walking the suffix chain for
        every symbol during search.
        '''
        zero_state = self._zero_state
        zero_state.outputs = ()
        processed = set()
        to_process = [zero_state]
        while to_process:
            state = to_process.pop()
            processed.add(state.identifier)
            for child in state.transitions.values():
                if child.identifier not in processed:
                    outputs = []
                    suffix = child
                    while suffix is not zero_state:
                        if suffix.success:
                            keyword = suffix.matched_keyword
                            outputs.append((keyword, len(keyword)))
                        suffix = suffix.longest_strict_suffix
                    child.outputs = tuple(outputs)
                    to_process.append(child)

    def _compile_skip_pattern(self):
        '''
        Compiles a regex character class matching all symbols that a
        keyword can start with. The search loop uses it to skip over
        stretches of text in which no keyword can start. Only possible
        when all these symbols are single characters of the same string
        type, otherwise search falls back to the generic loop.
        '''
        self._skip_pattern = None
        self._skip_pattern_type = None
        symbols = list(self._zero_state.transitions)
        if not symbols:
            return
        symbol_type = type(symbols[0])
        if symbol_type not in _TEXT_TYPES:
            return
        for symbol in symbols:
            if type(symbol) is not symbol_type or len(symbol) != 1:
                return
        character_class = '[' + ''.join(
            [re.escape(symbol) for symbol in symbols]) + ']'
        self._skip_pattern = re.compile(character_class)
        self._skip_pattern_type = symbol_type

    def search_lss_for_children(self, zero_state):
        processed = set()
        to_process = [zero_state]
        while to_process:
            state = to_process.pop()
            processed.add(state.identifier)
            for child in state.transitions.values():
                if child.identifier not in processed:
                    self.search_lss(child)
                    to_process.append(child)

    def search_lss(self, state):
        zero_state = self._zero_state
        parent = state.parent
        traversed = parent.longest_strict_suffix
        while True:
            if state.symbol in traversed.transitions and\
                    traversed.transitions[state.symbol] is not state:
                state.longest_strict_suffix =\
                    traversed.transitions[state.symbol]
                break
            elif traversed is zero_state:
                state.longest_strict_suffix = zero_state
                break
            else:
                traversed = traversed.longest_strict_suffix
        suffix = state.longest_strict_suffix
        if suffix is zero_state:
            return
        if suffix.longest_strict_suffix is None:
            self.search_lss(suffix)
        for symbol, next_state in suffix.transitions.items():
            if symbol not in state.transitions:
                state.transitions[symbol] = next_state

    def __str__(self):
        return "ahocorapy KeywordTree"

    def __getstate__(self):
        state_list = [None] * self._counter
        todo_list = [self._zero_state]
        while todo_list:
            state = todo_list.pop()
            transitions = {key: value.identifier for key,
                           value in state.transitions.items()}
            state_list[state.identifier] = {
                'symbol': state.symbol,
                'success': state.success,
                'parent':  state.parent.identifier if state.parent is not None else None,
                'matched_keyword': state.matched_keyword,
                'longest_strict_suffix': state.longest_strict_suffix.identifier if state.longest_strict_suffix is not None else None,
                'transitions': transitions
            }
            for child in state.transitions.values():
                if len(state_list) <= child.identifier or not state_list[child.identifier]:
                    todo_list.append(child)

        return {
            'case_insensitive': self._case_insensitive,
            'finalized': self._finalized,
            'counter': self._counter,
            'states': state_list
        }

    def __setstate__(self, state):
        self._case_insensitive = state['case_insensitive']
        self._counter = state['counter']
        self._finalized = state['finalized']
        states = [None] * len(state['states'])
        for idx, serialized_state in enumerate(state['states']):
            deserialized_state = State(idx, serialized_state['symbol'])
            deserialized_state.success = serialized_state['success']
            deserialized_state.matched_keyword = serialized_state['matched_keyword']
            states[idx] = deserialized_state
        for idx, serialized_state in enumerate(state['states']):
            deserialized_state = states[idx]
            if serialized_state['longest_strict_suffix'] is not None:
                deserialized_state.longest_strict_suffix = states[
                    serialized_state['longest_strict_suffix']]
            else:
                deserialized_state.longest_strict_suffix = None
            if serialized_state['parent'] is not None:
                deserialized_state.parent = states[serialized_state['parent']]
            else:
                deserialized_state.parent = None
            deserialized_state.transitions = {
                key: states[value] for key, value in serialized_state['transitions'].items()}
        self._zero_state = states[0]
        # outputs and the skip pattern are not part of the serialized
        # format, they are recomputed instead.
        self._skip_pattern = None
        self._skip_pattern_type = None
        if self._finalized:
            self._precompute_outputs()
            self._compile_skip_pattern()
