# coding: UTF-8
import sys
bstack1l111ll_opy_ = sys.version_info [0] == 2
bstack1lll11l_opy_ = 2048
bstack111ll11_opy_ = 7
def bstack111l11_opy_ (bstack1ll1lll_opy_):
    global bstack11l11_opy_
    bstack1llll1_opy_ = ord (bstack1ll1lll_opy_ [-1])
    bstack11lll_opy_ = bstack1ll1lll_opy_ [:-1]
    bstack111l11l_opy_ = bstack1llll1_opy_ % len (bstack11lll_opy_)
    bstack1lllllll_opy_ = bstack11lll_opy_ [:bstack111l11l_opy_] + bstack11lll_opy_ [bstack111l11l_opy_:]
    if bstack1l111ll_opy_:
        bstack1l11_opy_ = unicode () .join ([unichr (ord (char) - bstack1lll11l_opy_ - (bstack11ll1l1_opy_ + bstack1llll1_opy_) % bstack111ll11_opy_) for bstack11ll1l1_opy_, char in enumerate (bstack1lllllll_opy_)])
    else:
        bstack1l11_opy_ = str () .join ([chr (ord (char) - bstack1lll11l_opy_ - (bstack11ll1l1_opy_ + bstack1llll1_opy_) % bstack111ll11_opy_) for bstack11ll1l1_opy_, char in enumerate (bstack1lllllll_opy_)])
    return eval (bstack1l11_opy_)
from datetime import datetime, timezone
import os
import builtins
from pathlib import Path
from typing import Any, Tuple, Callable, List
from browserstack_sdk.sdk_cli.bstack1lllll11l1l_opy_ import bstack1lllll1ll1l_opy_, bstack1llllll111l_opy_, bstack1llll1l111l_opy_
from browserstack_sdk.sdk_cli.bstack1lll111ll1l_opy_ import bstack1ll1ll1lll1_opy_
from browserstack_sdk.sdk_cli.bstack1ll1l1l1lll_opy_ import bstack1lll111lll1_opy_
from browserstack_sdk.sdk_cli.bstack1ll1l1ll111_opy_ import bstack1ll1ll1l11l_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1lll11ll111_opy_, bstack1lll1llll1l_opy_, bstack1lll1lll111_opy_, bstack1ll1lll1111_opy_
from json import dumps, JSONEncoder
import grpc
from browserstack_sdk import sdk_pb2 as structs
import sys
import traceback
import time
import json
from bstack_utils.helper import bstack1l1l1ll11ll_opy_, bstack1l1lll1111l_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
bstack1l1ll11l111_opy_ = [bstack111l11_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦቭ"), bstack111l11_opy_ (u"ࠢࡱࡣࡵࡩࡳࡺࠢቮ"), bstack111l11_opy_ (u"ࠣࡥࡲࡲ࡫࡯ࡧࠣቯ"), bstack111l11_opy_ (u"ࠤࡶࡩࡸࡹࡩࡰࡰࠥተ"), bstack111l11_opy_ (u"ࠥࡴࡦࡺࡨࠣቱ")]
bstack1l1ll11l11l_opy_ = bstack1l1lll1111l_opy_()
bstack1l1l1l11l1l_opy_ = bstack111l11_opy_ (u"࡚ࠦࡶ࡬ࡰࡣࡧࡩࡩࡇࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࡵ࠰ࠦቲ")
bstack1l1ll1llll1_opy_ = {
    bstack111l11_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠳ࡶࡹࡵࡪࡲࡲ࠳ࡏࡴࡦ࡯ࠥታ"): bstack1l1ll11l111_opy_,
    bstack111l11_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹ࠴ࡰࡺࡶ࡫ࡳࡳ࠴ࡐࡢࡥ࡮ࡥ࡬࡫ࠢቴ"): bstack1l1ll11l111_opy_,
    bstack111l11_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺ࠮ࡱࡻࡷ࡬ࡴࡴ࠮ࡎࡱࡧࡹࡱ࡫ࠢት"): bstack1l1ll11l111_opy_,
    bstack111l11_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴ࠯ࡲࡼࡸ࡭ࡵ࡮࠯ࡅ࡯ࡥࡸࡹࠢቶ"): bstack1l1ll11l111_opy_,
    bstack111l11_opy_ (u"ࠤࡳࡽࡹ࡫ࡳࡵ࠰ࡳࡽࡹ࡮࡯࡯࠰ࡉࡹࡳࡩࡴࡪࡱࡱࠦቷ"): bstack1l1ll11l111_opy_
    + [
        bstack111l11_opy_ (u"ࠥࡳࡷ࡯ࡧࡪࡰࡤࡰࡳࡧ࡭ࡦࠤቸ"),
        bstack111l11_opy_ (u"ࠦࡰ࡫ࡹࡸࡱࡵࡨࡸࠨቹ"),
        bstack111l11_opy_ (u"ࠧ࡬ࡩࡹࡶࡸࡶࡪ࡯࡮ࡧࡱࠥቺ"),
        bstack111l11_opy_ (u"ࠨ࡫ࡦࡻࡺࡳࡷࡪࡳࠣቻ"),
        bstack111l11_opy_ (u"ࠢࡤࡣ࡯ࡰࡸࡶࡥࡤࠤቼ"),
        bstack111l11_opy_ (u"ࠣࡥࡤࡰࡱࡵࡢ࡫ࠤች"),
        bstack111l11_opy_ (u"ࠤࡶࡸࡦࡸࡴࠣቾ"),
        bstack111l11_opy_ (u"ࠥࡷࡹࡵࡰࠣቿ"),
        bstack111l11_opy_ (u"ࠦࡩࡻࡲࡢࡶ࡬ࡳࡳࠨኀ"),
        bstack111l11_opy_ (u"ࠧࡽࡨࡦࡰࠥኁ"),
    ],
    bstack111l11_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹ࠴࡭ࡢ࡫ࡱ࠲ࡘ࡫ࡳࡴ࡫ࡲࡲࠧኂ"): [bstack111l11_opy_ (u"ࠢࡴࡶࡤࡶࡹࡶࡡࡵࡪࠥኃ"), bstack111l11_opy_ (u"ࠣࡶࡨࡷࡹࡹࡦࡢ࡫࡯ࡩࡩࠨኄ"), bstack111l11_opy_ (u"ࠤࡷࡩࡸࡺࡳࡤࡱ࡯ࡰࡪࡩࡴࡦࡦࠥኅ"), bstack111l11_opy_ (u"ࠥ࡭ࡹ࡫࡭ࡴࠤኆ")],
    bstack111l11_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷ࠲ࡨࡵ࡮ࡧ࡫ࡪ࠲ࡈࡵ࡮ࡧ࡫ࡪࠦኇ"): [bstack111l11_opy_ (u"ࠧ࡯࡮ࡷࡱࡦࡥࡹ࡯࡯࡯ࡡࡳࡥࡷࡧ࡭ࡴࠤኈ"), bstack111l11_opy_ (u"ࠨࡡࡳࡩࡶࠦ኉")],
    bstack111l11_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺ࠮ࡧ࡫ࡻࡸࡺࡸࡥࡴ࠰ࡉ࡭ࡽࡺࡵࡳࡧࡇࡩ࡫ࠨኊ"): [bstack111l11_opy_ (u"ࠣࡵࡦࡳࡵ࡫ࠢኋ"), bstack111l11_opy_ (u"ࠤࡤࡶ࡬ࡴࡡ࡮ࡧࠥኌ"), bstack111l11_opy_ (u"ࠥࡪࡺࡴࡣࠣኍ"), bstack111l11_opy_ (u"ࠦࡵࡧࡲࡢ࡯ࡶࠦ኎"), bstack111l11_opy_ (u"ࠧࡻ࡮ࡪࡶࡷࡩࡸࡺࠢ኏"), bstack111l11_opy_ (u"ࠨࡩࡥࡵࠥነ")],
    bstack111l11_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺ࠮ࡧ࡫ࡻࡸࡺࡸࡥࡴ࠰ࡖࡹࡧࡘࡥࡲࡷࡨࡷࡹࠨኑ"): [bstack111l11_opy_ (u"ࠣࡨ࡬ࡼࡹࡻࡲࡦࡰࡤࡱࡪࠨኒ"), bstack111l11_opy_ (u"ࠤࡳࡥࡷࡧ࡭ࠣና"), bstack111l11_opy_ (u"ࠥࡴࡦࡸࡡ࡮ࡡ࡬ࡲࡩ࡫ࡸࠣኔ")],
    bstack111l11_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷ࠲ࡷࡻ࡮࡯ࡧࡵ࠲ࡈࡧ࡬࡭ࡋࡱࡪࡴࠨን"): [bstack111l11_opy_ (u"ࠧࡽࡨࡦࡰࠥኖ"), bstack111l11_opy_ (u"ࠨࡲࡦࡵࡸࡰࡹࠨኗ")],
    bstack111l11_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺ࠮࡮ࡣࡵ࡯࠳ࡹࡴࡳࡷࡦࡸࡺࡸࡥࡴ࠰ࡑࡳࡩ࡫ࡋࡦࡻࡺࡳࡷࡪࡳࠣኘ"): [bstack111l11_opy_ (u"ࠣࡰࡲࡨࡪࠨኙ"), bstack111l11_opy_ (u"ࠤࡳࡥࡷ࡫࡮ࡵࠤኚ")],
    bstack111l11_opy_ (u"ࠥࡴࡾࡺࡥࡴࡶ࠱ࡱࡦࡸ࡫࠯ࡵࡷࡶࡺࡩࡴࡶࡴࡨࡷ࠳ࡓࡡࡳ࡭ࠥኛ"): [bstack111l11_opy_ (u"ࠦࡳࡧ࡭ࡦࠤኜ"), bstack111l11_opy_ (u"ࠧࡧࡲࡨࡵࠥኝ"), bstack111l11_opy_ (u"ࠨ࡫ࡸࡣࡵ࡫ࡸࠨኞ")],
}
_1l1l1ll1l1l_opy_ = set()
class bstack1lll111l1ll_opy_(bstack1ll1ll1lll1_opy_):
    bstack1l1l1l1ll1l_opy_ = bstack111l11_opy_ (u"ࠢࡵࡧࡶࡸࡤࡪࡥࡧࡧࡵࡶࡪࡪࠢኟ")
    bstack1l1ll1l1l1l_opy_ = bstack111l11_opy_ (u"ࠣࡋࡑࡊࡔࠨአ")
    bstack1l1l1llll1l_opy_ = bstack111l11_opy_ (u"ࠤࡈࡖࡗࡕࡒࠣኡ")
    bstack1l1l1llll11_opy_: Callable
    bstack1l1ll111l1l_opy_: Callable
    def __init__(self, bstack1lll11lllll_opy_, bstack1llll11l1l1_opy_):
        super().__init__()
        self.bstack1ll111l1111_opy_ = bstack1llll11l1l1_opy_
        if os.getenv(bstack111l11_opy_ (u"ࠥࡗࡉࡑ࡟ࡄࡎࡌࡣࡋࡒࡁࡈࡡࡒ࠵࠶࡟ࠢኢ"), bstack111l11_opy_ (u"ࠦ࠶ࠨኣ")) != bstack111l11_opy_ (u"ࠧ࠷ࠢኤ") or not self.is_enabled():
            self.logger.warning(bstack111l11_opy_ (u"ࠨࠢእ") + str(self.__class__.__name__) + bstack111l11_opy_ (u"ࠢࠡࡦ࡬ࡷࡦࡨ࡬ࡦࡦࠥኦ"))
            return
        TestFramework.bstack1ll11llll1l_opy_((bstack1lll11ll111_opy_.TEST, bstack1lll1lll111_opy_.PRE), self.bstack1ll111ll11l_opy_)
        TestFramework.bstack1ll11llll1l_opy_((bstack1lll11ll111_opy_.TEST, bstack1lll1lll111_opy_.POST), self.bstack1ll11111lll_opy_)
        for event in bstack1lll11ll111_opy_:
            for state in bstack1lll1lll111_opy_:
                TestFramework.bstack1ll11llll1l_opy_((event, state), self.bstack1l1ll1l1lll_opy_)
        bstack1lll11lllll_opy_.bstack1ll11llll1l_opy_((bstack1llllll111l_opy_.bstack1llll1llll1_opy_, bstack1llll1l111l_opy_.POST), self.bstack1l1ll1lllll_opy_)
        self.bstack1l1l1llll11_opy_ = sys.stdout.write
        sys.stdout.write = self.bstack1l1ll11l1ll_opy_(bstack1lll111l1ll_opy_.bstack1l1ll1l1l1l_opy_, self.bstack1l1l1llll11_opy_)
        self.bstack1l1ll111l1l_opy_ = sys.stderr.write
        sys.stderr.write = self.bstack1l1ll11l1ll_opy_(bstack1lll111l1ll_opy_.bstack1l1l1llll1l_opy_, self.bstack1l1ll111l1l_opy_)
        self.bstack1l1ll111ll1_opy_ = builtins.print
        builtins.print = self.bstack1l1ll11ll1l_opy_()
    def is_enabled(self) -> bool:
        return True
    def bstack1l1ll1l1lll_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1llll1l_opy_,
        bstack1llllll1l1l_opy_: Tuple[bstack1lll11ll111_opy_, bstack1lll1lll111_opy_],
        *args,
        **kwargs,
    ):
        if f.bstack1l1ll1ll111_opy_() and instance:
            bstack1l1ll11lll1_opy_ = datetime.now()
            test_framework_state, test_hook_state = bstack1llllll1l1l_opy_
            if test_framework_state == bstack1lll11ll111_opy_.SETUP_FIXTURE:
                return
            elif test_framework_state == bstack1lll11ll111_opy_.LOG:
                bstack11l1ll1l_opy_ = datetime.now()
                entries = f.bstack1l1ll1lll11_opy_(instance, bstack1llllll1l1l_opy_)
                if entries:
                    self.bstack1l1ll1ll11l_opy_(instance, entries)
                    instance.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠣࡩࡵࡴࡨࡀࡳࡦࡰࡧࡣࡱࡵࡧࡠࡥࡵࡩࡦࡺࡥࡥࡡࡨࡺࡪࡴࡴࠣኧ"), datetime.now() - bstack11l1ll1l_opy_)
                    f.bstack1l1lll11l11_opy_(instance, bstack1llllll1l1l_opy_)
                instance.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠤࡲ࠵࠶ࡿ࠺ࡰࡰࡢࡥࡱࡲ࡟ࡵࡧࡶࡸࡤ࡫ࡶࡦࡰࡷࡷࠧከ"), datetime.now() - bstack1l1ll11lll1_opy_)
                return # bstack1l1l1l1ll11_opy_ not send this event with the bstack1l1ll1l1111_opy_ bstack1l1l1l1llll_opy_
            elif (
                test_framework_state == bstack1lll11ll111_opy_.TEST
                and test_hook_state == bstack1lll1lll111_opy_.POST
                and not f.bstack1lllll111ll_opy_(instance, TestFramework.bstack1l1ll111l11_opy_)
            ):
                self.logger.warning(bstack111l11_opy_ (u"ࠥࡨࡷࡵࡰࡱ࡫ࡱ࡫ࠥࡪࡵࡦࠢࡷࡳࠥࡲࡡࡤ࡭ࠣࡳ࡫ࠦࡲࡦࡵࡸࡰࡹࡹࠠࠣኩ") + str(TestFramework.bstack1lllll111ll_opy_(instance, TestFramework.bstack1l1ll111l11_opy_)) + bstack111l11_opy_ (u"ࠦࠧኪ"))
                f.bstack1llll1l11l1_opy_(instance, bstack1lll111l1ll_opy_.bstack1l1l1l1ll1l_opy_, True)
                return # bstack1l1l1l1ll11_opy_ not send this event bstack1l1ll11111l_opy_ bstack1l1l1lll1ll_opy_
            elif (
                f.bstack1llll1l11ll_opy_(instance, bstack1lll111l1ll_opy_.bstack1l1l1l1ll1l_opy_, False)
                and test_framework_state == bstack1lll11ll111_opy_.LOG_REPORT
                and test_hook_state == bstack1lll1lll111_opy_.POST
                and f.bstack1lllll111ll_opy_(instance, TestFramework.bstack1l1ll111l11_opy_)
            ):
                self.logger.warning(bstack111l11_opy_ (u"ࠧ࡯࡮࡫ࡧࡦࡸ࡮ࡴࡧࠡࡖࡨࡷࡹࡌࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡔࡶࡤࡸࡪ࠴ࡔࡆࡕࡗ࠰࡚ࠥࡥࡴࡶࡋࡳࡴࡱࡓࡵࡣࡷࡩ࠳ࡖࡏࡔࡖࠣࠦካ") + str(TestFramework.bstack1lllll111ll_opy_(instance, TestFramework.bstack1l1ll111l11_opy_)) + bstack111l11_opy_ (u"ࠨࠢኬ"))
                self.bstack1l1ll1l1lll_opy_(f, instance, (bstack1lll11ll111_opy_.TEST, bstack1lll1lll111_opy_.POST), *args, **kwargs)
            bstack11l1ll1l_opy_ = datetime.now()
            data = instance.data.copy()
            bstack1l1l1l1l1l1_opy_ = sorted(
                filter(lambda x: x.get(bstack111l11_opy_ (u"ࠢࡦࡸࡨࡲࡹࡥࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠥክ"), None), data.pop(bstack111l11_opy_ (u"ࠣࡶࡨࡷࡹࡥࡦࡪࡺࡷࡹࡷ࡫ࡳࠣኮ"), {}).values()),
                key=lambda x: x[bstack111l11_opy_ (u"ࠤࡨࡺࡪࡴࡴࡠࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠧኯ")],
            )
            if bstack1lll111lll1_opy_.bstack1l1l1l1l111_opy_ in data:
                data.pop(bstack1lll111lll1_opy_.bstack1l1l1l1l111_opy_)
            data.update({bstack111l11_opy_ (u"ࠥࡸࡪࡹࡴࡠࡨ࡬ࡼࡹࡻࡲࡦࡵࠥኰ"): bstack1l1l1l1l1l1_opy_})
            instance.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠦ࡯ࡹ࡯࡯࠼ࡷࡩࡸࡺ࡟ࡧ࡫ࡻࡸࡺࡸࡥࡴࠤ኱"), datetime.now() - bstack11l1ll1l_opy_)
            bstack11l1ll1l_opy_ = datetime.now()
            event_json = dumps(data, cls=bstack1l1lll111l1_opy_)
            instance.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠧࡰࡳࡰࡰ࠽ࡳࡳࡥࡡ࡭࡮ࡢࡸࡪࡹࡴࡠࡧࡹࡩࡳࡺࡳࠣኲ"), datetime.now() - bstack11l1ll1l_opy_)
            self.bstack1l1l1l1llll_opy_(instance, bstack1llllll1l1l_opy_, event_json=event_json)
            instance.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠨ࡯࠲࠳ࡼ࠾ࡴࡴ࡟ࡢ࡮࡯ࡣࡹ࡫ࡳࡵࡡࡨࡺࡪࡴࡴࡴࠤኳ"), datetime.now() - bstack1l1ll11lll1_opy_)
    def bstack1ll111ll11l_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1llll1l_opy_,
        bstack1llllll1l1l_opy_: Tuple[bstack1lll11ll111_opy_, bstack1lll1lll111_opy_],
        *args,
        **kwargs,
    ):
        from bstack_utils.bstack1l1l1l1111_opy_ import bstack1ll1l1ll1l1_opy_
        bstack1ll1111l1l1_opy_ = bstack1ll1l1ll1l1_opy_.bstack1ll11l1ll1l_opy_(EVENTS.bstack111llll11_opy_.value)
        self.bstack1ll111l1111_opy_.bstack1l1ll111lll_opy_(instance, f, bstack1llllll1l1l_opy_, *args, **kwargs)
        bstack1ll1l1ll1l1_opy_.end(EVENTS.bstack111llll11_opy_.value, bstack1ll1111l1l1_opy_ + bstack111l11_opy_ (u"ࠢ࠻ࡵࡷࡥࡷࡺࠢኴ"), bstack1ll1111l1l1_opy_ + bstack111l11_opy_ (u"ࠣ࠼ࡨࡲࡩࠨኵ"), status=True, failure=None, test_name=None)
    def bstack1ll11111lll_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1llll1l_opy_,
        bstack1llllll1l1l_opy_: Tuple[bstack1lll11ll111_opy_, bstack1lll1lll111_opy_],
        *args,
        **kwargs,
    ):
        req = self.bstack1ll111l1111_opy_.bstack1l1l1lll111_opy_(instance, f, bstack1llllll1l1l_opy_, *args, **kwargs)
        self.bstack1l1l1ll11l1_opy_(f, instance, req)
    @measure(event_name=EVENTS.bstack1l1lll11l1l_opy_, stage=STAGE.bstack111lllll1_opy_)
    def bstack1l1l1ll11l1_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1llll1l_opy_,
        req: structs.TestSessionEventRequest
    ):
        if not req:
            self.logger.debug(bstack111l11_opy_ (u"ࠤࡖ࡯࡮ࡶࡰࡪࡰࡪࠤ࡙࡫ࡳࡵࡕࡨࡷࡸ࡯࡯࡯ࡇࡹࡩࡳࡺࠠࡨࡔࡓࡇࠥࡩࡡ࡭࡮࠽ࠤࡓࡵࠠࡷࡣ࡯࡭ࡩࠦࡲࡦࡳࡸࡩࡸࡺࠠࡥࡣࡷࡥࠧ኶"))
            return
        bstack11l1ll1l_opy_ = datetime.now()
        try:
            r = self.bstack1ll1ll1ll1l_opy_.TestSessionEvent(req)
            instance.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠥ࡫ࡷࡶࡣ࠻ࡵࡨࡲࡩࡥࡴࡦࡵࡷࡣࡸ࡫ࡳࡴ࡫ࡲࡲࡤ࡫ࡶࡦࡰࡷࠦ኷"), datetime.now() - bstack11l1ll1l_opy_)
            f.bstack1llll1l11l1_opy_(instance, self.bstack1ll111l1111_opy_.bstack1l1ll1ll1ll_opy_, r.success)
            if not r.success:
                self.logger.info(bstack111l11_opy_ (u"ࠦࡷ࡫ࡣࡦ࡫ࡹࡩࡩࠦࡦࡳࡱࡰࠤࡸ࡫ࡲࡷࡧࡵ࠾ࠥࠨኸ") + str(r) + bstack111l11_opy_ (u"ࠧࠨኹ"))
        except grpc.RpcError as e:
            self.logger.error(bstack111l11_opy_ (u"ࠨࡲࡱࡥ࠰ࡩࡷࡸ࡯ࡳ࠼ࠣࠦኺ") + str(e) + bstack111l11_opy_ (u"ࠢࠣኻ"))
            traceback.print_exc()
            raise e
    def bstack1l1ll1lllll_opy_(
        self,
        f: bstack1ll1ll1l11l_opy_,
        _driver: object,
        exec: Tuple[bstack1lllll1ll1l_opy_, str],
        _1l1ll1l1ll1_opy_: Tuple[bstack1llllll111l_opy_, bstack1llll1l111l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if not bstack1ll1ll1l11l_opy_.bstack1ll111lll1l_opy_(method_name):
            return
        if f.bstack1ll111l1ll1_opy_(*args) == bstack1ll1ll1l11l_opy_.bstack1l1l1l11l11_opy_:
            bstack1l1ll11lll1_opy_ = datetime.now()
            screenshot = result.get(bstack111l11_opy_ (u"ࠣࡸࡤࡰࡺ࡫ࠢኼ"), None) if isinstance(result, dict) else None
            if not isinstance(screenshot, str) or len(screenshot) <= 0:
                self.logger.warning(bstack111l11_opy_ (u"ࠤ࡬ࡲࡻࡧ࡬ࡪࡦࠣࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࠠࡪ࡯ࡤ࡫ࡪࠦࡢࡢࡵࡨ࠺࠹ࠦࡳࡵࡴࠥኽ"))
                return
            bstack1l1ll1111ll_opy_ = self.bstack1l1ll1l1l11_opy_(instance)
            if bstack1l1ll1111ll_opy_:
                entry = bstack1ll1lll1111_opy_(TestFramework.bstack1l1l1ll111l_opy_, screenshot)
                self.bstack1l1ll1ll11l_opy_(bstack1l1ll1111ll_opy_, [entry])
                instance.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠥࡳ࠶࠷ࡹ࠻ࡱࡱࡣࡦ࡬ࡴࡦࡴࡢࡩࡽ࡫ࡣࡶࡶࡨࠦኾ"), datetime.now() - bstack1l1ll11lll1_opy_)
            else:
                self.logger.warning(bstack111l11_opy_ (u"ࠦࡺࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡥࡧࡷࡩࡷࡳࡩ࡯ࡧࠣࡸࡪࡹࡴࠡࡨࡲࡶࠥࡽࡨࡪࡥ࡫ࠤࡹ࡮ࡩࡴࠢࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹࠦࡷࡢࡵࠣࡸࡦࡱࡥ࡯ࠢࡥࡽࠥࡪࡲࡪࡸࡨࡶࡂࠦࡻࡾࠤ኿").format(instance.ref()))
        event = {}
        bstack1l1ll1111ll_opy_ = self.bstack1l1ll1l1l11_opy_(instance)
        if bstack1l1ll1111ll_opy_:
            self.bstack1l1l1ll1l11_opy_(event, bstack1l1ll1111ll_opy_)
            if event.get(bstack111l11_opy_ (u"ࠧࡲ࡯ࡨࡵࠥዀ")):
                self.bstack1l1ll1ll11l_opy_(bstack1l1ll1111ll_opy_, event[bstack111l11_opy_ (u"ࠨ࡬ࡰࡩࡶࠦ዁")])
            else:
                self.logger.debug(bstack111l11_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡨࡪࡺࡥࡳ࡯࡬ࡲࡪࠦ࡬ࡰࡩࡶࠤ࡫ࡵࡲࠡࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࠥ࡫ࡶࡦࡰࡷࠦዂ"))
    @measure(event_name=EVENTS.bstack1l1l1l1lll1_opy_, stage=STAGE.bstack111lllll1_opy_)
    def bstack1l1ll1ll11l_opy_(
        self,
        bstack1l1ll1111ll_opy_: bstack1lll1llll1l_opy_,
        entries: List[bstack1ll1lll1111_opy_],
    ):
        self.bstack1ll11l11111_opy_()
        req = structs.LogCreatedEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1llll1l11ll_opy_(bstack1l1ll1111ll_opy_, TestFramework.bstack1ll1111lll1_opy_)
        req.execution_context.hash = str(bstack1l1ll1111ll_opy_.context.hash)
        req.execution_context.thread_id = str(bstack1l1ll1111ll_opy_.context.thread_id)
        req.execution_context.process_id = str(bstack1l1ll1111ll_opy_.context.process_id)
        for entry in entries:
            log_entry = req.logs.add()
            log_entry.test_framework_name = TestFramework.bstack1llll1l11ll_opy_(bstack1l1ll1111ll_opy_, TestFramework.bstack1ll111l111l_opy_)
            log_entry.test_framework_version = TestFramework.bstack1llll1l11ll_opy_(bstack1l1ll1111ll_opy_, TestFramework.bstack1l1l1l11ll1_opy_)
            log_entry.uuid = TestFramework.bstack1llll1l11ll_opy_(bstack1l1ll1111ll_opy_, TestFramework.bstack1ll11l111l1_opy_)
            log_entry.test_framework_state = bstack1l1ll1111ll_opy_.state.name
            log_entry.message = entry.message.encode(bstack111l11_opy_ (u"ࠣࡷࡷࡪ࠲࠾ࠢዃ"))
            log_entry.kind = entry.kind
            log_entry.timestamp = (
                entry.timestamp.isoformat()
                if isinstance(entry.timestamp, datetime)
                else datetime.now(tz=timezone.utc).isoformat()
            )
            if isinstance(entry.level, str) and len(entry.level.strip()) > 0:
                log_entry.level = entry.level.strip()
            if entry.kind == bstack111l11_opy_ (u"ࠤࡗࡉࡘ࡚࡟ࡂࡖࡗࡅࡈࡎࡍࡆࡐࡗࠦዄ"):
                log_entry.file_name = entry.fileName
                log_entry.file_size = entry.bstack1l1lll111ll_opy_
                log_entry.file_path = entry.bstack11l1l1_opy_
        def bstack1l1ll1ll1l1_opy_():
            bstack11l1ll1l_opy_ = datetime.now()
            try:
                self.bstack1ll1ll1ll1l_opy_.LogCreatedEvent(req)
                if entry.kind == TestFramework.bstack1l1l1ll111l_opy_:
                    bstack1l1ll1111ll_opy_.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠥ࡫ࡷࡶࡣ࠻ࡵࡨࡲࡩࡥ࡬ࡰࡩࡢࡧࡷ࡫ࡡࡵࡧࡧࡣࡪࡼࡥ࡯ࡶࡢࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࠢዅ"), datetime.now() - bstack11l1ll1l_opy_)
                elif entry.kind == TestFramework.bstack1l1lll11lll_opy_:
                    bstack1l1ll1111ll_opy_.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠦ࡬ࡸࡰࡤ࠼ࡶࡩࡳࡪ࡟࡭ࡱࡪࡣࡨࡸࡥࡢࡶࡨࡨࡤ࡫ࡶࡦࡰࡷࡣࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࠣ዆"), datetime.now() - bstack11l1ll1l_opy_)
                else:
                    bstack1l1ll1111ll_opy_.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠧ࡭ࡲࡱࡥ࠽ࡷࡪࡴࡤࡠ࡮ࡲ࡫ࡤࡩࡲࡦࡣࡷࡩࡩࡥࡥࡷࡧࡱࡸࡤࡲ࡯ࡨࠤ዇"), datetime.now() - bstack11l1ll1l_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack111l11_opy_ (u"ࠨࡲࡱࡥ࠰ࡩࡷࡸ࡯ࡳ࠼ࠣࠦወ") + str(e))
                traceback.print_exc()
                raise e
        self.bstack1llllllllll_opy_.enqueue(bstack1l1ll1ll1l1_opy_)
    @measure(event_name=EVENTS.bstack1l1l1l11lll_opy_, stage=STAGE.bstack111lllll1_opy_)
    def bstack1l1l1l1llll_opy_(
        self,
        instance: bstack1lll1llll1l_opy_,
        bstack1llllll1l1l_opy_: Tuple[bstack1lll11ll111_opy_, bstack1lll1lll111_opy_],
        event_json=None,
    ):
        self.bstack1ll11l11111_opy_()
        req = structs.TestFrameworkEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1ll1111lll1_opy_)
        req.test_framework_name = TestFramework.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1ll111l111l_opy_)
        req.test_framework_version = TestFramework.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1l1l1l11ll1_opy_)
        req.test_framework_state = bstack1llllll1l1l_opy_[0].name
        req.test_hook_state = bstack1llllll1l1l_opy_[1].name
        started_at = TestFramework.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1l1lll1l11l_opy_, None)
        if started_at:
            req.started_at = started_at.isoformat()
        ended_at = TestFramework.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1l1lll11ll1_opy_, None)
        if ended_at:
            req.ended_at = ended_at.isoformat()
        req.uuid = instance.ref()
        req.event_json = (event_json if event_json else dumps(instance.data, cls=bstack1l1lll111l1_opy_)).encode(bstack111l11_opy_ (u"ࠢࡶࡶࡩ࠱࠽ࠨዉ"))
        req.execution_context.hash = str(instance.context.hash)
        req.execution_context.thread_id = str(instance.context.thread_id)
        req.execution_context.process_id = str(instance.context.process_id)
        def bstack1l1ll1ll1l1_opy_():
            bstack11l1ll1l_opy_ = datetime.now()
            try:
                self.bstack1ll1ll1ll1l_opy_.TestFrameworkEvent(req)
                instance.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠣࡩࡵࡴࡨࡀࡳࡦࡰࡧࡣࡹ࡫ࡳࡵࡡࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤ࡫ࡶࡦࡰࡷࠦዊ"), datetime.now() - bstack11l1ll1l_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack111l11_opy_ (u"ࠤࡵࡴࡨ࠳ࡥࡳࡴࡲࡶ࠿ࠦࠢዋ") + str(e))
                traceback.print_exc()
                raise e
        self.bstack1llllllllll_opy_.enqueue(bstack1l1ll1ll1l1_opy_)
    def bstack1l1ll1l1l11_opy_(self, instance: bstack1lllll1ll1l_opy_):
        bstack1l1ll11llll_opy_ = TestFramework.bstack1llllll1111_opy_(instance.context)
        for t in bstack1l1ll11llll_opy_:
            bstack1l1l1ll1ll1_opy_ = TestFramework.bstack1llll1l11ll_opy_(t, bstack1lll111lll1_opy_.bstack1l1l1l1l111_opy_, [])
            if any(instance is d[1] for d in bstack1l1l1ll1ll1_opy_):
                return t
    def bstack1l1ll11ll11_opy_(self, message):
        self.bstack1l1l1llll11_opy_(message + bstack111l11_opy_ (u"ࠥࡠࡳࠨዌ"))
    def log_error(self, message):
        self.bstack1l1ll111l1l_opy_(message + bstack111l11_opy_ (u"ࠦࡡࡴࠢው"))
    def bstack1l1ll11l1ll_opy_(self, level, original_func):
        def bstack1l1l1ll1lll_opy_(*args):
            return_value = original_func(*args)
            if not args or not isinstance(args[0], str) or not args[0].strip():
                return return_value
            message = args[0].strip()
            if bstack111l11_opy_ (u"ࠧࡋࡶࡦࡰࡷࡈ࡮ࡹࡰࡢࡶࡦ࡬ࡪࡸࡍࡰࡦࡸࡰࡪࠨዎ") in message or bstack111l11_opy_ (u"ࠨ࡛ࡔࡆࡎࡇࡑࡏ࡝ࠣዏ") in message or bstack111l11_opy_ (u"ࠢ࡜࡙ࡨࡦࡉࡸࡩࡷࡧࡵࡑࡴࡪࡵ࡭ࡧࡠࠦዐ") in message:
                return return_value
            bstack1l1ll11llll_opy_ = TestFramework.bstack1l1ll1l11ll_opy_()
            if not bstack1l1ll11llll_opy_:
                return return_value
            bstack1l1ll1111ll_opy_ = next(
                (
                    instance
                    for instance in bstack1l1ll11llll_opy_
                    if TestFramework.bstack1lllll111ll_opy_(instance, TestFramework.bstack1ll11l111l1_opy_)
                ),
                None,
            )
            if not bstack1l1ll1111ll_opy_:
                return return_value
            entry = bstack1ll1lll1111_opy_(TestFramework.bstack1l1l1lll1l1_opy_, message, level)
            self.bstack1l1ll1ll11l_opy_(bstack1l1ll1111ll_opy_, [entry])
            return return_value
        return bstack1l1l1ll1lll_opy_
    def bstack1l1ll11ll1l_opy_(self):
        def bstack1l1l1l1l11l_opy_(*args, **kwargs):
            try:
                self.bstack1l1ll111ll1_opy_(*args, **kwargs)
                if not args:
                    return
                message = bstack111l11_opy_ (u"ࠨࠢࠪዑ").join(str(arg) for arg in args)
                if not message.strip():
                    return
                if bstack111l11_opy_ (u"ࠤࡈࡺࡪࡴࡴࡅ࡫ࡶࡴࡦࡺࡣࡩࡧࡵࡑࡴࡪࡵ࡭ࡧࠥዒ") in message:
                    return
                bstack1l1ll11llll_opy_ = TestFramework.bstack1l1ll1l11ll_opy_()
                if not bstack1l1ll11llll_opy_:
                    return
                bstack1l1ll1111ll_opy_ = next(
                    (
                        instance
                        for instance in bstack1l1ll11llll_opy_
                        if TestFramework.bstack1lllll111ll_opy_(instance, TestFramework.bstack1ll11l111l1_opy_)
                    ),
                    None,
                )
                if not bstack1l1ll1111ll_opy_:
                    return
                entry = bstack1ll1lll1111_opy_(TestFramework.bstack1l1l1lll1l1_opy_, message, bstack1lll111l1ll_opy_.bstack1l1ll1l1l1l_opy_)
                self.bstack1l1ll1ll11l_opy_(bstack1l1ll1111ll_opy_, [entry])
            except Exception as e:
                try:
                    self.bstack1l1ll111ll1_opy_(bstack111111ll11_opy_ (u"ࠥ࡟ࡊࡼࡥ࡯ࡶࡇ࡭ࡸࡶࡡࡵࡥ࡫ࡩࡷࡓ࡯ࡥࡷ࡯ࡩࡢࠦࡌࡰࡩࠣࡧࡦࡶࡴࡶࡴࡨࠤࡪࡸࡲࡰࡴ࠽ࠤࢀ࡫ࡽࠣዓ"))
                except:
                    pass
        return bstack1l1l1l1l11l_opy_
    def bstack1l1l1ll1l11_opy_(self, event: dict, instance=None) -> None:
        global _1l1l1ll1l1l_opy_
        levels = [bstack111l11_opy_ (u"࡙ࠦ࡫ࡳࡵࡎࡨࡺࡪࡲࠢዔ"), bstack111l11_opy_ (u"ࠧࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࠤዕ")]
        bstack1l1l1lll11l_opy_ = bstack111l11_opy_ (u"ࠨࠢዖ")
        if instance is not None:
            try:
                bstack1l1l1lll11l_opy_ = TestFramework.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1ll11l111l1_opy_)
            except Exception as e:
                self.logger.warning(bstack111l11_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡧࡦࡶࡷ࡭ࡳ࡭ࠠࡶࡷ࡬ࡨࠥ࡬ࡲࡰ࡯ࠣ࡭ࡳࡹࡴࡢࡰࡦࡩࠧ዗").format(e))
        bstack1l1l1lllll1_opy_ = []
        try:
            for level in levels:
                platform_index = os.environ[bstack111l11_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡌࡒࡉࡋࡘࠨዘ")]
                bstack1l1ll1l111l_opy_ = os.path.join(bstack1l1ll11l11l_opy_, (bstack1l1l1l11l1l_opy_ + str(platform_index)), level)
                if not os.path.isdir(bstack1l1ll1l111l_opy_):
                    self.logger.debug(bstack111l11_opy_ (u"ࠤࡇ࡭ࡷ࡫ࡣࡵࡱࡵࡽࠥࡴ࡯ࡵࠢࡳࡶࡪࡹࡥ࡯ࡶࠣࡪࡴࡸࠠࡱࡴࡲࡧࡪࡹࡳࡪࡰࡪࠤ࡙࡫ࡳࡵࠢࡤࡲࡩࠦࡂࡶ࡫࡯ࡨࠥࡲࡥࡷࡧ࡯ࠤࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࡴࠢࡾࢁࠧዙ").format(bstack1l1ll1l111l_opy_))
                    continue
                file_names = os.listdir(bstack1l1ll1l111l_opy_)
                for file_name in file_names:
                    file_path = os.path.join(bstack1l1ll1l111l_opy_, file_name)
                    abs_path = os.path.abspath(file_path)
                    if abs_path in _1l1l1ll1l1l_opy_:
                        self.logger.info(bstack111l11_opy_ (u"ࠥࡔࡦࡺࡨࠡࡣ࡯ࡶࡪࡧࡤࡺࠢࡳࡶࡴࡩࡥࡴࡵࡨࡨࠥࢁࡽࠣዚ").format(abs_path))
                        continue
                    if os.path.isfile(file_path):
                        try:
                            bstack1l1l1llllll_opy_ = os.path.getmtime(file_path)
                            timestamp = datetime.fromtimestamp(bstack1l1l1llllll_opy_, tz=timezone.utc).isoformat()
                            file_size = os.path.getsize(file_path)
                            if level == bstack111l11_opy_ (u"࡙ࠦ࡫ࡳࡵࡎࡨࡺࡪࡲࠢዛ"):
                                entry = bstack1ll1lll1111_opy_(
                                    kind=bstack111l11_opy_ (u"࡚ࠧࡅࡔࡖࡢࡅ࡙࡚ࡁࡄࡊࡐࡉࡓ࡚ࠢዜ"),
                                    message=bstack111l11_opy_ (u"ࠨࠢዝ"),
                                    level=level,
                                    timestamp=timestamp,
                                    fileName=file_name,
                                    bstack1l1lll111ll_opy_=file_size,
                                    bstack1l1ll1l11l1_opy_=bstack111l11_opy_ (u"ࠢࡎࡃࡑ࡙ࡆࡒ࡟ࡖࡒࡏࡓࡆࡊࠢዞ"),
                                    bstack11l1l1_opy_=os.path.abspath(file_path),
                                    bstack1l1lllll1_opy_=bstack1l1l1lll11l_opy_
                                )
                            elif level == bstack111l11_opy_ (u"ࠣࡄࡸ࡭ࡱࡪࡌࡦࡸࡨࡰࠧዟ"):
                                entry = bstack1ll1lll1111_opy_(
                                    kind=bstack111l11_opy_ (u"ࠤࡗࡉࡘ࡚࡟ࡂࡖࡗࡅࡈࡎࡍࡆࡐࡗࠦዠ"),
                                    message=bstack111l11_opy_ (u"ࠥࠦዡ"),
                                    level=level,
                                    timestamp=timestamp,
                                    fileName=file_name,
                                    bstack1l1lll111ll_opy_=file_size,
                                    bstack1l1ll1l11l1_opy_=bstack111l11_opy_ (u"ࠦࡒࡇࡎࡖࡃࡏࡣ࡚ࡖࡌࡐࡃࡇࠦዢ"),
                                    bstack11l1l1_opy_=os.path.abspath(file_path),
                                    bstack1l1ll1111l1_opy_=bstack1l1l1lll11l_opy_
                                )
                            bstack1l1l1lllll1_opy_.append(entry)
                            _1l1l1ll1l1l_opy_.add(abs_path)
                        except Exception as bstack1l1ll1lll1l_opy_:
                            self.logger.error(bstack111l11_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡴࡤ࡭ࡸ࡫ࡤࠡࡹ࡫ࡩࡳࠦࡰࡳࡱࡦࡩࡸࡹࡩ࡯ࡩࠣࡥࡹࡺࡡࡤࡪࡰࡩࡳࡺࡳࠡࡽࢀࠦዣ").format(bstack1l1ll1lll1l_opy_))
        except Exception as e:
            self.logger.error(bstack111l11_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢࡵࡥ࡮ࡹࡥࡥࠢࡺ࡬ࡪࡴࠠࡱࡴࡲࡧࡪࡹࡳࡪࡰࡪࠤࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࡴࠢࡾࢁࠧዤ").format(e))
        event[bstack111l11_opy_ (u"ࠢ࡭ࡱࡪࡷࠧዥ")] = bstack1l1l1lllll1_opy_
class bstack1l1lll111l1_opy_(JSONEncoder):
    def __init__(self, **kwargs):
        self.bstack1l1l1l1l1ll_opy_ = set()
        kwargs[bstack111l11_opy_ (u"ࠣࡵ࡮࡭ࡵࡱࡥࡺࡵࠥዦ")] = True
        super().__init__(**kwargs)
    def default(self, obj):
        return bstack1l1l1ll1111_opy_(obj, self.bstack1l1l1l1l1ll_opy_)
def bstack1l1ll111111_opy_(obj):
    return isinstance(obj, (str, int, float, bool, type(None)))
def bstack1l1l1ll1111_opy_(obj, bstack1l1l1l1l1ll_opy_=None, max_depth=3):
    if bstack1l1l1l1l1ll_opy_ is None:
        bstack1l1l1l1l1ll_opy_ = set()
    if id(obj) in bstack1l1l1l1l1ll_opy_ or max_depth <= 0:
        return None
    max_depth -= 1
    bstack1l1l1l1l1ll_opy_.add(id(obj))
    if isinstance(obj, datetime):
        return obj.isoformat()
    bstack1l1ll11l1l1_opy_ = TestFramework.bstack1l1lll11111_opy_(obj)
    bstack1l1lll1l111_opy_ = next((k.lower() in bstack1l1ll11l1l1_opy_.lower() for k in bstack1l1ll1llll1_opy_.keys()), None)
    if bstack1l1lll1l111_opy_:
        obj = TestFramework.bstack1l1lll1l1l1_opy_(obj, bstack1l1ll1llll1_opy_[bstack1l1lll1l111_opy_])
    if not isinstance(obj, dict):
        keys = []
        if hasattr(obj, bstack111l11_opy_ (u"ࠤࡢࡣࡸࡲ࡯ࡵࡵࡢࡣࠧዧ")):
            keys = getattr(obj, bstack111l11_opy_ (u"ࠥࡣࡤࡹ࡬ࡰࡶࡶࡣࡤࠨየ"), [])
        elif hasattr(obj, bstack111l11_opy_ (u"ࠦࡤࡥࡤࡪࡥࡷࡣࡤࠨዩ")):
            keys = getattr(obj, bstack111l11_opy_ (u"ࠧࡥ࡟ࡥ࡫ࡦࡸࡤࡥࠢዪ"), {}).keys()
        else:
            keys = dir(obj)
        obj = {k: getattr(obj, k, None) for k in keys if not str(k).startswith(bstack111l11_opy_ (u"ࠨ࡟ࠣያ"))}
        if not obj and bstack1l1ll11l1l1_opy_ == bstack111l11_opy_ (u"ࠢࡱࡣࡷ࡬ࡱ࡯ࡢ࠯ࡒࡲࡷ࡮ࡾࡐࡢࡶ࡫ࠦዬ"):
            obj = {bstack111l11_opy_ (u"ࠣࡲࡤࡸ࡭ࠨይ"): str(obj)}
    result = {}
    for key, value in obj.items():
        if not bstack1l1ll111111_opy_(key) or str(key).startswith(bstack111l11_opy_ (u"ࠤࡢࠦዮ")):
            continue
        if value is not None and bstack1l1ll111111_opy_(value):
            result[key] = value
        elif isinstance(value, dict):
            r = bstack1l1l1ll1111_opy_(value, bstack1l1l1l1l1ll_opy_, max_depth)
            if r is not None:
                result[key] = r
        elif isinstance(value, (list, tuple, set, frozenset)):
            result[key] = list(filter(None, [bstack1l1l1ll1111_opy_(o, bstack1l1l1l1l1ll_opy_, max_depth) for o in value]))
    return result or None