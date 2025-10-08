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
from typing import Dict, List, Any, Callable, Tuple, Union
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1lll111ll1l_opy_ import bstack1ll1ll1lll1_opy_
from browserstack_sdk.sdk_cli.bstack1lllll11l1l_opy_ import (
    bstack1llllll111l_opy_,
    bstack1llll1l111l_opy_,
    bstack1lllll1ll1l_opy_,
)
from bstack_utils.helper import  bstack1l11lllll1_opy_
from browserstack_sdk.sdk_cli.bstack1ll1l1ll111_opy_ import bstack1ll1ll1l11l_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1lll11ll111_opy_, bstack1lll1llll1l_opy_, bstack1lll1lll111_opy_, bstack1ll1lll1111_opy_
from typing import Tuple, Any
import threading
from bstack_utils.bstack1l11l1l1l_opy_ import bstack11lllll11_opy_
from browserstack_sdk.sdk_cli.bstack1ll1l1l1lll_opy_ import bstack1lll111lll1_opy_
from bstack_utils.percy import bstack1ll11l1lll_opy_
from bstack_utils.percy_sdk import PercySDK
from bstack_utils.constants import *
import re
class bstack1ll1l1llll1_opy_(bstack1ll1ll1lll1_opy_):
    def __init__(self, bstack1l1l1l111ll_opy_: Dict[str, str]):
        super().__init__()
        self.bstack1l1l1l111ll_opy_ = bstack1l1l1l111ll_opy_
        self.percy = bstack1ll11l1lll_opy_()
        self.bstack1l111l1111_opy_ = bstack11lllll11_opy_()
        self.bstack1l1l11l1lll_opy_()
        bstack1ll1ll1l11l_opy_.bstack1ll11llll1l_opy_((bstack1llllll111l_opy_.bstack1llll1llll1_opy_, bstack1llll1l111l_opy_.PRE), self.bstack1l1l1l111l1_opy_)
        TestFramework.bstack1ll11llll1l_opy_((bstack1lll11ll111_opy_.TEST, bstack1lll1lll111_opy_.POST), self.bstack1ll11111lll_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l1ll1l1l11_opy_(self, instance: bstack1lllll1ll1l_opy_, driver: object):
        bstack1l1ll11llll_opy_ = TestFramework.bstack1llllll1111_opy_(instance.context)
        for t in bstack1l1ll11llll_opy_:
            bstack1l1l1ll1ll1_opy_ = TestFramework.bstack1llll1l11ll_opy_(t, bstack1lll111lll1_opy_.bstack1l1l1l1l111_opy_, [])
            if any(instance is d[1] for d in bstack1l1l1ll1ll1_opy_) or instance == driver:
                return t
    def bstack1l1l1l111l1_opy_(
        self,
        f: bstack1ll1ll1l11l_opy_,
        driver: object,
        exec: Tuple[bstack1lllll1ll1l_opy_, str],
        bstack1llllll1l1l_opy_: Tuple[bstack1llllll111l_opy_, bstack1llll1l111l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        try:
            instance, method_name = exec
            if not bstack1ll1ll1l11l_opy_.bstack1ll111lll1l_opy_(method_name):
                return
            platform_index = f.bstack1llll1l11ll_opy_(instance, bstack1ll1ll1l11l_opy_.bstack1ll1111lll1_opy_, 0)
            bstack1l1ll1111ll_opy_ = self.bstack1l1ll1l1l11_opy_(instance, driver)
            bstack1l1l1l1111l_opy_ = TestFramework.bstack1llll1l11ll_opy_(bstack1l1ll1111ll_opy_, TestFramework.bstack1l1l11lll1l_opy_, None)
            if not bstack1l1l1l1111l_opy_:
                self.logger.debug(bstack111l11_opy_ (u"ࠥࡳࡳࡥࡰࡳࡧࡢࡩࡽ࡫ࡣࡶࡶࡨ࠾ࠥࡸࡥࡵࡷࡵࡲ࡮ࡴࡧࠡࡣࡶࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥ࡯ࡳࠡࡰࡲࡸࠥࡿࡥࡵࠢࡶࡸࡦࡸࡴࡦࡦࠥዯ"))
                return
            driver_command = f.bstack1ll111l1ll1_opy_(*args)
            for command in bstack1l1ll111ll_opy_:
                if command == driver_command:
                    self.bstack1lll1l1ll_opy_(driver, platform_index)
            bstack1l11l1l1_opy_ = self.percy.bstack1lll1111l_opy_()
            if driver_command in bstack1ll1111111_opy_[bstack1l11l1l1_opy_]:
                self.bstack1l111l1111_opy_.bstack11ll1111l1_opy_(bstack1l1l1l1111l_opy_, driver_command)
        except Exception as e:
            self.logger.error(bstack111l11_opy_ (u"ࠦࡴࡴ࡟ࡱࡴࡨࡣࡪࡾࡥࡤࡷࡷࡩ࠿ࠦࡥࡳࡴࡲࡶࠧደ"), e)
    def bstack1ll11111lll_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1llll1l_opy_,
        bstack1llllll1l1l_opy_: Tuple[bstack1lll11ll111_opy_, bstack1lll1lll111_opy_],
        *args,
        **kwargs,
    ):
        from bstack_utils.bstack1l1l1l1111_opy_ import bstack1ll1l1ll1l1_opy_
        bstack1l1l1ll1ll1_opy_ = f.bstack1llll1l11ll_opy_(instance, bstack1lll111lll1_opy_.bstack1l1l1l1l111_opy_, [])
        if not bstack1l1l1ll1ll1_opy_:
            self.logger.debug(bstack111l11_opy_ (u"ࠧࡵ࡮ࡠࡣࡩࡸࡪࡸ࡟ࡵࡧࡶࡸ࠿ࠦ࡮ࡰࠢࡧࡶ࡮ࡼࡥࡳࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢዱ") + str(kwargs) + bstack111l11_opy_ (u"ࠨࠢዲ"))
            return
        if len(bstack1l1l1ll1ll1_opy_) > 1:
            self.logger.debug(bstack111l11_opy_ (u"ࠢࡰࡰࡢࡥ࡫ࡺࡥࡳࡡࡷࡩࡸࡺ࠺ࠡࡽ࡯ࡩࡳ࠮ࡤࡳ࡫ࡹࡩࡷࡥࡩ࡯ࡵࡷࡥࡳࡩࡥࡴࠫࢀࠤࡩࡸࡩࡷࡧࡵࡷࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤዳ") + str(kwargs) + bstack111l11_opy_ (u"ࠣࠤዴ"))
        bstack1l1l11ll1ll_opy_, bstack1l1l11ll111_opy_ = bstack1l1l1ll1ll1_opy_[0]
        driver = bstack1l1l11ll1ll_opy_()
        if not driver:
            self.logger.debug(bstack111l11_opy_ (u"ࠤࡲࡲࡤࡧࡦࡵࡧࡵࡣࡹ࡫ࡳࡵ࠼ࠣࡲࡴࠦࡤࡳ࡫ࡹࡩࡷࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥድ") + str(kwargs) + bstack111l11_opy_ (u"ࠥࠦዶ"))
            return
        bstack1l1l11lll11_opy_ = {
            TestFramework.bstack1ll11lll11l_opy_: bstack111l11_opy_ (u"ࠦࡹ࡫ࡳࡵࠢࡱࡥࡲ࡫ࠢዷ"),
            TestFramework.bstack1ll11l111l1_opy_: bstack111l11_opy_ (u"ࠧࡺࡥࡴࡶࠣࡹࡺ࡯ࡤࠣዸ"),
            TestFramework.bstack1l1l11lll1l_opy_: bstack111l11_opy_ (u"ࠨࡴࡦࡵࡷࠤࡷ࡫ࡲࡶࡰࠣࡲࡦࡳࡥࠣዹ")
        }
        bstack1l1l11ll11l_opy_ = { key: f.bstack1llll1l11ll_opy_(instance, key) for key in bstack1l1l11lll11_opy_ }
        bstack1l1l11lllll_opy_ = [key for key, value in bstack1l1l11ll11l_opy_.items() if not value]
        if bstack1l1l11lllll_opy_:
            for key in bstack1l1l11lllll_opy_:
                self.logger.debug(bstack111l11_opy_ (u"ࠢࡰࡰࡢࡥ࡫ࡺࡥࡳࡡࡷࡩࡸࡺ࠺ࠡ࡯࡬ࡷࡸ࡯࡮ࡨࠢࠥዺ") + str(key) + bstack111l11_opy_ (u"ࠣࠤዻ"))
            return
        platform_index = f.bstack1llll1l11ll_opy_(instance, bstack1ll1ll1l11l_opy_.bstack1ll1111lll1_opy_, 0)
        if self.bstack1l1l1l111ll_opy_.percy_capture_mode == bstack111l11_opy_ (u"ࠤࡷࡩࡸࡺࡣࡢࡵࡨࠦዼ"):
            bstack1lllll1l1_opy_ = bstack1l1l11ll11l_opy_.get(TestFramework.bstack1l1l11lll1l_opy_) + bstack111l11_opy_ (u"ࠥ࠱ࡹ࡫ࡳࡵࡥࡤࡷࡪࠨዽ")
            bstack1ll1111l1l1_opy_ = bstack1ll1l1ll1l1_opy_.bstack1ll11l1ll1l_opy_(EVENTS.bstack1l1l1l11111_opy_.value)
            PercySDK.screenshot(
                driver,
                bstack1lllll1l1_opy_,
                bstack11l1l11l1_opy_=bstack1l1l11ll11l_opy_[TestFramework.bstack1ll11lll11l_opy_],
                bstack1lll11l1l_opy_=bstack1l1l11ll11l_opy_[TestFramework.bstack1ll11l111l1_opy_],
                bstack1ll1l1lll_opy_=platform_index
            )
            bstack1ll1l1ll1l1_opy_.end(EVENTS.bstack1l1l1l11111_opy_.value, bstack1ll1111l1l1_opy_+bstack111l11_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦዾ"), bstack1ll1111l1l1_opy_+bstack111l11_opy_ (u"ࠧࡀࡥ࡯ࡦࠥዿ"), True, None, None, None, None, test_name=bstack1lllll1l1_opy_)
    def bstack1lll1l1ll_opy_(self, driver, platform_index):
        if self.bstack1l111l1111_opy_.bstack11lll111_opy_() is True or self.bstack1l111l1111_opy_.capturing() is True:
            return
        self.bstack1l111l1111_opy_.bstack1lll11l11l_opy_()
        while not self.bstack1l111l1111_opy_.bstack11lll111_opy_():
            bstack1l1l1l1111l_opy_ = self.bstack1l111l1111_opy_.bstack1l11llll1l_opy_()
            self.bstack1l11llllll_opy_(driver, bstack1l1l1l1111l_opy_, platform_index)
        self.bstack1l111l1111_opy_.bstack1lll1l11l1_opy_()
    def bstack1l11llllll_opy_(self, driver, bstack1l11l11ll_opy_, platform_index, test=None):
        from bstack_utils.bstack1l1l1l1111_opy_ import bstack1ll1l1ll1l1_opy_
        bstack1ll1111l1l1_opy_ = bstack1ll1l1ll1l1_opy_.bstack1ll11l1ll1l_opy_(EVENTS.bstack1l111lll1_opy_.value)
        if test != None:
            bstack11l1l11l1_opy_ = getattr(test, bstack111l11_opy_ (u"࠭࡮ࡢ࡯ࡨࠫጀ"), None)
            bstack1lll11l1l_opy_ = getattr(test, bstack111l11_opy_ (u"ࠧࡶࡷ࡬ࡨࠬጁ"), None)
            PercySDK.screenshot(driver, bstack1l11l11ll_opy_, bstack11l1l11l1_opy_=bstack11l1l11l1_opy_, bstack1lll11l1l_opy_=bstack1lll11l1l_opy_, bstack1ll1l1lll_opy_=platform_index)
        else:
            PercySDK.screenshot(driver, bstack1l11l11ll_opy_)
        bstack1ll1l1ll1l1_opy_.end(EVENTS.bstack1l111lll1_opy_.value, bstack1ll1111l1l1_opy_+bstack111l11_opy_ (u"ࠣ࠼ࡶࡸࡦࡸࡴࠣጂ"), bstack1ll1111l1l1_opy_+bstack111l11_opy_ (u"ࠤ࠽ࡩࡳࡪࠢጃ"), True, None, None, None, None, test_name=bstack1l11l11ll_opy_)
    def bstack1l1l11l1lll_opy_(self):
        os.environ[bstack111l11_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡉࡗࡉ࡙ࠨጄ")] = str(self.bstack1l1l1l111ll_opy_.success)
        os.environ[bstack111l11_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡊࡘࡃ࡚ࡡࡆࡅࡕ࡚ࡕࡓࡇࡢࡑࡔࡊࡅࠨጅ")] = str(self.bstack1l1l1l111ll_opy_.percy_capture_mode)
        self.percy.bstack1l1l11ll1l1_opy_(self.bstack1l1l1l111ll_opy_.is_percy_auto_enabled)
        self.percy.bstack1l1l11llll1_opy_(self.bstack1l1l1l111ll_opy_.percy_build_id)