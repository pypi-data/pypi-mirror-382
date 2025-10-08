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
from browserstack_sdk.sdk_cli.bstack1lll111ll1l_opy_ import bstack1ll1ll1lll1_opy_
from browserstack_sdk.sdk_cli.bstack1lllll11l1l_opy_ import (
    bstack1llllll111l_opy_,
    bstack1llll1l111l_opy_,
    bstack1lllll1ll1l_opy_,
)
from browserstack_sdk.sdk_cli.bstack1ll1l1ll111_opy_ import bstack1ll1ll1l11l_opy_
from typing import Tuple, Callable, Any
import grpc
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1lll111ll1l_opy_ import bstack1ll1ll1lll1_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
import traceback
import os
import time
class bstack1lll1ll1l11_opy_(bstack1ll1ll1lll1_opy_):
    bstack1ll11111l1l_opy_ = False
    def __init__(self):
        super().__init__()
        bstack1ll1ll1l11l_opy_.bstack1ll11llll1l_opy_((bstack1llllll111l_opy_.bstack1llll1llll1_opy_, bstack1llll1l111l_opy_.PRE), self.bstack1l1lllll1l1_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l1lllll1l1_opy_(
        self,
        f: bstack1ll1ll1l11l_opy_,
        driver: object,
        exec: Tuple[bstack1lllll1ll1l_opy_, str],
        bstack1llllll1l1l_opy_: Tuple[bstack1llllll111l_opy_, bstack1llll1l111l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        hub_url = f.hub_url(driver)
        if f.bstack1l1lllll1ll_opy_(hub_url):
            if not bstack1lll1ll1l11_opy_.bstack1ll11111l1l_opy_:
                self.logger.warning(bstack111l11_opy_ (u"ࠦࡱࡵࡣࡢ࡮ࠣࡷࡪࡲࡦ࠮ࡪࡨࡥࡱࠦࡦ࡭ࡱࡺࠤࡩ࡯ࡳࡢࡤ࡯ࡩࡩࠦࡦࡰࡴࠣࡆࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࠢ࡬ࡲ࡫ࡸࡡࠡࡵࡨࡷࡸ࡯࡯࡯ࡵࠣ࡬ࡺࡨ࡟ࡶࡴ࡯ࡁࠧሺ") + str(hub_url) + bstack111l11_opy_ (u"ࠧࠨሻ"))
                bstack1lll1ll1l11_opy_.bstack1ll11111l1l_opy_ = True
            return
        command_name = f.bstack1ll111l1ll1_opy_(*args)
        bstack1ll1111111l_opy_ = f.bstack1ll111111l1_opy_(*args)
        if command_name and command_name.lower() == bstack111l11_opy_ (u"ࠨࡦࡪࡰࡧࡩࡱ࡫࡭ࡦࡰࡷࠦሼ") and bstack1ll1111111l_opy_:
            framework_session_id = f.session_id(driver)
            locator_type, locator_value = bstack1ll1111111l_opy_.get(bstack111l11_opy_ (u"ࠢࡶࡵ࡬ࡲ࡬ࠨሽ"), None), bstack1ll1111111l_opy_.get(bstack111l11_opy_ (u"ࠣࡸࡤࡰࡺ࡫ࠢሾ"), None)
            if not framework_session_id or not locator_type or not locator_value:
                self.logger.warning(bstack111l11_opy_ (u"ࠤࡾࡧࡴࡳ࡭ࡢࡰࡧࡣࡳࡧ࡭ࡦࡿ࠽ࠤࡲ࡯ࡳࡴ࡫ࡱ࡫ࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡨࡷࡸ࡯࡯࡯ࡡ࡬ࡨࠥࡵࡲࠡࡣࡵ࡫ࡸ࠴ࡵࡴ࡫ࡱ࡫ࡂࢁ࡬ࡰࡥࡤࡸࡴࡸ࡟ࡵࡻࡳࡩࢂࠦ࡯ࡳࠢࡤࡶ࡬ࡹ࠮ࡷࡣ࡯ࡹࡪࡃࠢሿ") + str(locator_value) + bstack111l11_opy_ (u"ࠥࠦቀ"))
                return
            def bstack1lllll1llll_opy_(driver, bstack1l1llllll1l_opy_, *args, **kwargs):
                from selenium.common.exceptions import NoSuchElementException
                try:
                    result = bstack1l1llllll1l_opy_(driver, *args, **kwargs)
                    response = self.bstack1l1llllllll_opy_(
                        framework_session_id=framework_session_id,
                        is_success=True,
                        locator_type=locator_type,
                        locator_value=locator_value,
                    )
                    if response and response.execute_script:
                        driver.execute_script(response.execute_script)
                        self.logger.info(bstack111l11_opy_ (u"ࠦࡸࡻࡣࡤࡧࡶࡷ࠲ࡹࡣࡳ࡫ࡳࡸ࠿ࠦ࡬ࡰࡥࡤࡸࡴࡸ࡟ࡵࡻࡳࡩࡂࢁ࡬ࡰࡥࡤࡸࡴࡸ࡟ࡵࡻࡳࡩࢂࠦ࡬ࡰࡥࡤࡸࡴࡸ࡟ࡷࡣ࡯ࡹࡪࡃࠢቁ") + str(locator_value) + bstack111l11_opy_ (u"ࠧࠨቂ"))
                    else:
                        self.logger.warning(bstack111l11_opy_ (u"ࠨࡳࡶࡥࡦࡩࡸࡹ࠭࡯ࡱ࠰ࡷࡨࡸࡩࡱࡶ࠽ࠤࡱࡵࡣࡢࡶࡲࡶࡤࡺࡹࡱࡧࡀࡿࡱࡵࡣࡢࡶࡲࡶࡤࡺࡹࡱࡧࢀࠤࡱࡵࡣࡢࡶࡲࡶࡤࡼࡡ࡭ࡷࡨࡁࢀࡲ࡯ࡤࡣࡷࡳࡷࡥࡶࡢ࡮ࡸࡩࢂࠦࡲࡦࡵࡳࡳࡳࡹࡥ࠾ࠤቃ") + str(response) + bstack111l11_opy_ (u"ࠢࠣቄ"))
                    return result
                except NoSuchElementException as e:
                    locator = (locator_type, locator_value)
                    return self.__1ll111111ll_opy_(
                        driver, bstack1l1llllll1l_opy_, e, framework_session_id, locator, *args, **kwargs
                    )
            bstack1lllll1llll_opy_.__name__ = command_name
            return bstack1lllll1llll_opy_
    def __1ll111111ll_opy_(
        self,
        driver,
        bstack1l1llllll1l_opy_: Callable,
        exception,
        framework_session_id: str,
        locator: Tuple[str, str],
        *args,
        **kwargs,
    ):
        try:
            locator_type, locator_value = locator
            response = self.bstack1l1llllllll_opy_(
                framework_session_id=framework_session_id,
                is_success=False,
                locator_type=locator_type,
                locator_value=locator_value,
            )
            if response and response.execute_script:
                driver.execute_script(response.execute_script)
                self.logger.info(bstack111l11_opy_ (u"ࠣࡨࡤ࡭ࡱࡻࡲࡦ࠯࡫ࡩࡦࡲࡩ࡯ࡩ࠰ࡸࡷ࡯ࡧࡨࡧࡵࡩࡩࡀࠠ࡭ࡱࡦࡥࡹࡵࡲࡠࡶࡼࡴࡪࡃࡻ࡭ࡱࡦࡥࡹࡵࡲࡠࡶࡼࡴࡪࢃࠠ࡭ࡱࡦࡥࡹࡵࡲࡠࡸࡤࡰࡺ࡫࠽ࠣቅ") + str(locator_value) + bstack111l11_opy_ (u"ࠤࠥቆ"))
                bstack1ll11111111_opy_ = self.bstack1l1llllll11_opy_(
                    framework_session_id=framework_session_id,
                    locator_type=locator_type,
                )
                self.logger.info(bstack111l11_opy_ (u"ࠥࡪࡦ࡯࡬ࡶࡴࡨ࠱࡭࡫ࡡ࡭࡫ࡱ࡫࠲ࡸࡥࡴࡷ࡯ࡸ࠿ࠦ࡬ࡰࡥࡤࡸࡴࡸ࡟ࡵࡻࡳࡩࡂࢁ࡬ࡰࡥࡤࡸࡴࡸ࡟ࡵࡻࡳࡩࢂࠦ࡬ࡰࡥࡤࡸࡴࡸ࡟ࡷࡣ࡯ࡹࡪࡃࡻ࡭ࡱࡦࡥࡹࡵࡲࡠࡸࡤࡰࡺ࡫ࡽࠡࡪࡨࡥࡱ࡯࡮ࡨࡡࡵࡩࡸࡻ࡬ࡵ࠿ࠥቇ") + str(bstack1ll11111111_opy_) + bstack111l11_opy_ (u"ࠦࠧቈ"))
                if bstack1ll11111111_opy_.success and args and len(args) > 1:
                    args[1].update(
                        {
                            bstack111l11_opy_ (u"ࠧࡻࡳࡪࡰࡪࠦ቉"): bstack1ll11111111_opy_.locator_type,
                            bstack111l11_opy_ (u"ࠨࡶࡢ࡮ࡸࡩࠧቊ"): bstack1ll11111111_opy_.locator_value,
                        }
                    )
                    return bstack1l1llllll1l_opy_(driver, *args, **kwargs)
                elif os.environ.get(bstack111l11_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡁࡊࡡࡇࡉࡇ࡛ࡇࠣቋ"), False):
                    self.logger.info(bstack111111ll11_opy_ (u"ࠣࡨࡤ࡭ࡱࡻࡲࡦ࠯࡫ࡩࡦࡲࡩ࡯ࡩ࠰ࡶࡪࡹࡵ࡭ࡶ࠰ࡱ࡮ࡹࡳࡪࡰࡪ࠾ࠥࡹ࡬ࡦࡧࡳࠬ࠸࠶ࠩࠡ࡮ࡨࡸࡹ࡯࡮ࡨࠢࡼࡳࡺࠦࡩ࡯ࡵࡳࡩࡨࡺࠠࡵࡪࡨࠤࡧࡸ࡯ࡸࡵࡨࡶࠥ࡫ࡸࡵࡧࡱࡷ࡮ࡵ࡮ࠡ࡮ࡲ࡫ࡸࠨቌ"))
                    time.sleep(300)
            else:
                self.logger.warning(bstack111l11_opy_ (u"ࠤࡩࡥ࡮ࡲࡵࡳࡧ࠰ࡲࡴ࠳ࡳࡤࡴ࡬ࡴࡹࡀࠠ࡭ࡱࡦࡥࡹࡵࡲࡠࡶࡼࡴࡪࡃࡻ࡭ࡱࡦࡥࡹࡵࡲࡠࡶࡼࡴࡪࢃࠠ࡭ࡱࡦࡥࡹࡵࡲࡠࡸࡤࡰࡺ࡫࠽ࡼ࡮ࡲࡧࡦࡺ࡯ࡳࡡࡹࡥࡱࡻࡥࡾࠢࡵࡩࡸࡶ࡯࡯ࡵࡨࡁࠧቍ") + str(response) + bstack111l11_opy_ (u"ࠥࠦ቎"))
        except Exception as err:
            self.logger.warning(bstack111l11_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡷࡵࡩ࠲࡮ࡥࡢ࡮࡬ࡲ࡬࠳ࡲࡦࡵࡸࡰࡹࡀࠠࡦࡴࡵࡳࡷࡀࠠࠣ቏") + str(err) + bstack111l11_opy_ (u"ࠧࠨቐ"))
        raise exception
    @measure(event_name=EVENTS.bstack1l1lllllll1_opy_, stage=STAGE.bstack111lllll1_opy_)
    def bstack1l1llllllll_opy_(
        self,
        framework_session_id: str,
        is_success: bool,
        locator_type: str,
        locator_value: str,
        platform_index=bstack111l11_opy_ (u"ࠨ࠰ࠣቑ"),
    ):
        self.bstack1ll11l11111_opy_()
        req = structs.AISelfHealStepRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_session_id = framework_session_id
        req.is_success = is_success
        req.test_name = bstack111l11_opy_ (u"ࠢࠣቒ")
        req.locator_type = locator_type
        req.locator_value = locator_value
        try:
            r = self.bstack1ll1ll1ll1l_opy_.AISelfHealStep(req)
            self.logger.info(bstack111l11_opy_ (u"ࠣࡴࡨࡧࡪ࡯ࡶࡦࡦࠣࡪࡷࡵ࡭ࠡࡵࡨࡶࡻ࡫ࡲ࠻ࠢࠥቓ") + str(r) + bstack111l11_opy_ (u"ࠤࠥቔ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack111l11_opy_ (u"ࠥࡶࡵࡩ࠭ࡦࡴࡵࡳࡷࡀࠠࠣቕ") + str(e) + bstack111l11_opy_ (u"ࠦࠧቖ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l1lllll11l_opy_, stage=STAGE.bstack111lllll1_opy_)
    def bstack1l1llllll11_opy_(self, framework_session_id: str, locator_type: str, platform_index=bstack111l11_opy_ (u"ࠧ࠶ࠢ቗")):
        self.bstack1ll11l11111_opy_()
        req = structs.AISelfHealGetRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_session_id = framework_session_id
        req.locator_type = locator_type
        try:
            r = self.bstack1ll1ll1ll1l_opy_.AISelfHealGetResult(req)
            self.logger.info(bstack111l11_opy_ (u"ࠨࡲࡦࡥࡨ࡭ࡻ࡫ࡤࠡࡨࡵࡳࡲࠦࡳࡦࡴࡹࡩࡷࡀࠠࠣቘ") + str(r) + bstack111l11_opy_ (u"ࠢࠣ቙"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack111l11_opy_ (u"ࠣࡴࡳࡧ࠲࡫ࡲࡳࡱࡵ࠾ࠥࠨቚ") + str(e) + bstack111l11_opy_ (u"ࠤࠥቛ"))
            traceback.print_exc()
            raise e