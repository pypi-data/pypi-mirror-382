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
from urllib.parse import urlparse
from bstack_utils.config import Config
from bstack_utils.messages import bstack111l1l11111_opy_
bstack1llll1111_opy_ = Config.bstack1lll111l11_opy_()
def bstack1111111111l_opy_(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
def bstack11111111l11_opy_(bstack1lllllllllll_opy_, bstack111111111l1_opy_):
    from pypac import get_pac
    from pypac import PACSession
    from pypac.parser import PACFile
    import socket
    if os.path.isfile(bstack1lllllllllll_opy_):
        with open(bstack1lllllllllll_opy_) as f:
            pac = PACFile(f.read())
    elif bstack1111111111l_opy_(bstack1lllllllllll_opy_):
        pac = get_pac(url=bstack1lllllllllll_opy_)
    else:
        raise Exception(bstack111l11_opy_ (u"ࠨࡒࡤࡧࠥ࡬ࡩ࡭ࡧࠣࡨࡴ࡫ࡳࠡࡰࡲࡸࠥ࡫ࡸࡪࡵࡷ࠾ࠥࢁࡽࠨὐ").format(bstack1lllllllllll_opy_))
    session = PACSession(pac)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((bstack111l11_opy_ (u"ࠤ࠻࠲࠽࠴࠸࠯࠺ࠥὑ"), 80))
        bstack1llllllllll1_opy_ = s.getsockname()[0]
        s.close()
    except:
        bstack1llllllllll1_opy_ = bstack111l11_opy_ (u"ࠪ࠴࠳࠶࠮࠱࠰࠳ࠫὒ")
    proxy_url = session.get_pac().find_proxy_for_url(bstack111111111l1_opy_, bstack1llllllllll1_opy_)
    return proxy_url
def bstack1l11111111_opy_(config):
    return bstack111l11_opy_ (u"ࠫ࡭ࡺࡴࡱࡒࡵࡳࡽࡿࠧὓ") in config or bstack111l11_opy_ (u"ࠬ࡮ࡴࡵࡲࡶࡔࡷࡵࡸࡺࠩὔ") in config
def bstack1l11l11l_opy_(config):
    if not bstack1l11111111_opy_(config):
        return
    if config.get(bstack111l11_opy_ (u"࠭ࡨࡵࡶࡳࡔࡷࡵࡸࡺࠩὕ")):
        return config.get(bstack111l11_opy_ (u"ࠧࡩࡶࡷࡴࡕࡸ࡯ࡹࡻࠪὖ"))
    if config.get(bstack111l11_opy_ (u"ࠨࡪࡷࡸࡵࡹࡐࡳࡱࡻࡽࠬὗ")):
        return config.get(bstack111l11_opy_ (u"ࠩ࡫ࡸࡹࡶࡳࡑࡴࡲࡼࡾ࠭὘"))
def bstack111lllll11_opy_(config, bstack111111111l1_opy_):
    proxy = bstack1l11l11l_opy_(config)
    proxies = {}
    if config.get(bstack111l11_opy_ (u"ࠪ࡬ࡹࡺࡰࡑࡴࡲࡼࡾ࠭Ὑ")) or config.get(bstack111l11_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨ὚")):
        if proxy.endswith(bstack111l11_opy_ (u"ࠬ࠴ࡰࡢࡥࠪὛ")):
            proxies = bstack111ll11l1_opy_(proxy, bstack111111111l1_opy_)
        else:
            proxies = {
                bstack111l11_opy_ (u"࠭ࡨࡵࡶࡳࡷࠬ὜"): proxy
            }
    bstack1llll1111_opy_.bstack1l1l1l1lll_opy_(bstack111l11_opy_ (u"ࠧࡱࡴࡲࡼࡾ࡙ࡥࡵࡶ࡬ࡲ࡬ࡹࠧὝ"), proxies)
    return proxies
def bstack111ll11l1_opy_(bstack1lllllllllll_opy_, bstack111111111l1_opy_):
    proxies = {}
    global bstack11111111111_opy_
    if bstack111l11_opy_ (u"ࠨࡒࡄࡇࡤࡖࡒࡐ࡚࡜ࠫ὞") in globals():
        return bstack11111111111_opy_
    try:
        proxy = bstack11111111l11_opy_(bstack1lllllllllll_opy_, bstack111111111l1_opy_)
        if bstack111l11_opy_ (u"ࠤࡇࡍࡗࡋࡃࡕࠤὟ") in proxy:
            proxies = {}
        elif bstack111l11_opy_ (u"ࠥࡌ࡙࡚ࡐࠣὠ") in proxy or bstack111l11_opy_ (u"ࠦࡍ࡚ࡔࡑࡕࠥὡ") in proxy or bstack111l11_opy_ (u"࡙ࠧࡏࡄࡍࡖࠦὢ") in proxy:
            bstack111111111ll_opy_ = proxy.split(bstack111l11_opy_ (u"ࠨࠠࠣὣ"))
            if bstack111l11_opy_ (u"ࠢ࠻࠱࠲ࠦὤ") in bstack111l11_opy_ (u"ࠣࠤὥ").join(bstack111111111ll_opy_[1:]):
                proxies = {
                    bstack111l11_opy_ (u"ࠩ࡫ࡸࡹࡶࡳࠨὦ"): bstack111l11_opy_ (u"ࠥࠦὧ").join(bstack111111111ll_opy_[1:])
                }
            else:
                proxies = {
                    bstack111l11_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࠪὨ"): str(bstack111111111ll_opy_[0]).lower() + bstack111l11_opy_ (u"ࠧࡀ࠯࠰ࠤὩ") + bstack111l11_opy_ (u"ࠨࠢὪ").join(bstack111111111ll_opy_[1:])
                }
        elif bstack111l11_opy_ (u"ࠢࡑࡔࡒ࡜࡞ࠨὫ") in proxy:
            bstack111111111ll_opy_ = proxy.split(bstack111l11_opy_ (u"ࠣࠢࠥὬ"))
            if bstack111l11_opy_ (u"ࠤ࠽࠳࠴ࠨὭ") in bstack111l11_opy_ (u"ࠥࠦὮ").join(bstack111111111ll_opy_[1:]):
                proxies = {
                    bstack111l11_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࠪὯ"): bstack111l11_opy_ (u"ࠧࠨὰ").join(bstack111111111ll_opy_[1:])
                }
            else:
                proxies = {
                    bstack111l11_opy_ (u"࠭ࡨࡵࡶࡳࡷࠬά"): bstack111l11_opy_ (u"ࠢࡩࡶࡷࡴ࠿࠵࠯ࠣὲ") + bstack111l11_opy_ (u"ࠣࠤέ").join(bstack111111111ll_opy_[1:])
                }
        else:
            proxies = {
                bstack111l11_opy_ (u"ࠩ࡫ࡸࡹࡶࡳࠨὴ"): proxy
            }
    except Exception as e:
        print(bstack111l11_opy_ (u"ࠥࡷࡴࡳࡥࠡࡧࡵࡶࡴࡸࠢή"), bstack111l1l11111_opy_.format(bstack1lllllllllll_opy_, str(e)))
    bstack11111111111_opy_ = proxies
    return proxies