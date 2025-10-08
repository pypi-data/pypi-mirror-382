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
import logging
import bstack_utils.accessibility as bstack1l1l111l1l_opy_
from bstack_utils.helper import bstack1l11lllll1_opy_
logger = logging.getLogger(__name__)
def bstack1lll11l1l1_opy_(bstack1ll1ll11l_opy_):
  return True if bstack1ll1ll11l_opy_ in threading.current_thread().__dict__.keys() else False
def bstack1ll1l1l11_opy_(context, *args):
    tags = getattr(args[0], bstack111l11_opy_ (u"ࠫࡹࡧࡧࡴࠩត"), [])
    bstack111lll1ll1_opy_ = bstack1l1l111l1l_opy_.bstack11l1l1ll11_opy_(tags)
    threading.current_thread().isA11yTest = bstack111lll1ll1_opy_
    try:
      bstack111l11111_opy_ = threading.current_thread().bstackSessionDriver if bstack1lll11l1l1_opy_(bstack111l11_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡘ࡫ࡳࡴ࡫ࡲࡲࡉࡸࡩࡷࡧࡵࠫថ")) else context.browser
      if bstack111l11111_opy_ and bstack111l11111_opy_.session_id and bstack111lll1ll1_opy_ and bstack1l11lllll1_opy_(
              threading.current_thread(), bstack111l11_opy_ (u"࠭ࡡ࠲࠳ࡼࡔࡱࡧࡴࡧࡱࡵࡱࠬទ"), None):
          threading.current_thread().isA11yTest = bstack1l1l111l1l_opy_.bstack1lllll1ll_opy_(bstack111l11111_opy_, bstack111lll1ll1_opy_)
    except Exception as e:
       logger.debug(bstack111l11_opy_ (u"ࠧࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡹࡧࡲࡵࠢࡤ࠵࠶ࡿࠠࡪࡰࠣࡦࡪ࡮ࡡࡷࡧ࠽ࠤࢀࢃࠧធ").format(str(e)))
def bstack1ll1l11l1_opy_(bstack111l11111_opy_):
    if bstack1l11lllll1_opy_(threading.current_thread(), bstack111l11_opy_ (u"ࠨ࡫ࡶࡅ࠶࠷ࡹࡕࡧࡶࡸࠬន"), None) and bstack1l11lllll1_opy_(
      threading.current_thread(), bstack111l11_opy_ (u"ࠩࡤ࠵࠶ࡿࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨប"), None) and not bstack1l11lllll1_opy_(threading.current_thread(), bstack111l11_opy_ (u"ࠪࡥ࠶࠷ࡹࡠࡵࡷࡳࡵ࠭ផ"), False):
      threading.current_thread().a11y_stop = True
      bstack1l1l111l1l_opy_.bstack111l1lll_opy_(bstack111l11111_opy_, name=bstack111l11_opy_ (u"ࠦࠧព"), path=bstack111l11_opy_ (u"ࠧࠨភ"))