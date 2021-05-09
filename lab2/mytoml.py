import inspect
import types
import sys
import dis
import builtins
#from math import *
import math
from collections import deque

class mytoml:
    def __init__(self):
        self.builtin_fnames = [el[0] for el in inspect.getmembers(builtins, inspect.isbuiltin)]
        self.builtin_cnames = [el[0] for el in inspect.getmembers(builtins, inspect.isclass)]
        self.serialization_q = deque()
        self.placeholders_q = deque()
        self.ph_iter = self.generate_placeholder()

    def generate_placeholder(self):
        i = 0
        while True:
            yield f"<placeholder {i}>"
            i += 1

    def expand_list(self, lst):
        # this can be either of list, tuple, set or frozenset,
        # so we add an element at the very beginning which will
        # indictate what it actually is
        tmplst = list()
        if isinstance(lst, list):
            tmplst.append("list")
        elif isinstance(lst, tuple):
            tmplst.append("tuple")
        elif isinstance(lst, set):
            tmplst.append("set")
        elif isinstance(lst, frozenset):
            tmplst.append("frozenset")
        else:
            raise ValueError(f"Cannot dump toml array from {lst}.")
        tmplst.extend(list(lst))

        for i in range(len(tmplist)):
            if isinstance(tmplst[i], dict):
                ph = next(self.ph_iter)
                self.placeholders_q.append( (ph, tmplist[i]) )
                tmplst[i] = ph
        return tmplst

    def generate_key(self, *args):
        res = ""
        for el in args:
            if not isinstance(el, str):
                raise ValueError("Arguments of key generator must be strings!")
            if not ("." in el or " " in el):
                res += el + "."
            else:
                res += f"\"{el}\"."
        res = res[:-1] # getting rid of last dot
        return res

    def split_key(self, full_key):
        if not isinstance(full_key, str):
            raise ValueError(f"Key must be a string! Actual type:{type(full_key)}")
        
        key_seq, key_list = [], []
        dot_just_encountered = False
        complex_key_encountered = False
        ind = 0
        while ind < len(full_key):
            if dot_just_encountered:
                if key_list:
                    res = "".join(key_list).strip()
                    if not res or " " in res:
                        if not complex_key_encountered:
                            raise ValueError(f"No spaces allowed in a bare key! Key: {res}")
                    key_seq.append(res)
                else:
                    raise ValueError("Empty key encountered!")
                if full_key[ind] == '.':
                    raise ValueError(f"Double dots encountered! Key: {full_key}")
                dot_just_encountered = False
                complex_key_encountered = False
                key_list = []
                ind -= 1
            else:
                if full_key[ind] == '.':
                    dot_just_encountered = True
                elif full_key[ind] == '"':
                    if complex_key_encountered:
                        raise ValueError("Double complex key encountered!")
                    key, ind = self.parse_tstring(full_key, ind)
                    ind -= 1
                    complex_key_encountered = True
                    key_list.append(key)
                elif full_key[ind] != " " and complex_key_encountered:
                    raise ValueError("Invalid key encountered!")
                else:
                    key_list.append(full_key[ind])
            ind += 1

        if dot_just_encountered:
            raise ValueError("Dot at the end detected!")

        if key_list:
            res = "".join(key_list).strip()
            if not res:
                raise ValueError("Empty key encountered!")
            if not complex_key_encountered and " " in res:
                raise ValueError(f"No spaces allowed in a bare key! Key: {res}")
            key_seq.append(res)

        return key_seq
            

    def set_val(self, dct, full_key, val):
        key_seq = self.split_key(full_key)
        curr_dct_lvl = dct
        for key in key_seq[:-1]:
            try:
                curr_dct_lvl = curr_dct_lvl[key]
            except KeyError:
                curr_dct_lvl[key] = dict()
                curr_dct_lvl = curr_dct_lvl[key]
        key = key_seq[-1] 
        curr_dct_lvl[key] = val
        print(curr_dct_lvl)
        print(dct)

    def cls_to_dict(self, clsobj):
        bases = []
        for base in clsobj.__bases__:
            if base.__name__ != "object":
                bases.append(self.cls_to_dict(base))
        clsdict = {}
        attrs = clsobj.__dict__
        for key in attrs:
            if inspect.isclass(attrs[key]):
                clsdict[key] = self.cls_to_dict(attrs[key])
            elif inspect.isfunction(attrs[key]):
                clsdict[key] = self.func_to_dict(attrs[key])
            elif isinstance(attrs[key], (set, frozenset, dict, list, 
                                        tuple, int, float, bool, 
                                        type(None), str)):
                clsdict[key] = attrs[key]
            elif isinstance(attrs[key], classmethod):
                clsdict[key] = {"classmethod" : self.func_to_dict(attrs[key].__func__)}
            elif isinstance(attrs[key], staticmethod):
                clsdict[key] = {"staticmethod" : self.func_to_dict(attrs[key].__func__)}
        return {"name" : clsobj.__name__, "bases" : bases, "dict" : clsdict}

    def obj_to_dict(self, obj):
        if isinstance(obj, types.CodeType):
            return {"co_argcount": obj.co_argcount, \
                    "co_posonlyargcount": obj.co_posonlyargcount, \
                    "co_kwonlyargcount" : obj.co_kwonlyargcount, \
                    "co_nlocals" : obj.co_nlocals, \
                    "co_stacksize" : obj.co_stacksize, \
                    "co_flags" : obj.co_flags, \
                    "co_code" : obj.co_code, \
                    "co_consts" : obj.co_consts, \
                    "co_names" : obj.co_names, \
                    "co_varnames" : obj.co_varnames, \
                    "co_filename" : obj.co_filename, \
                    "co_name" : obj.co_name, \
                    "co_firstlineno" : obj.co_firstlineno, \
                    "co_lnotab" : obj.co_lnotab, \
                    "co_freevars" : obj.co_freevars, \
                    "co_cellvars" : obj.co_cellvars}    
        return {"class": self.cls_to_dict(obj.__class__), "vars": obj.__dict__}

    def pull_from_code_to_func_globals(self, codeobj, func = None):
        if func is None:
            return {}
        
        globs = {}
        for i in codeobj.co_names: 
            if i in self.builtin_fnames:
                globs[i] = f"<built-in function {i}>"
            elif i in self.builtin_cnames:
                globs[i] = f"<built-in class {i}>"
            elif i in func.__globals__:
                if inspect.isclass(func.__globals__[i]):
                    globs[i] = self.cls_to_dict(func.__globals__[i])
                elif inspect.isfunction(func.__globals__[i]):
                    if func.__name__ == i:
                        globs[i] = f"<recursive function {i}>" # recursion identifier
                    else:
                        globs[i] = self.func_to_dict(func.__globals__[i])
                elif inspect.ismodule(func.__globals__[i]):
                    globs[i] = f"<module {i}>" # sets the module with its name
                else:
                    globs[i] = func.__globals__[i]

        for i in codeobj.co_consts:
            if isinstance(i, types.CodeType):
                globs.update(self.pull_from_code_to_func_globals(i, func))

        return globs

    def func_to_dict(self, func):
        
        globs = {}
        globs.update(self.pull_from_code_to_func_globals(func.__code__, func))

        return {"__globals__": globs, \
            "__name__": func.__name__, \
            "__qualname__" : func.__qualname__, \
            "__code__": self.obj_to_dict(func.__code__), \
            "__module__" : func.__module__, \
            "__annotations__" : func.__annotations__, \
            "__closure__" : func.__closure__, \
            "__defaults__" : func.__defaults__, \
            "__kwdefaults__" : func.__kwdefaults__}


    def dumps_str(self, string):
        return '"' + string.replace("\\", r"\\").replace("\"", r"\"")\
                .replace("\r", r"\r").replace("\t", r"\t").replace("\f", r"\f")\
                .replace("\b", "\\b").replace("\n", r"\n") + '"'

    def dumps_list(self, lst):
        res = "["
        for el in tmplst:
            res += " " + self._dumps(el) + ","
        res = res[:-1] # gettin rid of the last comma
        res += " ]"
        return res 

    def dumps_dict(self, dct, fullname = None):
        # fullname is auto-generated sequence key1.key2.key3."key 4".key5 and so on.
        # If fullname is empty - that means we are on the top level dictionary.
        # Else - we create table like this: [key1.key2.key3."key 4".key5].
        # After we did that, we append all 'key = value' pairs down the road.
        # After everything is done, add the last line: "\n".
        # Let's just ensure ourselves that keys in tables cannot be complicated!
        # Then [key1.key2."key 3".key4]
        #      internal_key1.internal_key2 = ...
        # is impossible.
        res = ""
        if fullname:
            res = f"[{fullname}]\n"

        for key, val in dct.items():
            if isinstance(val, dict):
                self.serialization_q.append( (self.generate_key(fullname, key), val) )
            else:
                res += f"{str(key)} = {self.dumps(val)}\n"
        res += "\n"
        return res
        
    def _dumps(self, obj):
        if obj is True:
            return "true"   
        elif obj is False:
            return "false"
        elif isinstance(obj, (int, float)):    
            return str(obj)                    
        elif isinstance(obj, bytes):
            return f"\"{str(list(bytearray(obj)))}\""
        elif isinstance(obj, str):
            return self.dumps_str(obj)
        elif isinstance(obj, (set, frozenset, list, tuple) ):
            return self.dumps_list(obj)
        elif isinstance(obj, dict):
            return self.dumps_dict(obj)
        elif isinstance(obj, types.FunctionType):
            return self.dumps_dict(self.func_to_dict(obj))
        elif isinstance(obj, types.BuiltinFunctionType):
            if obj.__name__ in self.builtin_fnames:
                return f"\"<built-in function {obj.__name__}>\""
            else:
                module = __import__(obj.__module__)
                module_func = getattr(module, obj.__name__)
                if module_func is not None: 
                    return f"\"<{module.__name__} function {module_func.__name__}>\"" 
                else:
                    raise NameError(f"No function {obj.__name__} was found" \
                                    + f"in module {module.__name__}")
        elif obj is None:
            return "<None>"
        elif inspect.isclass(obj):
            return self.dumps_dict(self.cls_to_dict(obj))
        elif isinstance(obj, types.CellType):   # for closures
            return self.dumps(obj.cell_contents)
        elif isinstance(obj, object):
            return self.dumps_dict(self.obj_to_dict(obj))
        else:
            raise TypeError(f"Object {obj} is not TOML-parsable.")

    def dumps(self, obj):
        toml_dict = dict() # primitivated dictionary to convert to TOML
        if obj is True:
            return "ttype = \"bool\"\ntvalue = true"
        elif obj is False:
            return "ttype = \"bool\"\ntvalue = false"
        elif obj is None:
            return "ttype = \"NoneType\"\ntvalue = \"<None>\""
        elif isinstance(obj, (int, float)):
            return f"ttype = \"digit\"\ntvalue = {str(obj)}"
        elif isinstance(obj, bytes):
            return f"ttype = \"bytes\"\ntvalue = \"{str(list(bytearray(obj)))}\""
        elif isinstance(obj, str):
            return f"ttype = \"string\"\ntvalue = {self.dumps_str(obj)}"
        elif isinstance(obj, (set, frozenset, list, tuple) ):
            toml_dict["ttype"] = "array"
            toml_dict["tvalue"] = self.expand_list(obj)
        elif isinstance(obj, dict):
            toml_dict["ttype"] = "dictionary"
            toml_dict["tvalue"] = self.expand_dict(obj)
        elif isinstance(obj, types.FunctionType):
            toml_dict["ttype"] = "dictionary"
            toml_dict["tvalue"] = self.func_to_dict(obj)
        elif isinstance(obj, types.BuiltinFunctionType):
            if obj.__name__ in self.builtin_fnames:
                return f"ttype = \"string\"\n\"<built-in function {obj.__name__}>\""
            else:
                module = __import__(obj.__module__)
                module_func = getattr(module, obj.__name__)
                if module_func is not None: 
                    return f"ttype = \"string\"\n\"<{module.__name__} function {module_func.__name__}>\"" 
                else:
                    raise NameError(f"No function {obj.__name__} was found" \
                                    + f"in module {module.__name__}")
        elif inspect.isclass(obj):
            toml_dict["ttype"] = "dictionary"
            toml_dict["tvalue"] = self.cls_to_dict(obj)
        elif isinstance(obj, object):
            toml_dict["ttype"] = "dictionary"
            toml_dict["tvalue"] = self.obj_to_dict(obj)
        else:
            raise TypeError(f"Object {obj} is not TOML-parsable.")
        
        for el in self.serialization_q:
            self.set_val(toml_dict, el[0], el[1])
        






    def parse_tstring(self, tstr, index):
        if tstr[index] != '"':
            #self._exception_notify(tstr, index)
            raise ValueError(f"This is not a string! Current index: {index}")
        end_index = index + 1

        try:
            while True: # read everything until we get bare " symbol
                if tstr[end_index] == '\\': # this one is for sure escaping
                    end_index += 2
                    continue
                if tstr[end_index] == '"':
                    break
                end_index += 1
        except IndexError:
            raise IndexError(f"No \" was encountered on the end of string!")
        
        s = tstr[index + 1 : end_index]
        # working on escaping symblos
        res, n, i = [], len(s), 0
        while i < n:
            if s[i] == "\\":
                if i + 1 == n:
                    break
                if s[i + 1] == "\\":
                    res.append("\\")
                elif s[i + 1] == "n":
                    res.append("\n")
                elif s[i + 1] == "r":
                    res.append("\r")
                elif s[i + 1] == "t":
                    res.append("\t")
                elif s[i + 1] == '"':
                    res.append('"')
                elif s[i + 1] == "b":
                    res.append("\b")
                elif s[i + 1] == "f":
                    res.append("\f")
                elif s[i + 1] == "/":
                    res.append("/")
                else:
                    raise ValueError(f"Can't work out this escaping {s[i : i + 2]}.")
                i += 1
            else:
                res.append(s[i])
            i += 1
        res = "".join(res)
        return res, end_index + 1






def main():
    pass

if __name__ == "__main__":
    main()