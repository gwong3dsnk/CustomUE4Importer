"""
Tool: UE4 Custom Importer
Author: Gabe Wong

This script is executed by the user selecting the 'Import Character FBX' menu option from the Content Browser context menu (right-clicking in empty space)
It handles the retrieval of the FBX file (and path), retrieval of UE4 destination path, setting the import options and finally executing the import logic.
"""

import unreal, json, os, importlib
import CustomImporter.CustomImporterFunctions as CustomImporterFunctions
import CustomImporter.ImporterQtFunctions as ImporterQtFunctions

def openImportWindow():
    CustomImporterFunctions.assetImportType = 'Characters'
    CustomImporterFunctions.initialBrowserDir = r'D:\ITOYS\Resources\Art\Characters'
    importlib.reload(ImporterQtFunctions)

    # Start the GUi
    main_window = ImporterQtFunctions.OpenImportWindow()
    main_window.show()
    unreal.parent_external_window_to_slate(main_window.winId())

def executeAssetImport(fbxFile, ue4_destinationPath, filePostImportStatus):
    editorAssetLib = unreal.EditorAssetLibrary()
    unreal.log('---[Starting import process for %s]---' % (fbxFile))

    # Check if the ue4 destination directory is valid, if not, create it.
    isUE4DirectoryValid = editorAssetLib.does_directory_exist(ue4_destinationPath)
    if isUE4DirectoryValid == False:
        editorAssetLib.make_directory(ue4_destinationPath)

    # Get asset name details
    assetNamePreConfigure, assetNameReplacePrefix, assetName, assetNameIfExist, ue4AssetName = CustomImporterFunctions.extractAssetName(fbxFile)

    # Import logic
    if filePostImportStatus == 'PENDING IMPORT':
        if 'Bodies' in fbxFile:
            if 'Backpack' in assetName or 'Gloves' in assetName:
                skeletal_mesh_task = CustomImporterFunctions.buildImportTask(fbxFile, ue4_destinationPath, buildCharacterPartsImportOptions(fbxFile))
            else:
                skeletal_mesh_task = CustomImporterFunctions.buildImportTask(fbxFile, ue4_destinationPath, buildCharacterBodiesImportOptions(fbxFile))
        elif 'Backpacks' in fbxFile or 'Gloves' in fbxFile:
            skeletal_mesh_task = CustomImporterFunctions.buildImportTask(fbxFile, ue4_destinationPath, buildCharacterPartsImportOptions(fbxFile))
    elif filePostImportStatus == 'PENDING REIMPORT':
        skeletal_mesh_task = CustomImporterFunctions.buildImportTask(fbxFile, ue4_destinationPath, buildCharacterReImportOptions(fbxFile))
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([skeletal_mesh_task])

    # Get the character LOD Settings uasset to be assigned to the character SK mesh's LODSettings interface.
    optionSection = "lodSettings"
    optionKey = "characterLODSettings"
    optionValueReturned = CustomImporterFunctions.querySingleImportOptions(optionSection, optionKey)

    # Call function that assigns the LODSettings uasset.
    skMeshAsset = CustomImporterFunctions.setLODSettings(ue4_destinationPath, ue4AssetName, optionValueReturned)

    # Call function to conduct the material creation process
    textureList = []
    CustomImporterFunctions.startMaterialCreation(ue4_destinationPath, skMeshAsset, CustomImporterFunctions.assetImportType, textureList)

    # Call function to assign PM_Cloth only if active SK mesh being processed is a Backpack
    optionSection = "physicalMaterial"
    optionKey = "backpackphysicalMaterial"
    optionValueReturned = CustomImporterFunctions.querySingleImportOptions(optionSection, optionKey)
    if 'Backpacks' in fbxFile:
        CustomImporterFunctions.setPhysicalMaterial(ue4_destinationPath, ue4AssetName, optionValueReturned)

    # TODO: Call function to check if bone removal option is checked or not and if it is, set the bone removal properties on character SK mesh.

    unreal.log('---[Succesfully imported %s.  Uassets can be found here: %s]---' % (fbxFile, ue4_destinationPath))

def buildCharacterBodiesImportOptions(fbxFile):
    # This is where you set all the import options for the FBX.  Read Json file to retrieve data for this particular asset type.
    options = unreal.FbxImportUI()
    jsonFilePath = os.path.join( os.path.dirname( __file__ ), '../CustomImporter/itoys_importOptionsConfig.json' )

    with open(jsonFilePath) as f:
        data = json.load(f)
        optionData = data['characterBodiesImportOptions']

        unreal.log('Setting import options for asset...')
        unreal.log('Import Options - characterBodiesImportOptions')

        for element in data:
            if 'characterBodiesImportOptions' in element:
                options.set_editor_property('import_mesh', optionData['import_mesh'])
                options.set_editor_property('import_textures', optionData['import_textures'])
                options.set_editor_property('import_materials', optionData['import_materials'])
                options.set_editor_property('import_as_skeletal', optionData['import_as_skeletal'])
                options.set_editor_property('create_physics_asset', optionData['create_physics_asset'])
                options.set_editor_property('reset_to_fbx_on_material_conflict', optionData['reset_to_fbx_on_material_conflict'])
                options.set_editor_property('import_animations', optionData['import_animations'])
                options.skeleton = unreal.load_asset(optionData['skeleton'])
                options.physics_asset = unreal.load_asset(optionData['physics_asset'])
                options.skeletal_mesh_import_data.set_editor_property('import_morph_targets', optionData['import_morph_targets'])
                options.skeletal_mesh_import_data.set_editor_property('update_skeleton_reference_pose', optionData['update_skeleton_reference_pose'])
                options.skeletal_mesh_import_data.set_editor_property('import_mesh_lo_ds', optionData['import_mesh_lo_ds'])
                options.skeletal_mesh_import_data.set_editor_property('reorder_material_to_fbx_order', optionData['reorder_material_to_fbx_order'])
                options.skeletal_mesh_import_data.set_editor_property('use_t0_as_ref_pose', optionData['use_t0_as_ref_pose'])
                return options

def buildCharacterPartsImportOptions(fbxFile):
    options = unreal.FbxImportUI()
    jsonFilePath = os.path.join( os.path.dirname( __file__ ), '../CustomImporter/itoys_importOptionsConfig.json' )

    with open(jsonFilePath) as f:
        data = json.load(f)
        optionData = data['characterPartsImportOptions']

        unreal.log('Setting import options for asset...')
        unreal.log('Import Options - characterPartsImportOptions')

        for element in data:
            if 'characterPartsImportOptions' in element:
                options.set_editor_property('import_mesh', optionData['import_mesh'])
                options.set_editor_property('import_textures', optionData['import_textures'])
                options.set_editor_property('import_materials', optionData['import_materials'])
                options.set_editor_property('import_as_skeletal', optionData['import_as_skeletal'])
                options.set_editor_property('create_physics_asset', optionData['create_physics_asset'])
                options.set_editor_property('reset_to_fbx_on_material_conflict', optionData['reset_to_fbx_on_material_conflict'])
                options.set_editor_property('import_animations', optionData['import_animations'])
                options.skeleton = unreal.load_asset(optionData['skeleton'])
                options.skeletal_mesh_import_data.set_editor_property('import_morph_targets', optionData['import_morph_targets'])
                options.skeletal_mesh_import_data.set_editor_property('update_skeleton_reference_pose', optionData['update_skeleton_reference_pose'])
                options.skeletal_mesh_import_data.set_editor_property('import_mesh_lo_ds', optionData['import_mesh_lo_ds'])
                options.skeletal_mesh_import_data.set_editor_property('reorder_material_to_fbx_order', optionData['reorder_material_to_fbx_order'])
                options.skeletal_mesh_import_data.set_editor_property('use_t0_as_ref_pose', optionData['use_t0_as_ref_pose'])
                return options

def buildCharacterReImportOptions(fbxFile):
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
                options.skeletal_mesh_import_data.set_editor_property('import_mesh_lo_ds', optionData['import_mesh_lo_ds'])
                options.skeletal_mesh_import_data.set_editor_property('reorder_material_to_fbx_order', optionData['reorder_material_to_fbx_order'])
                options.skeletal_mesh_import_data.set_editor_property('use_t0_as_ref_pose', optionData['use_t0_as_ref_pose'])
                return options

def generateUE4Path(sourceFilePath, assetName):
    if 'Bodies' in sourceFilePath:
        if 'Gloves' not in assetName and 'Backpack' not in assetName:
            expectedUE4AssetPath = '/Game/Art/Characters/Bodies/%s/' % (assetName)
        elif 'Gloves' in assetName and 'Backpack' not in assetName:
            expectedUE4AssetPath = '/Game/Art/Characters/Gloves/%s/' % (assetName)
        elif 'Gloves' not in assetName and 'Backpack' in assetName:
            expectedUE4AssetPath = '/Game/Art/Characters/Backpacks/%s/' % (assetName)
    elif 'Gloves' in sourceFilePath:
        expectedUE4AssetPath = '/Game/Art/Characters/Gloves/%s/' % (assetName)
    elif 'Backpacks' in sourceFilePath:
        expectedUE4AssetPath = '/Game/Art/Characters/Backpacks/%s/' % (assetName)

    return expectedUE4AssetPath