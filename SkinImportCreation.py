"""
Whenever the user is importing skin textures, these are the functions that are called to conduct the actual import logic
and to execute the post-import logic to handle skin material creation
"""

import unreal, json, os
import CustomImporter.VehicleSkinImporter as VehicleSkinImporter
import CustomImporter.WeaponSkinImporter as WeaponSkinImporter
import CustomImporter.UITextureImporter as UITextureImporter
import CustomImporter.CustomImporterFunctions as CustomImporterFunctions

def executeAssetImport(sourceFilePath, ue4_destinationPath, filePostImportStatus):
    # Execute Import Logic
    editorAssetLib = unreal.EditorAssetLibrary()
    unreal.log('---[Starting import process for %s]---' % (sourceFilePath))

    # Check if the ue4 destination directory is valid, if not, create it.
    isUE4DirectoryValid = editorAssetLib.does_directory_exist(ue4_destinationPath)
    if isUE4DirectoryValid == False:
        editorAssetLib.make_directory(ue4_destinationPath)

    if filePostImportStatus == 'PENDING IMPORT' or filePostImportStatus == 'PENDING REIMPORT':
        assetTools = unreal.AssetToolsHelpers.get_asset_tools()
        assetImportTask = unreal.AssetImportTask()
        assetImportTask.set_editor_property('filename', sourceFilePath)
        assetImportTask.set_editor_property('automated', True)
        assetImportTask.set_editor_property('replace_existing', True)
        assetImportTask.set_editor_property('replace_existing_settings', False)
        assetImportTask.set_editor_property('destination_path', ue4_destinationPath)
        assetTools.import_asset_tasks([assetImportTask])
        unreal.log('---[Succesfully imported %s.  Uassets can be found here: %s]---' % (sourceFilePath, ue4_destinationPath))

def setupSkinMaterials(ue4DestinationFolderList, assetNameList, assetType):
    rtyuFolderList = []
    rtyrFolderList = []
    rtyeFolderList = []
    rtyuNameList = []
    rtyrNameList = []
    rtyeNameList = []
    assetEditSubsys = unreal.AssetEditorSubsystem()

    print("assetNameList: " + str(assetNameList))
    print("ue4DestinationFolderList: " + str(ue4DestinationFolderList))

    # Start by isolating textures by their rarity tier into their own rarity lists.  Do it for both the asset name and full uasset path
    for uasset in assetNameList:
        # Uncommon/Rare will share their own unique MRO, import a new BC, reuse Common N
        if 'RTYU' in uasset:
            uassetIndex = assetNameList.index(uasset)
            rtyuNameList.append(uasset)
            rtyuFolderList.append(ue4DestinationFolderList[uassetIndex])
        elif 'RTYR' in uasset:
            uassetIndex = assetNameList.index(uasset)
            rtyrNameList.append(uasset)
            rtyrFolderList.append(ue4DestinationFolderList[uassetIndex])
        elif 'RTYE' in uasset:
            # Epic will import new BC/MRO and reuse Common N but only if no Epic N is imported
            uassetIndex = assetNameList.index(uasset)
            rtyeNameList.append(uasset)
            rtyeFolderList.append(ue4DestinationFolderList[uassetIndex])

    # Process skin textures
    if rtyuNameList:
        assetRarity = 'Uncommon'
        if assetType == 'VehicleSkins':
            rtyuMatInstNames, allTextureSets = VehicleSkinImporter.prepareVehMaterialInstNameAndLists(rtyuNameList, rtyuFolderList)
        else:
            rtyuMatInstNames, allTextureSets = WeaponSkinImporter.prepareWpnMaterialInstNameAndLists(rtyuNameList, rtyuFolderList)
        ue4DestinationFolderList, uassetsToOpen, matInstFullPath = setupSkinTextureParameters(ue4DestinationFolderList, rtyuMatInstNames, allTextureSets, assetRarity)
        assetEditSubsys.open_editor_for_assets(uassetsToOpen)
    if rtyrNameList:
        assetRarity = 'Rare'
        if assetType == 'VehicleSkins':
            rtyrMatInstNames, allTextureSets = VehicleSkinImporter.prepareVehMaterialInstNameAndLists(rtyrNameList, rtyrFolderList)
        else:
            rtyrMatInstNames, allTextureSets = WeaponSkinImporter.prepareWpnMaterialInstNameAndLists(rtyrNameList, rtyrFolderList)
        ue4DestinationFolderList, uassetsToOpen, matInstFullPath = setupSkinTextureParameters(ue4DestinationFolderList, rtyrMatInstNames, allTextureSets, assetRarity)
        assetEditSubsys.open_editor_for_assets(uassetsToOpen)
    if rtyeNameList:
        assetRarity = 'Epic'
        if assetType == 'VehicleSkins':
            rtyeMatInstNames, allTextureSets = VehicleSkinImporter.prepareVehMaterialInstNameAndLists(rtyeNameList, rtyeFolderList)
        else:
            rtyeMatInstNames, allTextureSets = WeaponSkinImporter.prepareWpnMaterialInstNameAndLists(rtyeNameList, rtyeFolderList)
        ue4DestinationFolderList, uassetsToOpen, matInstFullPath = setupSkinTextureParameters(ue4DestinationFolderList, rtyeMatInstNames, allTextureSets, assetRarity)
        assetEditSubsys.open_editor_for_assets(uassetsToOpen)

    return matInstFullPath

def setupSkinTextureParameters(ue4DestinationFolderList, matInstNames, allTextureSets, assetRarity):
    uassetsToOpen = []
    materialEditLib = unreal.MaterialEditingLibrary()
    assetTools = unreal.AssetToolsHelpers.get_asset_tools()
    assetRegistry = unreal.AssetRegistryHelpers.get_asset_registry()
    editorAssetLib = unreal.EditorAssetLibrary()
    doesNormalTextureExist = True
    doesMROTextureExist = True

    # Create the material instance and assign the texture set to the proper texture parameter values.
    for set in allTextureSets:
        print("allTextures set: " + str(set))
        uassetName = '/' + set[0].split("/")[-1] # /T_SMG_GabeUMP_RTYE_GabeGreySlush_BC.T_SMG_GabeUMP_RTYE_GabeGreySlush_BC
        matInstDestinationPath = set[0].replace(uassetName, '') + "/" # /Game/Art/Weapons/Base/SubMachineGuns/GabeUMP/Epic
        setIndex = allTextureSets.index(set)

        matInstFullPath = matInstDestinationPath + '%s.%s' % (matInstNames[setIndex], matInstNames[setIndex])

        if editorAssetLib.does_asset_exist(matInstFullPath):
            matInstData = assetRegistry.get_asset_by_object_path(matInstFullPath)
            skinMatInst = matInstData.get_asset()
        else:
            jsonFilePath = os.path.join( os.path.dirname( __file__ ), '../CustomImporter/itoys_importOptionsConfig.json' )
            with open(jsonFilePath) as f:
                data = json.load(f)
                optionData = data['materialOptions']
                unreal.log('Import Options - materialOptions')
                for element in data:
                    if 'materialOptions' in element:
                        parentMaterial = editorAssetLib.find_asset_data(optionData['opaqueMaterial'])

            # Create the material instance uasset.
            skinMatInst = assetTools.create_asset(matInstNames[setIndex], matInstDestinationPath, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
            materialEditLib.set_material_instance_parent(skinMatInst, parentMaterial.get_asset()) # Set the MI parent material.  For weapon skins, we use the MI_PBR_Master_AO.

        # Append mat inst full path to the ue4DestinationFolderList to later be used to save all the assets.
        if "Gadgets" not in matInstFullPath:
            ue4DestinationFolderList.append(matInstFullPath)

        # Add the new material instance to an array to later auto-open up for user to evaluate accuracy.
        uassetsToOpen.append(skinMatInst)

        # Check if skin texture set contains a MRO map.  If not, set the boolean for later logic.
        for texture in set:
            if texture.endswith('_MRO'):
                doesMROTextureExist = True
                break
            else:
                doesMROTextureExist = False

        # Check if skin texture set contains a normal map.  If not, set the boolean for later logic.
        for texture in set:
            if texture.endswith('_N'):
                doesNormalTextureExist = True
                break
            else:
                doesNormalTextureExist = False

        # Assign the textures to the proper material instance texture parameters.
        for texture in set:
            textureAssetData = editorAssetLib.find_asset_data(texture)
            textureAsset = textureAssetData.get_asset()

            if texture.endswith('_BC'):
                materialEditLib.set_material_instance_texture_parameter_value(skinMatInst, 'T_BaseColor', textureAsset)
            elif texture.endswith('_MRO'):
                materialEditLib.set_material_instance_texture_parameter_value(skinMatInst, 'T_MRO', textureAsset)
            elif texture.endswith('_N'):
                materialEditLib.set_material_instance_texture_parameter_value(skinMatInst, 'T_Normal', textureAsset)

            # Normal map doesn't exist in skin texture set.  Construct the full uasset path to the common Normal map texture and use that.
            if doesNormalTextureExist == False:
                # Construct Common normal map texture uasset name
                textureNameSplit = uassetName.split('.')[1] # T_SMG_GabeUMP_RTYE_GabeGreySlush_BC
                removeSuffix = textureNameSplit.rpartition('_')[0] # T_SMG_GabeUMP_RTYE_GabeGreySlush
                removeSkinName = removeSuffix.rpartition('_')[0] # T_SMG_GabeUMP_RTYE
                removeRarity = removeSkinName.rpartition('_')[0] # T_SMG_GabeUMP
                normalMapName = removeRarity + '_N' # T_SMG_GabeUMP_N
                commonNormalMapName = '%s.%s' % (normalMapName, normalMapName) # T_SMG_GabeUMP_N.T_SMG_GabeUMP_N

                # Construst Common normal map texture path
                if "Season" in matInstDestinationPath:
                    normalPathWithSeasonToken = matInstDestinationPath.rpartition('/')[0] # /Game/Art/Gadgets/Explosives/M67Grenade/Season01.
                    normalTexturePath = normalPathWithSeasonToken.rpartition('/')[0] # /Game/Art/Gadgets/Explosives/M67Grenade.
                else:
                    normalTexturePath = matInstDestinationPath.rpartition('/')[0] # /Game/Art/Gadgets/Explosives/M67Grenade

                commonNormalMapFullPath = '%s/%s' % (normalTexturePath, commonNormalMapName) # /Game/Art/Gadgets/Explosives/M67Grenade/T_Explosives_M67Grenade_N.T_Explosives_M67Grenade_N

                normalTextureAssetData = editorAssetLib.find_asset_data(commonNormalMapFullPath)
                normalTextureAsset = normalTextureAssetData.get_asset()
                materialEditLib.set_material_instance_texture_parameter_value(skinMatInst, 'T_Normal', normalTextureAsset)

            # MRO map doesn't exist in skin texture set.  If weapon, construct the full uasset path to the uniform MRO map texture and use that.
            # If not weapon, get the base level mro texture.
            if doesMROTextureExist == False:
                textureNameSplit = uassetName.split('.')[1] # T_SMG_GabeUMP_RTYE_GabeGreySlush_BC
                removeSuffix = textureNameSplit.rpartition('_')[0] # T_SMG_GabeUMP_RTYE_GabeGreySlush
                removeSkinName = removeSuffix.rpartition('_')[0] # T_SMG_GabeUMP_RTYE
                removeRarity = removeSkinName.rpartition('_')[0] # T_SMG_GabeUMP

                if "Weapons" in matInstDestinationPath and (assetRarity == 'Uncommon' or assetRarity ==  'Rare'):
                    # Construct weapon Uniform MRO texture uasset name
                    mroMapName = removeRarity + '_Uniform_MRO' # T_SMG_GabeUMP_Uniform_MRO
                    commonMROMapName = '%s.%s' % (mroMapName, mroMapName) # T_SMG_GabeUMP_MRO.T_SMG_GabeUMP_MRO
                    # Construct Common normal map texture path
                    mroTexturePath = matInstDestinationPath.rpartition('/')[0]
                    print('Weapon MRO Texture Path - ' + mroTexturePath)
                    commonMROMapFullPath = '%s/%s' % (mroTexturePath, commonMROMapName)
                    print('Weapon MRO Texture Full Path - ' + commonMROMapFullPath)
                else:
                    # Non-Weapons don't need the Uniform text in the constructed MRO asset name.
                    mroMapName = removeRarity + '_MRO' # T_SMG_GabeUMP_MRO
                    commonMROMapName = '%s.%s' % (mroMapName, mroMapName) # T_SMG_GabeUMP_MRO.T_SMG_GabeUMP_MRO

                    if CustomImporterFunctions.assetImportType == "GadgetSkins" and "Season" in matInstDestinationPath:
                        mroPathWithSeasonToken = matInstDestinationPath.rpartition('/')[0] # /Game/Art/Gadgets/Explosives/M67Grenade/Season01.
                        mroTexturePath = normalPathWithSeasonToken.rpartition('/')[0] # /Game/Art/Gadgets/Explosives/M67Grenade.
                    else:
                        mroTexturePath = matInstDestinationPath.rpartition('/')[0] # /Game/Art/Gadgets/Explosives/M67Grenade

                    print('Other MRO Texture Path - ' + mroTexturePath)
                    commonMROMapFullPath = '%s/%s' % (mroTexturePath, commonMROMapName)
                    print('Other MRO Texture Full Path - ' + commonMROMapFullPath)

                mroTextureAssetData = editorAssetLib.find_asset_data(commonMROMapFullPath)
                mroTextureAsset = mroTextureAssetData.get_asset()
                materialEditLib.set_material_instance_texture_parameter_value(skinMatInst, 'T_MRO', mroTextureAsset)

    return ue4DestinationFolderList, uassetsToOpen, matInstFullPath

#def createSkinBlueprintNameAndPath(matInstFullPath):
#    print("SKIN BLUEPRINT matInstFullPath - " + matInstFullPath)
#    materialName = matInstFullPath.split(".")[-1]
#    materialUasset = materialName + "." + materialName
#    blueprintName = materialName.replace("MI_", "BP_")
#    blueprintPath = matInstFullPath.replace(materialUasset, "")
#    blueprintFullPath = blueprintPath + blueprintName + "." + blueprintName
#    print("SKIN BLUEPRINT blueprintFullPath - " + blueprintFullPath)
#    return blueprintName, blueprintPath, blueprintFullPath

#def createSkinBlueprintUasset(skinBlueprintName, skinBlueprintPath):
#    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
#    blueprintFactory = unreal.BlueprintFactory()

#    blueprintFactory.set_editor_property("parent_class", unreal.EquipmentSkinLinkage)
#    blueprint = asset_tools.create_asset(skinBlueprintName, skinBlueprintPath, None, blueprintFactory)

#def setSkinBlueprintProperties(matInstFullPath, blueprintFullPath):
#    # Get generated blueprint class
#    blueprintClassFullPath = blueprintFullPath + "_C"
#    generatedClass = unreal.load_object(blueprintClassFullPath)
#    # Get blueprint class default object (CDO)
#    classDefaultObject = unreal.get_default_object(generatedClass)
#    # Find the parent mesh asset
#    parentMeshAsset = findSkinParentMeshAsset(matInstFullPath)
#    # Set property values - MeshOverride and MaterialOverride
#    classDefaultObject.set_editor_property("MeshOverride", parentMeshAsset)
#    classDefaultObject.set_editor_property("MaterialOverride", matInstFullPath)

#def findSkinParentMeshAsset(matInstFullPath):
#    seasonPath = matInstFullPath.rsplit("/", -1)
#    print("SKIN BLUEPRINT seasonPath - " + seasonPath)

#def validateSkinBlueprintProperties():
#    return