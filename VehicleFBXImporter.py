"""
Tool: UE4 Custom Importer
Author: Gabe Wong

This script is executed by the user selecting the 'Import Weapon FBX' menu option from the Content Browser context menu (right-clicking in empty space)
It handles the retrieval of the FBX file (and path), retrieval of UE4 destination path, setting the import options and finally executing the import logic.
"""

import unreal, json, os, importlib
import CustomImporter.CustomImporterFunctions as CustomImporterFunctions
import CustomImporter.ImporterQtFunctions as ImporterQtFunctions

def openImportWindow():
    CustomImporterFunctions.assetImportType = 'Vehicles'
    CustomImporterFunctions.initialBrowserDir = r'D:\ITOYS\Resources\Art\Vehicles'
    importlib.reload(ImporterQtFunctions)

    # Start the GUi
    main_window = ImporterQtFunctions.OpenImportWindow()
    main_window.show()
    unreal.parent_external_window_to_slate(main_window.winId())

def executeAssetImport(fbxFile, ue4_destinationPath, filePostImportStatus):
    # Execute Import Logic
    editorAssetLib = unreal.EditorAssetLibrary()
    unreal.log('---[Starting import process for %s]---' % (fbxFile))

    # Check if the ue4 destination directory is valid, if not, create it.
    isUE4DirectoryValid = editorAssetLib.does_directory_exist(ue4_destinationPath)
    if isUE4DirectoryValid == False:
        editorAssetLib.make_directory(ue4_destinationPath)

    # Get asset name details
    # I.e. assetNamePreConfigure - SK_Tank_GabeT90.fbx, assetNameReplacePrefix - Tank_GabeT90.fbx, assetName - Tank_GabeT90, ue4AssetName - SK_Tank_GabeT90
    assetNamePreConfigure, assetNameReplacePrefix, assetName, assetNameIfExist, ue4AssetName = CustomImporterFunctions.extractAssetName(fbxFile)

    if "_Destroyed" in ue4AssetName or "_FP" in ue4AssetName:
        # Create the full UE4 path to the vehicle skeleton that's used on all vehicle states (Destroyed, Pristine, FP)
        if "Destroyed" in ue4AssetName:
            ue4BaseAssetName = ue4AssetName.replace("_Destroyed", "")
        elif "FP" in ue4AssetName:
            ue4BaseAssetName = ue4AssetName.replace("_FP", "")
        pathToVehicleSkeleton = ue4_destinationPath + ue4BaseAssetName + '_Skeleton' + '.' + ue4BaseAssetName + '_Skeleton'
    else:
        pathToVehicleSkeleton = ""

    if filePostImportStatus == 'PENDING IMPORT':
        skeletal_mesh_task = CustomImporterFunctions.buildImportTask(fbxFile, ue4_destinationPath, buildVehicleBaseImportOptions(pathToVehicleSkeleton, fbxFile))
    elif filePostImportStatus == 'PENDING REIMPORT':
        skeletal_mesh_task = CustomImporterFunctions.buildImportTask(fbxFile, ue4_destinationPath, buildVehicleReImportOptions(fbxFile))

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([skeletal_mesh_task])

    # Get LODSettings assetData and start auto-material creation process
    optionSection = "lodSettings"
    optionKey = "vehicleLODSettings"
    optionValueReturned = CustomImporterFunctions.querySingleImportOptions(optionSection, optionKey)
    skMeshAsset = CustomImporterFunctions.setLODSettings(ue4_destinationPath, ue4AssetName, optionValueReturned)

    # Call function to conduct the material creation process
    textureList = []
    CustomImporterFunctions.startMaterialCreation(ue4_destinationPath, skMeshAsset, CustomImporterFunctions.assetImportType, textureList)

    unreal.log('---[Succesfully imported %s.  Uassets can be found here: %s]---' % (fbxFile, ue4_destinationPath))

def buildVehicleBaseImportOptions(pathToVehicleSkeleton, fbxFile):
    # This is where you set all the import options for the FBX.  Read Json file to retrieve data for this particular asset type.
    options = unreal.FbxImportUI()
    jsonFilePath = os.path.join( os.path.dirname( __file__ ), '../CustomImporter/itoys_importOptionsConfig.json' )

    with open(jsonFilePath) as f:
        data = json.load(f)
        optionData = data['vehicleBaseImportOptions']

        unreal.log('Setting import options for asset...')
        unreal.log('Import Options - vehicleBaseImportOptions')

        for element in data:
            if 'vehicleBaseImportOptions' in element:
                options.set_editor_property('import_mesh', optionData['import_mesh'])
                options.set_editor_property('import_textures', optionData['import_textures'])
                options.set_editor_property('import_materials', optionData['import_materials'])
                options.set_editor_property('import_as_skeletal', optionData['import_as_skeletal'])
                options.set_editor_property('create_physics_asset', optionData['create_physics_asset'])
                options.set_editor_property('reset_to_fbx_on_material_conflict', optionData['reset_to_fbx_on_material_conflict'])
                options.set_editor_property('import_animations', optionData['import_animations'])
                options.skeletal_mesh_import_data.set_editor_property('import_morph_targets', optionData['import_morph_targets'])
                options.skeletal_mesh_import_data.set_editor_property('update_skeleton_reference_pose', optionData['update_skeleton_reference_pose'])
                options.skeletal_mesh_import_data.set_editor_property('reorder_material_to_fbx_order', optionData['reorder_material_to_fbx_order'])
                options.skeletal_mesh_import_data.set_editor_property('import_mesh_lo_ds', optionData['import_mesh_lo_ds'])
                if pathToVehicleSkeleton:
                    options.skeleton = unreal.load_asset(pathToVehicleSkeleton)
                return options

def buildVehicleReImportOptions(fbxFile):
    options = unreal.FbxImportUI()
    jsonFilePath = os.path.join( os.path.dirname( __file__ ), '../CustomImporter/itoys_importOptionsConfig.json' )

    with open(jsonFilePath) as f:
        data = json.load(f)
        optionData = data['skMeshReimportOptions']

        unreal.log('Setting import options for asset...')
        unreal.log('Import Options - skMeshReimportOptions')

        for element in data:
            if 'skMeshReimportOptions' in element:
                options.set_editor_property('import_mesh', optionData['import_mesh'])
                options.set_editor_property('import_textures', optionData['import_textures'])
                options.set_editor_property('import_materials', optionData['import_materials'])
                options.set_editor_property('import_as_skeletal', optionData['import_as_skeletal'])
                options.set_editor_property('create_physics_asset', optionData['create_physics_asset'])
                options.set_editor_property('reset_to_fbx_on_material_conflict', optionData['reset_to_fbx_on_material_conflict'])
                options.set_editor_property('import_animations', optionData['import_animations'])
                options.skeletal_mesh_import_data.set_editor_property('import_morph_targets', optionData['import_morph_targets'])
                options.skeletal_mesh_import_data.set_editor_property('update_skeleton_reference_pose', optionData['update_skeleton_reference_pose'])
                options.skeletal_mesh_import_data.set_editor_property('reorder_material_to_fbx_order', optionData['reorder_material_to_fbx_order'])
                options.skeletal_mesh_import_data.set_editor_property('import_mesh_lo_ds', optionData['import_mesh_lo_ds'])

                return options

def generateUE4Path(sourceFilePath, vehBaseName):
    if 'Tanks' in sourceFilePath:
        expectedUE4AssetPath = '/Game/Art/Vehicles/Tanks/%s' % (vehBaseName)
    elif 'Aircrafts' in sourceFilePath:
        expectedUE4AssetPath = '/Game/Art/Vehicles/Aircrafts/%s' % (vehBaseName)
    elif 'Ships' in sourceFilePath:
        expectedUE4AssetPath = '/Game/Art/Vehicles/Ships/%s' % (vehBaseName)
    elif 'Utility' in sourceFilePath:
        expectedUE4AssetPath = '/Game/Art/Vehicles/Utility/%s' % (vehBaseName)

    return expectedUE4AssetPath