import pygraphviz as pgv

try:
    text_type = unicode  # Python 2
except NameError:
    text_type = str  # Python 3


class Visualizer(object):

    def __init__(self):
        self._added = set()


    def _add_state_and_children(self, kwtree, graph, state, added_state_ids):
        if state.identifier in added_state_ids:
            return
        if state.success:
            current_state = state
            results = []
            while current_state != kwtree._zero_state and current_state.success:
                keyword = current_state.matched_keyword
                if keyword:
                    results.append(keyword)
                current_state = current_state.longest_strict_suffix
            graph.add_node(
                    state.identifier,
                    color='green',
                    label=text_type(state.identifier) + ' [' +
                    ','.join(results) + ']')
        else:
            graph.add_node(state.identifier)
        added_state_ids.add(state.identifier)
        for symbol, child in state.transitions.items():
            self._add_state_and_children(kwtree, graph, child, added_state_ids)
            graph.add_edge(state.identifier, child.identifier, label=symbol)
    
    
    def draw(self, filename, kwtree):
        graph = pgv.AGraph(directed=True)
        added_state_ids = set()
        self._add_state_and_children(kwtree, graph, kwtree._zero_state, added_state_ids)
        graph.draw(filename, prog='dot')
