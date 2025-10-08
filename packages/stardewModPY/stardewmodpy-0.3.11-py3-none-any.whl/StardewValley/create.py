import sys, os, subprocess, platform, shutil

from .projectlibs import *
import subprocess
from .verification import steamLoad
from .jsonreader import jsonStardewRead
from .frameworks import frameworksList

def help(default:bool=False, cp_optional:bool=False):
    cores=colorize()
    msg_finally=""
    if default:
        msg_finally+=f"{cores.colorize(cores.green)}Usage:{cores.reset()}"       
        comandos_obrigatorios = {
            "sdvpy": cores.white,
            "create": cores.green,
            "<modname>": cores.cyan,
            "<author>": cores.yellow,
            "<version>": cores.cyan,
            "<description>": cores.red
        }
        msg_finally+="\n  " + ' '.join(f'{cores.colorize(cor)}{arg}' for arg, cor in comandos_obrigatorios.items()) + cores.reset()

    if cp_optional:
        print(f"\n{cores.colorize(cores.green)}Optional arguments:{cores.reset()}")

        comandos_opcionais = {
            "--framework <FrameworkName>": "Define custom framework (default: ContentPatcher)",
            "--MinimumApiVersion <Version>": "Set minimum API version",
            "--mods_path <Path>": "Define custom path to the game's Mods folder",
            "--Dialogues": "Create folder and structure for NPC dialogues",
            "--Events": "Create folder and structure for custom events",
            "--Maps": "Create folder and structure for maps",
            "--NPCs": "Create folder and structure for custom NPCs",
            "--Schedules": "Create folder and structure for schedules"
        }

        for opcional, descricao in comandos_opcionais.items():
            msg_finally+=f"\n  {cores.colorize(cores.cyan)}{opcional:<35}{cores.colorize(cores.white)}# {descricao}{cores.reset()}"

    msg_finally+=f"\n {cores.colorize(cores.green)}Adicionando novos itens:\n  {cores.colorize(cores.cyan)}sdvpy modName --add NPCS <nameNPC>{cores.reset()}"
    print(msg_finally)

def verify_dependence(unique_id:str, frameworksFolder:str, frameworkName:str):
    output_path = os.path.join(frameworksFolder, frameworkName)
    if os.path.exists(output_path + ".zip"):
        return True
    
    steamVerify=steamLoad()
    pathSteam=steamVerify.verify()
    pathModsSteam=os.path.join(pathSteam, "Mods")

    jsonRead=jsonStardewRead()

    for folder_name in os.listdir(pathModsSteam):
        folder_path = os.path.join(pathModsSteam, folder_name)
        manifest_path = os.path.join(folder_path, "manifest.json")

        if not os.path.isdir(folder_path) or not os.path.exists(manifest_path):
            continue
        manifest = jsonRead.read_json(manifest_path)

        if manifest.get("UniqueID") == unique_id:            
            jsonRead.compress(folder_path, output_path, frameworkName)
            return True
    
    return False
def setFrameworks(frameworkName:str):
    framework_info = frameworksList[frameworkName]

    unique_id = framework_info["UniqueID"]
    download_url = framework_info["url_download"]
    
    frameworksFolder= os.path.join("frameworks")
    os.makedirs(frameworksFolder, exist_ok=True)

    dependencesFolder=os.path.join("dependences")
    os.makedirs(dependencesFolder, exist_ok=True)

    
    if not verify_dependence(unique_id, frameworksFolder, frameworkName):
        print(f"{frameworkName} not found. Download it from {download_url} and place the downloaded .zip in the 'frameworks' folder of your project.")

    for dependence in frameworksList[frameworkName]["Dependencies"]:
        if not verify_dependence(frameworksList[dependence]["UniqueID"], dependencesFolder, dependence):
            print(f"{dependence} not found. Download it from {frameworksList[dependence]['url_download']} and place the downloaded .zip in the 'dependences' folder of your project.")

def createProject(modName:str, framework:str, mods_path:str=None):
    fileProject=os.path.join("sdvproject.json")
    jsonRead=jsonStardewRead()
    project_json={
        "defaultProject":modName,
        "mods_path":mods_path,
        "projects":{}
    }
    if os.path.exists(fileProject):
        project_json=jsonRead.read_json(fileProject)
    
    project_json["projects"][modName] = {
        "path": modName,
        "framework": framework
    }
    jsonRead.write_json(fileProject, project_json)

def runGame(modsFolder:str, projectsFolders:list[str]):
    jsonRead=jsonStardewRead()
    framework_folder=os.path.join(os.getcwd(), "frameworks")
    dependences_folder=os.path.join(os.getcwd(), "dependences")
    buildsFolder=os.path.join(os.getcwd(), "build")

    if os.path.exists(buildsFolder):
        shutil.rmtree(buildsFolder)
    os.makedirs(buildsFolder, exist_ok=True)

    if not os.path.exists(framework_folder):
        print(f"Pasta de frameworks não encontrada: {framework_folder}")
        return
    

    if not os.path.exists(dependences_folder):
        print(f"Pasta de dependências não encontrada: {dependences_folder}")
        return
    



    for fileName in os.listdir(framework_folder):
        if fileName.endswith(".zip"):
            zipPath = os.path.join(framework_folder, fileName)
            jsonRead.decompress(zipPath, buildsFolder)
    
    for fileName in os.listdir(dependences_folder):
        if fileName.endswith(".zip"):
            zipPath = os.path.join(dependences_folder, fileName)
            jsonRead.decompress(zipPath, buildsFolder)
    
    atualModBuild=os.path.join(modsFolder, "build")
    if os.path.exists(atualModBuild):
        shutil.copytree(atualModBuild, buildsFolder, dirs_exist_ok=True)  

    for folder in projectsFolders:
        folderBuild=os.path.join(folder, "build")
        if os.path.exists(folderBuild):
            shutil.copytree(folderBuild, buildsFolder, dirs_exist_ok=True)
        else:
            print(f"Pasta build não encontrada em {folder} compile esse projeto.")
    try:
        steamVerify=steamLoad()
        pathSteam=steamVerify.verify()
        exe_path = os.path.join(
            pathSteam,
            "StardewModdingAPI.exe" if platform.system() == 'Windows' else "StardewModdingAPI"
        )
        subprocess.run([exe_path, "--mods-path", buildsFolder], check=True)
        
    except Exception as e:
        print(f"Erro ao iniciar o jogo: {e}")

def main():
    if os.name == 'nt':
        os.system('')

    cores=colorize()
    if (len(sys.argv) == 2 or len(sys.argv) == 3) and sys.argv[1]=="run":
        fileProject = os.path.join("sdvproject.json")
        if not os.path.exists(fileProject):
            print(f"{cores.colorize(cores.red)}Arquivo sdvproject.json não encontrado.{cores.reset()}")
            return

        jsonRead = jsonStardewRead()
        projects_data = jsonRead.read_json(fileProject)
        projects = projects_data.get("projects", {})

        if len(sys.argv) == 3:
            modName = sys.argv[2]
        else:
            modName = projects_data.get("defaultProject")
        
        if not modName:
            print(f"{cores.colorize(cores.red)}Nenhum projeto padrão definido no arquivo de configuração.{cores.reset()}")
            return
        
        if modName not in projects:
            print(f"{cores.colorize(cores.red)}Projeto '{modName}' não encontrado no arquivo de configuração.{cores.reset()}")
            return
        
        project_path = projects[modName]["path"]
        main_py_path = os.path.join(project_path, "main.py")
        if os.path.exists(main_py_path):
            print(f"{cores.colorize(cores.green)}Iniciando o Projeto:{cores.reset()}")
            subprocess.run([sys.executable, "main.py"], cwd=project_path)
        else:
            print(f"{cores.colorize(cores.red)}main.py não encontrado no diretório do {modName}.{cores.reset()}")
            raise Exception("main.py not found")
        if len(sys.argv) == 2:
            runGame(
                modsFolder=project_path,
                projectsFolders=[paths["path"] for paths in projects_data["projects"].values() if paths["path"] != project_path]
            )
        return
    
    if len(sys.argv) == 5 and sys.argv[2]=="--add":
        modName=os.path.join(sys.argv[1])
        className=sys.argv[3]
        newItem=sys.argv[4]

        if className=="NPCS":
            classItens=NPCS({"NPCs": False}, modName)
            classItens.add_item(newItem)

            classItens=Dialogues({"Dialogues": False}, modName)
            classItens.add_item(newItem)

            classItens=Events({"Events": False}, modName)
            classItens.add_item(newItem)

            classItens=Schedules({"Schedules": False}, modName)
            classItens.add_item(newItem)
        if className=="Maps":
            classItens=Maps({"Maps": False}, modName)
            classItens.add_item(newItem)
        return


    if len(sys.argv) <6 or (len(sys.argv) == 2 and (sys.argv[1]=="help" or sys.argv[1]=="-h" or sys.argv[1]=="--help")):
        help(True, True)
        return
    
    modName=sys.argv[2]
    author=sys.argv[3]
    version=sys.argv[4]
    description=sys.argv[5]

    opcionais = {
        "framework": "ContentPatcher",
        "MinimumApiVersion": None,
        "mods_path": None,
        "Dialogues": False,
        "Events": False,
        "Maps": False,
        "NPCs": False,
        "Schedules": False
    }

    

    i = 6
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--framework" and i + 1 < len(sys.argv):
            opcionais["framework"] = sys.argv[i + 1]
            if opcionais["framework"] not in frameworksList:
                raise Exception(f"Framework {opcionais['framework']} not found")
            
            i += 2
        elif arg == "--MinimumApiVersion" and i + 1 < len(sys.argv):
            opcionais["MinimumApiVersion"] = sys.argv[i + 1]
            i += 2
        elif arg == "--mods_path" and i + 1 < len(sys.argv):
            opcionais["mods_path"] = sys.argv[i + 1]
            i += 2
        elif arg == "--Dialogues":
            if opcionais["framework"] != "ContentPatcher":
                print(f"{cores.colorize(cores.red)}--Dialogues option is only available for ContentPatcher framework.{cores.reset()}")
                raise Exception("Invalid argument: --Dialogues")
            opcionais["Dialogues"] = True
            i += 1
        elif arg == "--Events":
            if opcionais["framework"] != "ContentPatcher":
                print(f"{cores.colorize(cores.red)}--Events option is only available for ContentPatcher framework.{cores.reset()}")
                raise Exception("Invalid argument: --Events")
            opcionais["Events"] = True
            i += 1
        elif arg == "--Maps":
            if opcionais["framework"] != "ContentPatcher":
                print(f"{cores.colorize(cores.red)}--Maps option is only available for ContentPatcher framework.{cores.reset()}")
                raise Exception("Invalid argument: --Maps")
            opcionais["Maps"] = True
            i += 1
        elif arg == "--NPCs":
            if opcionais["framework"] != "ContentPatcher":
                print(f"{cores.colorize(cores.red)}--NPCs option is only available for ContentPatcher framework.{cores.reset()}")
                raise Exception("Invalid argument: --NPCs")
            opcionais["NPCs"] = True
            i += 1
        elif arg == "--Schedules":
            if opcionais["framework"] != "ContentPatcher":
                print(f"{cores.colorize(cores.red)}--Schedules option is only available for ContentPatcher framework.{cores.reset()}")
                raise Exception("Invalid argument: --Schedules")
            opcionais["Schedules"] = True
            i += 1
        
        else:
            print(f"{cores.colorize(cores.red)}Invalid argument: {arg}{cores.reset()}")
            return
        

    if os.path.exists(modName):
        print(f"{cores.colorize(cores.red)}There is already a project or folder with that name, delete it or choose another name{cores.reset()}")
        return
    

    createProject(modName, opcionais["framework"], opcionais["mods_path"])

    
    os.makedirs(modName)
    setFrameworks(opcionais["framework"])
    
    contents_extra=ExtraContents(opcionais, modName)    
    
    contents_extra.saveEntry()
    contents_extra.saveMain(author=author, version=version, description=description)
    
    print(f"{cores.colorize(cores.green)}Projeto criado com sucesso!{cores.reset()}")