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
import multiprocessing
import os
from bstack_utils.config import Config
class bstack1ll11lllll_opy_():
  def __init__(self, args, logger, bstack1111l11l11_opy_, bstack11111l1lll_opy_, bstack1111111lll_opy_):
    self.args = args
    self.logger = logger
    self.bstack1111l11l11_opy_ = bstack1111l11l11_opy_
    self.bstack11111l1lll_opy_ = bstack11111l1lll_opy_
    self.bstack1111111lll_opy_ = bstack1111111lll_opy_
  def bstack1llll1111l_opy_(self, bstack11111llll1_opy_, bstack1lllll1l1l_opy_, bstack111111l111_opy_=False):
    bstack1llll1ll1l_opy_ = []
    manager = multiprocessing.Manager()
    bstack11111lllll_opy_ = manager.list()
    bstack1llll1111_opy_ = Config.bstack1lll111l11_opy_()
    if bstack111111l111_opy_:
      for index, platform in enumerate(self.bstack1111l11l11_opy_[bstack111l11_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ႔")]):
        if index == 0:
          bstack1lllll1l1l_opy_[bstack111l11_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭႕")] = self.args
        bstack1llll1ll1l_opy_.append(multiprocessing.Process(name=str(index),
                                                    target=bstack11111llll1_opy_,
                                                    args=(bstack1lllll1l1l_opy_, bstack11111lllll_opy_)))
    else:
      for index, platform in enumerate(self.bstack1111l11l11_opy_[bstack111l11_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ႖")]):
        bstack1llll1ll1l_opy_.append(multiprocessing.Process(name=str(index),
                                                    target=bstack11111llll1_opy_,
                                                    args=(bstack1lllll1l1l_opy_, bstack11111lllll_opy_)))
    i = 0
    for t in bstack1llll1ll1l_opy_:
      try:
        if bstack1llll1111_opy_.get_property(bstack111l11_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡤࡹࡥࡴࡵ࡬ࡳࡳ࠭႗")):
          os.environ[bstack111l11_opy_ (u"࠭ࡃࡖࡔࡕࡉࡓ࡚࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡇࡅ࡙ࡇࠧ႘")] = json.dumps(self.bstack1111l11l11_opy_[bstack111l11_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪ႙")][i % self.bstack1111111lll_opy_])
      except Exception as e:
        self.logger.debug(bstack111l11_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦࡳࡵࡱࡵ࡭ࡳ࡭ࠠࡤࡷࡵࡶࡪࡴࡴࠡࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࠣࡨࡪࡺࡡࡪ࡮ࡶ࠾ࠥࢁࡽࠣႚ").format(str(e)))
      i += 1
      t.start()
    for t in bstack1llll1ll1l_opy_:
      t.join()
    return list(bstack11111lllll_opy_)