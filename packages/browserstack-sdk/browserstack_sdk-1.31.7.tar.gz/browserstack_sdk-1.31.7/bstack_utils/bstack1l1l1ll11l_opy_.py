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
from bstack_utils.constants import bstack11ll111ll1l_opy_
def bstack11l1l11l1l_opy_(bstack11ll111lll1_opy_):
    from browserstack_sdk.sdk_cli.cli import cli
    from bstack_utils.helper import bstack1l1ll1lll1_opy_
    host = bstack1l1ll1lll1_opy_(cli.config, [bstack111l11_opy_ (u"ࠦࡦࡶࡩࡴࠤខ"), bstack111l11_opy_ (u"ࠧࡧࡵࡵࡱࡰࡥࡹ࡫ࠢគ"), bstack111l11_opy_ (u"ࠨࡡࡱ࡫ࠥឃ")], bstack11ll111ll1l_opy_)
    return bstack111l11_opy_ (u"ࠧࡼࡿ࠲ࡿࢂ࠭ង").format(host, bstack11ll111lll1_opy_)