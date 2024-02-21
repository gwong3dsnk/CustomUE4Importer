"""
This script executed by the user selecting the 'Import Weapon Skin' menu option from either the File menu or the Content Browser context menu (right-clicking in empty space)
It handles the retrieval of the texture image file (and path), retrieval of UE4 destination path, finally executing the import logic.
"""

import unreal, json, os, importlib
import CustomImporter.CustomImporterFunctions as CustomImporterFunctions
import CustomImporter.ImporterQtFunctions as ImporterQtFunctions

def openImportWindow():
    CustomImporterFunctions.assetImportType = 'VehicleSkins'
    CustomImporterFunctions.initialBrowserDir = r'D:\ITOYS\Resources\Art\Vehicles'
    importlib.reload(ImporterQtFunctions)

    # Start the GUI
    main_window = ImporterQtFunctions.OpenImportWindow()
    main_window.show()
    unreal.parent_external_window_to_slate(main_window.winId())

def getVehicleClassTokenName(vehicleClass):
    if vehicleClass == 'Tank':
        vehicleBaseFolderName = 'Tanks'
    elif vehicleClass == 'Heli':
        vehicleBaseFolderName = 'Helicopters'
    elif vehicleClass == 'Ship':
        vehicleBaseFolderName = 'Ships'
    elif vehicleClass == 'Util':
        vehicleBaseFolderName = 'Utility'
    else:
        vehicleBaseFolderName = 'Unknown'

    return vehicleBaseFolderName

def prepareVehMaterialInstNameAndLists(nameList, folderList):
    matInstNames = []
    allTextureSets = []
    assetSkinIDs = []
    construcedMatInstNames = []
    uniqueSkinID = []

    for name in nameList:
        textureSuffix = name.split('_')[5] # T_Heli_Apache_RTYE_Hyper_BC would return BC
        if textureSuffix == 'BC' or textureSuffix == 'MRO' or textureSuffix == 'N': # T_Tank_T90_RTYE_Risen_KitAtlas_BC would return KitAtlas.  Need BC
            replacePrefix = name.replace('T_', 'MI_')
            if textureSuffix == 'BC':
                replaceSuffix = replacePrefix.replace('_BC', '_Base')
            construcedMatInstNames.append(replaceSuffix)
        else:
            textureSuffix = name.split('_')[6]
            replacePrefix = name.replace('T_', 'MI_')
            if textureSuffix == 'BC':
                replaceSuffix = replacePrefix.replace('_BC', '')
            construcedMatInstNames.append(replaceSuffix)

        # Remove the texture suffix, what remains is a string ID that will be used to ID the texture set. Add to new list.
        if textureSuffix == 'BC':
            skinID = name.replace('_BC', '')
        elif textureSuffix == 'MRO':
            skinID = name.replace('_MRO', '')
        elif textureSuffix == 'N':
            skinID = name.replace('_N', '')
        assetSkinIDs.append(skinID)

    for name in construcedMatInstNames:
        if name not in matInstNames:
            matInstNames.append(name) 

    for skinID in assetSkinIDs:
        if skinID not in uniqueSkinID:
            uniqueSkinID.append(skinID)

    for uniqueID in uniqueSkinID: # uniqueID example - T_Heli_Apache_RTYE_Hyper
        skinTextureSet = []
        uniqueIDSplit = uniqueID.split('_') # [T, Heli, Apache, RTYE, Hyper]
        uniqueIDLen = len(uniqueIDSplit) + 1 # 6
        for uasset in folderList: # uasset example - /Game/Art/Vehicles/Helicopters/Apache/Epic/T_Heli_Apache_RTYE_Hyper_BC.T_Heli_Apache_RTYE_Hyper_BC
            uassetSplit = uasset.split('.')[1] # T_Heli_Apache_RTYE_Hyper_BC
            uassetSecondSplit = uassetSplit.split('_') # [T, Heli, Apache, RTYE, Hyper, BC]
            uassetLen = len(uassetSecondSplit) # 6
            if uniqueID in uasset:
                if uasset in skinTextureSet:
                    continue
                else:
                    if uniqueIDLen == uassetLen:
                        skinTextureSet.append(uasset)
        allTextureSets.append(skinTextureSet)

    return matInstNames, allTextureSets