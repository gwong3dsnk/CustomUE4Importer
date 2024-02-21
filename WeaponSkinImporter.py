"""
This script executed by the user selecting the 'Import Weapon Skin' menu option from either the File menu or the Content Browser context menu (right-clicking in empty space)
It handles the retrieval of the texture image file (and path), retrieval of UE4 destination path, finally executing the import logic.
"""

import unreal, json, os, importlib
import CustomImporter.CustomImporterFunctions as CustomImporterFunctions
import CustomImporter.ImporterQtFunctions as ImporterQtFunctions

def openImportWindow():
    CustomImporterFunctions.assetImportType = 'WeaponSkins'
    CustomImporterFunctions.initialBrowserDir = r'D:\ITOYS\Resources\Art\Weapons'
    importlib.reload(ImporterQtFunctions)

    # Start the GUI
    main_window = ImporterQtFunctions.OpenImportWindow()
    main_window.show()
    unreal.parent_external_window_to_slate(main_window.winId())

def prepareWpnMaterialInstNameAndLists(nameList, folderList):
    skinNames = []
    matInstNames = []
    allTextureSets = []

    for name in nameList:
        skinName = name.split('_')[4] # T_SMG_GabeUMP_RTYE_GabeGreySlush_BC would get GabeGraySlush

        if skinName not in skinNames: # Extract just the skin name and add to a new list.
            skinNames.append(skinName)

            # Construct the name to use when creating the MI uasset and adding to a new list.
            replacePrefix = name.replace('T_', 'MI_')
            if name.endswith('_BC'):
                replaceSuffix = replacePrefix.replace('_BC','')
            elif name.endswith('_MRO'):
                replaceSuffix = replacePrefix.replace('_MRO','')
            elif name.endswith('_N'):
                replaceSuffix = replacePrefix.replace('_N','')
            matInstNames.append(replaceSuffix)

    # Find other textures using the same skin name from folderList and isolate them into skinTextureSet list.  Then append the skinTextureSet list to the allTextureSets list.
    # Each nested array in allTextureSets list is a texture set for that specific skin.
    for skinName in skinNames:
        skinTextureSet = []
        for uasset in folderList:
            if skinName in uasset:
                skinTextureSet.append(uasset)
        allTextureSets.append(skinTextureSet)

    return matInstNames, allTextureSets