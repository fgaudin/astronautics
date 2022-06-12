from collections import namedtuple
import functools
from graphviz import Digraph

class TrackList(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_stack = []

    def caller(self):
        if self.call_stack:
            return self.call_stack[-1]
        
        return None

    def stack(self, func_name):
        self.call_stack.append(func_name)

    def unstack(self, func_name):
        val = self.call_stack.pop()
        assert val == func_name

    def save(self):
        gra = Digraph(strict=True)

        for dep in self:
            gra.node(dep.called, dep.called)
        
        for dep in self:
            gra.edge(dep.caller, dep.called, contraint='false')

        gra.render('deps.gv', view=True)


    def __str__(self) -> str:
        return "\n".join([f"{d.caller} -> {d.called}" for d in self])


        
track_list = TrackList()
Dep = namedtuple('Dep', 'caller called')

def tracked(func):
    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        caller = track_list.caller()
        called = func.__name__
        track_list.stack(called)
        if caller:
            track_list.append(Dep(caller, called))
        result = func(*args, **kwargs)
        track_list.unstack(called)
        return result

    return wrapper_decorator

def tracked_property(func):
    return property(tracked(func))