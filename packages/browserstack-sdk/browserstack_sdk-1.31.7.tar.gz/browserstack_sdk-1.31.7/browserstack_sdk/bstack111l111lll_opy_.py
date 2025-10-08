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
class RobotHandler():
    def __init__(self, args, logger, bstack1111l11l11_opy_, bstack11111l1lll_opy_):
        self.args = args
        self.logger = logger
        self.bstack1111l11l11_opy_ = bstack1111l11l11_opy_
        self.bstack11111l1lll_opy_ = bstack11111l1lll_opy_
    @staticmethod
    def version():
        import robot
        return robot.__version__
    @staticmethod
    def bstack111l11lll1_opy_(bstack1111111l11_opy_):
        bstack11111111ll_opy_ = []
        if bstack1111111l11_opy_:
            tokens = str(os.path.basename(bstack1111111l11_opy_)).split(bstack111l11_opy_ (u"ࠤࡢࠦႛ"))
            camelcase_name = bstack111l11_opy_ (u"ࠥࠤࠧႜ").join(t.title() for t in tokens)
            suite_name, bstack1111111ll1_opy_ = os.path.splitext(camelcase_name)
            bstack11111111ll_opy_.append(suite_name)
        return bstack11111111ll_opy_
    @staticmethod
    def bstack1111111l1l_opy_(typename):
        if bstack111l11_opy_ (u"ࠦࡆࡹࡳࡦࡴࡷ࡭ࡴࡴࠢႝ") in typename:
            return bstack111l11_opy_ (u"ࠧࡇࡳࡴࡧࡵࡸ࡮ࡵ࡮ࡆࡴࡵࡳࡷࠨ႞")
        return bstack111l11_opy_ (u"ࠨࡕ࡯ࡪࡤࡲࡩࡲࡥࡥࡇࡵࡶࡴࡸࠢ႟")