# Author-kantoku
# Description-コンポーネント毎に分割してクローン作るよ!
# Fusion360API Python

import adsk.core
import traceback

try:
    from . import config
    from .apper import apper

    from .commands.BUNKUROCore import BUNKUROCore
    from .commands.BodiesCounterCore import BodiesCounterCore

    # Create our addin definition object
    my_addin = apper.FusionApp(config.app_name, config.company_name, False)
    my_addin.root_path = config.app_path

    my_addin.add_command(
        'ぶんくろ',
        BUNKUROCore,
        {
            'cmd_description': 'コンポーネント毎に分割してクローン作るよ!',
            'cmd_id': 'bunkuro',
            'workspace': 'FusionSolidEnvironment',
            'toolbar_panel_id': 'UtilityPanel',
            'cmd_resources': 'BUNKURO',
            'command_visible': True,
            'command_promoted': False,
            'create_feature': False,
        }
    )

    my_addin.add_command(
        '部品数',
        BodiesCounterCore,
        {
            'cmd_description': '表示されているボディ数を集計し表示、CSV出力します。',
            'cmd_id': 'bodiesCounter',
            'workspace': 'FusionSolidEnvironment',
            'toolbar_panel_id': 'AssemblePanel',
            'cmd_resources': 'BodiesCounterFactry/cmd',
            'command_visible': True,
            'command_promoted': False,
            'create_feature': False,
        }
    )


except:
    app = adsk.core.Application.get()
    ui = app.userInterface
    if ui:
        ui.messageBox('Initialization: {}'.format(traceback.format_exc()))


def run(context):
    my_addin.run_app()


def stop(context):
    my_addin.stop_app()
