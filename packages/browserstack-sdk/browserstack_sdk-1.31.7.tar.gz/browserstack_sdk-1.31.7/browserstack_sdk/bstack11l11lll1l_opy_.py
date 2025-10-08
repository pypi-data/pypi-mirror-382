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
import json
import logging
logger = logging.getLogger(__name__)
class BrowserStackSdk:
    def get_current_platform():
        bstack1l1111llll_opy_ = {}
        bstack111lll1l11_opy_ = os.environ.get(bstack111l11_opy_ (u"ࠧࡄࡗࡕࡖࡊࡔࡔࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡈࡆ࡚ࡁࠨ༑"), bstack111l11_opy_ (u"ࠨࠩ༒"))
        if not bstack111lll1l11_opy_:
            return bstack1l1111llll_opy_
        try:
            bstack111lll1l1l_opy_ = json.loads(bstack111lll1l11_opy_)
            if bstack111l11_opy_ (u"ࠤࡲࡷࠧ༓") in bstack111lll1l1l_opy_:
                bstack1l1111llll_opy_[bstack111l11_opy_ (u"ࠥࡳࡸࠨ༔")] = bstack111lll1l1l_opy_[bstack111l11_opy_ (u"ࠦࡴࡹࠢ༕")]
            if bstack111l11_opy_ (u"ࠧࡵࡳࡠࡸࡨࡶࡸ࡯࡯࡯ࠤ༖") in bstack111lll1l1l_opy_ or bstack111l11_opy_ (u"ࠨ࡯ࡴࡘࡨࡶࡸ࡯࡯࡯ࠤ༗") in bstack111lll1l1l_opy_:
                bstack1l1111llll_opy_[bstack111l11_opy_ (u"ࠢࡰࡵ࡙ࡩࡷࡹࡩࡰࡰ༘ࠥ")] = bstack111lll1l1l_opy_.get(bstack111l11_opy_ (u"ࠣࡱࡶࡣࡻ࡫ࡲࡴ࡫ࡲࡲ༙ࠧ"), bstack111lll1l1l_opy_.get(bstack111l11_opy_ (u"ࠤࡲࡷ࡛࡫ࡲࡴ࡫ࡲࡲࠧ༚")))
            if bstack111l11_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࠦ༛") in bstack111lll1l1l_opy_ or bstack111l11_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠤ༜") in bstack111lll1l1l_opy_:
                bstack1l1111llll_opy_[bstack111l11_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠥ༝")] = bstack111lll1l1l_opy_.get(bstack111l11_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࠢ༞"), bstack111lll1l1l_opy_.get(bstack111l11_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠧ༟")))
            if bstack111l11_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࡡࡹࡩࡷࡹࡩࡰࡰࠥ༠") in bstack111lll1l1l_opy_ or bstack111l11_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠥ༡") in bstack111lll1l1l_opy_:
                bstack1l1111llll_opy_[bstack111l11_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠦ༢")] = bstack111lll1l1l_opy_.get(bstack111l11_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡤࡼࡥࡳࡵ࡬ࡳࡳࠨ༣"), bstack111lll1l1l_opy_.get(bstack111l11_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳࠨ༤")))
            if bstack111l11_opy_ (u"ࠨࡤࡦࡸ࡬ࡧࡪࠨ༥") in bstack111lll1l1l_opy_ or bstack111l11_opy_ (u"ࠢࡥࡧࡹ࡭ࡨ࡫ࡎࡢ࡯ࡨࠦ༦") in bstack111lll1l1l_opy_:
                bstack1l1111llll_opy_[bstack111l11_opy_ (u"ࠣࡦࡨࡺ࡮ࡩࡥࡏࡣࡰࡩࠧ༧")] = bstack111lll1l1l_opy_.get(bstack111l11_opy_ (u"ࠤࡧࡩࡻ࡯ࡣࡦࠤ༨"), bstack111lll1l1l_opy_.get(bstack111l11_opy_ (u"ࠥࡨࡪࡼࡩࡤࡧࡑࡥࡲ࡫ࠢ༩")))
            if bstack111l11_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲࠨ༪") in bstack111lll1l1l_opy_ or bstack111l11_opy_ (u"ࠧࡶ࡬ࡢࡶࡩࡳࡷࡳࡎࡢ࡯ࡨࠦ༫") in bstack111lll1l1l_opy_:
                bstack1l1111llll_opy_[bstack111l11_opy_ (u"ࠨࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡏࡣࡰࡩࠧ༬")] = bstack111lll1l1l_opy_.get(bstack111l11_opy_ (u"ࠢࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࠤ༭"), bstack111lll1l1l_opy_.get(bstack111l11_opy_ (u"ࠣࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡑࡥࡲ࡫ࠢ༮")))
            if bstack111l11_opy_ (u"ࠤࡳࡰࡦࡺࡦࡰࡴࡰࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠧ༯") in bstack111lll1l1l_opy_ or bstack111l11_opy_ (u"ࠥࡴࡱࡧࡴࡧࡱࡵࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠧ༰") in bstack111lll1l1l_opy_:
                bstack1l1111llll_opy_[bstack111l11_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲ࡜ࡥࡳࡵ࡬ࡳࡳࠨ༱")] = bstack111lll1l1l_opy_.get(bstack111l11_opy_ (u"ࠧࡶ࡬ࡢࡶࡩࡳࡷࡳ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠣ༲"), bstack111lll1l1l_opy_.get(bstack111l11_opy_ (u"ࠨࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠣ༳")))
            if bstack111l11_opy_ (u"ࠢࡤࡷࡶࡸࡴࡳࡖࡢࡴ࡬ࡥࡧࡲࡥࡴࠤ༴") in bstack111lll1l1l_opy_:
                bstack1l1111llll_opy_[bstack111l11_opy_ (u"ࠣࡥࡸࡷࡹࡵ࡭ࡗࡣࡵ࡭ࡦࡨ࡬ࡦࡵ༵ࠥ")] = bstack111lll1l1l_opy_[bstack111l11_opy_ (u"ࠤࡦࡹࡸࡺ࡯࡮ࡘࡤࡶ࡮ࡧࡢ࡭ࡧࡶࠦ༶")]
        except Exception as error:
            logger.error(bstack111l11_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡷࡩ࡫࡯ࡩࠥ࡭ࡥࡵࡶ࡬ࡲ࡬ࠦࡣࡶࡴࡵࡩࡳࡺࠠࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࠢࡧࡥࡹࡧ࠺ࠡࠤ༷") +  str(error))
        return bstack1l1111llll_opy_