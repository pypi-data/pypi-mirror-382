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
import atexit
import datetime
import inspect
import logging
import signal
import threading
from uuid import uuid4
from bstack_utils.measure import bstack1l1l1l1111_opy_
from bstack_utils.percy_sdk import PercySDK
import pytest
from packaging import version
from browserstack_sdk.__init__ import (bstack11l1l1l11_opy_, bstack1l1ll1l1ll_opy_, update, bstack1ll1lllll_opy_,
                                       bstack11ll1lllll_opy_, bstack11l1l1ll1_opy_, bstack111l11l1l_opy_, bstack1ll111ll1_opy_,
                                       bstack1ll1l111_opy_, bstack1l11l11l11_opy_, bstack1lll1lll1l_opy_,
                                       bstack1l1l1llll_opy_, getAccessibilityResults, getAccessibilityResultsSummary, perform_scan, bstack11l1l1l1l_opy_)
from browserstack_sdk.bstack1l1ll1l11l_opy_ import bstack1ll1111l_opy_
from browserstack_sdk._version import __version__
from bstack_utils import bstack11l1l1111_opy_
from bstack_utils.capture import bstack111ll11ll1_opy_
from bstack_utils.config import Config
from bstack_utils.percy import *
from bstack_utils.constants import bstack11111l1l_opy_, bstack11l1lllll1_opy_, bstack11ll11l1l1_opy_, \
    bstack11lll1l1_opy_
from bstack_utils.helper import bstack1l11lllll1_opy_, bstack11l11l11111_opy_, bstack1111ll11ll_opy_, bstack11llll1111_opy_, bstack1l1l1ll11ll_opy_, bstack11ll11lll_opy_, \
    bstack11l111llll1_opy_, \
    bstack11l111lllll_opy_, bstack1l11111ll1_opy_, bstack11l1l1lll_opy_, bstack111lll1l11l_opy_, bstack11l11l111_opy_, Notset, \
    bstack1l111l111_opy_, bstack111ll11l1l1_opy_, bstack111lll11l11_opy_, Result, bstack111llllll1l_opy_, bstack11l11l11l1l_opy_, error_handler, \
    bstack1ll1l1ll1_opy_, bstack1111lll1l_opy_, bstack11ll1l11_opy_, bstack111llll1lll_opy_
from bstack_utils.bstack111ll111ll1_opy_ import bstack111ll11111l_opy_
from bstack_utils.messages import bstack11111l11l_opy_, bstack11lllllll1_opy_, bstack1l1111111_opy_, bstack1ll1l1l1l1_opy_, bstack1ll11111l1_opy_, \
    bstack11lll1l11l_opy_, bstack111llll11l_opy_, bstack11lll11l1l_opy_, bstack1l11lll11l_opy_, bstack111l1l1ll_opy_, \
    bstack11lll1111l_opy_, bstack1ll1111ll_opy_, bstack1lll11ll1l_opy_
from bstack_utils.proxy import bstack1l11l11l_opy_, bstack111ll11l1_opy_
from bstack_utils.bstack1111111l1_opy_ import bstack1llllllll111_opy_, bstack1lllllll1l11_opy_, bstack1llllllll11l_opy_, bstack1lllllll1l1l_opy_, \
    bstack1llllllll1ll_opy_, bstack1lllllll11ll_opy_, bstack1lllllll11l1_opy_, bstack11111111l_opy_, bstack1lllllllll11_opy_
from bstack_utils.bstack1ll1llll1l_opy_ import bstack11l111ll1_opy_
from bstack_utils.bstack1ll1l1ll11_opy_ import bstack11llllll_opy_, bstack11l1l1l1ll_opy_, bstack1111111l_opy_, \
    bstack1l1l1l1l1l_opy_, bstack111111l1l_opy_
from bstack_utils.bstack111l1llll1_opy_ import bstack111lll11l1_opy_
from bstack_utils.bstack111lll1111_opy_ import bstack1l1lll1ll1_opy_
import bstack_utils.accessibility as bstack1l1l111l1l_opy_
from bstack_utils.bstack111l1lll11_opy_ import bstack111l1ll1_opy_
from bstack_utils.bstack11l1ll111l_opy_ import bstack11l1ll111l_opy_
from bstack_utils.bstack1l11ll11_opy_ import bstack11111l1ll_opy_
from browserstack_sdk.__init__ import bstack1l1ll1l111_opy_
from browserstack_sdk.sdk_cli.bstack1llll11111l_opy_ import bstack1lll111l1ll_opy_
from browserstack_sdk.sdk_cli.bstack1lll11l1_opy_ import bstack1lll11l1_opy_, bstack1l111l1l11_opy_, bstack11l11ll111_opy_
from browserstack_sdk.sdk_cli.test_framework import bstack1l111l1l111_opy_, bstack1lll11ll111_opy_, bstack1lll1lll111_opy_
from browserstack_sdk.sdk_cli.cli import cli
from browserstack_sdk.sdk_cli.bstack1lll11l1_opy_ import bstack1lll11l1_opy_, bstack1l111l1l11_opy_, bstack11l11ll111_opy_
bstack11ll11111_opy_ = None
bstack11l11l1ll_opy_ = None
bstack1ll11l1111_opy_ = None
bstack11llll1l_opy_ = None
bstack11l11111ll_opy_ = None
bstack1l1llll1_opy_ = None
bstack11lll1lll_opy_ = None
bstack1lll11llll_opy_ = None
bstack1l1lll111l_opy_ = None
bstack1111l1l1_opy_ = None
bstack1l1111l1_opy_ = None
bstack111lll1l_opy_ = None
bstack11llll1ll1_opy_ = None
bstack1l1llll11l_opy_ = bstack111l11_opy_ (u"ࠪࠫ∜")
CONFIG = {}
bstack1ll11ll1_opy_ = False
bstack11l11ll1l1_opy_ = bstack111l11_opy_ (u"ࠫࠬ∝")
bstack1l11lll111_opy_ = bstack111l11_opy_ (u"ࠬ࠭∞")
bstack11ll111lll_opy_ = False
bstack1lll1ll1l_opy_ = []
bstack11ll1l1l_opy_ = bstack11111l1l_opy_
bstack1lll1lll111l_opy_ = bstack111l11_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭∟")
bstack111ll1lll_opy_ = {}
bstack1ll1l111l_opy_ = None
bstack11l11l11ll_opy_ = False
logger = bstack11l1l1111_opy_.get_logger(__name__, bstack11ll1l1l_opy_)
store = {
    bstack111l11_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡪࡲࡳࡰࡥࡵࡶ࡫ࡧࠫ∠"): []
}
bstack1llll1111111_opy_ = False
try:
    from playwright.sync_api import (
        BrowserContext,
        Page
    )
except:
    pass
import json
_1111l1llll_opy_ = {}
current_test_uuid = None
cli_context = bstack1l111l1l111_opy_(
    test_framework_name=bstack1l1llll11_opy_[bstack111l11_opy_ (u"ࠨࡒ࡜ࡘࡊ࡙ࡔ࠮ࡄࡇࡈࠬ∡")] if bstack11l11l111_opy_() else bstack1l1llll11_opy_[bstack111l11_opy_ (u"ࠩࡓ࡝࡙ࡋࡓࡕࠩ∢")],
    test_framework_version=pytest.__version__,
    platform_index=-1,
)
def bstack1ll11ll11l_opy_(page, bstack1lllllll11_opy_):
    try:
        page.evaluate(bstack111l11_opy_ (u"ࠥࡣࠥࡃ࠾ࠡࡽࢀࠦ∣"),
                      bstack111l11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡰࡤࡱࡪࠨ࠺ࠨ∤") + json.dumps(
                          bstack1lllllll11_opy_) + bstack111l11_opy_ (u"ࠧࢃࡽࠣ∥"))
    except Exception as e:
        print(bstack111l11_opy_ (u"ࠨࡥࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠢࡶࡩࡸࡹࡩࡰࡰࠣࡲࡦࡳࡥࠡࡽࢀࠦ∦"), e)
def bstack11lll111ll_opy_(page, message, level):
    try:
        page.evaluate(bstack111l11_opy_ (u"ࠢࡠࠢࡀࡂࠥࢁࡽࠣ∧"), bstack111l11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡣࡱࡲࡴࡺࡡࡵࡧࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨࡤࡢࡶࡤࠦ࠿࠭∨") + json.dumps(
            message) + bstack111l11_opy_ (u"ࠩ࠯ࠦࡱ࡫ࡶࡦ࡮ࠥ࠾ࠬ∩") + json.dumps(level) + bstack111l11_opy_ (u"ࠪࢁࢂ࠭∪"))
    except Exception as e:
        print(bstack111l11_opy_ (u"ࠦࡪࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠠࡢࡰࡱࡳࡹࡧࡴࡪࡱࡱࠤࢀࢃࠢ∫"), e)
def pytest_configure(config):
    global bstack11l11ll1l1_opy_
    global CONFIG
    bstack1llll1111_opy_ = Config.bstack1lll111l11_opy_()
    config.args = bstack1l1lll1ll1_opy_.bstack1llll111l11l_opy_(config.args)
    bstack1llll1111_opy_.bstack1ll1ll1l11_opy_(bstack11ll1l11_opy_(config.getoption(bstack111l11_opy_ (u"ࠬࡹ࡫ࡪࡲࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡺࡵࡴࠩ∬"))))
    try:
        bstack11l1l1111_opy_.bstack111l1l1llll_opy_(config.inipath, config.rootpath)
    except:
        pass
    if cli.is_running():
        bstack1lll11l1_opy_.invoke(bstack1l111l1l11_opy_.CONNECT, bstack11l11ll111_opy_())
        cli_context.platform_index = int(os.environ.get(bstack111l11_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡊࡐࡇࡉ࡝࠭∭"), bstack111l11_opy_ (u"ࠧ࠱ࠩ∮")))
        config = json.loads(os.environ.get(bstack111l11_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡄࡑࡑࡊࡎࡍࠢ∯"), bstack111l11_opy_ (u"ࠤࡾࢁࠧ∰")))
        cli.bstack1ll1l1ll11l_opy_(bstack11l1l1lll_opy_(bstack11l11ll1l1_opy_, CONFIG), cli_context.platform_index, bstack1ll1lllll_opy_)
    if cli.bstack1lll111111l_opy_(bstack1lll111l1ll_opy_):
        cli.bstack1llll111ll1_opy_()
        logger.debug(bstack111l11_opy_ (u"ࠥࡇࡑࡏࠠࡪࡵࠣࡥࡨࡺࡩࡷࡧࠣࡪࡴࡸࠠࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡡ࡬ࡲࡩ࡫ࡸ࠾ࠤ∱") + str(cli_context.platform_index) + bstack111l11_opy_ (u"ࠦࠧ∲"))
        cli.test_framework.track_event(cli_context, bstack1lll11ll111_opy_.BEFORE_ALL, bstack1lll1lll111_opy_.PRE, config)
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    when = getattr(call, bstack111l11_opy_ (u"ࠧࡽࡨࡦࡰࠥ∳"), None)
    if cli.is_running() and when == bstack111l11_opy_ (u"ࠨࡣࡢ࡮࡯ࠦ∴"):
        cli.test_framework.track_event(cli_context, bstack1lll11ll111_opy_.LOG_REPORT, bstack1lll1lll111_opy_.PRE, item, call)
    outcome = yield
    if when == bstack111l11_opy_ (u"ࠢࡤࡣ࡯ࡰࠧ∵"):
        report = outcome.get_result()
        passed = report.passed or report.skipped or (report.failed and hasattr(report, bstack111l11_opy_ (u"ࠣࡹࡤࡷࡽ࡬ࡡࡪ࡮ࠥ∶")))
        if not passed:
            config = json.loads(os.environ.get(bstack111l11_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡅࡒࡒࡋࡏࡇࠣ∷"), bstack111l11_opy_ (u"ࠥࡿࢂࠨ∸")))
            if bstack11111l1ll_opy_.bstack1l11ll1l_opy_(config):
                bstack1111l1llll1_opy_ = bstack11111l1ll_opy_.bstack11l1lll11_opy_(config)
                if item.execution_count > bstack1111l1llll1_opy_:
                    print(bstack111l11_opy_ (u"࡙ࠫ࡫ࡳࡵࠢࡩࡥ࡮ࡲࡥࡥࠢࡤࡪࡹ࡫ࡲࠡࡴࡨࡸࡷ࡯ࡥࡴ࠼ࠣࠫ∹"), report.nodeid, os.environ.get(bstack111l11_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪ∺")))
                    bstack11111l1ll_opy_.bstack1111lll1lll_opy_(report.nodeid)
            else:
                print(bstack111l11_opy_ (u"࠭ࡔࡦࡵࡷࠤ࡫ࡧࡩ࡭ࡧࡧ࠾ࠥ࠭∻"), report.nodeid, os.environ.get(bstack111l11_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬ∼")))
                bstack11111l1ll_opy_.bstack1111lll1lll_opy_(report.nodeid)
        else:
            print(bstack111l11_opy_ (u"ࠨࡖࡨࡷࡹࠦࡰࡢࡵࡶࡩࡩࡀࠠࠨ∽"), report.nodeid, os.environ.get(bstack111l11_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧ∾")))
    if cli.is_running():
        if when == bstack111l11_opy_ (u"ࠥࡷࡪࡺࡵࡱࠤ∿"):
            cli.test_framework.track_event(cli_context, bstack1lll11ll111_opy_.BEFORE_EACH, bstack1lll1lll111_opy_.POST, item, call, outcome)
        elif when == bstack111l11_opy_ (u"ࠦࡨࡧ࡬࡭ࠤ≀"):
            cli.test_framework.track_event(cli_context, bstack1lll11ll111_opy_.LOG_REPORT, bstack1lll1lll111_opy_.POST, item, call, outcome)
        elif when == bstack111l11_opy_ (u"ࠧࡺࡥࡢࡴࡧࡳࡼࡴࠢ≁"):
            cli.test_framework.track_event(cli_context, bstack1lll11ll111_opy_.AFTER_EACH, bstack1lll1lll111_opy_.POST, item, call, outcome)
        return # skip all existing operations
    skipSessionName = item.config.getoption(bstack111l11_opy_ (u"࠭ࡳ࡬࡫ࡳࡗࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨ≂"))
    plugins = item.config.getoption(bstack111l11_opy_ (u"ࠢࡱ࡮ࡸ࡫࡮ࡴࡳࠣ≃"))
    report = outcome.get_result()
    os.environ[bstack111l11_opy_ (u"ࠨࡒ࡜ࡘࡊ࡙ࡔࡠࡖࡈࡗ࡙ࡥࡎࡂࡏࡈࠫ≄")] = report.nodeid
    bstack1lll1llllll1_opy_(item, call, report)
    if bstack111l11_opy_ (u"ࠤࡳࡽࡹ࡫ࡳࡵࡡࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡱ࡮ࡸ࡫࡮ࡴࠢ≅") not in plugins or bstack11l11l111_opy_():
        return
    summary = []
    driver = getattr(item, bstack111l11_opy_ (u"ࠥࡣࡩࡸࡩࡷࡧࡵࠦ≆"), None)
    page = getattr(item, bstack111l11_opy_ (u"ࠦࡤࡶࡡࡨࡧࠥ≇"), None)
    try:
        if (driver == None or driver.session_id == None):
            driver = threading.current_thread().bstackSessionDriver
    except:
        pass
    item._driver = driver
    if (driver is not None or cli.is_running()):
        bstack1lll1ll1l1ll_opy_(item, report, summary, skipSessionName)
    if (page is not None):
        bstack1lll1lll1l11_opy_(item, report, summary, skipSessionName)
def bstack1lll1ll1l1ll_opy_(item, report, summary, skipSessionName):
    if report.when == bstack111l11_opy_ (u"ࠬࡹࡥࡵࡷࡳࠫ≈") and report.skipped:
        bstack1lllllllll11_opy_(report)
    if report.when in [bstack111l11_opy_ (u"ࠨࡳࡦࡶࡸࡴࠧ≉"), bstack111l11_opy_ (u"ࠢࡵࡧࡤࡶࡩࡵࡷ࡯ࠤ≊")]:
        return
    if not bstack1l1l1ll11ll_opy_():
        return
    try:
        if ((str(skipSessionName).lower() != bstack111l11_opy_ (u"ࠨࡶࡵࡹࡪ࠭≋")) and (not cli.is_running())) and item._driver.session_id:
            item._driver.execute_script(
                bstack111l11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨ࡮ࡢ࡯ࡨࠦ࠿ࠦࠧ≌") + json.dumps(
                    report.nodeid) + bstack111l11_opy_ (u"ࠪࢁࢂ࠭≍"))
        os.environ[bstack111l11_opy_ (u"ࠫࡕ࡟ࡔࡆࡕࡗࡣ࡙ࡋࡓࡕࡡࡑࡅࡒࡋࠧ≎")] = report.nodeid
    except Exception as e:
        summary.append(
            bstack111l11_opy_ (u"ࠧ࡝ࡁࡓࡐࡌࡒࡌࡀࠠࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡱࡦࡸ࡫ࠡࡵࡨࡷࡸ࡯࡯࡯ࠢࡱࡥࡲ࡫࠺ࠡࡽ࠳ࢁࠧ≏").format(e)
        )
    passed = report.passed or report.skipped or (report.failed and hasattr(report, bstack111l11_opy_ (u"ࠨࡷࡢࡵࡻࡪࡦ࡯࡬ࠣ≐")))
    bstack1l11ll1ll1_opy_ = bstack111l11_opy_ (u"ࠢࠣ≑")
    bstack1lllllllll11_opy_(report)
    if not passed:
        try:
            bstack1l11ll1ll1_opy_ = report.longrepr.reprcrash
        except Exception as e:
            summary.append(
                bstack111l11_opy_ (u"࡙ࠣࡄࡖࡓࡏࡎࡈ࠼ࠣࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡤࡦࡶࡨࡶࡲ࡯࡮ࡦࠢࡩࡥ࡮ࡲࡵࡳࡧࠣࡶࡪࡧࡳࡰࡰ࠽ࠤࢀ࠶ࡽࠣ≒").format(e)
            )
        try:
            if (threading.current_thread().bstackTestErrorMessages == None):
                threading.current_thread().bstackTestErrorMessages = []
        except Exception as e:
            threading.current_thread().bstackTestErrorMessages = []
        threading.current_thread().bstackTestErrorMessages.append(str(bstack1l11ll1ll1_opy_))
    if not report.skipped:
        passed = report.passed or (report.failed and hasattr(report, bstack111l11_opy_ (u"ࠤࡺࡥࡸࡾࡦࡢ࡫࡯ࠦ≓")))
        bstack1l11ll1ll1_opy_ = bstack111l11_opy_ (u"ࠥࠦ≔")
        if not passed:
            try:
                bstack1l11ll1ll1_opy_ = report.longrepr.reprcrash
            except Exception as e:
                summary.append(
                    bstack111l11_opy_ (u"ࠦ࡜ࡇࡒࡏࡋࡑࡋ࠿ࠦࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡧࡩࡹ࡫ࡲ࡮࡫ࡱࡩࠥ࡬ࡡࡪ࡮ࡸࡶࡪࠦࡲࡦࡣࡶࡳࡳࡀࠠࡼ࠲ࢀࠦ≕").format(e)
                )
            try:
                if (threading.current_thread().bstackTestErrorMessages == None):
                    threading.current_thread().bstackTestErrorMessages = []
            except Exception as e:
                threading.current_thread().bstackTestErrorMessages = []
            threading.current_thread().bstackTestErrorMessages.append(str(bstack1l11ll1ll1_opy_))
        try:
            if passed:
                item._driver.execute_script(
                    bstack111l11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼ࡞ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡢࡰࡱࡳࡹࡧࡴࡦࠤ࠯ࠤࡡࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁ࡜ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠨ࡬ࡦࡸࡨࡰࠧࡀࠠࠣ࡫ࡱࡪࡴࠨࠬࠡ࡞ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠣࡦࡤࡸࡦࠨ࠺ࠡࠩ≖")
                    + json.dumps(bstack111l11_opy_ (u"ࠨࡰࡢࡵࡶࡩࡩࠧࠢ≗"))
                    + bstack111l11_opy_ (u"ࠢ࡝ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࢀࡠࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡿࠥ≘")
                )
            else:
                item._driver.execute_script(
                    bstack111l11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࡡࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡥࡳࡴ࡯ࡵࡣࡷࡩࠧ࠲ࠠ࡝ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࡽ࡟ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠤ࡯ࡩࡻ࡫࡬ࠣ࠼ࠣࠦࡪࡸࡲࡰࡴࠥ࠰ࠥࡢࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠧࡪࡡࡵࡣࠥ࠾ࠥ࠭≙")
                    + json.dumps(str(bstack1l11ll1ll1_opy_))
                    + bstack111l11_opy_ (u"ࠤ࡟ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࢂࡢࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࢁࠧ≚")
                )
        except Exception as e:
            summary.append(bstack111l11_opy_ (u"࡛ࠥࡆࡘࡎࡊࡐࡊ࠾ࠥࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡣࡱࡲࡴࡺࡡࡵࡧ࠽ࠤࢀ࠶ࡽࠣ≛").format(e))
def bstack1lll1ll1l111_opy_(test_name, error_message):
    try:
        bstack1lll1lllllll_opy_ = []
        bstack1l1ll1lll_opy_ = os.environ.get(bstack111l11_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠫ≜"), bstack111l11_opy_ (u"ࠬ࠶ࠧ≝"))
        bstack1l1111l1ll_opy_ = {bstack111l11_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ≞"): test_name, bstack111l11_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭≟"): error_message, bstack111l11_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧ≠"): bstack1l1ll1lll_opy_}
        bstack1lll1llll11l_opy_ = os.path.join(tempfile.gettempdir(), bstack111l11_opy_ (u"ࠩࡳࡻࡤࡶࡹࡵࡧࡶࡸࡤ࡫ࡲࡳࡱࡵࡣࡱ࡯ࡳࡵ࠰࡭ࡷࡴࡴࠧ≡"))
        if os.path.exists(bstack1lll1llll11l_opy_):
            with open(bstack1lll1llll11l_opy_) as f:
                bstack1lll1lllllll_opy_ = json.load(f)
        bstack1lll1lllllll_opy_.append(bstack1l1111l1ll_opy_)
        with open(bstack1lll1llll11l_opy_, bstack111l11_opy_ (u"ࠪࡻࠬ≢")) as f:
            json.dump(bstack1lll1lllllll_opy_, f)
    except Exception as e:
        logger.debug(bstack111l11_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡰࡦࡴࡶ࡭ࡸࡺࡩ࡯ࡩࠣࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠠࡱࡻࡷࡩࡸࡺࠠࡦࡴࡵࡳࡷࡹ࠺ࠡࠩ≣") + str(e))
def bstack1lll1lll1l11_opy_(item, report, summary, skipSessionName):
    if report.when in [bstack111l11_opy_ (u"ࠧࡹࡥࡵࡷࡳࠦ≤"), bstack111l11_opy_ (u"ࠨࡴࡦࡣࡵࡨࡴࡽ࡮ࠣ≥")]:
        return
    if (str(skipSessionName).lower() != bstack111l11_opy_ (u"ࠧࡵࡴࡸࡩࠬ≦")):
        bstack1ll11ll11l_opy_(item._page, report.nodeid)
    passed = report.passed or report.skipped or (report.failed and hasattr(report, bstack111l11_opy_ (u"ࠣࡹࡤࡷࡽ࡬ࡡࡪ࡮ࠥ≧")))
    bstack1l11ll1ll1_opy_ = bstack111l11_opy_ (u"ࠤࠥ≨")
    bstack1lllllllll11_opy_(report)
    if not report.skipped:
        if not passed:
            try:
                bstack1l11ll1ll1_opy_ = report.longrepr.reprcrash
            except Exception as e:
                summary.append(
                    bstack111l11_opy_ (u"࡛ࠥࡆࡘࡎࡊࡐࡊ࠾ࠥࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡦࡨࡸࡪࡸ࡭ࡪࡰࡨࠤ࡫ࡧࡩ࡭ࡷࡵࡩࠥࡸࡥࡢࡵࡲࡲ࠿ࠦࡻ࠱ࡿࠥ≩").format(e)
                )
        try:
            if passed:
                bstack111111l1l_opy_(getattr(item, bstack111l11_opy_ (u"ࠫࡤࡶࡡࡨࡧࠪ≪"), None), bstack111l11_opy_ (u"ࠧࡶࡡࡴࡵࡨࡨࠧ≫"))
            else:
                error_message = bstack111l11_opy_ (u"࠭ࠧ≬")
                if bstack1l11ll1ll1_opy_:
                    bstack11lll111ll_opy_(item._page, str(bstack1l11ll1ll1_opy_), bstack111l11_opy_ (u"ࠢࡦࡴࡵࡳࡷࠨ≭"))
                    bstack111111l1l_opy_(getattr(item, bstack111l11_opy_ (u"ࠨࡡࡳࡥ࡬࡫ࠧ≮"), None), bstack111l11_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࠤ≯"), str(bstack1l11ll1ll1_opy_))
                    error_message = str(bstack1l11ll1ll1_opy_)
                else:
                    bstack111111l1l_opy_(getattr(item, bstack111l11_opy_ (u"ࠪࡣࡵࡧࡧࡦࠩ≰"), None), bstack111l11_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࠦ≱"))
                bstack1lll1ll1l111_opy_(report.nodeid, error_message)
        except Exception as e:
            summary.append(bstack111l11_opy_ (u"ࠧ࡝ࡁࡓࡐࡌࡒࡌࡀࠠࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡹࡵࡪࡡࡵࡧࠣࡷࡪࡹࡳࡪࡱࡱࠤࡸࡺࡡࡵࡷࡶ࠾ࠥࢁ࠰ࡾࠤ≲").format(e))
def pytest_addoption(parser):
    parser.addoption(bstack111l11_opy_ (u"ࠨ࠭࠮ࡵ࡮࡭ࡵ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠥ≳"), default=bstack111l11_opy_ (u"ࠢࡇࡣ࡯ࡷࡪࠨ≴"), help=bstack111l11_opy_ (u"ࠣࡃࡸࡸࡴࡳࡡࡵ࡫ࡦࠤࡸ࡫ࡴࠡࡵࡨࡷࡸ࡯࡯࡯ࠢࡱࡥࡲ࡫ࠢ≵"))
    parser.addoption(bstack111l11_opy_ (u"ࠤ࠰࠱ࡸࡱࡩࡱࡕࡨࡷࡸ࡯࡯࡯ࡕࡷࡥࡹࡻࡳࠣ≶"), default=bstack111l11_opy_ (u"ࠥࡊࡦࡲࡳࡦࠤ≷"), help=bstack111l11_opy_ (u"ࠦࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡩࠠࡴࡧࡷࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡴࡡ࡮ࡧࠥ≸"))
    try:
        import pytest_selenium.pytest_selenium
    except:
        parser.addoption(bstack111l11_opy_ (u"ࠧ࠳࠭ࡥࡴ࡬ࡺࡪࡸࠢ≹"), action=bstack111l11_opy_ (u"ࠨࡳࡵࡱࡵࡩࠧ≺"), default=bstack111l11_opy_ (u"ࠢࡤࡪࡵࡳࡲ࡫ࠢ≻"),
                         help=bstack111l11_opy_ (u"ࠣࡆࡵ࡭ࡻ࡫ࡲࠡࡶࡲࠤࡷࡻ࡮ࠡࡶࡨࡷࡹࡹࠢ≼"))
def bstack111l1lllll_opy_(log):
    if not (log[bstack111l11_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪ≽")] and log[bstack111l11_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫ≾")].strip()):
        return
    active = bstack111ll1l1ll_opy_()
    log = {
        bstack111l11_opy_ (u"ࠫࡱ࡫ࡶࡦ࡮ࠪ≿"): log[bstack111l11_opy_ (u"ࠬࡲࡥࡷࡧ࡯ࠫ⊀")],
        bstack111l11_opy_ (u"࠭ࡴࡪ࡯ࡨࡷࡹࡧ࡭ࡱࠩ⊁"): bstack1111ll11ll_opy_().isoformat() + bstack111l11_opy_ (u"࡛ࠧࠩ⊂"),
        bstack111l11_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩ⊃"): log[bstack111l11_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪ⊄")],
    }
    if active:
        if active[bstack111l11_opy_ (u"ࠪࡸࡾࡶࡥࠨ⊅")] == bstack111l11_opy_ (u"ࠫ࡭ࡵ࡯࡬ࠩ⊆"):
            log[bstack111l11_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ⊇")] = active[bstack111l11_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭⊈")]
        elif active[bstack111l11_opy_ (u"ࠧࡵࡻࡳࡩࠬ⊉")] == bstack111l11_opy_ (u"ࠨࡶࡨࡷࡹ࠭⊊"):
            log[bstack111l11_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ⊋")] = active[bstack111l11_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ⊌")]
    bstack111l1ll1_opy_.bstack11l1ll111_opy_([log])
def bstack111ll1l1ll_opy_():
    if len(store[bstack111l11_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤ࡮࡯ࡰ࡭ࡢࡹࡺ࡯ࡤࠨ⊍")]) > 0 and store[bstack111l11_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡨࡰࡱ࡮ࡣࡺࡻࡩࡥࠩ⊎")][-1]:
        return {
            bstack111l11_opy_ (u"࠭ࡴࡺࡲࡨࠫ⊏"): bstack111l11_opy_ (u"ࠧࡩࡱࡲ࡯ࠬ⊐"),
            bstack111l11_opy_ (u"ࠨࡪࡲࡳࡰࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ⊑"): store[bstack111l11_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢ࡬ࡴࡵ࡫ࡠࡷࡸ࡭ࡩ࠭⊒")][-1]
        }
    if store.get(bstack111l11_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡹ࡫ࡳࡵࡡࡸࡹ࡮ࡪࠧ⊓"), None):
        return {
            bstack111l11_opy_ (u"ࠫࡹࡿࡰࡦࠩ⊔"): bstack111l11_opy_ (u"ࠬࡺࡥࡴࡶࠪ⊕"),
            bstack111l11_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭⊖"): store[bstack111l11_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡵࡶ࡫ࡧࠫ⊗")]
        }
    return None
def pytest_runtest_logstart(nodeid, location):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1lll11ll111_opy_.INIT_TEST, bstack1lll1lll111_opy_.PRE, nodeid, location)
def pytest_runtest_logfinish(nodeid, location):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1lll11ll111_opy_.INIT_TEST, bstack1lll1lll111_opy_.POST, nodeid, location)
def pytest_runtest_call(item):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1lll11ll111_opy_.TEST, bstack1lll1lll111_opy_.PRE, item)
        return
    try:
        global CONFIG
        item._1lll1llll111_opy_ = True
        bstack111lll1ll1_opy_ = bstack1l1l111l1l_opy_.bstack11l1l1ll11_opy_(bstack11l111lllll_opy_(item.own_markers))
        if not cli.bstack1lll111111l_opy_(bstack1lll111l1ll_opy_):
            item._a11y_test_case = bstack111lll1ll1_opy_
            if bstack1l11lllll1_opy_(threading.current_thread(), bstack111l11_opy_ (u"ࠨࡣ࠴࠵ࡾࡖ࡬ࡢࡶࡩࡳࡷࡳࠧ⊘"), None):
                driver = getattr(item, bstack111l11_opy_ (u"ࠩࡢࡨࡷ࡯ࡶࡦࡴࠪ⊙"), None)
                item._a11y_started = bstack1l1l111l1l_opy_.bstack1lllll1ll_opy_(driver, bstack111lll1ll1_opy_)
        if not bstack111l1ll1_opy_.on() or bstack1lll1lll111l_opy_ != bstack111l11_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪ⊚"):
            return
        global current_test_uuid #, bstack111ll1lll1_opy_
        bstack111l11l11l_opy_ = {
            bstack111l11_opy_ (u"ࠫࡺࡻࡩࡥࠩ⊛"): uuid4().__str__(),
            bstack111l11_opy_ (u"ࠬࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠩ⊜"): bstack1111ll11ll_opy_().isoformat() + bstack111l11_opy_ (u"࡚࠭ࠨ⊝")
        }
        current_test_uuid = bstack111l11l11l_opy_[bstack111l11_opy_ (u"ࠧࡶࡷ࡬ࡨࠬ⊞")]
        store[bstack111l11_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡶࡷ࡬ࡨࠬ⊟")] = bstack111l11l11l_opy_[bstack111l11_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ⊠")]
        threading.current_thread().current_test_uuid = current_test_uuid
        _1111l1llll_opy_[item.nodeid] = {**_1111l1llll_opy_[item.nodeid], **bstack111l11l11l_opy_}
        bstack1lll1ll1llll_opy_(item, _1111l1llll_opy_[item.nodeid], bstack111l11_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡗࡹࡧࡲࡵࡧࡧࠫ⊡"))
    except Exception as err:
        print(bstack111l11_opy_ (u"ࠫࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡴࡾࡺࡥࡴࡶࡢࡶࡺࡴࡴࡦࡵࡷࡣࡨࡧ࡬࡭࠼ࠣࡿࢂ࠭⊢"), str(err))
def pytest_runtest_setup(item):
    store[bstack111l11_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣ࡮ࡺࡥ࡮ࠩ⊣")] = item
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1lll11ll111_opy_.BEFORE_EACH, bstack1lll1lll111_opy_.PRE, item, bstack111l11_opy_ (u"࠭ࡳࡦࡶࡸࡴࠬ⊤"))
    if bstack11111l1ll_opy_.bstack1111lllll11_opy_():
            bstack1lll1ll1l11l_opy_ = bstack111l11_opy_ (u"ࠢࡔ࡭࡬ࡴࡵ࡯࡮ࡨࠢࡷࡩࡸࡺࠠࡢࡵࠣࡸ࡭࡫ࠠࡢࡤࡲࡶࡹࠦࡢࡶ࡫࡯ࡨࠥ࡬ࡩ࡭ࡧࠣࡩࡽ࡯ࡳࡵࡵ࠱ࠦ⊥")
            logger.error(bstack1lll1ll1l11l_opy_)
            bstack111l11l11l_opy_ = {
                bstack111l11_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭⊦"): uuid4().__str__(),
                bstack111l11_opy_ (u"ࠩࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹ࠭⊧"): bstack1111ll11ll_opy_().isoformat() + bstack111l11_opy_ (u"ࠪ࡞ࠬ⊨"),
                bstack111l11_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩ⊩"): bstack1111ll11ll_opy_().isoformat() + bstack111l11_opy_ (u"ࠬࡠࠧ⊪"),
                bstack111l11_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭⊫"): bstack111l11_opy_ (u"ࠧࡴ࡭࡬ࡴࡵ࡫ࡤࠨ⊬"),
                bstack111l11_opy_ (u"ࠨࡴࡨࡥࡸࡵ࡮ࠨ⊭"): bstack1lll1ll1l11l_opy_,
                bstack111l11_opy_ (u"ࠩ࡫ࡳࡴࡱࡳࠨ⊮"): [],
                bstack111l11_opy_ (u"ࠪࡪ࡮ࡾࡴࡶࡴࡨࡷࠬ⊯"): []
            }
            bstack1lll1ll1llll_opy_(item, bstack111l11l11l_opy_, bstack111l11_opy_ (u"࡙ࠫ࡫ࡳࡵࡔࡸࡲࡘࡱࡩࡱࡲࡨࡨࠬ⊰"))
            pytest.skip(bstack1lll1ll1l11l_opy_)
            return # skip all existing operations
    global bstack1llll1111111_opy_
    threading.current_thread().percySessionName = item.nodeid
    if bstack111lll1l11l_opy_():
        atexit.register(bstack11llll1ll_opy_)
        if not bstack1llll1111111_opy_:
            try:
                bstack1lll1ll1ll11_opy_ = [signal.SIGINT, signal.SIGTERM]
                if not bstack111llll1lll_opy_():
                    bstack1lll1ll1ll11_opy_.extend([signal.SIGHUP, signal.SIGQUIT])
                for s in bstack1lll1ll1ll11_opy_:
                    signal.signal(s, bstack1lll1ll11lll_opy_)
                bstack1llll1111111_opy_ = True
            except Exception as e:
                logger.debug(
                    bstack111l11_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡳࡧࡪ࡭ࡸࡺࡥࡳࠢࡶ࡭࡬ࡴࡡ࡭ࠢ࡫ࡥࡳࡪ࡬ࡦࡴࡶ࠾ࠥࠨ⊱") + str(e))
        try:
            item.config.hook.pytest_selenium_runtest_makereport = bstack1llllllll111_opy_
        except Exception as err:
            threading.current_thread().testStatus = bstack111l11_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭⊲")
    try:
        if not bstack111l1ll1_opy_.on():
            return
        uuid = uuid4().__str__()
        bstack111l11l11l_opy_ = {
            bstack111l11_opy_ (u"ࠧࡶࡷ࡬ࡨࠬ⊳"): uuid,
            bstack111l11_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬ⊴"): bstack1111ll11ll_opy_().isoformat() + bstack111l11_opy_ (u"ࠩ࡝ࠫ⊵"),
            bstack111l11_opy_ (u"ࠪࡸࡾࡶࡥࠨ⊶"): bstack111l11_opy_ (u"ࠫ࡭ࡵ࡯࡬ࠩ⊷"),
            bstack111l11_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡸࡾࡶࡥࠨ⊸"): bstack111l11_opy_ (u"࠭ࡂࡆࡈࡒࡖࡊࡥࡅࡂࡅࡋࠫ⊹"),
            bstack111l11_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡴࡡ࡮ࡧࠪ⊺"): bstack111l11_opy_ (u"ࠨࡵࡨࡸࡺࡶࠧ⊻")
        }
        threading.current_thread().current_hook_uuid = uuid
        threading.current_thread().current_test_item = item
        store[bstack111l11_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠ࡫ࡷࡩࡲ࠭⊼")] = item
        store[bstack111l11_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣ࡭ࡵ࡯࡬ࡡࡸࡹ࡮ࡪࠧ⊽")] = [uuid]
        if not _1111l1llll_opy_.get(item.nodeid, None):
            _1111l1llll_opy_[item.nodeid] = {bstack111l11_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡵࠪ⊾"): [], bstack111l11_opy_ (u"ࠬ࡬ࡩࡹࡶࡸࡶࡪࡹࠧ⊿"): []}
        _1111l1llll_opy_[item.nodeid][bstack111l11_opy_ (u"࠭ࡨࡰࡱ࡮ࡷࠬ⋀")].append(bstack111l11l11l_opy_[bstack111l11_opy_ (u"ࠧࡶࡷ࡬ࡨࠬ⋁")])
        _1111l1llll_opy_[item.nodeid + bstack111l11_opy_ (u"ࠨ࠯ࡶࡩࡹࡻࡰࠨ⋂")] = bstack111l11l11l_opy_
        bstack1lll1llll1l1_opy_(item, bstack111l11l11l_opy_, bstack111l11_opy_ (u"ࠩࡋࡳࡴࡱࡒࡶࡰࡖࡸࡦࡸࡴࡦࡦࠪ⋃"))
    except Exception as err:
        print(bstack111l11_opy_ (u"ࠪࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡽࡹ࡫ࡳࡵࡡࡵࡹࡳࡺࡥࡴࡶࡢࡷࡪࡺࡵࡱ࠼ࠣࡿࢂ࠭⋄"), str(err))
def pytest_runtest_teardown(item):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1lll11ll111_opy_.TEST, bstack1lll1lll111_opy_.POST, item)
        cli.test_framework.track_event(cli_context, bstack1lll11ll111_opy_.AFTER_EACH, bstack1lll1lll111_opy_.PRE, item, bstack111l11_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳ࠭⋅"))
        return # skip all existing operations
    try:
        global bstack111ll1lll_opy_
        bstack1l1ll1lll_opy_ = 0
        if bstack11ll111lll_opy_ is True:
            bstack1l1ll1lll_opy_ = int(os.environ.get(bstack111l11_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡉࡏࡆࡈ࡜ࠬ⋆")))
        if bstack1ll11l1lll_opy_.bstack11l11ll1ll_opy_() == bstack111l11_opy_ (u"ࠨࡴࡳࡷࡨࠦ⋇"):
            if bstack1ll11l1lll_opy_.bstack1lll1111l_opy_() == bstack111l11_opy_ (u"ࠢࡵࡧࡶࡸࡨࡧࡳࡦࠤ⋈"):
                bstack1lll1lllll11_opy_ = bstack1l11lllll1_opy_(threading.current_thread(), bstack111l11_opy_ (u"ࠨࡲࡨࡶࡨࡿࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫ⋉"), None)
                bstack1lllll1l1_opy_ = bstack1lll1lllll11_opy_ + bstack111l11_opy_ (u"ࠤ࠰ࡸࡪࡹࡴࡤࡣࡶࡩࠧ⋊")
                driver = getattr(item, bstack111l11_opy_ (u"ࠪࡣࡩࡸࡩࡷࡧࡵࠫ⋋"), None)
                bstack11l1l11l1_opy_ = getattr(item, bstack111l11_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ⋌"), None)
                bstack1lll11l1l_opy_ = getattr(item, bstack111l11_opy_ (u"ࠬࡻࡵࡪࡦࠪ⋍"), None)
                PercySDK.screenshot(driver, bstack1lllll1l1_opy_, bstack11l1l11l1_opy_=bstack11l1l11l1_opy_, bstack1lll11l1l_opy_=bstack1lll11l1l_opy_, bstack1ll1l1lll_opy_=bstack1l1ll1lll_opy_)
        if not cli.bstack1lll111111l_opy_(bstack1lll111l1ll_opy_):
            if getattr(item, bstack111l11_opy_ (u"࠭࡟ࡢ࠳࠴ࡽࡤࡹࡴࡢࡴࡷࡩࡩ࠭⋎"), False):
                bstack1ll1111l_opy_.bstack1l111l1l1l_opy_(getattr(item, bstack111l11_opy_ (u"ࠧࡠࡦࡵ࡭ࡻ࡫ࡲࠨ⋏"), None), bstack111ll1lll_opy_, logger, item)
        if not bstack111l1ll1_opy_.on():
            return
        bstack111l11l11l_opy_ = {
            bstack111l11_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭⋐"): uuid4().__str__(),
            bstack111l11_opy_ (u"ࠩࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹ࠭⋑"): bstack1111ll11ll_opy_().isoformat() + bstack111l11_opy_ (u"ࠪ࡞ࠬ⋒"),
            bstack111l11_opy_ (u"ࠫࡹࡿࡰࡦࠩ⋓"): bstack111l11_opy_ (u"ࠬ࡮࡯ࡰ࡭ࠪ⋔"),
            bstack111l11_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡹࡿࡰࡦࠩ⋕"): bstack111l11_opy_ (u"ࠧࡂࡈࡗࡉࡗࡥࡅࡂࡅࡋࠫ⋖"),
            bstack111l11_opy_ (u"ࠨࡪࡲࡳࡰࡥ࡮ࡢ࡯ࡨࠫ⋗"): bstack111l11_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱࠫ⋘")
        }
        _1111l1llll_opy_[item.nodeid + bstack111l11_opy_ (u"ࠪ࠱ࡹ࡫ࡡࡳࡦࡲࡻࡳ࠭⋙")] = bstack111l11l11l_opy_
        bstack1lll1llll1l1_opy_(item, bstack111l11l11l_opy_, bstack111l11_opy_ (u"ࠫࡍࡵ࡯࡬ࡔࡸࡲࡘࡺࡡࡳࡶࡨࡨࠬ⋚"))
    except Exception as err:
        print(bstack111l11_opy_ (u"ࠬࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡵࡿࡴࡦࡵࡷࡣࡷࡻ࡮ࡵࡧࡶࡸࡤࡺࡥࡢࡴࡧࡳࡼࡴ࠺ࠡࡽࢀࠫ⋛"), str(err))
@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):
    if bstack1lllllll1l1l_opy_(fixturedef.argname):
        store[bstack111l11_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟࡮ࡱࡧࡹࡱ࡫࡟ࡪࡶࡨࡱࠬ⋜")] = request.node
    elif bstack1llllllll1ll_opy_(fixturedef.argname):
        store[bstack111l11_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡥ࡯ࡥࡸࡹ࡟ࡪࡶࡨࡱࠬ⋝")] = request.node
    if not bstack111l1ll1_opy_.on():
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1lll11ll111_opy_.SETUP_FIXTURE, bstack1lll1lll111_opy_.PRE, fixturedef, request)
        outcome = yield
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1lll11ll111_opy_.SETUP_FIXTURE, bstack1lll1lll111_opy_.POST, fixturedef, request, outcome)
        return # skip all existing operations
    start_time = datetime.datetime.now()
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1lll11ll111_opy_.SETUP_FIXTURE, bstack1lll1lll111_opy_.PRE, fixturedef, request)
    outcome = yield
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1lll11ll111_opy_.SETUP_FIXTURE, bstack1lll1lll111_opy_.POST, fixturedef, request, outcome)
        return # skip all existing operations
    try:
        fixture = {
            bstack111l11_opy_ (u"ࠨࡰࡤࡱࡪ࠭⋞"): fixturedef.argname,
            bstack111l11_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩ⋟"): bstack11l111llll1_opy_(outcome),
            bstack111l11_opy_ (u"ࠪࡨࡺࡸࡡࡵ࡫ࡲࡲࠬ⋠"): (datetime.datetime.now() - start_time).total_seconds() * 1000
        }
        current_test_item = store[bstack111l11_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢ࡭ࡹ࡫࡭ࠨ⋡")]
        if not _1111l1llll_opy_.get(current_test_item.nodeid, None):
            _1111l1llll_opy_[current_test_item.nodeid] = {bstack111l11_opy_ (u"ࠬ࡬ࡩࡹࡶࡸࡶࡪࡹࠧ⋢"): []}
        _1111l1llll_opy_[current_test_item.nodeid][bstack111l11_opy_ (u"࠭ࡦࡪࡺࡷࡹࡷ࡫ࡳࠨ⋣")].append(fixture)
    except Exception as err:
        logger.debug(bstack111l11_opy_ (u"ࠧࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡰࡺࡶࡨࡷࡹࡥࡦࡪࡺࡷࡹࡷ࡫࡟ࡴࡧࡷࡹࡵࡀࠠࡼࡿࠪ⋤"), str(err))
if bstack11l11l111_opy_() and bstack111l1ll1_opy_.on():
    def pytest_bdd_before_step(request, step):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1lll11ll111_opy_.STEP, bstack1lll1lll111_opy_.PRE, request, step)
            return
        try:
            _1111l1llll_opy_[request.node.nodeid][bstack111l11_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫ⋥")].bstack11ll11lll1_opy_(id(step))
        except Exception as err:
            print(bstack111l11_opy_ (u"ࠩࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡲࡼࡸࡪࡹࡴࡠࡤࡧࡨࡤࡨࡥࡧࡱࡵࡩࡤࡹࡴࡦࡲ࠽ࠤࢀࢃࠧ⋦"), str(err))
    def pytest_bdd_step_error(request, step, exception):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1lll11ll111_opy_.STEP, bstack1lll1lll111_opy_.POST, request, step, exception)
            return
        try:
            _1111l1llll_opy_[request.node.nodeid][bstack111l11_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦ࠭⋧")].bstack111ll11111_opy_(id(step), Result.failed(exception=exception))
        except Exception as err:
            print(bstack111l11_opy_ (u"ࠫࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡴࡾࡺࡥࡴࡶࡢࡦࡩࡪ࡟ࡴࡶࡨࡴࡤ࡫ࡲࡳࡱࡵ࠾ࠥࢁࡽࠨ⋨"), str(err))
    def pytest_bdd_after_step(request, step):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1lll11ll111_opy_.STEP, bstack1lll1lll111_opy_.POST, request, step)
            return
        try:
            bstack111l1llll1_opy_: bstack111lll11l1_opy_ = _1111l1llll_opy_[request.node.nodeid][bstack111l11_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨ⋩")]
            bstack111l1llll1_opy_.bstack111ll11111_opy_(id(step), Result.passed())
        except Exception as err:
            print(bstack111l11_opy_ (u"࠭ࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶࡹࡵࡧࡶࡸࡤࡨࡤࡥࡡࡶࡸࡪࡶ࡟ࡦࡴࡵࡳࡷࡀࠠࡼࡿࠪ⋪"), str(err))
    def pytest_bdd_before_scenario(request, feature, scenario):
        global bstack1lll1lll111l_opy_
        try:
            if not bstack111l1ll1_opy_.on() or bstack1lll1lll111l_opy_ != bstack111l11_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠫ⋫"):
                return
            if cli.is_running():
                cli.test_framework.track_event(cli_context, bstack1lll11ll111_opy_.TEST, bstack1lll1lll111_opy_.PRE, request, feature, scenario)
                return
            driver = bstack1l11lllll1_opy_(threading.current_thread(), bstack111l11_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡔࡧࡶࡷ࡮ࡵ࡮ࡅࡴ࡬ࡺࡪࡸࠧ⋬"), None)
            if not _1111l1llll_opy_.get(request.node.nodeid, None):
                _1111l1llll_opy_[request.node.nodeid] = {}
            bstack111l1llll1_opy_ = bstack111lll11l1_opy_.bstack1lllll111l11_opy_(
                scenario, feature, request.node,
                name=bstack1lllllll11ll_opy_(request.node, scenario),
                started_at=bstack11ll11lll_opy_(),
                file_path=feature.filename,
                scope=[feature.name],
                framework=bstack111l11_opy_ (u"ࠩࡓࡽࡹ࡫ࡳࡵ࠯ࡦࡹࡨࡻ࡭ࡣࡧࡵࠫ⋭"),
                tags=bstack1lllllll11l1_opy_(feature, scenario),
                bstack111l1lll1l_opy_=bstack111l1ll1_opy_.bstack111ll11l1l_opy_(driver) if driver and driver.session_id else {}
            )
            _1111l1llll_opy_[request.node.nodeid][bstack111l11_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦ࠭⋮")] = bstack111l1llll1_opy_
            bstack1lll1ll1ll1l_opy_(bstack111l1llll1_opy_.uuid)
            bstack111l1ll1_opy_.bstack111ll11l11_opy_(bstack111l11_opy_ (u"࡙ࠫ࡫ࡳࡵࡔࡸࡲࡘࡺࡡࡳࡶࡨࡨࠬ⋯"), bstack111l1llll1_opy_)
        except Exception as err:
            print(bstack111l11_opy_ (u"ࠬࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡵࡿࡴࡦࡵࡷࡣࡧࡪࡤࡠࡤࡨࡪࡴࡸࡥࡠࡵࡦࡩࡳࡧࡲࡪࡱ࠽ࠤࢀࢃࠧ⋰"), str(err))
def bstack1lll1ll11ll1_opy_(bstack111ll111ll_opy_):
    if bstack111ll111ll_opy_ in store[bstack111l11_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡩࡱࡲ࡯ࡤࡻࡵࡪࡦࠪ⋱")]:
        store[bstack111l11_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡪࡲࡳࡰࡥࡵࡶ࡫ࡧࠫ⋲")].remove(bstack111ll111ll_opy_)
def bstack1lll1ll1ll1l_opy_(test_uuid):
    store[bstack111l11_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡶࡷ࡬ࡨࠬ⋳")] = test_uuid
    threading.current_thread().current_test_uuid = test_uuid
@bstack111l1ll1_opy_.bstack1llll1ll11l1_opy_
def bstack1lll1llllll1_opy_(item, call, report):
    logger.debug(bstack111l11_opy_ (u"ࠩ࡫ࡥࡳࡪ࡬ࡦࡡࡲ࠵࠶ࡿ࡟ࡵࡧࡶࡸࡤ࡫ࡶࡦࡰࡷ࠾ࠥࡹࡴࡢࡴࡷࠫ⋴"))
    global bstack1lll1lll111l_opy_
    bstack1ll11ll1ll_opy_ = bstack11ll11lll_opy_()
    if hasattr(report, bstack111l11_opy_ (u"ࠪࡷࡹࡵࡰࠨ⋵")):
        bstack1ll11ll1ll_opy_ = bstack111llllll1l_opy_(report.stop)
    elif hasattr(report, bstack111l11_opy_ (u"ࠫࡸࡺࡡࡳࡶࠪ⋶")):
        bstack1ll11ll1ll_opy_ = bstack111llllll1l_opy_(report.start)
    try:
        if getattr(report, bstack111l11_opy_ (u"ࠬࡽࡨࡦࡰࠪ⋷"), bstack111l11_opy_ (u"࠭ࠧ⋸")) == bstack111l11_opy_ (u"ࠧࡤࡣ࡯ࡰࠬ⋹"):
            logger.debug(bstack111l11_opy_ (u"ࠨࡪࡤࡲࡩࡲࡥࡠࡱ࠴࠵ࡾࡥࡴࡦࡵࡷࡣࡪࡼࡥ࡯ࡶ࠽ࠤࡸࡺࡡࡵࡧࠣ࠱ࠥࢁࡽ࠭ࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠥ࠳ࠠࡼࡿࠪ⋺").format(getattr(report, bstack111l11_opy_ (u"ࠩࡺ࡬ࡪࡴࠧ⋻"), bstack111l11_opy_ (u"ࠪࠫ⋼")).__str__(), bstack1lll1lll111l_opy_))
            if bstack1lll1lll111l_opy_ == bstack111l11_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫ⋽"):
                _1111l1llll_opy_[item.nodeid][bstack111l11_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪ⋾")] = bstack1ll11ll1ll_opy_
                bstack1lll1ll1llll_opy_(item, _1111l1llll_opy_[item.nodeid], bstack111l11_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨ⋿"), report, call)
                store[bstack111l11_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡵࡶ࡫ࡧࠫ⌀")] = None
            elif bstack1lll1lll111l_opy_ == bstack111l11_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠧ⌁"):
                bstack111l1llll1_opy_ = _1111l1llll_opy_[item.nodeid][bstack111l11_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬ⌂")]
                bstack111l1llll1_opy_.set(hooks=_1111l1llll_opy_[item.nodeid].get(bstack111l11_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡴࠩ⌃"), []))
                exception, bstack111ll11lll_opy_ = None, None
                if call.excinfo:
                    exception = call.excinfo.value
                    bstack111ll11lll_opy_ = [call.excinfo.exconly(), getattr(report, bstack111l11_opy_ (u"ࠫࡱࡵ࡮ࡨࡴࡨࡴࡷࡺࡥࡹࡶࠪ⌄"), bstack111l11_opy_ (u"ࠬ࠭⌅"))]
                bstack111l1llll1_opy_.stop(time=bstack1ll11ll1ll_opy_, result=Result(result=getattr(report, bstack111l11_opy_ (u"࠭࡯ࡶࡶࡦࡳࡲ࡫ࠧ⌆"), bstack111l11_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧ⌇")), exception=exception, bstack111ll11lll_opy_=bstack111ll11lll_opy_))
                bstack111l1ll1_opy_.bstack111ll11l11_opy_(bstack111l11_opy_ (u"ࠨࡖࡨࡷࡹࡘࡵ࡯ࡈ࡬ࡲ࡮ࡹࡨࡦࡦࠪ⌈"), _1111l1llll_opy_[item.nodeid][bstack111l11_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬ⌉")])
        elif getattr(report, bstack111l11_opy_ (u"ࠪࡻ࡭࡫࡮ࠨ⌊"), bstack111l11_opy_ (u"ࠫࠬ⌋")) in [bstack111l11_opy_ (u"ࠬࡹࡥࡵࡷࡳࠫ⌌"), bstack111l11_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮ࠨ⌍")]:
            logger.debug(bstack111l11_opy_ (u"ࠧࡩࡣࡱࡨࡱ࡫࡟ࡰ࠳࠴ࡽࡤࡺࡥࡴࡶࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡷࡹࡧࡴࡦࠢ࠰ࠤࢀࢃࠬࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠤ࠲ࠦࡻࡾࠩ⌎").format(getattr(report, bstack111l11_opy_ (u"ࠨࡹ࡫ࡩࡳ࠭⌏"), bstack111l11_opy_ (u"ࠩࠪ⌐")).__str__(), bstack1lll1lll111l_opy_))
            bstack111lll11ll_opy_ = item.nodeid + bstack111l11_opy_ (u"ࠪ࠱ࠬ⌑") + getattr(report, bstack111l11_opy_ (u"ࠫࡼ࡮ࡥ࡯ࠩ⌒"), bstack111l11_opy_ (u"ࠬ࠭⌓"))
            if getattr(report, bstack111l11_opy_ (u"࠭ࡳ࡬࡫ࡳࡴࡪࡪࠧ⌔"), False):
                hook_type = bstack111l11_opy_ (u"ࠧࡃࡇࡉࡓࡗࡋ࡟ࡆࡃࡆࡌࠬ⌕") if getattr(report, bstack111l11_opy_ (u"ࠨࡹ࡫ࡩࡳ࠭⌖"), bstack111l11_opy_ (u"ࠩࠪ⌗")) == bstack111l11_opy_ (u"ࠪࡷࡪࡺࡵࡱࠩ⌘") else bstack111l11_opy_ (u"ࠫࡆࡌࡔࡆࡔࡢࡉࡆࡉࡈࠨ⌙")
                _1111l1llll_opy_[bstack111lll11ll_opy_] = {
                    bstack111l11_opy_ (u"ࠬࡻࡵࡪࡦࠪ⌚"): uuid4().__str__(),
                    bstack111l11_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪ⌛"): bstack1ll11ll1ll_opy_,
                    bstack111l11_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡺࡹࡱࡧࠪ⌜"): hook_type
                }
            _1111l1llll_opy_[bstack111lll11ll_opy_][bstack111l11_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭⌝")] = bstack1ll11ll1ll_opy_
            bstack1lll1ll11ll1_opy_(_1111l1llll_opy_[bstack111lll11ll_opy_][bstack111l11_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ⌞")])
            bstack1lll1llll1l1_opy_(item, _1111l1llll_opy_[bstack111lll11ll_opy_], bstack111l11_opy_ (u"ࠪࡌࡴࡵ࡫ࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬ⌟"), report, call)
            if getattr(report, bstack111l11_opy_ (u"ࠫࡼ࡮ࡥ࡯ࠩ⌠"), bstack111l11_opy_ (u"ࠬ࠭⌡")) == bstack111l11_opy_ (u"࠭ࡳࡦࡶࡸࡴࠬ⌢"):
                if getattr(report, bstack111l11_opy_ (u"ࠧࡰࡷࡷࡧࡴࡳࡥࠨ⌣"), bstack111l11_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨ⌤")) == bstack111l11_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ⌥"):
                    bstack111l11l11l_opy_ = {
                        bstack111l11_opy_ (u"ࠪࡹࡺ࡯ࡤࠨ⌦"): uuid4().__str__(),
                        bstack111l11_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨ⌧"): bstack11ll11lll_opy_(),
                        bstack111l11_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪ⌨"): bstack11ll11lll_opy_()
                    }
                    _1111l1llll_opy_[item.nodeid] = {**_1111l1llll_opy_[item.nodeid], **bstack111l11l11l_opy_}
                    bstack1lll1ll1llll_opy_(item, _1111l1llll_opy_[item.nodeid], bstack111l11_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡓࡵࡣࡵࡸࡪࡪࠧ〈"))
                    bstack1lll1ll1llll_opy_(item, _1111l1llll_opy_[item.nodeid], bstack111l11_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡇ࡫ࡱ࡭ࡸ࡮ࡥࡥࠩ〉"), report, call)
    except Exception as err:
        print(bstack111l11_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡩࡣࡱࡨࡱ࡫࡟ࡰ࠳࠴ࡽࡤࡺࡥࡴࡶࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡿࢂ࠭⌫"), str(err))
def bstack1lll1lll1ll1_opy_(test, bstack111l11l11l_opy_, result=None, call=None, bstack1l1lll1ll_opy_=None, outcome=None):
    file_path = os.path.relpath(test.fspath.strpath, start=os.getcwd())
    bstack111l1llll1_opy_ = {
        bstack111l11_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ⌬"): bstack111l11l11l_opy_[bstack111l11_opy_ (u"ࠪࡹࡺ࡯ࡤࠨ⌭")],
        bstack111l11_opy_ (u"ࠫࡹࡿࡰࡦࠩ⌮"): bstack111l11_opy_ (u"ࠬࡺࡥࡴࡶࠪ⌯"),
        bstack111l11_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ⌰"): test.name,
        bstack111l11_opy_ (u"ࠧࡣࡱࡧࡽࠬ⌱"): {
            bstack111l11_opy_ (u"ࠨ࡮ࡤࡲ࡬࠭⌲"): bstack111l11_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯ࠩ⌳"),
            bstack111l11_opy_ (u"ࠪࡧࡴࡪࡥࠨ⌴"): inspect.getsource(test.obj)
        },
        bstack111l11_opy_ (u"ࠫ࡮ࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ⌵"): test.name,
        bstack111l11_opy_ (u"ࠬࡹࡣࡰࡲࡨࠫ⌶"): test.name,
        bstack111l11_opy_ (u"࠭ࡳࡤࡱࡳࡩࡸ࠭⌷"): bstack1l1lll1ll1_opy_.bstack111l11lll1_opy_(test),
        bstack111l11_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪ⌸"): file_path,
        bstack111l11_opy_ (u"ࠨ࡮ࡲࡧࡦࡺࡩࡰࡰࠪ⌹"): file_path,
        bstack111l11_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩ⌺"): bstack111l11_opy_ (u"ࠪࡴࡪࡴࡤࡪࡰࡪࠫ⌻"),
        bstack111l11_opy_ (u"ࠫࡻࡩ࡟ࡧ࡫࡯ࡩࡵࡧࡴࡩࠩ⌼"): file_path,
        bstack111l11_opy_ (u"ࠬࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠩ⌽"): bstack111l11l11l_opy_[bstack111l11_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪ⌾")],
        bstack111l11_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪ⌿"): bstack111l11_opy_ (u"ࠨࡒࡼࡸࡪࡹࡴࠨ⍀"),
        bstack111l11_opy_ (u"ࠩࡦࡹࡸࡺ࡯࡮ࡔࡨࡶࡺࡴࡐࡢࡴࡤࡱࠬ⍁"): {
            bstack111l11_opy_ (u"ࠪࡶࡪࡸࡵ࡯ࡡࡱࡥࡲ࡫ࠧ⍂"): test.nodeid
        },
        bstack111l11_opy_ (u"ࠫࡹࡧࡧࡴࠩ⍃"): bstack11l111lllll_opy_(test.own_markers)
    }
    if bstack1l1lll1ll_opy_ in [bstack111l11_opy_ (u"࡚ࠬࡥࡴࡶࡕࡹࡳ࡙࡫ࡪࡲࡳࡩࡩ࠭⍄"), bstack111l11_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨ⍅")]:
        bstack111l1llll1_opy_[bstack111l11_opy_ (u"ࠧ࡮ࡧࡷࡥࠬ⍆")] = {
            bstack111l11_opy_ (u"ࠨࡨ࡬ࡼࡹࡻࡲࡦࡵࠪ⍇"): bstack111l11l11l_opy_.get(bstack111l11_opy_ (u"ࠩࡩ࡭ࡽࡺࡵࡳࡧࡶࠫ⍈"), [])
        }
    if bstack1l1lll1ll_opy_ == bstack111l11_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡗࡰ࡯ࡰࡱࡧࡧࠫ⍉"):
        bstack111l1llll1_opy_[bstack111l11_opy_ (u"ࠫࡷ࡫ࡳࡶ࡮ࡷࠫ⍊")] = bstack111l11_opy_ (u"ࠬࡹ࡫ࡪࡲࡳࡩࡩ࠭⍋")
        bstack111l1llll1_opy_[bstack111l11_opy_ (u"࠭ࡨࡰࡱ࡮ࡷࠬ⍌")] = bstack111l11l11l_opy_[bstack111l11_opy_ (u"ࠧࡩࡱࡲ࡯ࡸ࠭⍍")]
        bstack111l1llll1_opy_[bstack111l11_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭⍎")] = bstack111l11l11l_opy_[bstack111l11_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧ⍏")]
    if result:
        bstack111l1llll1_opy_[bstack111l11_opy_ (u"ࠪࡶࡪࡹࡵ࡭ࡶࠪ⍐")] = result.outcome
        bstack111l1llll1_opy_[bstack111l11_opy_ (u"ࠫࡩࡻࡲࡢࡶ࡬ࡳࡳࡥࡩ࡯ࡡࡰࡷࠬ⍑")] = result.duration * 1000
        bstack111l1llll1_opy_[bstack111l11_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪ⍒")] = bstack111l11l11l_opy_[bstack111l11_opy_ (u"࠭ࡦࡪࡰ࡬ࡷ࡭࡫ࡤࡠࡣࡷࠫ⍓")]
        if result.failed:
            bstack111l1llll1_opy_[bstack111l11_opy_ (u"ࠧࡧࡣ࡬ࡰࡺࡸࡥࡠࡶࡼࡴࡪ࠭⍔")] = bstack111l1ll1_opy_.bstack1111111l1l_opy_(call.excinfo.typename)
            bstack111l1llll1_opy_[bstack111l11_opy_ (u"ࠨࡨࡤ࡭ࡱࡻࡲࡦࠩ⍕")] = bstack111l1ll1_opy_.bstack1llll1l11ll1_opy_(call.excinfo, result)
        bstack111l1llll1_opy_[bstack111l11_opy_ (u"ࠩ࡫ࡳࡴࡱࡳࠨ⍖")] = bstack111l11l11l_opy_[bstack111l11_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡴࠩ⍗")]
    if outcome:
        bstack111l1llll1_opy_[bstack111l11_opy_ (u"ࠫࡷ࡫ࡳࡶ࡮ࡷࠫ⍘")] = bstack11l111llll1_opy_(outcome)
        bstack111l1llll1_opy_[bstack111l11_opy_ (u"ࠬࡪࡵࡳࡣࡷ࡭ࡴࡴ࡟ࡪࡰࡢࡱࡸ࠭⍙")] = 0
        bstack111l1llll1_opy_[bstack111l11_opy_ (u"࠭ࡦࡪࡰ࡬ࡷ࡭࡫ࡤࡠࡣࡷࠫ⍚")] = bstack111l11l11l_opy_[bstack111l11_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬ⍛")]
        if bstack111l1llll1_opy_[bstack111l11_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨ⍜")] == bstack111l11_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ⍝"):
            bstack111l1llll1_opy_[bstack111l11_opy_ (u"ࠪࡪࡦ࡯࡬ࡶࡴࡨࡣࡹࡿࡰࡦࠩ⍞")] = bstack111l11_opy_ (u"࡚ࠫࡴࡨࡢࡰࡧࡰࡪࡪࡅࡳࡴࡲࡶࠬ⍟")  # bstack1lll1ll1l1l1_opy_
            bstack111l1llll1_opy_[bstack111l11_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡸࡶࡪ࠭⍠")] = [{bstack111l11_opy_ (u"࠭ࡢࡢࡥ࡮ࡸࡷࡧࡣࡦࠩ⍡"): [bstack111l11_opy_ (u"ࠧࡴࡱࡰࡩࠥ࡫ࡲࡳࡱࡵࠫ⍢")]}]
        bstack111l1llll1_opy_[bstack111l11_opy_ (u"ࠨࡪࡲࡳࡰࡹࠧ⍣")] = bstack111l11l11l_opy_[bstack111l11_opy_ (u"ࠩ࡫ࡳࡴࡱࡳࠨ⍤")]
    return bstack111l1llll1_opy_
def bstack1lll1lll11l1_opy_(test, bstack1111ll1111_opy_, bstack1l1lll1ll_opy_, result, call, outcome, bstack1llll1111l11_opy_):
    file_path = os.path.relpath(test.fspath.strpath, start=os.getcwd())
    hook_type = bstack1111ll1111_opy_[bstack111l11_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡶࡼࡴࡪ࠭⍥")]
    hook_name = bstack1111ll1111_opy_[bstack111l11_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡱࡥࡲ࡫ࠧ⍦")]
    hook_data = {
        bstack111l11_opy_ (u"ࠬࡻࡵࡪࡦࠪ⍧"): bstack1111ll1111_opy_[bstack111l11_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ⍨")],
        bstack111l11_opy_ (u"ࠧࡵࡻࡳࡩࠬ⍩"): bstack111l11_opy_ (u"ࠨࡪࡲࡳࡰ࠭⍪"),
        bstack111l11_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ⍫"): bstack111l11_opy_ (u"ࠪࡿࢂ࠭⍬").format(bstack1lllllll1l11_opy_(hook_name)),
        bstack111l11_opy_ (u"ࠫࡧࡵࡤࡺࠩ⍭"): {
            bstack111l11_opy_ (u"ࠬࡲࡡ࡯ࡩࠪ⍮"): bstack111l11_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭⍯"),
            bstack111l11_opy_ (u"ࠧࡤࡱࡧࡩࠬ⍰"): None
        },
        bstack111l11_opy_ (u"ࠨࡵࡦࡳࡵ࡫ࠧ⍱"): test.name,
        bstack111l11_opy_ (u"ࠩࡶࡧࡴࡶࡥࡴࠩ⍲"): bstack1l1lll1ll1_opy_.bstack111l11lll1_opy_(test, hook_name),
        bstack111l11_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭⍳"): file_path,
        bstack111l11_opy_ (u"ࠫࡱࡵࡣࡢࡶ࡬ࡳࡳ࠭⍴"): file_path,
        bstack111l11_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬ⍵"): bstack111l11_opy_ (u"࠭ࡰࡦࡰࡧ࡭ࡳ࡭ࠧ⍶"),
        bstack111l11_opy_ (u"ࠧࡷࡥࡢࡪ࡮ࡲࡥࡱࡣࡷ࡬ࠬ⍷"): file_path,
        bstack111l11_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬ⍸"): bstack1111ll1111_opy_[bstack111l11_opy_ (u"ࠩࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹ࠭⍹")],
        bstack111l11_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭⍺"): bstack111l11_opy_ (u"ࠫࡕࡿࡴࡦࡵࡷ࠱ࡨࡻࡣࡶ࡯ࡥࡩࡷ࠭⍻") if bstack1lll1lll111l_opy_ == bstack111l11_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠩ⍼") else bstack111l11_opy_ (u"࠭ࡐࡺࡶࡨࡷࡹ࠭⍽"),
        bstack111l11_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡺࡹࡱࡧࠪ⍾"): hook_type
    }
    bstack1ll11ll1111_opy_ = bstack1111lll1ll_opy_(_1111l1llll_opy_.get(test.nodeid, None))
    if bstack1ll11ll1111_opy_:
        hook_data[bstack111l11_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢ࡭ࡩ࠭⍿")] = bstack1ll11ll1111_opy_
    if result:
        hook_data[bstack111l11_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩ⎀")] = result.outcome
        hook_data[bstack111l11_opy_ (u"ࠪࡨࡺࡸࡡࡵ࡫ࡲࡲࡤ࡯࡮ࡠ࡯ࡶࠫ⎁")] = result.duration * 1000
        hook_data[bstack111l11_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩ⎂")] = bstack1111ll1111_opy_[bstack111l11_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪ⎃")]
        if result.failed:
            hook_data[bstack111l11_opy_ (u"࠭ࡦࡢ࡫࡯ࡹࡷ࡫࡟ࡵࡻࡳࡩࠬ⎄")] = bstack111l1ll1_opy_.bstack1111111l1l_opy_(call.excinfo.typename)
            hook_data[bstack111l11_opy_ (u"ࠧࡧࡣ࡬ࡰࡺࡸࡥࠨ⎅")] = bstack111l1ll1_opy_.bstack1llll1l11ll1_opy_(call.excinfo, result)
    if outcome:
        hook_data[bstack111l11_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨ⎆")] = bstack11l111llll1_opy_(outcome)
        hook_data[bstack111l11_opy_ (u"ࠩࡧࡹࡷࡧࡴࡪࡱࡱࡣ࡮ࡴ࡟࡮ࡵࠪ⎇")] = 100
        hook_data[bstack111l11_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨ⎈")] = bstack1111ll1111_opy_[bstack111l11_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩ⎉")]
        if hook_data[bstack111l11_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬ⎊")] == bstack111l11_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭⎋"):
            hook_data[bstack111l11_opy_ (u"ࠧࡧࡣ࡬ࡰࡺࡸࡥࡠࡶࡼࡴࡪ࠭⎌")] = bstack111l11_opy_ (u"ࠨࡗࡱ࡬ࡦࡴࡤ࡭ࡧࡧࡉࡷࡸ࡯ࡳࠩ⎍")  # bstack1lll1ll1l1l1_opy_
            hook_data[bstack111l11_opy_ (u"ࠩࡩࡥ࡮ࡲࡵࡳࡧࠪ⎎")] = [{bstack111l11_opy_ (u"ࠪࡦࡦࡩ࡫ࡵࡴࡤࡧࡪ࠭⎏"): [bstack111l11_opy_ (u"ࠫࡸࡵ࡭ࡦࠢࡨࡶࡷࡵࡲࠨ⎐")]}]
    if bstack1llll1111l11_opy_:
        hook_data[bstack111l11_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬ⎑")] = bstack1llll1111l11_opy_.result
        hook_data[bstack111l11_opy_ (u"࠭ࡤࡶࡴࡤࡸ࡮ࡵ࡮ࡠ࡫ࡱࡣࡲࡹࠧ⎒")] = bstack111ll11l1l1_opy_(bstack1111ll1111_opy_[bstack111l11_opy_ (u"ࠧࡴࡶࡤࡶࡹ࡫ࡤࡠࡣࡷࠫ⎓")], bstack1111ll1111_opy_[bstack111l11_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭⎔")])
        hook_data[bstack111l11_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧ⎕")] = bstack1111ll1111_opy_[bstack111l11_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨ⎖")]
        if hook_data[bstack111l11_opy_ (u"ࠫࡷ࡫ࡳࡶ࡮ࡷࠫ⎗")] == bstack111l11_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ⎘"):
            hook_data[bstack111l11_opy_ (u"࠭ࡦࡢ࡫࡯ࡹࡷ࡫࡟ࡵࡻࡳࡩࠬ⎙")] = bstack111l1ll1_opy_.bstack1111111l1l_opy_(bstack1llll1111l11_opy_.exception_type)
            hook_data[bstack111l11_opy_ (u"ࠧࡧࡣ࡬ࡰࡺࡸࡥࠨ⎚")] = [{bstack111l11_opy_ (u"ࠨࡤࡤࡧࡰࡺࡲࡢࡥࡨࠫ⎛"): bstack111lll11l11_opy_(bstack1llll1111l11_opy_.exception)}]
    return hook_data
def bstack1lll1ll1llll_opy_(test, bstack111l11l11l_opy_, bstack1l1lll1ll_opy_, result=None, call=None, outcome=None):
    logger.debug(bstack111l11_opy_ (u"ࠩࡶࡩࡳࡪ࡟ࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡨࡺࡪࡴࡴ࠻ࠢࡄࡸࡹ࡫࡭ࡱࡶ࡬ࡲ࡬ࠦࡴࡰࠢࡪࡩࡳ࡫ࡲࡢࡶࡨࠤࡹ࡫ࡳࡵࠢࡧࡥࡹࡧࠠࡧࡱࡵࠤࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥࠡ࠯ࠣࡿࢂ࠭⎜").format(bstack1l1lll1ll_opy_))
    bstack111l1llll1_opy_ = bstack1lll1lll1ll1_opy_(test, bstack111l11l11l_opy_, result, call, bstack1l1lll1ll_opy_, outcome)
    driver = getattr(test, bstack111l11_opy_ (u"ࠪࡣࡩࡸࡩࡷࡧࡵࠫ⎝"), None)
    if bstack1l1lll1ll_opy_ == bstack111l11_opy_ (u"࡙ࠫ࡫ࡳࡵࡔࡸࡲࡘࡺࡡࡳࡶࡨࡨࠬ⎞") and driver:
        bstack111l1llll1_opy_[bstack111l11_opy_ (u"ࠬ࡯࡮ࡵࡧࡪࡶࡦࡺࡩࡰࡰࡶࠫ⎟")] = bstack111l1ll1_opy_.bstack111ll11l1l_opy_(driver)
    if bstack1l1lll1ll_opy_ == bstack111l11_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡓ࡬࡫ࡳࡴࡪࡪࠧ⎠"):
        bstack1l1lll1ll_opy_ = bstack111l11_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡇ࡫ࡱ࡭ࡸ࡮ࡥࡥࠩ⎡")
    bstack111l1l1l11_opy_ = {
        bstack111l11_opy_ (u"ࠨࡧࡹࡩࡳࡺ࡟ࡵࡻࡳࡩࠬ⎢"): bstack1l1lll1ll_opy_,
        bstack111l11_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࠫ⎣"): bstack111l1llll1_opy_
    }
    bstack111l1ll1_opy_.bstack1ll1l1ll_opy_(bstack111l1l1l11_opy_)
    if bstack1l1lll1ll_opy_ == bstack111l11_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡗࡹࡧࡲࡵࡧࡧࠫ⎤"):
        threading.current_thread().bstackTestMeta = {bstack111l11_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ⎥"): bstack111l11_opy_ (u"ࠬࡶࡥ࡯ࡦ࡬ࡲ࡬࠭⎦")}
    elif bstack1l1lll1ll_opy_ == bstack111l11_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨ⎧"):
        threading.current_thread().bstackTestMeta = {bstack111l11_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧ⎨"): getattr(result, bstack111l11_opy_ (u"ࠨࡱࡸࡸࡨࡵ࡭ࡦࠩ⎩"), bstack111l11_opy_ (u"ࠩࠪ⎪"))}
def bstack1lll1llll1l1_opy_(test, bstack111l11l11l_opy_, bstack1l1lll1ll_opy_, result=None, call=None, outcome=None, bstack1llll1111l11_opy_=None):
    logger.debug(bstack111l11_opy_ (u"ࠪࡷࡪࡴࡤࡠࡪࡲࡳࡰࡥࡲࡶࡰࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡅࡹࡺࡥ࡮ࡲࡷ࡭ࡳ࡭ࠠࡵࡱࠣ࡫ࡪࡴࡥࡳࡣࡷࡩࠥ࡮࡯ࡰ࡭ࠣࡨࡦࡺࡡ࠭ࠢࡨࡺࡪࡴࡴࡕࡻࡳࡩࠥ࠳ࠠࡼࡿࠪ⎫").format(bstack1l1lll1ll_opy_))
    hook_data = bstack1lll1lll11l1_opy_(test, bstack111l11l11l_opy_, bstack1l1lll1ll_opy_, result, call, outcome, bstack1llll1111l11_opy_)
    bstack111l1l1l11_opy_ = {
        bstack111l11_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥࠨ⎬"): bstack1l1lll1ll_opy_,
        bstack111l11_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡶࡺࡴࠧ⎭"): hook_data
    }
    bstack111l1ll1_opy_.bstack1ll1l1ll_opy_(bstack111l1l1l11_opy_)
def bstack1111lll1ll_opy_(bstack111l11l11l_opy_):
    if not bstack111l11l11l_opy_:
        return None
    if bstack111l11l11l_opy_.get(bstack111l11_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩ⎮"), None):
        return getattr(bstack111l11l11l_opy_[bstack111l11_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣࠪ⎯")], bstack111l11_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭⎰"), None)
    return bstack111l11l11l_opy_.get(bstack111l11_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ⎱"), None)
@pytest.fixture(autouse=True)
def second_fixture(caplog, request):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1lll11ll111_opy_.LOG, bstack1lll1lll111_opy_.PRE, request, caplog)
    yield
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1lll11ll111_opy_.LOG, bstack1lll1lll111_opy_.POST, request, caplog)
        return # skip all existing operations
    try:
        if not bstack111l1ll1_opy_.on():
            return
        places = [bstack111l11_opy_ (u"ࠪࡷࡪࡺࡵࡱࠩ⎲"), bstack111l11_opy_ (u"ࠫࡨࡧ࡬࡭ࠩ⎳"), bstack111l11_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴࠧ⎴")]
        logs = []
        for bstack1llll1111ll1_opy_ in places:
            records = caplog.get_records(bstack1llll1111ll1_opy_)
            bstack1lll1lll1111_opy_ = bstack111l11_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭⎵") if bstack1llll1111ll1_opy_ == bstack111l11_opy_ (u"ࠧࡤࡣ࡯ࡰࠬ⎶") else bstack111l11_opy_ (u"ࠨࡪࡲࡳࡰࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ⎷")
            bstack1llll111111l_opy_ = request.node.nodeid + (bstack111l11_opy_ (u"ࠩࠪ⎸") if bstack1llll1111ll1_opy_ == bstack111l11_opy_ (u"ࠪࡧࡦࡲ࡬ࠨ⎹") else bstack111l11_opy_ (u"ࠫ࠲࠭⎺") + bstack1llll1111ll1_opy_)
            test_uuid = bstack1111lll1ll_opy_(_1111l1llll_opy_.get(bstack1llll111111l_opy_, None))
            if not test_uuid:
                continue
            for record in records:
                if bstack11l11l11l1l_opy_(record.message):
                    continue
                logs.append({
                    bstack111l11_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨ⎻"): bstack11l11l11111_opy_(record.created).isoformat() + bstack111l11_opy_ (u"࡚࠭ࠨ⎼"),
                    bstack111l11_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭⎽"): record.levelname,
                    bstack111l11_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩ⎾"): record.message,
                    bstack1lll1lll1111_opy_: test_uuid
                })
        if len(logs) > 0:
            bstack111l1ll1_opy_.bstack11l1ll111_opy_(logs)
    except Exception as err:
        print(bstack111l11_opy_ (u"ࠩࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡵࡨࡧࡴࡴࡤࡠࡨ࡬ࡼࡹࡻࡲࡦ࠼ࠣࡿࢂ࠭⎿"), str(err))
def bstack1lll11ll_opy_(sequence, driver_command, response=None, driver = None, args = None):
    global bstack11l11l11ll_opy_
    bstack1ll11llll1_opy_ = bstack1l11lllll1_opy_(threading.current_thread(), bstack111l11_opy_ (u"ࠪ࡭ࡸࡇ࠱࠲ࡻࡗࡩࡸࡺࠧ⏀"), None) and bstack1l11lllll1_opy_(
            threading.current_thread(), bstack111l11_opy_ (u"ࠫࡦ࠷࠱ࡺࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪ⏁"), None)
    bstack1lll1ll1l1_opy_ = getattr(driver, bstack111l11_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡆ࠷࠱ࡺࡕ࡫ࡳࡺࡲࡤࡔࡥࡤࡲࠬ⏂"), None) != None and getattr(driver, bstack111l11_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡇ࠱࠲ࡻࡖ࡬ࡴࡻ࡬ࡥࡕࡦࡥࡳ࠭⏃"), None) == True
    if sequence == bstack111l11_opy_ (u"ࠧࡣࡧࡩࡳࡷ࡫ࠧ⏄") and driver != None:
      if not bstack11l11l11ll_opy_ and bstack1l1l1ll11ll_opy_() and bstack111l11_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ⏅") in CONFIG and CONFIG[bstack111l11_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩ⏆")] == True and bstack11l1ll111l_opy_.bstack1l1l1lll1_opy_(driver_command) and (bstack1lll1ll1l1_opy_ or bstack1ll11llll1_opy_) and not bstack11l1l1l1l_opy_(args):
        try:
          bstack11l11l11ll_opy_ = True
          logger.debug(bstack111l11_opy_ (u"ࠪࡔࡪࡸࡦࡰࡴࡰ࡭ࡳ࡭ࠠࡴࡥࡤࡲࠥ࡬࡯ࡳࠢࡾࢁࠬ⏇").format(driver_command))
          logger.debug(perform_scan(driver, driver_command=driver_command))
        except Exception as err:
          logger.debug(bstack111l11_opy_ (u"ࠫࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡱࡧࡵࡪࡴࡸ࡭ࠡࡵࡦࡥࡳࠦࡻࡾࠩ⏈").format(str(err)))
        bstack11l11l11ll_opy_ = False
    if sequence == bstack111l11_opy_ (u"ࠬࡧࡦࡵࡧࡵࠫ⏉"):
        if driver_command == bstack111l11_opy_ (u"࠭ࡳࡤࡴࡨࡩࡳࡹࡨࡰࡶࠪ⏊"):
            bstack111l1ll1_opy_.bstack111ll11l_opy_({
                bstack111l11_opy_ (u"ࠧࡪ࡯ࡤ࡫ࡪ࠭⏋"): response[bstack111l11_opy_ (u"ࠨࡸࡤࡰࡺ࡫ࠧ⏌")],
                bstack111l11_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ⏍"): store[bstack111l11_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡹ࡫ࡳࡵࡡࡸࡹ࡮ࡪࠧ⏎")]
            })
def bstack11llll1ll_opy_():
    global bstack1lll1ll1l_opy_
    bstack11l1l1111_opy_.bstack11lll1ll1l_opy_()
    logging.shutdown()
    bstack111l1ll1_opy_.bstack111l1111ll_opy_()
    for driver in bstack1lll1ll1l_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
def bstack1lll1ll11lll_opy_(*args):
    global bstack1lll1ll1l_opy_
    bstack111l1ll1_opy_.bstack111l1111ll_opy_()
    for driver in bstack1lll1ll1l_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
@measure(event_name=EVENTS.bstack1l11l1l1l1_opy_, stage=STAGE.bstack111lllll1_opy_, bstack11l1l1lll1_opy_=bstack1ll1l111l_opy_)
def bstack1ll11l1ll1_opy_(self, *args, **kwargs):
    bstack1l11ll1l11_opy_ = bstack11ll11111_opy_(self, *args, **kwargs)
    bstack1ll111l11_opy_ = getattr(threading.current_thread(), bstack111l11_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡘࡪࡹࡴࡎࡧࡷࡥࠬ⏏"), None)
    if bstack1ll111l11_opy_ and bstack1ll111l11_opy_.get(bstack111l11_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬ⏐"), bstack111l11_opy_ (u"࠭ࠧ⏑")) == bstack111l11_opy_ (u"ࠧࡱࡧࡱࡨ࡮ࡴࡧࠨ⏒"):
        bstack111l1ll1_opy_.bstack1ll111l1ll_opy_(self)
    return bstack1l11ll1l11_opy_
@measure(event_name=EVENTS.bstack11lll11l1_opy_, stage=STAGE.bstack11ll111ll1_opy_, bstack11l1l1lll1_opy_=bstack1ll1l111l_opy_)
def bstack1l11111l_opy_(framework_name):
    from bstack_utils.config import Config
    bstack1llll1111_opy_ = Config.bstack1lll111l11_opy_()
    if bstack1llll1111_opy_.get_property(bstack111l11_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡠ࡯ࡲࡨࡤࡩࡡ࡭࡮ࡨࡨࠬ⏓")):
        return
    bstack1llll1111_opy_.bstack1l1l1l1lll_opy_(bstack111l11_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡡࡰࡳࡩࡥࡣࡢ࡮࡯ࡩࡩ࠭⏔"), True)
    global bstack1l1llll11l_opy_
    global bstack1ll1l1111l_opy_
    bstack1l1llll11l_opy_ = framework_name
    logger.info(bstack1ll1111ll_opy_.format(bstack1l1llll11l_opy_.split(bstack111l11_opy_ (u"ࠪ࠱ࠬ⏕"))[0]))
    try:
        from selenium import webdriver
        from selenium.webdriver.common.service import Service
        from selenium.webdriver.remote.webdriver import WebDriver
        if bstack1l1l1ll11ll_opy_():
            Service.start = bstack111l11l1l_opy_
            Service.stop = bstack1ll111ll1_opy_
            webdriver.Remote.get = bstack1l11l1111l_opy_
            webdriver.Remote.__init__ = bstack1ll111ll_opy_
            if not isinstance(os.getenv(bstack111l11_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔ࡞࡚ࡅࡔࡖࡢࡔࡆࡘࡁࡍࡎࡈࡐࠬ⏖")), str):
                return
            WebDriver.quit = bstack1ll1l1l1_opy_
            WebDriver.getAccessibilityResults = getAccessibilityResults
            WebDriver.get_accessibility_results = getAccessibilityResults
            WebDriver.getAccessibilityResultsSummary = getAccessibilityResultsSummary
            WebDriver.get_accessibility_results_summary = getAccessibilityResultsSummary
            WebDriver.performScan = perform_scan
            WebDriver.perform_scan = perform_scan
        elif bstack111l1ll1_opy_.on():
            webdriver.Remote.__init__ = bstack1ll11l1ll1_opy_
        bstack1ll1l1111l_opy_ = True
    except Exception as e:
        pass
    if os.environ.get(bstack111l11_opy_ (u"࡙ࠬࡅࡍࡇࡑࡍ࡚ࡓ࡟ࡐࡔࡢࡔࡑࡇ࡙ࡘࡔࡌࡋࡍ࡚࡟ࡊࡐࡖࡘࡆࡒࡌࡆࡆࠪ⏗")):
        bstack1ll1l1111l_opy_ = eval(os.environ.get(bstack111l11_opy_ (u"࠭ࡓࡆࡎࡈࡒࡎ࡛ࡍࡠࡑࡕࡣࡕࡒࡁ࡚࡙ࡕࡍࡌࡎࡔࡠࡋࡑࡗ࡙ࡇࡌࡍࡇࡇࠫ⏘")))
    if not bstack1ll1l1111l_opy_:
        bstack1l11l11l11_opy_(bstack111l11_opy_ (u"ࠢࡑࡣࡦ࡯ࡦ࡭ࡥࡴࠢࡱࡳࡹࠦࡩ࡯ࡵࡷࡥࡱࡲࡥࡥࠤ⏙"), bstack11lll1111l_opy_)
    if bstack1l1l1lll_opy_():
        try:
            from selenium.webdriver.remote.remote_connection import RemoteConnection
            if hasattr(RemoteConnection, bstack111l11_opy_ (u"ࠨࡡࡪࡩࡹࡥࡰࡳࡱࡻࡽࡤࡻࡲ࡭ࠩ⏚")) and callable(getattr(RemoteConnection, bstack111l11_opy_ (u"ࠩࡢ࡫ࡪࡺ࡟ࡱࡴࡲࡼࡾࡥࡵࡳ࡮ࠪ⏛"))):
                RemoteConnection._get_proxy_url = bstack1l1ll111l_opy_
            else:
                from selenium.webdriver.remote.client_config import ClientConfig
                ClientConfig.get_proxy_url = bstack1l1ll111l_opy_
        except Exception as e:
            logger.error(bstack11lll1l11l_opy_.format(str(e)))
    if bstack111l11_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪ⏜") in str(framework_name).lower():
        if not bstack1l1l1ll11ll_opy_():
            return
        try:
            from pytest_selenium import pytest_selenium
            from _pytest.config import Config
            pytest_selenium.pytest_report_header = bstack11ll1lllll_opy_
            from pytest_selenium.drivers import browserstack
            browserstack.pytest_selenium_runtest_makereport = bstack11l1l1ll1_opy_
            Config.getoption = bstack1l1111l11_opy_
        except Exception as e:
            pass
        try:
            from pytest_bdd import reporting
            reporting.runtest_makereport = bstack11lllll1ll_opy_
        except Exception as e:
            pass
@measure(event_name=EVENTS.bstack1l1111ll1l_opy_, stage=STAGE.bstack111lllll1_opy_, bstack11l1l1lll1_opy_=bstack1ll1l111l_opy_)
def bstack1ll1l1l1_opy_(self):
    global bstack1l1llll11l_opy_
    global bstack1ll1lllll1_opy_
    global bstack11l11l1ll_opy_
    try:
        if bstack111l11_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫ⏝") in bstack1l1llll11l_opy_ and self.session_id != None and bstack1l11lllll1_opy_(threading.current_thread(), bstack111l11_opy_ (u"ࠬࡺࡥࡴࡶࡖࡸࡦࡺࡵࡴࠩ⏞"), bstack111l11_opy_ (u"࠭ࠧ⏟")) != bstack111l11_opy_ (u"ࠧࡴ࡭࡬ࡴࡵ࡫ࡤࠨ⏠"):
            bstack1l111lll_opy_ = bstack111l11_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨ⏡") if len(threading.current_thread().bstackTestErrorMessages) == 0 else bstack111l11_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ⏢")
            bstack1111lll1l_opy_(logger, True)
            if os.environ.get(bstack111l11_opy_ (u"ࠪࡔ࡞࡚ࡅࡔࡖࡢࡘࡊ࡙ࡔࡠࡐࡄࡑࡊ࠭⏣"), None):
                self.execute_script(
                    bstack111l11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡰࡤࡱࡪࠨ࠺ࠡࠩ⏤") + json.dumps(
                        os.environ.get(bstack111l11_opy_ (u"ࠬࡖ࡙ࡕࡇࡖࡘࡤ࡚ࡅࡔࡖࡢࡒࡆࡓࡅࠨ⏥"))) + bstack111l11_opy_ (u"࠭ࡽࡾࠩ⏦"))
            if self != None:
                bstack1l1l1l1l1l_opy_(self, bstack1l111lll_opy_, bstack111l11_opy_ (u"ࠧ࠭ࠢࠪ⏧").join(threading.current_thread().bstackTestErrorMessages))
        if not cli.bstack1lll111111l_opy_(bstack1lll111l1ll_opy_):
            item = store.get(bstack111l11_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡪࡶࡨࡱࠬ⏨"), None)
            if item is not None and bstack1l11lllll1_opy_(threading.current_thread(), bstack111l11_opy_ (u"ࠩࡤ࠵࠶ࡿࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ⏩"), None):
                bstack1ll1111l_opy_.bstack1l111l1l1l_opy_(self, bstack111ll1lll_opy_, logger, item)
        threading.current_thread().testStatus = bstack111l11_opy_ (u"ࠪࠫ⏪")
    except Exception as e:
        logger.debug(bstack111l11_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡻ࡭࡯࡬ࡦࠢࡰࡥࡷࡱࡩ࡯ࡩࠣࡷࡹࡧࡴࡶࡵ࠽ࠤࠧ⏫") + str(e))
    bstack11l11l1ll_opy_(self)
    self.session_id = None
@measure(event_name=EVENTS.bstack11ll1l1ll_opy_, stage=STAGE.bstack111lllll1_opy_, bstack11l1l1lll1_opy_=bstack1ll1l111l_opy_)
def bstack1ll111ll_opy_(self, command_executor,
             desired_capabilities=None, browser_profile=None, proxy=None,
             keep_alive=True, file_detector=None, options=None):
    global CONFIG
    global bstack1ll1lllll1_opy_
    global bstack1ll1l111l_opy_
    global bstack11ll111lll_opy_
    global bstack1l1llll11l_opy_
    global bstack11ll11111_opy_
    global bstack1lll1ll1l_opy_
    global bstack11l11ll1l1_opy_
    global bstack1l11lll111_opy_
    global bstack111ll1lll_opy_
    CONFIG[bstack111l11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡗࡉࡑࠧ⏬")] = str(bstack1l1llll11l_opy_) + str(__version__)
    command_executor = bstack11l1l1lll_opy_(bstack11l11ll1l1_opy_, CONFIG)
    logger.debug(bstack1ll1l1l1l1_opy_.format(command_executor))
    proxy = bstack1l1l1llll_opy_(CONFIG, proxy)
    bstack1l1ll1lll_opy_ = 0
    try:
        if bstack11ll111lll_opy_ is True:
            bstack1l1ll1lll_opy_ = int(os.environ.get(bstack111l11_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡊࡐࡇࡉ࡝࠭⏭")))
    except:
        bstack1l1ll1lll_opy_ = 0
    bstack1lllll1ll1_opy_ = bstack11l1l1l11_opy_(CONFIG, bstack1l1ll1lll_opy_)
    logger.debug(bstack11lll11l1l_opy_.format(str(bstack1lllll1ll1_opy_)))
    bstack111ll1lll_opy_ = CONFIG.get(bstack111l11_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪ⏮"))[bstack1l1ll1lll_opy_]
    if bstack111l11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬ⏯") in CONFIG and CONFIG[bstack111l11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡍࡱࡦࡥࡱ࠭⏰")]:
        bstack1111111l_opy_(bstack1lllll1ll1_opy_, bstack1l11lll111_opy_)
    if bstack1l1l111l1l_opy_.bstack1l1l11111l_opy_(CONFIG, bstack1l1ll1lll_opy_) and bstack1l1l111l1l_opy_.bstack1llll1l1_opy_(bstack1lllll1ll1_opy_, options, desired_capabilities):
        threading.current_thread().a11yPlatform = True
        if not cli.bstack1lll111111l_opy_(bstack1lll111l1ll_opy_):
            bstack1l1l111l1l_opy_.set_capabilities(bstack1lllll1ll1_opy_, CONFIG)
    if desired_capabilities:
        bstack1l11lllll_opy_ = bstack1l1ll1l1ll_opy_(desired_capabilities)
        bstack1l11lllll_opy_[bstack111l11_opy_ (u"ࠪࡹࡸ࡫ࡗ࠴ࡅࠪ⏱")] = bstack1l111l111_opy_(CONFIG)
        bstack1l11ll11ll_opy_ = bstack11l1l1l11_opy_(bstack1l11lllll_opy_)
        if bstack1l11ll11ll_opy_:
            bstack1lllll1ll1_opy_ = update(bstack1l11ll11ll_opy_, bstack1lllll1ll1_opy_)
        desired_capabilities = None
    if options:
        bstack1ll1l111_opy_(options, bstack1lllll1ll1_opy_)
    if not options:
        options = bstack1ll1lllll_opy_(bstack1lllll1ll1_opy_)
    if proxy and bstack1l11111ll1_opy_() >= version.parse(bstack111l11_opy_ (u"ࠫ࠹࠴࠱࠱࠰࠳ࠫ⏲")):
        options.proxy(proxy)
    if options and bstack1l11111ll1_opy_() >= version.parse(bstack111l11_opy_ (u"ࠬ࠹࠮࠹࠰࠳ࠫ⏳")):
        desired_capabilities = None
    if (
            not options and not desired_capabilities
    ) or (
            bstack1l11111ll1_opy_() < version.parse(bstack111l11_opy_ (u"࠭࠳࠯࠺࠱࠴ࠬ⏴")) and not desired_capabilities
    ):
        desired_capabilities = {}
        desired_capabilities.update(bstack1lllll1ll1_opy_)
    logger.info(bstack1l1111111_opy_)
    bstack1l1l1l1111_opy_.end(EVENTS.bstack11lll11l1_opy_.value, EVENTS.bstack11lll11l1_opy_.value + bstack111l11_opy_ (u"ࠢ࠻ࡵࡷࡥࡷࡺࠢ⏵"),
                               EVENTS.bstack11lll11l1_opy_.value + bstack111l11_opy_ (u"ࠣ࠼ࡨࡲࡩࠨ⏶"), True, None)
    try:
        if bstack1l11111ll1_opy_() >= version.parse(bstack111l11_opy_ (u"ࠩ࠷࠲࠶࠶࠮࠱ࠩ⏷")):
            bstack11ll11111_opy_(self, command_executor=command_executor,
                      options=options, keep_alive=keep_alive, file_detector=file_detector, *args, **kwargs)
        elif bstack1l11111ll1_opy_() >= version.parse(bstack111l11_opy_ (u"ࠪ࠷࠳࠾࠮࠱ࠩ⏸")):
            bstack11ll11111_opy_(self, command_executor=command_executor,
                      desired_capabilities=desired_capabilities, options=options,
                      browser_profile=browser_profile, proxy=proxy,
                      keep_alive=keep_alive, file_detector=file_detector)
        elif bstack1l11111ll1_opy_() >= version.parse(bstack111l11_opy_ (u"ࠫ࠷࠴࠵࠴࠰࠳ࠫ⏹")):
            bstack11ll11111_opy_(self, command_executor=command_executor,
                      desired_capabilities=desired_capabilities,
                      browser_profile=browser_profile, proxy=proxy,
                      keep_alive=keep_alive, file_detector=file_detector)
        else:
            bstack11ll11111_opy_(self, command_executor=command_executor,
                      desired_capabilities=desired_capabilities,
                      browser_profile=browser_profile, proxy=proxy,
                      keep_alive=keep_alive)
    except Exception as bstack1l11llll_opy_:
        logger.error(bstack1lll11ll1l_opy_.format(bstack111l11_opy_ (u"ࠬࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠫ⏺"), str(bstack1l11llll_opy_)))
        raise bstack1l11llll_opy_
    try:
        bstack1ll11l1l1_opy_ = bstack111l11_opy_ (u"࠭ࠧ⏻")
        if bstack1l11111ll1_opy_() >= version.parse(bstack111l11_opy_ (u"ࠧ࠵࠰࠳࠲࠵ࡨ࠱ࠨ⏼")):
            bstack1ll11l1l1_opy_ = self.caps.get(bstack111l11_opy_ (u"ࠣࡱࡳࡸ࡮ࡳࡡ࡭ࡊࡸࡦ࡚ࡸ࡬ࠣ⏽"))
        else:
            bstack1ll11l1l1_opy_ = self.capabilities.get(bstack111l11_opy_ (u"ࠤࡲࡴࡹ࡯࡭ࡢ࡮ࡋࡹࡧ࡛ࡲ࡭ࠤ⏾"))
        if bstack1ll11l1l1_opy_:
            bstack1ll1l1ll1_opy_(bstack1ll11l1l1_opy_)
            if bstack1l11111ll1_opy_() <= version.parse(bstack111l11_opy_ (u"ࠪ࠷࠳࠷࠳࠯࠲ࠪ⏿")):
                self.command_executor._url = bstack111l11_opy_ (u"ࠦ࡭ࡺࡴࡱ࠼࠲࠳ࠧ␀") + bstack11l11ll1l1_opy_ + bstack111l11_opy_ (u"ࠧࡀ࠸࠱࠱ࡺࡨ࠴࡮ࡵࡣࠤ␁")
            else:
                self.command_executor._url = bstack111l11_opy_ (u"ࠨࡨࡵࡶࡳࡷ࠿࠵࠯ࠣ␂") + bstack1ll11l1l1_opy_ + bstack111l11_opy_ (u"ࠢ࠰ࡹࡧ࠳࡭ࡻࡢࠣ␃")
            logger.debug(bstack11lllllll1_opy_.format(bstack1ll11l1l1_opy_))
        else:
            logger.debug(bstack11111l11l_opy_.format(bstack111l11_opy_ (u"ࠣࡑࡳࡸ࡮ࡳࡡ࡭ࠢࡋࡹࡧࠦ࡮ࡰࡶࠣࡪࡴࡻ࡮ࡥࠤ␄")))
    except Exception as e:
        logger.debug(bstack11111l11l_opy_.format(e))
    bstack1ll1lllll1_opy_ = self.session_id
    if bstack111l11_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩ␅") in bstack1l1llll11l_opy_:
        threading.current_thread().bstackSessionId = self.session_id
        threading.current_thread().bstackSessionDriver = self
        threading.current_thread().bstackTestErrorMessages = []
        item = store.get(bstack111l11_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡹ࡫ࡳࡵࡡ࡬ࡸࡪࡳࠧ␆"), None)
        if item:
            bstack1lll1lll11ll_opy_ = getattr(item, bstack111l11_opy_ (u"ࠫࡤࡺࡥࡴࡶࡢࡧࡦࡹࡥࡠࡵࡷࡥࡷࡺࡥࡥࠩ␇"), False)
            if not getattr(item, bstack111l11_opy_ (u"ࠬࡥࡤࡳ࡫ࡹࡩࡷ࠭␈"), None) and bstack1lll1lll11ll_opy_:
                setattr(store[bstack111l11_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤ࡯ࡴࡦ࡯ࠪ␉")], bstack111l11_opy_ (u"ࠧࡠࡦࡵ࡭ࡻ࡫ࡲࠨ␊"), self)
        bstack1ll111l11_opy_ = getattr(threading.current_thread(), bstack111l11_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡕࡧࡶࡸࡒ࡫ࡴࡢࠩ␋"), None)
        if bstack1ll111l11_opy_ and bstack1ll111l11_opy_.get(bstack111l11_opy_ (u"ࠩࡶࡸࡦࡺࡵࡴࠩ␌"), bstack111l11_opy_ (u"ࠪࠫ␍")) == bstack111l11_opy_ (u"ࠫࡵ࡫࡮ࡥ࡫ࡱ࡫ࠬ␎"):
            bstack111l1ll1_opy_.bstack1ll111l1ll_opy_(self)
    bstack1lll1ll1l_opy_.append(self)
    if bstack111l11_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ␏") in CONFIG and bstack111l11_opy_ (u"࠭ࡳࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫ␐") in CONFIG[bstack111l11_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪ␑")][bstack1l1ll1lll_opy_]:
        bstack1ll1l111l_opy_ = CONFIG[bstack111l11_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ␒")][bstack1l1ll1lll_opy_][bstack111l11_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧ␓")]
    logger.debug(bstack111l1l1ll_opy_.format(bstack1ll1lllll1_opy_))
@measure(event_name=EVENTS.bstack11lll111l_opy_, stage=STAGE.bstack111lllll1_opy_, bstack11l1l1lll1_opy_=bstack1ll1l111l_opy_)
def bstack1l11l1111l_opy_(self, url):
    global bstack1l1lll111l_opy_
    global CONFIG
    try:
        bstack11l1l1l1ll_opy_(url, CONFIG, logger)
    except Exception as err:
        logger.debug(bstack1l11lll11l_opy_.format(str(err)))
    try:
        bstack1l1lll111l_opy_(self, url)
    except Exception as e:
        try:
            bstack1llll11l_opy_ = str(e)
            if any(err_msg in bstack1llll11l_opy_ for err_msg in bstack11ll11l1l1_opy_):
                bstack11l1l1l1ll_opy_(url, CONFIG, logger, True)
        except Exception as err:
            logger.debug(bstack1l11lll11l_opy_.format(str(err)))
        raise e
def bstack11l11l1ll1_opy_(item, when):
    global bstack111lll1l_opy_
    try:
        bstack111lll1l_opy_(item, when)
    except Exception as e:
        pass
def bstack11lllll1ll_opy_(item, call, rep):
    global bstack11llll1ll1_opy_
    global bstack1lll1ll1l_opy_
    name = bstack111l11_opy_ (u"ࠪࠫ␔")
    try:
        if rep.when == bstack111l11_opy_ (u"ࠫࡨࡧ࡬࡭ࠩ␕"):
            bstack1ll1lllll1_opy_ = threading.current_thread().bstackSessionId
            skipSessionName = item.config.getoption(bstack111l11_opy_ (u"ࠬࡹ࡫ࡪࡲࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧ␖"))
            try:
                if (str(skipSessionName).lower() != bstack111l11_opy_ (u"࠭ࡴࡳࡷࡨࠫ␗")):
                    name = str(rep.nodeid)
                    bstack1lllll111l_opy_ = bstack11llllll_opy_(bstack111l11_opy_ (u"ࠧࡴࡧࡷࡗࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨ␘"), name, bstack111l11_opy_ (u"ࠨࠩ␙"), bstack111l11_opy_ (u"ࠩࠪ␚"), bstack111l11_opy_ (u"ࠪࠫ␛"), bstack111l11_opy_ (u"ࠫࠬ␜"))
                    os.environ[bstack111l11_opy_ (u"ࠬࡖ࡙ࡕࡇࡖࡘࡤ࡚ࡅࡔࡖࡢࡒࡆࡓࡅࠨ␝")] = name
                    for driver in bstack1lll1ll1l_opy_:
                        if bstack1ll1lllll1_opy_ == driver.session_id:
                            driver.execute_script(bstack1lllll111l_opy_)
            except Exception as e:
                logger.debug(bstack111l11_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡵࡨࡸࡹ࡯࡮ࡨࠢࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠠࡧࡱࡵࠤࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠡࡵࡨࡷࡸ࡯࡯࡯࠼ࠣࡿࢂ࠭␞").format(str(e)))
            try:
                bstack11111111l_opy_(rep.outcome.lower())
                if rep.outcome.lower() != bstack111l11_opy_ (u"ࠧࡴ࡭࡬ࡴࡵ࡫ࡤࠨ␟"):
                    status = bstack111l11_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨ␠") if rep.outcome.lower() == bstack111l11_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ␡") else bstack111l11_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪ␢")
                    reason = bstack111l11_opy_ (u"ࠫࠬ␣")
                    if status == bstack111l11_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ␤"):
                        reason = rep.longrepr.reprcrash.message
                        if (not threading.current_thread().bstackTestErrorMessages):
                            threading.current_thread().bstackTestErrorMessages = []
                        threading.current_thread().bstackTestErrorMessages.append(reason)
                    level = bstack111l11_opy_ (u"࠭ࡩ࡯ࡨࡲࠫ␥") if status == bstack111l11_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧ␦") else bstack111l11_opy_ (u"ࠨࡧࡵࡶࡴࡸࠧ␧")
                    data = name + bstack111l11_opy_ (u"ࠩࠣࡴࡦࡹࡳࡦࡦࠤࠫ␨") if status == bstack111l11_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪ␩") else name + bstack111l11_opy_ (u"ࠫࠥ࡬ࡡࡪ࡮ࡨࡨࠦࠦࠧ␪") + reason
                    bstack11ll1l111l_opy_ = bstack11llllll_opy_(bstack111l11_opy_ (u"ࠬࡧ࡮࡯ࡱࡷࡥࡹ࡫ࠧ␫"), bstack111l11_opy_ (u"࠭ࠧ␬"), bstack111l11_opy_ (u"ࠧࠨ␭"), bstack111l11_opy_ (u"ࠨࠩ␮"), level, data)
                    for driver in bstack1lll1ll1l_opy_:
                        if bstack1ll1lllll1_opy_ == driver.session_id:
                            driver.execute_script(bstack11ll1l111l_opy_)
            except Exception as e:
                logger.debug(bstack111l11_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡸ࡫ࡴࡵ࡫ࡱ࡫ࠥࡹࡥࡴࡵ࡬ࡳࡳࠦࡣࡰࡰࡷࡩࡽࡺࠠࡧࡱࡵࠤࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠡࡵࡨࡷࡸ࡯࡯࡯࠼ࠣࡿࢂ࠭␯").format(str(e)))
    except Exception as e:
        logger.debug(bstack111l11_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥ࡭ࡥࡵࡶ࡬ࡲ࡬ࠦࡳࡵࡣࡷࡩࠥ࡯࡮ࠡࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠥࡺࡥࡴࡶࠣࡷࡹࡧࡴࡶࡵ࠽ࠤࢀࢃࠧ␰").format(str(e)))
    bstack11llll1ll1_opy_(item, call, rep)
notset = Notset()
def bstack1l1111l11_opy_(self, name: str, default=notset, skip: bool = False):
    global bstack1l1111l1_opy_
    if str(name).lower() == bstack111l11_opy_ (u"ࠫࡩࡸࡩࡷࡧࡵࠫ␱"):
        return bstack111l11_opy_ (u"ࠧࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠦ␲")
    else:
        return bstack1l1111l1_opy_(self, name, default, skip)
def bstack1l1ll111l_opy_(self):
    global CONFIG
    global bstack11lll1lll_opy_
    try:
        proxy = bstack1l11l11l_opy_(CONFIG)
        if proxy:
            if proxy.endswith(bstack111l11_opy_ (u"࠭࠮ࡱࡣࡦࠫ␳")):
                proxies = bstack111ll11l1_opy_(proxy, bstack11l1l1lll_opy_())
                if len(proxies) > 0:
                    protocol, bstack1ll11l111_opy_ = proxies.popitem()
                    if bstack111l11_opy_ (u"ࠢ࠻࠱࠲ࠦ␴") in bstack1ll11l111_opy_:
                        return bstack1ll11l111_opy_
                    else:
                        return bstack111l11_opy_ (u"ࠣࡪࡷࡸࡵࡀ࠯࠰ࠤ␵") + bstack1ll11l111_opy_
            else:
                return proxy
    except Exception as e:
        logger.error(bstack111l11_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡸ࡫ࡴࡵ࡫ࡱ࡫ࠥࡶࡲࡰࡺࡼࠤࡺࡸ࡬ࠡ࠼ࠣࡿࢂࠨ␶").format(str(e)))
    return bstack11lll1lll_opy_(self)
def bstack1l1l1lll_opy_():
    return (bstack111l11_opy_ (u"ࠪ࡬ࡹࡺࡰࡑࡴࡲࡼࡾ࠭␷") in CONFIG or bstack111l11_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨ␸") in CONFIG) and bstack11llll1111_opy_() and bstack1l11111ll1_opy_() >= version.parse(
        bstack11l1lllll1_opy_)
def bstack111l1111l_opy_(self,
               executablePath=None,
               channel=None,
               args=None,
               ignoreDefaultArgs=None,
               handleSIGINT=None,
               handleSIGTERM=None,
               handleSIGHUP=None,
               timeout=None,
               env=None,
               headless=None,
               devtools=None,
               proxy=None,
               downloadsPath=None,
               slowMo=None,
               tracesDir=None,
               chromiumSandbox=None,
               firefoxUserPrefs=None
               ):
    global CONFIG
    global bstack1ll1l111l_opy_
    global bstack11ll111lll_opy_
    global bstack1l1llll11l_opy_
    CONFIG[bstack111l11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡗࡉࡑࠧ␹")] = str(bstack1l1llll11l_opy_) + str(__version__)
    bstack1l1ll1lll_opy_ = 0
    try:
        if bstack11ll111lll_opy_ is True:
            bstack1l1ll1lll_opy_ = int(os.environ.get(bstack111l11_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡊࡐࡇࡉ࡝࠭␺")))
    except:
        bstack1l1ll1lll_opy_ = 0
    CONFIG[bstack111l11_opy_ (u"ࠢࡪࡵࡓࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠨ␻")] = True
    bstack1lllll1ll1_opy_ = bstack11l1l1l11_opy_(CONFIG, bstack1l1ll1lll_opy_)
    logger.debug(bstack11lll11l1l_opy_.format(str(bstack1lllll1ll1_opy_)))
    if CONFIG.get(bstack111l11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬ␼")):
        bstack1111111l_opy_(bstack1lllll1ll1_opy_, bstack1l11lll111_opy_)
    if bstack111l11_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ␽") in CONFIG and bstack111l11_opy_ (u"ࠪࡷࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨ␾") in CONFIG[bstack111l11_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ␿")][bstack1l1ll1lll_opy_]:
        bstack1ll1l111l_opy_ = CONFIG[bstack111l11_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ⑀")][bstack1l1ll1lll_opy_][bstack111l11_opy_ (u"࠭ࡳࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫ⑁")]
    import urllib
    import json
    if bstack111l11_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫ⑂") in CONFIG and str(CONFIG[bstack111l11_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬ⑃")]).lower() != bstack111l11_opy_ (u"ࠩࡩࡥࡱࡹࡥࠨ⑄"):
        bstack1ll11ll11_opy_ = bstack1l1ll1l111_opy_()
        bstack1111lllll_opy_ = bstack1ll11ll11_opy_ + urllib.parse.quote(json.dumps(bstack1lllll1ll1_opy_))
    else:
        bstack1111lllll_opy_ = bstack111l11_opy_ (u"ࠪࡻࡸࡹ࠺࠰࠱ࡦࡨࡵ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࡅࡣࡢࡲࡶࡁࠬ⑅") + urllib.parse.quote(json.dumps(bstack1lllll1ll1_opy_))
    browser = self.connect(bstack1111lllll_opy_)
    return browser
def bstack11llll111_opy_():
    global bstack1ll1l1111l_opy_
    global bstack1l1llll11l_opy_
    try:
        from playwright._impl._browser_type import BrowserType
        from bstack_utils.helper import bstack11ll1l1ll1_opy_
        if not bstack1l1l1ll11ll_opy_():
            global bstack1lll1111ll_opy_
            if not bstack1lll1111ll_opy_:
                from bstack_utils.helper import bstack111l11l1_opy_, bstack11l1ll11l1_opy_
                bstack1lll1111ll_opy_ = bstack111l11l1_opy_()
                bstack11l1ll11l1_opy_(bstack1l1llll11l_opy_)
            BrowserType.connect = bstack11ll1l1ll1_opy_
            return
        BrowserType.launch = bstack111l1111l_opy_
        bstack1ll1l1111l_opy_ = True
    except Exception as e:
        pass
def bstack1lll1ll1lll1_opy_():
    global CONFIG
    global bstack1ll11ll1_opy_
    global bstack11l11ll1l1_opy_
    global bstack1l11lll111_opy_
    global bstack11ll111lll_opy_
    global bstack11ll1l1l_opy_
    CONFIG = json.loads(os.environ.get(bstack111l11_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡔࡔࡆࡊࡉࠪ⑆")))
    bstack1ll11ll1_opy_ = eval(os.environ.get(bstack111l11_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡎ࡙࡟ࡂࡒࡓࡣࡆ࡛ࡔࡐࡏࡄࡘࡊ࠭⑇")))
    bstack11l11ll1l1_opy_ = os.environ.get(bstack111l11_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡎࡕࡃࡡࡘࡖࡑ࠭⑈"))
    bstack1lll1lll1l_opy_(CONFIG, bstack1ll11ll1_opy_)
    bstack11ll1l1l_opy_ = bstack11l1l1111_opy_.configure_logger(CONFIG, bstack11ll1l1l_opy_)
    if cli.bstack111lllll1l_opy_():
        bstack1lll11l1_opy_.invoke(bstack1l111l1l11_opy_.CONNECT, bstack11l11ll111_opy_())
        cli_context.platform_index = int(os.environ.get(bstack111l11_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡍࡃࡗࡊࡔࡘࡍࡠࡋࡑࡈࡊ࡞ࠧ⑉"), bstack111l11_opy_ (u"ࠨ࠲ࠪ⑊")))
        cli.bstack1ll1l1l1l1l_opy_(cli_context.platform_index)
        cli.bstack1ll1l1ll11l_opy_(bstack11l1l1lll_opy_(bstack11l11ll1l1_opy_, CONFIG), cli_context.platform_index, bstack1ll1lllll_opy_)
        cli.bstack1llll111ll1_opy_()
        logger.debug(bstack111l11_opy_ (u"ࠤࡆࡐࡎࠦࡩࡴࠢࡤࡧࡹ࡯ࡶࡦࠢࡩࡳࡷࠦࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡠ࡫ࡱࡨࡪࡾ࠽ࠣ⑋") + str(cli_context.platform_index) + bstack111l11_opy_ (u"ࠥࠦ⑌"))
        return # skip all existing operations
    global bstack11ll11111_opy_
    global bstack11l11l1ll_opy_
    global bstack1ll11l1111_opy_
    global bstack11llll1l_opy_
    global bstack11l11111ll_opy_
    global bstack1l1llll1_opy_
    global bstack1lll11llll_opy_
    global bstack1l1lll111l_opy_
    global bstack11lll1lll_opy_
    global bstack1l1111l1_opy_
    global bstack111lll1l_opy_
    global bstack11llll1ll1_opy_
    try:
        from selenium import webdriver
        from selenium.webdriver.remote.webdriver import WebDriver
        bstack11ll11111_opy_ = webdriver.Remote.__init__
        bstack11l11l1ll_opy_ = WebDriver.quit
        bstack1lll11llll_opy_ = WebDriver.close
        bstack1l1lll111l_opy_ = WebDriver.get
    except Exception as e:
        pass
    if (bstack111l11_opy_ (u"ࠫ࡭ࡺࡴࡱࡒࡵࡳࡽࡿࠧ⑍") in CONFIG or bstack111l11_opy_ (u"ࠬ࡮ࡴࡵࡲࡶࡔࡷࡵࡸࡺࠩ⑎") in CONFIG) and bstack11llll1111_opy_():
        if bstack1l11111ll1_opy_() < version.parse(bstack11l1lllll1_opy_):
            logger.error(bstack111llll11l_opy_.format(bstack1l11111ll1_opy_()))
        else:
            try:
                from selenium.webdriver.remote.remote_connection import RemoteConnection
                if hasattr(RemoteConnection, bstack111l11_opy_ (u"࠭࡟ࡨࡧࡷࡣࡵࡸ࡯ࡹࡻࡢࡹࡷࡲࠧ⑏")) and callable(getattr(RemoteConnection, bstack111l11_opy_ (u"ࠧࡠࡩࡨࡸࡤࡶࡲࡰࡺࡼࡣࡺࡸ࡬ࠨ⑐"))):
                    bstack11lll1lll_opy_ = RemoteConnection._get_proxy_url
                else:
                    from selenium.webdriver.remote.client_config import ClientConfig
                    bstack11lll1lll_opy_ = ClientConfig.get_proxy_url
            except Exception as e:
                logger.error(bstack11lll1l11l_opy_.format(str(e)))
    try:
        from _pytest.config import Config
        bstack1l1111l1_opy_ = Config.getoption
        from _pytest import runner
        bstack111lll1l_opy_ = runner._update_current_test_var
    except Exception as e:
        logger.warn(e, bstack1ll11111l1_opy_)
    try:
        from pytest_bdd import reporting
        bstack11llll1ll1_opy_ = reporting.runtest_makereport
    except Exception as e:
        logger.debug(bstack111l11_opy_ (u"ࠨࡒ࡯ࡩࡦࡹࡥࠡ࡫ࡱࡷࡹࡧ࡬࡭ࠢࡳࡽࡹ࡫ࡳࡵ࠯ࡥࡨࡩࠦࡴࡰࠢࡵࡹࡳࠦࡰࡺࡶࡨࡷࡹ࠳ࡢࡥࡦࠣࡸࡪࡹࡴࡴࠩ⑑"))
    bstack1l11lll111_opy_ = CONFIG.get(bstack111l11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭⑒"), {}).get(bstack111l11_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ⑓"))
    bstack11ll111lll_opy_ = True
    bstack1l11111l_opy_(bstack11lll1l1_opy_)
if (bstack111lll1l11l_opy_()):
    bstack1lll1ll1lll1_opy_()
@error_handler(class_method=False)
def bstack1llll1111l1l_opy_(hook_name, event, bstack1l111ll11ll_opy_=None):
    if hook_name not in [bstack111l11_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࡢࡪࡺࡴࡣࡵ࡫ࡲࡲࠬ⑔"), bstack111l11_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴ࡟ࡧࡷࡱࡧࡹ࡯࡯࡯ࠩ⑕"), bstack111l11_opy_ (u"࠭ࡳࡦࡶࡸࡴࡤࡳ࡯ࡥࡷ࡯ࡩࠬ⑖"), bstack111l11_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡰࡳࡩࡻ࡬ࡦࠩ⑗"), bstack111l11_opy_ (u"ࠨࡵࡨࡸࡺࡶ࡟ࡤ࡮ࡤࡷࡸ࠭⑘"), bstack111l11_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱࡣࡨࡲࡡࡴࡵࠪ⑙"), bstack111l11_opy_ (u"ࠪࡷࡪࡺࡵࡱࡡࡰࡩࡹ࡮࡯ࡥࠩ⑚"), bstack111l11_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳࡥ࡭ࡦࡶ࡫ࡳࡩ࠭⑛")]:
        return
    node = store[bstack111l11_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣ࡮ࡺࡥ࡮ࠩ⑜")]
    if hook_name in [bstack111l11_opy_ (u"࠭ࡳࡦࡶࡸࡴࡤࡳ࡯ࡥࡷ࡯ࡩࠬ⑝"), bstack111l11_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡰࡳࡩࡻ࡬ࡦࠩ⑞")]:
        node = store[bstack111l11_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡰࡳࡩࡻ࡬ࡦࡡ࡬ࡸࡪࡳࠧ⑟")]
    elif hook_name in [bstack111l11_opy_ (u"ࠩࡶࡩࡹࡻࡰࡠࡥ࡯ࡥࡸࡹࠧ①"), bstack111l11_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࡤࡩ࡬ࡢࡵࡶࠫ②")]:
        node = store[bstack111l11_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡩ࡬ࡢࡵࡶࡣ࡮ࡺࡥ࡮ࠩ③")]
    hook_type = bstack1llllllll11l_opy_(hook_name)
    if event == bstack111l11_opy_ (u"ࠬࡨࡥࡧࡱࡵࡩࠬ④"):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1lll11ll111_opy_[hook_type], bstack1lll1lll111_opy_.PRE, node, hook_name)
            return
        uuid = uuid4().__str__()
        bstack1111ll1111_opy_ = {
            bstack111l11_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ⑤"): uuid,
            bstack111l11_opy_ (u"ࠧࡴࡶࡤࡶࡹ࡫ࡤࡠࡣࡷࠫ⑥"): bstack11ll11lll_opy_(),
            bstack111l11_opy_ (u"ࠨࡶࡼࡴࡪ࠭⑦"): bstack111l11_opy_ (u"ࠩ࡫ࡳࡴࡱࠧ⑧"),
            bstack111l11_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡶࡼࡴࡪ࠭⑨"): hook_type,
            bstack111l11_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡱࡥࡲ࡫ࠧ⑩"): hook_name
        }
        store[bstack111l11_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡨࡰࡱ࡮ࡣࡺࡻࡩࡥࠩ⑪")].append(uuid)
        bstack1llll11111ll_opy_ = node.nodeid
        if hook_type == bstack111l11_opy_ (u"࠭ࡂࡆࡈࡒࡖࡊࡥࡅࡂࡅࡋࠫ⑫"):
            if not _1111l1llll_opy_.get(bstack1llll11111ll_opy_, None):
                _1111l1llll_opy_[bstack1llll11111ll_opy_] = {bstack111l11_opy_ (u"ࠧࡩࡱࡲ࡯ࡸ࠭⑬"): []}
            _1111l1llll_opy_[bstack1llll11111ll_opy_][bstack111l11_opy_ (u"ࠨࡪࡲࡳࡰࡹࠧ⑭")].append(bstack1111ll1111_opy_[bstack111l11_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ⑮")])
        _1111l1llll_opy_[bstack1llll11111ll_opy_ + bstack111l11_opy_ (u"ࠪ࠱ࠬ⑯") + hook_name] = bstack1111ll1111_opy_
        bstack1lll1llll1l1_opy_(node, bstack1111ll1111_opy_, bstack111l11_opy_ (u"ࠫࡍࡵ࡯࡬ࡔࡸࡲࡘࡺࡡࡳࡶࡨࡨࠬ⑰"))
    elif event == bstack111l11_opy_ (u"ࠬࡧࡦࡵࡧࡵࠫ⑱"):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1lll11ll111_opy_[hook_type], bstack1lll1lll111_opy_.POST, node, None, bstack1l111ll11ll_opy_)
            return
        bstack111lll11ll_opy_ = node.nodeid + bstack111l11_opy_ (u"࠭࠭ࠨ⑲") + hook_name
        _1111l1llll_opy_[bstack111lll11ll_opy_][bstack111l11_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬ⑳")] = bstack11ll11lll_opy_()
        bstack1lll1ll11ll1_opy_(_1111l1llll_opy_[bstack111lll11ll_opy_][bstack111l11_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭⑴")])
        bstack1lll1llll1l1_opy_(node, _1111l1llll_opy_[bstack111lll11ll_opy_], bstack111l11_opy_ (u"ࠩࡋࡳࡴࡱࡒࡶࡰࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫ⑵"), bstack1llll1111l11_opy_=bstack1l111ll11ll_opy_)
def bstack1lll1lllll1l_opy_():
    global bstack1lll1lll111l_opy_
    if bstack11l11l111_opy_():
        bstack1lll1lll111l_opy_ = bstack111l11_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶ࠰ࡦࡩࡪࠧ⑶")
    else:
        bstack1lll1lll111l_opy_ = bstack111l11_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫ⑷")
def pytest_collection_modifyitems(session, config, items):
    bstack111l11_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࡌࡩ࡭ࡶࡨࡶࡸࠦࡣࡰ࡮࡯ࡩࡨࡺࡥࡥࠢࡳࡽࡹ࡫ࡳࡵࠢ࡬ࡸࡪࡳࡳࠡࡤࡤࡷࡪࡪࠠࡰࡰࠣࡳࡷࡩࡨࡦࡵࡷࡶࡦࡺࡥࡥࠢࡶࡩࡱ࡫ࡣࡵࡱࡵࡷࠥ࡬ࡲࡰ࡯ࠣࡳࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࠣࡷࡪࡸࡶࡦࡴ࠱ࠎࠥࠦࠠࠡࠤࠥࠦ⑸")
    import os
    bstack1lll1lll1lll_opy_ = os.environ.get(bstack111l11_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡕࡒࡄࡊࡈࡗ࡙ࡘࡁࡕࡇࡇࡣࡘࡋࡌࡆࡅࡗࡓࡗ࡙ࠧ⑹"))
    if not bstack1lll1lll1lll_opy_:
        return
    try:
        bstack1lll1llll1ll_opy_ = json.loads(bstack1lll1lll1lll_opy_)
        if not isinstance(bstack1lll1llll1ll_opy_, (list, set)) or not bstack1lll1llll1ll_opy_:
            return
    except Exception as e:
        logger.debug(bstack111l11_opy_ (u"ࠢࡄࡱࡸࡰࡩࠦ࡮ࡰࡶࠣࡴࡦࡸࡳࡦࠢࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡑࡕࡇࡍࡋࡓࡕࡔࡄࡘࡊࡊ࡟ࡔࡇࡏࡉࡈ࡚ࡏࡓࡕ࠽ࠤࠧ⑺") + str(e) + bstack111l11_opy_ (u"ࠣࠤ⑻"))
        return
    selected = []
    deselected = []
    bstack1llll11111l1_opy_ = set()
    for selector in bstack1lll1llll1ll_opy_:
        if not selector or not isinstance(selector, str):
            continue
        bstack1llll11111l1_opy_.add(selector)
    for item in items:
        nodeid = getattr(item, bstack111l11_opy_ (u"ࠩࡱࡳࡩ࡫ࡩࡥࠩ⑼"), None)
        if not nodeid:
            deselected.append(item)
            continue
        if (
            nodeid in bstack1llll11111l1_opy_ or
            any(sel in nodeid for sel in bstack1llll11111l1_opy_)
        ):
            selected.append(item)
        else:
            deselected.append(item)
    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = selected
@bstack111l1ll1_opy_.bstack1llll1ll11l1_opy_
def bstack1lll1lll1l1l_opy_():
    bstack1lll1lllll1l_opy_()
    if cli.is_running():
        try:
            bstack111ll11111l_opy_(bstack1llll1111l1l_opy_)
        except Exception as e:
            logger.debug(bstack111l11_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢ࡫ࡳࡴࡱࡳࠡࡲࡤࡸࡨ࡮࠺ࠡࡽࢀࠦ⑽").format(e))
        return
    if bstack11llll1111_opy_():
        bstack1llll1111_opy_ = Config.bstack1lll111l11_opy_()
        bstack111l11_opy_ (u"ࠫࠬ࠭ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡌ࡯ࡳࠢࡳࡴࡵࠦ࠽ࠡ࠳࠯ࠤࡲࡵࡤࡠࡧࡻࡩࡨࡻࡴࡦࠢࡪࡩࡹࡹࠠࡶࡵࡨࡨࠥ࡬࡯ࡳࠢࡤ࠵࠶ࡿࠠࡤࡱࡰࡱࡦࡴࡤࡴ࠯ࡺࡶࡦࡶࡰࡪࡰࡪࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡉࡳࡷࠦࡰࡱࡲࠣࡂࠥ࠷ࠬࠡ࡯ࡲࡨࡤ࡫ࡸࡦࡥࡸࡸࡪࠦࡤࡰࡧࡶࠤࡳࡵࡴࠡࡴࡸࡲࠥࡨࡥࡤࡣࡸࡷࡪࠦࡩࡵࠢ࡬ࡷࠥࡶࡡࡵࡥ࡫ࡩࡩࠦࡩ࡯ࠢࡤࠤࡩ࡯ࡦࡧࡧࡵࡩࡳࡺࠠࡱࡴࡲࡧࡪࡹࡳࠡ࡫ࡧࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡗ࡬ࡺࡹࠠࡸࡧࠣࡲࡪ࡫ࡤࠡࡶࡲࠤࡺࡹࡥࠡࡕࡨࡰࡪࡴࡩࡶ࡯ࡓࡥࡹࡩࡨࠩࡵࡨࡰࡪࡴࡩࡶ࡯ࡢ࡬ࡦࡴࡤ࡭ࡧࡵ࠭ࠥ࡬࡯ࡳࠢࡳࡴࡵࠦ࠾ࠡ࠳ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠬ࠭ࠧ⑾")
        if bstack1llll1111_opy_.get_property(bstack111l11_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡤࡳ࡯ࡥࡡࡦࡥࡱࡲࡥࡥࠩ⑿")):
            if CONFIG.get(bstack111l11_opy_ (u"࠭ࡰࡢࡴࡤࡰࡱ࡫࡬ࡴࡒࡨࡶࡕࡲࡡࡵࡨࡲࡶࡲ࠭⒀")) is not None and int(CONFIG[bstack111l11_opy_ (u"ࠧࡱࡣࡵࡥࡱࡲࡥ࡭ࡵࡓࡩࡷࡖ࡬ࡢࡶࡩࡳࡷࡳࠧ⒁")]) > 1:
                bstack11l111ll1_opy_(bstack1lll11ll_opy_)
            return
        bstack11l111ll1_opy_(bstack1lll11ll_opy_)
    try:
        bstack111ll11111l_opy_(bstack1llll1111l1l_opy_)
    except Exception as e:
        logger.debug(bstack111l11_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡩࡱࡲ࡯ࡸࠦࡰࡢࡶࡦ࡬࠿ࠦࡻࡾࠤ⒂").format(e))
bstack1lll1lll1l1l_opy_()