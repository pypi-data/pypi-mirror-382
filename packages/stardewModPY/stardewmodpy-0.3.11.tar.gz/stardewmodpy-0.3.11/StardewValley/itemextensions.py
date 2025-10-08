from .contentpatcher import ContentPatcher
from .manifest import Manifest

class ItemExtensions(ContentPatcher):
    def __init__(self, manifest:Manifest):
        super().__init__(manifest=manifest)

        self.Manifest.ContentPackFor={
            "UniqueID": "mistyspring.ItemExtensions"
        }

        self.Manifest.Dependencies=[
            {
                "UniqueID": "Pathoschild.ContentPatcher",
                "IsRequired": True
            }
        ]