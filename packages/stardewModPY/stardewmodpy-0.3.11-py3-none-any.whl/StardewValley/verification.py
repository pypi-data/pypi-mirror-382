import os
import re
import platform
if platform.system() == 'Windows':
    import winreg

class steamLoad():
    def __init__(self) -> None:
        self.system = platform.system()

    def get_steam_install_path(self):
        if self.system == 'Windows':
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
                steam_path, _ = winreg.QueryValueEx(key, "SteamPath")
                winreg.CloseKey(key)
                return steam_path
            except FileNotFoundError:
                return None
        else:
            possible_paths = [
                os.path.expanduser("~/.steam/steam"),
                os.path.expanduser("~/.local/share/Steam"),
                os.path.expanduser("~/.steam"),
                os.path.expanduser("~/.var/app/com.valvesoftware.Steam/.local/share/Steam")
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    return path
            return None

    def get_steam_library_folders(self, steam_path):
        library_folders = [steam_path]  # Inclui a pasta padrão do Steam
        library_folders_file = os.path.join(steam_path, 'steamapps', 'libraryfolders.vdf')
        with open(library_folders_file, 'r') as file:
            content = file.read()
        
        # Corrige o parser para diferentes formatações de libraryfolders.vdf
        pattern = re.compile(r'"path"\s+"([^"]+)"')
        matches = pattern.findall(content)
        for match in matches:
            library_folders.append(match.replace('\\\\', '\\'))  # Corrige as barras invertidas
        
        return library_folders

    def get_game_installation_path(self, steam_path, appid):
        library_folders = self.get_steam_library_folders(steam_path)
        for library in library_folders:
            manifest_file = os.path.join(library, 'steamapps', f'appmanifest_{appid}.acf')
            if os.path.exists(manifest_file):
                with open(manifest_file, 'r') as file:
                    content = file.read()
                install_dir_pattern = re.compile(r'"installdir"\s*"\s*(.*?)\s*"')
                match = install_dir_pattern.search(content)
                if match:
                    return os.path.join(library, 'steamapps', 'common', match.group(1))
        return None
    def verify(self):
        steam_path = self.get_steam_install_path()
        if not steam_path:
            return '-1'
        
        appid = '413150'  # APPID do Stardew Valley
        game_path = self.get_game_installation_path(steam_path, appid)
        if game_path:
            return game_path
        else:
            return '0'