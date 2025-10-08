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
import threading
from collections import deque
from bstack_utils.constants import *
class bstack11lllll11_opy_:
    def __init__(self):
        self._111111l1lll_opy_ = deque()
        self._111111l11ll_opy_ = {}
        self._111111ll111_opy_ = False
        self._lock = threading.RLock()
    def bstack111111ll11l_opy_(self, test_name, bstack111111ll1l1_opy_):
        with self._lock:
            bstack111111l1l1l_opy_ = self._111111l11ll_opy_.get(test_name, {})
            return bstack111111l1l1l_opy_.get(bstack111111ll1l1_opy_, 0)
    def bstack111111l1ll1_opy_(self, test_name, bstack111111ll1l1_opy_):
        with self._lock:
            bstack111111ll1ll_opy_ = self.bstack111111ll11l_opy_(test_name, bstack111111ll1l1_opy_)
            self.bstack111111l1l11_opy_(test_name, bstack111111ll1l1_opy_)
            return bstack111111ll1ll_opy_
    def bstack111111l1l11_opy_(self, test_name, bstack111111ll1l1_opy_):
        with self._lock:
            if test_name not in self._111111l11ll_opy_:
                self._111111l11ll_opy_[test_name] = {}
            bstack111111l1l1l_opy_ = self._111111l11ll_opy_[test_name]
            bstack111111ll1ll_opy_ = bstack111111l1l1l_opy_.get(bstack111111ll1l1_opy_, 0)
            bstack111111l1l1l_opy_[bstack111111ll1l1_opy_] = bstack111111ll1ll_opy_ + 1
    def bstack11ll1111l1_opy_(self, bstack111111l1111_opy_, bstack111111l11l1_opy_):
        bstack111111l111l_opy_ = self.bstack111111l1ll1_opy_(bstack111111l1111_opy_, bstack111111l11l1_opy_)
        event_name = bstack11l1lll1l1l_opy_[bstack111111l11l1_opy_]
        bstack1l1l1l1111l_opy_ = bstack111l11_opy_ (u"ࠥࡿࢂ࠳ࡻࡾ࠯ࡾࢁࠧἶ").format(bstack111111l1111_opy_, event_name, bstack111111l111l_opy_)
        with self._lock:
            self._111111l1lll_opy_.append(bstack1l1l1l1111l_opy_)
    def bstack11lll111_opy_(self):
        with self._lock:
            return len(self._111111l1lll_opy_) == 0
    def bstack1l11llll1l_opy_(self):
        with self._lock:
            if self._111111l1lll_opy_:
                bstack1111111llll_opy_ = self._111111l1lll_opy_.popleft()
                return bstack1111111llll_opy_
            return None
    def capturing(self):
        with self._lock:
            return self._111111ll111_opy_
    def bstack1lll11l11l_opy_(self):
        with self._lock:
            self._111111ll111_opy_ = True
    def bstack1lll1l11l1_opy_(self):
        with self._lock:
            self._111111ll111_opy_ = False