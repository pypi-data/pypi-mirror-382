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
from time import sleep
from datetime import datetime
from urllib.parse import urlencode
from bstack_utils.bstack11ll1111l11_opy_ import bstack11ll1111l1l_opy_
from bstack_utils.constants import *
import json
class bstack1l1ll111l1_opy_:
    def __init__(self, bstack1l1lllll1_opy_, bstack11ll111l111_opy_):
        self.bstack1l1lllll1_opy_ = bstack1l1lllll1_opy_
        self.bstack11ll111l111_opy_ = bstack11ll111l111_opy_
        self.bstack11ll1111lll_opy_ = None
    def __call__(self):
        bstack11ll111l11l_opy_ = {}
        while True:
            self.bstack11ll1111lll_opy_ = bstack11ll111l11l_opy_.get(
                bstack111l11_opy_ (u"ࠨࡰࡨࡼࡹࡥࡰࡰ࡮࡯ࡣࡹ࡯࡭ࡦࠩច"),
                int(datetime.now().timestamp() * 1000)
            )
            bstack11ll111ll11_opy_ = self.bstack11ll1111lll_opy_ - int(datetime.now().timestamp() * 1000)
            if bstack11ll111ll11_opy_ > 0:
                sleep(bstack11ll111ll11_opy_ / 1000)
            params = {
                bstack111l11_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩឆ"): self.bstack1l1lllll1_opy_,
                bstack111l11_opy_ (u"ࠪࡸ࡮ࡳࡥࡴࡶࡤࡱࡵ࠭ជ"): int(datetime.now().timestamp() * 1000)
            }
            bstack11ll1111ll1_opy_ = bstack111l11_opy_ (u"ࠦ࡭ࡺࡴࡱࡵ࠽࠳࠴ࠨឈ") + bstack11ll111l1l1_opy_ + bstack111l11_opy_ (u"ࠧ࠵ࡡࡶࡶࡲࡱࡦࡺࡥ࠰ࡣࡳ࡭࠴ࡼ࠱࠰ࠤញ")
            if self.bstack11ll111l111_opy_.lower() == bstack111l11_opy_ (u"ࠨࡲࡦࡵࡸࡰࡹࡹࠢដ"):
                bstack11ll111l11l_opy_ = bstack11ll1111l1l_opy_.results(bstack11ll1111ll1_opy_, params)
            else:
                bstack11ll111l11l_opy_ = bstack11ll1111l1l_opy_.bstack11ll111l1ll_opy_(bstack11ll1111ll1_opy_, params)
            if str(bstack11ll111l11l_opy_.get(bstack111l11_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧឋ"), bstack111l11_opy_ (u"ࠨ࠴࠳࠴ࠬឌ"))) != bstack111l11_opy_ (u"ࠩ࠷࠴࠹࠭ឍ"):
                break
        return bstack11ll111l11l_opy_.get(bstack111l11_opy_ (u"ࠪࡨࡦࡺࡡࠨណ"), bstack11ll111l11l_opy_)