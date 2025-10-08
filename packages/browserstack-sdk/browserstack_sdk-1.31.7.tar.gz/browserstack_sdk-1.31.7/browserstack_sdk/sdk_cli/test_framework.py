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
from enum import Enum
import os
import threading
import traceback
from typing import Dict, List, Any, Callable, Tuple, Union
import abc
from datetime import datetime, timezone
from dataclasses import dataclass
from browserstack_sdk.sdk_cli.bstack1llllllllll_opy_ import bstack1111111111_opy_
from browserstack_sdk.sdk_cli.bstack1llll1ll111_opy_ import bstack1lllll11l11_opy_, bstack1llll1lllll_opy_
class bstack1lll1lll111_opy_(Enum):
    PRE = 0
    POST = 1
    def __repr__(self) -> str:
        return bstack111l11_opy_ (u"࡚ࠧࡥࡴࡶࡋࡳࡴࡱࡓࡵࡣࡷࡩ࠳ࢁࡽࠣᗉ").format(self.name)
class bstack1lll11ll111_opy_(Enum):
    NONE = 0
    BEFORE_ALL = 1
    LOG = 2
    SETUP_FIXTURE = 3
    INIT_TEST = 4
    BEFORE_EACH = 5
    AFTER_EACH = 6
    TEST = 7
    STEP = 8
    LOG_REPORT = 9
    AFTER_ALL = 10
    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.value == other.value
        return NotImplemented
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented
    def __repr__(self) -> str:
        return bstack111l11_opy_ (u"ࠨࡔࡦࡵࡷࡊࡷࡧ࡭ࡦࡹࡲࡶࡰ࡙ࡴࡢࡶࡨ࠲ࢀࢃࠢᗊ").format(self.name)
class bstack1lll1llll1l_opy_(bstack1lllll11l11_opy_):
    bstack1ll11l1111l_opy_: List[str]
    bstack1l11111111l_opy_: Dict[str, str]
    state: bstack1lll11ll111_opy_
    bstack1lllll1ll11_opy_: datetime
    bstack1lllll11lll_opy_: datetime
    def __init__(
        self,
        context: bstack1llll1lllll_opy_,
        bstack1ll11l1111l_opy_: List[str],
        bstack1l11111111l_opy_: Dict[str, str],
        state=bstack1lll11ll111_opy_.NONE,
    ):
        super().__init__(context)
        self.bstack1ll11l1111l_opy_ = bstack1ll11l1111l_opy_
        self.bstack1l11111111l_opy_ = bstack1l11111111l_opy_
        self.state = state
        self.bstack1lllll1ll11_opy_ = datetime.now(tz=timezone.utc)
        self.bstack1lllll11lll_opy_ = datetime.now(tz=timezone.utc)
    def bstack1llll1l11l1_opy_(self, bstack1llllll1l11_opy_: bstack1lll11ll111_opy_):
        bstack1lllllll111_opy_ = bstack1lll11ll111_opy_(bstack1llllll1l11_opy_).name
        if not bstack1lllllll111_opy_:
            return False
        if bstack1llllll1l11_opy_ == self.state:
            return False
        self.state = bstack1llllll1l11_opy_
        self.bstack1lllll11lll_opy_ = datetime.now(tz=timezone.utc)
        return True
@dataclass
class bstack1l111l1l111_opy_:
    test_framework_name: str
    test_framework_version: str
    platform_index: int
@dataclass
class bstack1ll1lll1111_opy_:
    kind: str
    message: str
    level: Union[None, str] = None
    timestamp: Union[None, datetime] = datetime.now(tz=timezone.utc)
    fileName: str = None
    bstack1l1lll111ll_opy_: int = None
    bstack1l1ll1l11l1_opy_: str = None
    bstack11l1l1_opy_: str = None
    bstack1l1lllll1_opy_: str = None
    bstack1l1ll1111l1_opy_: str = None
    bstack1l111l11lll_opy_: str = None
class TestFramework(abc.ABC):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    bstack1ll11l111l1_opy_ = bstack111l11_opy_ (u"ࠢࡵࡧࡶࡸࡤࡻࡵࡪࡦࠥᗋ")
    bstack1l1111lll1l_opy_ = bstack111l11_opy_ (u"ࠣࡶࡨࡷࡹࡥࡩࡥࠤᗌ")
    bstack1ll11lll11l_opy_ = bstack111l11_opy_ (u"ࠤࡷࡩࡸࡺ࡟࡯ࡣࡰࡩࠧᗍ")
    bstack11lllll1ll1_opy_ = bstack111l11_opy_ (u"ࠥࡸࡪࡹࡴࡠࡨ࡬ࡰࡪࡥࡰࡢࡶ࡫ࠦᗎ")
    bstack1l111llll11_opy_ = bstack111l11_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡷࡥ࡬ࡹࠢᗏ")
    bstack1l11lllll1l_opy_ = bstack111l11_opy_ (u"ࠧࡺࡥࡴࡶࡢࡶࡪࡹࡵ࡭ࡶࠥᗐ")
    bstack1l1ll111l11_opy_ = bstack111l11_opy_ (u"ࠨࡴࡦࡵࡷࡣࡷ࡫ࡳࡶ࡮ࡷࡣࡦࡺࠢᗑ")
    bstack1l1lll1l11l_opy_ = bstack111l11_opy_ (u"ࠢࡵࡧࡶࡸࡤࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠤᗒ")
    bstack1l1lll11ll1_opy_ = bstack111l11_opy_ (u"ࠣࡶࡨࡷࡹࡥࡥ࡯ࡦࡨࡨࡤࡧࡴࠣᗓ")
    bstack1l11111ll1l_opy_ = bstack111l11_opy_ (u"ࠤࡷࡩࡸࡺ࡟࡭ࡱࡦࡥࡹ࡯࡯࡯ࠤᗔ")
    bstack1ll111l111l_opy_ = bstack111l11_opy_ (u"ࠥࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦࠤᗕ")
    bstack1l1l1l11ll1_opy_ = bstack111l11_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡼࡥࡳࡵ࡬ࡳࡳࠨᗖ")
    bstack11lllll1l1l_opy_ = bstack111l11_opy_ (u"ࠧࡺࡥࡴࡶࡢࡧࡴࡪࡥࠣᗗ")
    bstack1l1l11lll1l_opy_ = bstack111l11_opy_ (u"ࠨࡴࡦࡵࡷࡣࡷ࡫ࡲࡶࡰࡢࡲࡦࡳࡥࠣᗘ")
    bstack1ll1111lll1_opy_ = bstack111l11_opy_ (u"ࠢࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡡ࡬ࡲࡩ࡫ࡸࠣᗙ")
    bstack1l11llll11l_opy_ = bstack111l11_opy_ (u"ࠣࡶࡨࡷࡹࡥࡦࡢ࡫࡯ࡹࡷ࡫ࠢᗚ")
    bstack1l111l111ll_opy_ = bstack111l11_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡧࡣ࡬ࡰࡺࡸࡥࡠࡶࡼࡴࡪࠨᗛ")
    bstack1l11111lll1_opy_ = bstack111l11_opy_ (u"ࠥࡸࡪࡹࡴࡠ࡮ࡲ࡫ࡸࠨᗜ")
    bstack1l1111l1ll1_opy_ = bstack111l11_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡰࡩࡹࡧࠢᗝ")
    bstack11llll1l1ll_opy_ = bstack111l11_opy_ (u"ࠬࡺࡥࡴࡶࡢࡷࡨࡵࡰࡦࡵࠪᗞ")
    bstack1l11l11lll1_opy_ = bstack111l11_opy_ (u"ࠨࡡࡶࡶࡲࡱࡦࡺࡥࡠࡵࡨࡷࡸ࡯࡯࡯ࡡࡱࡥࡲ࡫ࠢᗟ")
    bstack11lllll1l11_opy_ = bstack111l11_opy_ (u"ࠢࡦࡸࡨࡲࡹࡥࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠥᗠ")
    bstack1l11111llll_opy_ = bstack111l11_opy_ (u"ࠣࡧࡹࡩࡳࡺ࡟ࡦࡰࡧࡩࡩࡥࡡࡵࠤᗡ")
    bstack1l1111l11l1_opy_ = bstack111l11_opy_ (u"ࠤ࡫ࡳࡴࡱ࡟ࡪࡦࠥᗢ")
    bstack1l111l11ll1_opy_ = bstack111l11_opy_ (u"ࠥ࡬ࡴࡵ࡫ࡠࡴࡨࡷࡺࡲࡴࠣᗣ")
    bstack1l111l1lll1_opy_ = bstack111l11_opy_ (u"ࠦ࡭ࡵ࡯࡬ࡡ࡯ࡳ࡬ࡹࠢᗤ")
    bstack1l1111ll111_opy_ = bstack111l11_opy_ (u"ࠧ࡮࡯ࡰ࡭ࡢࡲࡦࡳࡥࠣᗥ")
    bstack1l1111l1l1l_opy_ = bstack111l11_opy_ (u"ࠨ࡬ࡰࡩࡶࠦᗦ")
    bstack11llll1ll1l_opy_ = bstack111l11_opy_ (u"ࠢࡤࡷࡶࡸࡴࡳ࡟࡮ࡧࡷࡥࡩࡧࡴࡢࠤᗧ")
    bstack1l111l11l11_opy_ = bstack111l11_opy_ (u"ࠣࡲࡨࡲࡩ࡯࡮ࡨࠤᗨ")
    bstack1l1111111l1_opy_ = bstack111l11_opy_ (u"ࠤࡳࡩࡳࡪࡩ࡯ࡩࠥᗩ")
    bstack1l1l1ll111l_opy_ = bstack111l11_opy_ (u"ࠥࡘࡊ࡙ࡔࡠࡕࡆࡖࡊࡋࡎࡔࡊࡒࡘࠧᗪ")
    bstack1l1l1lll1l1_opy_ = bstack111l11_opy_ (u"࡙ࠦࡋࡓࡕࡡࡏࡓࡌࠨᗫ")
    bstack1l1lll11lll_opy_ = bstack111l11_opy_ (u"࡚ࠧࡅࡔࡖࡢࡅ࡙࡚ࡁࡄࡊࡐࡉࡓ࡚ࠢᗬ")
    bstack1lllll111l1_opy_: Dict[str, bstack1lll1llll1l_opy_] = dict()
    bstack11llll11l11_opy_: Dict[str, List[Callable]] = dict()
    bstack1ll11l1111l_opy_: List[str]
    bstack1l11111111l_opy_: Dict[str, str]
    def __init__(
        self,
        bstack1ll11l1111l_opy_: List[str],
        bstack1l11111111l_opy_: Dict[str, str],
        bstack1llllllllll_opy_: bstack1111111111_opy_
    ):
        self.bstack1ll11l1111l_opy_ = bstack1ll11l1111l_opy_
        self.bstack1l11111111l_opy_ = bstack1l11111111l_opy_
        self.bstack1llllllllll_opy_ = bstack1llllllllll_opy_
    def track_event(
        self,
        context: bstack1l111l1l111_opy_,
        test_framework_state: bstack1lll11ll111_opy_,
        test_hook_state: bstack1lll1lll111_opy_,
        *args,
        **kwargs,
    ):
        self.logger.debug(bstack111l11_opy_ (u"ࠨࡴࡳࡣࡦ࡯ࡤ࡫ࡶࡦࡰࡷ࠾ࠥࡺࡥࡴࡶࡢࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡳࡵࡣࡷࡩࡂࢁࡽࠡࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡣࡸࡺࡡࡵࡧࡀࡿࢂࠦࡡࡳࡩࡶࡁࢀࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࡼࡿࠥᗭ").format(test_framework_state,test_hook_state,args,kwargs))
    def bstack11llllllll1_opy_(
        self,
        instance: bstack1lll1llll1l_opy_,
        bstack1llllll1l1l_opy_: Tuple[bstack1lll11ll111_opy_, bstack1lll1lll111_opy_],
        *args,
        **kwargs,
    ):
        bstack1l11l111111_opy_ = TestFramework.bstack1l11l111l11_opy_(bstack1llllll1l1l_opy_)
        if not bstack1l11l111111_opy_ in TestFramework.bstack11llll11l11_opy_:
            return
        self.logger.debug(bstack111l11_opy_ (u"ࠢࡪࡰࡹࡳࡰ࡯࡮ࡨࠢࡾࢁࠥࡩࡡ࡭࡮ࡥࡥࡨࡱࡳࠣᗮ").format(len(TestFramework.bstack11llll11l11_opy_[bstack1l11l111111_opy_])))
        for callback in TestFramework.bstack11llll11l11_opy_[bstack1l11l111111_opy_]:
            try:
                callback(self, instance, bstack1llllll1l1l_opy_, *args, **kwargs)
            except Exception as e:
                self.logger.error(bstack111l11_opy_ (u"ࠣࡧࡵࡶࡴࡸࠠࡪࡰࡹࡳࡰ࡯࡮ࡨࠢࡦࡥࡱࡲࡢࡢࡥ࡮࠾ࠥࢁࡽࠣᗯ").format(e))
                traceback.print_exc()
    @abc.abstractmethod
    def bstack1l1ll1ll111_opy_(self):
        return
    @abc.abstractmethod
    def bstack1l1ll1lll11_opy_(self, instance, bstack1llllll1l1l_opy_):
        return
    @abc.abstractmethod
    def bstack1l1lll11l11_opy_(self, instance, bstack1llllll1l1l_opy_):
        return
    @staticmethod
    def bstack1lllllll1ll_opy_(target: object, strict=True):
        if target is None:
            return None
        ctx = bstack1lllll11l11_opy_.create_context(target)
        instance = TestFramework.bstack1lllll111l1_opy_.get(ctx.id, None)
        if instance and instance.bstack1llllll1ll1_opy_(target):
            return instance
        return instance if instance and not strict else None
    @staticmethod
    def bstack1l1ll1l11ll_opy_(reverse=True) -> List[bstack1lll1llll1l_opy_]:
        thread_id = threading.get_ident()
        process_id = os.getpid()
        return sorted(
            filter(
                lambda t: t.context.thread_id == thread_id
                and t.context.process_id == process_id,
                TestFramework.bstack1lllll111l1_opy_.values(),
            ),
            key=lambda t: t.bstack1lllll1ll11_opy_,
            reverse=reverse,
        )
    @staticmethod
    def bstack1llllll1111_opy_(ctx: bstack1llll1lllll_opy_, reverse=True) -> List[bstack1lll1llll1l_opy_]:
        return sorted(
            filter(
                lambda t: t.context.thread_id == ctx.thread_id
                and t.context.process_id == ctx.process_id,
                TestFramework.bstack1lllll111l1_opy_.values(),
            ),
            key=lambda t: t.bstack1lllll1ll11_opy_,
            reverse=reverse,
        )
    @staticmethod
    def bstack1lllll111ll_opy_(instance: bstack1lll1llll1l_opy_, key: str):
        return instance and key in instance.data
    @staticmethod
    def bstack1llll1l11ll_opy_(instance: bstack1lll1llll1l_opy_, key: str, default_value=None):
        return instance.data.get(key, default_value) if instance else default_value
    @staticmethod
    def bstack1llll1l11l1_opy_(instance: bstack1lll1llll1l_opy_, key: str, value: Any):
        TestFramework.logger.debug(bstack111l11_opy_ (u"ࠤࡶࡩࡹࡥࡳࡵࡣࡷࡩ࠿ࠦࡩ࡯ࡵࡷࡥࡳࡩࡥ࠾ࡽࢀࠤࡰ࡫ࡹ࠾ࡽࢀࠤࡻࡧ࡬ࡶࡧࡀࡿࢂࠨᗰ").format(instance.ref(),key,value))
        instance.data[key] = value
        return True
    @staticmethod
    def bstack11lllllll1l_opy_(instance: bstack1lll1llll1l_opy_, entries: Dict[str, Any]):
        TestFramework.logger.debug(bstack111l11_opy_ (u"ࠥࡷࡪࡺ࡟ࡴࡶࡤࡸࡪࡥࡥ࡯ࡶࡵ࡭ࡪࡹ࠺ࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡀࡿࢂࠦࡥ࡯ࡶࡵ࡭ࡪࡹ࠽ࡼࡿࠥᗱ").format(instance.ref(),entries,))
        instance.data.update(entries)
        return True
    @staticmethod
    def bstack11lll1lll11_opy_(instance: bstack1lll11ll111_opy_, key: str, value: Any):
        TestFramework.logger.debug(bstack111l11_opy_ (u"ࠦࡺࡶࡤࡢࡶࡨࡣࡸࡺࡡࡵࡧ࠽ࠤ࡮ࡴࡳࡵࡣࡱࡧࡪࡃࡻࡾࠢ࡮ࡩࡾࡃࡻࡾࠢࡹࡥࡱࡻࡥ࠾ࡽࢀࠦᗲ").format(instance.ref(),key,value))
        instance.data.update(key, value)
        return True
    @staticmethod
    def get_data(key: str, target: object, strict=True, default_value=None):
        instance = TestFramework.bstack1lllllll1ll_opy_(target, strict)
        return TestFramework.bstack1llll1l11ll_opy_(instance, key, default_value)
    @staticmethod
    def set_data(key: str, value: Any, target: object, strict=True):
        instance = TestFramework.bstack1lllllll1ll_opy_(target, strict)
        if not instance:
            return False
        instance.data[key] = value
        return True
    @staticmethod
    def bstack1l111l1ll1l_opy_(instance: bstack1lll1llll1l_opy_, key: str, value: object):
        if instance == None:
            return
        instance.data[key] = value
    @staticmethod
    def bstack1l11111ll11_opy_(instance: bstack1lll1llll1l_opy_, key: str):
        return instance.data[key]
    @staticmethod
    def bstack1l11l111l11_opy_(bstack1llllll1l1l_opy_: Tuple[bstack1lll11ll111_opy_, bstack1lll1lll111_opy_]):
        return bstack111l11_opy_ (u"ࠧࡀࠢᗳ").join((bstack1lll11ll111_opy_(bstack1llllll1l1l_opy_[0]).name, bstack1lll1lll111_opy_(bstack1llllll1l1l_opy_[1]).name))
    @staticmethod
    def bstack1ll11llll1l_opy_(bstack1llllll1l1l_opy_: Tuple[bstack1lll11ll111_opy_, bstack1lll1lll111_opy_], callback: Callable):
        bstack1l11l111111_opy_ = TestFramework.bstack1l11l111l11_opy_(bstack1llllll1l1l_opy_)
        TestFramework.logger.debug(bstack111l11_opy_ (u"ࠨࡳࡦࡶࡢ࡬ࡴࡵ࡫ࡠࡥࡤࡰࡱࡨࡡࡤ࡭࠽ࠤ࡭ࡵ࡯࡬ࡡࡵࡩ࡬࡯ࡳࡵࡴࡼࡣࡰ࡫ࡹ࠾ࡽࢀࠦᗴ").format(bstack1l11l111111_opy_))
        if not bstack1l11l111111_opy_ in TestFramework.bstack11llll11l11_opy_:
            TestFramework.bstack11llll11l11_opy_[bstack1l11l111111_opy_] = []
        TestFramework.bstack11llll11l11_opy_[bstack1l11l111111_opy_].append(callback)
    @staticmethod
    def bstack1l1lll11111_opy_(o):
        klass = o.__class__
        module = klass.__module__
        if module == bstack111l11_opy_ (u"ࠢࡣࡷ࡬ࡰࡹ࡯࡮ࡴࠤᗵ"):
            return klass.__qualname__
        return module + bstack111l11_opy_ (u"ࠣ࠰ࠥᗶ") + klass.__qualname__
    @staticmethod
    def bstack1l1lll1l1l1_opy_(obj, keys, default_value=None):
        return {k: getattr(obj, k, default_value) for k in keys}