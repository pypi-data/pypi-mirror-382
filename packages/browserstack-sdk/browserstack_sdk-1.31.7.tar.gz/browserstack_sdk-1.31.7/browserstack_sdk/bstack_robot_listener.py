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
import threading
from uuid import uuid4
from itertools import zip_longest
from collections import OrderedDict
from robot.libraries.BuiltIn import BuiltIn
from browserstack_sdk.bstack111l111lll_opy_ import RobotHandler
from bstack_utils.capture import bstack111ll11ll1_opy_
from bstack_utils.bstack111l1llll1_opy_ import bstack111l11l1ll_opy_, bstack111ll111l1_opy_, bstack111lll11l1_opy_
from bstack_utils.bstack111lll1111_opy_ import bstack1l1lll1ll1_opy_
from bstack_utils.bstack111l1lll11_opy_ import bstack111l1ll1_opy_
from bstack_utils.constants import *
from bstack_utils.helper import bstack1l11lllll1_opy_, bstack11ll11lll_opy_, Result, \
    error_handler, bstack1111ll11ll_opy_
class bstack_robot_listener:
    ROBOT_LISTENER_API_VERSION = 2
    _lock = threading.Lock()
    store = {
        bstack111l11_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤ࡮࡯ࡰ࡭ࡢࡹࡺ࡯ࡤࠨ྅"): [],
        bstack111l11_opy_ (u"ࠬ࡭࡬ࡰࡤࡤࡰࡤ࡮࡯ࡰ࡭ࡶࠫ྆"): [],
        bstack111l11_opy_ (u"࠭ࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡵࠪ྇"): []
    }
    bstack111l1l1lll_opy_ = []
    bstack1111lll11l_opy_ = []
    @staticmethod
    def bstack111l1lllll_opy_(log):
        if not ((isinstance(log[bstack111l11_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨྈ")], list) or (isinstance(log[bstack111l11_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩྉ")], dict)) and len(log[bstack111l11_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪྊ")])>0) or (isinstance(log[bstack111l11_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫྋ")], str) and log[bstack111l11_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬྌ")].strip())):
            return
        active = bstack1l1lll1ll1_opy_.bstack111ll1l1ll_opy_()
        log = {
            bstack111l11_opy_ (u"ࠬࡲࡥࡷࡧ࡯ࠫྍ"): log[bstack111l11_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬྎ")],
            bstack111l11_opy_ (u"ࠧࡵ࡫ࡰࡩࡸࡺࡡ࡮ࡲࠪྏ"): bstack1111ll11ll_opy_().isoformat() + bstack111l11_opy_ (u"ࠨ࡜ࠪྐ"),
            bstack111l11_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪྑ"): log[bstack111l11_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫྒ")],
        }
        if active:
            if active[bstack111l11_opy_ (u"ࠫࡹࡿࡰࡦࠩྒྷ")] == bstack111l11_opy_ (u"ࠬ࡮࡯ࡰ࡭ࠪྔ"):
                log[bstack111l11_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭ྕ")] = active[bstack111l11_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧྖ")]
            elif active[bstack111l11_opy_ (u"ࠨࡶࡼࡴࡪ࠭ྗ")] == bstack111l11_opy_ (u"ࠩࡷࡩࡸࡺࠧ྘"):
                log[bstack111l11_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪྙ")] = active[bstack111l11_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫྚ")]
        bstack111l1ll1_opy_.bstack11l1ll111_opy_([log])
    def __init__(self):
        self.messages = bstack1111ll111l_opy_()
        self._1111ll1ll1_opy_ = None
        self._1111lllll1_opy_ = None
        self._1111l1llll_opy_ = OrderedDict()
        self.bstack111ll1lll1_opy_ = bstack111ll11ll1_opy_(self.bstack111l1lllll_opy_)
    @error_handler(class_method=True)
    def start_suite(self, name, attrs):
        self.messages.bstack111l111111_opy_()
        if not self._1111l1llll_opy_.get(attrs.get(bstack111l11_opy_ (u"ࠬ࡯ࡤࠨྛ")), None):
            self._1111l1llll_opy_[attrs.get(bstack111l11_opy_ (u"࠭ࡩࡥࠩྜ"))] = {}
        bstack111l1111l1_opy_ = bstack111lll11l1_opy_(
                bstack111l111ll1_opy_=attrs.get(bstack111l11_opy_ (u"ࠧࡪࡦࠪྜྷ")),
                name=name,
                started_at=bstack11ll11lll_opy_(),
                file_path=os.path.relpath(attrs[bstack111l11_opy_ (u"ࠨࡵࡲࡹࡷࡩࡥࠨྞ")], start=os.getcwd()) if attrs.get(bstack111l11_opy_ (u"ࠩࡶࡳࡺࡸࡣࡦࠩྟ")) != bstack111l11_opy_ (u"ࠪࠫྠ") else bstack111l11_opy_ (u"ࠫࠬྡ"),
                framework=bstack111l11_opy_ (u"ࠬࡘ࡯ࡣࡱࡷࠫྡྷ")
            )
        threading.current_thread().current_suite_id = attrs.get(bstack111l11_opy_ (u"࠭ࡩࡥࠩྣ"), None)
        self._1111l1llll_opy_[attrs.get(bstack111l11_opy_ (u"ࠧࡪࡦࠪྤ"))][bstack111l11_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫྥ")] = bstack111l1111l1_opy_
    @error_handler(class_method=True)
    def end_suite(self, name, attrs):
        messages = self.messages.bstack111l11ll11_opy_()
        self._111l1l1l1l_opy_(messages)
        with self._lock:
            for bstack111l11ll1l_opy_ in self.bstack111l1l1lll_opy_:
                bstack111l11ll1l_opy_[bstack111l11_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࠫྦ")][bstack111l11_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡴࠩྦྷ")].extend(self.store[bstack111l11_opy_ (u"ࠫ࡬ࡲ࡯ࡣࡣ࡯ࡣ࡭ࡵ࡯࡬ࡵࠪྨ")])
                bstack111l1ll1_opy_.bstack1ll1l1ll_opy_(bstack111l11ll1l_opy_)
            self.bstack111l1l1lll_opy_ = []
            self.store[bstack111l11_opy_ (u"ࠬ࡭࡬ࡰࡤࡤࡰࡤ࡮࡯ࡰ࡭ࡶࠫྩ")] = []
    @error_handler(class_method=True)
    def start_test(self, name, attrs):
        self.bstack111ll1lll1_opy_.start()
        if not self._1111l1llll_opy_.get(attrs.get(bstack111l11_opy_ (u"࠭ࡩࡥࠩྪ")), None):
            self._1111l1llll_opy_[attrs.get(bstack111l11_opy_ (u"ࠧࡪࡦࠪྫ"))] = {}
        driver = bstack1l11lllll1_opy_(threading.current_thread(), bstack111l11_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡔࡧࡶࡷ࡮ࡵ࡮ࡅࡴ࡬ࡺࡪࡸࠧྫྷ"), None)
        bstack111l1llll1_opy_ = bstack111lll11l1_opy_(
            bstack111l111ll1_opy_=attrs.get(bstack111l11_opy_ (u"ࠩ࡬ࡨࠬྭ")),
            name=name,
            started_at=bstack11ll11lll_opy_(),
            file_path=os.path.relpath(attrs[bstack111l11_opy_ (u"ࠪࡷࡴࡻࡲࡤࡧࠪྮ")], start=os.getcwd()),
            scope=RobotHandler.bstack111l11lll1_opy_(attrs.get(bstack111l11_opy_ (u"ࠫࡸࡵࡵࡳࡥࡨࠫྯ"), None)),
            framework=bstack111l11_opy_ (u"ࠬࡘ࡯ࡣࡱࡷࠫྰ"),
            tags=attrs[bstack111l11_opy_ (u"࠭ࡴࡢࡩࡶࠫྱ")],
            hooks=self.store[bstack111l11_opy_ (u"ࠧࡨ࡮ࡲࡦࡦࡲ࡟ࡩࡱࡲ࡯ࡸ࠭ྲ")],
            bstack111l1lll1l_opy_=bstack111l1ll1_opy_.bstack111ll11l1l_opy_(driver) if driver and driver.session_id else {},
            meta={},
            code=bstack111l11_opy_ (u"ࠣࡽࢀࠤࡡࡴࠠࡼࡿࠥླ").format(bstack111l11_opy_ (u"ࠤࠣࠦྴ").join(attrs[bstack111l11_opy_ (u"ࠪࡸࡦ࡭ࡳࠨྵ")]), name) if attrs[bstack111l11_opy_ (u"ࠫࡹࡧࡧࡴࠩྶ")] else name
        )
        self._1111l1llll_opy_[attrs.get(bstack111l11_opy_ (u"ࠬ࡯ࡤࠨྷ"))][bstack111l11_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩྸ")] = bstack111l1llll1_opy_
        threading.current_thread().current_test_uuid = bstack111l1llll1_opy_.bstack1111llll1l_opy_()
        threading.current_thread().current_test_id = attrs.get(bstack111l11_opy_ (u"ࠧࡪࡦࠪྐྵ"), None)
        self.bstack111ll11l11_opy_(bstack111l11_opy_ (u"ࠨࡖࡨࡷࡹࡘࡵ࡯ࡕࡷࡥࡷࡺࡥࡥࠩྺ"), bstack111l1llll1_opy_)
    @error_handler(class_method=True)
    def end_test(self, name, attrs):
        self.bstack111ll1lll1_opy_.reset()
        bstack111l111l11_opy_ = bstack111l111l1l_opy_.get(attrs.get(bstack111l11_opy_ (u"ࠩࡶࡸࡦࡺࡵࡴࠩྻ")), bstack111l11_opy_ (u"ࠪࡷࡰ࡯ࡰࡱࡧࡧࠫྼ"))
        self._1111l1llll_opy_[attrs.get(bstack111l11_opy_ (u"ࠫ࡮ࡪࠧ྽"))][bstack111l11_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨ྾")].stop(time=bstack11ll11lll_opy_(), duration=int(attrs.get(bstack111l11_opy_ (u"࠭ࡥ࡭ࡣࡳࡷࡪࡪࡴࡪ࡯ࡨࠫ྿"), bstack111l11_opy_ (u"ࠧ࠱ࠩ࿀"))), result=Result(result=bstack111l111l11_opy_, exception=attrs.get(bstack111l11_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩ࿁")), bstack111ll11lll_opy_=[attrs.get(bstack111l11_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪ࿂"))]))
        self.bstack111ll11l11_opy_(bstack111l11_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬ࿃"), self._1111l1llll_opy_[attrs.get(bstack111l11_opy_ (u"ࠫ࡮ࡪࠧ࿄"))][bstack111l11_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨ࿅")], True)
        with self._lock:
            self.store[bstack111l11_opy_ (u"࠭ࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡵ࿆ࠪ")] = []
        threading.current_thread().current_test_uuid = None
        threading.current_thread().current_test_id = None
    @error_handler(class_method=True)
    def start_keyword(self, name, attrs):
        self.messages.bstack111l111111_opy_()
        current_test_id = bstack1l11lllll1_opy_(threading.current_thread(), bstack111l11_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡩࡥࠩ࿇"), None)
        bstack111l1ll111_opy_ = current_test_id if bstack1l11lllll1_opy_(threading.current_thread(), bstack111l11_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡪࡦࠪ࿈"), None) else bstack1l11lllll1_opy_(threading.current_thread(), bstack111l11_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡷࡺ࡯ࡴࡦࡡ࡬ࡨࠬ࿉"), None)
        if attrs.get(bstack111l11_opy_ (u"ࠪࡸࡾࡶࡥࠨ࿊"), bstack111l11_opy_ (u"ࠫࠬ࿋")).lower() in [bstack111l11_opy_ (u"ࠬࡹࡥࡵࡷࡳࠫ࿌"), bstack111l11_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮ࠨ࿍")]:
            hook_type = bstack1111ll1l11_opy_(attrs.get(bstack111l11_opy_ (u"ࠧࡵࡻࡳࡩࠬ࿎")), bstack1l11lllll1_opy_(threading.current_thread(), bstack111l11_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡶࡷ࡬ࡨࠬ࿏"), None))
            hook_name = bstack111l11_opy_ (u"ࠩࡾࢁࠬ࿐").format(attrs.get(bstack111l11_opy_ (u"ࠪ࡯ࡼࡴࡡ࡮ࡧࠪ࿑"), bstack111l11_opy_ (u"ࠫࠬ࿒")))
            if hook_type in [bstack111l11_opy_ (u"ࠬࡈࡅࡇࡑࡕࡉࡤࡇࡌࡍࠩ࿓"), bstack111l11_opy_ (u"࠭ࡁࡇࡖࡈࡖࡤࡇࡌࡍࠩ࿔")]:
                hook_name = bstack111l11_opy_ (u"ࠧ࡜ࡽࢀࡡࠥࢁࡽࠨ࿕").format(bstack1111ll11l1_opy_.get(hook_type), attrs.get(bstack111l11_opy_ (u"ࠨ࡭ࡺࡲࡦࡳࡥࠨ࿖"), bstack111l11_opy_ (u"ࠩࠪ࿗")))
            bstack1111ll1111_opy_ = bstack111ll111l1_opy_(
                bstack111l111ll1_opy_=bstack111l1ll111_opy_ + bstack111l11_opy_ (u"ࠪ࠱ࠬ࿘") + attrs.get(bstack111l11_opy_ (u"ࠫࡹࡿࡰࡦࠩ࿙"), bstack111l11_opy_ (u"ࠬ࠭࿚")).lower(),
                name=hook_name,
                started_at=bstack11ll11lll_opy_(),
                file_path=os.path.relpath(attrs.get(bstack111l11_opy_ (u"࠭ࡳࡰࡷࡵࡧࡪ࠭࿛")), start=os.getcwd()),
                framework=bstack111l11_opy_ (u"ࠧࡓࡱࡥࡳࡹ࠭࿜"),
                tags=attrs[bstack111l11_opy_ (u"ࠨࡶࡤ࡫ࡸ࠭࿝")],
                scope=RobotHandler.bstack111l11lll1_opy_(attrs.get(bstack111l11_opy_ (u"ࠩࡶࡳࡺࡸࡣࡦࠩ࿞"), None)),
                hook_type=hook_type,
                meta={}
            )
            threading.current_thread().current_hook_uuid = bstack1111ll1111_opy_.bstack1111llll1l_opy_()
            threading.current_thread().current_hook_id = bstack111l1ll111_opy_ + bstack111l11_opy_ (u"ࠪ࠱ࠬ࿟") + attrs.get(bstack111l11_opy_ (u"ࠫࡹࡿࡰࡦࠩ࿠"), bstack111l11_opy_ (u"ࠬ࠭࿡")).lower()
            with self._lock:
                self.store[bstack111l11_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡩࡱࡲ࡯ࡤࡻࡵࡪࡦࠪ࿢")] = [bstack1111ll1111_opy_.bstack1111llll1l_opy_()]
                if bstack1l11lllll1_opy_(threading.current_thread(), bstack111l11_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡵࡶ࡫ࡧࠫ࿣"), None):
                    self.store[bstack111l11_opy_ (u"ࠨࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡷࠬ࿤")].append(bstack1111ll1111_opy_.bstack1111llll1l_opy_())
                else:
                    self.store[bstack111l11_opy_ (u"ࠩࡪࡰࡴࡨࡡ࡭ࡡ࡫ࡳࡴࡱࡳࠨ࿥")].append(bstack1111ll1111_opy_.bstack1111llll1l_opy_())
            if bstack111l1ll111_opy_:
                self._1111l1llll_opy_[bstack111l1ll111_opy_ + bstack111l11_opy_ (u"ࠪ࠱ࠬ࿦") + attrs.get(bstack111l11_opy_ (u"ࠫࡹࡿࡰࡦࠩ࿧"), bstack111l11_opy_ (u"ࠬ࠭࿨")).lower()] = { bstack111l11_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩ࿩"): bstack1111ll1111_opy_ }
            bstack111l1ll1_opy_.bstack111ll11l11_opy_(bstack111l11_opy_ (u"ࠧࡉࡱࡲ࡯ࡗࡻ࡮ࡔࡶࡤࡶࡹ࡫ࡤࠨ࿪"), bstack1111ll1111_opy_)
        else:
            bstack111l1ll1ll_opy_ = {
                bstack111l11_opy_ (u"ࠨ࡫ࡧࠫ࿫"): uuid4().__str__(),
                bstack111l11_opy_ (u"ࠩࡷࡩࡽࡺࠧ࿬"): bstack111l11_opy_ (u"ࠪࡿࢂࠦࡻࡾࠩ࿭").format(attrs.get(bstack111l11_opy_ (u"ࠫࡰࡽ࡮ࡢ࡯ࡨࠫ࿮")), attrs.get(bstack111l11_opy_ (u"ࠬࡧࡲࡨࡵࠪ࿯"), bstack111l11_opy_ (u"࠭ࠧ࿰"))) if attrs.get(bstack111l11_opy_ (u"ࠧࡢࡴࡪࡷࠬ࿱"), []) else attrs.get(bstack111l11_opy_ (u"ࠨ࡭ࡺࡲࡦࡳࡥࠨ࿲")),
                bstack111l11_opy_ (u"ࠩࡶࡸࡪࡶ࡟ࡢࡴࡪࡹࡲ࡫࡮ࡵࠩ࿳"): attrs.get(bstack111l11_opy_ (u"ࠪࡥࡷ࡭ࡳࠨ࿴"), []),
                bstack111l11_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨ࿵"): bstack11ll11lll_opy_(),
                bstack111l11_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬ࿶"): bstack111l11_opy_ (u"࠭ࡰࡦࡰࡧ࡭ࡳ࡭ࠧ࿷"),
                bstack111l11_opy_ (u"ࠧࡥࡧࡶࡧࡷ࡯ࡰࡵ࡫ࡲࡲࠬ࿸"): attrs.get(bstack111l11_opy_ (u"ࠨࡦࡲࡧࠬ࿹"), bstack111l11_opy_ (u"ࠩࠪ࿺"))
            }
            if attrs.get(bstack111l11_opy_ (u"ࠪࡰ࡮ࡨ࡮ࡢ࡯ࡨࠫ࿻"), bstack111l11_opy_ (u"ࠫࠬ࿼")) != bstack111l11_opy_ (u"ࠬ࠭࿽"):
                bstack111l1ll1ll_opy_[bstack111l11_opy_ (u"࠭࡫ࡦࡻࡺࡳࡷࡪࠧ࿾")] = attrs.get(bstack111l11_opy_ (u"ࠧ࡭࡫ࡥࡲࡦࡳࡥࠨ࿿"))
            if not self.bstack1111lll11l_opy_:
                self._1111l1llll_opy_[self._1111l1lll1_opy_()][bstack111l11_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫက")].add_step(bstack111l1ll1ll_opy_)
                threading.current_thread().current_step_uuid = bstack111l1ll1ll_opy_[bstack111l11_opy_ (u"ࠩ࡬ࡨࠬခ")]
            self.bstack1111lll11l_opy_.append(bstack111l1ll1ll_opy_)
    @error_handler(class_method=True)
    def end_keyword(self, name, attrs):
        messages = self.messages.bstack111l11ll11_opy_()
        self._111l1l1l1l_opy_(messages)
        current_test_id = bstack1l11lllll1_opy_(threading.current_thread(), bstack111l11_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡹ࡫ࡳࡵࡡ࡬ࡨࠬဂ"), None)
        bstack111l1ll111_opy_ = current_test_id if current_test_id else bstack1l11lllll1_opy_(threading.current_thread(), bstack111l11_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡹࡵࡪࡶࡨࡣ࡮ࡪࠧဃ"), None)
        bstack1111l1ll1l_opy_ = bstack111l111l1l_opy_.get(attrs.get(bstack111l11_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬင")), bstack111l11_opy_ (u"࠭ࡳ࡬࡫ࡳࡴࡪࡪࠧစ"))
        bstack1111llll11_opy_ = attrs.get(bstack111l11_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨဆ"))
        if bstack1111l1ll1l_opy_ != bstack111l11_opy_ (u"ࠨࡵ࡮࡭ࡵࡶࡥࡥࠩဇ") and not attrs.get(bstack111l11_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪဈ")) and self._1111ll1ll1_opy_:
            bstack1111llll11_opy_ = self._1111ll1ll1_opy_
        bstack111lll111l_opy_ = Result(result=bstack1111l1ll1l_opy_, exception=bstack1111llll11_opy_, bstack111ll11lll_opy_=[bstack1111llll11_opy_])
        if attrs.get(bstack111l11_opy_ (u"ࠪࡸࡾࡶࡥࠨဉ"), bstack111l11_opy_ (u"ࠫࠬည")).lower() in [bstack111l11_opy_ (u"ࠬࡹࡥࡵࡷࡳࠫဋ"), bstack111l11_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮ࠨဌ")]:
            bstack111l1ll111_opy_ = current_test_id if current_test_id else bstack1l11lllll1_opy_(threading.current_thread(), bstack111l11_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡵࡸ࡭ࡹ࡫࡟ࡪࡦࠪဍ"), None)
            if bstack111l1ll111_opy_:
                bstack111lll11ll_opy_ = bstack111l1ll111_opy_ + bstack111l11_opy_ (u"ࠣ࠯ࠥဎ") + attrs.get(bstack111l11_opy_ (u"ࠩࡷࡽࡵ࡫ࠧဏ"), bstack111l11_opy_ (u"ࠪࠫတ")).lower()
                self._1111l1llll_opy_[bstack111lll11ll_opy_][bstack111l11_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧထ")].stop(time=bstack11ll11lll_opy_(), duration=int(attrs.get(bstack111l11_opy_ (u"ࠬ࡫࡬ࡢࡲࡶࡩࡩࡺࡩ࡮ࡧࠪဒ"), bstack111l11_opy_ (u"࠭࠰ࠨဓ"))), result=bstack111lll111l_opy_)
                bstack111l1ll1_opy_.bstack111ll11l11_opy_(bstack111l11_opy_ (u"ࠧࡉࡱࡲ࡯ࡗࡻ࡮ࡇ࡫ࡱ࡭ࡸ࡮ࡥࡥࠩန"), self._1111l1llll_opy_[bstack111lll11ll_opy_][bstack111l11_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫပ")])
        else:
            bstack111l1ll111_opy_ = current_test_id if current_test_id else bstack1l11lllll1_opy_(threading.current_thread(), bstack111l11_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢ࡬ࡴࡵ࡫ࡠ࡫ࡧࠫဖ"), None)
            if bstack111l1ll111_opy_ and len(self.bstack1111lll11l_opy_) == 1:
                current_step_uuid = bstack1l11lllll1_opy_(threading.current_thread(), bstack111l11_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡸࡺࡥࡱࡡࡸࡹ࡮ࡪࠧဗ"), None)
                self._1111l1llll_opy_[bstack111l1ll111_opy_][bstack111l11_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧဘ")].bstack111ll11111_opy_(current_step_uuid, duration=int(attrs.get(bstack111l11_opy_ (u"ࠬ࡫࡬ࡢࡲࡶࡩࡩࡺࡩ࡮ࡧࠪမ"), bstack111l11_opy_ (u"࠭࠰ࠨယ"))), result=bstack111lll111l_opy_)
            else:
                self.bstack111l1l1111_opy_(attrs)
            self.bstack1111lll11l_opy_.pop()
    def log_message(self, message):
        try:
            if message.get(bstack111l11_opy_ (u"ࠧࡩࡶࡰࡰࠬရ"), bstack111l11_opy_ (u"ࠨࡰࡲࠫလ")) == bstack111l11_opy_ (u"ࠩࡼࡩࡸ࠭ဝ"):
                return
            self.messages.push(message)
            logs = []
            if bstack1l1lll1ll1_opy_.bstack111ll1l1ll_opy_():
                logs.append({
                    bstack111l11_opy_ (u"ࠪࡸ࡮ࡳࡥࡴࡶࡤࡱࡵ࠭သ"): bstack11ll11lll_opy_(),
                    bstack111l11_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬဟ"): message.get(bstack111l11_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭ဠ")),
                    bstack111l11_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬအ"): message.get(bstack111l11_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭ဢ")),
                    **bstack1l1lll1ll1_opy_.bstack111ll1l1ll_opy_()
                })
                if len(logs) > 0:
                    bstack111l1ll1_opy_.bstack11l1ll111_opy_(logs)
        except Exception as err:
            pass
    def close(self):
        bstack111l1ll1_opy_.bstack111l1111ll_opy_()
    def bstack111l1l1111_opy_(self, bstack111l1ll11l_opy_):
        if not bstack1l1lll1ll1_opy_.bstack111ll1l1ll_opy_():
            return
        kwname = bstack111l11_opy_ (u"ࠨࡽࢀࠤࢀࢃࠧဣ").format(bstack111l1ll11l_opy_.get(bstack111l11_opy_ (u"ࠩ࡮ࡻࡳࡧ࡭ࡦࠩဤ")), bstack111l1ll11l_opy_.get(bstack111l11_opy_ (u"ࠪࡥࡷ࡭ࡳࠨဥ"), bstack111l11_opy_ (u"ࠫࠬဦ"))) if bstack111l1ll11l_opy_.get(bstack111l11_opy_ (u"ࠬࡧࡲࡨࡵࠪဧ"), []) else bstack111l1ll11l_opy_.get(bstack111l11_opy_ (u"࠭࡫ࡸࡰࡤࡱࡪ࠭ဨ"))
        error_message = bstack111l11_opy_ (u"ࠢ࡬ࡹࡱࡥࡲ࡫࠺ࠡ࡞ࠥࡿ࠵ࢃ࡜ࠣࠢࡿࠤࡸࡺࡡࡵࡷࡶ࠾ࠥࡢࠢࡼ࠳ࢀࡠࠧࠦࡼࠡࡧࡻࡧࡪࡶࡴࡪࡱࡱ࠾ࠥࡢࠢࡼ࠴ࢀࡠࠧࠨဩ").format(kwname, bstack111l1ll11l_opy_.get(bstack111l11_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨဪ")), str(bstack111l1ll11l_opy_.get(bstack111l11_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪါ"))))
        bstack1111lll1l1_opy_ = bstack111l11_opy_ (u"ࠥ࡯ࡼࡴࡡ࡮ࡧ࠽ࠤࡡࠨࡻ࠱ࡿ࡟ࠦࠥࢂࠠࡴࡶࡤࡸࡺࡹ࠺ࠡ࡞ࠥࡿ࠶ࢃ࡜ࠣࠤာ").format(kwname, bstack111l1ll11l_opy_.get(bstack111l11_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫိ")))
        bstack1111lll111_opy_ = error_message if bstack111l1ll11l_opy_.get(bstack111l11_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭ီ")) else bstack1111lll1l1_opy_
        bstack111l1l1ll1_opy_ = {
            bstack111l11_opy_ (u"࠭ࡴࡪ࡯ࡨࡷࡹࡧ࡭ࡱࠩု"): self.bstack1111lll11l_opy_[-1].get(bstack111l11_opy_ (u"ࠧࡴࡶࡤࡶࡹ࡫ࡤࡠࡣࡷࠫူ"), bstack11ll11lll_opy_()),
            bstack111l11_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩေ"): bstack1111lll111_opy_,
            bstack111l11_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨဲ"): bstack111l11_opy_ (u"ࠪࡉࡗࡘࡏࡓࠩဳ") if bstack111l1ll11l_opy_.get(bstack111l11_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫဴ")) == bstack111l11_opy_ (u"ࠬࡌࡁࡊࡎࠪဵ") else bstack111l11_opy_ (u"࠭ࡉࡏࡈࡒࠫံ"),
            **bstack1l1lll1ll1_opy_.bstack111ll1l1ll_opy_()
        }
        bstack111l1ll1_opy_.bstack11l1ll111_opy_([bstack111l1l1ll1_opy_])
    def _1111l1lll1_opy_(self):
        for bstack111l111ll1_opy_ in reversed(self._1111l1llll_opy_):
            bstack111l1l111l_opy_ = bstack111l111ll1_opy_
            data = self._1111l1llll_opy_[bstack111l111ll1_opy_][bstack111l11_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣ့ࠪ")]
            if isinstance(data, bstack111ll111l1_opy_):
                if not bstack111l11_opy_ (u"ࠨࡇࡄࡇࡍ࠭း") in data.bstack111l11l1l1_opy_():
                    return bstack111l1l111l_opy_
            else:
                return bstack111l1l111l_opy_
    def _111l1l1l1l_opy_(self, messages):
        try:
            bstack111l11l111_opy_ = BuiltIn().get_variable_value(bstack111l11_opy_ (u"ࠤࠧࡿࡑࡕࡇࠡࡎࡈ࡚ࡊࡒࡽ္ࠣ")) in (bstack1111llllll_opy_.DEBUG, bstack1111llllll_opy_.TRACE)
            for message, bstack1111ll1lll_opy_ in zip_longest(messages, messages[1:]):
                name = message.get(bstack111l11_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨ်ࠫ"))
                level = message.get(bstack111l11_opy_ (u"ࠫࡱ࡫ࡶࡦ࡮ࠪျ"))
                if level == bstack1111llllll_opy_.FAIL:
                    self._1111ll1ll1_opy_ = name or self._1111ll1ll1_opy_
                    self._1111lllll1_opy_ = bstack1111ll1lll_opy_.get(bstack111l11_opy_ (u"ࠧࡳࡥࡴࡵࡤ࡫ࡪࠨြ")) if bstack111l11l111_opy_ and bstack1111ll1lll_opy_ else self._1111lllll1_opy_
        except:
            pass
    @classmethod
    def bstack111ll11l11_opy_(self, event: str, bstack111l11llll_opy_: bstack111l11l1ll_opy_, bstack111l1l11ll_opy_=False):
        if event == bstack111l11_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨွ"):
            bstack111l11llll_opy_.set(hooks=self.store[bstack111l11_opy_ (u"ࠧࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡶࠫှ")])
        if event == bstack111l11_opy_ (u"ࠨࡖࡨࡷࡹࡘࡵ࡯ࡕ࡮࡭ࡵࡶࡥࡥࠩဿ"):
            event = bstack111l11_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫ၀")
        if bstack111l1l11ll_opy_:
            bstack111l1l1l11_opy_ = {
                bstack111l11_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫ࠧ၁"): event,
                bstack111l11llll_opy_.bstack111l11111l_opy_(): bstack111l11llll_opy_.bstack1111ll1l1l_opy_(event)
            }
            with self._lock:
                self.bstack111l1l1lll_opy_.append(bstack111l1l1l11_opy_)
        else:
            bstack111l1ll1_opy_.bstack111ll11l11_opy_(event, bstack111l11llll_opy_)
class bstack1111ll111l_opy_:
    def __init__(self):
        self._1111l1ll11_opy_ = []
    def bstack111l111111_opy_(self):
        self._1111l1ll11_opy_.append([])
    def bstack111l11ll11_opy_(self):
        return self._1111l1ll11_opy_.pop() if self._1111l1ll11_opy_ else list()
    def push(self, message):
        self._1111l1ll11_opy_[-1].append(message) if self._1111l1ll11_opy_ else self._1111l1ll11_opy_.append([message])
class bstack1111llllll_opy_:
    FAIL = bstack111l11_opy_ (u"ࠫࡋࡇࡉࡍࠩ၂")
    ERROR = bstack111l11_opy_ (u"ࠬࡋࡒࡓࡑࡕࠫ၃")
    WARNING = bstack111l11_opy_ (u"࠭ࡗࡂࡔࡑࠫ၄")
    bstack111l1ll1l1_opy_ = bstack111l11_opy_ (u"ࠧࡊࡐࡉࡓࠬ၅")
    DEBUG = bstack111l11_opy_ (u"ࠨࡆࡈࡆ࡚ࡍࠧ၆")
    TRACE = bstack111l11_opy_ (u"ࠩࡗࡖࡆࡉࡅࠨ၇")
    bstack111l1l11l1_opy_ = [FAIL, ERROR]
def bstack1111lll1ll_opy_(bstack111l11l11l_opy_):
    if not bstack111l11l11l_opy_:
        return None
    if bstack111l11l11l_opy_.get(bstack111l11_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦ࠭၈"), None):
        return getattr(bstack111l11l11l_opy_[bstack111l11_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧ၉")], bstack111l11_opy_ (u"ࠬࡻࡵࡪࡦࠪ၊"), None)
    return bstack111l11l11l_opy_.get(bstack111l11_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ။"), None)
def bstack1111ll1l11_opy_(hook_type, current_test_uuid):
    if hook_type.lower() not in [bstack111l11_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠭၌"), bstack111l11_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࠪ၍")]:
        return
    if hook_type.lower() == bstack111l11_opy_ (u"ࠩࡶࡩࡹࡻࡰࠨ၎"):
        if current_test_uuid is None:
            return bstack111l11_opy_ (u"ࠪࡆࡊࡌࡏࡓࡇࡢࡅࡑࡒࠧ၏")
        else:
            return bstack111l11_opy_ (u"ࠫࡇࡋࡆࡐࡔࡈࡣࡊࡇࡃࡉࠩၐ")
    elif hook_type.lower() == bstack111l11_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴࠧၑ"):
        if current_test_uuid is None:
            return bstack111l11_opy_ (u"࠭ࡁࡇࡖࡈࡖࡤࡇࡌࡍࠩၒ")
        else:
            return bstack111l11_opy_ (u"ࠧࡂࡈࡗࡉࡗࡥࡅࡂࡅࡋࠫၓ")