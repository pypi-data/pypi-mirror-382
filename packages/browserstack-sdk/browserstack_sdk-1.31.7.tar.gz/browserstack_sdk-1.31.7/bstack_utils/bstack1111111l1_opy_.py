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
import re
from bstack_utils.bstack1ll1l1ll11_opy_ import bstack1lllllll111l_opy_
def bstack1lllllll1lll_opy_(fixture_name):
    if fixture_name.startswith(bstack111l11_opy_ (u"ࠫࡤࡾࡵ࡯࡫ࡷࡣࡸ࡫ࡴࡶࡲࡢࡪࡺࡴࡣࡵ࡫ࡲࡲࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭ὶ")):
        return bstack111l11_opy_ (u"ࠬࡹࡥࡵࡷࡳ࠱࡫ࡻ࡮ࡤࡶ࡬ࡳࡳ࠭ί")
    elif fixture_name.startswith(bstack111l11_opy_ (u"࠭࡟ࡹࡷࡱ࡭ࡹࡥࡳࡦࡶࡸࡴࡤࡳ࡯ࡥࡷ࡯ࡩࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭ὸ")):
        return bstack111l11_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠳࡭ࡰࡦࡸࡰࡪ࠭ό")
    elif fixture_name.startswith(bstack111l11_opy_ (u"ࠨࡡࡻࡹࡳ࡯ࡴࡠࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡪࡺࡴࡣࡵ࡫ࡲࡲࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭ὺ")):
        return bstack111l11_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱ࠱࡫ࡻ࡮ࡤࡶ࡬ࡳࡳ࠭ύ")
    elif fixture_name.startswith(bstack111l11_opy_ (u"ࠪࡣࡽࡻ࡮ࡪࡶࡢࡸࡪࡧࡲࡥࡱࡺࡲࡤ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨὼ")):
        return bstack111l11_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳ࠳࡭ࡰࡦࡸࡰࡪ࠭ώ")
def bstack1lllllll1ll1_opy_(fixture_name):
    return bool(re.match(bstack111l11_opy_ (u"ࠬࡤ࡟ࡹࡷࡱ࡭ࡹࡥࠨࡴࡧࡷࡹࡵࢂࡴࡦࡣࡵࡨࡴࡽ࡮ࠪࡡࠫࡪࡺࡴࡣࡵ࡫ࡲࡲࢁࡳ࡯ࡥࡷ࡯ࡩ࠮ࡥࡦࡪࡺࡷࡹࡷ࡫࡟࠯ࠬࠪ὾"), fixture_name))
def bstack1lllllll1l1l_opy_(fixture_name):
    return bool(re.match(bstack111l11_opy_ (u"࠭࡞ࡠࡺࡸࡲ࡮ࡺ࡟ࠩࡵࡨࡸࡺࡶࡼࡵࡧࡤࡶࡩࡵࡷ࡯ࠫࡢࡱࡴࡪࡵ࡭ࡧࡢࡪ࡮ࡾࡴࡶࡴࡨࡣ࠳࠰ࠧ὿"), fixture_name))
def bstack1llllllll1ll_opy_(fixture_name):
    return bool(re.match(bstack111l11_opy_ (u"ࠧ࡟ࡡࡻࡹࡳ࡯ࡴࡠࠪࡶࡩࡹࡻࡰࡽࡶࡨࡥࡷࡪ࡯ࡸࡰࠬࡣࡨࡲࡡࡴࡵࡢࡪ࡮ࡾࡴࡶࡴࡨࡣ࠳࠰ࠧᾀ"), fixture_name))
def bstack1llllllll1l1_opy_(fixture_name):
    if fixture_name.startswith(bstack111l11_opy_ (u"ࠨࡡࡻࡹࡳ࡯ࡴࡠࡵࡨࡸࡺࡶ࡟ࡧࡷࡱࡧࡹ࡯࡯࡯ࡡࡩ࡭ࡽࡺࡵࡳࡧࠪᾁ")):
        return bstack111l11_opy_ (u"ࠩࡶࡩࡹࡻࡰ࠮ࡨࡸࡲࡨࡺࡩࡰࡰࠪᾂ"), bstack111l11_opy_ (u"ࠪࡆࡊࡌࡏࡓࡇࡢࡉࡆࡉࡈࠨᾃ")
    elif fixture_name.startswith(bstack111l11_opy_ (u"ࠫࡤࡾࡵ࡯࡫ࡷࡣࡸ࡫ࡴࡶࡲࡢࡱࡴࡪࡵ࡭ࡧࡢࡪ࡮ࡾࡴࡶࡴࡨࠫᾄ")):
        return bstack111l11_opy_ (u"ࠬࡹࡥࡵࡷࡳ࠱ࡲࡵࡤࡶ࡮ࡨࠫᾅ"), bstack111l11_opy_ (u"࠭ࡂࡆࡈࡒࡖࡊࡥࡁࡍࡎࠪᾆ")
    elif fixture_name.startswith(bstack111l11_opy_ (u"ࠧࡠࡺࡸࡲ࡮ࡺ࡟ࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡩࡹࡳࡩࡴࡪࡱࡱࡣ࡫࡯ࡸࡵࡷࡵࡩࠬᾇ")):
        return bstack111l11_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰ࠰ࡪࡺࡴࡣࡵ࡫ࡲࡲࠬᾈ"), bstack111l11_opy_ (u"ࠩࡄࡊ࡙ࡋࡒࡠࡇࡄࡇࡍ࠭ᾉ")
    elif fixture_name.startswith(bstack111l11_opy_ (u"ࠪࡣࡽࡻ࡮ࡪࡶࡢࡸࡪࡧࡲࡥࡱࡺࡲࡤࡳ࡯ࡥࡷ࡯ࡩࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭ᾊ")):
        return bstack111l11_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳ࠳࡭ࡰࡦࡸࡰࡪ࠭ᾋ"), bstack111l11_opy_ (u"ࠬࡇࡆࡕࡇࡕࡣࡆࡒࡌࠨᾌ")
    return None, None
def bstack1lllllll1l11_opy_(hook_name):
    if hook_name in [bstack111l11_opy_ (u"࠭ࡳࡦࡶࡸࡴࠬᾍ"), bstack111l11_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࠩᾎ")]:
        return hook_name.capitalize()
    return hook_name
def bstack1llllllll11l_opy_(hook_name):
    if hook_name in [bstack111l11_opy_ (u"ࠨࡵࡨࡸࡺࡶ࡟ࡧࡷࡱࡧࡹ࡯࡯࡯ࠩᾏ"), bstack111l11_opy_ (u"ࠩࡶࡩࡹࡻࡰࡠ࡯ࡨࡸ࡭ࡵࡤࠨᾐ")]:
        return bstack111l11_opy_ (u"ࠪࡆࡊࡌࡏࡓࡇࡢࡉࡆࡉࡈࠨᾑ")
    elif hook_name in [bstack111l11_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࡢࡱࡴࡪࡵ࡭ࡧࠪᾒ"), bstack111l11_opy_ (u"ࠬࡹࡥࡵࡷࡳࡣࡨࡲࡡࡴࡵࠪᾓ")]:
        return bstack111l11_opy_ (u"࠭ࡂࡆࡈࡒࡖࡊࡥࡁࡍࡎࠪᾔ")
    elif hook_name in [bstack111l11_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡩࡹࡳࡩࡴࡪࡱࡱࠫᾕ"), bstack111l11_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡱࡪࡺࡨࡰࡦࠪᾖ")]:
        return bstack111l11_opy_ (u"ࠩࡄࡊ࡙ࡋࡒࡠࡇࡄࡇࡍ࠭ᾗ")
    elif hook_name in [bstack111l11_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࡤࡳ࡯ࡥࡷ࡯ࡩࠬᾘ"), bstack111l11_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳࡥࡣ࡭ࡣࡶࡷࠬᾙ")]:
        return bstack111l11_opy_ (u"ࠬࡇࡆࡕࡇࡕࡣࡆࡒࡌࠨᾚ")
    return hook_name
def bstack1lllllll11ll_opy_(node, scenario):
    if hasattr(node, bstack111l11_opy_ (u"࠭ࡣࡢ࡮࡯ࡷࡵ࡫ࡣࠨᾛ")):
        parts = node.nodeid.rsplit(bstack111l11_opy_ (u"ࠢ࡜ࠤᾜ"))
        params = parts[-1]
        return bstack111l11_opy_ (u"ࠣࡽࢀࠤࡠࢁࡽࠣᾝ").format(scenario.name, params)
    return scenario.name
def bstack1lllllllll1l_opy_(node):
    try:
        examples = []
        if hasattr(node, bstack111l11_opy_ (u"ࠩࡦࡥࡱࡲࡳࡱࡧࡦࠫᾞ")):
            examples = list(node.callspec.params[bstack111l11_opy_ (u"ࠪࡣࡵࡿࡴࡦࡵࡷࡣࡧࡪࡤࡠࡧࡻࡥࡲࡶ࡬ࡦࠩᾟ")].values())
        return examples
    except:
        return []
def bstack1lllllll11l1_opy_(feature, scenario):
    return list(feature.tags) + list(scenario.tags)
def bstack1lllllllll11_opy_(report):
    try:
        status = bstack111l11_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫᾠ")
        if report.passed or (report.failed and hasattr(report, bstack111l11_opy_ (u"ࠧࡽࡡࡴࡺࡩࡥ࡮ࡲࠢᾡ"))):
            status = bstack111l11_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭ᾢ")
        elif report.skipped:
            status = bstack111l11_opy_ (u"ࠧࡴ࡭࡬ࡴࡵ࡫ࡤࠨᾣ")
        bstack1lllllll111l_opy_(status)
    except:
        pass
def bstack11111111l_opy_(status):
    try:
        bstack1lllllll1111_opy_ = bstack111l11_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨᾤ")
        if status == bstack111l11_opy_ (u"ࠩࡳࡥࡸࡹࡥࡥࠩᾥ"):
            bstack1lllllll1111_opy_ = bstack111l11_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪᾦ")
        elif status == bstack111l11_opy_ (u"ࠫࡸࡱࡩࡱࡲࡨࡨࠬᾧ"):
            bstack1lllllll1111_opy_ = bstack111l11_opy_ (u"ࠬࡹ࡫ࡪࡲࡳࡩࡩ࠭ᾨ")
        bstack1lllllll111l_opy_(bstack1lllllll1111_opy_)
    except:
        pass
def bstack1llllllll111_opy_(item=None, report=None, summary=None, extra=None):
    return