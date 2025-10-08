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
from datetime import datetime
import os
import threading
from browserstack_sdk.sdk_cli.bstack1lllll11l1l_opy_ import (
    bstack1llllll111l_opy_,
    bstack1llll1l111l_opy_,
    bstack1lllll1l1l1_opy_,
    bstack1lllll1ll1l_opy_,
)
from browserstack_sdk.sdk_cli.bstack1ll1l1ll111_opy_ import bstack1ll1ll1l11l_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1lll11ll111_opy_, bstack1lll1lll111_opy_, bstack1lll1llll1l_opy_
from typing import Tuple, Dict, Any, List, Union
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1lll111ll1l_opy_ import bstack1ll1ll1lll1_opy_
from browserstack_sdk.sdk_cli.bstack1ll1l1l1lll_opy_ import bstack1lll111lll1_opy_
from browserstack_sdk.sdk_cli.bstack1lll11l1ll1_opy_ import bstack1ll1llllll1_opy_
from browserstack_sdk.sdk_cli.bstack1ll1ll11l11_opy_ import bstack1ll1ll11111_opy_
from bstack_utils.helper import bstack1ll11l1l11l_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
from bstack_utils.bstack1l1l1l1111_opy_ import bstack1ll1l1ll1l1_opy_
import grpc
import traceback
import json
class bstack1lll1l11l1l_opy_(bstack1ll1ll1lll1_opy_):
    bstack1ll11111l1l_opy_ = False
    bstack1ll1l1111ll_opy_ = bstack111l11_opy_ (u"ࠧࡹࡥ࡭ࡧࡱ࡭ࡺࡳ࠮ࡸࡧࡥࡨࡷ࡯ࡶࡦࡴࠥᆓ")
    bstack1ll1111ll11_opy_ = bstack111l11_opy_ (u"ࠨࡲࡦ࡯ࡲࡸࡪ࠴ࡷࡦࡤࡧࡶ࡮ࡼࡥࡳࠤᆔ")
    bstack1ll11l1l111_opy_ = bstack111l11_opy_ (u"ࠢࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿ࡟ࡪࡰ࡬ࡸࠧᆕ")
    bstack1ll11ll11ll_opy_ = bstack111l11_opy_ (u"ࠣࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡠ࡫ࡶࡣࡸࡩࡡ࡯ࡰ࡬ࡲ࡬ࠨᆖ")
    bstack1ll11l1l1l1_opy_ = bstack111l11_opy_ (u"ࠤࡧࡶ࡮ࡼࡥࡳࡡ࡫ࡥࡸࡥࡵࡳ࡮ࠥᆗ")
    scripts: Dict[str, Dict[str, str]]
    commands: Dict[str, Dict[str, Dict[str, List[str]]]]
    def __init__(self, bstack1lll11lllll_opy_, bstack1llll11l1l1_opy_):
        super().__init__()
        self.scripts = dict()
        self.commands = dict()
        self.accessibility = False
        self.bstack1ll111l11l1_opy_ = False
        self.bstack1ll111ll111_opy_ = dict()
        if not self.is_enabled():
            return
        self.bstack1ll111l1111_opy_ = bstack1llll11l1l1_opy_
        bstack1lll11lllll_opy_.bstack1ll11llll1l_opy_((bstack1llllll111l_opy_.bstack1llll1llll1_opy_, bstack1llll1l111l_opy_.PRE), self.bstack1ll11l1lll1_opy_)
        TestFramework.bstack1ll11llll1l_opy_((bstack1lll11ll111_opy_.TEST, bstack1lll1lll111_opy_.PRE), self.bstack1ll111ll11l_opy_)
        TestFramework.bstack1ll11llll1l_opy_((bstack1lll11ll111_opy_.TEST, bstack1lll1lll111_opy_.POST), self.bstack1ll11111lll_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1ll111ll11l_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1llll1l_opy_,
        bstack1llllll1l1l_opy_: Tuple[bstack1lll11ll111_opy_, bstack1lll1lll111_opy_],
        *args,
        **kwargs,
    ):
        tags = self._1ll11l11ll1_opy_(instance, args)
        test_framework = f.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1ll111l111l_opy_)
        if self.bstack1ll111l11l1_opy_:
            self.bstack1ll111ll111_opy_[bstack111l11_opy_ (u"ࠥࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠥᆘ")] = f.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1ll11l111l1_opy_)
        if bstack111l11_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠨᆙ") in instance.bstack1ll11l1111l_opy_:
            platform_index = f.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1ll1111lll1_opy_)
            self.accessibility = self.bstack1ll11llllll_opy_(tags, self.config[bstack111l11_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨᆚ")][platform_index])
        else:
            capabilities = self.bstack1ll111l1111_opy_.bstack1ll11l11l11_opy_(f, instance, bstack1llllll1l1l_opy_, *args, **kwargs)
            if not capabilities:
                self.logger.debug(bstack111l11_opy_ (u"ࠨ࡯࡯ࡡࡥࡩ࡫ࡵࡲࡦࡡࡷࡩࡸࡺ࠺ࠡࡰࡲࠤࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠣࡪࡴࡻ࡮ࡥࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࡾ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࠨᆛ") + str(kwargs) + bstack111l11_opy_ (u"ࠢࠣᆜ"))
                return
            self.accessibility = self.bstack1ll11llllll_opy_(tags, capabilities)
        if self.bstack1ll111l1111_opy_.pages and self.bstack1ll111l1111_opy_.pages.values():
            bstack1ll11l111ll_opy_ = list(self.bstack1ll111l1111_opy_.pages.values())
            if bstack1ll11l111ll_opy_ and isinstance(bstack1ll11l111ll_opy_[0], (list, tuple)) and bstack1ll11l111ll_opy_[0]:
                bstack1ll111ll1ll_opy_ = bstack1ll11l111ll_opy_[0][0]
                if callable(bstack1ll111ll1ll_opy_):
                    page = bstack1ll111ll1ll_opy_()
                    def bstack11111llll_opy_():
                        self.get_accessibility_results(page, bstack111l11_opy_ (u"ࠣࡲ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࠧᆝ"))
                    def bstack1ll111lllll_opy_():
                        self.get_accessibility_results_summary(page, bstack111l11_opy_ (u"ࠤࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠨᆞ"))
                    setattr(page, bstack111l11_opy_ (u"ࠥ࡫ࡪࡺࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡘࡥࡴࡷ࡯ࡸࡸࠨᆟ"), bstack11111llll_opy_)
                    setattr(page, bstack111l11_opy_ (u"ࠦ࡬࡫ࡴࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡒࡦࡵࡸࡰࡹ࡙ࡵ࡮࡯ࡤࡶࡾࠨᆠ"), bstack1ll111lllll_opy_)
        self.logger.debug(bstack111l11_opy_ (u"ࠧࡹࡨࡰࡷ࡯ࡨࠥࡸࡵ࡯ࠢࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡹࡥࡱࡻࡥ࠾ࠤᆡ") + str(self.accessibility) + bstack111l11_opy_ (u"ࠨࠢᆢ"))
    def bstack1ll11l1lll1_opy_(
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
            bstack11l1ll1l_opy_ = datetime.now()
            self.bstack1ll1l111l11_opy_(f, exec, *args, **kwargs)
            instance, method_name = exec
            instance.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠢࡢ࠳࠴ࡽ࠿࡯࡮ࡪࡶࡢࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡢࡧࡴࡴࡦࡪࡩࠥᆣ"), datetime.now() - bstack11l1ll1l_opy_)
            if (
                not f.bstack1ll111lll1l_opy_(method_name)
                or f.bstack1ll11lll1ll_opy_(method_name, *args)
                or f.bstack1ll11llll11_opy_(method_name, *args)
            ):
                return
            if not f.bstack1llll1l11ll_opy_(instance, bstack1lll1l11l1l_opy_.bstack1ll11l1l111_opy_, False):
                if not bstack1lll1l11l1l_opy_.bstack1ll11111l1l_opy_:
                    self.logger.warning(bstack111l11_opy_ (u"ࠣ࡝ࡳࡰࡦࡺࡦࡰࡴࡰࡣ࡮ࡴࡤࡦࡺࡀࠦᆤ") + str(f.platform_index) + bstack111l11_opy_ (u"ࠤࡠࠤࡦ࠷࠱ࡺࠢࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠡࡪࡤࡺࡪࠦ࡮ࡰࡶࠣࡦࡪ࡫࡮ࠡࡵࡨࡸࠥ࡬࡯ࡳࠢࡷ࡬࡮ࡹࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠣᆥ"))
                    bstack1lll1l11l1l_opy_.bstack1ll11111l1l_opy_ = True
                return
            bstack1ll11111ll1_opy_ = self.scripts.get(f.framework_name, {})
            if not bstack1ll11111ll1_opy_:
                platform_index = f.bstack1llll1l11ll_opy_(instance, bstack1ll1ll1l11l_opy_.bstack1ll1111lll1_opy_, 0)
                self.logger.debug(bstack111l11_opy_ (u"ࠥࡲࡴࠦࡡ࠲࠳ࡼࠤࡸࡩࡲࡪࡲࡷࡷࠥ࡬࡯ࡳࠢࡳࡰࡦࡺࡦࡰࡴࡰࡣ࡮ࡴࡤࡦࡺࡀࡿࡵࡲࡡࡵࡨࡲࡶࡲࡥࡩ࡯ࡦࡨࡼࢂࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫࠽ࠣᆦ") + str(f.framework_name) + bstack111l11_opy_ (u"ࠦࠧᆧ"))
                return
            command_name = f.bstack1ll111l1ll1_opy_(*args)
            if not command_name:
                self.logger.debug(bstack111l11_opy_ (u"ࠧࡳࡩࡴࡵ࡬ࡲ࡬ࠦࡣࡰ࡯ࡰࡥࡳࡪ࡟࡯ࡣࡰࡩࠥ࡬࡯ࡳࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡴࡡ࡮ࡧࡀࡿ࡫࠴ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫ࡽࠡ࡯ࡨࡸ࡭ࡵࡤࡠࡰࡤࡱࡪࡃࠢᆨ") + str(method_name) + bstack111l11_opy_ (u"ࠨࠢᆩ"))
                return
            bstack1ll11lll1l1_opy_ = f.bstack1llll1l11ll_opy_(instance, bstack1lll1l11l1l_opy_.bstack1ll11l1l1l1_opy_, False)
            if command_name == bstack111l11_opy_ (u"ࠢࡨࡧࡷࠦᆪ") and not bstack1ll11lll1l1_opy_:
                f.bstack1llll1l11l1_opy_(instance, bstack1lll1l11l1l_opy_.bstack1ll11l1l1l1_opy_, True)
                bstack1ll11lll1l1_opy_ = True
            if not bstack1ll11lll1l1_opy_ and not self.bstack1ll111l11l1_opy_:
                self.logger.debug(bstack111l11_opy_ (u"ࠣࡰࡲࠤ࡚ࡘࡌࠡ࡮ࡲࡥࡩ࡫ࡤࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦ࠿ࡾࡪ࠳࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡰࡤࡱࡪࢃࠠࡤࡱࡰࡱࡦࡴࡤࡠࡰࡤࡱࡪࡃࠢᆫ") + str(command_name) + bstack111l11_opy_ (u"ࠤࠥᆬ"))
                return
            scripts_to_run = self.commands.get(f.framework_name, {}).get(method_name, {}).get(command_name, [])
            if not scripts_to_run:
                self.logger.debug(bstack111l11_opy_ (u"ࠥࡲࡴࠦࡡ࠲࠳ࡼࠤࡸࡩࡲࡪࡲࡷࡷࠥ࡬࡯ࡳࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡴࡡ࡮ࡧࡀࡿ࡫࠴ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫ࡽࠡࡥࡲࡱࡲࡧ࡮ࡥࡡࡱࡥࡲ࡫࠽ࠣᆭ") + str(command_name) + bstack111l11_opy_ (u"ࠦࠧᆮ"))
                return
            self.logger.info(bstack111l11_opy_ (u"ࠧࡸࡵ࡯ࡰ࡬ࡲ࡬ࠦࡻ࡭ࡧࡱࠬࡸࡩࡲࡪࡲࡷࡷࡤࡺ࡯ࡠࡴࡸࡲ࠮ࢃࠠࡴࡥࡵ࡭ࡵࡺࡳࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦ࠿ࡾࡪ࠳࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡰࡤࡱࡪࢃࠠࡤࡱࡰࡱࡦࡴࡤࡠࡰࡤࡱࡪࡃࠢᆯ") + str(command_name) + bstack111l11_opy_ (u"ࠨࠢᆰ"))
            scripts = [(s, bstack1ll11111ll1_opy_[s]) for s in scripts_to_run if s in bstack1ll11111ll1_opy_]
            for script_name, bstack1ll111ll1l1_opy_ in scripts:
                try:
                    bstack11l1ll1l_opy_ = datetime.now()
                    if script_name == bstack111l11_opy_ (u"ࠢࡴࡥࡤࡲࠧᆱ"):
                        result = self.perform_scan(driver, method=command_name, framework_name=f.framework_name)
                    instance.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠣࡣ࠴࠵ࡾࡀࠢᆲ") + script_name, datetime.now() - bstack11l1ll1l_opy_)
                    if isinstance(result, dict) and not result.get(bstack111l11_opy_ (u"ࠤࡶࡹࡨࡩࡥࡴࡵࠥᆳ"), True):
                        self.logger.warning(bstack111l11_opy_ (u"ࠥࡷࡰ࡯ࡰࠡࡧࡻࡩࡨࡻࡴࡪࡰࡪࠤࡷ࡫࡭ࡢ࡫ࡱ࡭ࡳ࡭ࠠࡴࡥࡵ࡭ࡵࡺࡳ࠻ࠢࠥᆴ") + str(result) + bstack111l11_opy_ (u"ࠦࠧᆵ"))
                        break
                except Exception as e:
                    self.logger.error(bstack111l11_opy_ (u"ࠧ࡫ࡲࡳࡱࡵࠤࡪࡾࡥࡤࡷࡷ࡭ࡳ࡭ࠠࡴࡥࡵ࡭ࡵࡺ࠽ࡼࡵࡦࡶ࡮ࡶࡴࡠࡰࡤࡱࡪࢃࠠࡦࡴࡵࡳࡷࡃࠢᆶ") + str(e) + bstack111l11_opy_ (u"ࠨࠢᆷ"))
        except Exception as e:
            self.logger.error(bstack111l11_opy_ (u"ࠢࡰࡰࡢࡦࡪ࡬࡯ࡳࡧࡢࡩࡽ࡫ࡣࡶࡶࡨࠤࡪࡸࡲࡰࡴࡀࠦᆸ") + str(e) + bstack111l11_opy_ (u"ࠣࠤᆹ"))
    def bstack1ll11111lll_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1llll1l_opy_,
        bstack1llllll1l1l_opy_: Tuple[bstack1lll11ll111_opy_, bstack1lll1lll111_opy_],
        *args,
        **kwargs,
    ):
        tags = self._1ll11l11ll1_opy_(instance, args)
        capabilities = self.bstack1ll111l1111_opy_.bstack1ll11l11l11_opy_(f, instance, bstack1llllll1l1l_opy_, *args, **kwargs)
        self.accessibility = self.bstack1ll11llllll_opy_(tags, capabilities)
        if not self.accessibility:
            self.logger.debug(bstack111l11_opy_ (u"ࠤࡲࡲࡤࡧࡦࡵࡧࡵࡣࡹ࡫ࡳࡵ࠼ࠣࡥ࠶࠷ࡹࠡࡰࡲࡸࠥ࡫࡮ࡢࡤ࡯ࡩࡩࠨᆺ"))
            return
        driver = self.bstack1ll111l1111_opy_.bstack1ll11ll111l_opy_(f, instance, bstack1llllll1l1l_opy_, *args, **kwargs)
        test_name = f.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1ll11lll11l_opy_)
        if not test_name:
            self.logger.debug(bstack111l11_opy_ (u"ࠥࡳࡳࡥࡡࡧࡶࡨࡶࡤࡺࡥࡴࡶ࠽ࠤࡲ࡯ࡳࡴ࡫ࡱ࡫ࠥࡺࡥࡴࡶࠣࡲࡦࡳࡥࠣᆻ"))
            return
        test_uuid = f.bstack1llll1l11ll_opy_(instance, TestFramework.bstack1ll11l111l1_opy_)
        if not test_uuid:
            self.logger.debug(bstack111l11_opy_ (u"ࠦࡴࡴ࡟ࡢࡨࡷࡩࡷࡥࡴࡦࡵࡷ࠾ࠥࡳࡩࡴࡵ࡬ࡲ࡬ࠦࡴࡦࡵࡷࠤࡺࡻࡩࡥࠤᆼ"))
            return
        if isinstance(self.bstack1ll111l1111_opy_, bstack1ll1llllll1_opy_):
            framework_name = bstack111l11_opy_ (u"ࠬࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠩᆽ")
        else:
            framework_name = bstack111l11_opy_ (u"࠭ࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࠨᆾ")
        self.bstack111l1lll_opy_(driver, test_name, framework_name, test_uuid)
    def perform_scan(self, driver: object, method: Union[None, str], framework_name: str):
        bstack1ll1111l1l1_opy_ = bstack1ll1l1ll1l1_opy_.bstack1ll11l1ll1l_opy_(EVENTS.bstack11111ll1_opy_.value)
        if not self.accessibility:
            self.logger.debug(bstack111l11_opy_ (u"ࠢࡱࡧࡵࡪࡴࡸ࡭ࡠࡵࡦࡥࡳࡀࠠࡢ࠳࠴ࡽࠥࡴ࡯ࡵࠢࡨࡲࡦࡨ࡬ࡦࡦࠣࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥ࡮ࡢ࡯ࡨࡁࢀ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡰࡤࡱࡪࢃࠠࠣᆿ"))
            return
        bstack11l1ll1l_opy_ = datetime.now()
        bstack1ll111ll1l1_opy_ = self.scripts.get(framework_name, {}).get(bstack111l11_opy_ (u"ࠣࡵࡦࡥࡳࠨᇀ"), None)
        if not bstack1ll111ll1l1_opy_:
            self.logger.debug(bstack111l11_opy_ (u"ࠤࡳࡩࡷ࡬࡯ࡳ࡯ࡢࡷࡨࡧ࡮࠻ࠢࡰ࡭ࡸࡹࡩ࡯ࡩࠣࠫࡸࡩࡡ࡯ࠩࠣࡷࡨࡸࡩࡱࡶࠣࡪࡴࡸࠠࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡲࡦࡳࡥ࠾ࠤᇁ") + str(framework_name) + bstack111l11_opy_ (u"ࠥࠤࠧᇂ"))
            return
        if self.bstack1ll111l11l1_opy_:
            arg = dict()
            arg[bstack111l11_opy_ (u"ࠦࡲ࡫ࡴࡩࡱࡧࠦᇃ")] = method if method else bstack111l11_opy_ (u"ࠧࠨᇄ")
            arg[bstack111l11_opy_ (u"ࠨࡴࡩࡖࡨࡷࡹࡘࡵ࡯ࡗࡸ࡭ࡩࠨᇅ")] = self.bstack1ll111ll111_opy_[bstack111l11_opy_ (u"ࠢࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠢᇆ")]
            arg[bstack111l11_opy_ (u"ࠣࡶ࡫ࡆࡺ࡯࡬ࡥࡗࡸ࡭ࡩࠨᇇ")] = self.bstack1ll111ll111_opy_[bstack111l11_opy_ (u"ࠤࡷࡩࡸࡺࡨࡶࡤࡢࡦࡺ࡯࡬ࡥࡡࡸࡹ࡮ࡪࠢᇈ")]
            arg[bstack111l11_opy_ (u"ࠥࡥࡺࡺࡨࡉࡧࡤࡨࡪࡸࠢᇉ")] = self.bstack1ll111ll111_opy_[bstack111l11_opy_ (u"ࠦࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡘࡴࡱࡥ࡯ࠤᇊ")]
            arg[bstack111l11_opy_ (u"ࠧࡺࡨࡋࡹࡷࡘࡴࡱࡥ࡯ࠤᇋ")] = self.bstack1ll111ll111_opy_[bstack111l11_opy_ (u"ࠨࡴࡩࡡ࡭ࡻࡹࡥࡴࡰ࡭ࡨࡲࠧᇌ")]
            arg[bstack111l11_opy_ (u"ࠢࡴࡥࡤࡲ࡙࡯࡭ࡦࡵࡷࡥࡲࡶࠢᇍ")] = str(int(datetime.now().timestamp() * 1000))
            bstack1ll11l1llll_opy_ = bstack1ll111ll1l1_opy_ % json.dumps(arg)
            driver.execute_script(bstack1ll11l1llll_opy_)
            return
        instance = bstack1lllll1l1l1_opy_.bstack1lllllll1ll_opy_(driver)
        if instance:
            if not bstack1lllll1l1l1_opy_.bstack1llll1l11ll_opy_(instance, bstack1lll1l11l1l_opy_.bstack1ll11ll11ll_opy_, False):
                bstack1lllll1l1l1_opy_.bstack1llll1l11l1_opy_(instance, bstack1lll1l11l1l_opy_.bstack1ll11ll11ll_opy_, True)
            else:
                self.logger.info(bstack111l11_opy_ (u"ࠣࡲࡨࡶ࡫ࡵࡲ࡮ࡡࡶࡧࡦࡴ࠺ࠡࡣ࡯ࡶࡪࡧࡤࡺࠢ࡬ࡲࠥࡶࡲࡰࡩࡵࡩࡸࡹࠠࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡲࡦࡳࡥ࠾ࡽࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡴࡡ࡮ࡧࢀࠤࡲ࡫ࡴࡩࡱࡧࡁࠧᇎ") + str(method) + bstack111l11_opy_ (u"ࠤࠥᇏ"))
                return
        self.logger.info(bstack111l11_opy_ (u"ࠥࡴࡪࡸࡦࡰࡴࡰࡣࡸࡩࡡ࡯࠼ࠣࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥ࡮ࡢ࡯ࡨࡁࢀ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡰࡤࡱࡪࢃࠠ࡮ࡧࡷ࡬ࡴࡪ࠽ࠣᇐ") + str(method) + bstack111l11_opy_ (u"ࠦࠧᇑ"))
        if framework_name == bstack111l11_opy_ (u"ࠬࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠩᇒ"):
            result = self.bstack1ll111l1111_opy_.bstack1ll111l11ll_opy_(driver, bstack1ll111ll1l1_opy_)
        else:
            result = driver.execute_async_script(bstack1ll111ll1l1_opy_, {bstack111l11_opy_ (u"ࠨ࡭ࡦࡶ࡫ࡳࡩࠨᇓ"): method if method else bstack111l11_opy_ (u"ࠢࠣᇔ")})
        bstack1ll1l1ll1l1_opy_.end(EVENTS.bstack11111ll1_opy_.value, bstack1ll1111l1l1_opy_+bstack111l11_opy_ (u"ࠣ࠼ࡶࡸࡦࡸࡴࠣᇕ"), bstack1ll1111l1l1_opy_+bstack111l11_opy_ (u"ࠤ࠽ࡩࡳࡪࠢᇖ"), True, None, command=method)
        if instance:
            bstack1lllll1l1l1_opy_.bstack1llll1l11l1_opy_(instance, bstack1lll1l11l1l_opy_.bstack1ll11ll11ll_opy_, False)
            instance.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠥࡥ࠶࠷ࡹ࠻ࡲࡨࡶ࡫ࡵࡲ࡮ࡡࡶࡧࡦࡴࠢᇗ"), datetime.now() - bstack11l1ll1l_opy_)
        return result
        def bstack1ll1111llll_opy_(self, driver: object, framework_name, bstack1lll1l1111_opy_: str):
            self.bstack1ll11l11111_opy_()
            req = structs.AccessibilityResultRequest()
            req.bin_session_id = self.bin_session_id
            req.bstack1ll11ll1111_opy_ = self.bstack1ll111ll111_opy_[bstack111l11_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠦᇘ")]
            req.bstack1lll1l1111_opy_ = bstack1lll1l1111_opy_
            req.session_id = self.bin_session_id
            try:
                r = self.bstack1ll1ll1ll1l_opy_.AccessibilityResult(req)
                if not r.success:
                    self.logger.debug(bstack111l11_opy_ (u"ࠧࡸࡥࡤࡧ࡬ࡺࡪࡪࠠࡧࡴࡲࡱࠥࡹࡥࡳࡸࡨࡶ࠿ࠦࠢᇙ") + str(r) + bstack111l11_opy_ (u"ࠨࠢᇚ"))
                else:
                    bstack1ll1111l1ll_opy_ = json.loads(r.bstack1ll1111l111_opy_.decode(bstack111l11_opy_ (u"ࠧࡶࡶࡩ࠱࠽࠭ᇛ")))
                    if bstack1lll1l1111_opy_ == bstack111l11_opy_ (u"ࠨࡩࡨࡸࡗ࡫ࡳࡶ࡮ࡷࡷࠬᇜ"):
                        return bstack1ll1111l1ll_opy_.get(bstack111l11_opy_ (u"ࠤࡧࡥࡹࡧࠢᇝ"), [])
                    else:
                        return bstack1ll1111l1ll_opy_.get(bstack111l11_opy_ (u"ࠥࡨࡦࡺࡡࠣᇞ"), {})
            except grpc.RpcError as e:
                self.logger.error(bstack111l11_opy_ (u"ࠦࡷࡶࡣ࠮ࡧࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦࡦࡦࡶࡦ࡬࡮ࡴࡧࠡࡩࡨࡸࡤࡧࡰࡱࡡࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡡࡵࡩࡸࡻ࡬ࡵࠢࡩࡶࡴࡳࠠࡤ࡮࡬࠾ࠥࠨᇟ") + str(e) + bstack111l11_opy_ (u"ࠧࠨᇠ"))
    @measure(event_name=EVENTS.bstack1ll11l111l_opy_, stage=STAGE.bstack111lllll1_opy_)
    def get_accessibility_results(self, driver: object, framework_name):
        if not self.accessibility:
            self.logger.debug(bstack111l11_opy_ (u"ࠨࡧࡦࡶࡢࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡢࡶࡪࡹࡵ࡭ࡶࡶ࠾ࠥࡧ࠱࠲ࡻࠣࡲࡴࡺࠠࡦࡰࡤࡦࡱ࡫ࡤࠣᇡ"))
            return
        if self.bstack1ll111l11l1_opy_:
            self.logger.debug(bstack111l11_opy_ (u"ࠧࡑࡧࡵࡪࡴࡸ࡭ࡪࡰࡪࠤࡸࡩࡡ࡯ࠢࡩࡳࡷࠦࡡࡱࡲࠣࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪᇢ"))
            self.perform_scan(driver, method=None, framework_name=framework_name)
            return self.bstack1ll1111llll_opy_(driver, framework_name, bstack111l11_opy_ (u"ࠣࡩࡨࡸࡗ࡫ࡳࡶ࡮ࡷࡷࠧᇣ"))
        bstack1ll111ll1l1_opy_ = self.scripts.get(framework_name, {}).get(bstack111l11_opy_ (u"ࠤࡪࡩࡹࡘࡥࡴࡷ࡯ࡸࡸࠨᇤ"), None)
        if not bstack1ll111ll1l1_opy_:
            self.logger.debug(bstack111l11_opy_ (u"ࠥࡱ࡮ࡹࡳࡪࡰࡪࠤࠬ࡭ࡥࡵࡔࡨࡷࡺࡲࡴࡴࠩࠣࡷࡨࡸࡩࡱࡶࠣࡪࡴࡸࠠࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡲࡦࡳࡥ࠾ࠤᇥ") + str(framework_name) + bstack111l11_opy_ (u"ࠦࠧᇦ"))
            return
        self.perform_scan(driver, method=None, framework_name=framework_name)
        bstack11l1ll1l_opy_ = datetime.now()
        if framework_name == bstack111l11_opy_ (u"ࠬࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠩᇧ"):
            result = self.bstack1ll111l1111_opy_.bstack1ll111l11ll_opy_(driver, bstack1ll111ll1l1_opy_)
        else:
            result = driver.execute_async_script(bstack1ll111ll1l1_opy_)
        instance = bstack1lllll1l1l1_opy_.bstack1lllllll1ll_opy_(driver)
        if instance:
            instance.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠨࡡ࠲࠳ࡼ࠾࡬࡫ࡴࡠࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡠࡴࡨࡷࡺࡲࡴࡴࠤᇨ"), datetime.now() - bstack11l1ll1l_opy_)
        return result
    @measure(event_name=EVENTS.bstack1ll1ll111l_opy_, stage=STAGE.bstack111lllll1_opy_)
    def get_accessibility_results_summary(self, driver: object, framework_name):
        if not self.accessibility:
            self.logger.debug(bstack111l11_opy_ (u"ࠢࡨࡧࡷࡣࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡣࡷ࡫ࡳࡶ࡮ࡷࡷࡤࡹࡵ࡮࡯ࡤࡶࡾࡀࠠࡢ࠳࠴ࡽࠥࡴ࡯ࡵࠢࡨࡲࡦࡨ࡬ࡦࡦࠥᇩ"))
            return
        if self.bstack1ll111l11l1_opy_:
            self.perform_scan(driver, method=None, framework_name=framework_name)
            return self.bstack1ll1111llll_opy_(driver, framework_name, bstack111l11_opy_ (u"ࠨࡩࡨࡸࡗ࡫ࡳࡶ࡮ࡷࡷࡘࡻ࡭࡮ࡣࡵࡽࠬᇪ"))
        bstack1ll111ll1l1_opy_ = self.scripts.get(framework_name, {}).get(bstack111l11_opy_ (u"ࠤࡪࡩࡹࡘࡥࡴࡷ࡯ࡸࡸ࡙ࡵ࡮࡯ࡤࡶࡾࠨᇫ"), None)
        if not bstack1ll111ll1l1_opy_:
            self.logger.debug(bstack111l11_opy_ (u"ࠥࡱ࡮ࡹࡳࡪࡰࡪࠤࠬ࡭ࡥࡵࡔࡨࡷࡺࡲࡴࡴࡕࡸࡱࡲࡧࡲࡺࠩࠣࡷࡨࡸࡩࡱࡶࠣࡪࡴࡸࠠࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡲࡦࡳࡥ࠾ࠤᇬ") + str(framework_name) + bstack111l11_opy_ (u"ࠦࠧᇭ"))
            return
        self.perform_scan(driver, method=None, framework_name=framework_name)
        bstack11l1ll1l_opy_ = datetime.now()
        if framework_name == bstack111l11_opy_ (u"ࠬࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠩᇮ"):
            result = self.bstack1ll111l1111_opy_.bstack1ll111l11ll_opy_(driver, bstack1ll111ll1l1_opy_)
        else:
            result = driver.execute_async_script(bstack1ll111ll1l1_opy_)
        instance = bstack1lllll1l1l1_opy_.bstack1lllllll1ll_opy_(driver)
        if instance:
            instance.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠨࡡ࠲࠳ࡼ࠾࡬࡫ࡴࡠࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡠࡴࡨࡷࡺࡲࡴࡴࡡࡶࡹࡲࡳࡡࡳࡻࠥᇯ"), datetime.now() - bstack11l1ll1l_opy_)
        return result
    @measure(event_name=EVENTS.bstack1ll11l1ll11_opy_, stage=STAGE.bstack111lllll1_opy_)
    def bstack1ll11ll1l11_opy_(
        self,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        hub_url: str,
    ):
        self.bstack1ll11l11111_opy_()
        req = structs.AccessibilityConfigRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.hub_url = hub_url
        try:
            r = self.bstack1ll1ll1ll1l_opy_.AccessibilityConfig(req)
            if not r.success:
                self.logger.debug(bstack111l11_opy_ (u"ࠢࡳࡧࡦࡩ࡮ࡼࡥࡥࠢࡩࡶࡴࡳࠠࡴࡧࡵࡺࡪࡸ࠺ࠡࠤᇰ") + str(r) + bstack111l11_opy_ (u"ࠣࠤᇱ"))
            else:
                self.bstack1ll11l1l1ll_opy_(framework_name, r)
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack111l11_opy_ (u"ࠤࡵࡴࡨ࠳ࡥࡳࡴࡲࡶ࠿ࠦࠢᇲ") + str(e) + bstack111l11_opy_ (u"ࠥࠦᇳ"))
            traceback.print_exc()
            raise e
    def bstack1ll11l1l1ll_opy_(self, framework_name: str, result: structs.AccessibilityConfigResponse) -> bool:
        if not result.success or not result.accessibility.success:
            self.logger.debug(bstack111l11_opy_ (u"ࠦࡱࡵࡡࡥࡡࡦࡳࡳ࡬ࡩࡨ࠼ࠣࡥ࠶࠷ࡹࠡࡰࡲࡸࠥ࡬࡯ࡶࡰࡧࠦᇴ"))
            return False
        if result.accessibility.is_app_accessibility:
            self.bstack1ll111l11l1_opy_ = result.accessibility.is_app_accessibility
        if result.testhub.build_hashed_id:
            self.bstack1ll111ll111_opy_[bstack111l11_opy_ (u"ࠧࡺࡥࡴࡶ࡫ࡹࡧࡥࡢࡶ࡫࡯ࡨࡤࡻࡵࡪࡦࠥᇵ")] = result.testhub.build_hashed_id
        if result.testhub.jwt:
            self.bstack1ll111ll111_opy_[bstack111l11_opy_ (u"ࠨࡴࡩࡡ࡭ࡻࡹࡥࡴࡰ࡭ࡨࡲࠧᇶ")] = result.testhub.jwt
        if result.accessibility.options:
            options = result.accessibility.options
            if options.capabilities:
                for caps in options.capabilities:
                    self.bstack1ll111ll111_opy_[caps.name] = caps.value
            if options.scripts:
                self.scripts[framework_name] = {row.name: row.command for row in options.scripts}
            if options.commands_to_wrap and options.commands_to_wrap.commands:
                scripts_to_run = [s for s in options.commands_to_wrap.scripts_to_run]
                if not scripts_to_run:
                    return False
                bstack1ll11lllll1_opy_ = dict()
                for command in options.commands_to_wrap.commands:
                    if command.library == self.bstack1ll1l1111ll_opy_ and command.module == self.bstack1ll1111ll11_opy_:
                        if command.method and not command.method in bstack1ll11lllll1_opy_:
                            bstack1ll11lllll1_opy_[command.method] = dict()
                        if command.name and not command.name in bstack1ll11lllll1_opy_[command.method]:
                            bstack1ll11lllll1_opy_[command.method][command.name] = list()
                        bstack1ll11lllll1_opy_[command.method][command.name].extend(scripts_to_run)
                self.commands[framework_name] = bstack1ll11lllll1_opy_
        return bool(self.commands.get(framework_name, None))
    def bstack1ll1l111l11_opy_(
        self,
        f: bstack1ll1ll1l11l_opy_,
        exec: Tuple[bstack1lllll1ll1l_opy_, str],
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if isinstance(self.bstack1ll111l1111_opy_, bstack1ll1llllll1_opy_) and method_name != bstack111l11_opy_ (u"ࠧࡤࡱࡱࡲࡪࡩࡴࠨᇷ"):
            return
        if bstack1lllll1l1l1_opy_.bstack1lllll111ll_opy_(instance, bstack1lll1l11l1l_opy_.bstack1ll11l1l111_opy_):
            return
        if f.bstack1ll111lll11_opy_(method_name, *args):
            bstack1ll11ll1ll1_opy_ = False
            desired_capabilities = f.bstack1ll11lll111_opy_(instance)
            if isinstance(desired_capabilities, dict):
                hub_url = f.bstack1ll1l111111_opy_(instance)
                platform_index = f.bstack1llll1l11ll_opy_(instance, bstack1ll1ll1l11l_opy_.bstack1ll1111lll1_opy_, 0)
                bstack1ll11l11lll_opy_ = datetime.now()
                r = self.bstack1ll11ll1l11_opy_(platform_index, f.framework_name, f.framework_version, hub_url)
                instance.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠣࡩࡵࡴࡨࡀࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡥࡣࡰࡰࡩ࡭࡬ࠨᇸ"), datetime.now() - bstack1ll11l11lll_opy_)
                bstack1ll11ll1ll1_opy_ = r.success
            else:
                self.logger.error(bstack111l11_opy_ (u"ࠤࡰ࡭ࡸࡹࡩ࡯ࡩࠣࡨࡪࡹࡩࡳࡧࡧࠤࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࡀࠦᇹ") + str(desired_capabilities) + bstack111l11_opy_ (u"ࠥࠦᇺ"))
            f.bstack1llll1l11l1_opy_(instance, bstack1lll1l11l1l_opy_.bstack1ll11l1l111_opy_, bstack1ll11ll1ll1_opy_)
    def bstack11l1l1ll11_opy_(self, test_tags):
        bstack1ll11ll1l11_opy_ = self.config.get(bstack111l11_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡓࡵࡺࡩࡰࡰࡶࠫᇻ"))
        if not bstack1ll11ll1l11_opy_:
            return True
        try:
            include_tags = bstack1ll11ll1l11_opy_[bstack111l11_opy_ (u"ࠬ࡯࡮ࡤ࡮ࡸࡨࡪ࡚ࡡࡨࡵࡌࡲ࡙࡫ࡳࡵ࡫ࡱ࡫ࡘࡩ࡯ࡱࡧࠪᇼ")] if bstack111l11_opy_ (u"࠭ࡩ࡯ࡥ࡯ࡹࡩ࡫ࡔࡢࡩࡶࡍࡳ࡚ࡥࡴࡶ࡬ࡲ࡬࡙ࡣࡰࡲࡨࠫᇽ") in bstack1ll11ll1l11_opy_ and isinstance(bstack1ll11ll1l11_opy_[bstack111l11_opy_ (u"ࠧࡪࡰࡦࡰࡺࡪࡥࡕࡣࡪࡷࡎࡴࡔࡦࡵࡷ࡭ࡳ࡭ࡓࡤࡱࡳࡩࠬᇾ")], list) else []
            exclude_tags = bstack1ll11ll1l11_opy_[bstack111l11_opy_ (u"ࠨࡧࡻࡧࡱࡻࡤࡦࡖࡤ࡫ࡸࡏ࡮ࡕࡧࡶࡸ࡮ࡴࡧࡔࡥࡲࡴࡪ࠭ᇿ")] if bstack111l11_opy_ (u"ࠩࡨࡼࡨࡲࡵࡥࡧࡗࡥ࡬ࡹࡉ࡯ࡖࡨࡷࡹ࡯࡮ࡨࡕࡦࡳࡵ࡫ࠧሀ") in bstack1ll11ll1l11_opy_ and isinstance(bstack1ll11ll1l11_opy_[bstack111l11_opy_ (u"ࠪࡩࡽࡩ࡬ࡶࡦࡨࡘࡦ࡭ࡳࡊࡰࡗࡩࡸࡺࡩ࡯ࡩࡖࡧࡴࡶࡥࠨሁ")], list) else []
            excluded = any(tag in exclude_tags for tag in test_tags)
            included = len(include_tags) == 0 or any(tag in include_tags for tag in test_tags)
            return not excluded and included
        except Exception as error:
            self.logger.debug(bstack111l11_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡻ࡭࡯࡬ࡦࠢࡹࡥࡱ࡯ࡤࡢࡶ࡬ࡲ࡬ࠦࡴࡦࡵࡷࠤࡨࡧࡳࡦࠢࡩࡳࡷࠦࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡢࡦࡨࡲࡶࡪࠦࡳࡤࡣࡱࡲ࡮ࡴࡧ࠯ࠢࡈࡶࡷࡵࡲࠡ࠼ࠣࠦሂ") + str(error))
        return False
    def bstack1llll1l1_opy_(self, caps):
        try:
            if self.bstack1ll111l11l1_opy_:
                bstack1ll1111l11l_opy_ = caps.get(bstack111l11_opy_ (u"ࠧࡶ࡬ࡢࡶࡩࡳࡷࡳࡎࡢ࡯ࡨࠦሃ"))
                if bstack1ll1111l11l_opy_ is not None and str(bstack1ll1111l11l_opy_).lower() == bstack111l11_opy_ (u"ࠨࡡ࡯ࡦࡵࡳ࡮ࡪࠢሄ"):
                    bstack1ll111l1l11_opy_ = caps.get(bstack111l11_opy_ (u"ࠢࡢࡲࡳ࡭ࡺࡳ࠺ࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡘࡨࡶࡸ࡯࡯࡯ࠤህ")) or caps.get(bstack111l11_opy_ (u"ࠣࡲ࡯ࡥࡹ࡬࡯ࡳ࡯࡙ࡩࡷࡹࡩࡰࡰࠥሆ"))
                    if bstack1ll111l1l11_opy_ is not None and int(bstack1ll111l1l11_opy_) < 11:
                        self.logger.warning(bstack111l11_opy_ (u"ࠤࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࠦࡷࡪ࡮࡯ࠤࡷࡻ࡮ࠡࡱࡱࡰࡾࠦ࡯࡯ࠢࡄࡲࡩࡸ࡯ࡪࡦࠣ࠵࠶ࠦࡡ࡯ࡦࠣࡥࡧࡵࡶࡦ࠰ࠣࡇࡺࡸࡲࡦࡰࡷࠤࡵࡲࡡࡵࡨࡲࡶࡲࠦࡶࡦࡴࡶ࡭ࡴࡴࠠ࠾ࠤሇ") + str(bstack1ll111l1l11_opy_) + bstack111l11_opy_ (u"ࠥࠦለ"))
                        return False
                return True
            bstack1ll11l11l1l_opy_ = caps.get(bstack111l11_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬሉ"), {}).get(bstack111l11_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࡓࡧ࡭ࡦࠩሊ"), caps.get(bstack111l11_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪ࠭ላ"), bstack111l11_opy_ (u"ࠧࠨሌ")))
            if bstack1ll11l11l1l_opy_:
                self.logger.warning(bstack111l11_opy_ (u"ࠣࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠥࡽࡩ࡭࡮ࠣࡶࡺࡴࠠࡰࡰ࡯ࡽࠥࡵ࡮ࠡࡆࡨࡷࡰࡺ࡯ࡱࠢࡥࡶࡴࡽࡳࡦࡴࡶ࠲ࠧል"))
                return False
            browser = caps.get(bstack111l11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧሎ"), bstack111l11_opy_ (u"ࠪࠫሏ")).lower()
            if browser != bstack111l11_opy_ (u"ࠫࡨ࡮ࡲࡰ࡯ࡨࠫሐ"):
                self.logger.warning(bstack111l11_opy_ (u"ࠧࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡺ࡭ࡱࡲࠠࡳࡷࡱࠤࡴࡴ࡬ࡺࠢࡲࡲࠥࡉࡨࡳࡱࡰࡩࠥࡨࡲࡰࡹࡶࡩࡷࡹ࠮ࠣሑ"))
                return False
            bstack1ll111l1lll_opy_ = bstack1ll11ll1l1l_opy_
            if not self.config.get(bstack111l11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨሒ")) or self.config.get(bstack111l11_opy_ (u"ࠧࡵࡷࡵࡦࡴࡹࡣࡢ࡮ࡨࠫሓ")):
                bstack1ll111l1lll_opy_ = bstack1ll1l11111l_opy_
            browser_version = caps.get(bstack111l11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩሔ"))
            if not browser_version:
                browser_version = caps.get(bstack111l11_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪሕ"), {}).get(bstack111l11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫሖ"), bstack111l11_opy_ (u"ࠫࠬሗ"))
            if browser_version and browser_version != bstack111l11_opy_ (u"ࠬࡲࡡࡵࡧࡶࡸࠬመ") and int(browser_version.split(bstack111l11_opy_ (u"࠭࠮ࠨሙ"))[0]) <= bstack1ll111l1lll_opy_:
                self.logger.warning(bstack111l11_opy_ (u"ࠢࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡼ࡯࡬࡭ࠢࡵࡹࡳࠦ࡯࡯࡮ࡼࠤࡴࡴࠠࡄࡪࡵࡳࡲ࡫ࠠࡣࡴࡲࡻࡸ࡫ࡲࠡࡸࡨࡶࡸ࡯࡯࡯ࠢࡪࡶࡪࡧࡴࡦࡴࠣࡸ࡭ࡧ࡮ࠡࠤሚ") + str(bstack1ll111l1lll_opy_) + bstack111l11_opy_ (u"ࠣ࠰ࠥማ"))
                return False
            bstack1ll111llll1_opy_ = caps.get(bstack111l11_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪሜ"), {}).get(bstack111l11_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪም"))
            if not bstack1ll111llll1_opy_:
                bstack1ll111llll1_opy_ = caps.get(bstack111l11_opy_ (u"ࠫ࡬ࡵ࡯ࡨ࠼ࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩሞ"), {})
            if bstack1ll111llll1_opy_ and bstack111l11_opy_ (u"ࠬ࠳࠭ࡩࡧࡤࡨࡱ࡫ࡳࡴࠩሟ") in bstack1ll111llll1_opy_.get(bstack111l11_opy_ (u"࠭ࡡࡳࡩࡶࠫሠ"), []):
                self.logger.warning(bstack111l11_opy_ (u"ࠢࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡼ࡯࡬࡭ࠢࡱࡳࡹࠦࡲࡶࡰࠣࡳࡳࠦ࡬ࡦࡩࡤࡧࡾࠦࡨࡦࡣࡧࡰࡪࡹࡳࠡ࡯ࡲࡨࡪ࠴ࠠࡔࡹ࡬ࡸࡨ࡮ࠠࡵࡱࠣࡲࡪࡽࠠࡩࡧࡤࡨࡱ࡫ࡳࡴࠢࡰࡳࡩ࡫ࠠࡰࡴࠣࡥࡻࡵࡩࡥࠢࡸࡷ࡮ࡴࡧࠡࡪࡨࡥࡩࡲࡥࡴࡵࠣࡱࡴࡪࡥ࠯ࠤሡ"))
                return False
            return True
        except Exception as error:
            self.logger.debug(bstack111l11_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡷࡣ࡯࡭ࡩࡧࡴࡦࠢࡤ࠵࠶ࡿࠠࡴࡷࡳࡴࡴࡸࡴࠡ࠼ࠥሢ") + str(error))
            return False
    def bstack1ll11111l11_opy_(self, test_uuid: str, result: structs.FetchDriverExecuteParamsEventResponse):
        bstack1ll11ll11l1_opy_ = {
            bstack111l11_opy_ (u"ࠩࡷ࡬࡙࡫ࡳࡵࡔࡸࡲ࡚ࡻࡩࡥࠩሣ"): test_uuid,
        }
        bstack1ll1l1111l1_opy_ = {}
        if result.success:
            bstack1ll1l1111l1_opy_ = json.loads(result.accessibility_execute_params)
        return bstack1ll11l1l11l_opy_(bstack1ll11ll11l1_opy_, bstack1ll1l1111l1_opy_)
    def bstack111l1lll_opy_(self, driver: object, name: str, framework_name: str, test_uuid: str):
        bstack1ll1111l1l1_opy_ = None
        try:
            self.bstack1ll11l11111_opy_()
            req = structs.FetchDriverExecuteParamsEventRequest()
            req.bin_session_id = self.bin_session_id
            req.product = bstack111l11_opy_ (u"ࠥࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠥሤ")
            req.script_name = bstack111l11_opy_ (u"ࠦࡸࡧࡶࡦࡔࡨࡷࡺࡲࡴࡴࠤሥ")
            r = self.bstack1ll1ll1ll1l_opy_.FetchDriverExecuteParamsEvent(req)
            if not r.success:
                self.logger.debug(bstack111l11_opy_ (u"ࠧࡸࡥࡤࡧ࡬ࡺࡪࡪࠠࡥࡴ࡬ࡺࡪࡸࠠࡦࡺࡨࡧࡺࡺࡥࠡࡲࡤࡶࡦࡳࡳࠡࡨࡵࡳࡲࠦࡳࡦࡴࡹࡩࡷࡀࠠࠣሦ") + str(r.error) + bstack111l11_opy_ (u"ࠨࠢሧ"))
            else:
                bstack1ll11ll11l1_opy_ = self.bstack1ll11111l11_opy_(test_uuid, r)
                bstack1ll111ll1l1_opy_ = r.script
            self.logger.debug(bstack111l11_opy_ (u"ࠧࡑࡧࡵࡪࡴࡸ࡭ࡪࡰࡪࠤࡸࡩࡡ࡯ࠢࡥࡩ࡫ࡵࡲࡦࠢࡶࡥࡻ࡯࡮ࡨࠢࡵࡩࡸࡻ࡬ࡵࡵࠪረ") + str(bstack1ll11ll11l1_opy_))
            self.perform_scan(driver, name, framework_name=framework_name)
            if not bstack1ll111ll1l1_opy_:
                self.logger.debug(bstack111l11_opy_ (u"ࠣࡲࡨࡶ࡫ࡵࡲ࡮ࡡࡶࡧࡦࡴ࠺ࠡ࡯࡬ࡷࡸ࡯࡮ࡨࠢࠪࡷࡦࡼࡥࡓࡧࡶࡹࡱࡺࡳࠨࠢࡶࡧࡷ࡯ࡰࡵࠢࡩࡳࡷࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫࠽ࠣሩ") + str(framework_name) + bstack111l11_opy_ (u"ࠤࠣࠦሪ"))
                return
            bstack1ll1111l1l1_opy_ = bstack1ll1l1ll1l1_opy_.bstack1ll11l1ll1l_opy_(EVENTS.bstack1ll11ll1lll_opy_.value)
            self.bstack1ll111l1l1l_opy_(driver, bstack1ll111ll1l1_opy_, bstack1ll11ll11l1_opy_, framework_name)
            self.logger.info(bstack111l11_opy_ (u"ࠥࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡸࡪࡹࡴࡪࡰࡪࠤ࡫ࡵࡲࠡࡶ࡫࡭ࡸࠦࡴࡦࡵࡷࠤࡨࡧࡳࡦࠢ࡫ࡥࡸࠦࡥ࡯ࡦࡨࡨ࠳ࠨራ"))
            bstack1ll1l1ll1l1_opy_.end(EVENTS.bstack1ll11ll1lll_opy_.value, bstack1ll1111l1l1_opy_+bstack111l11_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦሬ"), bstack1ll1111l1l1_opy_+bstack111l11_opy_ (u"ࠧࡀࡥ࡯ࡦࠥር"), True, None, command=bstack111l11_opy_ (u"࠭ࡳࡢࡸࡨࡖࡪࡹࡵ࡭ࡶࡶࠫሮ"),test_name=name)
        except Exception as bstack1ll1111ll1l_opy_:
            self.logger.error(bstack111l11_opy_ (u"ࠢࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡳࡧࡶࡹࡱࡺࡳࠡࡥࡲࡹࡱࡪࠠ࡯ࡱࡷࠤࡧ࡫ࠠࡱࡴࡲࡧࡪࡹࡳࡦࡦࠣࡪࡴࡸࠠࡵࡪࡨࠤࡹ࡫ࡳࡵࠢࡦࡥࡸ࡫࠺ࠡࠤሯ") + bstack111l11_opy_ (u"ࠣࡵࡷࡶ࠭ࡶࡡࡵࡪࠬࠦሰ") + bstack111l11_opy_ (u"ࠤࠣࡉࡷࡸ࡯ࡳࠢ࠽ࠦሱ") + str(bstack1ll1111ll1l_opy_))
            bstack1ll1l1ll1l1_opy_.end(EVENTS.bstack1ll11ll1lll_opy_.value, bstack1ll1111l1l1_opy_+bstack111l11_opy_ (u"ࠥ࠾ࡸࡺࡡࡳࡶࠥሲ"), bstack1ll1111l1l1_opy_+bstack111l11_opy_ (u"ࠦ࠿࡫࡮ࡥࠤሳ"), False, bstack1ll1111ll1l_opy_, command=bstack111l11_opy_ (u"ࠬࡹࡡࡷࡧࡕࡩࡸࡻ࡬ࡵࡵࠪሴ"),test_name=name)
    def bstack1ll111l1l1l_opy_(self, driver, bstack1ll111ll1l1_opy_, bstack1ll11ll11l1_opy_, framework_name):
        if framework_name == bstack111l11_opy_ (u"࠭ࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠪስ"):
            self.bstack1ll111l1111_opy_.bstack1ll111l11ll_opy_(driver, bstack1ll111ll1l1_opy_, bstack1ll11ll11l1_opy_)
        else:
            self.logger.debug(driver.execute_async_script(bstack1ll111ll1l1_opy_, bstack1ll11ll11l1_opy_))
    def _1ll11l11ll1_opy_(self, instance: bstack1lll1llll1l_opy_, args: Tuple) -> list:
        bstack111l11_opy_ (u"ࠢࠣࠤࡈࡼࡹࡸࡡࡤࡶࠣࡸࡦ࡭ࡳࠡࡤࡤࡷࡪࡪࠠࡰࡰࠣࡸ࡭࡫ࠠࡵࡧࡶࡸࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫࠯ࠤࠥࠦሶ")
        if bstack111l11_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠬሷ") in instance.bstack1ll11l1111l_opy_:
            return args[2].tags if hasattr(args[2], bstack111l11_opy_ (u"ࠩࡷࡥ࡬ࡹࠧሸ")) else []
        if hasattr(args[0], bstack111l11_opy_ (u"ࠪࡳࡼࡴ࡟࡮ࡣࡵ࡯ࡪࡸࡳࠨሹ")):
            return [marker.name for marker in args[0].own_markers]
        return []
    def bstack1ll11llllll_opy_(self, tags, capabilities):
        return self.bstack11l1l1ll11_opy_(tags) and self.bstack1llll1l1_opy_(capabilities)