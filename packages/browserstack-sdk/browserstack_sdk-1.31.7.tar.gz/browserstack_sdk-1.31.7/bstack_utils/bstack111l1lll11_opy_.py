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
import logging
import os
import datetime
import threading
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.helper import bstack11ll1l11lll_opy_, bstack11ll1ll1ll1_opy_, bstack11ll1llll_opy_, error_handler, bstack111lll1l111_opy_, bstack11l1111l1ll_opy_, bstack111ll1lllll_opy_, bstack11ll11lll_opy_, bstack1l11lllll1_opy_
from bstack_utils.measure import measure
from bstack_utils.bstack1llllll1l111_opy_ import bstack1llllll1l11l_opy_
import bstack_utils.bstack11ll11l11_opy_ as bstack1ll1111l1l_opy_
from bstack_utils.bstack111lll1111_opy_ import bstack1l1lll1ll1_opy_
import bstack_utils.accessibility as bstack1l1l111l1l_opy_
from bstack_utils.bstack11l1ll111l_opy_ import bstack11l1ll111l_opy_
from bstack_utils.bstack111l1llll1_opy_ import bstack111l11l1ll_opy_
from bstack_utils.constants import bstack1l11lll1ll_opy_
bstack1llll11lll1l_opy_ = bstack111l11_opy_ (u"ࠬ࡮ࡴࡵࡲࡶ࠾࠴࠵ࡣࡰ࡮࡯ࡩࡨࡺ࡯ࡳ࠯ࡲࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡥࡲࡱࠬ₲")
logger = logging.getLogger(__name__)
class bstack111l1ll1_opy_:
    bstack1llllll1l111_opy_ = None
    bs_config = None
    bstack11l1llll11_opy_ = None
    @classmethod
    @error_handler(class_method=True)
    @measure(event_name=EVENTS.bstack11l1lll11l1_opy_, stage=STAGE.bstack111lllll1_opy_)
    def launch(cls, bs_config, bstack11l1llll11_opy_):
        cls.bs_config = bs_config
        cls.bstack11l1llll11_opy_ = bstack11l1llll11_opy_
        try:
            cls.bstack1llll1l1lll1_opy_()
            bstack11ll1l1l1l1_opy_ = bstack11ll1l11lll_opy_(bs_config)
            bstack11ll11l1l1l_opy_ = bstack11ll1ll1ll1_opy_(bs_config)
            data = bstack1ll1111l1l_opy_.bstack1llll11llll1_opy_(bs_config, bstack11l1llll11_opy_)
            config = {
                bstack111l11_opy_ (u"࠭ࡡࡶࡶ࡫ࠫ₳"): (bstack11ll1l1l1l1_opy_, bstack11ll11l1l1l_opy_),
                bstack111l11_opy_ (u"ࠧࡩࡧࡤࡨࡪࡸࡳࠨ₴"): cls.default_headers()
            }
            response = bstack11ll1llll_opy_(bstack111l11_opy_ (u"ࠨࡒࡒࡗ࡙࠭₵"), cls.request_url(bstack111l11_opy_ (u"ࠩࡤࡴ࡮࠵ࡶ࠳࠱ࡥࡹ࡮ࡲࡤࡴࠩ₶")), data, config)
            if response.status_code != 200:
                bstack11ll1ll11_opy_ = response.json()
                if bstack11ll1ll11_opy_[bstack111l11_opy_ (u"ࠪࡷࡺࡩࡣࡦࡵࡶࠫ₷")] == False:
                    cls.bstack1llll1l1l1ll_opy_(bstack11ll1ll11_opy_)
                    return
                cls.bstack1llll1l111l1_opy_(bstack11ll1ll11_opy_[bstack111l11_opy_ (u"ࠫࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫ₸")])
                cls.bstack1llll11ll1l1_opy_(bstack11ll1ll11_opy_[bstack111l11_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ₹")])
                return None
            bstack1llll1l11lll_opy_ = cls.bstack1llll1l1111l_opy_(response)
            return bstack1llll1l11lll_opy_, response.json()
        except Exception as error:
            logger.error(bstack111l11_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢࡺ࡬࡮ࡲࡥࠡࡥࡵࡩࡦࡺࡩ࡯ࡩࠣࡦࡺ࡯࡬ࡥࠢࡩࡳࡷࠦࡔࡦࡵࡷࡌࡺࡨ࠺ࠡࡽࢀࠦ₺").format(str(error)))
            return None
    @classmethod
    @error_handler(class_method=True)
    def stop(cls, bstack1llll1l1ll11_opy_=None):
        if not bstack1l1lll1ll1_opy_.on() and not bstack1l1l111l1l_opy_.on():
            return
        if os.environ.get(bstack111l11_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠫ₻")) == bstack111l11_opy_ (u"ࠣࡰࡸࡰࡱࠨ₼") or os.environ.get(bstack111l11_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧ₽")) == bstack111l11_opy_ (u"ࠥࡲࡺࡲ࡬ࠣ₾"):
            logger.error(bstack111l11_opy_ (u"ࠫࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡷࡹࡵࡰࠡࡤࡸ࡭ࡱࡪࠠࡳࡧࡴࡹࡪࡹࡴࠡࡶࡲࠤ࡙࡫ࡳࡵࡊࡸࡦ࠿ࠦࡍࡪࡵࡶ࡭ࡳ࡭ࠠࡢࡷࡷ࡬ࡪࡴࡴࡪࡥࡤࡸ࡮ࡵ࡮ࠡࡶࡲ࡯ࡪࡴࠧ₿"))
            return {
                bstack111l11_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬ⃀"): bstack111l11_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬ⃁"),
                bstack111l11_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨ⃂"): bstack111l11_opy_ (u"ࠨࡖࡲ࡯ࡪࡴ࠯ࡣࡷ࡬ࡰࡩࡏࡄࠡ࡫ࡶࠤࡺࡴࡤࡦࡨ࡬ࡲࡪࡪࠬࠡࡤࡸ࡭ࡱࡪࠠࡤࡴࡨࡥࡹ࡯࡯࡯ࠢࡰ࡭࡬࡮ࡴࠡࡪࡤࡺࡪࠦࡦࡢ࡫࡯ࡩࡩ࠭⃃")
            }
        try:
            cls.bstack1llllll1l111_opy_.shutdown()
            data = {
                bstack111l11_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧ⃄"): bstack11ll11lll_opy_()
            }
            if not bstack1llll1l1ll11_opy_ is None:
                data[bstack111l11_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡳࡥࡵࡣࡧࡥࡹࡧࠧ⃅")] = [{
                    bstack111l11_opy_ (u"ࠫࡷ࡫ࡡࡴࡱࡱࠫ⃆"): bstack111l11_opy_ (u"ࠬࡻࡳࡦࡴࡢ࡯࡮ࡲ࡬ࡦࡦࠪ⃇"),
                    bstack111l11_opy_ (u"࠭ࡳࡪࡩࡱࡥࡱ࠭⃈"): bstack1llll1l1ll11_opy_
                }]
            config = {
                bstack111l11_opy_ (u"ࠧࡩࡧࡤࡨࡪࡸࡳࠨ⃉"): cls.default_headers()
            }
            bstack11ll111lll1_opy_ = bstack111l11_opy_ (u"ࠨࡣࡳ࡭࠴ࡼ࠱࠰ࡤࡸ࡭ࡱࡪࡳ࠰ࡽࢀ࠳ࡸࡺ࡯ࡱࠩ⃊").format(os.environ[bstack111l11_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠢ⃋")])
            bstack1llll1l11l1l_opy_ = cls.request_url(bstack11ll111lll1_opy_)
            response = bstack11ll1llll_opy_(bstack111l11_opy_ (u"ࠪࡔ࡚࡚ࠧ⃌"), bstack1llll1l11l1l_opy_, data, config)
            if not response.ok:
                raise Exception(bstack111l11_opy_ (u"ࠦࡘࡺ࡯ࡱࠢࡵࡩࡶࡻࡥࡴࡶࠣࡲࡴࡺࠠࡰ࡭ࠥ⃍"))
        except Exception as error:
            logger.error(bstack111l11_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡸࡺ࡯ࡱࠢࡥࡹ࡮ࡲࡤࠡࡴࡨࡵࡺ࡫ࡳࡵࠢࡷࡳ࡚ࠥࡥࡴࡶࡋࡹࡧࡀ࠺ࠡࠤ⃎") + str(error))
            return {
                bstack111l11_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭⃏"): bstack111l11_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭⃐"),
                bstack111l11_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩ⃑"): str(error)
            }
    @classmethod
    @error_handler(class_method=True)
    def bstack1llll1l1111l_opy_(cls, response):
        bstack11ll1ll11_opy_ = response.json() if not isinstance(response, dict) else response
        bstack1llll1l11lll_opy_ = {}
        if bstack11ll1ll11_opy_.get(bstack111l11_opy_ (u"ࠩ࡭ࡻࡹ⃒࠭")) is None:
            os.environ[bstack111l11_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢࡎ࡜⃓࡚ࠧ")] = bstack111l11_opy_ (u"ࠫࡳࡻ࡬࡭ࠩ⃔")
        else:
            os.environ[bstack111l11_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤࡐࡗࡕࠩ⃕")] = bstack11ll1ll11_opy_.get(bstack111l11_opy_ (u"࠭ࡪࡸࡶࠪ⃖"), bstack111l11_opy_ (u"ࠧ࡯ࡷ࡯ࡰࠬ⃗"))
        os.environ[bstack111l11_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ⃘࠭")] = bstack11ll1ll11_opy_.get(bstack111l11_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧ⃙ࠫ"), bstack111l11_opy_ (u"ࠪࡲࡺࡲ࡬ࠨ⃚"))
        logger.info(bstack111l11_opy_ (u"࡙ࠫ࡫ࡳࡵࡪࡸࡦࠥࡹࡴࡢࡴࡷࡩࡩࠦࡷࡪࡶ࡫ࠤ࡮ࡪ࠺ࠡࠩ⃛") + os.getenv(bstack111l11_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪ⃜")));
        if bstack1l1lll1ll1_opy_.bstack1llll1l11111_opy_(cls.bs_config, cls.bstack11l1llll11_opy_.get(bstack111l11_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡸࡷࡪࡪࠧ⃝"), bstack111l11_opy_ (u"ࠧࠨ⃞"))) is True:
            bstack1llllll11111_opy_, build_hashed_id, bstack1llll1l111ll_opy_ = cls.bstack1llll1ll11ll_opy_(bstack11ll1ll11_opy_)
            if bstack1llllll11111_opy_ != None and build_hashed_id != None:
                bstack1llll1l11lll_opy_[bstack111l11_opy_ (u"ࠨࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࠨ⃟")] = {
                    bstack111l11_opy_ (u"ࠩ࡭ࡻࡹࡥࡴࡰ࡭ࡨࡲࠬ⃠"): bstack1llllll11111_opy_,
                    bstack111l11_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡡ࡫ࡥࡸ࡮ࡥࡥࡡ࡬ࡨࠬ⃡"): build_hashed_id,
                    bstack111l11_opy_ (u"ࠫࡦࡲ࡬ࡰࡹࡢࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࡳࠨ⃢"): bstack1llll1l111ll_opy_
                }
            else:
                bstack1llll1l11lll_opy_[bstack111l11_opy_ (u"ࠬࡵࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠬ⃣")] = {}
        else:
            bstack1llll1l11lll_opy_[bstack111l11_opy_ (u"࠭࡯ࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠭⃤")] = {}
        bstack1llll1l1llll_opy_, build_hashed_id = cls.bstack1llll1ll111l_opy_(bstack11ll1ll11_opy_)
        if bstack1llll1l1llll_opy_ != None and build_hashed_id != None:
            bstack1llll1l11lll_opy_[bstack111l11_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿ⃥ࠧ")] = {
                bstack111l11_opy_ (u"ࠨࡣࡸࡸ࡭ࡥࡴࡰ࡭ࡨࡲ⃦ࠬ"): bstack1llll1l1llll_opy_,
                bstack111l11_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠫ⃧"): build_hashed_id,
            }
        else:
            bstack1llll1l11lll_opy_[bstack111l11_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻ⃨ࠪ")] = {}
        if bstack1llll1l11lll_opy_[bstack111l11_opy_ (u"ࠫࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫ⃩")].get(bstack111l11_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡣ࡭ࡧࡳࡩࡧࡧࡣ࡮ࡪ⃪ࠧ")) != None or bstack1llll1l11lll_opy_[bstack111l11_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ⃫࠭")].get(bstack111l11_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡥࡨࡢࡵ࡫ࡩࡩࡥࡩࡥ⃬ࠩ")) != None:
            cls.bstack1llll1l1ll1l_opy_(bstack11ll1ll11_opy_.get(bstack111l11_opy_ (u"ࠨ࡬ࡺࡸ⃭ࠬ")), bstack11ll1ll11_opy_.get(bstack111l11_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧ⃮ࠫ")))
        return bstack1llll1l11lll_opy_
    @classmethod
    def bstack1llll1ll11ll_opy_(cls, bstack11ll1ll11_opy_):
        if bstack11ll1ll11_opy_.get(bstack111l11_opy_ (u"ࠪࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻ⃯ࠪ")) == None:
            cls.bstack1llll1l111l1_opy_()
            return [None, None, None]
        if bstack11ll1ll11_opy_[bstack111l11_opy_ (u"ࠫࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫ⃰")][bstack111l11_opy_ (u"ࠬࡹࡵࡤࡥࡨࡷࡸ࠭⃱")] != True:
            cls.bstack1llll1l111l1_opy_(bstack11ll1ll11_opy_[bstack111l11_opy_ (u"࠭࡯ࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠭⃲")])
            return [None, None, None]
        logger.debug(bstack111l11_opy_ (u"ࠧࡼࡿࠣࡆࡺ࡯࡬ࡥࠢࡦࡶࡪࡧࡴࡪࡱࡱࠤࡘࡻࡣࡤࡧࡶࡷ࡫ࡻ࡬ࠢࠩ⃳").format(bstack1l11lll1ll_opy_))
        os.environ[bstack111l11_opy_ (u"ࠨࡄࡖࡣ࡙ࡋࡓࡕࡑࡓࡗࡤࡈࡕࡊࡎࡇࡣࡈࡕࡍࡑࡎࡈࡘࡊࡊࠧ⃴")] = bstack111l11_opy_ (u"ࠩࡷࡶࡺ࡫ࠧ⃵")
        if bstack11ll1ll11_opy_.get(bstack111l11_opy_ (u"ࠪ࡮ࡼࡺࠧ⃶")):
            os.environ[bstack111l11_opy_ (u"ࠫࡈࡘࡅࡅࡇࡑࡘࡎࡇࡌࡔࡡࡉࡓࡗࡥࡃࡓࡃࡖࡌࡤࡘࡅࡑࡑࡕࡘࡎࡔࡇࠨ⃷")] = json.dumps({
                bstack111l11_opy_ (u"ࠬࡻࡳࡦࡴࡱࡥࡲ࡫ࠧ⃸"): bstack11ll1l11lll_opy_(cls.bs_config),
                bstack111l11_opy_ (u"࠭ࡰࡢࡵࡶࡻࡴࡸࡤࠨ⃹"): bstack11ll1ll1ll1_opy_(cls.bs_config)
            })
        if bstack11ll1ll11_opy_.get(bstack111l11_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡥࡨࡢࡵ࡫ࡩࡩࡥࡩࡥࠩ⃺")):
            os.environ[bstack111l11_opy_ (u"ࠨࡄࡖࡣ࡙ࡋࡓࡕࡑࡓࡗࡤࡈࡕࡊࡎࡇࡣࡍࡇࡓࡉࡇࡇࡣࡎࡊࠧ⃻")] = bstack11ll1ll11_opy_[bstack111l11_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠫ⃼")]
        if bstack11ll1ll11_opy_[bstack111l11_opy_ (u"ࠪࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪ⃽")].get(bstack111l11_opy_ (u"ࠫࡴࡶࡴࡪࡱࡱࡷࠬ⃾"), {}).get(bstack111l11_opy_ (u"ࠬࡧ࡬࡭ࡱࡺࡣࡸࡩࡲࡦࡧࡱࡷ࡭ࡵࡴࡴࠩ⃿")):
            os.environ[bstack111l11_opy_ (u"࠭ࡂࡔࡡࡗࡉࡘ࡚ࡏࡑࡕࡢࡅࡑࡒࡏࡘࡡࡖࡇࡗࡋࡅࡏࡕࡋࡓ࡙࡙ࠧ℀")] = str(bstack11ll1ll11_opy_[bstack111l11_opy_ (u"ࠧࡰࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࠧ℁")][bstack111l11_opy_ (u"ࠨࡱࡳࡸ࡮ࡵ࡮ࡴࠩℂ")][bstack111l11_opy_ (u"ࠩࡤࡰࡱࡵࡷࡠࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࡸ࠭℃")])
        else:
            os.environ[bstack111l11_opy_ (u"ࠪࡆࡘࡥࡔࡆࡕࡗࡓࡕ࡙࡟ࡂࡎࡏࡓ࡜ࡥࡓࡄࡔࡈࡉࡓ࡙ࡈࡐࡖࡖࠫ℄")] = bstack111l11_opy_ (u"ࠦࡳࡻ࡬࡭ࠤ℅")
        return [bstack11ll1ll11_opy_[bstack111l11_opy_ (u"ࠬࡰࡷࡵࠩ℆")], bstack11ll1ll11_opy_[bstack111l11_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡤ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠨℇ")], os.environ[bstack111l11_opy_ (u"ࠧࡃࡕࡢࡘࡊ࡙ࡔࡐࡒࡖࡣࡆࡒࡌࡐ࡙ࡢࡗࡈࡘࡅࡆࡐࡖࡌࡔ࡚ࡓࠨ℈")]]
    @classmethod
    def bstack1llll1ll111l_opy_(cls, bstack11ll1ll11_opy_):
        if bstack11ll1ll11_opy_.get(bstack111l11_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ℉")) == None:
            cls.bstack1llll11ll1l1_opy_()
            return [None, None]
        if bstack11ll1ll11_opy_[bstack111l11_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩℊ")][bstack111l11_opy_ (u"ࠪࡷࡺࡩࡣࡦࡵࡶࠫℋ")] != True:
            cls.bstack1llll11ll1l1_opy_(bstack11ll1ll11_opy_[bstack111l11_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫℌ")])
            return [None, None]
        if bstack11ll1ll11_opy_[bstack111l11_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬℍ")].get(bstack111l11_opy_ (u"࠭࡯ࡱࡶ࡬ࡳࡳࡹࠧℎ")):
            logger.debug(bstack111l11_opy_ (u"ࠧࡕࡧࡶࡸࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡈࡵࡪ࡮ࡧࠤࡨࡸࡥࡢࡶ࡬ࡳࡳࠦࡓࡶࡥࡦࡩࡸࡹࡦࡶ࡮ࠤࠫℏ"))
            parsed = json.loads(os.getenv(bstack111l11_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡤࡇࡃࡄࡇࡖࡗࡎࡈࡉࡍࡋࡗ࡝ࡤࡉࡏࡏࡈࡌࡋ࡚ࡘࡁࡕࡋࡒࡒࡤ࡟ࡍࡍࠩℐ"), bstack111l11_opy_ (u"ࠩࡾࢁࠬℑ")))
            capabilities = bstack1ll1111l1l_opy_.bstack1llll1l1l111_opy_(bstack11ll1ll11_opy_[bstack111l11_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪℒ")][bstack111l11_opy_ (u"ࠫࡴࡶࡴࡪࡱࡱࡷࠬℓ")][bstack111l11_opy_ (u"ࠬࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠫ℔")], bstack111l11_opy_ (u"࠭࡮ࡢ࡯ࡨࠫℕ"), bstack111l11_opy_ (u"ࠧࡷࡣ࡯ࡹࡪ࠭№"))
            bstack1llll1l1llll_opy_ = capabilities[bstack111l11_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡕࡱ࡮ࡩࡳ࠭℗")]
            os.environ[bstack111l11_opy_ (u"ࠩࡅࡗࡤࡇ࠱࠲࡛ࡢࡎ࡜࡚ࠧ℘")] = bstack1llll1l1llll_opy_
            if bstack111l11_opy_ (u"ࠥࡥࡺࡺ࡯࡮ࡣࡷࡩࠧℙ") in bstack11ll1ll11_opy_ and bstack11ll1ll11_opy_.get(bstack111l11_opy_ (u"ࠦࡦࡶࡰࡠࡣࡸࡸࡴࡳࡡࡵࡧࠥℚ")) is None:
                parsed[bstack111l11_opy_ (u"ࠬࡹࡣࡢࡰࡱࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ℛ")] = capabilities[bstack111l11_opy_ (u"࠭ࡳࡤࡣࡱࡲࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧℜ")]
            os.environ[bstack111l11_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡣࡆࡉࡃࡆࡕࡖࡍࡇࡏࡌࡊࡖ࡜ࡣࡈࡕࡎࡇࡋࡊ࡙ࡗࡇࡔࡊࡑࡑࡣ࡞ࡓࡌࠨℝ")] = json.dumps(parsed)
            scripts = bstack1ll1111l1l_opy_.bstack1llll1l1l111_opy_(bstack11ll1ll11_opy_[bstack111l11_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ℞")][bstack111l11_opy_ (u"ࠩࡲࡴࡹ࡯࡯࡯ࡵࠪ℟")][bstack111l11_opy_ (u"ࠪࡷࡨࡸࡩࡱࡶࡶࠫ℠")], bstack111l11_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ℡"), bstack111l11_opy_ (u"ࠬࡩ࡯࡮࡯ࡤࡲࡩ࠭™"))
            bstack11l1ll111l_opy_.bstack11ll1l1lll_opy_(scripts)
            commands = bstack11ll1ll11_opy_[bstack111l11_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭℣")][bstack111l11_opy_ (u"ࠧࡰࡲࡷ࡭ࡴࡴࡳࠨℤ")][bstack111l11_opy_ (u"ࠨࡥࡲࡱࡲࡧ࡮ࡥࡵࡗࡳ࡜ࡸࡡࡱࠩ℥")].get(bstack111l11_opy_ (u"ࠩࡦࡳࡲࡳࡡ࡯ࡦࡶࠫΩ"))
            bstack11l1ll111l_opy_.bstack11ll11lll1l_opy_(commands)
            bstack11ll11l1l11_opy_ = capabilities.get(bstack111l11_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨ℧"))
            bstack11l1ll111l_opy_.bstack11ll11l1111_opy_(bstack11ll11l1l11_opy_)
            bstack11l1ll111l_opy_.store()
        return [bstack1llll1l1llll_opy_, bstack11ll1ll11_opy_[bstack111l11_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡢ࡬ࡦࡹࡨࡦࡦࡢ࡭ࡩ࠭ℨ")]]
    @classmethod
    def bstack1llll1l111l1_opy_(cls, response=None):
        os.environ[bstack111l11_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪ℩")] = bstack111l11_opy_ (u"࠭࡮ࡶ࡮࡯ࠫK")
        os.environ[bstack111l11_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠫÅ")] = bstack111l11_opy_ (u"ࠨࡰࡸࡰࡱ࠭ℬ")
        os.environ[bstack111l11_opy_ (u"ࠩࡅࡗࡤ࡚ࡅࡔࡖࡒࡔࡘࡥࡂࡖࡋࡏࡈࡤࡉࡏࡎࡒࡏࡉ࡙ࡋࡄࠨℭ")] = bstack111l11_opy_ (u"ࠪࡪࡦࡲࡳࡦࠩ℮")
        os.environ[bstack111l11_opy_ (u"ࠫࡇ࡙࡟ࡕࡇࡖࡘࡔࡖࡓࡠࡄࡘࡍࡑࡊ࡟ࡉࡃࡖࡌࡊࡊ࡟ࡊࡆࠪℯ")] = bstack111l11_opy_ (u"ࠧࡴࡵ࡭࡮ࠥℰ")
        os.environ[bstack111l11_opy_ (u"࠭ࡂࡔࡡࡗࡉࡘ࡚ࡏࡑࡕࡢࡅࡑࡒࡏࡘࡡࡖࡇࡗࡋࡅࡏࡕࡋࡓ࡙࡙ࠧℱ")] = bstack111l11_opy_ (u"ࠢ࡯ࡷ࡯ࡰࠧℲ")
        cls.bstack1llll1l1l1ll_opy_(response, bstack111l11_opy_ (u"ࠣࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࠣℳ"))
        return [None, None, None]
    @classmethod
    def bstack1llll11ll1l1_opy_(cls, response=None):
        os.environ[bstack111l11_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧℴ")] = bstack111l11_opy_ (u"ࠪࡲࡺࡲ࡬ࠨℵ")
        os.environ[bstack111l11_opy_ (u"ࠫࡇ࡙࡟ࡂ࠳࠴࡝ࡤࡐࡗࡕࠩℶ")] = bstack111l11_opy_ (u"ࠬࡴࡵ࡭࡮ࠪℷ")
        os.environ[bstack111l11_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪℸ")] = bstack111l11_opy_ (u"ࠧ࡯ࡷ࡯ࡰࠬℹ")
        cls.bstack1llll1l1l1ll_opy_(response, bstack111l11_opy_ (u"ࠣࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠣ℺"))
        return [None, None, None]
    @classmethod
    def bstack1llll1l1ll1l_opy_(cls, jwt, build_hashed_id):
        os.environ[bstack111l11_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡍ࡛࡙࠭℻")] = jwt
        os.environ[bstack111l11_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨℼ")] = build_hashed_id
    @classmethod
    def bstack1llll1l1l1ll_opy_(cls, response=None, product=bstack111l11_opy_ (u"ࠦࠧℽ")):
        if response == None or response.get(bstack111l11_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࡷࠬℾ")) == None:
            logger.error(product + bstack111l11_opy_ (u"ࠨࠠࡃࡷ࡬ࡰࡩࠦࡣࡳࡧࡤࡸ࡮ࡵ࡮ࠡࡨࡤ࡭ࡱ࡫ࡤࠣℿ"))
            return
        for error in response[bstack111l11_opy_ (u"ࠧࡦࡴࡵࡳࡷࡹࠧ⅀")]:
            bstack11l111ll111_opy_ = error[bstack111l11_opy_ (u"ࠨ࡭ࡨࡽࠬ⅁")]
            error_message = error[bstack111l11_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪ⅂")]
            if error_message:
                if bstack11l111ll111_opy_ == bstack111l11_opy_ (u"ࠥࡉࡗࡘࡏࡓࡡࡄࡇࡈࡋࡓࡔࡡࡇࡉࡓࡏࡅࡅࠤ⅃"):
                    logger.info(error_message)
                else:
                    logger.error(error_message)
            else:
                logger.error(bstack111l11_opy_ (u"ࠦࡉࡧࡴࡢࠢࡸࡴࡱࡵࡡࡥࠢࡷࡳࠥࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠤࠧ⅄") + product + bstack111l11_opy_ (u"ࠧࠦࡦࡢ࡫࡯ࡩࡩࠦࡤࡶࡧࠣࡸࡴࠦࡳࡰ࡯ࡨࠤࡪࡸࡲࡰࡴࠥⅅ"))
    @classmethod
    def bstack1llll1l1lll1_opy_(cls):
        if cls.bstack1llllll1l111_opy_ is not None:
            return
        cls.bstack1llllll1l111_opy_ = bstack1llllll1l11l_opy_(cls.bstack1llll1l1l1l1_opy_)
        cls.bstack1llllll1l111_opy_.start()
    @classmethod
    def bstack111l1111ll_opy_(cls):
        if cls.bstack1llllll1l111_opy_ is None:
            return
        cls.bstack1llllll1l111_opy_.shutdown()
    @classmethod
    @error_handler(class_method=True)
    def bstack1llll1l1l1l1_opy_(cls, bstack111l11llll_opy_, event_url=bstack111l11_opy_ (u"࠭ࡡࡱ࡫࠲ࡺ࠶࠵ࡢࡢࡶࡦ࡬ࠬⅆ")):
        config = {
            bstack111l11_opy_ (u"ࠧࡩࡧࡤࡨࡪࡸࡳࠨⅇ"): cls.default_headers()
        }
        logger.debug(bstack111l11_opy_ (u"ࠣࡲࡲࡷࡹࡥࡤࡢࡶࡤ࠾࡙ࠥࡥ࡯ࡦ࡬ࡲ࡬ࠦࡤࡢࡶࡤࠤࡹࡵࠠࡵࡧࡶࡸ࡭ࡻࡢࠡࡨࡲࡶࠥ࡫ࡶࡦࡰࡷࡷࠥࢁࡽࠣⅈ").format(bstack111l11_opy_ (u"ࠩ࠯ࠤࠬⅉ").join([event[bstack111l11_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫ࠧ⅊")] for event in bstack111l11llll_opy_])))
        response = bstack11ll1llll_opy_(bstack111l11_opy_ (u"ࠫࡕࡕࡓࡕࠩ⅋"), cls.request_url(event_url), bstack111l11llll_opy_, config)
        bstack11ll11ll1l1_opy_ = response.json()
    @classmethod
    def bstack1ll1l1ll_opy_(cls, bstack111l11llll_opy_, event_url=bstack111l11_opy_ (u"ࠬࡧࡰࡪ࠱ࡹ࠵࠴ࡨࡡࡵࡥ࡫ࠫ⅌")):
        logger.debug(bstack111l11_opy_ (u"ࠨࡳࡦࡰࡧࡣࡩࡧࡴࡢ࠼ࠣࡅࡹࡺࡥ࡮ࡲࡷ࡭ࡳ࡭ࠠࡵࡱࠣࡥࡩࡪࠠࡥࡣࡷࡥࠥࡺ࡯ࠡࡤࡤࡸࡨ࡮ࠠࡸ࡫ࡷ࡬ࠥ࡫ࡶࡦࡰࡷࡣࡹࡿࡰࡦ࠼ࠣࡿࢂࠨ⅍").format(bstack111l11llll_opy_[bstack111l11_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠫⅎ")]))
        if not bstack1ll1111l1l_opy_.bstack1llll1ll1111_opy_(bstack111l11llll_opy_[bstack111l11_opy_ (u"ࠨࡧࡹࡩࡳࡺ࡟ࡵࡻࡳࡩࠬ⅏")]):
            logger.debug(bstack111l11_opy_ (u"ࠤࡶࡩࡳࡪ࡟ࡥࡣࡷࡥ࠿ࠦࡎࡰࡶࠣࡥࡩࡪࡩ࡯ࡩࠣࡨࡦࡺࡡࠡࡹ࡬ࡸ࡭ࠦࡥࡷࡧࡱࡸࡤࡺࡹࡱࡧ࠽ࠤࢀࢃࠢ⅐").format(bstack111l11llll_opy_[bstack111l11_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫ࠧ⅑")]))
            return
        bstack111l111l_opy_ = bstack1ll1111l1l_opy_.bstack1llll11lll11_opy_(bstack111l11llll_opy_[bstack111l11_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥࠨ⅒")], bstack111l11llll_opy_.get(bstack111l11_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴࠧ⅓")))
        if bstack111l111l_opy_ != None:
            if bstack111l11llll_opy_.get(bstack111l11_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࠨ⅔")) != None:
                bstack111l11llll_opy_[bstack111l11_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࠩ⅕")][bstack111l11_opy_ (u"ࠨࡲࡵࡳࡩࡻࡣࡵࡡࡰࡥࡵ࠭⅖")] = bstack111l111l_opy_
            else:
                bstack111l11llll_opy_[bstack111l11_opy_ (u"ࠩࡳࡶࡴࡪࡵࡤࡶࡢࡱࡦࡶࠧ⅗")] = bstack111l111l_opy_
        if event_url == bstack111l11_opy_ (u"ࠪࡥࡵ࡯࠯ࡷ࠳࠲ࡦࡦࡺࡣࡩࠩ⅘"):
            cls.bstack1llll1l1lll1_opy_()
            logger.debug(bstack111l11_opy_ (u"ࠦࡸ࡫࡮ࡥࡡࡧࡥࡹࡧ࠺ࠡࡃࡧࡨ࡮ࡴࡧࠡࡦࡤࡸࡦࠦࡴࡰࠢࡥࡥࡹࡩࡨࠡࡹ࡬ࡸ࡭ࠦࡥࡷࡧࡱࡸࡤࡺࡹࡱࡧ࠽ࠤࢀࢃࠢ⅙").format(bstack111l11llll_opy_[bstack111l11_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡹࡿࡰࡦࠩ⅚")]))
            cls.bstack1llllll1l111_opy_.add(bstack111l11llll_opy_)
        elif event_url == bstack111l11_opy_ (u"࠭ࡡࡱ࡫࠲ࡺ࠶࠵ࡳࡤࡴࡨࡩࡳࡹࡨࡰࡶࡶࠫ⅛"):
            cls.bstack1llll1l1l1l1_opy_([bstack111l11llll_opy_], event_url)
    @classmethod
    @error_handler(class_method=True)
    def bstack11l1ll111_opy_(cls, logs):
        for log in logs:
            bstack1llll1l1l11l_opy_ = {
                bstack111l11_opy_ (u"ࠧ࡬࡫ࡱࡨࠬ⅜"): bstack111l11_opy_ (u"ࠨࡖࡈࡗ࡙ࡥࡌࡐࡉࠪ⅝"),
                bstack111l11_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨ⅞"): log[bstack111l11_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩ⅟")],
                bstack111l11_opy_ (u"ࠫࡹ࡯࡭ࡦࡵࡷࡥࡲࡶࠧⅠ"): log[bstack111l11_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨⅡ")],
                bstack111l11_opy_ (u"࠭ࡨࡵࡶࡳࡣࡷ࡫ࡳࡱࡱࡱࡷࡪ࠭Ⅲ"): {},
                bstack111l11_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨⅣ"): log[bstack111l11_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩⅤ")],
            }
            if bstack111l11_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩⅥ") in log:
                bstack1llll1l1l11l_opy_[bstack111l11_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪⅦ")] = log[bstack111l11_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫⅧ")]
            elif bstack111l11_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬⅨ") in log:
                bstack1llll1l1l11l_opy_[bstack111l11_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭Ⅹ")] = log[bstack111l11_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧⅪ")]
            cls.bstack1ll1l1ll_opy_({
                bstack111l11_opy_ (u"ࠨࡧࡹࡩࡳࡺ࡟ࡵࡻࡳࡩࠬⅫ"): bstack111l11_opy_ (u"ࠩࡏࡳ࡬ࡉࡲࡦࡣࡷࡩࡩ࠭Ⅼ"),
                bstack111l11_opy_ (u"ࠪࡰࡴ࡭ࡳࠨⅭ"): [bstack1llll1l1l11l_opy_]
            })
    @classmethod
    @error_handler(class_method=True)
    def bstack1llll1l11l11_opy_(cls, steps):
        bstack1llll11lllll_opy_ = []
        for step in steps:
            bstack1llll11ll1ll_opy_ = {
                bstack111l11_opy_ (u"ࠫࡰ࡯࡮ࡥࠩⅮ"): bstack111l11_opy_ (u"࡚ࠬࡅࡔࡖࡢࡗ࡙ࡋࡐࠨⅯ"),
                bstack111l11_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬⅰ"): step[bstack111l11_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭ⅱ")],
                bstack111l11_opy_ (u"ࠨࡶ࡬ࡱࡪࡹࡴࡢ࡯ࡳࠫⅲ"): step[bstack111l11_opy_ (u"ࠩࡷ࡭ࡲ࡫ࡳࡵࡣࡰࡴࠬⅳ")],
                bstack111l11_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫⅴ"): step[bstack111l11_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬⅵ")],
                bstack111l11_opy_ (u"ࠬࡪࡵࡳࡣࡷ࡭ࡴࡴࠧⅶ"): step[bstack111l11_opy_ (u"࠭ࡤࡶࡴࡤࡸ࡮ࡵ࡮ࠨⅷ")]
            }
            if bstack111l11_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧⅸ") in step:
                bstack1llll11ll1ll_opy_[bstack111l11_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨⅹ")] = step[bstack111l11_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩⅺ")]
            elif bstack111l11_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪⅻ") in step:
                bstack1llll11ll1ll_opy_[bstack111l11_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫⅼ")] = step[bstack111l11_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬⅽ")]
            bstack1llll11lllll_opy_.append(bstack1llll11ll1ll_opy_)
        cls.bstack1ll1l1ll_opy_({
            bstack111l11_opy_ (u"࠭ࡥࡷࡧࡱࡸࡤࡺࡹࡱࡧࠪⅾ"): bstack111l11_opy_ (u"ࠧࡍࡱࡪࡇࡷ࡫ࡡࡵࡧࡧࠫⅿ"),
            bstack111l11_opy_ (u"ࠨ࡮ࡲ࡫ࡸ࠭ↀ"): bstack1llll11lllll_opy_
        })
    @classmethod
    @error_handler(class_method=True)
    @measure(event_name=EVENTS.bstack1ll1lll111_opy_, stage=STAGE.bstack111lllll1_opy_)
    def bstack111ll11l_opy_(cls, screenshot):
        cls.bstack1ll1l1ll_opy_({
            bstack111l11_opy_ (u"ࠩࡨࡺࡪࡴࡴࡠࡶࡼࡴࡪ࠭ↁ"): bstack111l11_opy_ (u"ࠪࡐࡴ࡭ࡃࡳࡧࡤࡸࡪࡪࠧↂ"),
            bstack111l11_opy_ (u"ࠫࡱࡵࡧࡴࠩↃ"): [{
                bstack111l11_opy_ (u"ࠬࡱࡩ࡯ࡦࠪↄ"): bstack111l11_opy_ (u"࠭ࡔࡆࡕࡗࡣࡘࡉࡒࡆࡇࡑࡗࡍࡕࡔࠨↅ"),
                bstack111l11_opy_ (u"ࠧࡵ࡫ࡰࡩࡸࡺࡡ࡮ࡲࠪↆ"): datetime.datetime.utcnow().isoformat() + bstack111l11_opy_ (u"ࠨ࡜ࠪↇ"),
                bstack111l11_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪↈ"): screenshot[bstack111l11_opy_ (u"ࠪ࡭ࡲࡧࡧࡦࠩ↉")],
                bstack111l11_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ↊"): screenshot[bstack111l11_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ↋")]
            }]
        }, event_url=bstack111l11_opy_ (u"࠭ࡡࡱ࡫࠲ࡺ࠶࠵ࡳࡤࡴࡨࡩࡳࡹࡨࡰࡶࡶࠫ↌"))
    @classmethod
    @error_handler(class_method=True)
    def bstack1ll111l1ll_opy_(cls, driver):
        current_test_uuid = cls.current_test_uuid()
        if not current_test_uuid:
            return
        cls.bstack1ll1l1ll_opy_({
            bstack111l11_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠫ↍"): bstack111l11_opy_ (u"ࠨࡅࡅࡘࡘ࡫ࡳࡴ࡫ࡲࡲࡈࡸࡥࡢࡶࡨࡨࠬ↎"),
            bstack111l11_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࠫ↏"): {
                bstack111l11_opy_ (u"ࠥࡹࡺ࡯ࡤࠣ←"): cls.current_test_uuid(),
                bstack111l11_opy_ (u"ࠦ࡮ࡴࡴࡦࡩࡵࡥࡹ࡯࡯࡯ࡵࠥ↑"): cls.bstack111ll11l1l_opy_(driver)
            }
        })
    @classmethod
    def bstack111ll11l11_opy_(cls, event: str, bstack111l11llll_opy_: bstack111l11l1ll_opy_):
        bstack111l1l1l11_opy_ = {
            bstack111l11_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡹࡿࡰࡦࠩ→"): event,
            bstack111l11llll_opy_.bstack111l11111l_opy_(): bstack111l11llll_opy_.bstack1111ll1l1l_opy_(event)
        }
        cls.bstack1ll1l1ll_opy_(bstack111l1l1l11_opy_)
        result = getattr(bstack111l11llll_opy_, bstack111l11_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭↓"), None)
        if event == bstack111l11_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡔࡶࡤࡶࡹ࡫ࡤࠨ↔"):
            threading.current_thread().bstackTestMeta = {bstack111l11_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ↕"): bstack111l11_opy_ (u"ࠩࡳࡩࡳࡪࡩ࡯ࡩࠪ↖")}
        elif event == bstack111l11_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬ↗"):
            threading.current_thread().bstackTestMeta = {bstack111l11_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ↘"): getattr(result, bstack111l11_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬ↙"), bstack111l11_opy_ (u"࠭ࠧ↚"))}
    @classmethod
    def on(cls):
        if (os.environ.get(bstack111l11_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠫ↛"), None) is None or os.environ[bstack111l11_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡌ࡚ࡘࠬ↜")] == bstack111l11_opy_ (u"ࠤࡱࡹࡱࡲࠢ↝")) and (os.environ.get(bstack111l11_opy_ (u"ࠪࡆࡘࡥࡁ࠲࠳࡜ࡣࡏ࡝ࡔࠨ↞"), None) is None or os.environ[bstack111l11_opy_ (u"ࠫࡇ࡙࡟ࡂ࠳࠴࡝ࡤࡐࡗࡕࠩ↟")] == bstack111l11_opy_ (u"ࠧࡴࡵ࡭࡮ࠥ↠")):
            return False
        return True
    @staticmethod
    def bstack1llll1ll11l1_opy_(func):
        def wrap(*args, **kwargs):
            if bstack111l1ll1_opy_.on():
                return func(*args, **kwargs)
            return
        return wrap
    @staticmethod
    def default_headers():
        headers = {
            bstack111l11_opy_ (u"࠭ࡃࡰࡰࡷࡩࡳࡺ࠭ࡕࡻࡳࡩࠬ↡"): bstack111l11_opy_ (u"ࠧࡢࡲࡳࡰ࡮ࡩࡡࡵ࡫ࡲࡲ࠴ࡰࡳࡰࡰࠪ↢"),
            bstack111l11_opy_ (u"ࠨ࡚࠰ࡆࡘ࡚ࡁࡄࡍ࠰ࡘࡊ࡙ࡔࡐࡒࡖࠫ↣"): bstack111l11_opy_ (u"ࠩࡷࡶࡺ࡫ࠧ↤")
        }
        if os.environ.get(bstack111l11_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢࡎ࡜࡚ࠧ↥"), None):
            headers[bstack111l11_opy_ (u"ࠫࡆࡻࡴࡩࡱࡵ࡭ࡿࡧࡴࡪࡱࡱࠫ↦")] = bstack111l11_opy_ (u"ࠬࡈࡥࡢࡴࡨࡶࠥࢁࡽࠨ↧").format(os.environ[bstack111l11_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠥ↨")])
        return headers
    @staticmethod
    def request_url(url):
        return bstack111l11_opy_ (u"ࠧࡼࡿ࠲ࡿࢂ࠭↩").format(bstack1llll11lll1l_opy_, url)
    @staticmethod
    def current_test_uuid():
        return getattr(threading.current_thread(), bstack111l11_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡶࡷ࡬ࡨࠬ↪"), None)
    @staticmethod
    def bstack111ll11l1l_opy_(driver):
        return {
            bstack111lll1l111_opy_(): bstack11l1111l1ll_opy_(driver)
        }
    @staticmethod
    def bstack1llll1l11ll1_opy_(exception_info, report):
        return [{bstack111l11_opy_ (u"ࠩࡥࡥࡨࡱࡴࡳࡣࡦࡩࠬ↫"): [exception_info.exconly(), report.longreprtext]}]
    @staticmethod
    def bstack1111111l1l_opy_(typename):
        if bstack111l11_opy_ (u"ࠥࡅࡸࡹࡥࡳࡶ࡬ࡳࡳࠨ↬") in typename:
            return bstack111l11_opy_ (u"ࠦࡆࡹࡳࡦࡴࡷ࡭ࡴࡴࡅࡳࡴࡲࡶࠧ↭")
        return bstack111l11_opy_ (u"࡛ࠧ࡮ࡩࡣࡱࡨࡱ࡫ࡤࡆࡴࡵࡳࡷࠨ↮")