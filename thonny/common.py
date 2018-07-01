# -*- coding: utf-8 -*-
 
"""
Classes used both by front-end and back-end
"""
import os.path
import shlex

class Record:
    def __init__(self, **kw):
        self.__dict__.update(kw)
    
    def update(self, **kw):
        self.__dict__.update(kw)
    
    def setdefault(self, **kw):
        "updates those fields that are not yet present (similar to dict.setdefault)"
        for key in kw:
            if not hasattr(self, key):
                setattr(self, key, kw[key])
    
    def __repr__(self):
        keys = self.__dict__.keys()
        items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
        return "{}({})".format(self.__class__.__name__, ", ".join(items))
    
    def __str__(self):
        keys = sorted(self.__dict__.keys())
        items = ("{}={!r}".format(k, str(self.__dict__[k])) for k in keys)
        return "{}({})".format(self.__class__.__name__, ", ".join(items))
    
    def __eq__(self, other):
        if type(self) != type(other):
            return False
        
        if len(self.__dict__) != len(other.__dict__):
            return False 
        
        for key in self.__dict__:
            if not hasattr(other, key):
                return False
            self_value = getattr(self, key)
            other_value = getattr(other, key)
            
            if type(self_value) != type(other_value) or self_value != other_value:
                return False
        
        return True

    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __hash__(self):
        return hash(repr(self))


class TextRange(Record):
    def __init__(self, lineno, col_offset, end_lineno, end_col_offset):
        self.lineno = lineno
        self.col_offset = col_offset
        self.end_lineno = end_lineno
        self.end_col_offset = end_col_offset
    
    def contains_smaller(self, other):
        this_start = (self.lineno, self.col_offset)
        this_end = (self.end_lineno, self.end_col_offset)
        other_start = (other.lineno, other.col_offset)
        other_end = (other.end_lineno, other.end_col_offset)
        
        return (this_start < other_start and this_end > other_end
                or this_start == other_start and this_end > other_end
                or this_start < other_start and this_end == other_end)
    
    def contains_smaller_eq(self, other):
        return self.contains_smaller(other) or self == other
    
    def not_smaller_in(self, other):
        return not other.contains_smaller(self)

    def is_smaller_in(self, other):
        return other.contains_smaller(self)
    
    def not_smaller_eq_in(self, other):
        return not other.contains_smaller_eq(self)

    def is_smaller_eq_in(self, other):
        return other.contains_smaller_eq(self)
    
    def get_start_index(self):
        return str(self.lineno) + "." + str(self.col_offset)
    
    def get_end_index(self):
        return str(self.end_lineno) + "." + str(self.end_col_offset)
    
    def __str__(self):
        return "TR(" + str(self.lineno) + "." + str(self.col_offset) + ", " \
                     + str(self.end_lineno) + "." + str(self.end_col_offset) + ")"
    
    
                 
class FrameInfo(Record):
    def get_description(self):
        return (
            "[" + str(self.id) + "] "
            + self.code_name + " in " + self.filename
            + ", focus=" + str(self.focus)
        )

class Command(Record):
    pass

class ToplevelCommand(Command):
    pass

class DebuggerCommand(Command):
    def __init__(self, command, **kw):
        Record.__init__(self, **kw)
        self.command = command

class InputSubmission(Command):
    pass

class InlineCommand(Command):
    """
    Can be used both during debugging and between debugging.
    Initially meant for sending variable and heap info requests
    """
    def __init__(self, command, **kw):
        Record.__init__(self, **kw)
        self.command = command


class UserCommandError(Exception):
    pass

def construct_cmd_line(parts):
    return " ".join(map(shlex.quote, parts))

def parse_cmd_line(s):
    return shlex.split(s, posix=True)

def serialize_message(msg):
    # I want to transfer only ASCII chars because 
    # encodings are not reliable 
    # (eg. can't find a way to specify PYTHONIOENCODING for cx_freeze'd program) 
    return repr(msg).encode("UTF-7").decode("ASCII") 

def parse_message(msg_string):
    # DataFrames may have nan 
    nan = float("nan")  # @UnusedVariable
    return eval(msg_string.encode("ASCII").decode("UTF-7"))



def quote_path_for_shell(path):
    for c in path:
        if (not c.isalpha() 
            and not c.isnumeric()
            and c not in "-_./\\"):
            return '"' + path.replace('"', '\\"') + '"'
    else:
        return path


def print_structure(o):
    print(o.__class__.__name__)
    for attr in dir(o):
        print(attr, "=", getattr(o, attr))

def actual_path(name: str) -> str:
    """In Windows return the path with the case it is stored in the filesystem"""
    assert os.path.isabs(name)
    
    if os.name == "nt":
        name = os.path.realpath(name)
        from ctypes import create_unicode_buffer, windll

        buf = create_unicode_buffer(512)
        windll.kernel32.GetLongPathNameW(name, buf, 512)  # @UndefinedVariable
        assert len(buf.value) >= 2
        
        result = buf.value
        assert isinstance(result, str) 
        
        if result[1] == ":":
            # ensure drive letter is capital
            return result[0].upper() + result[1:]
        else:
            return result
    else:
        return os.path.realpath(name)

def is_same_path(name1, name2):
    return os.path.realpath(os.path.normcase(name1)) == os.path.realpath(os.path.normcase(name2))

def path_startswith(child_name, dir_name):
    normchild = os.path.realpath(os.path.normcase(child_name))
    normdir = os.path.realpath(os.path.normcase(dir_name))
    return normdir == normchild or normchild.startswith(normdir.rstrip(os.path.sep) + os.path.sep)
    

class UserError(RuntimeError):
    pass

if __name__ == "__main__":
    print(repr(actual_path("c:\\users/aivar/DesKTOp")))
