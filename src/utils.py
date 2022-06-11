from collections import namedtuple
import functools
import inspect
from graphviz import Digraph

class TrackList(list):
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

def track(func):
    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        caller = inspect.stack()[1].function
        if caller == '<module>':
            caller = 'start'
        called = func.__name__
        track_list.append(Dep(caller, called))
        return func(*args, **kwargs)

    return wrapper_decorator