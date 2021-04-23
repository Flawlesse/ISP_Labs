import inspect
import types
import sys
import dis
import builtins
#from math import *
import math

class myjson:
    def __init__(self, indent=4):
        self._indent = indent
        self.builtin_names = [el[0] for el in inspect.getmembers(builtins, inspect.isbuiltin)]
    
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
    
    def dumps_str(self, string):
        return '"' + string.replace("\\", r"\\").replace("\"", r"\"")\
                .replace("\r", r"\r").replace("\t", r"\t").replace("\f", r"\f")\
                .replace("\b", "\\b").replace("\n", r"\n") + '"'

    def func_to_dict(self, func):
        # this code will be updated
        globs = {}
        
        for i in func.__code__.co_names: 
            if i in self.builtin_names:
                globs[i] = f"<built-in function {i}>"
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

        return {"__globals__": globs,
            "__name__": func.__name__,
            "__qualname__" : func.__qualname__,
            "__code__": self.obj_to_dict(func.__code__),
            "__module__" : func.__module__,
            "__annotations__" : func.__annotations__,
            "__closure__" : func.__closure__,
            "__defaults__" : func.__defaults__,
            "__kwdefaults__" : func.__kwdefaults__
            }
    
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
            elif isinstance(attrs[key], (
                                           set, dict, list, tuple, int, 
                                           float, bool, type(None), str
                                          )
                ):
                clsdict[key] = attrs[key]
            elif isinstance(attrs[key], classmethod):
                clsdict[key] = {"classmethod" : self.func_to_dict(attrs[key].__func__)}
            elif isinstance(attrs[key], staticmethod):
                clsdict[key] = {"staticmethod" : self.func_to_dict(attrs[key].__func__)}
        return {"name" : clsobj.__name__, "bases" : bases, "dict" : clsdict}

    def obj_to_dict(self, obj):
        # this thing needs refactoring in case it parses code objects in closures!!!
        if isinstance(obj, types.CodeType):
            #print("codetype called")
            return {"co_argcount": obj.co_argcount,
                    "co_posonlyargcount": obj.co_posonlyargcount,
                    "co_kwonlyargcount" : obj.co_kwonlyargcount,
                    "co_nlocals" : obj.co_nlocals,
                    "co_stacksize" : obj.co_stacksize,
                    "co_flags" : obj.co_flags,
                    "co_code" : obj.co_code,
                    "co_consts" : obj.co_consts,
                    "co_names" : obj.co_names,
                    "co_varnames" : obj.co_varnames,
                    "co_filename" : obj.co_filename,
                    "co_name" : obj.co_name,
                    "co_firstlineno" : obj.co_firstlineno,
                    "co_lnotab" : obj.co_lnotab,
                    "co_freevars" : obj.co_freevars,
                    "co_cellvars" : obj.co_cellvars}
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
        if obj is True:
            return "true"   
        elif obj is False:
            return "false"
        elif isinstance(obj, (int, float)):    # I honestly do not understand why the fuck 
            return str(obj)                    # isinstance(True, (int, float)) returns True 
        elif isinstance(obj, bytes):
            return f"\"{str(list(bytearray(obj)))}\""
        elif isinstance(obj, str):
            return self.dumps_str(obj)
        elif isinstance(obj, (set, tuple)):
            return self.dumps_list(list(obj), level + 1)
        elif isinstance(obj, list):
            return self.dumps_list(obj, level + 1)
        elif isinstance(obj, dict):
            return self.dumps_dict(obj, level + 1)
        elif isinstance(obj, types.FunctionType):
            return self.dumps_dict(self.func_to_dict(obj), level + 1)
        elif isinstance(obj, types.BuiltinFunctionType):
            if obj.__name__ in self.builtin_names:
                return f"\"<built-in function {obj.__name__}>\""
            else:
                module = __import__(obj.__module__)
                module_func = getattr(module, obj.__name__)
                if module_func is not None: #and inspect.isfunction(module_func):
                    return f"\"<{module.__name__} function {module_func.__name__}>\"" 
                else:
                    raise NameError(f"No function {obj.__name__} was found" \
                                    + f"in module {module.__name__}")
        elif obj is None:
            return "null"
        elif inspect.isclass(obj):
            return self.dumps_dict(self.cls_to_dict(obj), level + 1)
        elif isinstance(obj, object):
            return self.dumps_dict(self.obj_to_dict(obj), level + 1)
        else:
            raise TypeError()

    def dump(self, obj, fname):
        try:
            with open(fname, "w") as fhandler:
                fhandler.write(self.dumps(obj))
        except FileNotFoundError as e:
            print(e)


    
    def _exception_notify(self, jstr, index):
        if index >= 10:
            print(f"Surroundings: {jstr[index - 10 : index + 10]}")
        else:
            print(f"Surroundings: {jstr[0 : index + 10]}")
        print(f"The actual symbol: {jstr[index]}")
    
    # EVALUATING THE JSON STRING 
    def _parse(self, jstr, index):
        if jstr[index] == '"':
            res, index = self.parse_jstring(jstr, index)
        elif jstr[index] == '[':
            res, index = self.parse_jarray(jstr, index)
        elif jstr[index] == '{':
            res, index = self.parse_jdict(jstr, index)
        elif jstr[index] == 't' and jstr[index : index + 4] == "true":
            index += 4
            res = True
        elif jstr[index] == 'f' and jstr[index : index + 5] == "false":
            index += 5
            res = False
        elif jstr[index] == 'n' and jstr[index : index + 4] == "null":
            index += 4
            res = None
        elif jstr[index].isdigit() or jstr[index] == '-'\
            and jstr[index + 1].isdigit():
            res, index = self.parse_jdigit(jstr, index)
        else:
            self._exception_notify(jstr, index)
            raise ValueError(f"Something is not parsable at index {index}")
        return res, index


    def parse_jstring(self, jstr, index):
        if jstr[index] != '"':
            self._exception_notify(jstr, index)
            raise ValueError(f"This is not a string! Current index: {index}")
        end_index = index + 1

        while True: # read everything until we get bare " symbol
            if jstr[end_index] == '\\': # this one is for sure escaping
                end_index += 2
                continue
            if jstr[end_index] == '"':
                break
            end_index += 1
        
        res = jstr[index + 1 : end_index]
        res = res.replace(r"\"", "\"").replace(r"\n", "\n")\
                .replace(r"\r", "\r").replace(r"\t", "\t")\
                .replace(r"\\", "\\").replace("\\b", "\b")\
                .replace(r"\f", "\f").replace(r"\/", "/")
        return res, end_index + 1
    
    def parse_jdigit(self, jstr, index):
        if not (jstr[index].isdigit() or jstr[index] == '-' ):
            self._exception_notify(jstr, index)
            raise ValueError(f"This is not a number! Current index: {index}")
        end_index = index + 1
        while True:
            if not jstr[end_index].isdigit() \
                and (jstr[end_index] != 'E' \
                or jstr[end_index] != 'e' or jstr[end_index] != '+' \
                or jstr[end_index] != '-' or jstr[end_index] != '.'):
                break
            end_index += 1
        try:
            jstr[end_index + 1] # check if we are at the very end of json string
        except IndexError:
            # convert to int or float
            try: 
                return int(jstr[index : end_index]), end_index
            except ValueError:
                try:
                    return float(jstr[index : end_index]), end_index
                except ValueError:
                    raise ValueError(f"Digit like this \"{jstr[index : end_index]}\" is non-parsable!")

        if not jstr[end_index + 1].isdigit() \
            and (jstr[end_index + 1] == ' ' \
            or jstr[end_index + 1] == '\n' \
            or jstr[end_index + 1] == ','):
            try: 
                return int(jstr[index : end_index]), end_index
            except ValueError:
                try:
                    return float(jstr[index : end_index]), end_index
                except ValueError:
                    raise ValueError(f"Digit like this \"{jstr[index : end_index]}\" is non-parsable!")
        raise ValueError(f"Digit like this \"{jstr[index : end_index + 1]}\" is non-parsable!")

    def parse_jarray(self, jstr, index):
        if jstr[index] != '[':
            self._exception_notify(jstr, index)
            raise ValueError(f"This is not an array! Current index: {index}")
        end_index = index + 1
        if jstr[index + 1] == ']':
            return list(), end_index + 1
        
        lst = []
        comma_encountered = False
        while True:
            if jstr[end_index] == ']':
                if not comma_encountered:
                    break
                else:
                    self._exception_notify(jstr, end_index)
                    raise ValueError("Unneeded comma at the end!" \
                        + f"Current index: {end_index}")
            elif jstr[end_index] == ',':
                if not comma_encountered:
                    comma_encountered = True
                    end_index += 1
                    continue
                else:
                    self._exception_notify(jstr, end_index)
                    raise ValueError(f"Two commas in a row encountered!" \
                                    + f"Current index: {end_index}")
            elif jstr[end_index] == '\n' or jstr[end_index] == ' ':
                end_index += 1
                continue

            res, end_index = self._parse(jstr, end_index)

            if len(lst) != 0:
                if comma_encountered:
                    lst.append(res)
                    comma_encountered = False
                else:
                    self._exception_notify(jstr, end_index)
                    raise ValueError("One of elements in array is not json parsable!"
                                    + f"Current index: {end_index}") 
            else:
                lst.append(res)
        # on this stage we have the fully parsed array
        return lst, end_index + 1
            
    def parse_jdict(self, jstr, index):
        if jstr[index] != '{':
            self._exception_notify(jstr, index)
            raise ValueError(f"This is not a dictionary! Current index: {index}")
        end_index = index + 1
        if jstr[end_index] == '}':
            return dict(), end_index + 1
        
        dct = {}
        comma_encountered, colon_encountered = False, False
        key, val = None, None
        while True:
            if jstr[end_index] == '}':
                if not (comma_encountered and colon_encountered):
                    break
                else:
                    self._exception_notify(jstr, end_index)
                    raise ValueError("Unneeded comma or colon at the end!" \
                                    + f"Current index: {end_index}")
            elif jstr[end_index] == ',':
                comma_encountered = True
                end_index += 1
                continue
            elif jstr[end_index] == ':':
                if key is not None:
                    colon_encountered = True
                    end_index += 1
                    continue
                else:
                    self._exception_notify(jstr, end_index)
                    raise ValueError("Colon encountered before the key appeared!" \
                    + f"Current index: {end_index}")
            elif jstr[end_index] == '\n' or jstr[end_index] == ' ':
                end_index += 1
                continue
            
            if key is None and not colon_encountered:
                key, end_index = self.parse_jstring(jstr, end_index) # this can only be a string
                continue

            if key is not None and colon_encountered:
                val, end_index = self._parse(jstr, end_index) # this can be anything
                colon_encountered = False
            if len(dct) != 0:
                if comma_encountered:
                    dct[key] = val
                    comma_encountered = False
                else:
                    self._exception_notify(jstr, end_index)
                    raise ValueError("No comma was encountered!"
                                     + f"Current index: {end_index}")
            else:
                dct[key] = val
            key, val = None, None
        # on this stage we have the fully parsed dictionary
        return dct, end_index + 1
    

    # this evaluates the json string into python primitives (dict, str, bool, ...)
    def _evaluate(self, jstr):
        res = None
        curr_index = 0
        while True:
            if jstr[curr_index] == '\n' or jstr[curr_index] == ' ':
                curr_index += 1
            else:
                break
        res, _ = self._parse(jstr, curr_index)
        return res



    # ACTUALLY GETTING DESERIALIZED OBJECT
    def dict_to_func(self, jsonobj):
        # here will be the whole lot of magic behind closures and other stuff
        globs = {}
        for key, val in jsonobj["__globals__"].items():
            if isinstance(val, str):
                if "built-in function" in val:
                    globs[key] = getattr(builtins, key)
                    continue
            globs[key] = self._deserialize(val)

        codeobj = self.dict_to_code(jsonobj["__code__"])
        res = types.FunctionType(codeobj, 
                                 globs, 
                                 jsonobj["__name__"])

        res.__defaults__ = jsonobj["__defaults__"] if jsonobj["__defaults__"] is None \
                             else tuple(jsonobj["__defaults__"])
        res.__kwdefaults__ = jsonobj["__kwdefaults__"]
        self.add_recursion_if_needed(res)

        return res

    # use when de-serializing
    def add_recursion_if_needed(self, func_obj):
        if (func_obj.__name__ in func_obj.__globals__.keys()):
            if inspect.ismethod(func_obj):
                func_obj.__globals__[func_obj.__name__] = func_obj.__func__
            else:
                func_obj.__globals__[func_obj.__name__] = func_obj

    def dict_to_class(self, jsonobj):
        bases = self.deserialize_jarr(jsonobj["bases"])
        return type(jsonobj["name"], 
                    tuple(bases), 
                    self.deserialize_jobj(jsonobj["dict"]))

    def dict_to_obj(self, jsonobj):
        objcls = self.dict_to_class(jsonobj["class"])
        res = objcls()
        res.__dict__ = self.deserialize_jobj(jsonobj["vars"])
        return res

    def dict_to_code(self, jsonobj):
        consts = tuple(self._deserialize(jsonobj["co_consts"]))
        codeobj = types.CodeType(jsonobj["co_argcount"],
                                jsonobj["co_posonlyargcount"],
                                jsonobj["co_kwonlyargcount"],
                                jsonobj["co_nlocals"],
                                jsonobj["co_stacksize"],
                                jsonobj["co_flags"],
                                bytes(bytearray(self.parse_jarray(jsonobj["co_code"], 0)[0])),
                                consts,
                                tuple(jsonobj["co_names"]),
                                tuple(jsonobj["co_varnames"]),
                                jsonobj["co_filename"],
                                jsonobj["co_name"],
                                jsonobj["co_firstlineno"],
                                bytes(bytearray(self.parse_jarray(jsonobj["co_lnotab"], 0)[0])),
                                tuple(jsonobj["co_freevars"]),
                                tuple(jsonobj["co_cellvars"]))
        return codeobj

    def deserialize_jobj(self, jsonobj):
        if "co_argcount" in jsonobj \
            and "co_posonlyargcount" in jsonobj \
            and "co_kwonlyargcount" in jsonobj \
            and "co_nlocals" in jsonobj \
            and "co_stacksize" in jsonobj \
            and "co_flags" in jsonobj \
            and "co_code" in jsonobj \
            and "co_consts" in jsonobj \
            and "co_names" in jsonobj \
            and "co_varnames" in jsonobj \
            and "co_filename" in jsonobj \
            and "co_name" in jsonobj \
            and "co_firstlineno" in jsonobj \
            and "co_lnotab" in jsonobj \
            and "co_freevars" in jsonobj \
            and "co_cellvars" in jsonobj:
            res = self.dict_to_code(jsonobj)
        elif "__globals__" in jsonobj \
            and "__name__" in jsonobj \
            and "__code__" in jsonobj:
            res = self.dict_to_func(jsonobj)
        elif "class" in jsonobj \
            and "vars" in jsonobj:
            res = self.dict_to_obj(jsonobj)
        elif "name" in jsonobj \
            and "bases" in jsonobj \
            and "dict" in jsonobj:
            res = self.dict_to_class(jsonobj)
        elif "staticmethod" in jsonobj:
            res = staticmethod(self.dict_to_func(jsonobj["staticmethod"]))
        elif "classmethod" in jsonobj:
            res = classmethod(self.dict_to_func(jsonobj["classmethod"]))
        else:
            res = {}
            for key, val in jsonobj.items():
                if isinstance(val, str):
                    if "built-in function" in val:
                        res[key] = getattr(builtins, val)
                    else:
                        res[key] = val
                elif isinstance(val, list):
                    res[key] = self.deserialize_jarr(val)
                elif isinstance(val, dict):
                    res[key] = self.deserialize_jobj(val)
                else:
                    res[key] = val

        return res
            
    
    def deserialize_jarr(self, jsonobj):
        res = []
        for el in jsonobj:
            res.append(self._deserialize(el))
        return res


    def _deserialize(self, jsonobj):
        if isinstance(jsonobj, dict):
            res = self.deserialize_jobj(jsonobj)
        elif isinstance(jsonobj, list):
            res = self.deserialize_jarr(jsonobj)
        elif isinstance(jsonobj, str) and jsonobj[0] == '<' and jsonobj[-1] == '>':
            tmp = jsonobj[1 : -1].split(' ')
            if len(tmp) == 3:
                module_name, func_name = tmp[0], tmp[2]
                if "built-in" == module_name:
                    module = builtins
                elif "recursive" == module_name:
                    return module_name
                else: 
                    module = __import__(module_name)
                module_func = getattr(module, func_name)
                if module_func is not None: #and inspect.isfunction(module_func):
                    return module_func 
                else:
                    raise NameError(f"No function {func_name} was found" \
                                    + f"in module {module_name}")
            elif len(tmp) == 2:
                module_name = tmp[1]
                module = __import__(module_name)
                if module is not None:
                    return module
                else:
                    raise NameError(f"No module {module_name} was found")
        else:
            res = jsonobj
        return res


    def loads(self, string):
        return self._deserialize(self._evaluate(string))

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
    print(math.sqrt(a))
    if a < 2:
        return 1
    return a * fact(a - 1)

class A:
    def __init__(self):
        self.prop1 = 7
        self.prop2 = [12,13,14]
    
    @classmethod
    def fact(cls, a):
        #print(math.sqrt(a))
        print(math.sqrt(a))
        #print(a)
        if a < 2:
            return 1
        return a * cls.fact(a - 1)

    @classmethod
    def cmeth(cls, b):
        print(cls.fact)

    @staticmethod
    def smeth(a):
        print(a)

class myclass:
    def __init__(self):
        self.a = 5
        self.b = "string"
        self.c = (3,2,[23, "another string"],)
        self.d = A()
        print("Constructor of myclass called!")



def main():
    packer = myjson(2)
    #dis.dis(mul)
    #print(packer.dumps(mul))
    #times4 = mul(4)
    #dis.dis(times4)
    #print(times4)
    # print(packer.dumps(math.sqrt))
    obj = myjson
    packer.dump(obj, "output4.json")
    p = packer.load("output4.json")
    packer = p()


    obj1 = myclass()
    packer.dump(obj1, "output1.json")

    cls1 = myclass
    packer.dump(cls1, "output2.json")

    obj = packer.load("output1.json")
    print(type(obj.d).fact(5))
    obj.d.smeth(54)
    type(obj.d).smeth([13,(2,"aa")])

    obj = packer.load("output3.json")
    print(obj)

    print(packer.dumps(fact))
    
    

if __name__ == "__main__":
    main()