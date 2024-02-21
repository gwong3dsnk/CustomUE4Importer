"""
Tool: UE4 Custom Importer
Author: Gabe Wong
Company: Industrial Toys @ EA

This script is executed by the user selecting the 'Import Gadget FBX' menu option from the Content Browser context menu (right-clicking in empty space)
It handles the retrieval of the FBX file (and path), retrieval of UE4 destination path, setting the import options and finally executing the import logic.
"""

import unreal, json, os, importlib
import CustomImporter.CustomImporterFunctions as CustomImporterFunctions
import CustomImporter.ImporterQtFunctions as ImporterQtFunctions

def openImportWindow():
    CustomImporterFunctions.assetImportType = 'Gadgets'
    CustomImporterFunctions.initialBrowserDir = r'D:\ITOYS\Resources\Art\Gadgets'
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
    assetNamePreConfigure, assetNameReplacePrefix, assetName, assetNameIfExist, ue4AssetName = CustomImporterFunctions.extractAssetName(fbxFile)

    if filePostImportStatus == 'PENDING IMPORT':
        if assetNamePreConfigure.startswith('SK_'):
            skeletal_mesh_task = CustomImporterFunctions.buildImportTask(fbxFile, ue4_destinationPath, buildGadgetSKImportOptions(fbxFile))
        elif assetNamePreConfigure.startswith('SM_'):
            skeletal_mesh_task = CustomImporterFunctions.buildImportTask(fbxFile, ue4_destinationPath, buildGadgetSMImportOptions(fbxFile))
    elif filePostImportStatus == 'PENDING REIMPORT':
        if assetNamePreConfigure.startswith('SK_'):
            skeletal_mesh_task = CustomImporterFunctions.buildImportTask(fbxFile, ue4_destinationPath, buildGadgetSKReImportOptions(fbxFile))
        elif assetNamePreConfigure.startswith('SM_'):
            skeletal_mesh_task = CustomImporterFunctions.buildImportTask(fbxFile, ue4_destinationPath, buildGadgetSMReImportOptions(fbxFile))

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([skeletal_mesh_task])

    # Get LODSettings assetData and start auto-material creation process
    optionSection = "lodSettings"
    optionKey = "gadgetLODSettings"
    optionValueReturned = CustomImporterFunctions.querySingleImportOptions(optionSection, optionKey)
    meshData = CustomImporterFunctions.setLODSettings(ue4_destinationPath, ue4AssetName, optionValueReturned)

    # Call function to conduct the material creation process
    textureList = []
    CustomImporterFunctions.startMaterialCreation(ue4_destinationPath, meshData, CustomImporterFunctions.assetImportType, textureList)

    unreal.log('---[Succesfully imported %s.  Uassets can be found here: %s]---' % (fbxFile, ue4_destinationPath))

def buildGadgetSKImportOptions(fbxFile):
    # Create build options for importing new skeletal mesh
    options = unreal.FbxImportUI()
    jsonFilePath = os.path.join( os.path.dirname( __file__ ), '../CustomImporter/itoys_importOptionsConfig.json' )

    with open(jsonFilePath) as f:
        data = json.load(f)
        optionData = data['gadgetSKImportOptions']

        unreal.log('Setting import options for asset...')
        unreal.log('Import Options - gadgetSKImportOptions')

        for element in data:
            if 'gadgetSKImportOptions' in element:
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
                if "Grenade" in fbxFile:
                    options.skeleton = unreal.load_asset(optionData['skeleton_grenade'])
                return options

def buildGadgetSMImportOptions(fbxFile):
    # Create build options for importing new skeletal mesh
    options = unreal.FbxImportUI()
    jsonFilePath = os.path.join( os.path.dirname( __file__ ), '../CustomImporter/itoys_importOptionsConfig.json' )

    with open(jsonFilePath) as f:
        data = json.load(f)
        optionData = data['gadgetSMImportOptions']

        unreal.log('Setting import options for asset...')
        unreal.log('Import Options - gadgetSMImportOptions')

        for element in data:
            if 'gadgetSMImportOptions' in element:
                options.set_editor_property('import_mesh', optionData['import_mesh'])
                options.set_editor_property('import_textures', optionData['import_textures'])
                options.set_editor_property('import_materials', optionData['import_materials'])
                options.set_editor_property('import_as_skeletal', optionData['import_as_skeletal'])
                options.set_editor_property('reset_to_fbx_on_material_conflict', optionData['reset_to_fbx_on_material_conflict'])
                options.static_mesh_import_data.set_editor_property('auto_generate_collision', optionData['auto_generate_collision'])
                options.static_mesh_import_data.set_editor_property('combine_meshes', optionData['combine_meshes'])
                options.static_mesh_import_data.set_editor_property('generate_lightmap_u_vs', optionData['generate_lightmap_u_vs'])
                options.static_mesh_import_data.set_editor_property('one_convex_hull_per_ucx', optionData['one_convex_hull_per_ucx'])
                options.static_mesh_import_data.set_editor_property('reorder_material_to_fbx_order', optionData['reorder_material_to_fbx_order'])
                options.static_mesh_import_data.set_editor_property('import_mesh_lo_ds', optionData['import_mesh_lo_ds'])
                options.static_mesh_import_data.set_editor_property('transform_vertex_to_absolute', optionData['transform_vertex_to_absolute'])
                return options

def buildGadgetSKReImportOptions(fbxFile):
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

def buildGadgetSMReImportOptions(fbxFile):
    # Create build options for importing new skeletal mesh
    options = unreal.FbxImportUI()
    jsonFilePath = os.path.join( os.path.dirname( __file__ ), '../CustomImporter/itoys_importOptionsConfig.json' )

    with open(jsonFilePath) as f:
        data = json.load(f)
        optionData = data['smMeshReimportOptions']

        unreal.log('Setting import options for asset...')
        unreal.log('Import Options - smMeshReimportOptions')

        for element in data:
            if 'smMeshReimportOptions' in element:
                options.set_editor_property('import_mesh', optionData['import_mesh'])
                options.set_editor_property('import_textures', optionData['import_textures'])
                options.set_editor_property('import_materials', optionData['import_materials'])
                options.set_editor_property('import_as_skeletal', optionData['import_as_skeletal'])
                options.set_editor_property('reset_to_fbx_on_material_conflict', optionData['reset_to_fbx_on_material_conflict'])
                options.static_mesh_import_data.set_editor_property('auto_generate_collision', optionData['auto_generate_collision'])
                options.static_mesh_import_data.set_editor_property('combine_meshes', optionData['combine_meshes'])
                options.static_mesh_import_data.set_editor_property('generate_lightmap_u_vs', optionData['generate_lightmap_u_vs'])
                options.static_mesh_import_data.set_editor_property('one_convex_hull_per_ucx', optionData['one_convex_hull_per_ucx'])
                options.static_mesh_import_data.set_editor_property('reorder_material_to_fbx_order', optionData['reorder_material_to_fbx_order'])
                options.static_mesh_import_data.set_editor_property('import_mesh_lo_ds', optionData['import_mesh_lo_ds'])
                return options