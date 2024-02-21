"""
Tool: UE4 Custom Importer
Author: Gabe Wong

This script contains global functions that are used by the various FBX and Skin Importer files.
"""

import unreal, platform, os, json, importlib
import CustomImporter.CharacterFBXImporter as CharacterFBXImporter
import CustomImporter.CharacterSkinImporter as CharacterSkinImporter
import CustomImporter.WeaponFBXImporter as WeaponFBXImporter
import CustomImporter.WeaponSkinImporter as WeaponSkinImporter
import CustomImporter.GadgetFBXImporter as GadgetFBXImporter
import CustomImporter.GadgetSkinImporter as GadgetSkinImporter
import CustomImporter.VehicleFBXImporter as VehicleFBXImporter
import CustomImporter.VehicleSkinImporter as VehicleSkinImporter
import CustomImporter.UITextureImporter as UITextureImporter

# Global Variables
assetImportType = ''
initialBrowserDir = ''
ue4PathError = []

def checkOS(assetType):
    if platform.system() == 'Windows':
        if assetType == 'Characters':
            importlib.reload(CharacterFBXImporter)
            CharacterFBXImporter.openImportWindow()
        elif assetType == 'CharacterSkins':
            unreal.log('CharacterSkin type detected.')
            importlib.reload(CharacterSkinImporter)
            CharacterSkinImporter.openImportWindow()
        elif assetType == 'Weapons':
            importlib.reload(WeaponFBXImporter)
            WeaponFBXImporter.openImportWindow()
        elif assetType == 'WeaponSkins':
            importlib.reload(WeaponSkinImporter)
            WeaponSkinImporter.openImportWindow()
        elif assetType == 'Gadgets':
            importlib.reload(GadgetFBXImporter)
            GadgetFBXImporter.openImportWindow()
        elif assetType == 'GadgetSkins':
            importlib.reload(GadgetSkinImporter)
            GadgetSkinImporter.openImportWindow()
        elif assetType == 'Vehicles':
            importlib.reload(VehicleFBXImporter)
            VehicleFBXImporter.openImportWindow()
        elif assetType == 'VehicleSkins':
            importlib.reload(VehicleSkinImporter)
            VehicleSkinImporter.openImportWindow()
        elif assetType == 'UITextures':
            importlib.reload(UITextureImporter)
            UITextureImporter.openImportWindow()
    else:
        unreal.log_error('This tool cannot be used on this operating system.  This tool relies on modules that only support Windows at this time.')
        unreal.log_error('Your current operating system is - %s' % (platform.system()))

def verifyAssetSourcePath(sourceFilePath, ue4_destinationPath, assetType):
    # Validates if asset file path is correct or not
    isSourcePathCorrect = False
    characterPathTokens = ['Bodies', 'Backpacks', 'Gloves']
    weaponPathTokens = ['Base', 'Barrels', 'Sights', 'Foregrips', 'Charms', "Lasersights", "Bipods", "Projectiles"]
    gadgetPathTokens = ['Explosives', 'Melee', 'SupportHeavy', 'SupportMedium', 'Parachutes']
    vehiclePathTokens = ['Tanks', 'Helicopters', 'Ships', 'Utility']
    uiTexturePathTokens = ['Avatars', 'Banners', 'Frames', 'Thumbnails', "MetaArt"]

    if 'Resources' in sourceFilePath:
        if assetType == 'Characters' and any(token in sourceFilePath for token in characterPathTokens):
            isSourcePathCorrect = True
            return isSourcePathCorrect
        elif assetType == 'CharacterSkins' and any(token in sourceFilePath for token in characterPathTokens):
            isSourcePathCorrect = True
            return isSourcePathCorrect
        elif assetType == 'Weapons' and any(token in sourceFilePath for token in weaponPathTokens):
            isSourcePathCorrect = True
            return isSourcePathCorrect
        elif assetType == 'WeaponSkins' and 'Base' in sourceFilePath:
            isSourcePathCorrect = True
            return isSourcePathCorrect
        elif (assetType == 'Gadgets' or assetType == 'GadgetSkins') and any(token in sourceFilePath for token in gadgetPathTokens):
            isSourcePathCorrect = True
            return isSourcePathCorrect
        elif (assetType == 'Vehicles' or assetType == 'VehicleSkins') and any(token in sourceFilePath for token in vehiclePathTokens):
            isSourcePathCorrect = True
            return isSourcePathCorrect
        elif assetType == 'UITextures' and any(token in sourceFilePath for token in uiTexturePathTokens):
            isSourcePathCorrect = True
            return isSourcePathCorrect
        else:
            if 'Developers' in ue4_destinationPath:
                isSourcePathCorrect = True
                return isSourcePathCorrect 
            else:
                return isSourcePathCorrect
    else:
        if 'Developers' in ue4_destinationPath:
            isSourcePathCorrect = True
            return isSourcePathCorrect 
        else:
            return isSourcePathCorrect

def verifyUE4Path(sourceFilePath, ue4_destinationPath, assetType):
    # Validates if FBX destination path in UE4 project is correct or not
    editorAssetLib = unreal.EditorAssetLibrary()
    isUE4PathCorrect = True

    # Get asset name details
    assetNamePreConfigure, assetNameReplacePrefix, assetName, assetNameIfExist, ue4AssetName = extractAssetName(sourceFilePath)

    if assetType != 'Characters':
        # Construct the UE4 Destination Directory for the asset.
        print("sourceFilePath - " + sourceFilePath)
        sourceFilePathReplace = sourceFilePath.replace("D:/ITOYS/Resources/", "")
        print("sourceFilePathReplace - " + sourceFilePathReplace)
        sourceFilePathSplit = sourceFilePathReplace.split("/")
        print("sourceFilePathSplit - " + str(sourceFilePathSplit))
        fileNameSplitIndex = len(sourceFilePathSplit) - 1
        ue4PathSegment = sourceFilePathReplace.replace(sourceFilePathSplit[fileNameSplitIndex], "")
        print("ue4PathSegment - " + ue4PathSegment)

    if assetType == 'UITextures':
        if "Thumbnail" in sourceFilePath or "MetaArt" in sourceFilePath:
            # Thumbnails do want to respect the entire path and retain the Seasonal directories which is lost during the above if statement.
            expectedUE4AssetPath = "/Game/" + ue4PathSegment
        else:
            # Player profile textures don't want to create an asset-specific folder, but rather, dump everything into the Seasonal root.
            # So here, we remove the RTY_<PlayerProfileName> from the path.
            ue4PathSegmentSplit = ue4PathSegment.split("/")
            print("ue4PathSegmentSplit - " + str(ue4PathSegmentSplit))
            fileNameSplitIndexUI = len(ue4PathSegmentSplit) - 1
            # ue4PathSegment ends with a '/' at the end.  After splitting, it causes the last element in the list to be empty - ''.
            # Get last element, if empty, reduce index by 1 to get the filename string to strip then manually add in the final '/' for ue4PathSegmentUI
            if ue4PathSegmentSplit[fileNameSplitIndexUI] == '':
                fileNameSplitIndexUI -= 1
            ue4PathSegmentUI = ue4PathSegment.replace(ue4PathSegmentSplit[fileNameSplitIndexUI] + '/', "")
            print("ue4PathSegmentUI - " + ue4PathSegmentUI)
            expectedUE4AssetPath = "/Game/" + ue4PathSegmentUI
            print("expectedUE4AssetPath - " + expectedUE4AssetPath)
    elif assetType == 'Characters':
        expectedUE4AssetPath = CharacterFBXImporter.generateUE4Path(sourceFilePath, assetName)
    elif assetType == 'CharacterSkins':
        splitSourceFilePath = sourceFilePath.split('/')[-3]
        if "Backpacks" in ue4PathSegment:
            expectedUE4AssetPath = '/Game/Art/Characters/Backpacks/%s_Backpack/%s/' % (splitSourceFilePath, sourceFilePathSplit[-2])
        else:
            expectedUE4AssetPath = ""
            isUE4PathCorrect = False
            return isUE4PathCorrect, expectedUE4AssetPath
    else:
        expectedUE4AssetPath = "/Game/" + ue4PathSegment

    if 'Developers' in ue4_destinationPath:
        return isUE4PathCorrect, ue4_destinationPath
    else:
        fullUE4Path = expectedUE4AssetPath + '/' + assetNameIfExist + '.' + assetNameIfExist
        doesUassetExist = editorAssetLib.does_asset_exist(fullUE4Path)
        if doesUassetExist:
            isUE4PathCorrect = False
            return isUE4PathCorrect, expectedUE4AssetPath
        else:
            return isUE4PathCorrect, expectedUE4AssetPath

def extractAssetName(sourceFilePath):
    assetNamePreConfigure = sourceFilePath.split("/")[-1] # i.e. SK_Beech2.fbx or T_SMG_UMP_RTYE_GreySlush_BC.tga
    if assetNamePreConfigure.endswith('fbx'):
        if assetNamePreConfigure.startswith('SK_'):
            assetNameReplacePrefix = assetNamePreConfigure.replace('SK_','') # i.e. Beech2.fbx
        elif assetNamePreConfigure.startswith('SM_'):
            assetNameReplacePrefix = assetNamePreConfigure.replace('SM_','') # i.e. Beech2.fbx
        assetName = assetNameReplacePrefix.replace('.fbx','') # i.e. Beech2
        assetNameIfExist = assetNamePreConfigure.replace('.fbx','') # i.e. SK_Beech2
        ue4AssetName = assetNamePreConfigure.replace('.fbx','') # i.e. SK_Beech2
    elif assetNamePreConfigure.endswith('png'):
        assetNameReplacePrefix = assetNamePreConfigure.replace('TX_','') # i.e. SMG_UMP_RTYE_GreySlush_BC.tga
        assetName = assetNameReplacePrefix.replace('.png','') # i.e. SMG_UMP_RTYE_GreySlush_BC
        assetNameIfExist = assetNamePreConfigure.replace('.png','') # i.e. T_SMG_UMP_RTYE_GreySlush_BC
        ue4AssetName = assetNamePreConfigure.replace('.png','')
    else: # Below is for skin textures
        assetNameReplacePrefix = assetNamePreConfigure.replace('T_','') # i.e. SMG_UMP_RTYE_GreySlush_BC.tga
        assetName = assetNameReplacePrefix.replace('.tga','') # i.e. SMG_UMP_RTYE_GreySlush_BC
        assetNameIfExist = assetNamePreConfigure.replace('.tga','') # i.e. T_SMG_UMP_RTYE_GreySlush_BC
        ue4AssetName = assetNamePreConfigure.replace('.tga','')

    return assetNamePreConfigure, assetNameReplacePrefix, assetName, assetNameIfExist, ue4AssetName

def buildImportTask(filename, destination_path, options):
    unreal.log('Generating import task...')
    task = unreal.AssetImportTask()
    task.set_editor_property('automated', True)
    task.set_editor_property('destination_name', '')
    task.set_editor_property('destination_path', destination_path)
    task.set_editor_property('filename', filename)
    task.set_editor_property('replace_existing', True)
    task.set_editor_property('save', True)
    task.set_editor_property('options', options)
    return task

def validatePaths(sourceFilePath):
    # Conducts validation to make sure that the FBX is coming from a proper directory and that it's being imported into a proper UE4 directory.
    sourceErrorMsg = ''
    ue4ErrorMsg = ''

    # Get UE4 Destination Path by calling C++ function GetContentBrowserActivePath() from ODPython
    ue4_destinationPath = unreal.ODPython.get_content_browser_active_path()

    if assetImportType == 'Characters' or assetImportType == 'CharacterSkins':
        confluencePageLink = 'https://confluence.itoys.ea.com/x/vYhM'
        correctResourcesRoot = 'D:/ITOYS/Resources/Art/Characters/'
        unknownCategories = 'body, backpack, or glove'
    elif assetImportType == 'Weapons':
        confluencePageLink = 'https://confluence.itoys.ea.com/x/8UQk'
        correctResourcesRoot = 'D:/ITOYS/Resources/Art/Weapons/'
        unknownCategories = 'base, sight, barrel, foregrip or charm'
    elif assetImportType == 'WeaponSkins':
        confluencePageLink = 'https://confluence.itoys.ea.com/x/hiZMAQ'
        correctResourcesRoot = 'D:/ITOYS/Resources/Art/Weapons/'
        unknownCategories = 'n/a'
    elif assetImportType == 'Gadgets':
        confluencePageLink = 'https://confluence.itoys.ea.com/x/NSlMAQ'
        correctResourcesRoot = 'D:/ITOYS/Resources/Art/Gadgets/'
        unknownCategories = 'legendary, explosives, melee, supportheavy, supportmedium'
    elif assetImportType == 'GadgetSkins':
        confluencePageLink = 'https://confluence.itoys.ea.com/x/0CJMAQ'
        correctResourcesRoot = 'D:/ITOYS/Resources/Art/Gadgets/'
        unknownCategories = 'n/a'
    elif assetImportType == 'Vehicles':
        confluencePageLink = 'https://confluence.itoys.ea.com/x/EYRM'
        correctResourcesRoot = 'D:/ITOYS/Resources/Art/Vehicles/'
        unknownCategories = 'tanks, ships, helicopters, utility'
    elif assetImportType == 'VehicleSkins':
        confluencePageLink = 'https://confluence.itoys.ea.com/x/EYRM'
        correctResourcesRoot = 'D:/ITOYS/Resources/Art/Vehicles/'
        unknownCategories = 'n/a'
    elif assetImportType == 'UITextures':
        confluencePageLink = 'https://confluence.itoys.ea.com/x/2yFMAQ'
        correctResourcesRoot = 'D:/ITOYS/Resources/Art/UI/'
        unknownCategories = 'banner, avatar, frame, thumbnail, or metaart'
    else:
        unreal.log('No global assetImportType specified')
        confluencePageLink = ''
        correctResourcesRoot = ''
        unknownCategories = ''

    # Source file path validation
    isSourcePathCorrect = verifyAssetSourcePath(sourceFilePath, ue4_destinationPath, assetImportType)
    if isSourcePathCorrect == False:
        unreal.log_error('%s asset file is not located in the right directory.' % (assetImportType))
        unreal.log_error('It is unknown if the asset file you are importing is a %s' % (unknownCategories))
        unreal.log_error('You can only import an unknown asset file into your UE4 Developers folder.')
        unreal.log_error('Please verify that the asset file lives in the proper directory under %s, then try again.' % (correctResourcesRoot))
        unreal.log_error('View this confluence page to see the folder and file name conventions for your asset - %s' % (confluencePageLink))
        unreal.log_error('---[Import process skipped for %s]---' % (sourceFilePath))
        sourceErrorMsg = 'incorrectSourceDirectory'

    # UE4 file path validation
    isUE4PathCorrect, ue4_destinationPath = verifyUE4Path(sourceFilePath, ue4_destinationPath, assetImportType)

    if isUE4PathCorrect == False:
        if ue4_destinationPath == "":
            unreal.log_error("No support selected asset intake.  If this is in error, please reach out to gawong on Slack.")
            ue4ErrorMsg = "noSupportExists"
        else:
            unreal.log_error('The asset already exists in %s' % (ue4_destinationPath))
            unreal.log_error('Right-click on the UE4 Destination Path for this asset and select Force Reimport if you want to reimport and overwrite the existing asset.')
            unreal.log_error('---[Import process skipped for %s]---' % (sourceFilePath))
            ue4ErrorMsg = 'uassetAlreadyExists'

    return ue4_destinationPath, sourceErrorMsg, ue4ErrorMsg

def saveAssets(importedAssets):
    # Save individual uassets.  Takes in an array of strings.  Each string is full path - '/Game/... .../AssetName.AssetName'
    editorAssetLib = unreal.EditorAssetLibrary()

    for fullAssetPath in importedAssets:
        editorAssetLib.save_asset(fullAssetPath, only_if_is_dirty=True)

def saveAssetsInDirectory(ue4_destinationDirectory):
    editorAssetLib = unreal.EditorAssetLibrary()
    editorAssetLib.save_directory(ue4_destinationDirectory, only_if_is_dirty=True, recursive=False)

def setLODSettings(ue4_destinationPath, ue4AssetName, lodSettingsData):
    # Assigns the LODSettings uasset to the SK mesh LODSettings interface.
    tokenList = ['Base', 'Barrels', 'Sights', 'Foregrips', 'Bodies', 'Backpacks', 'Gloves']
    print("ue4AssetName - %s" % (ue4AssetName))

    skMeshFullUE4Path = ue4_destinationPath + ue4AssetName + '.' + ue4AssetName

    print("skMeshFullUE4Path - %s" % (skMeshFullUE4Path))
    assetRegistry = unreal.AssetRegistryHelpers.get_asset_registry()
    meshData = assetRegistry.get_asset_by_object_path(skMeshFullUE4Path)
    skMeshAsset = meshData.get_asset()

    if any(token in ue4_destinationPath for token in tokenList):
        lodSettingsAsset = lodSettingsData.get_asset()
        skMeshAsset.set_editor_property('lod_settings', lodSettingsAsset)

    return meshData

def setPhysicalMaterial(ue4_destinationPath, ue4AssetName, physicalMaterial):
    tokenList = ['Backpacks']
    skMeshFullUE4Path = ue4_destinationPath + ue4AssetName + '.' + ue4AssetName
    assetRegistry = unreal.AssetRegistryHelpers.get_asset_registry()
    meshData = assetRegistry.get_asset_by_object_path(skMeshFullUE4Path)
    skMeshAsset = meshData.get_asset()

    if any(token in ue4_destinationPath for token in tokenList):
        meshMaterials = skMeshAsset.get_editor_property('materials')
        for mat in meshMaterials:
            matInterface = mat.get_editor_property('material_interface')

            matInst = castAssetToType(matInterface, unreal.MaterialInstance)

            if matInst:
                unreal.log("Casting material interface to material instance - SUCCESS")
            else:
                unreal.log_error("Casting material interface to material instance - FAILED")
                break

            physicalMaterialAsset = physicalMaterial.get_asset()
            matInst.set_editor_property('phys_material', physicalMaterialAsset)

def startMaterialCreation(ue4_destinationPath, meshData, assetType, projectileTextureList):
    materialList = []
    materialEditLib = unreal.MaterialEditingLibrary()
    editorAssetLib = unreal.EditorAssetLibrary()
    assetTools = unreal.AssetToolsHelpers.get_asset_tools()
    assetRegistry = unreal.AssetRegistryHelpers.get_asset_registry()
    allAssets = unreal.EditorAssetLibrary.list_assets(ue4_destinationPath, recursive=False, include_folder=False)
    jsonFilePath = os.path.join( os.path.dirname( __file__ ), '../CustomImporter/itoys_importOptionsConfig.json' )
    assetClass = meshData.get_editor_property('asset_class')
    meshAsset = meshData.get_asset()

    print('meshData - %s' % (meshData))
    print('assetClass - %s' % (assetClass))

    if assetClass == 'StaticMesh':
        meshMaterials = meshAsset.get_editor_property('static_materials')
    else:
        meshMaterials = meshAsset.get_editor_property('materials')

    print("skMeshMaterials - %s" % (meshMaterials))
    print("allAssets - %s" % (allAssets))

    with open(jsonFilePath) as f:
        data = json.load(f)
        optionData = data['materialOptions']

        for mat in meshMaterials:
            matSlotName = mat.get_editor_property('material_slot_name')
            matSlotNameStr = str(matSlotName)
            matFullPath = ue4_destinationPath + '%s.%s' % (matSlotNameStr, matSlotNameStr)

            print("matSlotName - %s" % (matSlotName))
            print("matSlotNameStr - %s" % (matSlotNameStr))
            print("matFullPath - %s" % (matFullPath))

            # Check to see if the material already exists or not.
            if editorAssetLib.does_asset_exist(matFullPath):
                unreal.log("Asset already exists")
                matInstData = assetRegistry.get_asset_by_object_path(matFullPath)
                matInstAsset = matInstData.get_asset()
                if assetClass == 'StaticMesh':
                    newMaterial = unreal.StaticMaterial(material_interface=matInstAsset, material_slot_name=matSlotName, uv_channel_data=unreal.MeshUVChannelInfo())
                    materialList.append(newMaterial)
                else:
                    newMaterial = unreal.SkeletalMaterial(material_interface=matInstAsset, material_slot_name=matSlotName, uv_channel_data=unreal.MeshUVChannelInfo())
                    materialList.append(newMaterial)
                continue

            # Check if material slot name is of type that needs to reuse existing mat instance. If so, get the existing mat inst and add to list, then continue to next for loop item.
            if assetType == 'Weapons':
                if '_Bullet' in matSlotNameStr and 'Base' in ue4_destinationPath and '_Casing' not in matSlotNameStr:
                    matInstData = unreal.AssetData(optionData['bulletMaterial'])
                    matInstAsset = matInstData.get_asset()
                    for element in data:
                        if 'materialOptions' in element:
                            newSkeletalMaterial = unreal.SkeletalMaterial(material_interface=matInstAsset, material_slot_name=matSlotName, uv_channel_data=unreal.MeshUVChannelInfo())
                            materialList.append(newSkeletalMaterial)
                    continue
                elif '_Glass' in matSlotNameStr and 'Sight' in ue4_destinationPath:
                    matInstData = unreal.AssetData(optionData['sightGlassMaterial'])
                    matInstAsset = matInstData.get_asset()
                    for element in data:
                        if 'materialOptions' in element:
                            newSkeletalMaterial = unreal.SkeletalMaterial(material_interface=matInstAsset, material_slot_name=matSlotName, uv_channel_data=unreal.MeshUVChannelInfo())
                            materialList.append(newSkeletalMaterial)
                    continue

            textureSet, textureSlotName = generateTextureSetList(matSlotNameStr, assetType, ue4_destinationPath, editorAssetLib, projectileTextureList)
            print('textureSet - %s' % (textureSet))

            # Create the material instances based on any existing tokens
            if matSlotNameStr.endswith('_TRN') or '_TRN_' in matSlotNameStr:
                print('Material Slot is Translucent with NO Reflection')
                newMatInst = assetTools.create_asset(matSlotName, ue4_destinationPath, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
                for element in data:
                    if 'materialOptions' in element:
                        parentMaterial = unreal.EditorAssetLibrary.find_asset_data(optionData['translucentMaterial'])
                materialList = setupMatInst(newMatInst, parentMaterial, matSlotName, materialList, textureSlotName, assetClass, assetType, textureSet)
            elif matSlotNameStr.endswith('_TRR') or '_TRR_' in matSlotNameStr:
                if assetType == "Characters":
                   print('Material Slot is Translucent with Reflection for Characters')
                   newMatInst = assetTools.create_asset(matSlotName, ue4_destinationPath, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
                   for element in data:
                       if 'materialOptions' in element:
                           parentMaterial = unreal.EditorAssetLibrary.find_asset_data(optionData['translucentReflectChaMaterial'])
                else:
                    print('Material Slot is Translucent with Reflection')
                    newMatInst = assetTools.create_asset(matSlotName, ue4_destinationPath, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
                    for element in data:
                        if 'materialOptions' in element:
                            parentMaterial = unreal.EditorAssetLibrary.find_asset_data(optionData['translucentReflectMaterial'])
                materialList = setupMatInst(newMatInst, parentMaterial, matSlotName, materialList, textureSlotName, assetClass, assetType, textureSet)
            elif matSlotNameStr.endswith('_MSK') or '_MSK_' in matSlotNameStr:
                print('Material Slot is Masked')
                newMatInst = assetTools.create_asset(matSlotName, ue4_destinationPath, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
                for element in data:
                    if 'materialOptions' in element:
                        parentMaterial = unreal.EditorAssetLibrary.find_asset_data(optionData['maskedMaterial'])
                materialList = setupMatInst(newMatInst, parentMaterial, matSlotName, materialList, textureSlotName, assetClass, assetType, textureSet)
            elif matSlotNameStr.endswith('_VCM') or '_VCM_' in matSlotNameStr:
                print('Material Slot is VertexColorMasking')
                newMatInst = assetTools.create_asset(matSlotName, ue4_destinationPath, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
                for element in data:
                    if 'materialOptions' in element:
                        parentMaterial = unreal.EditorAssetLibrary.find_asset_data(optionData['vertexColorMask'])
                materialList = setupMatInst(newMatInst, parentMaterial, matSlotName, materialList, textureSlotName, assetClass, assetType, textureSet)
            elif matSlotNameStr.endswith('_EMT') or '_EMT_' in matSlotNameStr:
                print('Material Slot is Emissive Texture')
                newMatInst = assetTools.create_asset(matSlotName, ue4_destinationPath, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
                for element in data:
                    if 'materialOptions' in element:
                        parentMaterial = unreal.EditorAssetLibrary.find_asset_data(optionData['emissiveTextureMaterial'])
                materialList = setupMatInst(newMatInst, parentMaterial, matSlotName, materialList, textureSlotName, assetClass, assetType, textureSet)
            elif matSlotNameStr.endswith('_EMC') or '_EMC_' in matSlotNameStr:
                print('Material Slot is Emissive Color')
                newMatInst = assetTools.create_asset(matSlotName, ue4_destinationPath, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
                for element in data:
                    if 'materialOptions' in element:
                        parentMaterial = unreal.EditorAssetLibrary.find_asset_data(optionData['emissiveColorMaterial'])
                materialList = setupMatInst(newMatInst, parentMaterial, matSlotName, materialList, textureSlotName, assetClass, assetType, textureSet)
            elif matSlotNameStr.endswith('_EMM') or '_EMM_' in matSlotNameStr:
                print('Material Slot is Emissive Masked')
                newMatInst = assetTools.create_asset(matSlotName, ue4_destinationPath, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
                for element in data:
                    if 'materialOptions' in element:
                        parentMaterial = unreal.EditorAssetLibrary.find_asset_data(optionData['emissiveMasked'])
                materialList = setupMatInst(newMatInst, parentMaterial, matSlotName, materialList, textureSlotName, assetClass, assetType, textureSet)
            elif matSlotNameStr.endswith('_PDY') or '_PDY_' in matSlotNameStr:
                print('Material Slot is PannerDynamic')
                newMatInst = assetTools.create_asset(matSlotName, ue4_destinationPath, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
                for element in data:
                    if 'materialOptions' in element:
                        parentMaterial = unreal.EditorAssetLibrary.find_asset_data(optionData['pannerDynMaterial'])
                materialList = setupMatInst(newMatInst, parentMaterial, matSlotName, materialList, textureSlotName, assetClass, assetType, textureSet)
            elif matSlotNameStr.endswith('_O2S') or '_O2S_' in matSlotNameStr:
                print('Material Slot is Opaque Two Sided')
                newMatInst = assetTools.create_asset(matSlotName, ue4_destinationPath, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
                for element in data:
                    if 'materialOptions' in element:
                        parentMaterial = unreal.EditorAssetLibrary.find_asset_data(optionData['opaque2SMaterial'])
                materialList = setupMatInst(newMatInst, parentMaterial, matSlotName, materialList, textureSlotName, assetClass, assetType, textureSet)
            elif matSlotNameStr.endswith('_OEM') or '_OEM_' in matSlotNameStr:
                print('Material Slot is Opaque Emissive')
                newMatInst = assetTools.create_asset(matSlotName, ue4_destinationPath, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
                for element in data:
                    if 'materialOptions' in element:
                        parentMaterial = unreal.EditorAssetLibrary.find_asset_data(optionData['opaqueEmissiveMaterial'])
                materialList = setupMatInst(newMatInst, parentMaterial, matSlotName, materialList, textureSlotName, assetClass, assetType, textureSet)
            else:
                print('Material Slot is Opaque')
                newMatInst = assetTools.create_asset(matSlotName, ue4_destinationPath, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
                for element in data:
                    if 'materialOptions' in element:
                        parentMaterial = unreal.EditorAssetLibrary.find_asset_data(optionData['opaqueMaterial'])
                materialList = setupMatInst(newMatInst, parentMaterial, matSlotName, materialList, textureSlotName, assetClass, assetType, textureSet)

    # Use the materialList to assign the instances to the proper interfaces on the meshAsset
    print('Final Material List - ' + str(materialList))
    if assetClass == 'StaticMesh':
        meshAsset.set_editor_property('static_materials', materialList)
    else:
        meshAsset.set_editor_property('materials', materialList)

def setupMatInst(newMatInst, parentMaterial, matSlotName, materialList, textureSlotName, assetClass, assetType, textureSet):
    materialEditLib = unreal.MaterialEditingLibrary()

    # Set material instance parent
    materialEditLib.set_material_instance_parent(newMatInst, parentMaterial.get_asset())

    # Assign found textures to the proper texture sample interfaces in the material instance.
    if textureSet:
        for texture in textureSet:
            textureData = unreal.AssetData(texture)
            textureAsset = textureData.get_asset()
            print('textureAsset - ' + str(textureAsset))

            if texture.endswith('_BC'):
                materialEditLib.set_material_instance_texture_parameter_value(newMatInst, 'T_BaseColor', textureAsset)
            elif texture.endswith('_MRO'):
                materialEditLib.set_material_instance_texture_parameter_value(newMatInst, 'T_MRO', textureAsset)
            elif texture.endswith('_N'):
                materialEditLib.set_material_instance_texture_parameter_value(newMatInst, 'T_Normal', textureAsset)

    if assetClass == 'StaticMesh':
        newStaticMaterial = unreal.StaticMaterial(material_interface=newMatInst, material_slot_name=matSlotName, uv_channel_data=unreal.MeshUVChannelInfo())
        materialList.append(newStaticMaterial)
    else:
        newSkeletalMaterial = unreal.SkeletalMaterial(material_interface=newMatInst, material_slot_name=matSlotName, uv_channel_data=unreal.MeshUVChannelInfo())
        materialList.append(newSkeletalMaterial)

    return materialList

def generateTextureSetList(matSlotNameStr, assetType, ue4_destinationPath, editorAssetLib, projectileTextureList):
    print("Start within function generateTextureSetList in CustomImporterFunctions")

    if not projectileTextureList:
        # To construct texture name, use material slot name.  Start with replacing the MI_ prefix with T_. 
        texturePrefixSwap = matSlotNameStr.replace('MI_', 'T_')

        # Detect if blend type token exists and if so, remove it.
        if matSlotNameStr.endswith('_TRN') or '_TRN_' in matSlotNameStr:
            textureTokenReplace = texturePrefixSwap.replace('_TRN', '')
        elif matSlotNameStr.endswith('_TRR') or '_TRR_' in matSlotNameStr:
            textureTokenReplace = texturePrefixSwap.replace('_TRR', '')
        elif matSlotNameStr.endswith('_MSK') or '_MSK_' in matSlotNameStr:
            textureTokenReplace = texturePrefixSwap.replace('_MSK', '')
        elif matSlotNameStr.endswith('_VCM') or '_VCM_' in matSlotNameStr:
            textureTokenReplace = texturePrefixSwap.replace('_VCM', '')
        elif matSlotNameStr.endswith('_EMC') or '_EMC_' in matSlotNameStr:
            textureTokenReplace = texturePrefixSwap.replace('_EMC', '')
        elif matSlotNameStr.endswith('_EMT') or '_EMT_' in matSlotNameStr:
            textureTokenReplace = texturePrefixSwap.replace('_EMT', '')
        elif matSlotNameStr.endswith('_EMM') or '_EMM_' in matSlotNameStr:
            textureTokenReplace = texturePrefixSwap.replace('_EMM', '')
        elif matSlotNameStr.endswith('_PDY') or '_PDY_' in matSlotNameStr:
            textureTokenReplace = texturePrefixSwap.replace('_PDY', '')
        elif matSlotNameStr.endswith('_O2S') or '_O2S_' in matSlotNameStr:
            textureTokenReplace = texturePrefixSwap.replace('_O2S', '')
        elif matSlotNameStr.endswith('_OEM') or '_OEM_' in matSlotNameStr:
            textureTokenReplace = texturePrefixSwap.replace('_OEM', '')
        else:
            textureTokenReplace = texturePrefixSwap

        print('textureTokenReplace - %s' % (textureTokenReplace))

        # Get the slot name token.
        materialNameSplit = matSlotNameStr.split('_')
        materialNameLen = len(materialNameSplit)
        slotNameToken = materialNameSplit[materialNameLen-1]
        print('materialNameSplit - %s' % (materialNameSplit))
        print('materialNameLen - %s' % (materialNameLen))
        print('slotNameToken - %s' % (slotNameToken))

        # Charm material names could be missing a slot name and skin name and just have the RTY token.
        matBlendTokenList = ['RTY', 'TRN', 'MSK', 'VCM', 'EMC', 'EMT', 'EMM', 'PDY', 'O2S', 'OEM']
        if any(token in slotNameToken for token in matBlendTokenList):
            textureSlotName = ''
        else:
            textureSlotName = slotNameToken

        print('TextureSlotName - %s ' % (textureSlotName))

        # If the slot name is Base, use the default texture set.  If it's something else, use the slot name to search the texture name for a match.
        if assetType == 'Weapons' or assetType == 'Vehicles':
            if matSlotNameStr.endswith('_Base'):
                textureBaseName = textureTokenReplace.replace('_Base', '')
            elif matSlotNameStr.endswith('_Reticle') and '_RTYL_' in matSlotNameStr:
                textureBaseName = textureTokenReplace
            elif matSlotNameStr.endswith('_Reticle'):
                textureBaseName = textureTokenReplace.replace('_Reticle', '')
            elif matSlotNameStr.endswith('_Treads01'):
                textureBaseName = textureTokenReplace.replace('_Treads01', '_Treads')
            elif matSlotNameStr.endswith('_Treads02'):
                textureBaseName = textureTokenReplace.replace('_Treads02', '_Treads')
            else:
                textureBaseName = textureTokenReplace
        elif assetType == 'Characters' or assetType == 'Gadgets':
            textureBaseName = textureTokenReplace

        print('TextureBaseName - %s' % (textureBaseName))

        # Construct the full UE4 paths to the BC, MRO, N textures.
        texFullNameBC = textureBaseName + '_BC.' + textureBaseName + '_BC'
        if '_Destr' in textureBaseName:
            destrBaseColor = textureBaseName.replace('_Destr', '')
            texFullNameMRO = destrBaseColor + '_MRO.' + destrBaseColor + '_MRO'
            texFullNameN = destrBaseColor + '_N.' + destrBaseColor + '_N'
        else:
            texFullNameMRO = textureBaseName + '_MRO.' + textureBaseName + '_MRO'
            texFullNameN = textureBaseName + '_N.' + textureBaseName + '_N'

        texFullPathBC = ue4_destinationPath + texFullNameBC
        print('texFullPathBC - %s' % (texFullPathBC))
        texFullPathMRO = ue4_destinationPath + texFullNameMRO
        print('texFullPathMRO - %s' % (texFullPathMRO))
        texFullPathN = ue4_destinationPath + texFullNameN
        print('texFullPathN - %s' % (texFullPathN))
    else:
        for texture in projectileTextureList:
            if texture.endswith("_BC"):
                texFullPathBC = texture
            elif texture.endswith("_MRO"):
                texFullPathMRO = texture
            elif texture.endswith("_N"):
                texFullPathN = texture
        textureSlotName = ''

    # Use full UE4 path to see if the textures exist.  The ones that do exist get added to the textureSet list.
    if editorAssetLib.does_asset_exist(texFullPathBC) and editorAssetLib.does_asset_exist(texFullPathMRO) and editorAssetLib.does_asset_exist(texFullPathN):
        textureSet = [texFullPathBC, texFullPathMRO, texFullPathN]
    elif editorAssetLib.does_asset_exist(texFullPathBC) and editorAssetLib.does_asset_exist(texFullPathMRO) and not editorAssetLib.does_asset_exist(texFullPathN):
        textureSet = [texFullPathBC, texFullPathMRO]
    elif editorAssetLib.does_asset_exist(texFullPathBC) and not editorAssetLib.does_asset_exist(texFullPathMRO) and editorAssetLib.does_asset_exist(texFullPathN):
        textureSet = [texFullPathBC, texFullPathN]
    elif editorAssetLib.does_asset_exist(texFullPathBC) and not editorAssetLib.does_asset_exist(texFullPathMRO) and not editorAssetLib.does_asset_exist(texFullPathN):
        textureSet = [texFullPathBC]
    else:
        textureSet = []

    print("End within function generateTextureSetList in CustomImporterFunctions")
    return textureSet, textureSlotName

def querySingleImportOptions(optionSection, optionKey):
    jsonFilePath = os.path.join( os.path.dirname( __file__ ), '../CustomImporter/itoys_importOptionsConfig.json' )
    with open(jsonFilePath) as f:
        data = json.load(f)
        optionData = data[optionSection]

        for element in data:
            if optionSection in element:
                optionValue = unreal.AssetData(optionData[optionKey])

    return optionValue

def castAssetToType(objectToCast, objectClass):
    try:
        return objectClass.cast(objectToCast)
    except:
        return None

def setCMSInclusionTag(assetPath):
    unreal.ITContentManagementBPLibrary.mark_asset_should_have_content_definition(assetPath, True)