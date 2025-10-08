# StardewModPY

## 🌍 Other languages

- 🇬🇧 English (you are here)
- 🇧🇷 [Português](README.pt.md)

**StardewModPY** is a Python library designed to simplify the creation and manipulation of content patch files (mods) for the game **Stardew Valley**.

## Installation

You can install the library via pip:

```bash
pip install StardewModPY
```

## 1. Creating a New Project

After installing StardewModPY, you can easily create a new mod project using the following command:

```bash
sdvpy create nameMod nameAuthor 0.0.1 "Mod Description"
```

**File: ModEntry.py**

```python
from StardewValley import Manifest
from StardewValley.helper import Helper

class ModEntry(Helper):
    def __init__(self):
        super().__init__(Manifest(
            "nameMod", "nameAuthor", "0.0.1", "Mod Description", "nameAuthor.nameMod", ContentPackFor={
                "UniqueID": "Pathoschild.ContentPatcher"
            }
        ))
        self.contents()

    def contents(self):
        ...
```

**File: main.py**

```python
from ModEntry import ModEntry

mod=ModEntry()
mod.write()
```



## Compiling the Mod

To compile the mod, simply run:

```bash
sdvpy run
```


> We will continue improving the library's documentation over time. We also recommend checking the Stardew Valley wiki to find accurate information about the game data you want to modify. [Documentation](http://stardewmodpy.kya.app.br/)