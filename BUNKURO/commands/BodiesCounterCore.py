# Author-kantoku
# Description-
# Fusion360API Python

import adsk.core
import adsk.fusion

import time
from ..apper import apper
from .. import config
from .ktkCmdInputHelper import TextBoxCommandInputHelper, BoolValueCommandInputHelper
from .BodiesCounterFactry import BodiesCounterFactry

_fact: 'BodiesCounterFactry' = None

_info = TextBoxCommandInputHelper(
    'infoTxt',
    '表示ボディ',
    '',
    1,
    True)

_clearBtn = BoolValueCommandInputHelper(
    'clearbool',
    'テキストコマンドクリア',
    False,
    'commands/resources/BodiesCounterFactry/clearBtn',
)

_dumpBtn = BoolValueCommandInputHelper(
    'dumpbool',
    'テキストコマンドに出力',
    False,
    'commands/resources/BodiesCounterFactry/dumpBtn',
)

_csvBtn = BoolValueCommandInputHelper(
    'csvbool',
    'CSVファイル出力',
    False,
    'commands/resources/BodiesCounterFactry/csvBtn',
)


_handlers = []

class BodiesCounterCore(apper.Fusion360CommandBase):

    def on_preview(self, command, inputs, args, input_values):
        pass

    def on_destroy(self, command, inputs, reason, input_values):
        pass

    def on_input_changed(self, command, inputs, changed_input, input_values):
        global _fact,_clearBtn, _dumpBtn, _csvBtn

        if changed_input == _clearBtn.obj:
            adsk.core.Application.get().log(u'TextCommandWindow.Clear')

        if changed_input == _dumpBtn.obj:
            _fact.dumpTxtCommandsWindow()

        if changed_input == _csvBtn.obj:
            path = getExportPath()
            if len(path) < 1:
                return
            _fact.exportCsv(path)

    def on_execute(self, command, inputs, args, input_values):
        pass

    def on_create(self, command: adsk.core.Command, inputs):
        command.isOKButtonVisible = False
        
        global _fact
        _fact = BodiesCounterFactry()

        global _info
        _info.register(inputs)
        _info.obj.text = _fact.getBodiesCount()

        global _clearBtn
        _clearBtn.register(inputs)

        global _dumpBtn
        _dumpBtn.register(inputs)
        
        global _csvBtn
        _csvBtn.register(inputs)

        global _handlers
        onCommandTerminated = MyCommandTerminatedHandler()
        adsk.core.Application.get().userInterface.commandTerminated.add(onCommandTerminated)
        _handlers.append(onCommandTerminated)

    # expansion
    def on_validate(self, command, inputs, args, input_values):
        pass

    # expansion
    def on_preselect(self, command, inputs, args, pre_input, input_values):
        pass


class MyCommandTerminatedHandler(adsk.core.ApplicationCommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args: adsk.core.ApplicationCommandEventArgs):
        global _fact
        _fact.update()

        global _info
        _info.obj.text = _fact.getBodiesCount()


def getExportPath(initialFilename='') -> str:
    ui: adsk.core.UserInterface = adsk.core.Application.get().userInterface

    dlg: adsk.core.FileDialog = ui.createFileDialog()
    dlg.title = 'CSVファイルとして保存'
    dlg.isMultiSelectEnabled = False
    dlg.filter = 'CSVファイル(*.csv)'
    if len(initialFilename) > 0:
        dlg.initialFilename = initialFilename

    if dlg.showSave() != adsk.core.DialogResults.DialogOK:
        return ''

    return dlg.filename