"""
This script executed by the user selecting the 'Import Weapon Skin' menu option from either the File menu or the Content Browser context menu (right-clicking in empty space)
It handles the retrieval of the texture image file (and path), retrieval of UE4 destination path, finally executing the import logic.
"""

import unreal, importlib
import CustomImporter.CustomImporterFunctions as CustomImporterFunctions
import CustomImporter.ImporterQtFunctions as ImporterQtFunctions

def openImportWindow():
    CustomImporterFunctions.assetImportType = 'UITextures'
    CustomImporterFunctions.initialBrowserDir = r'D:\ITOYS\Resources\UI\Images'
    importlib.reload(ImporterQtFunctions)

    # Start the GUI
    main_window = ImporterQtFunctions.OpenImportWindow()
    main_window.show()
    unreal.parent_external_window_to_slate(main_window.winId())

def setTextureProperties(ue4DestinationFolderList):
    assetRegistry = unreal.AssetRegistryHelpers.get_asset_registry()

    for path in ue4DestinationFolderList:
        textureData = assetRegistry.get_asset_by_object_path(path)
        textureAsset = textureData.get_asset()

        compressionQuality = unreal.TextureCompressionQuality.TCQ_HIGHEST
        addressTiling = unreal.TextureAddress.TA_CLAMP
        thumbnailTextureGroup = unreal.TextureGroup.TEXTUREGROUP_PROJECT09
        uiTextureGroup = unreal.TextureGroup.TEXTUREGROUP_UI

        textureAsset.set_editor_property('compression_quality', compressionQuality)
        textureAsset.set_editor_property('address_x', addressTiling)
        textureAsset.set_editor_property('address_y', addressTiling)
        if "Thumbnail" in path:
            textureAsset.set_editor_property('lod_group', thumbnailTextureGroup)
        else:
            textureAsset.set_editor_property('lod_group', uiTextureGroup)