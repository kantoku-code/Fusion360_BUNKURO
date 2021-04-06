# Author-kantoku
# Description-コンポーネント毎に分割してクローン作るよ!
# Fusion360API Python

import adsk.core
import adsk.fusion
import traceback
# import time
import re

_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_cancelFG = False

def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        BUNKUROFactry.createCloneOccurrences('CloneCompDoc',False,False)

    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class BUNKUROFactry:
    @staticmethod
    def getActiveDocumentInfo():
        app :adsk.core.Application = adsk.core.Application.get()
        des = adsk.fusion.Design.cast(app.activeProduct)
        root :adsk.fusion.Component = des.rootComponent
        actDoc :adsk.fusion.FusionDocument = app.activeDocument
        fact = BUNKUROFactry

        isSave = True if actDoc.dataFile else False
        isModified = actDoc.isModified
        bodiesCount = len(fact._getShowBodyList(root))
        occCount = root.occurrences.count

        return (isSave, isModified ,bodiesCount, occCount)

    @staticmethod
    def createCloneOccurrences(
        folderName :str,
        combine: bool = True,
        save :bool = True):

        def updeteProgress(
            prog :adsk.core.ProgressDialog,
            msg :str):

            prog.progressValue += 1
            prog.message = f'Processing {msg} ....'
            adsk.doEvents()
            if progress.wasCancelled:
                global _cancelFG
                _cancelFG = True
                return

        rootLights = []
        occLights = []
        try:
            # Preparation
            app :adsk.core.Application = adsk.core.Application.get()
            des = adsk.fusion.Design.cast(app.activeProduct)
            root :adsk.fusion.Component = des.rootComponent
            vp :adsk.core.Viewport = app.activeViewport

            fact = BUNKUROFactry

            # --start--
            actDoc :adsk.fusion.FusionDocument = app.activeDocument
            dumpMsg(f'--- {actDoc.name} start --- ')

            # show body check
            if len(fact._getShowBodyList(root)) < 1:
                return

            # DataFolder
            dataFolder :adsk.core.DataFolder = None
            fileNames = [] #データフォルダー内のファイル名リスト
            if save:
                dataFolder = fact._getDataFolder(actDoc, folderName)
                if not dataFolder:
                    dumpMsg(f'!! dataFolder  Failure')
                    return
                
                # データファイル名リスト作成
                fileNames = fact._getDateFileNameList(dataFolder)

            # light data
            rootLights, occLights = fact._getLightBulbOnMap(root)

            # -root-
            dumpMsg(f'- root start - ')

            # progress
            ui :adsk.core.UserInterface = app.userInterface
            progress :adsk.core.ProgressDialog = ui.createProgressDialog()
            progress.isCancelButtonShown = True
            progress.show('-- BUNKURO --', '', 0, len(occLights) + 1)
            updeteProgress(progress, 'Root Component')
            global _cancelFG
            if _cancelFG:
                _cancelFG = not _cancelFG
                return

            # light off occ
            fact._changeLights(occLights, False)

            # doc name
            cloneName = actDoc.name + '_root'

            # get show bodies
            bodies = fact._getShowBodyList(root)

            # clone bodies
            if len(bodies) > 0:
                newDoc = fact._initCloneBodies(bodies, combine, cloneName)
                vp.fit()
                if dataFolder:
                    newName = fact._saveDoc(newDoc, dataFolder, cloneName, fileNames)
                    fileNames.append(newName)

            # light off
            fact._changeLights(rootLights, False)

            dumpMsg(f'-- root finish -- ')

            # -occ-
            occ :adsk.fusion.Occurrence
            for occ, light in occLights:

                if not light:
                    continue

                updeteProgress(progress, occ.name)
                # global _cancelFG
                if _cancelFG:
                    _cancelFG = not _cancelFG
                    return

                dumpMsg(f'-- {occ.name} start -- ')

                # light on
                occ.isLightBulbOn = True

                # doc name
                cloneName = f'{actDoc.name}_{occ.name}'

                # get show bodies
                bodies = fact._getShowBodyList(root)

                # clone bodies
                if len(bodies) > 0:
                    newDoc = fact._initCloneBodies(bodies, combine, cloneName)
                    vp.fit()
                    if dataFolder:
                        newName = fact._saveDoc(newDoc, dataFolder, cloneName, fileNames)
                        fileNames.append(newName)

                # light off
                occ.isLightBulbOn = False

                dumpMsg(f'-- {occ.name} finish -- ')

            dumpMsg(f'--- {actDoc.name} finish --- ')
            # actDoc.activate()

        except:
            dumpMsg('Failed:\n{}'.format(traceback.format_exc()))
        finally:
            try:
               BUNKUROFactry._changeLights(rootLights, False, True)
               BUNKUROFactry._changeLights(occLights, False, True)
            except:
                pass


    # -- support function --

    # 名前の重複を避ける為の名前取得
    @staticmethod
    def _getDateFileNameList(
        folder :adsk.core.DataFolder) -> list:

        fileNames = [f.name for f in folder.dataFiles]
        return fileNames

    @staticmethod
    def _getDataFolder(
        doc :adsk.fusion.FusionDocument,
        name :str) -> adsk.core.DataFolder:

        try:  
            rootFolder :adsk.core.DataProject = doc.dataFile.parentProject.rootFolder
            folders :adsk.core.DataFolders = rootFolder.dataFolders
            folder :adsk.core.DataFolder = folders.itemByName(name)

            if folder:
                return folder

            newFolder :adsk.core.DataFolder = folders.add(name)
            return newFolder
        except:
            dumpMsg('!! data folder Failure')

    @staticmethod
    def _getShowBodyList(
        root :adsk.fusion.Component) -> list:

        bodyLst = root.findBRepUsingPoint(
        adsk.core.Point3D.create(0,0,0),
        adsk.fusion.BRepEntityTypes.BRepBodyEntityType,
        10000000000000,
        True)

        return bodyLst

    @staticmethod
    def _changeLights(
        lightData: list,
        show: bool = False,
        restore: bool = False
        ):

        if restore:
            for o, light in lightData:
                o.isLightBulbOn = light
            return

        for o, light in lightData:
            if not light == show:
                o.isLightBulbOn = show

    @staticmethod
    def _getLightBulbOnMap(
        root :adsk.fusion.Component):

        # root bodies
        rootLights = [(b, b.isLightBulbOn) for b in root.bRepBodies]
        occLights = [(o, o.isLightBulbOn) for o in root.occurrences]
        

        return rootLights, occLights

    @staticmethod
    def _initCloneBodies(
        bodyLst :list,
        combine :bool,
        name :str) -> adsk.fusion.FusionDocument:

        app :adsk.core.Application = adsk.core.Application.get()

        # clone body
        tmpMgr = adsk.fusion.TemporaryBRepManager.get()
        clones = []
        for body in bodyLst:
            clones.append(tmpMgr.copy(body))

        # new doc
        newDoc :adsk.fusion.FusionDocument = app.documents.add(
            adsk.core.DocumentTypes.FusionDesignDocumentType)
        newDoc.activate()
        newDoc.name = name
        newDoc.design.designType = adsk.fusion.DesignTypes.DirectDesignType

        # add clone
        bodies :adsk.fusion.BRepBodies = newDoc.design.rootComponent.bRepBodies
        for body in clones:
            bodies.add(body)

        # Combine
        des = adsk.fusion.Design.cast(app.activeProduct)
        root :adsk.fusion.Component = des.rootComponent
        feats :adsk.fusion.Features = root.features

        combFeats :adsk.fusion.CombineFeatures = feats.combineFeatures

        if combine:
            bodyLst = [b for b in bodies]
            if bodies.count > 1:
                try:
                    base = bodyLst[0]
                    tools = adsk.core.ObjectCollection.create()
                    [tools.add(b) for b in bodyLst[1:]]

                    combIpt = combFeats.createInput(base, tools)
                    combFeats.add(combIpt)
                except:
                    dumpMsg('!! Combine Failure')
                    pass

        newDoc.design.designType = adsk.fusion.DesignTypes.ParametricDesignType

        return newDoc

    @staticmethod
    def _saveDoc(
        saveDoc :adsk.fusion.FusionDocument,
        folder :adsk.core.DataFolder,
        fileName :str,
        fileNames :list) -> str:

        # 名前の重複を避ける為の名前取得
        def getUniqueName(
            fileNames :list,
            fileName :str) -> str:

            fileName = re.sub(r'[\\|/|:|?|.|"|<|>|\|]', '-', fileName)

            if not fileName in fileNames:
                return fileName

            counter = 1
            tmpName = ''
            while True:
                tmpName = fileName + '_' + str(counter)

                if not tmpName in fileNames:
                    return tmpName
                
                counter +=1

        unique = getUniqueName(fileNames, fileName)
        dumpMsg(f'-> clone doc name:{unique}')

        res = saveDoc.saveAs(unique, folder, 'Created with add-ins', '')
        if not res:
            dumpMsg('!! document saveed Failure')
        
        return unique


def dumpMsg(msg :str):
    adsk.core.Application.get().userInterface.palettes.itemById('TextCommands').writeText(str(msg))