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
import os
import threading
from bstack_utils.config import Config
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.helper import bstack11l11llll11_opy_, bstack11ll1lll_opy_, bstack1l11lllll1_opy_, bstack1ll1l1l111_opy_, \
    bstack11l11l1lll1_opy_
from bstack_utils.measure import measure
def bstack11llll1ll_opy_(bstack1lllll1l1lll_opy_):
    for driver in bstack1lllll1l1lll_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
@measure(event_name=EVENTS.bstack1ll1ll1l_opy_, stage=STAGE.bstack111lllll1_opy_)
def bstack1l1l1l1l1l_opy_(driver, status, reason=bstack111l11_opy_ (u"ࠫࠬΏ")):
    bstack1llll1111_opy_ = Config.bstack1lll111l11_opy_()
    if bstack1llll1111_opy_.bstack11111ll1l1_opy_():
        return
    bstack1lllll111l_opy_ = bstack11llllll_opy_(bstack111l11_opy_ (u"ࠬࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡕࡷࡥࡹࡻࡳࠨῼ"), bstack111l11_opy_ (u"࠭ࠧ´"), status, reason, bstack111l11_opy_ (u"ࠧࠨ῾"), bstack111l11_opy_ (u"ࠨࠩ῿"))
    driver.execute_script(bstack1lllll111l_opy_)
@measure(event_name=EVENTS.bstack1ll1ll1l_opy_, stage=STAGE.bstack111lllll1_opy_)
def bstack111111l1l_opy_(page, status, reason=bstack111l11_opy_ (u"ࠩࠪ ")):
    try:
        if page is None:
            return
        bstack1llll1111_opy_ = Config.bstack1lll111l11_opy_()
        if bstack1llll1111_opy_.bstack11111ll1l1_opy_():
            return
        bstack1lllll111l_opy_ = bstack11llllll_opy_(bstack111l11_opy_ (u"ࠪࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡓࡵࡣࡷࡹࡸ࠭ "), bstack111l11_opy_ (u"ࠫࠬ "), status, reason, bstack111l11_opy_ (u"ࠬ࠭ "), bstack111l11_opy_ (u"࠭ࠧ "))
        page.evaluate(bstack111l11_opy_ (u"ࠢࡠࠢࡀࡂࠥࢁࡽࠣ "), bstack1lllll111l_opy_)
    except Exception as e:
        print(bstack111l11_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡴࡧࡷࡸ࡮ࡴࡧࠡࡵࡨࡷࡸ࡯࡯࡯ࠢࡶࡸࡦࡺࡵࡴࠢࡩࡳࡷࠦࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠣࡿࢂࠨ "), e)
def bstack11llllll_opy_(type, name, status, reason, bstack1l11l11111_opy_, bstack1l11llll11_opy_):
    bstack11llll11_opy_ = {
        bstack111l11_opy_ (u"ࠩࡤࡧࡹ࡯࡯࡯ࠩ "): type,
        bstack111l11_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭ "): {}
    }
    if type == bstack111l11_opy_ (u"ࠫࡦࡴ࡮ࡰࡶࡤࡸࡪ࠭ "):
        bstack11llll11_opy_[bstack111l11_opy_ (u"ࠬࡧࡲࡨࡷࡰࡩࡳࡺࡳࠨ ")][bstack111l11_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬ​")] = bstack1l11l11111_opy_
        bstack11llll11_opy_[bstack111l11_opy_ (u"ࠧࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠪ‌")][bstack111l11_opy_ (u"ࠨࡦࡤࡸࡦ࠭‍")] = json.dumps(str(bstack1l11llll11_opy_))
    if type == bstack111l11_opy_ (u"ࠩࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ‎"):
        bstack11llll11_opy_[bstack111l11_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭‏")][bstack111l11_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ‐")] = name
    if type == bstack111l11_opy_ (u"ࠬࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡕࡷࡥࡹࡻࡳࠨ‑"):
        bstack11llll11_opy_[bstack111l11_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩ‒")][bstack111l11_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧ–")] = status
        if status == bstack111l11_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨ—") and str(reason) != bstack111l11_opy_ (u"ࠤࠥ―"):
            bstack11llll11_opy_[bstack111l11_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭‖")][bstack111l11_opy_ (u"ࠫࡷ࡫ࡡࡴࡱࡱࠫ‗")] = json.dumps(str(reason))
    bstack11l1111ll1_opy_ = bstack111l11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࡿࠪ‘").format(json.dumps(bstack11llll11_opy_))
    return bstack11l1111ll1_opy_
def bstack11l1l1l1ll_opy_(url, config, logger, bstack1ll1l1ll1l_opy_=False):
    hostname = bstack11ll1lll_opy_(url)
    is_private = bstack1ll1l1l111_opy_(hostname)
    try:
        if is_private or bstack1ll1l1ll1l_opy_:
            file_path = bstack11l11llll11_opy_(bstack111l11_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭’"), bstack111l11_opy_ (u"ࠧ࠯ࡤࡶࡸࡦࡩ࡫࠮ࡥࡲࡲ࡫࡯ࡧ࠯࡬ࡶࡳࡳ࠭‚"), logger)
            if os.environ.get(bstack111l11_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡍࡑࡆࡅࡑࡥࡎࡐࡖࡢࡗࡊ࡚࡟ࡆࡔࡕࡓࡗ࠭‛")) and eval(
                    os.environ.get(bstack111l11_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡎࡒࡇࡆࡒ࡟ࡏࡑࡗࡣࡘࡋࡔࡠࡇࡕࡖࡔࡘࠧ“"))):
                return
            if (bstack111l11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧ”") in config and not config[bstack111l11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨ„")]):
                os.environ[bstack111l11_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡑࡕࡃࡂࡎࡢࡒࡔ࡚࡟ࡔࡇࡗࡣࡊࡘࡒࡐࡔࠪ‟")] = str(True)
                bstack1lllll1l1l1l_opy_ = {bstack111l11_opy_ (u"࠭ࡨࡰࡵࡷࡲࡦࡳࡥࠨ†"): hostname}
                bstack11l11l1lll1_opy_(bstack111l11_opy_ (u"ࠧ࠯ࡤࡶࡸࡦࡩ࡫࠮ࡥࡲࡲ࡫࡯ࡧ࠯࡬ࡶࡳࡳ࠭‡"), bstack111l11_opy_ (u"ࠨࡰࡸࡨ࡬࡫࡟࡭ࡱࡦࡥࡱ࠭•"), bstack1lllll1l1l1l_opy_, logger)
    except Exception as e:
        pass
def bstack1111111l_opy_(caps, bstack1lllll1l1ll1_opy_):
    if bstack111l11_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪ‣") in caps:
        caps[bstack111l11_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫ․")][bstack111l11_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࠪ‥")] = True
        if bstack1lllll1l1ll1_opy_:
            caps[bstack111l11_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࠿ࡵࡰࡵ࡫ࡲࡲࡸ࠭…")][bstack111l11_opy_ (u"࠭࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ‧")] = bstack1lllll1l1ll1_opy_
    else:
        caps[bstack111l11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴࡬ࡰࡥࡤࡰࠬ ")] = True
        if bstack1lllll1l1ll1_opy_:
            caps[bstack111l11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮࡭ࡱࡦࡥࡱࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ ")] = bstack1lllll1l1ll1_opy_
def bstack1lllllll111l_opy_(bstack111l111l11_opy_):
    bstack1lllll1l1l11_opy_ = bstack1l11lllll1_opy_(threading.current_thread(), bstack111l11_opy_ (u"ࠩࡷࡩࡸࡺࡓࡵࡣࡷࡹࡸ࠭‪"), bstack111l11_opy_ (u"ࠪࠫ‫"))
    if bstack1lllll1l1l11_opy_ == bstack111l11_opy_ (u"ࠫࠬ‬") or bstack1lllll1l1l11_opy_ == bstack111l11_opy_ (u"ࠬࡹ࡫ࡪࡲࡳࡩࡩ࠭‭"):
        threading.current_thread().testStatus = bstack111l111l11_opy_
    else:
        if bstack111l111l11_opy_ == bstack111l11_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭‮"):
            threading.current_thread().testStatus = bstack111l111l11_opy_