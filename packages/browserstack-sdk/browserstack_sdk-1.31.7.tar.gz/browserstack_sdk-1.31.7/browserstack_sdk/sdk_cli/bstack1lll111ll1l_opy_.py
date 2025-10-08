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
import logging
import abc
from browserstack_sdk.sdk_cli.bstack1llllllllll_opy_ import bstack1111111111_opy_
class bstack1ll1ll1lll1_opy_(abc.ABC):
    bin_session_id: str
    bstack1llllllllll_opy_: bstack1111111111_opy_
    def __init__(self):
        self.bstack1ll1ll1ll1l_opy_ = None
        self.config = None
        self.bin_session_id = None
        self.bstack1llllllllll_opy_ = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
    def bstack1lll1111111_opy_(self):
        return (self.bstack1ll1ll1ll1l_opy_ != None and self.bin_session_id != None and self.bstack1llllllllll_opy_ != None)
    def configure(self, bstack1ll1ll1ll1l_opy_, config, bin_session_id: str, bstack1llllllllll_opy_: bstack1111111111_opy_):
        self.bstack1ll1ll1ll1l_opy_ = bstack1ll1ll1ll1l_opy_
        self.config = config
        self.bin_session_id = bin_session_id
        self.bstack1llllllllll_opy_ = bstack1llllllllll_opy_
        if self.bin_session_id:
            self.logger.debug(bstack111l11_opy_ (u"ࠥ࡟ࢀ࡯ࡤࠩࡵࡨࡰ࡫࠯ࡽ࡞ࠢࡦࡳࡳ࡬ࡩࡨࡷࡵࡩࡩࠦ࡭ࡰࡦࡸࡰࡪࠦࡻࡴࡧ࡯ࡪ࠳ࡥ࡟ࡤ࡮ࡤࡷࡸࡥ࡟࠯ࡡࡢࡲࡦࡳࡥࡠࡡࢀ࠾ࠥࡨࡩ࡯ࡡࡶࡩࡸࡹࡩࡰࡰࡢ࡭ࡩࡃࠢቜ") + str(self.bin_session_id) + bstack111l11_opy_ (u"ࠦࠧቝ"))
    def bstack1ll11l11111_opy_(self):
        if not self.bin_session_id:
            raise ValueError(bstack111l11_opy_ (u"ࠧࡨࡩ࡯ࡡࡶࡩࡸࡹࡩࡰࡰࡢ࡭ࡩࠦࡣࡢࡰࡱࡳࡹࠦࡢࡦࠢࡑࡳࡳ࡫ࠢ቞"))
    @abc.abstractmethod
    def is_enabled(self) -> bool:
        return False