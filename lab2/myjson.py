import inspect
import types
import dis

class myjson:
    def __init__(self, indent=4):
        self._indent = indent
    
    
    def dumps_list(self, lst, level): 
        if len(lst) == 0:
            return "[]"
        curr_indent = "\n" + " " * self._indent * level
        res = curr_indent + "["
        for el in lst:
            res += curr_indent + self.dumps(el, level) + ","
        res = res[:-1] # gettin rid of the last comma
        res += curr_indent + "]"
        return res 
        
    def dumps_dict(self, dct, level):
        if len(dct) == 0:
            return "{}"
        curr_indent = "\n" + " " * self._indent * level
        res = curr_indent + "{"
        for key in dct.keys():
            res += curr_indent + f"\"{str(key)}\" : " + self.dumps(dct[key], level) + ","
        res = res[:-1] # getting rid of the last comma
        res += curr_indent + "}"
        return res


    def func_to_dict(self, func):
        globs = {}
        for i in func.__code__.co_names:
            try:
                if inspect.isclass(func.__globals__[i]):
                    globs[i] = self.cls_to_dict(func.__globals__[i])
                if inspect.isfunction(func.__globals__[i]):
                    if func.__name__ == i:
                        globs[i] = f"<recursive function {i}>" # recursive
                    else:
                        globs[i] = self.func_to_dict(func.__globals__[i])
                else:
                    globs[i] = func.__globals__[i]
            except KeyError:
                if i in func.__globals__["__builtins__"]:
                    globs[i] = f"<built-in function {i}>"
        return {"__globals__": globs,
            "__name__": func.__name__,
            "__code__":
                {"co_argcount": func.__code__.co_argcount,
                 "co_posonlyargcount" : func.__code__.co_posonlyargcount,
                 "co_kwonlyargcount": func.__code__.co_kwonlyargcount,
                 "co_nlocals": func.__code__.co_nlocals,
                 "co_stacksize": func.__code__.co_stacksize,
                 "co_flags": func.__code__.co_flags,
                 "co_code": func.__code__.co_code,
                 "co_consts": func.__code__.co_consts,
                 "co_names": func.__code__.co_names,
                 "co_varnames": func.__code__.co_varnames,
                 "co_filename": func.__code__.co_filename,
                 "co_name": func.__code__.co_name,
                 "co_firstlineno": func.__code__.co_firstlineno,
                 "co_lnotab": func.__code__.co_lnotab,
                 "co_freevars": func.__code__.co_freevars,
                 "co_cellvars": func.__code__.co_cellvars
                 }
            }
    def cls_to_dict(self, clsobj):
        bases = []
        for base in clsobj.__bases__:
            if base.__name__ != "object":
                bases.append(self.cls_to_dict(base))
        clsdict = {}
        attrs = clsobj.__dict__
        for key in attrs.keys():
            if inspect.isclass(attrs[key]):
                clsdict[key] = self.cls_to_dict(attrs[key])
            elif inspect.isfunction(attrs[key]):
                clsdict[key] = self.func_to_dict(attrs[key])
            elif isinstance(attrs[key], (
                                           set, dict, list, tuple, int, 
                                           float, bool, type(None)
                                          )
                ):
                clsdict[key] = attrs[key]
        return {"name" : clsobj.__name__, "bases" : bases, "dict" : clsdict}



    def obj_to_dict(self, obj):
        if isinstance(obj, types.CodeType):
            tmp_dict, list_of_attrs = dict(), dir(obj)
            for attr in list_of_attrs:
                tmp_dict[attr] = getattr(obj, attr)
            return {"class": self.cls_to_dict(obj.__class__), "vars": tmp_dict}
        return {"class": self.cls_to_dict(obj.__class__), "vars": obj.__dict__}

    def dumps(self, obj, level=-1):
        """ 
        So, this is a complex object, which can be one of 3 different types:
            1. Function (lambdas included)
            2. Object (simple or complex, idc)
            3. Class (type nested from object)
        JSON supports simple parsing for these things:
            1. Strings
            2. Numbers (10, 1.5, -30, 1.2e10)
            3. Booleans (true, false)
            4. None (null)
            5. Array <or list> ([1,2,"hello"])
            6. Objects(!) <in our case dictionaries> {"key" : "value", "age" : 30}
        """
        if isinstance(obj, (int, float)):
            return str(obj)
        elif isinstance(obj, bytes):
            return f"\"{str(list(bytearray(obj)))}\""
        elif isinstance(obj, str):
            return f"\"{obj}\""
        elif isinstance(obj, (set, tuple)):
            return self.dumps_list(list(obj), level + 1)
        elif isinstance(obj, list):
            return self.dumps_list(obj, level + 1)
        elif isinstance(obj, dict):
            return self.dumps_dict(obj, level + 1)
        elif isinstance(obj, types.FunctionType):
            return self.dumps_dict(self.func_to_dict(obj), level + 1)
        elif obj is None:
            return "null"
        elif obj is True:
            return "true"
        elif obj is False:
            return "false"
        elif obj is float("Inf"):
            return "Infinity"
        elif obj is float("-Inf"):
            return "-Infinity"
        elif obj is float("NaN"):
            return "NaN"
        elif inspect.isclass(obj):
            return self.dumps_dict(self.cls_to_dict(obj), level + 1)
        elif isinstance(obj, object):
            return self.dumps_dict(self.obj_to_dict(obj), level + 1)
        else:
            raise TypeError()

    def dump(self, obj, fname):
        try:
            with open(fname, "w") as fhandler:
                fhandler.write(self.dumps(obj, 0))
        except FileNotFoundError as e:
            print(e)
    





    def loads(self, string):
        return ""

    def load(self, fname):
        try:
            with open(fname, "r") as fhandler:
                text = fhandler.read()
                obj = self.loads(text)
                return obj
        except FileNotFoundError as e:
            print(e)
















### TESTING SECTION  ###
def mul(a): # closure
    def helper(b):
        print(a*b)
    return helper

def fact(a):
    if a < 2:
        return 1
    return a * fact(a - 1)

class A:
    def __init__(self):
        self.prop1 = 7
        self.prop2 = [12,13,14]

    def fact(self, a):
        if a < 2:
            return 1
        return a * self.fact(a - 1)

class myclass:
    def __init__(self):
        self.a = 5
        self.b = "string"
        self.c = (3,2,[23, "another string"],)
        self.d = A()



def main():
    packer = myjson(2)
    obj1 = myclass()
    s = packer.dumps(obj1)
    with open("output1.json", "w") as file:
        file.write(s)
    print()

    cls1 = myclass
    s = packer.dumps(cls1)
    with open("output2.json", "w") as file:
        file.write(s)
    print()

if __name__ == "__main__":
    main()