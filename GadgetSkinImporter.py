"""
This script executed by the user selecting the 'Import Gadget Skin' menu option from either the File menu or the Content Browser context menu (right-clicking in empty space)
It handles the retrieval of the texture image file (and path), retrieval of UE4 destination path, finally executing the import logic.
"""

import unreal, importlib
import CustomImporter.CustomImporterFunctions as CustomImporterFunctions
import CustomImporter.ImporterQtFunctions as ImporterQtFunctions

def openImportWindow():
    CustomImporterFunctions.assetImportType = 'GadgetSkins'
    CustomImporterFunctions.initialBrowserDir = r'D:\ITOYS\Resources\Art\Gadgets'
    importlib.reload(ImporterQtFunctions)

    # Start the GUI
    main_window = ImporterQtFunctions.OpenImportWindow()
    main_window.show()
    unreal.parent_external_window_to_slate(main_window.winId())