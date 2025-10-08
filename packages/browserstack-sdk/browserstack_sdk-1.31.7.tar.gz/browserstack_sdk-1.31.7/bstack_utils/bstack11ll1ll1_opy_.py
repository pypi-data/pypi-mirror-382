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
import threading
import tempfile
import os
import time
from datetime import datetime
from bstack_utils.bstack11ll1111l11_opy_ import bstack11ll1111l1l_opy_
from bstack_utils.constants import bstack11l1l1lllll_opy_, bstack11111l1l_opy_
from bstack_utils.bstack1l11ll11_opy_ import bstack11111l1ll_opy_
from bstack_utils import bstack11l1l1111_opy_
bstack11l1l111lll_opy_ = 10
class bstack1ll1l1l1l_opy_:
    def __init__(self, bstack1lll1lllll_opy_, config, bstack11l1l11ll1l_opy_=0):
        self.bstack11l11llll1l_opy_ = set()
        self.lock = threading.Lock()
        self.bstack11l1l111l11_opy_ = bstack111l11_opy_ (u"ࠣࡽࢀ࠳ࡹ࡫ࡳࡵࡱࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮࠰ࡣࡳ࡭࠴ࡼ࠱࠰ࡨࡤ࡭ࡱ࡫ࡤ࠮ࡶࡨࡷࡹࡹࠢ᫢").format(bstack11l1l1lllll_opy_)
        self.bstack11l1l1l1111_opy_ = os.path.join(tempfile.gettempdir(), bstack111l11_opy_ (u"ࠤࡤࡦࡴࡸࡴࡠࡤࡸ࡭ࡱࡪ࡟ࡼࡿࠥ᫣").format(os.environ.get(bstack111l11_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨ᫤"))))
        self.bstack11l1l11l1l1_opy_ = os.path.join(tempfile.gettempdir(), bstack111l11_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࡣࡹ࡫ࡳࡵࡵࡢࡿࢂ࠴ࡴࡹࡶࠥ᫥").format(os.environ.get(bstack111l11_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪ᫦"))))
        self.bstack11l1l11l11l_opy_ = 2
        self.bstack1lll1lllll_opy_ = bstack1lll1lllll_opy_
        self.config = config
        self.logger = bstack11l1l1111_opy_.get_logger(__name__, bstack11111l1l_opy_)
        self.bstack11l1l11ll1l_opy_ = bstack11l1l11ll1l_opy_
        self.bstack11l1l111ll1_opy_ = False
        self.bstack11l1l11111l_opy_ = not (
                            os.environ.get(bstack111l11_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡈࡕࡊࡎࡇࡣࡗ࡛ࡎࡠࡋࡇࡉࡓ࡚ࡉࡇࡋࡈࡖࠧ᫧")) and
                            os.environ.get(bstack111l11_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡎࡐࡆࡈࡣࡎࡔࡄࡆ࡚ࠥ᫨")) and
                            os.environ.get(bstack111l11_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡑࡗࡅࡑࡥࡎࡐࡆࡈࡣࡈࡕࡕࡏࡖࠥ᫩"))
                        )
        if bstack11111l1ll_opy_.bstack11l1l1111ll_opy_(config):
            self.bstack11l1l11l11l_opy_ = bstack11111l1ll_opy_.bstack11l1l11l111_opy_(config, self.bstack11l1l11ll1l_opy_)
            self.bstack11l1l11llll_opy_()
    def bstack11l1l111111_opy_(self):
        return bstack111l11_opy_ (u"ࠤࡾࢁࡤࢁࡽࠣ᫪").format(self.config.get(bstack111l11_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭᫫")), os.environ.get(bstack111l11_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡆ࡚ࡏࡌࡅࡡࡕ࡙ࡓࡥࡉࡅࡇࡑࡘࡎࡌࡉࡆࡔࠪ᫬")))
    def bstack11l1l11ll11_opy_(self):
        try:
            if self.bstack11l1l11111l_opy_:
                return
            with self.lock:
                try:
                    with open(self.bstack11l1l11l1l1_opy_, bstack111l11_opy_ (u"ࠧࡸࠢ᫭")) as f:
                        bstack11l11llllll_opy_ = set(line.strip() for line in f if line.strip())
                except FileNotFoundError:
                    bstack11l11llllll_opy_ = set()
                bstack11l1l111l1l_opy_ = bstack11l11llllll_opy_ - self.bstack11l11llll1l_opy_
                if not bstack11l1l111l1l_opy_:
                    return
                self.bstack11l11llll1l_opy_.update(bstack11l1l111l1l_opy_)
                data = {bstack111l11_opy_ (u"ࠨࡦࡢ࡫࡯ࡩࡩ࡚ࡥࡴࡶࡶࠦ᫮"): list(self.bstack11l11llll1l_opy_), bstack111l11_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠥ᫯"): self.config.get(bstack111l11_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫ᫰")), bstack111l11_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡓࡷࡱࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠢ᫱"): os.environ.get(bstack111l11_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡅ࡙ࡎࡒࡄࡠࡔࡘࡒࡤࡏࡄࡆࡐࡗࡍࡋࡏࡅࡓࠩ᫲")), bstack111l11_opy_ (u"ࠦࡵࡸ࡯࡫ࡧࡦࡸࡓࡧ࡭ࡦࠤ᫳"): self.config.get(bstack111l11_opy_ (u"ࠬࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࠪ᫴"))}
            response = bstack11ll1111l1l_opy_.bstack11l11lllll1_opy_(self.bstack11l1l111l11_opy_, data)
            if response.get(bstack111l11_opy_ (u"ࠨࡳࡵࡣࡷࡹࡸࠨ᫵")) == 200:
                self.logger.debug(bstack111l11_opy_ (u"ࠢࡔࡷࡦࡧࡪࡹࡳࡧࡷ࡯ࡰࡾࠦࡳࡦࡰࡷࠤ࡫ࡧࡩ࡭ࡧࡧࠤࡹ࡫ࡳࡵࡵ࠽ࠤࢀࢃࠢ᫶").format(data))
            else:
                self.logger.debug(bstack111l11_opy_ (u"ࠣࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡸ࡫࡮ࡥࠢࡩࡥ࡮ࡲࡥࡥࠢࡷࡩࡸࡺࡳ࠻ࠢࡾࢁࠧ᫷").format(response))
        except Exception as e:
            self.logger.debug(bstack111l11_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡪࡵࡳ࡫ࡱ࡫ࠥࡹࡥ࡯ࡦ࡬ࡲ࡬ࠦࡦࡢ࡫࡯ࡩࡩࠦࡴࡦࡵࡷࡷ࠿ࠦࡻࡾࠤ᫸").format(e))
    def bstack11l1l1111l1_opy_(self):
        if self.bstack11l1l11111l_opy_:
            with self.lock:
                try:
                    with open(self.bstack11l1l11l1l1_opy_, bstack111l11_opy_ (u"ࠥࡶࠧ᫹")) as f:
                        bstack11l1l11lll1_opy_ = set(line.strip() for line in f if line.strip())
                    failed_count = len(bstack11l1l11lll1_opy_)
                except FileNotFoundError:
                    failed_count = 0
                self.logger.debug(bstack111l11_opy_ (u"ࠦࡕࡵ࡬࡭ࡧࡧࠤ࡫ࡧࡩ࡭ࡧࡧࠤࡹ࡫ࡳࡵࡵࠣࡧࡴࡻ࡮ࡵࠢࠫࡰࡴࡩࡡ࡭ࠫ࠽ࠤࢀࢃࠢ᫺").format(failed_count))
                if failed_count >= self.bstack11l1l11l11l_opy_:
                    self.logger.info(bstack111l11_opy_ (u"࡚ࠧࡨࡳࡧࡶ࡬ࡴࡲࡤࠡࡥࡵࡳࡸࡹࡥࡥࠢࠫࡰࡴࡩࡡ࡭ࠫ࠽ࠤࢀࢃࠠ࠿࠿ࠣࡿࢂࠨ᫻").format(failed_count, self.bstack11l1l11l11l_opy_))
                    self.bstack11l1l11l1ll_opy_(failed_count)
                    self.bstack11l1l111ll1_opy_ = True
            return
        try:
            response = bstack11ll1111l1l_opy_.bstack11l1l1111l1_opy_(bstack111l11_opy_ (u"ࠨࡻࡾࡁࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࡂࢁࡽࠧࡤࡸ࡭ࡱࡪࡒࡶࡰࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷࡃࡻࡾࠨࡳࡶࡴࡰࡥࡤࡶࡑࡥࡲ࡫࠽ࡼࡿࠥ᫼").format(self.bstack11l1l111l11_opy_, self.config.get(bstack111l11_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪ᫽")), os.environ.get(bstack111l11_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡃࡗࡌࡐࡉࡥࡒࡖࡐࡢࡍࡉࡋࡎࡕࡋࡉࡍࡊࡘࠧ᫾")), self.config.get(bstack111l11_opy_ (u"ࠩࡳࡶࡴࡰࡥࡤࡶࡑࡥࡲ࡫ࠧ᫿"))))
            if response.get(bstack111l11_opy_ (u"ࠥࡷࡹࡧࡴࡶࡵࠥᬀ")) == 200:
                failed_count = response.get(bstack111l11_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࡘࡪࡹࡴࡴࡅࡲࡹࡳࡺࠢᬁ"), 0)
                self.logger.debug(bstack111l11_opy_ (u"ࠧࡖ࡯࡭࡮ࡨࡨࠥ࡬ࡡࡪ࡮ࡨࡨࠥࡺࡥࡴࡶࡶࠤࡨࡵࡵ࡯ࡶ࠽ࠤࢀࢃࠢᬂ").format(failed_count))
                if failed_count >= self.bstack11l1l11l11l_opy_:
                    self.logger.info(bstack111l11_opy_ (u"ࠨࡔࡩࡴࡨࡷ࡭ࡵ࡬ࡥࠢࡦࡶࡴࡹࡳࡦࡦ࠽ࠤࢀࢃࠠ࠿࠿ࠣࡿࢂࠨᬃ").format(failed_count, self.bstack11l1l11l11l_opy_))
                    self.bstack11l1l11l1ll_opy_(failed_count)
                    self.bstack11l1l111ll1_opy_ = True
            else:
                self.logger.error(bstack111l11_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡴࡴࡲ࡬ࠡࡨࡤ࡭ࡱ࡫ࡤࠡࡶࡨࡷࡹࡹ࠺ࠡࡽࢀࠦᬄ").format(response))
        except Exception as e:
            self.logger.error(bstack111l11_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࡩࡻࡲࡪࡰࡪࠤࡵࡵ࡬࡭࡫ࡱ࡫࠿ࠦࡻࡾࠤᬅ").format(e))
    def bstack11l1l11l1ll_opy_(self, failed_count):
        with open(self.bstack11l1l1l1111_opy_, bstack111l11_opy_ (u"ࠤࡺࠦᬆ")) as f:
            f.write(bstack111l11_opy_ (u"ࠥࡘ࡭ࡸࡥࡴࡪࡲࡰࡩࠦࡣࡳࡱࡶࡷࡪࡪࠠࡢࡶࠣࡿࢂࡢ࡮ࠣᬇ").format(datetime.now()))
            f.write(bstack111l11_opy_ (u"ࠦࡋࡧࡩ࡭ࡧࡧࠤࡹ࡫ࡳࡵࡵࠣࡧࡴࡻ࡮ࡵ࠼ࠣࡿࢂࡢ࡮ࠣᬈ").format(failed_count))
        self.logger.debug(bstack111l11_opy_ (u"ࠧࡇࡢࡰࡴࡷࠤࡇࡻࡩ࡭ࡦࠣࡪ࡮ࡲࡥࠡࡥࡵࡩࡦࡺࡥࡥ࠼ࠣࡿࢂࠨᬉ").format(self.bstack11l1l1l1111_opy_))
    def bstack11l1l11llll_opy_(self):
        def bstack11l1l1l11l1_opy_():
            while not self.bstack11l1l111ll1_opy_:
                time.sleep(bstack11l1l111lll_opy_)
                self.bstack11l1l11ll11_opy_()
                self.bstack11l1l1111l1_opy_()
        bstack11l1l1l111l_opy_ = threading.Thread(target=bstack11l1l1l11l1_opy_, daemon=True)
        bstack11l1l1l111l_opy_.start()