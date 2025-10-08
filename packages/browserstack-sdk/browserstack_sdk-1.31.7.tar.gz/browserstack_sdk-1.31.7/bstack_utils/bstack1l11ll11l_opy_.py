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
from bstack_utils.constants import *
from browserstack_sdk.sdk_cli.cli import cli
from bstack_utils.bstack111l11l111l_opy_ import bstack111l11l1l11_opy_
from bstack_utils.bstack1l11ll11_opy_ import bstack11111l1ll_opy_
from bstack_utils.helper import bstack11ll1l11_opy_
class bstack11l1l1l11l_opy_:
    _1ll1l11lll1_opy_ = None
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.bstack111l11l1lll_opy_ = bstack111l11l1l11_opy_(self.config, logger)
        self.bstack1l11ll11_opy_ = bstack11111l1ll_opy_.bstack1lll111l11_opy_(config=self.config)
        self.bstack111l111ll11_opy_ = {}
        self.bstack1111l11lll_opy_ = False
        self.bstack111l111llll_opy_ = (
            self.__111l111lll1_opy_()
            and self.bstack1l11ll11_opy_ is not None
            and self.bstack1l11ll11_opy_.bstack1ll11111ll_opy_()
            and config.get(bstack111l11_opy_ (u"ࠩࡳࡶࡴࡰࡥࡤࡶࡑࡥࡲ࡫ࠧṇ"), None) is not None
            and config.get(bstack111l11_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭Ṉ"), os.path.basename(os.getcwd())) is not None
        )
    @classmethod
    def bstack1lll111l11_opy_(cls, config, logger):
        if cls._1ll1l11lll1_opy_ is None and config is not None:
            cls._1ll1l11lll1_opy_ = bstack11l1l1l11l_opy_(config, logger)
        return cls._1ll1l11lll1_opy_
    def bstack1ll11111ll_opy_(self):
        bstack111l11_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࡆࡲࠤࡳࡵࡴࠡࡣࡳࡴࡱࡿࠠࡵࡧࡶࡸࠥࡵࡲࡥࡧࡵ࡭ࡳ࡭ࠠࡸࡪࡨࡲ࠿ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢ࠰ࠤࡔ࠷࠱ࡺࠢ࡬ࡷࠥࡴ࡯ࡵࠢࡨࡲࡦࡨ࡬ࡦࡦࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࠭ࠡࡑࡵࡨࡪࡸࡩ࡯ࡩࠣ࡭ࡸࠦ࡮ࡰࡶࠣࡩࡳࡧࡢ࡭ࡧࡧࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠ࠮ࠢࡳࡶࡴࡰࡥࡤࡶࡑࡥࡲ࡫ࠠࡪࡵࠣࡒࡴࡴࡥࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࠲ࠦࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠢ࡬ࡷࠥࡔ࡯࡯ࡧࠍࠤࠥࠦࠠࠡࠢࠣࠤࠧࠨࠢṉ")
        return self.bstack111l111llll_opy_ and self.bstack111l11l1l1l_opy_()
    def bstack111l11l1l1l_opy_(self):
        return self.config.get(bstack111l11_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨṊ"), None) in bstack11l1ll11l1l_opy_
    def __111l111lll1_opy_(self):
        bstack11l1lllll11_opy_ = False
        for fw in bstack11l1ll1l11l_opy_:
            if fw in self.config.get(bstack111l11_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩṋ"), bstack111l11_opy_ (u"ࠧࠨṌ")):
                bstack11l1lllll11_opy_ = True
        return bstack11ll1l11_opy_(self.config.get(bstack111l11_opy_ (u"ࠨࡶࡨࡷࡹࡕࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠬṍ"), bstack11l1lllll11_opy_))
    def bstack111l11l1111_opy_(self):
        return (not self.bstack1ll11111ll_opy_() and
                self.bstack1l11ll11_opy_ is not None and self.bstack1l11ll11_opy_.bstack1ll11111ll_opy_())
    def bstack111l11ll111_opy_(self):
        if not self.bstack111l11l1111_opy_():
            return
        if self.config.get(bstack111l11_opy_ (u"ࠩࡳࡶࡴࡰࡥࡤࡶࡑࡥࡲ࡫ࠧṎ"), None) is None or self.config.get(bstack111l11_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭ṏ"), os.path.basename(os.getcwd())) is None:
            self.logger.info(bstack111l11_opy_ (u"࡙ࠦ࡫ࡳࡵࠢࡕࡩࡴࡸࡤࡦࡴ࡬ࡲ࡬ࠦࡣࡢࡰࠪࡸࠥࡽ࡯ࡳ࡭ࠣࡥࡸࠦࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠢࡲࡶࠥࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࠣ࡭ࡸࠦ࡮ࡶ࡮࡯࠲ࠥࡖ࡬ࡦࡣࡶࡩࠥࡹࡥࡵࠢࡤࠤࡳࡵ࡮࠮ࡰࡸࡰࡱࠦࡶࡢ࡮ࡸࡩ࠳ࠨṐ"))
        if not self.__111l111lll1_opy_():
            self.logger.info(bstack111l11_opy_ (u"࡚ࠧࡥࡴࡶࠣࡖࡪࡵࡲࡥࡧࡵ࡭ࡳ࡭ࠠࡤࡣࡱࠫࡹࠦࡷࡰࡴ࡮ࠤࡦࡹࠠࡵࡧࡶࡸࡗ࡫ࡰࡰࡴࡷ࡭ࡳ࡭ࠠࡪࡵࠣࡨ࡮ࡹࡡࡣ࡮ࡨࡨ࠳ࠦࡐ࡭ࡧࡤࡷࡪࠦࡥ࡯ࡣࡥࡰࡪࠦࡩࡵࠢࡩࡶࡴࡳࠠࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡹ࡮࡮ࠣࡪ࡮ࡲࡥ࠯ࠤṑ"))
    def bstack111l111ll1l_opy_(self):
        return self.bstack1111l11lll_opy_
    def bstack11111ll1ll_opy_(self, bstack111l11ll11l_opy_):
        self.bstack1111l11lll_opy_ = bstack111l11ll11l_opy_
        self.bstack1111l111ll_opy_(bstack111l11_opy_ (u"ࠨࡡࡱࡲ࡯࡭ࡪࡪࠢṒ"), bstack111l11ll11l_opy_)
    def bstack11111lll11_opy_(self, test_files):
        try:
            if test_files is None:
                self.logger.debug(bstack111l11_opy_ (u"ࠢ࡜ࡴࡨࡳࡷࡪࡥࡳࡡࡷࡩࡸࡺ࡟ࡧ࡫࡯ࡩࡸࡣࠠࡏࡱࠣࡸࡪࡹࡴࠡࡨ࡬ࡰࡪࡹࠠࡱࡴࡲࡺ࡮ࡪࡥࡥࠢࡩࡳࡷࠦ࡯ࡳࡦࡨࡶ࡮ࡴࡧ࠯ࠤṓ"))
                return None
            orchestration_strategy = None
            bstack111l11ll1l1_opy_ = self.bstack1l11ll11_opy_.bstack111l11ll1ll_opy_()
            if self.bstack1l11ll11_opy_ is not None:
                orchestration_strategy = self.bstack1l11ll11_opy_.bstack11ll1l11ll_opy_()
            if orchestration_strategy is None:
                self.logger.error(bstack111l11_opy_ (u"ࠣࡑࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮ࠡࡵࡷࡶࡦࡺࡥࡨࡻࠣ࡭ࡸࠦࡎࡰࡰࡨ࠲ࠥࡉࡡ࡯ࡰࡲࡸࠥࡶࡲࡰࡥࡨࡩࡩࠦࡷࡪࡶ࡫ࠤࡹ࡫ࡳࡵࠢࡲࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯ࠢࡶࡩࡸࡹࡩࡰࡰ࠱ࠦṔ"))
                return None
            self.logger.info(bstack111l11_opy_ (u"ࠤࡕࡩࡴࡸࡤࡦࡴ࡬ࡲ࡬ࠦࡴࡦࡵࡷࠤ࡫࡯࡬ࡦࡵࠣࡻ࡮ࡺࡨࠡࡱࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮ࠡࡵࡷࡶࡦࡺࡥࡨࡻ࠽ࠤࢀࢃࠢṕ").format(orchestration_strategy))
            if cli.is_running():
                self.logger.debug(bstack111l11_opy_ (u"࡙ࠥࡸ࡯࡮ࡨࠢࡆࡐࡎࠦࡦ࡭ࡱࡺࠤ࡫ࡵࡲࠡࡶࡨࡷࡹࠦࡦࡪ࡮ࡨࡷࠥࡵࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲ࠳ࠨṖ"))
                ordered_test_files = cli.test_orchestration_session(test_files, orchestration_strategy)
            else:
                self.logger.debug(bstack111l11_opy_ (u"࡚ࠦࡹࡩ࡯ࡩࠣࡷࡩࡱࠠࡧ࡮ࡲࡻࠥ࡬࡯ࡳࠢࡷࡩࡸࡺࠠࡧ࡫࡯ࡩࡸࠦ࡯ࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳ࠴ࠢṗ"))
                self.bstack111l11l1lll_opy_.bstack111l11l1ll1_opy_(test_files, orchestration_strategy, bstack111l11ll1l1_opy_)
                ordered_test_files = self.bstack111l11l1lll_opy_.bstack111l11l11l1_opy_()
            if not ordered_test_files:
                return None
            self.bstack1111l111ll_opy_(bstack111l11_opy_ (u"ࠧࡻࡰ࡭ࡱࡤࡨࡪࡪࡔࡦࡵࡷࡊ࡮ࡲࡥࡴࡅࡲࡹࡳࡺࠢṘ"), len(test_files))
            self.bstack1111l111ll_opy_(bstack111l11_opy_ (u"ࠨ࡮ࡰࡦࡨࡍࡳࡪࡥࡹࠤṙ"), int(os.environ.get(bstack111l11_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡎࡐࡆࡈࡣࡎࡔࡄࡆ࡚ࠥṚ")) or bstack111l11_opy_ (u"ࠣ࠲ࠥṛ")))
            self.bstack1111l111ll_opy_(bstack111l11_opy_ (u"ࠤࡷࡳࡹࡧ࡬ࡏࡱࡧࡩࡸࠨṜ"), int(os.environ.get(bstack111l11_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡑࡓࡉࡋ࡟ࡄࡑࡘࡒ࡙ࠨṝ")) or bstack111l11_opy_ (u"ࠦ࠶ࠨṞ")))
            self.bstack1111l111ll_opy_(bstack111l11_opy_ (u"ࠧࡪ࡯ࡸࡰ࡯ࡳࡦࡪࡥࡥࡖࡨࡷࡹࡌࡩ࡭ࡧࡶࡇࡴࡻ࡮ࡵࠤṟ"), len(ordered_test_files))
            self.bstack1111l111ll_opy_(bstack111l11_opy_ (u"ࠨࡳࡱ࡮࡬ࡸ࡙࡫ࡳࡵࡵࡄࡔࡎࡉࡡ࡭࡮ࡆࡳࡺࡴࡴࠣṠ"), self.bstack111l11l1lll_opy_.bstack111l11l11ll_opy_())
            return ordered_test_files
        except Exception as e:
            self.logger.debug(bstack111l11_opy_ (u"ࠢ࡜ࡴࡨࡳࡷࡪࡥࡳࡡࡷࡩࡸࡺ࡟ࡧ࡫࡯ࡩࡸࡣࠠࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡲࡶࡩ࡫ࡲࡪࡰࡪࠤࡹ࡫ࡳࡵࠢࡦࡰࡦࡹࡳࡦࡵ࠽ࠤࢀࢃࠢṡ").format(e))
        return None
    def bstack1111l111ll_opy_(self, key, value):
        self.bstack111l111ll11_opy_[key] = value
    def bstack1lll1lll11_opy_(self):
        return self.bstack111l111ll11_opy_