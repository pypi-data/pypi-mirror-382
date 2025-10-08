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
import requests
from urllib.parse import urljoin, urlencode
from datetime import datetime
import os
import logging
import json
from bstack_utils.constants import bstack11l1l1lllll_opy_
logger = logging.getLogger(__name__)
class bstack11ll1111l1l_opy_:
    @staticmethod
    def results(builder,params=None):
        bstack1lllll1llll1_opy_ = urljoin(builder, bstack111l11_opy_ (u"ࠫ࡮ࡹࡳࡶࡧࡶࠫᾮ"))
        if params:
            bstack1lllll1llll1_opy_ += bstack111l11_opy_ (u"ࠧࡅࡻࡾࠤᾯ").format(urlencode({bstack111l11_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭ᾰ"): params.get(bstack111l11_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧᾱ"))}))
        return bstack11ll1111l1l_opy_.bstack1llllll111l1_opy_(bstack1lllll1llll1_opy_)
    @staticmethod
    def bstack11ll111l1ll_opy_(builder,params=None):
        bstack1lllll1llll1_opy_ = urljoin(builder, bstack111l11_opy_ (u"ࠨ࡫ࡶࡷࡺ࡫ࡳ࠮ࡵࡸࡱࡲࡧࡲࡺࠩᾲ"))
        if params:
            bstack1lllll1llll1_opy_ += bstack111l11_opy_ (u"ࠤࡂࡿࢂࠨᾳ").format(urlencode({bstack111l11_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪᾴ"): params.get(bstack111l11_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ᾵"))}))
        return bstack11ll1111l1l_opy_.bstack1llllll111l1_opy_(bstack1lllll1llll1_opy_)
    @staticmethod
    def bstack1llllll111l1_opy_(bstack1llllll111ll_opy_):
        bstack1llllll11111_opy_ = os.environ.get(bstack111l11_opy_ (u"ࠬࡈࡓࡠࡃ࠴࠵࡞ࡥࡊࡘࡖࠪᾶ"), os.environ.get(bstack111l11_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪᾷ"), bstack111l11_opy_ (u"ࠧࠨᾸ")))
        headers = {bstack111l11_opy_ (u"ࠨࡃࡸࡸ࡭ࡵࡲࡪࡼࡤࡸ࡮ࡵ࡮ࠨᾹ"): bstack111l11_opy_ (u"ࠩࡅࡩࡦࡸࡥࡳࠢࡾࢁࠬᾺ").format(bstack1llllll11111_opy_)}
        response = requests.get(bstack1llllll111ll_opy_, headers=headers)
        bstack1lllll1lll1l_opy_ = {}
        try:
            bstack1lllll1lll1l_opy_ = response.json()
        except Exception as e:
            logger.debug(bstack111l11_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡰࡢࡴࡶࡩࠥࡐࡓࡐࡐࠣࡶࡪࡹࡰࡰࡰࡶࡩ࠿ࠦࡻࡾࠤΆ").format(e))
            pass
        if bstack1lllll1lll1l_opy_ is not None:
            bstack1lllll1lll1l_opy_[bstack111l11_opy_ (u"ࠫࡳ࡫ࡸࡵࡡࡳࡳࡱࡲ࡟ࡵ࡫ࡰࡩࠬᾼ")] = response.headers.get(bstack111l11_opy_ (u"ࠬࡴࡥࡹࡶࡢࡴࡴࡲ࡬ࡠࡶ࡬ࡱࡪ࠭᾽"), str(int(datetime.now().timestamp() * 1000)))
            bstack1lllll1lll1l_opy_[bstack111l11_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭ι")] = response.status_code
        return bstack1lllll1lll1l_opy_
    @staticmethod
    def bstack1lllll1lllll_opy_(bstack1lllll1lll11_opy_, data):
        logger.debug(bstack111l11_opy_ (u"ࠢࡑࡴࡲࡧࡪࡹࡳࡪࡰࡪࠤࡗ࡫ࡱࡶࡧࡶࡸࠥ࡬࡯ࡳࠢࡷࡩࡸࡺࡏࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳ࡙ࡰ࡭࡫ࡷࡘࡪࡹࡴࡴࠤ᾿"))
        return bstack11ll1111l1l_opy_.bstack1llllll1111l_opy_(bstack111l11_opy_ (u"ࠨࡒࡒࡗ࡙࠭῀"), bstack1lllll1lll11_opy_, data=data)
    @staticmethod
    def bstack1llllll11l11_opy_(bstack1lllll1lll11_opy_, data):
        logger.debug(bstack111l11_opy_ (u"ࠤࡓࡶࡴࡩࡥࡴࡵ࡬ࡲ࡬ࠦࡒࡦࡳࡸࡩࡸࡺࠠࡧࡱࡵࠤ࡬࡫ࡴࡕࡧࡶࡸࡔࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࡓࡷࡪࡥࡳࡧࡧࡘࡪࡹࡴࡴࠤ῁"))
        res = bstack11ll1111l1l_opy_.bstack1llllll1111l_opy_(bstack111l11_opy_ (u"ࠪࡋࡊ࡚ࠧῂ"), bstack1lllll1lll11_opy_, data=data)
        return res
    @staticmethod
    def bstack1llllll1111l_opy_(method, bstack1lllll1lll11_opy_, data=None, params=None, extra_headers=None):
        bstack1llllll11111_opy_ = os.environ.get(bstack111l11_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣࡏ࡝ࡔࠨῃ"), bstack111l11_opy_ (u"ࠬ࠭ῄ"))
        headers = {
            bstack111l11_opy_ (u"࠭ࡡࡶࡶ࡫ࡳࡷ࡯ࡺࡢࡶ࡬ࡳࡳ࠭῅"): bstack111l11_opy_ (u"ࠧࡃࡧࡤࡶࡪࡸࠠࡼࡿࠪῆ").format(bstack1llllll11111_opy_),
            bstack111l11_opy_ (u"ࠨࡅࡲࡲࡹ࡫࡮ࡵ࠯ࡗࡽࡵ࡫ࠧῇ"): bstack111l11_opy_ (u"ࠩࡤࡴࡵࡲࡩࡤࡣࡷ࡭ࡴࡴ࠯࡫ࡵࡲࡲࠬῈ"),
            bstack111l11_opy_ (u"ࠪࡅࡨࡩࡥࡱࡶࠪΈ"): bstack111l11_opy_ (u"ࠫࡦࡶࡰ࡭࡫ࡦࡥࡹ࡯࡯࡯࠱࡭ࡷࡴࡴࠧῊ")
        }
        if extra_headers:
            headers.update(extra_headers)
        url = bstack11l1l1lllll_opy_ + bstack111l11_opy_ (u"ࠧ࠵ࠢΉ") + bstack1lllll1lll11_opy_.lstrip(bstack111l11_opy_ (u"࠭࠯ࠨῌ"))
        try:
            if method == bstack111l11_opy_ (u"ࠧࡈࡇࡗࠫ῍"):
                response = requests.get(url, headers=headers, params=params, json=data)
            elif method == bstack111l11_opy_ (u"ࠨࡒࡒࡗ࡙࠭῎"):
                response = requests.post(url, headers=headers, json=data)
            elif method == bstack111l11_opy_ (u"ࠩࡓ࡙࡙࠭῏"):
                response = requests.put(url, headers=headers, json=data)
            else:
                raise ValueError(bstack111l11_opy_ (u"࡙ࠥࡳࡹࡵࡱࡲࡲࡶࡹ࡫ࡤࠡࡊࡗࡘࡕࠦ࡭ࡦࡶ࡫ࡳࡩࡀࠠࡼࡿࠥῐ").format(method))
            logger.debug(bstack111l11_opy_ (u"ࠦࡔࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࠤࡷ࡫ࡱࡶࡧࡶࡸࠥࡳࡡࡥࡧࠣࡸࡴࠦࡕࡓࡎ࠽ࠤࢀࢃࠠࡸ࡫ࡷ࡬ࠥࡳࡥࡵࡪࡲࡨ࠿ࠦࡻࡾࠤῑ").format(url, method))
            bstack1lllll1lll1l_opy_ = {}
            try:
                bstack1lllll1lll1l_opy_ = response.json()
            except Exception as e:
                logger.debug(bstack111l11_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡲࡤࡶࡸ࡫ࠠࡋࡕࡒࡒࠥࡸࡥࡴࡲࡲࡲࡸ࡫࠺ࠡࡽࢀࠤ࠲ࠦࡻࡾࠤῒ").format(e, response.text))
            if bstack1lllll1lll1l_opy_ is not None:
                bstack1lllll1lll1l_opy_[bstack111l11_opy_ (u"࠭࡮ࡦࡺࡷࡣࡵࡵ࡬࡭ࡡࡷ࡭ࡲ࡫ࠧΐ")] = response.headers.get(
                    bstack111l11_opy_ (u"ࠧ࡯ࡧࡻࡸࡤࡶ࡯࡭࡮ࡢࡸ࡮ࡳࡥࠨ῔"), str(int(datetime.now().timestamp() * 1000))
                )
                bstack1lllll1lll1l_opy_[bstack111l11_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ῕")] = response.status_code
            return bstack1lllll1lll1l_opy_
        except Exception as e:
            logger.error(bstack111l11_opy_ (u"ࠤࡒࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯ࠢࡵࡩࡶࡻࡥࡴࡶࠣࡪࡦ࡯࡬ࡦࡦ࠽ࠤࢀࢃࠠ࠮ࠢࡾࢁࠧῖ").format(e, url))
            return None
    @staticmethod
    def bstack11l11lllll1_opy_(bstack1llllll111ll_opy_, data):
        bstack111l11_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠࡔࡧࡱࡨࡸࠦࡡࠡࡒࡘࡘࠥࡸࡥࡲࡷࡨࡷࡹࠦࡴࡰࠢࡶࡸࡴࡸࡥࠡࡶ࡫ࡩࠥ࡬ࡡࡪ࡮ࡨࡨࠥࡺࡥࡴࡶࡶࠎࠥࠦࠠࠡࠢࠣࠤࠥࠨࠢࠣῗ")
        bstack1llllll11111_opy_ = os.environ.get(bstack111l11_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣࡏ࡝ࡔࠨῘ"), bstack111l11_opy_ (u"ࠬ࠭Ῑ"))
        headers = {
            bstack111l11_opy_ (u"࠭ࡡࡶࡶ࡫ࡳࡷ࡯ࡺࡢࡶ࡬ࡳࡳ࠭Ὶ"): bstack111l11_opy_ (u"ࠧࡃࡧࡤࡶࡪࡸࠠࡼࡿࠪΊ").format(bstack1llllll11111_opy_),
            bstack111l11_opy_ (u"ࠨࡅࡲࡲࡹ࡫࡮ࡵ࠯ࡗࡽࡵ࡫ࠧ῜"): bstack111l11_opy_ (u"ࠩࡤࡴࡵࡲࡩࡤࡣࡷ࡭ࡴࡴ࠯࡫ࡵࡲࡲࠬ῝")
        }
        response = requests.put(bstack1llllll111ll_opy_, headers=headers, json=data)
        bstack1lllll1lll1l_opy_ = {}
        try:
            bstack1lllll1lll1l_opy_ = response.json()
        except Exception as e:
            logger.debug(bstack111l11_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡰࡢࡴࡶࡩࠥࡐࡓࡐࡐࠣࡶࡪࡹࡰࡰࡰࡶࡩ࠿ࠦࡻࡾࠤ῞").format(e))
            pass
        logger.debug(bstack111l11_opy_ (u"ࠦࡗ࡫ࡱࡶࡧࡶࡸ࡚ࡺࡩ࡭ࡵ࠽ࠤࡵࡻࡴࡠࡨࡤ࡭ࡱ࡫ࡤࡠࡶࡨࡷࡹࡹࠠࡳࡧࡶࡴࡴࡴࡳࡦ࠼ࠣࡿࢂࠨ῟").format(bstack1lllll1lll1l_opy_))
        if bstack1lllll1lll1l_opy_ is not None:
            bstack1lllll1lll1l_opy_[bstack111l11_opy_ (u"ࠬࡴࡥࡹࡶࡢࡴࡴࡲ࡬ࡠࡶ࡬ࡱࡪ࠭ῠ")] = response.headers.get(
                bstack111l11_opy_ (u"࠭࡮ࡦࡺࡷࡣࡵࡵ࡬࡭ࡡࡷ࡭ࡲ࡫ࠧῡ"), str(int(datetime.now().timestamp() * 1000))
            )
            bstack1lllll1lll1l_opy_[bstack111l11_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧῢ")] = response.status_code
        return bstack1lllll1lll1l_opy_
    @staticmethod
    def bstack11l1l1111l1_opy_(bstack1llllll111ll_opy_):
        bstack111l11_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤ࡙ࠥࡥ࡯ࡦࡶࠤࡦࠦࡇࡆࡖࠣࡶࡪࡷࡵࡦࡵࡷࠤࡹࡵࠠࡨࡧࡷࠤࡹ࡮ࡥࠡࡥࡲࡹࡳࡺࠠࡰࡨࠣࡪࡦ࡯࡬ࡦࡦࠣࡸࡪࡹࡴࡴࠌࠣࠤࠥࠦࠠࠡࠢࠣࠦࠧࠨΰ")
        bstack1llllll11111_opy_ = os.environ.get(bstack111l11_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡍ࡛࡙࠭ῤ"), bstack111l11_opy_ (u"ࠪࠫῥ"))
        headers = {
            bstack111l11_opy_ (u"ࠫࡦࡻࡴࡩࡱࡵ࡭ࡿࡧࡴࡪࡱࡱࠫῦ"): bstack111l11_opy_ (u"ࠬࡈࡥࡢࡴࡨࡶࠥࢁࡽࠨῧ").format(bstack1llllll11111_opy_),
            bstack111l11_opy_ (u"࠭ࡃࡰࡰࡷࡩࡳࡺ࠭ࡕࡻࡳࡩࠬῨ"): bstack111l11_opy_ (u"ࠧࡢࡲࡳࡰ࡮ࡩࡡࡵ࡫ࡲࡲ࠴ࡰࡳࡰࡰࠪῩ")
        }
        response = requests.get(bstack1llllll111ll_opy_, headers=headers)
        bstack1lllll1lll1l_opy_ = {}
        try:
            bstack1lllll1lll1l_opy_ = response.json()
            logger.debug(bstack111l11_opy_ (u"ࠣࡔࡨࡵࡺ࡫ࡳࡵࡗࡷ࡭ࡱࡹ࠺ࠡࡩࡨࡸࡤ࡬ࡡࡪ࡮ࡨࡨࡤࡺࡥࡴࡶࡶࠤࡷ࡫ࡳࡱࡱࡱࡷࡪࡀࠠࡼࡿࠥῪ").format(bstack1lllll1lll1l_opy_))
        except Exception as e:
            logger.debug(bstack111l11_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡶࡡࡳࡵࡨࠤࡏ࡙ࡏࡏࠢࡵࡩࡸࡶ࡯࡯ࡵࡨ࠾ࠥࢁࡽࠡ࠯ࠣࡿࢂࠨΎ").format(e, response.text))
            pass
        if bstack1lllll1lll1l_opy_ is not None:
            bstack1lllll1lll1l_opy_[bstack111l11_opy_ (u"ࠪࡲࡪࡾࡴࡠࡲࡲࡰࡱࡥࡴࡪ࡯ࡨࠫῬ")] = response.headers.get(
                bstack111l11_opy_ (u"ࠫࡳ࡫ࡸࡵࡡࡳࡳࡱࡲ࡟ࡵ࡫ࡰࡩࠬ῭"), str(int(datetime.now().timestamp() * 1000))
            )
            bstack1lllll1lll1l_opy_[bstack111l11_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬ΅")] = response.status_code
        return bstack1lllll1lll1l_opy_
    @staticmethod
    def bstack1111ll1l11l_opy_(bstack11ll111lll1_opy_, payload):
        bstack111l11_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣࡑࡦࡱࡥࡴࠢࡤࠤࡕࡕࡓࡕࠢࡵࡩࡶࡻࡥࡴࡶࠣࡸࡴࠦࡴࡩࡧࠣࡧࡴࡲ࡬ࡦࡥࡷ࠱ࡧࡻࡩ࡭ࡦ࠰ࡨࡦࡺࡡࠡࡧࡱࡨࡵࡵࡩ࡯ࡶ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࡇࡲࡨࡵ࠽ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡨࡲࡩࡶ࡯ࡪࡰࡷࠤ࠭ࡹࡴࡳࠫ࠽ࠤ࡙࡮ࡥࠡࡃࡓࡍࠥ࡫࡮ࡥࡲࡲ࡭ࡳࡺࠠࡱࡣࡷ࡬࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡵࡧࡹ࡭ࡱࡤࡨࠥ࠮ࡤࡪࡥࡷ࠭࠿ࠦࡔࡩࡧࠣࡶࡪࡷࡵࡦࡵࡷࠤࡵࡧࡹ࡭ࡱࡤࡨ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࡓࡧࡷࡹࡷࡴࡳ࠻ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡥ࡫ࡦࡸ࠿ࠦࡒࡦࡵࡳࡳࡳࡹࡥࠡࡨࡵࡳࡲࠦࡴࡩࡧࠣࡅࡕࡏࠬࠡࡱࡵࠤࡓࡵ࡮ࡦࠢ࡬ࡪࠥ࡬ࡡࡪ࡮ࡨࡨ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠣࠤࠥ`")
        try:
            url = bstack111l11_opy_ (u"ࠢࡼࡿ࠲ࡿࢂࠨ῰").format(bstack11l1l1lllll_opy_, bstack11ll111lll1_opy_)
            bstack1llllll11111_opy_ = os.environ.get(bstack111l11_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡌ࡚ࡘࠬ῱"), bstack111l11_opy_ (u"ࠩࠪῲ"))
            headers = {
                bstack111l11_opy_ (u"ࠪࡥࡺࡺࡨࡰࡴ࡬ࡾࡦࡺࡩࡰࡰࠪῳ"): bstack111l11_opy_ (u"ࠫࡇ࡫ࡡࡳࡧࡵࠤࢀࢃࠧῴ").format(bstack1llllll11111_opy_),
                bstack111l11_opy_ (u"ࠬࡉ࡯࡯ࡶࡨࡲࡹ࠳ࡔࡺࡲࡨࠫ῵"): bstack111l11_opy_ (u"࠭ࡡࡱࡲ࡯࡭ࡨࡧࡴࡪࡱࡱ࠳࡯ࡹ࡯࡯ࠩῶ")
            }
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            if response.status_code == 200 or response.status_code == 202:
                return response.json()
            else:
                logger.error(bstack111l11_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡧࡴࡲ࡬ࡦࡥࡷࠤࡧࡻࡩ࡭ࡦࠣࡨࡦࡺࡡ࠯ࠢࡖࡸࡦࡺࡵࡴ࠼ࠣࡿࢂ࠲ࠠࡓࡧࡶࡴࡴࡴࡳࡦ࠼ࠣࡿࢂࠨῷ").format(
                    response.status_code, response.text))
                return None
        except Exception as e:
            logger.error(bstack111l11_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱࡱࡶࡸࡤࡩ࡯࡭࡮ࡨࡧࡹࡥࡢࡶ࡫࡯ࡨࡤࡪࡡࡵࡣ࠽ࠤࢀࢃࠢῸ").format(e))
            return None