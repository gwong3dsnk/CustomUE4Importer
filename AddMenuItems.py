"""
Tool: UE4 Custom Importer
Author: Gabe Wong

This script is setup to run on editor startup to populate new menu items in the editor.
This startup script is referenced by the DefaultEngine.ini file
"""

import unreal

# Create UI objects
menus = unreal.ToolMenus.get()
contentBrowserContextMenu = menus.find_menu("ContentBrowser.AddNewContextMenu")

"""
FBX Mesh Import Menu Options
"""
# Create context menu items
skinNestedMenu = contentBrowserContextMenu.add_sub_menu(contentBrowserContextMenu.get_name(), "ContentBrowserImportAsset", "Skins", "Import Skins")
meshFBXNestedMenu = contentBrowserContextMenu.add_sub_menu(contentBrowserContextMenu.get_name(), "ContentBrowserImportAsset", "FBXMesh", "Import Mesh FBX")

# Establish and setup the character menu options
characterEntry = unreal.ToolMenuEntry(
	name="ImportCharacterFBX",
	type=unreal.MultiBlockType.MENU_ENTRY,
	insert_position=unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.DEFAULT)
)
characterEntry.set_label("Import Character FBX")
characterEntry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON, string="import CustomImporter.CustomImporterFunctions as CustomImporterFunctions; import importlib; importlib.reload(CustomImporterFunctions); asset='Characters'; CustomImporterFunctions.checkOS(asset)", custom_type=unreal.Name(""))
meshFBXNestedMenu.add_menu_entry("FBXMesh",characterEntry)

# Establish and setup the weapon menu options
weaponEntry = unreal.ToolMenuEntry(
	name="ImportWeaponFBX",
	type=unreal.MultiBlockType.MENU_ENTRY,
	insert_position=unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.DEFAULT)
)
weaponEntry.set_label("Import Weapon FBX")
weaponEntry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON, string="import CustomImporter.CustomImporterFunctions as CustomImporterFunctions; import importlib; importlib.reload(CustomImporterFunctions); asset='Weapons'; CustomImporterFunctions.checkOS(asset)", custom_type=unreal.Name(""))
meshFBXNestedMenu.add_menu_entry("FBXMesh",weaponEntry)

# Establish and setup the gadget menu options
gadgetEntry = unreal.ToolMenuEntry(
	name="ImportGadgetFBX",
	type=unreal.MultiBlockType.MENU_ENTRY,
	insert_position=unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.DEFAULT)
)
gadgetEntry.set_label("Import Gadget FBX")
gadgetEntry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON, string="import CustomImporter.CustomImporterFunctions as CustomImporterFunctions; import importlib; importlib.reload(CustomImporterFunctions); asset='Gadgets'; CustomImporterFunctions.checkOS(asset)", custom_type=unreal.Name(""))
meshFBXNestedMenu.add_menu_entry("FBXMesh",gadgetEntry)

# Establish and setup the vehicle menu options
vehicleEntry = unreal.ToolMenuEntry(
	name="ImportVehicleFBX",
	type=unreal.MultiBlockType.MENU_ENTRY,
	insert_position=unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.DEFAULT)
)
vehicleEntry.set_label("Import Vehicle FBX")
vehicleEntry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON, string="import CustomImporter.CustomImporterFunctions as CustomImporterFunctions; import importlib; importlib.reload(CustomImporterFunctions); asset='Vehicles'; CustomImporterFunctions.checkOS(asset)", custom_type=unreal.Name(""))
meshFBXNestedMenu.add_menu_entry("FBXMesh",vehicleEntry)

"""
TGA Skin Import Menu Options
"""

# Establish and setup the weapon skin menu options
characterSkinsEntry = unreal.ToolMenuEntry(
	name="ImportCharacterSkin",
	type=unreal.MultiBlockType.MENU_ENTRY,
	insert_position=unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.DEFAULT)
)
characterSkinsEntry.set_label("Import Character Skin")
characterSkinsEntry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON, string="import CustomImporter.CustomImporterFunctions as CustomImporterFunctions; import importlib; importlib.reload(CustomImporterFunctions); asset='CharacterSkins'; CustomImporterFunctions.checkOS(asset)", custom_type=unreal.Name(""))
skinNestedMenu.add_menu_entry("Skins",characterSkinsEntry)

# Establish and setup the weapon skin menu options
weaponSkinsEntry = unreal.ToolMenuEntry(
	name="ImportWeaponSkin",
	type=unreal.MultiBlockType.MENU_ENTRY,
	insert_position=unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.DEFAULT)
)
weaponSkinsEntry.set_label("Import Weapon Skin")
weaponSkinsEntry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON, string="import CustomImporter.CustomImporterFunctions as CustomImporterFunctions; import importlib; importlib.reload(CustomImporterFunctions); asset='WeaponSkins'; CustomImporterFunctions.checkOS(asset)", custom_type=unreal.Name(""))
skinNestedMenu.add_menu_entry("Skins",weaponSkinsEntry)

# Establish and setup the gadget skin menu options
gadgetSkinsEntry = unreal.ToolMenuEntry(
	name="ImportGadgetSkin",
	type=unreal.MultiBlockType.MENU_ENTRY,
	insert_position=unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.DEFAULT)
)
gadgetSkinsEntry.set_label("Import Gadget Skin")
gadgetSkinsEntry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON, string="import CustomImporter.CustomImporterFunctions as CustomImporterFunctions; import importlib; importlib.reload(CustomImporterFunctions); asset='GadgetSkins'; CustomImporterFunctions.checkOS(asset)", custom_type=unreal.Name(""))
skinNestedMenu.add_menu_entry("Skins",gadgetSkinsEntry)

# Establish and setup the weapon skin menu options
vehicleSkinsEntry = unreal.ToolMenuEntry(
	name="ImportVehicleSkin",
	type=unreal.MultiBlockType.MENU_ENTRY,
	insert_position=unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.DEFAULT)
)
vehicleSkinsEntry.set_label("Import Vehicle Skin")
vehicleSkinsEntry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON, string="import CustomImporter.CustomImporterFunctions as CustomImporterFunctions; import importlib; importlib.reload(CustomImporterFunctions); asset='VehicleSkins'; CustomImporterFunctions.checkOS(asset)", custom_type=unreal.Name(""))
skinNestedMenu.add_menu_entry("Skins",vehicleSkinsEntry)

# Establish and setup the UI texture menu options
uiTextureEntry = unreal.ToolMenuEntry(
	name="ImportUITexture",
	type=unreal.MultiBlockType.MENU_ENTRY,
	insert_position=unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.DEFAULT)
)
uiTextureEntry.set_label("Import UI Textures")
uiTextureEntry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON, string="import CustomImporter.CustomImporterFunctions as CustomImporterFunctions; import importlib; importlib.reload(CustomImporterFunctions); asset='UITextures'; CustomImporterFunctions.checkOS(asset)", custom_type=unreal.Name(""))
contentBrowserContextMenu.add_menu_entry("ContentBrowserImportAsset",uiTextureEntry)