# Author-kantoku
# Description-コンポーネント毎に分割してクローン作るよ!
# Fusion360API Python

import adsk.core
import traceback

try:
    from . import config
    from .apper import apper

    from .commands.BUNKUROCore import BUNKUROCore

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

except:
    app = adsk.core.Application.get()
    ui = app.userInterface
    if ui:
        ui.messageBox('Initialization: {}'.format(traceback.format_exc()))


def run(context):
    my_addin.run_app()


def stop(context):
    my_addin.stop_app()
