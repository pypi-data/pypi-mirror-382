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
import tempfile
import math
from bstack_utils import bstack11l1l1111_opy_
from bstack_utils.constants import bstack11111l1l_opy_, bstack11l1ll11l1l_opy_
from bstack_utils.helper import bstack111ll1l1lll_opy_, get_host_info
from bstack_utils.bstack11ll1111l11_opy_ import bstack11ll1111l1l_opy_
bstack111l1111l11_opy_ = bstack111l11_opy_ (u"ࠣࡴࡨࡸࡷࡿࡔࡦࡵࡷࡷࡔࡴࡆࡢ࡫࡯ࡹࡷ࡫ࠢṢ")
bstack1111lll11l1_opy_ = bstack111l11_opy_ (u"ࠤࡤࡦࡴࡸࡴࡃࡷ࡬ࡰࡩࡕ࡮ࡇࡣ࡬ࡰࡺࡸࡥࠣṣ")
bstack1111ll111ll_opy_ = bstack111l11_opy_ (u"ࠥࡶࡺࡴࡐࡳࡧࡹ࡭ࡴࡻࡳ࡭ࡻࡉࡥ࡮ࡲࡥࡥࡈ࡬ࡶࡸࡺࠢṤ")
bstack1111ll1llll_opy_ = bstack111l11_opy_ (u"ࠦࡷ࡫ࡲࡶࡰࡓࡶࡪࡼࡩࡰࡷࡶࡰࡾࡌࡡࡪ࡮ࡨࡨࠧṥ")
bstack111l11111ll_opy_ = bstack111l11_opy_ (u"ࠧࡹ࡫ࡪࡲࡉࡰࡦࡱࡹࡢࡰࡧࡊࡦ࡯࡬ࡦࡦࠥṦ")
bstack111l111l11l_opy_ = bstack111l11_opy_ (u"ࠨࡲࡶࡰࡖࡱࡦࡸࡴࡔࡧ࡯ࡩࡨࡺࡩࡰࡰࠥṧ")
bstack1111ll1lll1_opy_ = {
    bstack111l1111l11_opy_,
    bstack1111lll11l1_opy_,
    bstack1111ll111ll_opy_,
    bstack1111ll1llll_opy_,
    bstack111l11111ll_opy_,
    bstack111l111l11l_opy_
}
bstack1111llll1ll_opy_ = {bstack111l11_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧṨ")}
logger = bstack11l1l1111_opy_.get_logger(__name__, bstack11111l1l_opy_)
class bstack1111ll11l11_opy_:
    def __init__(self):
        self.enabled = False
        self.name = None
    def enable(self, name):
        self.enabled = True
        self.name = name
    def disable(self):
        self.enabled = False
        self.name = None
    def bstack1111lll1111_opy_(self):
        return self.enabled
    def get_name(self):
        return self.name
class bstack11111l1ll_opy_:
    _1ll1l11lll1_opy_ = None
    def __init__(self, config):
        self.bstack1111ll11111_opy_ = False
        self.bstack1111ll1l111_opy_ = False
        self.bstack1111llll11l_opy_ = False
        self.bstack1111ll1111l_opy_ = False
        self.bstack1111lllll1l_opy_ = None
        self.bstack111l1111ll1_opy_ = bstack1111ll11l11_opy_()
        self.bstack111l111l1l1_opy_ = None
        opts = config.get(bstack111l11_opy_ (u"ࠨࡶࡨࡷࡹࡕࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲࡔࡶࡴࡪࡱࡱࡷࠬṩ"), {})
        bstack111l111111l_opy_ = opts.get(bstack111l111l11l_opy_, {})
        self.__1111ll11lll_opy_(
            bstack111l111111l_opy_.get(bstack111l11_opy_ (u"ࠩࡨࡲࡦࡨ࡬ࡦࡦࠪṪ"), False),
            bstack111l111111l_opy_.get(bstack111l11_opy_ (u"ࠪࡱࡴࡪࡥࠨṫ"), bstack111l11_opy_ (u"ࠫࡷ࡫࡬ࡦࡸࡤࡲࡹࡌࡩࡳࡵࡷࠫṬ")),
            bstack111l111111l_opy_.get(bstack111l11_opy_ (u"ࠬࡹ࡯ࡶࡴࡦࡩࠬṭ"), None)
        )
        self.__1111ll1ll1l_opy_(opts.get(bstack1111ll111ll_opy_, False))
        self.__1111lll1ll1_opy_(opts.get(bstack1111ll1llll_opy_, False))
        self.__1111ll1l1l1_opy_(opts.get(bstack111l11111ll_opy_, False))
    @classmethod
    def bstack1lll111l11_opy_(cls, config=None):
        if cls._1ll1l11lll1_opy_ is None and config is not None:
            cls._1ll1l11lll1_opy_ = bstack11111l1ll_opy_(config)
        return cls._1ll1l11lll1_opy_
    @staticmethod
    def bstack1l11ll1l_opy_(config: dict) -> bool:
        bstack111l1111lll_opy_ = config.get(bstack111l11_opy_ (u"࠭ࡴࡦࡵࡷࡓࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࡒࡴࡹ࡯࡯࡯ࡵࠪṮ"), {}).get(bstack111l1111l11_opy_, {})
        return bstack111l1111lll_opy_.get(bstack111l11_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡤࠨṯ"), False)
    @staticmethod
    def bstack11l1lll11_opy_(config: dict) -> int:
        bstack111l1111lll_opy_ = config.get(bstack111l11_opy_ (u"ࠨࡶࡨࡷࡹࡕࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲࡔࡶࡴࡪࡱࡱࡷࠬṰ"), {}).get(bstack111l1111l11_opy_, {})
        retries = 0
        if bstack11111l1ll_opy_.bstack1l11ll1l_opy_(config):
            retries = bstack111l1111lll_opy_.get(bstack111l11_opy_ (u"ࠩࡰࡥࡽࡘࡥࡵࡴ࡬ࡩࡸ࠭ṱ"), 1)
        return retries
    @staticmethod
    def bstack1lll1llll1_opy_(config: dict) -> dict:
        bstack1111lll1l1l_opy_ = config.get(bstack111l11_opy_ (u"ࠪࡸࡪࡹࡴࡐࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࡏࡱࡶ࡬ࡳࡳࡹࠧṲ"), {})
        return {
            key: value for key, value in bstack1111lll1l1l_opy_.items() if key in bstack1111ll1lll1_opy_
        }
    @staticmethod
    def bstack1111lllll11_opy_():
        bstack111l11_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࡅ࡫ࡩࡨࡱࠠࡪࡨࠣࡸ࡭࡫ࠠࡢࡤࡲࡶࡹࠦࡢࡶ࡫࡯ࡨࠥ࡬ࡩ࡭ࡧࠣࡩࡽ࡯ࡳࡵࡵ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠨࠢࠣṳ")
        return os.path.exists(os.path.join(tempfile.gettempdir(), bstack111l11_opy_ (u"ࠧࡧࡢࡰࡴࡷࡣࡧࡻࡩ࡭ࡦࡢࡿࢂࠨṴ").format(os.getenv(bstack111l11_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠦṵ")))))
    @staticmethod
    def bstack1111lll1lll_opy_(test_name: str):
        bstack111l11_opy_ (u"ࠢࠣࠤࠍࠤࠥࠦࠠࠡࠢࠣࠤࡈ࡮ࡥࡤ࡭ࠣ࡭࡫ࠦࡴࡩࡧࠣࡥࡧࡵࡲࡵࠢࡥࡹ࡮ࡲࡤࠡࡨ࡬ࡰࡪࠦࡥࡹ࡫ࡶࡸࡸ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦṶ")
        bstack1111lll11ll_opy_ = os.path.join(tempfile.gettempdir(), bstack111l11_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࡠࡶࡨࡷࡹࡹ࡟ࡼࡿ࠱ࡸࡽࡺࠢṷ").format(os.getenv(bstack111l11_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠢṸ"))))
        with open(bstack1111lll11ll_opy_, bstack111l11_opy_ (u"ࠪࡥࠬṹ")) as file:
            file.write(bstack111l11_opy_ (u"ࠦࢀࢃ࡜࡯ࠤṺ").format(test_name))
    @staticmethod
    def bstack1111ll11l1l_opy_(framework: str) -> bool:
       return framework.lower() in bstack1111llll1ll_opy_
    @staticmethod
    def bstack11l1l1111ll_opy_(config: dict) -> bool:
        bstack1111lll111l_opy_ = config.get(bstack111l11_opy_ (u"ࠬࡺࡥࡴࡶࡒࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯ࡑࡳࡸ࡮ࡵ࡮ࡴࠩṻ"), {}).get(bstack1111lll11l1_opy_, {})
        return bstack1111lll111l_opy_.get(bstack111l11_opy_ (u"࠭ࡥ࡯ࡣࡥࡰࡪࡪࠧṼ"), False)
    @staticmethod
    def bstack11l1l11l111_opy_(config: dict, bstack11l1l11ll1l_opy_: int = 0) -> int:
        bstack111l11_opy_ (u"ࠢࠣࠤࠍࠤࠥࠦࠠࠡࠢࠣࠤࡌ࡫ࡴࠡࡶ࡫ࡩࠥ࡬ࡡࡪ࡮ࡸࡶࡪࠦࡴࡩࡴࡨࡷ࡭ࡵ࡬ࡥ࠮ࠣࡻ࡭࡯ࡣࡩࠢࡦࡥࡳࠦࡢࡦࠢࡤࡲࠥࡧࡢࡴࡱ࡯ࡹࡹ࡫ࠠ࡯ࡷࡰࡦࡪࡸࠠࡰࡴࠣࡥࠥࡶࡥࡳࡥࡨࡲࡹࡧࡧࡦ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࡆࡸࡧࡴ࠼ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡥࡲࡲ࡫࡯ࡧࠡࠪࡧ࡭ࡨࡺࠩ࠻ࠢࡗ࡬ࡪࠦࡣࡰࡰࡩ࡭࡬ࡻࡲࡢࡶ࡬ࡳࡳࠦࡤࡪࡥࡷ࡭ࡴࡴࡡࡳࡻ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡷࡳࡹࡧ࡬ࡠࡶࡨࡷࡹࡹࠠࠩ࡫ࡱࡸ࠮ࡀࠠࡕࡪࡨࠤࡹࡵࡴࡢ࡮ࠣࡲࡺࡳࡢࡦࡴࠣࡳ࡫ࠦࡴࡦࡵࡷࡷࠥ࠮ࡲࡦࡳࡸ࡭ࡷ࡫ࡤࠡࡨࡲࡶࠥࡶࡥࡳࡥࡨࡲࡹࡧࡧࡦ࠯ࡥࡥࡸ࡫ࡤࠡࡶ࡫ࡶࡪࡹࡨࡰ࡮ࡧࡷ࠮࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࡔࡨࡸࡺࡸ࡮ࡴ࠼ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡ࡫ࡱࡸ࠿ࠦࡔࡩࡧࠣࡪࡦ࡯࡬ࡶࡴࡨࠤࡹ࡮ࡲࡦࡵ࡫ࡳࡱࡪ࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠥࠦࠧṽ")
        bstack1111lll111l_opy_ = config.get(bstack111l11_opy_ (u"ࠨࡶࡨࡷࡹࡕࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲࡔࡶࡴࡪࡱࡱࡷࠬṾ"), {}).get(bstack111l11_opy_ (u"ࠩࡤࡦࡴࡸࡴࡃࡷ࡬ࡰࡩࡕ࡮ࡇࡣ࡬ࡰࡺࡸࡥࠨṿ"), {})
        bstack1111ll111l1_opy_ = 0
        bstack111l111l111_opy_ = 0
        if bstack11111l1ll_opy_.bstack11l1l1111ll_opy_(config):
            bstack111l111l111_opy_ = bstack1111lll111l_opy_.get(bstack111l11_opy_ (u"ࠪࡱࡦࡾࡆࡢ࡫࡯ࡹࡷ࡫ࡳࠨẀ"), 5)
            if isinstance(bstack111l111l111_opy_, str) and bstack111l111l111_opy_.endswith(bstack111l11_opy_ (u"ࠫࠪ࠭ẁ")):
                try:
                    percentage = int(bstack111l111l111_opy_.strip(bstack111l11_opy_ (u"ࠬࠫࠧẂ")))
                    if bstack11l1l11ll1l_opy_ > 0:
                        bstack1111ll111l1_opy_ = math.ceil((percentage * bstack11l1l11ll1l_opy_) / 100)
                    else:
                        raise ValueError(bstack111l11_opy_ (u"ࠨࡔࡰࡶࡤࡰࠥࡺࡥࡴࡶࡶࠤࡲࡻࡳࡵࠢࡥࡩࠥࡶࡲࡰࡸ࡬ࡨࡪࡪࠠࡧࡱࡵࠤࡵ࡫ࡲࡤࡧࡱࡸࡦ࡭ࡥ࠮ࡤࡤࡷࡪࡪࠠࡵࡪࡵࡩࡸ࡮࡯࡭ࡦࡶ࠲ࠧẃ"))
                except ValueError as e:
                    raise ValueError(bstack111l11_opy_ (u"ࠢࡊࡰࡹࡥࡱ࡯ࡤࠡࡲࡨࡶࡨ࡫࡮ࡵࡣࡪࡩࠥࡼࡡ࡭ࡷࡨࠤ࡫ࡵࡲࠡ࡯ࡤࡼࡋࡧࡩ࡭ࡷࡵࡩࡸࡀࠠࡼࡿࠥẄ").format(bstack111l111l111_opy_)) from e
            else:
                bstack1111ll111l1_opy_ = int(bstack111l111l111_opy_)
        logger.info(bstack111l11_opy_ (u"ࠣࡏࡤࡼࠥ࡬ࡡࡪ࡮ࡸࡶࡪࡹࠠࡵࡪࡵࡩࡸ࡮࡯࡭ࡦࠣࡷࡪࡺࠠࡵࡱ࠽ࠤࢀࢃࠠࠩࡨࡵࡳࡲࠦࡣࡰࡰࡩ࡭࡬ࡀࠠࡼࡿࠬࠦẅ").format(bstack1111ll111l1_opy_, bstack111l111l111_opy_))
        return bstack1111ll111l1_opy_
    def bstack111l1111l1l_opy_(self):
        return self.bstack1111ll1111l_opy_
    def bstack1111ll1l1ll_opy_(self):
        return self.bstack1111lllll1l_opy_
    def bstack1111ll11ll1_opy_(self):
        return self.bstack111l111l1l1_opy_
    def __1111ll11lll_opy_(self, enabled, mode, source=None):
        try:
            self.bstack1111ll1111l_opy_ = bool(enabled)
            self.bstack1111lllll1l_opy_ = mode
            if source is None:
                self.bstack111l111l1l1_opy_ = []
            elif isinstance(source, list):
                self.bstack111l111l1l1_opy_ = source
            self.__1111llll1l1_opy_()
        except Exception as e:
            logger.error(bstack111l11_opy_ (u"ࠤ࡞ࡣࡤࡹࡥࡵࡡࡵࡹࡳࡥࡳ࡮ࡣࡵࡸࡤࡹࡥ࡭ࡧࡦࡸ࡮ࡵ࡮࡞ࠢࠣࡿࢂࠨẆ").format(e))
    def bstack111l11111l1_opy_(self):
        return self.bstack1111ll11111_opy_
    def __1111ll1ll1l_opy_(self, value):
        self.bstack1111ll11111_opy_ = bool(value)
        self.__1111llll1l1_opy_()
    def bstack1111llllll1_opy_(self):
        return self.bstack1111ll1l111_opy_
    def __1111lll1ll1_opy_(self, value):
        self.bstack1111ll1l111_opy_ = bool(value)
        self.__1111llll1l1_opy_()
    def bstack1111llll111_opy_(self):
        return self.bstack1111llll11l_opy_
    def __1111ll1l1l1_opy_(self, value):
        self.bstack1111llll11l_opy_ = bool(value)
        self.__1111llll1l1_opy_()
    def __1111llll1l1_opy_(self):
        if self.bstack1111ll1111l_opy_:
            self.bstack1111ll11111_opy_ = False
            self.bstack1111ll1l111_opy_ = False
            self.bstack1111llll11l_opy_ = False
            self.bstack111l1111ll1_opy_.enable(bstack111l111l11l_opy_)
        elif self.bstack1111ll11111_opy_:
            self.bstack1111ll1l111_opy_ = False
            self.bstack1111llll11l_opy_ = False
            self.bstack1111ll1111l_opy_ = False
            self.bstack111l1111ll1_opy_.enable(bstack1111ll111ll_opy_)
        elif self.bstack1111ll1l111_opy_:
            self.bstack1111ll11111_opy_ = False
            self.bstack1111llll11l_opy_ = False
            self.bstack1111ll1111l_opy_ = False
            self.bstack111l1111ll1_opy_.enable(bstack1111ll1llll_opy_)
        elif self.bstack1111llll11l_opy_:
            self.bstack1111ll11111_opy_ = False
            self.bstack1111ll1l111_opy_ = False
            self.bstack1111ll1111l_opy_ = False
            self.bstack111l1111ll1_opy_.enable(bstack111l11111ll_opy_)
        else:
            self.bstack111l1111ll1_opy_.disable()
    def bstack1ll11111ll_opy_(self):
        return self.bstack111l1111ll1_opy_.bstack1111lll1111_opy_()
    def bstack11ll1l11ll_opy_(self):
        if self.bstack111l1111ll1_opy_.bstack1111lll1111_opy_():
            return self.bstack111l1111ll1_opy_.get_name()
        return None
    def bstack111l11ll1ll_opy_(self):
        data = {
            bstack111l11_opy_ (u"ࠪࡶࡺࡴ࡟ࡴ࡯ࡤࡶࡹࡥࡳࡦ࡮ࡨࡧࡹ࡯࡯࡯ࠩẇ"): {
                bstack111l11_opy_ (u"ࠫࡪࡴࡡࡣ࡮ࡨࡨࠬẈ"): self.bstack111l1111l1l_opy_(),
                bstack111l11_opy_ (u"ࠬࡳ࡯ࡥࡧࠪẉ"): self.bstack1111ll1l1ll_opy_(),
                bstack111l11_opy_ (u"࠭ࡳࡰࡷࡵࡧࡪ࠭Ẋ"): self.bstack1111ll11ll1_opy_()
            }
        }
        return data
    def bstack1111lllllll_opy_(self, config):
        bstack1111ll1ll11_opy_ = {}
        bstack1111ll1ll11_opy_[bstack111l11_opy_ (u"ࠧࡳࡷࡱࡣࡸࡳࡡࡳࡶࡢࡷࡪࡲࡥࡤࡶ࡬ࡳࡳ࠭ẋ")] = {
            bstack111l11_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡥࠩẌ"): self.bstack111l1111l1l_opy_(),
            bstack111l11_opy_ (u"ࠩࡰࡳࡩ࡫ࠧẍ"): self.bstack1111ll1l1ll_opy_()
        }
        bstack1111ll1ll11_opy_[bstack111l11_opy_ (u"ࠪࡶࡪࡸࡵ࡯ࡡࡳࡶࡪࡼࡩࡰࡷࡶࡰࡾࡥࡦࡢ࡫࡯ࡩࡩ࠭Ẏ")] = {
            bstack111l11_opy_ (u"ࠫࡪࡴࡡࡣ࡮ࡨࡨࠬẏ"): self.bstack1111llllll1_opy_()
        }
        bstack1111ll1ll11_opy_[bstack111l11_opy_ (u"ࠬࡸࡵ࡯ࡡࡳࡶࡪࡼࡩࡰࡷࡶࡰࡾࡥࡦࡢ࡫࡯ࡩࡩࡥࡦࡪࡴࡶࡸࠬẐ")] = {
            bstack111l11_opy_ (u"࠭ࡥ࡯ࡣࡥࡰࡪࡪࠧẑ"): self.bstack111l11111l1_opy_()
        }
        bstack1111ll1ll11_opy_[bstack111l11_opy_ (u"ࠧࡴ࡭࡬ࡴࡤ࡬ࡡࡪ࡮࡬ࡲ࡬ࡥࡡ࡯ࡦࡢࡪࡱࡧ࡫ࡺࠩẒ")] = {
            bstack111l11_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡥࠩẓ"): self.bstack1111llll111_opy_()
        }
        if self.bstack1l11ll1l_opy_(config):
            bstack1111ll1ll11_opy_[bstack111l11_opy_ (u"ࠩࡵࡩࡹࡸࡹࡠࡶࡨࡷࡹࡹ࡟ࡰࡰࡢࡪࡦ࡯࡬ࡶࡴࡨࠫẔ")] = {
                bstack111l11_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧࡧࠫẕ"): True,
                bstack111l11_opy_ (u"ࠫࡲࡧࡸࡠࡴࡨࡸࡷ࡯ࡥࡴࠩẖ"): self.bstack11l1lll11_opy_(config)
            }
        if self.bstack11l1l1111ll_opy_(config):
            bstack1111ll1ll11_opy_[bstack111l11_opy_ (u"ࠬࡧࡢࡰࡴࡷࡣࡧࡻࡩ࡭ࡦࡢࡳࡳࡥࡦࡢ࡫࡯ࡹࡷ࡫ࠧẗ")] = {
                bstack111l11_opy_ (u"࠭ࡥ࡯ࡣࡥࡰࡪࡪࠧẘ"): True,
                bstack111l11_opy_ (u"ࠧ࡮ࡣࡻࡣ࡫ࡧࡩ࡭ࡷࡵࡩࡸ࠭ẙ"): self.bstack11l1l11l111_opy_(config)
            }
        return bstack1111ll1ll11_opy_
    def bstack11ll11l1_opy_(self, config):
        bstack111l11_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤࠥࡉ࡯࡭࡮ࡨࡧࡹࡹࠠࡣࡷ࡬ࡰࡩࠦࡤࡢࡶࡤࠤࡧࡿࠠ࡮ࡣ࡮࡭ࡳ࡭ࠠࡢࠢࡦࡥࡱࡲࠠࡵࡱࠣࡸ࡭࡫ࠠࡤࡱ࡯ࡰࡪࡩࡴ࠮ࡤࡸ࡭ࡱࡪ࠭ࡥࡣࡷࡥࠥ࡫࡮ࡥࡲࡲ࡭ࡳࡺ࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࡄࡶ࡬ࡹ࠺ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡢࡶ࡫࡯ࡨࡤࡻࡵࡪࡦࠣࠬࡸࡺࡲࠪ࠼ࠣࡘ࡭࡫ࠠࡖࡗࡌࡈࠥࡵࡦࠡࡶ࡫ࡩࠥࡨࡵࡪ࡮ࡧࠤࡹࡵࠠࡤࡱ࡯ࡰࡪࡩࡴࠡࡦࡤࡸࡦࠦࡦࡰࡴ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࡘࡥࡵࡷࡵࡲࡸࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡪࡩࡤࡶ࠽ࠤࡗ࡫ࡳࡱࡱࡱࡷࡪࠦࡦࡳࡱࡰࠤࡹ࡮ࡥࠡࡥࡲࡰࡱ࡫ࡣࡵ࠯ࡥࡹ࡮ࡲࡤ࠮ࡦࡤࡸࡦࠦࡥ࡯ࡦࡳࡳ࡮ࡴࡴ࠭ࠢࡲࡶࠥࡔ࡯࡯ࡧࠣ࡭࡫ࠦࡦࡢ࡫࡯ࡩࡩ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦẚ")
        if not (config.get(bstack111l11_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠬẛ"), None) in bstack11l1ll11l1l_opy_ and self.bstack111l1111l1l_opy_()):
            return None
        bstack1111lll1l11_opy_ = os.environ.get(bstack111l11_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨẜ"), None)
        logger.debug(bstack111l11_opy_ (u"ࠦࡠࡩ࡯࡭࡮ࡨࡧࡹࡈࡵࡪ࡮ࡧࡈࡦࡺࡡ࡞ࠢࡆࡳࡱࡲࡥࡤࡶ࡬ࡲ࡬ࠦࡢࡶ࡫࡯ࡨࠥࡪࡡࡵࡣࠣࡪࡴࡸࠠࡣࡷ࡬ࡰࡩࠦࡕࡖࡋࡇ࠾ࠥࢁࡽࠣẝ").format(bstack1111lll1l11_opy_))
        try:
            bstack11ll111lll1_opy_ = bstack111l11_opy_ (u"ࠧࡺࡥࡴࡶࡲࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯࠱ࡤࡴ࡮࠵ࡶ࠲࠱ࡥࡹ࡮ࡲࡤࡴ࠱ࡾࢁ࠴ࡩ࡯࡭࡮ࡨࡧࡹ࠳ࡢࡶ࡫࡯ࡨ࠲ࡪࡡࡵࡣࠥẞ").format(bstack1111lll1l11_opy_)
            bstack1111l1lllll_opy_ = self.bstack1111ll11ll1_opy_() or [] # for multi-repo
            bstack111l111l1ll_opy_ = bstack111ll1l1lll_opy_(bstack1111l1lllll_opy_) # bstack11l1111lll1_opy_-repo is handled bstack111l1111111_opy_
            payload = {
                bstack111l11_opy_ (u"ࠨࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠦẟ"): config.get(bstack111l11_opy_ (u"ࠧࡱࡴࡲ࡮ࡪࡩࡴࡏࡣࡰࡩࠬẠ"), bstack111l11_opy_ (u"ࠨࠩạ")),
                bstack111l11_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠧẢ"): config.get(bstack111l11_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭ả"), os.path.basename(os.path.abspath(os.getcwd()))),
                bstack111l11_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡕࡹࡳࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠤẤ"): config.get(bstack111l11_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧấ"), bstack111l11_opy_ (u"࠭ࠧẦ")),
                bstack111l11_opy_ (u"ࠢ࡯ࡱࡧࡩࡎࡴࡤࡦࡺࠥầ"): int(os.environ.get(bstack111l11_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡏࡑࡇࡉࡤࡏࡎࡅࡇ࡛ࠦẨ")) or bstack111l11_opy_ (u"ࠤ࠳ࠦẩ")),
                bstack111l11_opy_ (u"ࠥࡸࡴࡺࡡ࡭ࡐࡲࡨࡪࡹࠢẪ"): int(os.environ.get(bstack111l11_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡔ࡚ࡁࡍࡡࡑࡓࡉࡋ࡟ࡄࡑࡘࡒ࡙ࠨẫ")) or bstack111l11_opy_ (u"ࠧ࠷ࠢẬ")),
                bstack111l11_opy_ (u"ࠨࡨࡰࡵࡷࡍࡳ࡬࡯ࠣậ"): get_host_info(),
                bstack111l11_opy_ (u"ࠢࡱࡴࡇࡩࡹࡧࡩ࡭ࡵࠥẮ"): bstack111l111l1ll_opy_
            }
            logger.debug(bstack111l11_opy_ (u"ࠣ࡝ࡦࡳࡱࡲࡥࡤࡶࡅࡹ࡮ࡲࡤࡅࡣࡷࡥࡢࠦࡓࡦࡰࡧ࡭ࡳ࡭ࠠࡣࡷ࡬ࡰࡩࠦࡤࡢࡶࡤࠤࡵࡧࡹ࡭ࡱࡤࡨ࠿ࠦࡻࡾࠤắ").format(payload))
            response = bstack11ll1111l1l_opy_.bstack1111ll1l11l_opy_(bstack11ll111lll1_opy_, payload)
            if response:
                logger.debug(bstack111l11_opy_ (u"ࠤ࡞ࡧࡴࡲ࡬ࡦࡥࡷࡆࡺ࡯࡬ࡥࡆࡤࡸࡦࡣࠠࡃࡷ࡬ࡰࡩࠦࡤࡢࡶࡤࠤࡨࡵ࡬࡭ࡧࡦࡸ࡮ࡵ࡮ࠡࡴࡨࡷࡵࡵ࡮ࡴࡧ࠽ࠤࢀࢃࠢẰ").format(response))
                return response
            else:
                logger.error(bstack111l11_opy_ (u"ࠥ࡟ࡨࡵ࡬࡭ࡧࡦࡸࡇࡻࡩ࡭ࡦࡇࡥࡹࡧ࡝ࠡࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡨࡵ࡬࡭ࡧࡦࡸࠥࡨࡵࡪ࡮ࡧࠤࡩࡧࡴࡢࠢࡩࡳࡷࠦࡢࡶ࡫࡯ࡨ࡛ࠥࡕࡊࡆ࠽ࠤࢀࢃࠢằ").format(bstack1111lll1l11_opy_))
                return None
        except Exception as e:
            logger.error(bstack111l11_opy_ (u"ࠦࡠࡩ࡯࡭࡮ࡨࡧࡹࡈࡵࡪ࡮ࡧࡈࡦࡺࡡ࡞ࠢࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡥࡲࡰࡱ࡫ࡣࡵ࡫ࡱ࡫ࠥࡨࡵࡪ࡮ࡧࠤࡩࡧࡴࡢࠢࡩࡳࡷࠦࡢࡶ࡫࡯ࡨ࡛ࠥࡕࡊࡆࠣࡿࢂࡀࠠࡼࡿࠥẲ").format(bstack1111lll1l11_opy_, e))
            return None