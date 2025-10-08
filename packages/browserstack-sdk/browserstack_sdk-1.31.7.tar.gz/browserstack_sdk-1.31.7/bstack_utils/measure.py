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
import logging
from functools import wraps
from typing import Optional
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.bstack11l1l1111_opy_ import get_logger
from bstack_utils.bstack1l1l1l1111_opy_ import bstack1ll1l1ll1l1_opy_
bstack1l1l1l1111_opy_ = bstack1ll1l1ll1l1_opy_()
logger = get_logger(__name__)
def measure(event_name: EVENTS, stage: STAGE, hook_type: Optional[str] = None, bstack11l1l1lll1_opy_: Optional[str] = None):
    bstack111l11_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࡇࡩࡨࡵࡲࡢࡶࡲࡶࠥࡺ࡯ࠡ࡮ࡲ࡫ࠥࡺࡨࡦࠢࡶࡸࡦࡸࡴࠡࡶ࡬ࡱࡪࠦ࡯ࡧࠢࡤࠤ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࠦࡥࡹࡧࡦࡹࡹ࡯࡯࡯ࠌࠣࠤࠥࠦࡡ࡭ࡱࡱ࡫ࠥࡽࡩࡵࡪࠣࡩࡻ࡫࡮ࡵࠢࡱࡥࡲ࡫ࠠࡢࡰࡧࠤࡸࡺࡡࡨࡧ࠱ࠎࠥࠦࠠࠡࠤ᷺ࠥࠦ")
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            label: str = event_name.value
            bstack1ll1111l1l1_opy_: str = bstack1l1l1l1111_opy_.bstack11ll1l1l1ll_opy_(label)
            start_mark: str = label + bstack111l11_opy_ (u"ࠥ࠾ࡸࡺࡡࡳࡶࠥ᷻")
            end_mark: str = label + bstack111l11_opy_ (u"ࠦ࠿࡫࡮ࡥࠤ᷼")
            result = None
            try:
                if stage.value == STAGE.bstack11ll111ll1_opy_.value:
                    bstack1l1l1l1111_opy_.mark(start_mark)
                    result = func(*args, **kwargs)
                elif stage.value == STAGE.END.value:
                    result = func(*args, **kwargs)
                    bstack1l1l1l1111_opy_.end(label, start_mark, end_mark, status=True, failure=None,hook_type=hook_type,test_name=bstack11l1l1lll1_opy_)
                elif stage.value == STAGE.bstack111lllll1_opy_.value:
                    start_mark: str = bstack1ll1111l1l1_opy_ + bstack111l11_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸ᷽ࠧ")
                    end_mark: str = bstack1ll1111l1l1_opy_ + bstack111l11_opy_ (u"ࠨ࠺ࡦࡰࡧࠦ᷾")
                    bstack1l1l1l1111_opy_.mark(start_mark)
                    result = func(*args, **kwargs)
                    bstack1l1l1l1111_opy_.end(label, start_mark, end_mark, status=True, failure=None, hook_type=hook_type,test_name=bstack11l1l1lll1_opy_)
            except Exception as e:
                bstack1l1l1l1111_opy_.end(label, start_mark, end_mark, status=False, failure=str(e), hook_type=hook_type,
                                       test_name=bstack11l1l1lll1_opy_)
            return result
        return wrapper
    return decorator