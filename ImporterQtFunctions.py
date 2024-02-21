"""
Tool: UE4 Custom Importer
Author: Gabe Wong

This script contains all QT related functions for the importer UI.
"""

from PySide2 import QtWidgets, QtCore, QtGui, QtUiTools
import unreal, sys, os,importlib
import CustomImporter.CustomImporterFunctions as CustomImporterFunctions
import CustomImporter.CharacterFBXImporter as CharacterFBXImporter
import CustomImporter.WeaponFBXImporter as WeaponFBXImporter
import CustomImporter.GadgetFBXImporter as GadgetFBXImporter
import CustomImporter.SkinImportCreation as SkinImportCreation
import CustomImporter.VehicleFBXImporter as VehicleFBXImporter
import CustomImporter.UITextureImporter as UITextureImporter

class OpenImportWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(OpenImportWindow, self).__init__(parent)

        filePath = os.path.dirname(os.path.abspath(__file__))
        UI_FILE = r"%s\..\ui\customImporterUI.ui" % filePath
        ui_file = QtCore.QFile(UI_FILE)
        ui_file.open(QtCore.QFile.ReadOnly)
        ui_file.close()

        # Setting window title.  For some reason the width and height from the MainWindow from QTDesigner isn't coming through, so setting them here for now.
        self.setWindowTitle("IToys Custom Importer")
        self.setFixedWidth(2220)
        self.setFixedHeight(700)

        # Load the created UI widget from Designer
        self.widget = QtUiTools.QUiLoader().load(ui_file)

        # Attach the widget to the "self" GUI
        self.widget.setParent(self)

        self.createConnections()

        # The following will setup a right-click context menus.
        self.widget.TV_FileBrowse.customContextMenuRequested.connect(self.fileBrowserContextMenu)
        self.widget.LIST_Status.customContextMenuRequested.connect(self.statusContextMenu)

        self.populate()

    def createConnections(self):
        # Creates the connections between GUI elements and their respective function calls.
        #region
        self.widget.BTN_ClearLists.clicked.connect(lambda: self.clearLists())
        self.widget.BTN_ImportAssets.clicked.connect(lambda: self.importAssetFiles())
        self.widget.BTN_AddFile.clicked.connect(lambda: self.prepareToAddSelectedFilesToLists())
        self.widget.actionOpenCharacterFBXImporter.triggered.connect(self.openCharacterFBXImporter)
        self.widget.actionOpenWeaponFBXImporter.triggered.connect(self.openWeaponFBXImporter)
        self.widget.actionOpenGadgetFBXImporter.triggered.connect(self.openGadgetFBXImporter)
        self.widget.actionOpenVehicleFBXImporter.triggered.connect(self.openVehicleFBXImporter)
        self.widget.actionOpenCharacterSkinImporter.triggered.connect(self.openCharacterSkinImporter)
        self.widget.actionOpenWeaponSkinImporter.triggered.connect(self.openWeaponSkinImporter)
        self.widget.actionOpenGadgetSkinImporter.triggered.connect(self.openGadgetSkinImporter)
        self.widget.actionOpenVehicleSkinImporter.triggered.connect(self.openVehicleSkinImporter)
        self.widget.actionOpenUIImporter.triggered.connect(self.openUIImporter)
        self.widget.actionAboutCustomImporter.triggered.connect(self.aboutCustomImporter)
        self.widget.actionContactHelp.triggered.connect(self.contactHelp)
        self.widget.actionClearLists.triggered.connect(self.clearLists)
        self.widget.actionE_xit.triggered.connect(self.closeWindow)
        #endregion

    def populate(self):
        # Handles setup of the file browser TreeView and filters the types of files that are displayed based on the asset type (mesh [fbx] vs texture [tga])
        # Sets main label text to communicate asset type.
        #region
        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath((QtCore.QDir.rootPath()))
        if (CustomImporterFunctions.assetImportType == 'CharacterSkins' or CustomImporterFunctions.assetImportType == 'WeaponSkins' or
            CustomImporterFunctions.assetImportType == 'GadgetSkins' or CustomImporterFunctions.assetImportType == 'VehicleSkins'):
            self.model.setNameFilters(["*.tga", "*.TGA"])
        elif CustomImporterFunctions.assetImportType == 'UITextures':
            self.model.setNameFilters(["*.png", "*.PNG"])
        else:
            self.model.setNameFilters(["*.fbx", "*.FBX"])
        self.model.setNameFilterDisables(False)
        self.widget.TV_FileBrowse.setModel(self.model)
        self.widget.TV_FileBrowse.setRootIndex(self.model.index(CustomImporterFunctions.initialBrowserDir))
        headerStyle = "QHeaderView::section{Background-color:rgb(175,175,175);}"
        self.widget.TV_FileBrowse.setStyleSheet(headerStyle)
        self.widget.TV_FileBrowse.setStyleSheet("Background-color:rgb(220,220,220)")
        self.widget.TV_FileBrowse.setColumnWidth(0, 300)
        self.widget.TV_FileBrowse.setColumnWidth(1, 100)
        self.widget.TV_FileBrowse.setColumnWidth(2, 100)

        if CustomImporterFunctions.assetImportType == 'Characters':
            self.widget.LBL_TitleAssetType.setText("Character FBX Importer")
        elif CustomImporterFunctions.assetImportType == 'Weapons':
            self.widget.LBL_TitleAssetType.setText("Weapon FBX Importer")
        elif CustomImporterFunctions.assetImportType == 'Gadgets':
            self.widget.LBL_TitleAssetType.setText("Gadgets FBX Importer")
        elif CustomImporterFunctions.assetImportType == 'Vehicles':
            self.widget.LBL_TitleAssetType.setText("Vehicles FBX Importer")
        elif CustomImporterFunctions.assetImportType == 'CharacterSkins':
            self.widget.LBL_TitleAssetType.setText("Character Skin Importer")
        elif CustomImporterFunctions.assetImportType == 'WeaponSkins':
            self.widget.LBL_TitleAssetType.setText("Weapon Skin Importer")
        elif CustomImporterFunctions.assetImportType == 'GadgetSkins':
            self.widget.LBL_TitleAssetType.setText("Gadget Skin Importer")
        elif CustomImporterFunctions.assetImportType == 'VehicleSkins':
            self.widget.LBL_TitleAssetType.setText("Vehicle Skin Importer")
        elif CustomImporterFunctions.assetImportType == 'UITextures':
            self.widget.LBL_TitleAssetType.setText("UI Texture Importer")
        #endregion

    def openCharacterFBXImporter(self):
        self.closeWindow()
        CharacterFBXImporter.openImportWindow()

    def openWeaponFBXImporter(self):
        self.closeWindow()
        WeaponFBXImporter.openImportWindow()

    def openGadgetFBXImporter(self):
        self.closeWindow()
        GadgetFBXImporter.openImportWindow()

    def openVehicleFBXImporter(self):
        self.closeWindow()
        VehicleFBXImporter.openImportWindow()

    def openCharacterSkinImporter(self):
        self.closeWindow()
        import CustomImporter.CharacterSkinImporter as CharacterSkinImporter
        CharacterSkinImporter.openImportWindow()

    def openWeaponSkinImporter(self):
        self.closeWindow()
        import CustomImporter.WeaponSkinImporter as WeaponSkinImporter
        WeaponSkinImporter.openImportWindow()

    def openGadgetSkinImporter(self):
        self.closeWindow()
        import CustomImporter.GadgetSkinImporter as GadgetSkinImporter
        GadgetSkinImporter.openImportWindow()

    def openVehicleSkinImporter(self):
        self.closeWindow()
        import CustomImporter.VehicleSkinImporter as VehicleSkinImporter
        VehicleSkinImporter.openImportWindow()

    def openUIImporter(self):
        self.closeWindow()
        UITextureImporter.openImportWindow()

    def aboutCustomImporter(self):
        return

    def contactHelp(self):
        return

    def closeWindow(self):
        self.close()

    def clearLists(self):
        # Need to reset ue4PathError array otherwise will experience inconsistent behavior when trying to override assets for reimport via the context menu
        CustomImporterFunctions.ue4PathError = []
        self.widget.LIST_UE4Path.clear()
        self.widget.LIST_SourcePath.clear()
        self.widget.LIST_Status.clear()

    def statusContextMenu(self, QPos):
        # Setup the right-click context menu for the LIST_Status listwidget.
        #region
        currentRow = self.widget.LIST_Status.currentRow()
        if currentRow == -1:
            return

        sourceFilePath = self.widget.LIST_SourcePath.item(currentRow).text()
        assetNamePreConfigure = sourceFilePath.split("/")[-1] # i.e. SK_Beech.fbx or T_SMG_UMP_RTYE_GreySlush_BC.tga
        if assetNamePreConfigure.endswith('fbx'):
            assetName = assetNamePreConfigure.replace('.fbx','') # i.e. SK_Beech
        elif assetNamePreConfigure.endswith('tga'):
            assetName = assetNamePreConfigure.replace('.tga','') # i.e. T_SMG_UMP_RTYE_GreySlush_BC
        elif assetNamePreConfigure.endswith('png'):
            assetName = assetNamePreConfigure.replace('.png','') # i.e. TX_Avatar_Soldier0001

        self.contextMenu = QtWidgets.QMenu()
        menuForceReimport = self.contextMenu.addAction("Force Reimport - %s" % (assetName))
        menuForceAllReimport = self.contextMenu.addAction("Force All Reimport")
        self.contextMenu.addSeparator()
        clearErrorItems = self.contextMenu.addAction("Clear Erroneous Items")
        clearAllItems = self.contextMenu.addAction("Clear All Items")
        self.connect(menuForceReimport, QtCore.SIGNAL("triggered()"), self.forceReimportMenuItemClicked)
        self.connect(menuForceAllReimport, QtCore.SIGNAL("triggered()"), self.forceAllReimportMenuItemClicked)
        self.connect(clearErrorItems, QtCore.SIGNAL("triggered()"), self.clearErrorItemsClicked)
        self.connect(clearAllItems, QtCore.SIGNAL("triggered()"), self.clearLists)
        parentPosition = self.widget.LIST_Status.mapToGlobal(QtCore.QPoint(0, 0))
        self.contextMenu.move(parentPosition + QPos)
        self.contextMenu.show()
        #endregion

    def fileBrowserContextMenu(self, QPos):
        # Setup the right-click context menu for the file browser TreeView
        #region
        self.fbContextMenu = QtWidgets.QMenu()
        selected = self.widget.TV_FileBrowse.selectedIndexes()

        for index in selected:
            if index.column() == 0:
                addItems = self.fbContextMenu.addAction("Add Items to Import")
                self.fbContextMenu.addSeparator()
                expand = self.fbContextMenu.addAction("Expand")
                expandAll = self.fbContextMenu.addAction("Expand All")
                collapseFolder = self.fbContextMenu.addAction("Collapse")
                collapseAllFolder = self.fbContextMenu.addAction("Collapse All")
                self.connect(addItems, QtCore.SIGNAL("triggered()"), self.prepareToAddSelectedFilesToLists)
                self.connect(expand, QtCore.SIGNAL("triggered()"), self.expandMenuItemClicked)
                self.connect(expandAll, QtCore.SIGNAL("triggered()"), self.expandAllMenuItemClicked)
                self.connect(collapseFolder, QtCore.SIGNAL("triggered()"), self.collapseMenuItemClicked)
                self.connect(collapseAllFolder, QtCore.SIGNAL("triggered()"), self.collapseAllMenuItemClicked)
                break

        parentPosition = self.widget.TV_FileBrowse.mapToGlobal(QtCore.QPoint(0, 0))
        self.fbContextMenu.move(parentPosition + QPos)
        self.fbContextMenu.show()
        #endregion

    def forceReimportMenuItemClicked(self):
        # Called when selecting Force Reimport menu item from the LIST_Status context menu.
        #region
        currentStatusRow = self.widget.LIST_Status.currentRow()
        filePostImportStatus = self.widget.LIST_Status.item(currentStatusRow).text()

        if filePostImportStatus == 'ERROR' and CustomImporterFunctions.ue4PathError[currentStatusRow] == 'True':
            self.widget.LIST_Status.item(currentStatusRow).setBackground(QtGui.QColor("#dcdcdc"))
            self.widget.LIST_Status.item(currentStatusRow).setTextColor(QtCore.Qt.black)
            self.widget.LIST_Status.item(currentStatusRow).setText('PENDING REIMPORT')
            self.widget.LIST_UE4Path.item(currentStatusRow).setTextColor(QtCore.Qt.black)
            self.widget.LIST_UE4Path.item(currentStatusRow).setToolTip('Asset is being reimported and will override existing asset.')
        #endregion

    def forceAllReimportMenuItemClicked(self):
        # Called when selecting Force All Reimport menu item from the LIST_Status context menu.
        #region
        assetCount = self.widget.LIST_Status.count()
        for rowIndex in range(assetCount):
            filePostImportStatus = self.widget.LIST_Status.item(rowIndex).text()
            if filePostImportStatus == 'ERROR' and CustomImporterFunctions.ue4PathError[rowIndex] == 'True':
                self.widget.LIST_Status.item(rowIndex).setBackground(QtGui.QColor("#dcdcdc"))
                self.widget.LIST_Status.item(rowIndex).setTextColor(QtCore.Qt.black)
                self.widget.LIST_Status.item(rowIndex).setText('PENDING REIMPORT')
                self.widget.LIST_UE4Path.item(rowIndex).setTextColor(QtCore.Qt.black)
                self.widget.LIST_UE4Path.item(rowIndex).setToolTip('Asset is being reimported and will override existing asset.')
        #endregion

    def clearErrorItemsClicked(self):
        # Called when selecting the Clear Error Items menu item from the LIST_Status context menu.
        #region
        assetCount = self.widget.LIST_Status.count()
        errorCount = []

        for rowIndex in range(0,assetCount):
            filePostImportStatus = self.widget.LIST_Status.item(rowIndex).text()
            if (filePostImportStatus == 'ERROR' or filePostImportStatus == 'ERROR, SKIPPED'):
                errorCount.append(rowIndex)

        if len(errorCount) > 0:
            self.widget.LIST_Status.takeItem(errorCount[0])
            self.widget.LIST_UE4Path.takeItem(errorCount[0])
            self.widget.LIST_SourcePath.takeItem(errorCount[0])
            self.clearErrorItemsClicked()
        #endregion

    def expandMenuItemClicked(self):
        # Called when selecting the Expand menu item from the file browser TreeView context menu and expands selected folders by 1 level
        selected = self.widget.TV_FileBrowse.selectedIndexes()

        for index in selected:
            if index.column() == 0:
                self.widget.TV_FileBrowse.setExpanded(index, True)

    def expandAllMenuItemClicked(self):
        # Called when selecting the Expand All menu item from the file browser TreeView context menu and recursively expands selected folders.
        selected = self.widget.TV_FileBrowse.selectedIndexes()

        for index in selected:
            if index.column() == 0:
                self.fetchAndExpand(index)

    def fetchAndExpand(self, folderIndex):
        # Called by expandAllMenuItemClicked() to load subfolders for recursive expansion.
        #region
        if not folderIndex:
            return

        self.widget.TV_FileBrowse.setExpanded(folderIndex, True)
        childCount = self.model.rowCount(folderIndex)

        for i in range(childCount):
            child = folderIndex.child(i, 0)
            self.fetchAndExpand(child)

        if not self.widget.TV_FileBrowse.isExpanded(folderIndex):
            self.widget.TV_FileBrowse.setExpanded(folderIndex, True)
        #endregion

    def collapseMenuItemClicked(self):
        # Called when seleecting the Collapse menu item from the file browser TreeVIew context menu and collapses selected folders by 1 level
        selected = self.widget.TV_FileBrowse.selectedIndexes()

        for index in selected:
            if index.column() == 0:
                self.widget.TV_FileBrowse.setExpanded(index, False)

    def collapseAllMenuItemClicked(self):
        # Called when seleecting the Collapse All menu item from the file browser TreeVIew context menu and collapses all folders.
        self.widget.TV_FileBrowse.collapseAll()

    def prepareToAddSelectedFilesToLists(self):
        # Called when user clicks on Add File button with files selected in file browser TreeView and starts the process of populating the list widgets.
        #region
        selected = self.widget.TV_FileBrowse.selectedIndexes()
        uiTexturePathTokens = ['Avatars', 'Banners', 'Frames', 'Thumbnails', 'MetaArt']

        for index in selected:
            if index.column() == 0:
                sourceFilePath = self.model.filePath(index)

                if CustomImporterFunctions.assetImportType == 'UITextures' and not any(token in sourceFilePath for token in uiTexturePathTokens) or 'TEMPLATE' in sourceFilePath:
                    unreal.log_error('No support exists to import UI textures outside of the Avatars, Banners, Frames, Thumbnail, MetaArt directories.')
                    continue

                if sourceFilePath.endswith('.png') or sourceFilePath.endswith('.tga') or sourceFilePath.endswith('.fbx'):
                    # Validate that the source file path and ue4destination path are valid or erroneous.
                    ue4_destinationPath, sourceErrorMsg, ue4ErrorMsg = CustomImporterFunctions.validatePaths(sourceFilePath)
                    # Proceed with populating list widgets.
                    self.addFilesToLists(sourceFilePath, ue4_destinationPath, sourceErrorMsg, ue4ErrorMsg)
        #endregion

    def importAssetFiles(self):
        # Called when the user clicks on the Import button and starts the import process.
        #region
        assetCount = self.widget.LIST_Status.count()
        ue4DestinationFolderList = []
        tempFolderList = []
        assetNameList = []

        # Check status of files that were added.  If any are ERROR/ERROR_SKIPPED, SKIPPED or SUCCESS, they should not be imported again.
        for rowIndex in range(assetCount):
            filePostImportStatus = self.widget.LIST_Status.item(rowIndex).text()
            if filePostImportStatus == 'ERROR, SKIPPED' or filePostImportStatus == 'IMPORT SUCCESS' or filePostImportStatus == 'REIMPORT SUCCESS':
                continue
            elif filePostImportStatus == 'ERROR':
                    self.widget.LIST_Status.item(rowIndex).setText('ERROR, SKIPPED')
                    continue
            else:
                sourceFilePath = self.widget.LIST_SourcePath.item(rowIndex).text()
                print("sourceFilePath of Asset Being Processed - " + str(sourceFilePath))

                # Extract the file name and strip out the file extension to get the asset name.
                assetNamePreConfigure = sourceFilePath.split("/")[-1] # i.e. SK_Beech.fbx or T_SMG_UMP_RTYE_GreySlush_BC.tga
                if assetNamePreConfigure.endswith('fbx'):
                    assetName = assetNamePreConfigure.replace('.fbx','') # i.e. SK_Beech
                elif assetNamePreConfigure.endswith('tga'):
                    assetName = assetNamePreConfigure.replace('.tga','') # i.e. T_SMG_UMP_RTYE_GreySlush_BC
                elif assetNamePreConfigure.endswith('png'):
                    assetName = assetNamePreConfigure.replace('.png','') # i.e. T_SMG_UMP_RTYE_GreySlush_BC

                ue4_destinationPath = self.widget.LIST_UE4Path.item(rowIndex).text()
                print("ue4_destinationPath - " + str(ue4_destinationPath))

                # Create the full UE4 path to the asset
                assetPath = ue4_destinationPath + '%s.%s' % (assetName, assetName)
                print("assetPath - " + str(assetPath))
                tempFolderList.append(assetPath)
                for path in tempFolderList:
                    if path not in ue4DestinationFolderList:
                        ue4DestinationFolderList.append(path)

                # Call functions that will process the actual import process, set any custom properties, then save everything in the directory (only if dirtied).
                if CustomImporterFunctions.assetImportType == '':
                    unreal.log_error('No asset import type specified.')
                elif CustomImporterFunctions.assetImportType == 'Characters':
                    CharacterFBXImporter.executeAssetImport(sourceFilePath, ue4_destinationPath, filePostImportStatus)
                    CustomImporterFunctions.saveAssetsInDirectory(ue4_destinationPath)
                elif CustomImporterFunctions.assetImportType == 'Weapons':
                    WeaponFBXImporter.executeAssetImport(sourceFilePath, ue4_destinationPath, filePostImportStatus)
                    CustomImporterFunctions.saveAssetsInDirectory(ue4_destinationPath)
                elif CustomImporterFunctions.assetImportType == 'Gadgets':
                    GadgetFBXImporter.executeAssetImport(sourceFilePath, ue4_destinationPath, filePostImportStatus)
                    CustomImporterFunctions.saveAssetsInDirectory(ue4_destinationPath)
                elif CustomImporterFunctions.assetImportType == 'Vehicles':
                    VehicleFBXImporter.executeAssetImport(sourceFilePath, ue4_destinationPath, filePostImportStatus)
                    CustomImporterFunctions.saveAssetsInDirectory(ue4_destinationPath)
                elif (CustomImporterFunctions.assetImportType == 'CharacterSkins' or CustomImporterFunctions.assetImportType == 'WeaponSkins' or
                        CustomImporterFunctions.assetImportType == 'GadgetSkins' or CustomImporterFunctions.assetImportType == 'VehicleSkins' or
                        CustomImporterFunctions.assetImportType == 'UITextures'):
                    importlib.reload(SkinImportCreation)
                    SkinImportCreation.executeAssetImport(sourceFilePath, ue4_destinationPath, filePostImportStatus)
                    assetNameList.append(assetName)

                # Change status text of files that were imported/reimported successfully.
                if filePostImportStatus == 'PENDING IMPORT':
                    self.widget.LIST_Status.item(rowIndex).setText('IMPORT SUCCESS')
                    self.widget.LIST_Status.item(rowIndex).setBackground(QtCore.Qt.green)
                elif filePostImportStatus == 'PENDING REIMPORT':
                    self.widget.LIST_Status.item(rowIndex).setText('REIMPORT SUCCESS')
                    self.widget.LIST_Status.item(rowIndex).setBackground(QtCore.Qt.green)
                else:
                    continue

        if (CustomImporterFunctions.assetImportType == 'CharacterSkins' or CustomImporterFunctions.assetImportType == 'WeaponSkins' or
                CustomImporterFunctions.assetImportType == 'GadgetSkins' or CustomImporterFunctions.assetImportType == 'VehicleSkins'):
            matInstFullPath = SkinImportCreation.setupSkinMaterials(ue4DestinationFolderList, assetNameList, CustomImporterFunctions.assetImportType)
            # Set CMS metadata tag for skin assets
            CustomImporterFunctions.setCMSInclusionTag(matInstFullPath)
            # Create new BP (parent=EquipmentSkinLinkage) if it doesn't already exist.  Name BP after unique skin name.
            #skinBlueprintName, skinBlueprintPath, blueprintFullPath = SkinImportCreation.createSkinBlueprintNameAndPath(matInstFullPath)
            #doesBlueprintExist = unreal.EditorAssetLibrary.does_asset_exist(blueprintFullPath)
            #if not doesBlueprintExist:
            #    SkinImportCreation.createSkinBlueprintUasset(skinBlueprintName, skinBlueprintPath)
            #    SkinImportCreation.setSkinBlueprintProperties(matInstFullPath, blueprintFullPath)
            #else:
            #    SkinImportCreation.validateSkinBlueprintProperties()
        elif CustomImporterFunctions.assetImportType == 'UITextures':
            UITextureImporter.setTextureProperties(ue4DestinationFolderList)
            CustomImporterFunctions.saveAssets(ue4DestinationFolderList)

            # Set CMS metadata tag for player profile UI assets
            for fullAssetPath in ue4DestinationFolderList:
                if "Banners" in fullAssetPath or "Avatars" in fullAssetPath or "Frames" in fullAssetPath:
                    CustomImporterFunctions.setCMSInclusionTag(fullAssetPath)

        CustomImporterFunctions.saveAssetsInDirectory(ue4_destinationPath)

        # Select all the meshes that were imported by the tool in the content browser so user can see all imported assets at once.
        unreal.EditorAssetLibrary.sync_browser_to_objects(ue4DestinationFolderList)

        # For non-Skin and non-UI asset types, open the asset up for review in the editor windows.
        if not (CustomImporterFunctions.assetImportType == 'CharacterSkins' or CustomImporterFunctions.assetImportType == 'WeaponSkins' or
            CustomImporterFunctions.assetImportType == 'GadgetSkins' or CustomImporterFunctions.assetImportType == 'VehicleSkins' or
            CustomImporterFunctions.assetImportType == 'UITextures'):
            assetRegistry = unreal.AssetRegistryHelpers.get_asset_registry()
            assetObjects = []
            for assetStr in ue4DestinationFolderList:
                meshData = assetRegistry.get_asset_by_object_path(assetStr)
                meshObject = meshData.get_asset()
                assetObjects.append(meshObject)
            assetEditorSub = unreal.AssetEditorSubsystem()
            assetEditorSub.open_editor_for_assets(assetObjects)
        #endregion

    def addFilesToLists(self, file, ue4_destinationPath, sourceErrorMsg, ue4ErrorMsg):
        # Function to add selected files from file browser to list widget
        #region
        fbxListCount = self.widget.LIST_SourcePath.count()
        if fbxListCount == 0:
            # If the source path list is empty, go ahead and add the selected file.
            self.widget.LIST_SourcePath.addItem(file)
            self.widget.LIST_UE4Path.addItem(ue4_destinationPath)
            
            if sourceErrorMsg != '' or ue4ErrorMsg != '':
                self.widget.LIST_Status.addItem('ERROR')
                self.widget.LIST_Status.item(0).setBackground(QtCore.Qt.red)
                self.widget.LIST_Status.item(0).setTextColor(QtCore.Qt.white)
            else:
                self.widget.LIST_Status.addItem('PENDING IMPORT')

            if sourceErrorMsg == 'incorrectSourceDirectory':
                self.widget.LIST_SourcePath.item(0).setTextColor(QtCore.Qt.red)
                self.widget.LIST_Status.item(0).setToolTip('Source file(s) located in incorrect directory.  See output log for Confluence guidelines page on where to store source files.')
            if ue4ErrorMsg == 'uassetAlreadyExists':
                CustomImporterFunctions.ue4PathError.append('True')
                self.widget.LIST_UE4Path.item(0).setTextColor(QtCore.Qt.red)
                self.widget.LIST_Status.item(0).setToolTip('Asset already exists!  Right-click in the STATUS area and select Force Reimport to reimport and overwrite the existing asset.')
            elif ue4ErrorMsg == "noSupportExists":
                CustomImporterFunctions.ue4PathError.append('True')
                self.widget.LIST_UE4Path.item(0).setTextColor(QtCore.Qt.red)
                self.widget.LIST_Status.item(0).setToolTip('No support exists to import this asset.  Please reach out to gawong on Slack if this is in error.')
            else:
                CustomImporterFunctions.ue4PathError.append('False')

        else:
            # Items exist in the FBX list.  Loop through all to make sure you don't add a dup line item.
            isDupFound = False
            for x in range(fbxListCount):
                fbxItem = self.widget.LIST_SourcePath.item(x).text()
                if file == fbxItem:
                    isDupFound = True
                    break
                else:
                    continue

            if isDupFound == False:
                self.widget.LIST_SourcePath.addItem(file)
                self.widget.LIST_UE4Path.addItem(ue4_destinationPath)

                if sourceErrorMsg != '' or ue4ErrorMsg != '':
                    self.widget.LIST_Status.addItem('ERROR')
                    rowIndex = self.widget.LIST_Status.count() - 1
                    self.widget.LIST_Status.item(rowIndex).setBackground(QtCore.Qt.red)
                    self.widget.LIST_Status.item(rowIndex).setTextColor(QtCore.Qt.white)
                else:
                    self.widget.LIST_Status.addItem('PENDING IMPORT')

                if sourceErrorMsg == 'incorrectSourceDirectory':
                    self.widget.LIST_SourcePath.item(rowIndex).setTextColor(QtCore.Qt.red)
                    self.widget.LIST_Status.item(rowIndex).setToolTip('FBX lives in the wrong directory.  Can only be imported into Developers folder.  Verify FBX source file path, then try again.')
                if ue4ErrorMsg == 'uassetAlreadyExists':
                    CustomImporterFunctions.ue4PathError.append('True')
                    self.widget.LIST_UE4Path.item(rowIndex).setTextColor(QtCore.Qt.red)
                    self.widget.LIST_Status.item(rowIndex).setToolTip('Asset already exists!  Right-click and select Force Reimport to reimport and overwrite the existing asset.')
                else:
                    CustomImporterFunctions.ue4PathError.append('False')
        #endregion

app = None
if not QtWidgets.QApplication.instance():
    app = QtWidgets.QApplication(sys.argv)