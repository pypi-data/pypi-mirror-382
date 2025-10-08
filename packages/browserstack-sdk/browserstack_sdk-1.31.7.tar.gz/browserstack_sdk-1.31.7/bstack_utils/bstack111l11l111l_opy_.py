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
import os
import time
from bstack_utils.bstack11ll1111l11_opy_ import bstack11ll1111l1l_opy_
from bstack_utils.constants import bstack11l1l1lllll_opy_
from bstack_utils.helper import get_host_info, bstack111ll1l1lll_opy_
class bstack111l11l1l11_opy_:
    bstack111l11_opy_ (u"ࠢࠣࠤࠍࠤࠥࠦࠠࡉࡣࡱࡨࡱ࡫ࡳࠡࡶࡨࡷࡹࠦ࡯ࡳࡦࡨࡶ࡮ࡴࡧࠡࡱࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮ࠡࡹ࡬ࡸ࡭ࠦࡴࡩࡧࠣࡆࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࠢࡶࡩࡷࡼࡥࡳ࠰ࠍࠤࠥࠦࠠࠣࠤࠥ⁮")
    def __init__(self, config, logger):
        bstack111l11_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤࠥࡀࡰࡢࡴࡤࡱࠥࡩ࡯࡯ࡨ࡬࡫࠿ࠦࡤࡪࡥࡷ࠰ࠥࡺࡥࡴࡶࠣࡳࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࠣࡧࡴࡴࡦࡪࡩࠍࠤࠥࠦࠠࠡࠢࠣࠤ࠿ࡶࡡࡳࡣࡰࠤࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࡣࡸࡺࡲࡢࡶࡨ࡫ࡾࡀࠠࡴࡶࡵ࠰ࠥࡺࡥࡴࡶࠣࡳࡷࡪࡥࡳ࡫ࡱ࡫ࠥࡹࡴࡳࡣࡷࡩ࡬ࡿࠠ࡯ࡣࡰࡩࠏࠦࠠࠡࠢࠣࠤࠥࠦࠢࠣࠤ⁯")
        self.config = config
        self.logger = logger
        self.bstack1llll1lll11l_opy_ = bstack111l11_opy_ (u"ࠤࡷࡩࡸࡺ࡯ࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳ࠵ࡡࡱ࡫࠲ࡺ࠶࠵ࡳࡱ࡮࡬ࡸ࠲ࡺࡥࡴࡶࡶࠦ⁰")
        self.bstack1llll1lllll1_opy_ = None
        self.bstack1llll1ll1l11_opy_ = 60
        self.bstack1llll1ll1lll_opy_ = 5
        self.bstack1lllll111111_opy_ = 0
    def bstack111l11l1ll1_opy_(self, test_files, orchestration_strategy, bstack111l11ll1l1_opy_={}):
        bstack111l11_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠࡊࡰ࡬ࡸ࡮ࡧࡴࡦࡵࠣࡸ࡭࡫ࠠࡴࡲ࡯࡭ࡹࠦࡴࡦࡵࡷࡷࠥࡸࡥࡲࡷࡨࡷࡹࠦࡡ࡯ࡦࠣࡷࡹࡵࡲࡦࡵࠣࡸ࡭࡫ࠠࡳࡧࡶࡴࡴࡴࡳࡦࠢࡧࡥࡹࡧࠠࡧࡱࡵࠤࡵࡵ࡬࡭࡫ࡱ࡫࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠣࠤࠥⁱ")
        self.logger.debug(bstack111l11_opy_ (u"ࠦࡠࡹࡰ࡭࡫ࡷࡘࡪࡹࡴࡴ࡟ࠣࡍࡳ࡯ࡴࡪࡣࡷ࡭ࡳ࡭ࠠࡴࡲ࡯࡭ࡹࠦࡴࡦࡵࡷࡷࠥࡽࡩࡵࡪࠣࡷࡹࡸࡡࡵࡧࡪࡽ࠿ࠦࡻࡾࠤ⁲").format(orchestration_strategy))
        try:
            bstack111l111l1ll_opy_ = []
            if bstack111l11ll1l1_opy_[bstack111l11_opy_ (u"ࠬࡸࡵ࡯ࡡࡶࡱࡦࡸࡴࡠࡵࡨࡰࡪࡩࡴࡪࡱࡱࠫ⁳")].get(bstack111l11_opy_ (u"࠭ࡥ࡯ࡣࡥࡰࡪࡪࠧ⁴"), False): # check if bstack1llll1llllll_opy_ bstack1lllll11111l_opy_ is enabled
                bstack1111l1lllll_opy_ = bstack111l11ll1l1_opy_[bstack111l11_opy_ (u"ࠧࡳࡷࡱࡣࡸࡳࡡࡳࡶࡢࡷࡪࡲࡥࡤࡶ࡬ࡳࡳ࠭⁵")].get(bstack111l11_opy_ (u"ࠨࡵࡲࡹࡷࡩࡥࠨ⁶"), []) # for multi-repo
                bstack111l111l1ll_opy_ = bstack111ll1l1lll_opy_(bstack1111l1lllll_opy_) # bstack11l1111lll1_opy_-repo is handled bstack111l1111111_opy_
            payload = {
                bstack111l11_opy_ (u"ࠤࡷࡩࡸࡺࡳࠣ⁷"): [{bstack111l11_opy_ (u"ࠥࡪ࡮ࡲࡥࡑࡣࡷ࡬ࠧ⁸"): f} for f in test_files],
                bstack111l11_opy_ (u"ࠦࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࡗࡹࡸࡡࡵࡧࡪࡽࠧ⁹"): orchestration_strategy,
                bstack111l11_opy_ (u"ࠧࡵࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲࡒ࡫ࡴࡢࡦࡤࡸࡦࠨ⁺"): bstack111l11ll1l1_opy_,
                bstack111l11_opy_ (u"ࠨ࡮ࡰࡦࡨࡍࡳࡪࡥࡹࠤ⁻"): int(os.environ.get(bstack111l11_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡎࡐࡆࡈࡣࡎࡔࡄࡆ࡚ࠥ⁼")) or bstack111l11_opy_ (u"ࠣ࠲ࠥ⁽")),
                bstack111l11_opy_ (u"ࠤࡷࡳࡹࡧ࡬ࡏࡱࡧࡩࡸࠨ⁾"): int(os.environ.get(bstack111l11_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡓ࡙ࡇࡌࡠࡐࡒࡈࡊࡥࡃࡐࡗࡑࡘࠧⁿ")) or bstack111l11_opy_ (u"ࠦ࠶ࠨ₀")),
                bstack111l11_opy_ (u"ࠧࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࠥ₁"): self.config.get(bstack111l11_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠫ₂"), bstack111l11_opy_ (u"ࠧࠨ₃")),
                bstack111l11_opy_ (u"ࠣࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠦ₄"): self.config.get(bstack111l11_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬ₅"), os.path.basename(os.path.abspath(os.getcwd()))),
                bstack111l11_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡔࡸࡲࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠣ₆"): self.config.get(bstack111l11_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭₇"), bstack111l11_opy_ (u"ࠬ࠭₈")),
                bstack111l11_opy_ (u"ࠨࡨࡰࡵࡷࡍࡳ࡬࡯ࠣ₉"): get_host_info(),
                bstack111l11_opy_ (u"ࠢࡱࡴࡇࡩࡹࡧࡩ࡭ࡵࠥ₊"): bstack111l111l1ll_opy_
            }
            self.logger.debug(bstack111l11_opy_ (u"ࠣ࡝ࡶࡴࡱ࡯ࡴࡕࡧࡶࡸࡸࡣࠠࡔࡧࡱࡨ࡮ࡴࡧࠡࡶࡨࡷࡹࠦࡦࡪ࡮ࡨࡷ࠿ࠦࡻࡾࠤ₋").format(payload))
            response = bstack11ll1111l1l_opy_.bstack1lllll1lllll_opy_(self.bstack1llll1lll11l_opy_, payload)
            if response:
                self.bstack1llll1lllll1_opy_ = self._1llll1ll1ll1_opy_(response)
                self.logger.debug(bstack111l11_opy_ (u"ࠤ࡞ࡷࡵࡲࡩࡵࡖࡨࡷࡹࡹ࡝ࠡࡕࡳࡰ࡮ࡺࠠࡵࡧࡶࡸࡸࠦࡲࡦࡵࡳࡳࡳࡹࡥ࠻ࠢࡾࢁࠧ₌").format(self.bstack1llll1lllll1_opy_))
            else:
                self.logger.error(bstack111l11_opy_ (u"ࠥ࡟ࡸࡶ࡬ࡪࡶࡗࡩࡸࡺࡳ࡞ࠢࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥ࡭ࡥࡵࠢࡶࡴࡱ࡯ࡴࠡࡶࡨࡷࡹࡹࠠࡳࡧࡶࡴࡴࡴࡳࡦ࠰ࠥ₍"))
        except Exception as e:
            self.logger.error(bstack111l11_opy_ (u"ࠦࡠࡹࡰ࡭࡫ࡷࡘࡪࡹࡴࡴ࡟ࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡶࡩࡳࡪࡩ࡯ࡩࠣࡸࡪࡹࡴࠡࡨ࡬ࡰࡪࡹ࠺࠻ࠢࡾࢁࠧ₎").format(e))
    def _1llll1ll1ll1_opy_(self, response):
        bstack111l11_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࠦࠠࠡࠢࡓࡶࡴࡩࡥࡴࡵࡨࡷࠥࡺࡨࡦࠢࡶࡴࡱ࡯ࡴࠡࡶࡨࡷࡹࡹࠠࡂࡒࡌࠤࡷ࡫ࡳࡱࡱࡱࡷࡪࠦࡡ࡯ࡦࠣࡩࡽࡺࡲࡢࡥࡷࡷࠥࡸࡥ࡭ࡧࡹࡥࡳࡺࠠࡧ࡫ࡨࡰࡩࡹ࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠥࠦࠧ₏")
        bstack11ll1ll11_opy_ = {}
        bstack11ll1ll11_opy_[bstack111l11_opy_ (u"ࠨࡴࡪ࡯ࡨࡳࡺࡺࠢₐ")] = response.get(bstack111l11_opy_ (u"ࠢࡵ࡫ࡰࡩࡴࡻࡴࠣₑ"), self.bstack1llll1ll1l11_opy_)
        bstack11ll1ll11_opy_[bstack111l11_opy_ (u"ࠣࡶ࡬ࡱࡪࡵࡵࡵࡋࡱࡸࡪࡸࡶࡢ࡮ࠥₒ")] = response.get(bstack111l11_opy_ (u"ࠤࡷ࡭ࡲ࡫࡯ࡶࡶࡌࡲࡹ࡫ࡲࡷࡣ࡯ࠦₓ"), self.bstack1llll1ll1lll_opy_)
        bstack1llll1llll1l_opy_ = response.get(bstack111l11_opy_ (u"ࠥࡶࡪࡹࡵ࡭ࡶࡘࡶࡱࠨₔ"))
        bstack1llll1lll111_opy_ = response.get(bstack111l11_opy_ (u"ࠦࡹ࡯࡭ࡦࡱࡸࡸ࡚ࡸ࡬ࠣₕ"))
        if bstack1llll1llll1l_opy_:
            bstack11ll1ll11_opy_[bstack111l11_opy_ (u"ࠧࡸࡥࡴࡷ࡯ࡸ࡚ࡸ࡬ࠣₖ")] = bstack1llll1llll1l_opy_.split(bstack11l1l1lllll_opy_ + bstack111l11_opy_ (u"ࠨ࠯ࠣₗ"))[1] if bstack11l1l1lllll_opy_ + bstack111l11_opy_ (u"ࠢ࠰ࠤₘ") in bstack1llll1llll1l_opy_ else bstack1llll1llll1l_opy_
        else:
            bstack11ll1ll11_opy_[bstack111l11_opy_ (u"ࠣࡴࡨࡷࡺࡲࡴࡖࡴ࡯ࠦₙ")] = None
        if bstack1llll1lll111_opy_:
            bstack11ll1ll11_opy_[bstack111l11_opy_ (u"ࠤࡷ࡭ࡲ࡫࡯ࡶࡶࡘࡶࡱࠨₚ")] = bstack1llll1lll111_opy_.split(bstack11l1l1lllll_opy_ + bstack111l11_opy_ (u"ࠥ࠳ࠧₛ"))[1] if bstack11l1l1lllll_opy_ + bstack111l11_opy_ (u"ࠦ࠴ࠨₜ") in bstack1llll1lll111_opy_ else bstack1llll1lll111_opy_
        else:
            bstack11ll1ll11_opy_[bstack111l11_opy_ (u"ࠧࡺࡩ࡮ࡧࡲࡹࡹ࡛ࡲ࡭ࠤ₝")] = None
        if (
            response.get(bstack111l11_opy_ (u"ࠨࡴࡪ࡯ࡨࡳࡺࡺࠢ₞")) is None or
            response.get(bstack111l11_opy_ (u"ࠢࡵ࡫ࡰࡩࡴࡻࡴࡊࡰࡷࡩࡷࡼࡡ࡭ࠤ₟")) is None or
            response.get(bstack111l11_opy_ (u"ࠣࡶ࡬ࡱࡪࡵࡵࡵࡗࡵࡰࠧ₠")) is None or
            response.get(bstack111l11_opy_ (u"ࠤࡵࡩࡸࡻ࡬ࡵࡗࡵࡰࠧ₡")) is None
        ):
            self.logger.debug(bstack111l11_opy_ (u"ࠥ࡟ࡵࡸ࡯ࡤࡧࡶࡷࡤࡹࡰ࡭࡫ࡷࡣࡹ࡫ࡳࡵࡵࡢࡶࡪࡹࡰࡰࡰࡶࡩࡢࠦࡒࡦࡥࡨ࡭ࡻ࡫ࡤࠡࡰࡸࡰࡱࠦࡶࡢ࡮ࡸࡩ࠭ࡹࠩࠡࡨࡲࡶࠥࡹ࡯࡮ࡧࠣࡥࡹࡺࡲࡪࡤࡸࡸࡪࡹࠠࡪࡰࠣࡷࡵࡲࡩࡵࠢࡷࡩࡸࡺࡳࠡࡃࡓࡍࠥࡸࡥࡴࡲࡲࡲࡸ࡫ࠢ₢"))
        return bstack11ll1ll11_opy_
    def bstack111l11l11l1_opy_(self):
        if not self.bstack1llll1lllll1_opy_:
            self.logger.error(bstack111l11_opy_ (u"ࠦࡠ࡭ࡥࡵࡑࡵࡨࡪࡸࡥࡥࡖࡨࡷࡹࡌࡩ࡭ࡧࡶࡡࠥࡔ࡯ࠡࡴࡨࡵࡺ࡫ࡳࡵࠢࡧࡥࡹࡧࠠࡢࡸࡤ࡭ࡱࡧࡢ࡭ࡧࠣࡸࡴࠦࡦࡦࡶࡦ࡬ࠥࡵࡲࡥࡧࡵࡩࡩࠦࡴࡦࡵࡷࠤ࡫࡯࡬ࡦࡵ࠱ࠦ₣"))
            return None
        bstack1llll1ll1l1l_opy_ = None
        test_files = []
        bstack1lllll1111l1_opy_ = int(time.time() * 1000) # bstack1llll1llll11_opy_ sec
        bstack1llll1lll1l1_opy_ = int(self.bstack1llll1lllll1_opy_.get(bstack111l11_opy_ (u"ࠧࡺࡩ࡮ࡧࡲࡹࡹࡏ࡮ࡵࡧࡵࡺࡦࡲࠢ₤"), self.bstack1llll1ll1lll_opy_))
        bstack1llll1lll1ll_opy_ = int(self.bstack1llll1lllll1_opy_.get(bstack111l11_opy_ (u"ࠨࡴࡪ࡯ࡨࡳࡺࡺࠢ₥"), self.bstack1llll1ll1l11_opy_)) * 1000
        bstack1llll1lll111_opy_ = self.bstack1llll1lllll1_opy_.get(bstack111l11_opy_ (u"ࠢࡵ࡫ࡰࡩࡴࡻࡴࡖࡴ࡯ࠦ₦"), None)
        bstack1llll1llll1l_opy_ = self.bstack1llll1lllll1_opy_.get(bstack111l11_opy_ (u"ࠣࡴࡨࡷࡺࡲࡴࡖࡴ࡯ࠦ₧"), None)
        if bstack1llll1llll1l_opy_ is None and bstack1llll1lll111_opy_ is None:
            return None
        try:
            while bstack1llll1llll1l_opy_ and (time.time() * 1000 - bstack1lllll1111l1_opy_) < bstack1llll1lll1ll_opy_:
                response = bstack11ll1111l1l_opy_.bstack1llllll11l11_opy_(bstack1llll1llll1l_opy_, {})
                if response and response.get(bstack111l11_opy_ (u"ࠤࡷࡩࡸࡺࡳࠣ₨")):
                    bstack1llll1ll1l1l_opy_ = response.get(bstack111l11_opy_ (u"ࠥࡸࡪࡹࡴࡴࠤ₩"))
                self.bstack1lllll111111_opy_ += 1
                if bstack1llll1ll1l1l_opy_:
                    break
                time.sleep(bstack1llll1lll1l1_opy_)
                self.logger.debug(bstack111l11_opy_ (u"ࠦࡠ࡭ࡥࡵࡑࡵࡨࡪࡸࡥࡥࡖࡨࡷࡹࡌࡩ࡭ࡧࡶࡡࠥࡌࡥࡵࡥ࡫࡭ࡳ࡭ࠠࡰࡴࡧࡩࡷ࡫ࡤࠡࡶࡨࡷࡹࡹࠠࡧࡴࡲࡱࠥࡸࡥࡴࡷ࡯ࡸ࡛ࠥࡒࡍࠢࡤࡪࡹ࡫ࡲࠡࡹࡤ࡭ࡹ࡯࡮ࡨࠢࡩࡳࡷࠦࡻࡾࠢࡶࡩࡨࡵ࡮ࡥࡵ࠱ࠦ₪").format(bstack1llll1lll1l1_opy_))
            if bstack1llll1lll111_opy_ and not bstack1llll1ll1l1l_opy_:
                self.logger.debug(bstack111l11_opy_ (u"ࠧࡡࡧࡦࡶࡒࡶࡩ࡫ࡲࡦࡦࡗࡩࡸࡺࡆࡪ࡮ࡨࡷࡢࠦࡆࡦࡶࡦ࡬࡮ࡴࡧࠡࡱࡵࡨࡪࡸࡥࡥࠢࡷࡩࡸࡺࡳࠡࡨࡵࡳࡲࠦࡴࡪ࡯ࡨࡳࡺࡺࠠࡖࡔࡏࠦ₫"))
                response = bstack11ll1111l1l_opy_.bstack1llllll11l11_opy_(bstack1llll1lll111_opy_, {})
                if response and response.get(bstack111l11_opy_ (u"ࠨࡴࡦࡵࡷࡷࠧ€")):
                    bstack1llll1ll1l1l_opy_ = response.get(bstack111l11_opy_ (u"ࠢࡵࡧࡶࡸࡸࠨ₭"))
            if bstack1llll1ll1l1l_opy_ and len(bstack1llll1ll1l1l_opy_) > 0:
                for bstack111l1llll1_opy_ in bstack1llll1ll1l1l_opy_:
                    file_path = bstack111l1llll1_opy_.get(bstack111l11_opy_ (u"ࠣࡨ࡬ࡰࡪࡖࡡࡵࡪࠥ₮"))
                    if file_path:
                        test_files.append(file_path)
            if not bstack1llll1ll1l1l_opy_:
                return None
            self.logger.debug(bstack111l11_opy_ (u"ࠤ࡞࡫ࡪࡺࡏࡳࡦࡨࡶࡪࡪࡔࡦࡵࡷࡊ࡮ࡲࡥࡴ࡟ࠣࡓࡷࡪࡥࡳࡧࡧࠤࡹ࡫ࡳࡵࠢࡩ࡭ࡱ࡫ࡳࠡࡴࡨࡧࡪ࡯ࡶࡦࡦ࠽ࠤࢀࢃࠢ₯").format(test_files))
            return test_files
        except Exception as e:
            self.logger.error(bstack111l11_opy_ (u"ࠥ࡟࡬࡫ࡴࡐࡴࡧࡩࡷ࡫ࡤࡕࡧࡶࡸࡋ࡯࡬ࡦࡵࡠࠤࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡪࡪࡺࡣࡩ࡫ࡱ࡫ࠥࡵࡲࡥࡧࡵࡩࡩࠦࡴࡦࡵࡷࠤ࡫࡯࡬ࡦࡵ࠽ࠤࢀࢃࠢ₰").format(e))
            return None
    def bstack111l11l11ll_opy_(self):
        bstack111l11_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࡔࡨࡸࡺࡸ࡮ࡴࠢࡷ࡬ࡪࠦࡣࡰࡷࡱࡸࠥࡵࡦࠡࡵࡳࡰ࡮ࡺࠠࡵࡧࡶࡸࡸࠦࡁࡑࡋࠣࡧࡦࡲ࡬ࡴࠢࡰࡥࡩ࡫࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠥࠦࠧ₱")
        return self.bstack1lllll111111_opy_