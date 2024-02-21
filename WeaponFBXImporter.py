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
    CustomImporterFunctions.assetImportType = 'Weapons'
    CustomImporterFunctions.initialBrowserDir = r'D:\ITOYS\Resources\Art\Weapons'
    importlib.reload(ImporterQtFunctions)

    # Start the GUi
    main_window = ImporterQtFunctions.OpenImportWindow()
    main_window.show()
    unreal.parent_external_window_to_slate(main_window.winId())

def executeAssetImport(fbxFile, ue4_destinationPath, filePostImportStatus):
    # Execute Import Logic
    editorAssetLib = unreal.EditorAssetLibrary()
    assetSubType = ""
    weaponAttachPathTokens = ['Barrels', 'Sights', 'Foregrips', "Lasersights", "Bipods", "Projectiles"]
    unreal.log('---[Starting import process for %s]---' % (fbxFile))

    # Check if the ue4 destination directory is valid, if not, create it.
    isUE4DirectoryValid = editorAssetLib.does_directory_exist(ue4_destinationPath)
    if isUE4DirectoryValid == False:
        editorAssetLib.make_directory(ue4_destinationPath)

    # Get asset name details
    assetNamePreConfigure, assetNameReplacePrefix, assetName, assetNameIfExist, ue4AssetName = CustomImporterFunctions.extractAssetName(fbxFile)

    if filePostImportStatus == 'PENDING IMPORT':
        if assetNamePreConfigure.startswith('SK_'):
            assetSubType = ""
            if 'Base' in fbxFile:
                skeletal_mesh_task = CustomImporterFunctions.buildImportTask(fbxFile, ue4_destinationPath, buildWeaponBaseImportOptions(fbxFile))
            elif 'Charms' in fbxFile:
                skeletal_mesh_task = CustomImporterFunctions.buildImportTask(fbxFile, ue4_destinationPath, buildWeaponCharmsImportOptions(fbxFile))
            elif any(token in fbxFile for token in weaponAttachPathTokens):
                skeletal_mesh_task = CustomImporterFunctions.buildImportTask(fbxFile, ue4_destinationPath, buildWeaponPartsImportOptions(fbxFile))
        elif assetNamePreConfigure.startswith('SM_'):
            skeletal_mesh_task = CustomImporterFunctions.buildImportTask(fbxFile, ue4_destinationPath, buildWeaponProjectileImportOptions(fbxFile))
            assetSubType = "Projectile"
    elif filePostImportStatus == 'PENDING REIMPORT':
        if assetNamePreConfigure.startswith('SK_'):
            assetSubType = ""
            skeletal_mesh_task = CustomImporterFunctions.buildImportTask(fbxFile, ue4_destinationPath, buildWeaponReImportOptions(fbxFile))
        elif assetNamePreConfigure.startswith('SM_'):
            skeletal_mesh_task = CustomImporterFunctions.buildImportTask(fbxFile, ue4_destinationPath, buildWeaponSMReImportOptions(fbxFile))
            assetSubType = "Projectile"

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([skeletal_mesh_task])

    # Get LODSettings assetData and start auto-material creation process
    optionSection = "lodSettings"
    optionKey = "weaponLODSettings"
    optionValueReturned = CustomImporterFunctions.querySingleImportOptions(optionSection, optionKey)
    skMeshAsset = CustomImporterFunctions.setLODSettings(ue4_destinationPath, ue4AssetName, optionValueReturned)

    # Retrieve texture file names from fbx file IF the mesh asset is a projectile
    if assetSubType == "Projectile":
        projectileTextureList = []
        fbxFileRead = open(fbxFile, 'r')
        count = 0
        while True:
            count += 1
            line = fbxFileRead.readline()

            if not line:
                break

            if "Filename:" in line and "RelativeFilename:" not in line:
                # Construct the full UE4 path to the texture asset to later check if it exists or not.  Add to list and pass off to startMaterialCreation()
                print("Line{}: {}".format(count, line.strip()))

                print(line)

                replaceFileName = line.replace("Filename: ", "")
                print (replaceFileName)
                replaceQuotes = replaceFileName.replace('"', '')
                print (replaceQuotes)

                textureBaseNameWithExtension = replaceQuotes.rsplit("/")[-1]
                textureBaseName = textureBaseNameWithExtension.replace(".tga", "")
                textureRemoveNewLine = textureBaseName.rstrip()
                print (textureRemoveNewLine)

                stripWhiteSpace = replaceQuotes.strip()
                replaceRootPath = stripWhiteSpace.replace("D:/ITOYS/Resources/", "/Game/")
                print (replaceRootPath)
                replacementString = "." + textureRemoveNewLine
                fullUE4TexturePath = replaceRootPath.replace(".tga", replacementString)
                print (fullUE4TexturePath)

                projectileTextureList.append(fullUE4TexturePath)

        fbxFileRead.close()
        CustomImporterFunctions.startMaterialCreation(ue4_destinationPath, skMeshAsset, CustomImporterFunctions.assetImportType, projectileTextureList)
    else:
        projectileTextureList = []
        CustomImporterFunctions.startMaterialCreation(ue4_destinationPath, skMeshAsset, CustomImporterFunctions.assetImportType, projectileTextureList)

    # Call function to set the CMS metadata to True
    if 'Charms' in fbxFile:
        fullAssetPath = ue4_destinationPath + ue4AssetName + "." + ue4AssetName
        CustomImporterFunctions.setCMSInclusionTag(fullAssetPath)


    unreal.log('---[Succesfully imported %s.  Uassets can be found here: %s]---' % (fbxFile, ue4_destinationPath))

def buildWeaponBaseImportOptions(fbxFile):
    # This is where you set all the import options for the FBX.  Read Json file to retrieve data for this particular asset type.
    options = unreal.FbxImportUI()
    jsonFilePath = os.path.join( os.path.dirname( __file__ ), '../CustomImporter/itoys_importOptionsConfig.json' )

    with open(jsonFilePath) as f:
        data = json.load(f)
        optionData = data['weaponBaseImportOptions']

        unreal.log('Setting import options for asset...')
        unreal.log('Import Options - weaponBaseImportOptions')

        for element in data:
            if 'weaponBaseImportOptions' in element:
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
                options.skeletal_mesh_import_data.set_editor_property('reorder_material_to_fbx_order', optionData['reorder_material_to_fbx_order'])
                options.skeletal_mesh_import_data.set_editor_property('import_mesh_lo_ds', optionData['import_mesh_lo_ds'])
                return options

def buildWeaponPartsImportOptions(fbxFile):
    options = unreal.FbxImportUI()
    jsonFilePath = os.path.join( os.path.dirname( __file__ ), '../CustomImporter/itoys_importOptionsConfig.json' )

    with open(jsonFilePath) as f:
        data = json.load(f)
        optionData = data['weaponPartsImportOptions']

        unreal.log('Setting import options for asset...')
        unreal.log('Import Options - weaponPartsImportOptions')

        for element in data:
            if 'weaponPartsImportOptions' in element:
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

def buildWeaponCharmsImportOptions(fbxFile):
    # This is where you set all the import options for the FBX.  Read Json file to retrieve data for this particular asset type.
    options = unreal.FbxImportUI()
    jsonFilePath = os.path.join( os.path.dirname( __file__ ), '../CustomImporter/itoys_importOptionsConfig.json' )

    with open(jsonFilePath) as f:
        data = json.load(f)
        optionData = data['weaponCharmsImportOptions']

        unreal.log('Setting import options for asset...')
        unreal.log('Import Options - weaponCharmsImportOptions')

        for element in data:
            if 'weaponCharmsImportOptions' in element:
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
                options.skeletal_mesh_import_data.set_editor_property('use_t0_as_ref_pose', optionData['use_t0_as_ref_pose'])
                options.skeletal_mesh_import_data.set_editor_property('reorder_material_to_fbx_order', optionData['reorder_material_to_fbx_order'])
                options.skeletal_mesh_import_data.set_editor_property('import_mesh_lo_ds', optionData['import_mesh_lo_ds'])
                return options

def buildWeaponProjectileImportOptions(fbxFile):
    # Create build options for importing new skeletal mesh
    options = unreal.FbxImportUI()
    jsonFilePath = os.path.join( os.path.dirname( __file__ ), '../CustomImporter/itoys_importOptionsConfig.json' )

    with open(jsonFilePath) as f:
        data = json.load(f)
        optionData = data['weaponProjectileImportOptions']

        unreal.log('Setting import options for asset...')
        unreal.log('Import Options - weaponProjectileImportOptions')

        for element in data:
            if 'weaponProjectileImportOptions' in element:
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

def buildWeaponReImportOptions(fbxFile):
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

def buildWeaponSMReImportOptions(fbxFile):
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