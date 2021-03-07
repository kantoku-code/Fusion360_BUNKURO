# Author-kantoku
# Description-コンポーネント毎に分割してクローン作るよ!
# Fusion360API Python

import adsk.core
import adsk.fusion

from ..apper import apper
from .. import config
from .ktkCmdInputHelper import TextBoxCommandInputHelper, BoolValueCommandInputHelper
from .BUNKUROFactry import BUNKUROFactry

_FOLDERNAME = 'BUNKURO'

_info = TextBoxCommandInputHelper(
    'infoTxt',
    '情報',
    '',
    4,
    True)

_save = BoolValueCommandInputHelper(
    'savebool',
    '保存',
    True)

_comb = BoolValueCommandInputHelper(
    'combbool',
    '結合',
    True)

class BUNKUROCore(apper.Fusion360CommandBase):

    def on_preview(self, command, inputs, args, input_values):
        pass

    def on_destroy(self, command, inputs, reason, input_values):
        pass

    def on_input_changed(self, command, inputs, changed_input, input_values):
        pass

    def on_execute(self, command, inputs, args, input_values):
        global _FOLDERNAME, _save, _comb
        BUNKUROFactry.createCloneOccurrences(
            _FOLDERNAME, _comb.obj.value, _save.obj.value)

        _save.updateValue()
        _comb.updateValue()
        adsk.core.Application.get().userInterface.messageBox('終了')

    def on_create(self, command, inputs):
        command.isPositionDependent = True
        
        docInfo = BUNKUROFactry.getActiveDocumentInfo()

        global _info, _save, _comb
        _save.register(inputs)
        _comb.register(inputs)
        _info.register(inputs)

        msg = []
        if not docInfo[0]:
            msg.append('ドキュメントが一度も保存されていません')
        if docInfo[1]:
            msg.append('ドキュメントが変更されています')
        if docInfo[2] is None:
            msg.append('表示されているボディが有りません!!')
        else:
            msg.append(f'{docInfo[2]}個のボディが表示されています')
        if docInfo[3]:
            msg.append(f'最大{docInfo[3]+1}個のドキュメントを作成します')
        _info.obj.text = '\n'.join(msg)


    # expansions
    def on_validate(self, command, inputs, args, input_values):
        docInfo = BUNKUROFactry.getActiveDocumentInfo()

        global _save
        if docInfo[2] < 1:
            args.areInputsValid = False
            return

        if not docInfo[0] and _save.obj.value:
            args.areInputsValid = False
            return

    # expansion
    def on_preselect(self, command, inputs, args, pre_input, input_values):
        pass