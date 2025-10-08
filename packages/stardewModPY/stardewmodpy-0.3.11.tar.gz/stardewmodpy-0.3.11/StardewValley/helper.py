from .verification import steamLoad
from .contentpatcher import ContentPatcher
from .slingshot import SlingShotFramework
from .FTM.farmtypemanager import FarmTypeManager
from .itemextensions import ItemExtensions
from .manifest import Manifest
from .jsonreader import jsonStardewRead
import os, shutil
from typing import Optional


class i18n:
    def __init__(self):
        self.json={
            "default":{},
            "de":{},
            "es":{},
            "fr":{},
            "it":{},
            "ja":{},
            "ko":{},
            "hu":{},
            "pt":{},
            "ru":{},
            "tr":{},
            "zh":{}
        }
    

class Helper:
    def __init__(self, manifest:Manifest, modFramework:Optional[ContentPatcher|SlingShotFramework|FarmTypeManager|ItemExtensions]=None):
        self.modFolderAssets=os.path.join(os.getcwd(), "assets")
        self.assetsFileIgnore=[]
        if modFramework is None:
            self.content = ContentPatcher(manifest=manifest)
        else:
            self.content = modFramework
        
        
        self.i18n=i18n()
        steamVerify=steamLoad()
        self.pathSteam=steamVerify.verify()
        self.jsonRead=jsonStardewRead()

        self.modPath=os.path.join("build", self.content.Manifest.Name)
        self.autoTranslate=False
        
    
    def sdk(self, assetFolder:str, assetObject:str):
        sdkPath=os.path.join(self.pathSteam, "Content (unpacked)", assetFolder, assetObject+".json")
        return self.jsonRead.read_json(sdkPath)


    def translation(self, language:str, key:str, value:str):
        from translate import Translator
        if language == "default"and self.autoTranslate:
            for langKey in self.i18n.json.keys():
                if langKey == "default":
                    continue
                
                translator=Translator(from_lang="en", to_lang=langKey)
                try:
                    translated_value = translator.translate(value)
                except Exception as e:
                    print(f"Error translating to {langKey}: {e}")
                    translated_value="translate error"
                self.i18n.json[langKey].update({key:translated_value})
        self.i18n.json[language].update({key:value})

    def _ignore_files(self, dir, files):
        ignored = []
        for file in files:
            full_path = os.path.join(dir, file)
            rel_path = os.path.relpath(full_path, self.modFolderAssets)
            rel_path = rel_path.replace("\\", "/")
            if rel_path in self.assetsFileIgnore:
                ignored.append(file)
        return ignored
    
    
    def write(self):
        if os.path.exists(self.modPath):
            shutil.rmtree(self.modPath)        
        
        if os.path.exists(os.path.join("dist")):
            shutil.rmtree(os.path.join("dist"))
        
        


        if not os.path.exists(self.modPath):
            os.makedirs(self.modPath)
            if isinstance(self.content, ContentPatcher):
                if(os.path.exists(self.modFolderAssets)):
                    shutil.copytree(self.modFolderAssets,os.path.join(self.modPath, "assets"), ignore=self._ignore_files)

        

        if isinstance(self.content, ContentPatcher):
            i18nPath=os.path.join(self.modPath, "i18n")

            if not os.path.exists(i18nPath):
                os.makedirs(i18nPath)
                for key, value in self.i18n.json.items():
                    self.jsonRead.write_json(os.path.join(i18nPath, f"{key}.json"), value)
        
        if not os.path.exists(os.path.join("dist")):
            os.makedirs(os.path.join("dist"))
        
        
            
        self.jsonRead.write_json(os.path.join(self.modPath, "manifest.json"), self.content.Manifest.getJson())
        self.jsonRead.write_json(os.path.join(self.modPath, self.content.fileName), self.content.contentFile)
        
        if isinstance(self.content, ContentPatcher):
            assets_path = os.path.join(self.modPath, "assets")
            if not os.path.exists(assets_path):
                os.makedirs(assets_path)

            for key, value in self.content.contentFiles.items():            
                self.jsonRead.write_json(os.path.join(self.modPath, "assets", f"{key}.json"), value)
        
        self.jsonRead.compress(self.modPath, os.path.join("dist", self.content.Manifest.Name), self.content.Manifest.Name)

        