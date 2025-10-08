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
import json
import os
import grpc
import copy
import asyncio
import threading
from browserstack_sdk import sdk_pb2 as structs
from packaging import version
import traceback
from browserstack_sdk.sdk_cli.bstack1lll111ll1l_opy_ import bstack1ll1ll1lll1_opy_
from browserstack_sdk.sdk_cli.bstack1lllll11l1l_opy_ import (
    bstack1llllll111l_opy_,
    bstack1llll1l111l_opy_,
    bstack1lllll1ll1l_opy_,
)
from bstack_utils.constants import *
from typing import Any, List, Union, Dict
from pathlib import Path
from browserstack_sdk.sdk_cli.bstack1ll1ll11l11_opy_ import bstack1ll1ll11111_opy_
from datetime import datetime
from typing import Tuple, Any
from bstack_utils.messages import bstack1l1111111_opy_
from bstack_utils.helper import bstack1l1l1ll11ll_opy_
import threading
import os
import urllib.parse
class bstack1lll1l1l1ll_opy_(bstack1ll1ll1lll1_opy_):
    def __init__(self, bstack1llll11l1l1_opy_):
        super().__init__()
        bstack1ll1ll11111_opy_.bstack1ll11llll1l_opy_((bstack1llllll111l_opy_.bstack1llll1ll1l1_opy_, bstack1llll1l111l_opy_.PRE), self.bstack1l1l11l111l_opy_)
        bstack1ll1ll11111_opy_.bstack1ll11llll1l_opy_((bstack1llllll111l_opy_.bstack1llll1ll1l1_opy_, bstack1llll1l111l_opy_.PRE), self.bstack1l1l111l11l_opy_)
        bstack1ll1ll11111_opy_.bstack1ll11llll1l_opy_((bstack1llllll111l_opy_.bstack1lllll1l1ll_opy_, bstack1llll1l111l_opy_.PRE), self.bstack1l1l111ll11_opy_)
        bstack1ll1ll11111_opy_.bstack1ll11llll1l_opy_((bstack1llllll111l_opy_.bstack1llll1llll1_opy_, bstack1llll1l111l_opy_.PRE), self.bstack1l1l11l1l1l_opy_)
        bstack1ll1ll11111_opy_.bstack1ll11llll1l_opy_((bstack1llllll111l_opy_.bstack1llll1ll1l1_opy_, bstack1llll1l111l_opy_.PRE), self.bstack1l1l11l1111_opy_)
        bstack1ll1ll11111_opy_.bstack1ll11llll1l_opy_((bstack1llllll111l_opy_.QUIT, bstack1llll1l111l_opy_.PRE), self.on_close)
        self.bstack1llll11l1l1_opy_ = bstack1llll11l1l1_opy_
    def is_enabled(self) -> bool:
        return True
    def bstack1l1l11l111l_opy_(
        self,
        f: bstack1ll1ll11111_opy_,
        bstack1l1l1111l1l_opy_: object,
        exec: Tuple[bstack1lllll1ll1l_opy_, str],
        bstack1llllll1l1l_opy_: Tuple[bstack1llllll111l_opy_, bstack1llll1l111l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack111l11_opy_ (u"ࠧࡲࡡࡶࡰࡦ࡬ࠧጆ"):
            return
        if not bstack1l1l1ll11ll_opy_():
            self.logger.debug(bstack111l11_opy_ (u"ࠨࡒࡦࡶࡸࡶࡳ࡯࡮ࡨࠢ࡬ࡲࠥࡲࡡࡶࡰࡦ࡬ࠥࡳࡥࡵࡪࡲࡨ࠱ࠦ࡮ࡰࡶࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡶࡩࡸࡹࡩࡰࡰࠥጇ"))
            return
        def wrapped(bstack1l1l1111l1l_opy_, launch, *args, **kwargs):
            response = self.bstack1l1l111llll_opy_(f.platform_index, instance.ref(), json.dumps({bstack111l11_opy_ (u"ࠧࡪࡵࡓࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹ࠭ገ"): True}).encode(bstack111l11_opy_ (u"ࠣࡷࡷࡪ࠲࠾ࠢጉ")))
            if response is not None and response.capabilities:
                if not bstack1l1l1ll11ll_opy_():
                    browser = launch(bstack1l1l1111l1l_opy_)
                    return browser
                bstack1l1l11l1l11_opy_ = json.loads(response.capabilities.decode(bstack111l11_opy_ (u"ࠤࡸࡸ࡫࠳࠸ࠣጊ")))
                if not bstack1l1l11l1l11_opy_: # empty caps bstack1l1l111l111_opy_ bstack1l1l111l1l1_opy_ bstack1l1l111lll1_opy_ bstack1lll1l1ll11_opy_ or error in processing
                    return
                bstack1l1l11l11l1_opy_ = PLAYWRIGHT_HUB_URL + urllib.parse.quote(json.dumps(bstack1l1l11l1l11_opy_))
                f.bstack1llll1l11l1_opy_(instance, bstack1ll1ll11111_opy_.bstack1l1l11l11ll_opy_, bstack1l1l11l11l1_opy_)
                f.bstack1llll1l11l1_opy_(instance, bstack1ll1ll11111_opy_.bstack1l1l111l1ll_opy_, bstack1l1l11l1l11_opy_)
                browser = bstack1l1l1111l1l_opy_.connect(bstack1l1l11l11l1_opy_)
                return browser
        return wrapped
    def bstack1l1l111ll11_opy_(
        self,
        f: bstack1ll1ll11111_opy_,
        Connection: object,
        exec: Tuple[bstack1lllll1ll1l_opy_, str],
        bstack1llllll1l1l_opy_: Tuple[bstack1llllll111l_opy_, bstack1llll1l111l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack111l11_opy_ (u"ࠥࡨ࡮ࡹࡰࡢࡶࡦ࡬ࠧጋ"):
            self.logger.debug(bstack111l11_opy_ (u"ࠦࡗ࡫ࡴࡶࡴࡱ࡭ࡳ࡭ࠠࡪࡰࠣࡨ࡮ࡹࡰࡢࡶࡦ࡬ࠥࡳࡥࡵࡪࡲࡨ࠱ࠦ࡮ࡰࡶࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡶࡩࡸࡹࡩࡰࡰࠥጌ"))
            return
        if not bstack1l1l1ll11ll_opy_():
            return
        def wrapped(Connection, dispatch, *args, **kwargs):
            data = args[0]
            try:
                if args and args[0].get(bstack111l11_opy_ (u"ࠬࡶࡡࡳࡣࡰࡷࠬግ"), {}).get(bstack111l11_opy_ (u"࠭ࡢࡴࡒࡤࡶࡦࡳࡳࠨጎ")):
                    bstack1l1l11l1ll1_opy_ = args[0][bstack111l11_opy_ (u"ࠢࡱࡣࡵࡥࡲࡹࠢጏ")][bstack111l11_opy_ (u"ࠣࡤࡶࡔࡦࡸࡡ࡮ࡵࠥጐ")]
                    session_id = bstack1l1l11l1ll1_opy_.get(bstack111l11_opy_ (u"ࠤࡶࡩࡸࡹࡩࡰࡰࡌࡨࠧ጑"))
                    f.bstack1llll1l11l1_opy_(instance, bstack1ll1ll11111_opy_.bstack1l1l1111l11_opy_, session_id)
            except Exception as e:
                self.logger.debug(bstack111l11_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡧ࡭ࡸࡶࡡࡵࡥ࡫ࠤࡲ࡫ࡴࡩࡱࡧ࠾ࠥࠨጒ"), e)
            dispatch(Connection, *args)
        return wrapped
    def bstack1l1l11l1111_opy_(
        self,
        f: bstack1ll1ll11111_opy_,
        bstack1l1l1111l1l_opy_: object,
        exec: Tuple[bstack1lllll1ll1l_opy_, str],
        bstack1llllll1l1l_opy_: Tuple[bstack1llllll111l_opy_, bstack1llll1l111l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack111l11_opy_ (u"ࠦࡨࡵ࡮࡯ࡧࡦࡸࠧጓ"):
            return
        if not bstack1l1l1ll11ll_opy_():
            self.logger.debug(bstack111l11_opy_ (u"ࠧࡘࡥࡵࡷࡵࡲ࡮ࡴࡧࠡ࡫ࡱࠤࡨࡵ࡮࡯ࡧࡦࡸࠥࡳࡥࡵࡪࡲࡨ࠱ࠦ࡮ࡰࡶࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡶࡩࡸࡹࡩࡰࡰࠥጔ"))
            return
        def wrapped(bstack1l1l1111l1l_opy_, connect, *args, **kwargs):
            response = self.bstack1l1l111llll_opy_(f.platform_index, instance.ref(), json.dumps({bstack111l11_opy_ (u"࠭ࡩࡴࡒ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࠬጕ"): True}).encode(bstack111l11_opy_ (u"ࠢࡶࡶࡩ࠱࠽ࠨ጖")))
            if response is not None and response.capabilities:
                bstack1l1l11l1l11_opy_ = json.loads(response.capabilities.decode(bstack111l11_opy_ (u"ࠣࡷࡷࡪ࠲࠾ࠢ጗")))
                if not bstack1l1l11l1l11_opy_:
                    return
                bstack1l1l11l11l1_opy_ = PLAYWRIGHT_HUB_URL + urllib.parse.quote(json.dumps(bstack1l1l11l1l11_opy_))
                if bstack1l1l11l1l11_opy_.get(bstack111l11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨጘ")):
                    browser = bstack1l1l1111l1l_opy_.bstack1l1l1111ll1_opy_(bstack1l1l11l11l1_opy_)
                    return browser
                else:
                    args = list(args)
                    args[0] = bstack1l1l11l11l1_opy_
                    return connect(bstack1l1l1111l1l_opy_, *args, **kwargs)
        return wrapped
    def bstack1l1l111l11l_opy_(
        self,
        f: bstack1ll1ll11111_opy_,
        bstack1l1llll11ll_opy_: object,
        exec: Tuple[bstack1lllll1ll1l_opy_, str],
        bstack1llllll1l1l_opy_: Tuple[bstack1llllll111l_opy_, bstack1llll1l111l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack111l11_opy_ (u"ࠥࡲࡪࡽ࡟ࡱࡣࡪࡩࠧጙ"):
            return
        if not bstack1l1l1ll11ll_opy_():
            self.logger.debug(bstack111l11_opy_ (u"ࠦࡗ࡫ࡴࡶࡴࡱ࡭ࡳ࡭ࠠࡪࡰࠣࡲࡪࡽ࡟ࡱࡣࡪࡩࠥࡳࡥࡵࡪࡲࡨ࠱ࠦ࡮ࡰࡶࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡶࡩࡸࡹࡩࡰࡰࠥጚ"))
            return
        def wrapped(bstack1l1llll11ll_opy_, bstack1l1l1111lll_opy_, *args, **kwargs):
            contexts = bstack1l1llll11ll_opy_.browser.contexts
            if contexts:
                for context in contexts:
                    if context.pages:
                        for page in context.pages:
                                if bstack111l11_opy_ (u"ࠧࡧࡢࡰࡷࡷ࠾ࡧࡲࡡ࡯࡭ࠥጛ") in page.url:
                                    return page
                    else:
                        return bstack1l1l1111lll_opy_(bstack1l1llll11ll_opy_)
        return wrapped
    def bstack1l1l111llll_opy_(self, platform_index: int, ref, user_input_params: bytes):
        req = structs.DriverInitRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.user_input_params = user_input_params
        req.ref = ref
        self.logger.debug(bstack111l11_opy_ (u"ࠨࡲࡦࡩ࡬ࡷࡹ࡫ࡲࡠࡹࡨࡦࡩࡸࡩࡷࡧࡵࡣ࡮ࡴࡩࡵ࠼ࠣࠦጜ") + str(req) + bstack111l11_opy_ (u"ࠢࠣጝ"))
        try:
            r = self.bstack1ll1ll1ll1l_opy_.DriverInit(req)
            if not r.success:
                self.logger.debug(bstack111l11_opy_ (u"ࠣࡴࡨࡧࡪ࡯ࡶࡦࡦࠣࡪࡷࡵ࡭ࠡࡵࡨࡶࡻ࡫ࡲ࠻ࠢࡶࡹࡨࡩࡥࡴࡵࡀࠦጞ") + str(r.success) + bstack111l11_opy_ (u"ࠤࠥጟ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack111l11_opy_ (u"ࠥࡶࡵࡩ࠭ࡦࡴࡵࡳࡷࡀࠠࠣጠ") + str(e) + bstack111l11_opy_ (u"ࠦࠧጡ"))
            traceback.print_exc()
            raise e
    def bstack1l1l11l1l1l_opy_(
        self,
        f: bstack1ll1ll11111_opy_,
        Connection: object,
        exec: Tuple[bstack1lllll1ll1l_opy_, str],
        bstack1llllll1l1l_opy_: Tuple[bstack1llllll111l_opy_, bstack1llll1l111l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack111l11_opy_ (u"ࠧࡥࡳࡦࡰࡧࡣࡲ࡫ࡳࡴࡣࡪࡩࡤࡺ࡯ࡠࡵࡨࡶࡻ࡫ࡲࠣጢ"):
            return
        if not bstack1l1l1ll11ll_opy_():
            return
        def wrapped(Connection, bstack1l1l111ll1l_opy_, *args, **kwargs):
            return bstack1l1l111ll1l_opy_(Connection, *args, **kwargs)
        return wrapped
    def on_close(
        self,
        f: bstack1ll1ll11111_opy_,
        bstack1l1l1111l1l_opy_: object,
        exec: Tuple[bstack1lllll1ll1l_opy_, str],
        bstack1llllll1l1l_opy_: Tuple[bstack1llllll111l_opy_, bstack1llll1l111l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack111l11_opy_ (u"ࠨࡣ࡭ࡱࡶࡩࠧጣ"):
            return
        if not bstack1l1l1ll11ll_opy_():
            self.logger.debug(bstack111l11_opy_ (u"ࠢࡓࡧࡷࡹࡷࡴࡩ࡯ࡩࠣ࡭ࡳࠦࡣ࡭ࡱࡶࡩࠥࡳࡥࡵࡪࡲࡨ࠱ࠦ࡮ࡰࡶࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡶࡩࡸࡹࡩࡰࡰࠥጤ"))
            return
        def wrapped(Connection, close, *args, **kwargs):
            return close(Connection)
        return wrapped