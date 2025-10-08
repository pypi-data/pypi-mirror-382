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
from filelock import FileLock
import json
import os
import time
import uuid
import logging
from typing import Dict, List, Optional
from bstack_utils.bstack11l1l1111_opy_ import get_logger
logger = get_logger(__name__)
bstack1111111ll11_opy_: Dict[str, float] = {}
bstack1111111ll1l_opy_: List = []
bstack1111111l1l1_opy_ = 5
bstack1111llll_opy_ = os.path.join(os.getcwd(), bstack111l11_opy_ (u"ࠫࡱࡵࡧࠨἷ"), bstack111l11_opy_ (u"ࠬࡱࡥࡺ࠯ࡰࡩࡹࡸࡩࡤࡵ࠱࡮ࡸࡵ࡮ࠨἸ"))
logging.getLogger(bstack111l11_opy_ (u"࠭ࡦࡪ࡮ࡨࡰࡴࡩ࡫ࠨἹ")).setLevel(logging.WARNING)
lock = FileLock(bstack1111llll_opy_+bstack111l11_opy_ (u"ࠢ࠯࡮ࡲࡧࡰࠨἺ"))
class bstack1111111l111_opy_:
    duration: float
    name: str
    startTime: float
    worker: int
    status: bool
    failure: str
    details: Optional[str]
    entryType: str
    platform: Optional[int]
    command: Optional[str]
    hookType: Optional[str]
    cli: Optional[bool]
    def __init__(self, duration: float, name: str, start_time: float, bstack1111111l11l_opy_: int, status: bool, failure: str, details: Optional[str] = None, platform: Optional[int] = None, command: Optional[str] = None, test_name: Optional[str] = None, hook_type: Optional[str] = None, cli: Optional[bool] = False) -> None:
        self.duration = duration
        self.name = name
        self.startTime = start_time
        self.worker = bstack1111111l11l_opy_
        self.status = status
        self.failure = failure
        self.details = details
        self.entryType = bstack111l11_opy_ (u"ࠣ࡯ࡨࡥࡸࡻࡲࡦࠤἻ")
        self.platform = platform
        self.command = command
        self.testName = test_name
        self.hookType = hook_type
        self.cli = cli
class bstack1ll1l1ll1l1_opy_:
    global bstack1111111ll11_opy_
    @staticmethod
    def bstack1ll11l1ll1l_opy_(key: str):
        bstack1ll1111l1l1_opy_ = bstack1ll1l1ll1l1_opy_.bstack11ll1l1l1ll_opy_(key)
        bstack1ll1l1ll1l1_opy_.mark(bstack1ll1111l1l1_opy_+bstack111l11_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤἼ"))
        return bstack1ll1111l1l1_opy_
    @staticmethod
    def mark(key: str) -> None:
        try:
            bstack1111111ll11_opy_[key] = time.time_ns() / 1000000
        except Exception as e:
            logger.debug(bstack111l11_opy_ (u"ࠥࡉࡷࡸ࡯ࡳ࠼ࠣࡿࢂࠨἽ").format(e))
    @staticmethod
    def end(label: str, start: str, end: str, status: bool, failure: Optional[str] = None, hook_type: Optional[str] = None, details: Optional[str] = None, command: Optional[str] = None, test_name: Optional[str] = None) -> None:
        try:
            bstack1ll1l1ll1l1_opy_.mark(end)
            bstack1ll1l1ll1l1_opy_.measure(label, start, end, status, failure, hook_type, details, command, test_name)
        except Exception as e:
            logger.debug(bstack111l11_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣ࡭ࡳࠦ࡫ࡦࡻࠣࡱࡪࡺࡲࡪࡥࡶ࠾ࠥࢁࡽࠣἾ").format(e))
    @staticmethod
    def measure(label: str, start: str, end: str, status: bool, failure: Optional[str], hook_type: Optional[str] = None, details: Optional[str] = None, command: Optional[str] = None, test_name: Optional[str] = None) -> None:
        try:
            if start not in bstack1111111ll11_opy_ or end not in bstack1111111ll11_opy_:
                logger.debug(bstack111l11_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡴࡶࡤࡶࡹࠦ࡫ࡦࡻࠣࡻ࡮ࡺࡨࠡࡸࡤࡰࡺ࡫ࠠࡼࡿࠣࡳࡷࠦࡥ࡯ࡦࠣ࡯ࡪࡿࠠࡸ࡫ࡷ࡬ࠥࡼࡡ࡭ࡷࡨࠤࢀࢃࠢἿ").format(start,end))
                return
            duration: float = bstack1111111ll11_opy_[end] - bstack1111111ll11_opy_[start]
            bstack11111111ll1_opy_ = os.environ.get(bstack111l11_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡈࡉࡏࡃࡕ࡝ࡤࡏࡓࡠࡔࡘࡒࡓࡏࡎࡈࠤὀ"), bstack111l11_opy_ (u"ࠢࡧࡣ࡯ࡷࡪࠨὁ")).lower() == bstack111l11_opy_ (u"ࠣࡶࡵࡹࡪࠨὂ")
            bstack1111111lll1_opy_: bstack1111111l111_opy_ = bstack1111111l111_opy_(duration, label, bstack1111111ll11_opy_[start], os.getpid(), status, failure, details, os.environ.get(bstack111l11_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡍࡓࡊࡅ࡙ࠤὃ"), 0), command, test_name, hook_type, bstack11111111ll1_opy_)
            del bstack1111111ll11_opy_[start]
            del bstack1111111ll11_opy_[end]
            bstack1ll1l1ll1l1_opy_.bstack1111111l1ll_opy_(bstack1111111lll1_opy_)
        except Exception as e:
            logger.debug(bstack111l11_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡ࡯ࡨࡥࡸࡻࡲࡪࡰࡪࠤࡰ࡫ࡹࠡ࡯ࡨࡸࡷ࡯ࡣࡴ࠼ࠣࡿࢂࠨὄ").format(e))
    @staticmethod
    def bstack1111111l1ll_opy_(bstack1111111lll1_opy_):
        os.makedirs(os.path.dirname(bstack1111llll_opy_)) if not os.path.exists(os.path.dirname(bstack1111llll_opy_)) else None
        bstack1ll1l1ll1l1_opy_.bstack11111111lll_opy_()
        try:
            with lock:
                with open(bstack1111llll_opy_, bstack111l11_opy_ (u"ࠦࡷ࠱ࠢὅ"), encoding=bstack111l11_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦ὆")) as file:
                    try:
                        data = json.load(file)
                    except json.JSONDecodeError:
                        data = []
                    data.append(bstack1111111lll1_opy_.__dict__)
                    file.seek(0)
                    file.truncate()
                    json.dump(data, file, indent=4)
        except FileNotFoundError as bstack11111111l1l_opy_:
            logger.debug(bstack111l11_opy_ (u"ࠨࡆࡪ࡮ࡨࠤࡳࡵࡴࠡࡨࡲࡹࡳࡪࠠࡼࡿࠥ὇").format(bstack11111111l1l_opy_))
            with lock:
                with open(bstack1111llll_opy_, bstack111l11_opy_ (u"ࠢࡸࠤὈ"), encoding=bstack111l11_opy_ (u"ࠣࡷࡷࡪ࠲࠾ࠢὉ")) as file:
                    data = [bstack1111111lll1_opy_.__dict__]
                    json.dump(data, file, indent=4)
        except Exception as e:
            logger.debug(bstack111l11_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡽࡨࡪ࡮ࡨࠤࡰ࡫ࡹࠡ࡯ࡨࡸࡷ࡯ࡣࡴࠢࡤࡴࡵ࡫࡮ࡥࠢࡾࢁࠧὊ").format(str(e)))
        finally:
            if os.path.exists(bstack1111llll_opy_+bstack111l11_opy_ (u"ࠥ࠲ࡱࡵࡣ࡬ࠤὋ")):
                os.remove(bstack1111llll_opy_+bstack111l11_opy_ (u"ࠦ࠳ࡲ࡯ࡤ࡭ࠥὌ"))
    @staticmethod
    def bstack11111111lll_opy_():
        attempt = 0
        while (attempt < bstack1111111l1l1_opy_):
            attempt += 1
            if os.path.exists(bstack1111llll_opy_+bstack111l11_opy_ (u"ࠧ࠴࡬ࡰࡥ࡮ࠦὍ")):
                time.sleep(0.5)
            else:
                break
    @staticmethod
    def bstack11ll1l1l1ll_opy_(label: str) -> str:
        try:
            return bstack111l11_opy_ (u"ࠨࡻࡾ࠼ࡾࢁࠧ὎").format(label,str(uuid.uuid4().hex)[:6])
        except Exception as e:
            logger.debug(bstack111l11_opy_ (u"ࠢࡆࡴࡵࡳࡷࡀࠠࡼࡿࠥ὏").format(e))