"""
This script executed by the user selecting the 'Import Character Skin' menu option from either the File menu or the Content Browser context menu (right-clicking in empty space)
It handles the retrieval of the texture image file (and path), retrieval of UE4 destination path, finally executing the import logic.
"""

import unreal, json, os, sys, importlib
import CustomImporter.CustomImporterFunctions as CustomImporterFunctions
import CustomImporter.ImporterQtFunctions as ImporterQtFunctions

def openImportWindow():
    unreal.log('openImportWindow')
    CustomImporterFunctions.assetImportType = 'CharacterSkins'
    CustomImporterFunctions.initialBrowserDir = r'D:\ITOYS\Resources\Art\Characters'
    importlib.reload(ImporterQtFunctions)

    # Start the GUI
    main_window = ImporterQtFunctions.OpenImportWindow()
    main_window.show()
    unreal.parent_external_window_to_slate(main_window.winId())