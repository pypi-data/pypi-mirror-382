import copy

class StartError(Exception):
    lineNumber = 0
    trace_line_print = False
    trace_counter = 0
    trace_count = False

class start:
    def copy(self, other):
        if type(other) == start or type(self) == start:
            raise StartError("null pointer exception. You forgot to instantiate the object.")
        vars(other).clear()

        for attr_name, attr_value in vars(self).items():
            vars(other)[attr_name] = copy.deepcopy(attr_value)

    def clone(self):
        return copy.deepcopy(self)

    def to_key(self):
        if isinstance(self, text):
            return str(self.value)
        if isinstance(self, number):
            return str(int(self.value))
        key = ""
        for attr_name, attr_value in vars(self).items():
            key += attr_value.to_key()

        return key

    def toStr(self):
        if type(self) == start:
            return "null"

        if isinstance(self, number) or isinstance(self, text):
            return str(self.value)

        result = ""
        for attr_name, attr_value in vars(self).items():
            if isinstance(attr_value, start):
                result += attr_value.toStr()
        return result

    def toStrStructured(self, debug=False):
        if type(self) == start:
            return "null"

        if isinstance(self, number) or isinstance(self, text):
            return str(self.value)

        values = []
        for attr_name, attr_value in vars(self).items():
            if isinstance(attr_value, start):
                values.append(attr_value.toStrStructured(debug))

        if debug:
            names = vars(self).copy()
            names.pop('indexLength', None)  # remove indexLength for collections
            elements = [f"{name} = {value}" for name, value in zip(names, values)]
            return f"{self}({', '.join(elements)})"
        else:
            return f"[{', '.join(values)}]"

    def __repr__(self):
        return type(self).__name__

    def __bool__(self):
        return bool(self.value)

class number(start):
    def __init__(self, value=0):
        # check for start objects
        if isinstance(value, start):
            if hasattr(value, "value"):
                value = value.value
            elif type(value) is start:
                raise StartError("null pointer exception. You forgot to instantiate the object.")
            else:
                raise StartError(f"{value} is not a number or python floatable type")

        # check if it can be converted to a start number
        try:
            self.value = int(value) if float(value).is_integer() else float(value)
        except (ValueError, TypeError):
            raise StartError(f"{value} is not a number or python floatable type")

class text(start):
    def __init__(self, value=''):
        # check for start objects
        if isinstance(value, start):
            if hasattr(value, "value"):
                value = value.value
            elif type(value) is start:
                raise StartError("null pointer exception. You forgot to instantiate the object.")
            else:
                raise StartError(f"{value} is not a text or python string type")

        # check if it can be converted to a start text, should always work
        try:
            self.value = str(value)
        except (ValueError, TypeError):
            raise StartError(f"{value} is not a text, number or python stringable type")