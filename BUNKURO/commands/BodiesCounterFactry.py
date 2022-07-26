# Author-kantoku
# Description-
# Fusion360API Python

import adsk.core
import adsk.fusion
import traceback
import csv
from collections import Counter

_app: adsk.core.Application = None
_ui:adsk.core.UserInterface = None

SEPARATORS = [
    '@',
    ':',
    '|',
    '%',
    '&',
    '#',
]
COMP_SPACE = 20
BODY_SPACE = 15

class BodiesCounterFactry:
    def __init__(self) -> None:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        self.bodiesInfo = []
        self.update()

    def update(self):
        self.bodiesInfo = []
        self._setBodiesInfos()

    def getBodiesCount(self) -> str:
        if len(self.bodiesInfo) < 1:
            msg = '-- 表示されているボディがありません --'
        else:
            msg = f'ボディ数{len(self._getShowBodies())}({len(self.bodiesInfo)}種類)'
        return msg

    def dumpTxtCommandsWindow(self):
        if len(self.bodiesInfo) < 1:
            _app.log('-- 表示されているボディがありません --')
            return

        txts = [
            f'*** {self.getBodiesCount()} ***',
            f"{'コンポート名'.ljust(COMP_SPACE)}:{'ボディ名'.ljust(BODY_SPACE)} --- 個数"
        ]
        for info in self.bodiesInfo:
            txts.append(
                f"{info['comp'].ljust(COMP_SPACE)}:{info['body'].ljust(BODY_SPACE)} --- {info['count']}"
            )
        txts.append('')

        _app.log('\n'.join(txts))

    def exportCsv(self, path: str):
        txts = [[info['comp'], info['body'], info['count']] for info in self.bodiesInfo]

        with open(path, 'w', newline="") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerows(txts)

        _app.log(f'[{path}] を出力しました。')


    # *****************
    def _getSeparator(self, lst: list) -> str:
        txt = ''.join(lst)
        for sep in SEPARATORS:
            if not sep in txt:
                return sep

        raise Exception

    def _setBodiesInfos(self):
        des: adsk.fusion.Design = _app.activeProduct
        root: adsk.fusion.Component = des.rootComponent

        bodies = self._getShowBodies()
        compNames = []
        for b in bodies:
            try:
                compNames.append(b.assemblyContext.component.name)
            except:
                compNames.append(root.name)

        sep = self._getSeparator(
            [f'{c}{b.name}' for b, c in zip(bodies, compNames)]
        )

        res = Counter(
            [f'{c}{sep}{b.name}' for b, c in zip(bodies, compNames)]
        )

        self.bodiesInfo = []
        for key in res.keys():
            info = key.split(sep)
            self.bodiesInfo.append(
                {
                    'comp':info[0],
                    'body':info[1],
                    'count':res[key],
                }
            )

    def _getShowBodies(self) -> list:
        des: adsk.fusion.Design = _app.activeProduct
        root: adsk.fusion.Component = des.rootComponent

        # 表示されているボディの取得
        showBodies: adsk.core.ObjectCollection = root.findBRepUsingPoint(
            adsk.core.Point3D.create(0,0,0),
            adsk.fusion.BRepEntityTypes.BRepBodyEntityType,
            1000000000000,
            True
        )

        return [b for b in showBodies]