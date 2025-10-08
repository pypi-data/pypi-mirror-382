import os
from .Dialogues import Dialogues
from .Maps import Maps
from .Events import Events
from .NPCS import NPCS
from .Schedules import Schedules

class ExtraContents:
    def __init__(self, optionals, modName):
        self.optionals=optionals
        self.modName=modName

        self.Dialogues=None
        self.Maps=None
        self.Events=None
        self.NPCS=None
        self.Schedules=None

        if self.optionals["Dialogues"]:
            self.Dialogues=Dialogues(optionals, modName)
            self.Dialogues.contents()
        if self.optionals["Maps"]:
            self.Maps=Maps(optionals, modName)
            self.Maps.contents()
        if self.optionals["Events"]:
            self.Events= Events(optionals, modName)
            self.Events.contents()
        if self.optionals["NPCs"]:
            self.NPCS=NPCS(optionals, modName)
            self.NPCS.contents()
        if self.optionals["Schedules"]:
            self.Schedules=Schedules(optionals, modName)
            self.Schedules.contents()



    
    def saveEntry(self):
        mod_entry_path = os.path.join(self.modName, "ModEntry.py")
        framework_content=""
        framework_content_import=""
        if self.optionals["framework"] is not None:
            framework_content=f", modFramework={self.optionals['framework']}(manifest=manifest)"
            framework_content_import=f", {self.optionals['framework']}"
        
        imports=[]
        implements=[]

        if self.Dialogues is not None:
            imports.append(self.Dialogues.imports)
            implements.append(self.Dialogues.implements)
        if self.Maps is not None:
            imports.append(self.Maps.imports)
            implements.append(self.Maps.implements)
        if self.Events is not None:
            imports.append(self.Events.imports)
            implements.append(self.Events.implements)
        if self.NPCS is not None:
            imports.append(self.NPCS.imports)
            implements.append(self.NPCS.implements)
        if self.Schedules is not None:
            imports.append(self.Schedules.imports)
            implements.append(self.Schedules.implements)

        content = f"""from StardewValley import Manifest, Helper{framework_content_import}

{"\n\n".join(imports)}

class ModEntry(Helper):
    def __init__(self, manifest:Manifest):
        super().__init__(
            manifest=manifest{framework_content}
        )
        self.contents()
    
    def contents(self):
        # Add your contents here
        {",\n\n        ".join(implements)}
"""
        with open(mod_entry_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    def saveMain(self, author:str, version:str, description:str):
        main_path = os.path.join(self.modName, "main.py")
        mainContent=f"""from ModEntry import ModEntry
from StardewValley import Manifest

manifest=Manifest(
    Name="{self.modName}",
    Author="{author}",
    Version="{version}",
    Description="{description}",
    UniqueID="{author}.{self.modName}"
)
mod=ModEntry(manifest=manifest)

mod.write()
"""
        with open(main_path, "w", encoding="utf-8") as f:
            f.write(mainContent)