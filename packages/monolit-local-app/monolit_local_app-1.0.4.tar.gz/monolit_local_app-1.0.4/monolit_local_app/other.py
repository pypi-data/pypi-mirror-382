from flask import Request

class File:
    def __init__(self, path, name, text, data=None):
        self.path = path
        self.name = name
        self.text = text
        if data != None:
            self.data = data
        else:
            self.data = text

    def __repr__(self):
        return f"File object, with path '{self.path}'"

class DirTree:
    def __init__(self, path):
        import os

        self.path = path
        self.name = self.path.replace("/", "\\").split("\\")[-1]
        self.items = {}

        for i in os.walk(path):
            dir_path, dir_names, file_names = i
            break

        for file_name in file_names:
            #if file_name.split(".")[-1] in ["homl", "txt", "c", "h", "cpp", "xml", "json", "html", "css", "js", "py"]: # ЕЛЕНА ВИКТОРОВНА ЗДЕСЬ ВАЖНО!!! ПОСМОТРИТЕ!!! ЭТО СПИСОК ВСЕХ РАСШИРЕНИЙ КОТОРЫЕ РЕДАКТОР СМОЖЕТ КОРРЕКТНО ИНТЕРПРИТИРОВАТЬ, Я НЕ ЗНАЮ КАКИЕ СЮДА ЕЩЕ МОЖНО ДОБАВИТЬ ВЫПИСАЛ ВСЕ ЧТО ПРИШЛИ В ГОЛОВУ. ЕСЛИ НУЖНО ДОПОЛНИТЕ.
            try:
                with open(dir_path + "\\" + file_name, "r") as f:
                    file_text = f.read()

                self.items[file_name] = File(dir_path + "\\" + file_name, file_name, file_text)

            except UnicodeDecodeError:
                with open(dir_path + "\\" + file_name, "r") as f:
                    self.items[file_name] = File(dir_path + "\\" + file_name, file_name, None, f)

        for dir_name in dir_names:
            self.items[dir_name] = DirTree(dir_path + "\\" + dir_name)

    def __repr__(self, tabs=1, is_first=False):
        out = ""
        if is_first:
            out += "    "*(tabs-2) + "|---" + self.name + " {\n"
        else:
            out += "    "*(tabs-1) + self.name + " {\n"

        index = -1
        for item_key in self.items:
            index += 1
            if index == 0:
                is_first = True
            else:
                is_first = False

            item_ = self.items[item_key]
            if type(item_) == File:
                if is_first:
                    out += "    "*(tabs-1) + "|---" + item_.name + "\n"
                else:
                    out += "    "*tabs + item_.name + "\n"
                
            elif type(item_) == DirTree:
                out += item_.__repr__(tabs+1, is_first)

        return out + "    "*(tabs-1) + "}\n"

    def get(self, path_fragments, pos=0):
        for i in list(self.items.keys()):
            if i == path_fragments[pos]:
                if pos + 1 == len(path_fragments):
                    return self.items[i]

                return self.items[i].get(path_fragments, pos+1)

    def find(self, path):
        return self.get(path.replace("/", "\\").split("\\"))
    
    def walk(self, name):
        for key in self.items:
            item = self.items[key]

            if isinstance(item, File):
                if item.name == name:
                    return item
            else:
                return item.walk(name)
    
    def iterate_text(self, tabs=0):
        out = []
        for item_key in self.items:
            item_ = self.items[item_key]

            out.append("    "*tabs + item_.name)
            if type(item_) == DirTree:
                out.extend(item_.iterate_text(tabs+1))
        return out

def del_garbage(text):
    out = ""

    for i, char in enumerate(text):
        if not char in "\t\n ":
            out += text[i:]
            break

    i = len(out)
    while i > 1:
        i -= 1
        char = out[i]
        if not char in "\n\t ":
            return out[:i + 1]
    return out

def rinfo(name, data, tabs, tab):
    print(f"{tab*tabs}{name}:" + " {")
    for key, value in data.items():
        if not isinstance(value, dict):
            print(f"{tab*(tabs+1)}{key}: {value}")
        else:
            rinfo(key, value, tabs+1, tab)
    print(f"{tab*tabs}" + "}")

def info(request : Request):
    tab = "    "

    if not isinstance(request, Request):
        print("Not request")
        return
    
    print(f"Request <{request.content_type}> :" + " {")
    for key, value in request.json.items():
        if not isinstance(value, dict):
            print(f"{tab}{key}: {value}")
        else:
            rinfo(key, value, 1, tab)
    print("}")

def sum_paths(*args):
    out = ""
    for path in args:
        if del_garbage(path).replace("/", "\\")[-1] == "\\":
            out += del_garbage(path).replace("/", "\\")
        else:
            out += del_garbage(path).replace("/", "\\") + "\\"
    return out[:-1]