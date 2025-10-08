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
class bstack11l111ll1_opy_:
    def __init__(self, handler):
        self._1lllll1ll1ll_opy_ = None
        self.handler = handler
        self._1lllll1ll11l_opy_ = self.bstack1lllll1ll111_opy_()
        self.patch()
    def patch(self):
        self._1lllll1ll1ll_opy_ = self._1lllll1ll11l_opy_.execute
        self._1lllll1ll11l_opy_.execute = self.bstack1lllll1ll1l1_opy_()
    def bstack1lllll1ll1l1_opy_(self):
        def execute(this, driver_command, *args, **kwargs):
            self.handler(bstack111l11_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࠤΌ"), driver_command, None, this, args)
            response = self._1lllll1ll1ll_opy_(this, driver_command, *args, **kwargs)
            self.handler(bstack111l11_opy_ (u"ࠥࡥ࡫ࡺࡥࡳࠤῺ"), driver_command, response)
            return response
        return execute
    def reset(self):
        self._1lllll1ll11l_opy_.execute = self._1lllll1ll1ll_opy_
    @staticmethod
    def bstack1lllll1ll111_opy_():
        from selenium.webdriver.remote.webdriver import WebDriver
        return WebDriver