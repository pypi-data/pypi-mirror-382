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
from browserstack_sdk.bstack1l1ll1l11l_opy_ import bstack1ll1111l_opy_
from browserstack_sdk.bstack111l111lll_opy_ import RobotHandler
def bstack1ll1l11l1l_opy_(framework):
    if framework.lower() == bstack111l11_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ᬊ"):
        return bstack1ll1111l_opy_.version()
    elif framework.lower() == bstack111l11_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭ᬋ"):
        return RobotHandler.version()
    elif framework.lower() == bstack111l11_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨᬌ"):
        import behave
        return behave.__version__
    else:
        return bstack111l11_opy_ (u"ࠩࡸࡲࡰࡴ࡯ࡸࡰࠪᬍ")
def bstack11ll11llll_opy_():
    import importlib.metadata
    framework_name = []
    framework_version = []
    try:
        from selenium import webdriver
        framework_name.append(bstack111l11_opy_ (u"ࠪࡷࡪࡲࡥ࡯࡫ࡸࡱࠬᬎ"))
        framework_version.append(importlib.metadata.version(bstack111l11_opy_ (u"ࠦࡸ࡫࡬ࡦࡰ࡬ࡹࡲࠨᬏ")))
    except:
        pass
    try:
        import playwright
        framework_name.append(bstack111l11_opy_ (u"ࠬࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠩᬐ"))
        framework_version.append(importlib.metadata.version(bstack111l11_opy_ (u"ࠨࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠥᬑ")))
    except:
        pass
    return {
        bstack111l11_opy_ (u"ࠧ࡯ࡣࡰࡩࠬᬒ"): bstack111l11_opy_ (u"ࠨࡡࠪᬓ").join(framework_name),
        bstack111l11_opy_ (u"ࠩࡹࡩࡷࡹࡩࡰࡰࠪᬔ"): bstack111l11_opy_ (u"ࠪࡣࠬᬕ").join(framework_version)
    }