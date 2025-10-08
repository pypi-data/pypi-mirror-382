import os

class libModel:
    def __init__(self, optionals: dict, modName: str):
        self.optionals=optionals
        self.modName=modName
        self.imports=""
        self.implements=""
        self.classData=""

        self.classFileData=""
        self.classFileData_imports=""
        self.classFileData_Father=""
        self.classFileData_params=""
        self.classFileData_contents=""

        self.import_file="__init__.py"

        self.corrects={
            "Maps":"Maps",
            "NPCS":"NPCs",
            "Dialogues":"Dialogues",
            "Events":"Events",
            "Schedules":"Schedules"
        }
        
    def write_file(self, path, content):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    def contents(self):
        if self.optionals[self.corrects[self.__class__.__name__]]:
            os.makedirs(os.path.join(self.modName, self.__class__.__name__), exist_ok=True)
            file_init=os.path.join(self.modName, self.__class__.__name__, self.import_file)
            if not os.path.isfile(file_init):
                self.write_file(file_init, self.classData)
    
    

    

    def add_item(self, item_name: str):
        self.contents()
        function_name = self.corrects[self.__class__.__name__]
        file_path = os.path.join(self.modName, "ModEntry.py")

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        new_lines = []
        addItem_new = False
        item_already_added = False

        for i, line in enumerate(lines):
            stripped = line.strip()
            indent = line[:len(line) - len(line.lstrip())]

            if addItem_new:
                if stripped == f"{function_name}_List.{item_name}()," or stripped == f"{function_name}_List.{item_name}()":
                    item_already_added = True
                    addItem_new = False
                    print("⚠️ Item already added")
                    new_lines.append(line)
                elif stripped == "]),":
                    if not item_already_added:
                        # Verifica se a linha anterior termina com vírgula
                        if new_lines and not new_lines[-1].rstrip().endswith(","):
                            new_lines[-1] = new_lines[-1].rstrip() + ",\n"
                        new_lines.append(f"{indent}    {function_name}_List.{item_name}(),\n")
                        item_already_added = True
                        self.add_import(item_name)
                    new_lines.append(line)
                    addItem_new = False
                else:
                    new_lines.append(line)

            elif f"{function_name}(mod=self" in stripped and f"{function_name}_List=[]" in stripped:
                print("Criando primeiro item")
                new_lines.append(f"{indent}{function_name}(mod=self, {function_name}_List=[\n")
                new_lines.append(f"{indent}    {function_name}_List.{item_name}(),\n")
                new_lines.append(f"{indent}]),\n")
                self.add_import(item_name)
            elif stripped == f"{function_name}(mod=self, {function_name}_List=[":
                new_lines.append(line)
                addItem_new = True
                item_already_added = False
            else:
                new_lines.append(line)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)



    def add_import(self, name:str):
        importFile=os.path.join(self.modName, self.__class__.__name__, self.import_file)
        with open(importFile, 'a', encoding='utf-8') as f:
            f.write(f"\nfrom NPCS.{name} import {name}\n")

        newFile=os.path.join(self.modName, self.__class__.__name__, name+".py")
        self.buildClassData(name)
        with open(newFile, 'w', encoding='utf-8') as f:
            f.write(self.classFileData)
    
    def buildClassData(self, name):
        self.classFileData=f"""{self.classFileData_imports}

class {name}{self.classFileData_Father}:
    def __init__(self{self.classFileData_params}):
        {self.classFileData_contents.replace("###name###", name)}"""