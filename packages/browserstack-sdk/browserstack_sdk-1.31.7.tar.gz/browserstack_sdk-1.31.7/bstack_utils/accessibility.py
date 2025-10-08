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
import requests
import logging
import threading
import bstack_utils.constants as bstack11ll1l1llll_opy_
from urllib.parse import urlparse
from bstack_utils.constants import bstack11ll1l111ll_opy_ as bstack11ll1l1ll11_opy_, EVENTS
from bstack_utils.bstack11l1ll111l_opy_ import bstack11l1ll111l_opy_
from bstack_utils.helper import bstack11ll11lll_opy_, bstack1111ll11ll_opy_, bstack1lllll11ll_opy_, bstack11ll1l11lll_opy_, \
  bstack11ll1ll1ll1_opy_, bstack1lll111ll1_opy_, get_host_info, bstack11ll1l1ll1l_opy_, bstack11ll1llll_opy_, error_handler, bstack11ll1ll1lll_opy_, bstack11ll1l11l1l_opy_, bstack1l11lllll1_opy_
from browserstack_sdk._version import __version__
from bstack_utils.bstack11l1l1111_opy_ import get_logger
from bstack_utils.bstack1l1l1l1111_opy_ import bstack1ll1l1ll1l1_opy_
from selenium.webdriver.chrome.options import Options as ChromeOptions
from browserstack_sdk.sdk_cli.cli import cli
from bstack_utils.constants import *
logger = get_logger(__name__)
bstack1l1l1l1111_opy_ = bstack1ll1l1ll1l1_opy_()
@error_handler(class_method=False)
def _11ll1ll11ll_opy_(driver, bstack111111l1l1_opy_):
  response = {}
  try:
    caps = driver.capabilities
    response = {
        bstack111l11_opy_ (u"ࠨࡱࡶࡣࡳࡧ࡭ࡦࠩᘮ"): caps.get(bstack111l11_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡒࡦࡳࡥࠨᘯ"), None),
        bstack111l11_opy_ (u"ࠪࡳࡸࡥࡶࡦࡴࡶ࡭ࡴࡴࠧᘰ"): bstack111111l1l1_opy_.get(bstack111l11_opy_ (u"ࠫࡴࡹࡖࡦࡴࡶ࡭ࡴࡴࠧᘱ"), None),
        bstack111l11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡥ࡮ࡢ࡯ࡨࠫᘲ"): caps.get(bstack111l11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫᘳ"), None),
        bstack111l11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡸࡨࡶࡸ࡯࡯࡯ࠩᘴ"): caps.get(bstack111l11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩᘵ"), None)
    }
  except Exception as error:
    logger.debug(bstack111l11_opy_ (u"ࠩࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡨࡨࡸࡨ࡮ࡩ࡯ࡩࠣࡴࡱࡧࡴࡧࡱࡵࡱࠥࡪࡥࡵࡣ࡬ࡰࡸࠦࡷࡪࡶ࡫ࠤࡪࡸࡲࡰࡴࠣ࠾ࠥ࠭ᘶ") + str(error))
  return response
def on():
    if os.environ.get(bstack111l11_opy_ (u"ࠪࡆࡘࡥࡁ࠲࠳࡜ࡣࡏ࡝ࡔࠨᘷ"), None) is None or os.environ[bstack111l11_opy_ (u"ࠫࡇ࡙࡟ࡂ࠳࠴࡝ࡤࡐࡗࡕࠩᘸ")] == bstack111l11_opy_ (u"ࠧࡴࡵ࡭࡮ࠥᘹ"):
        return False
    return True
def bstack1l1l11ll1_opy_(config):
  return config.get(bstack111l11_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ᘺ"), False) or any([p.get(bstack111l11_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧᘻ"), False) == True for p in config.get(bstack111l11_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫᘼ"), [])])
def bstack1l1l11111l_opy_(config, bstack1l1ll1lll_opy_):
  try:
    bstack11ll1ll11l1_opy_ = config.get(bstack111l11_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩᘽ"), False)
    if int(bstack1l1ll1lll_opy_) < len(config.get(bstack111l11_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ᘾ"), [])) and config[bstack111l11_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧᘿ")][bstack1l1ll1lll_opy_]:
      bstack11ll1l11l11_opy_ = config[bstack111l11_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨᙀ")][bstack1l1ll1lll_opy_].get(bstack111l11_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ᙁ"), None)
    else:
      bstack11ll1l11l11_opy_ = config.get(bstack111l11_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧᙂ"), None)
    if bstack11ll1l11l11_opy_ != None:
      bstack11ll1ll11l1_opy_ = bstack11ll1l11l11_opy_
    bstack11ll1ll1l1l_opy_ = os.getenv(bstack111l11_opy_ (u"ࠨࡄࡖࡣࡆ࠷࠱࡚ࡡࡍ࡛࡙࠭ᙃ")) is not None and len(os.getenv(bstack111l11_opy_ (u"ࠩࡅࡗࡤࡇ࠱࠲࡛ࡢࡎ࡜࡚ࠧᙄ"))) > 0 and os.getenv(bstack111l11_opy_ (u"ࠪࡆࡘࡥࡁ࠲࠳࡜ࡣࡏ࡝ࡔࠨᙅ")) != bstack111l11_opy_ (u"ࠫࡳࡻ࡬࡭ࠩᙆ")
    return bstack11ll1ll11l1_opy_ and bstack11ll1ll1l1l_opy_
  except Exception as error:
    logger.debug(bstack111l11_opy_ (u"ࠬࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡻ࡫ࡲࡪࡨࡼ࡭ࡳ࡭ࠠࡵࡪࡨࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡽࡩࡵࡪࠣࡩࡷࡸ࡯ࡳࠢ࠽ࠤࠬᙇ") + str(error))
  return False
def bstack11l1l1ll11_opy_(test_tags):
  bstack1ll11ll1l11_opy_ = os.getenv(bstack111l11_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡢࡅࡈࡉࡅࡔࡕࡌࡆࡎࡒࡉࡕ࡛ࡢࡇࡔࡔࡆࡊࡉࡘࡖࡆ࡚ࡉࡐࡐࡢ࡝ࡒࡒࠧᙈ"))
  if bstack1ll11ll1l11_opy_ is None:
    return True
  bstack1ll11ll1l11_opy_ = json.loads(bstack1ll11ll1l11_opy_)
  try:
    include_tags = bstack1ll11ll1l11_opy_[bstack111l11_opy_ (u"ࠧࡪࡰࡦࡰࡺࡪࡥࡕࡣࡪࡷࡎࡴࡔࡦࡵࡷ࡭ࡳ࡭ࡓࡤࡱࡳࡩࠬᙉ")] if bstack111l11_opy_ (u"ࠨ࡫ࡱࡧࡱࡻࡤࡦࡖࡤ࡫ࡸࡏ࡮ࡕࡧࡶࡸ࡮ࡴࡧࡔࡥࡲࡴࡪ࠭ᙊ") in bstack1ll11ll1l11_opy_ and isinstance(bstack1ll11ll1l11_opy_[bstack111l11_opy_ (u"ࠩ࡬ࡲࡨࡲࡵࡥࡧࡗࡥ࡬ࡹࡉ࡯ࡖࡨࡷࡹ࡯࡮ࡨࡕࡦࡳࡵ࡫ࠧᙋ")], list) else []
    exclude_tags = bstack1ll11ll1l11_opy_[bstack111l11_opy_ (u"ࠪࡩࡽࡩ࡬ࡶࡦࡨࡘࡦ࡭ࡳࡊࡰࡗࡩࡸࡺࡩ࡯ࡩࡖࡧࡴࡶࡥࠨᙌ")] if bstack111l11_opy_ (u"ࠫࡪࡾࡣ࡭ࡷࡧࡩ࡙ࡧࡧࡴࡋࡱࡘࡪࡹࡴࡪࡰࡪࡗࡨࡵࡰࡦࠩᙍ") in bstack1ll11ll1l11_opy_ and isinstance(bstack1ll11ll1l11_opy_[bstack111l11_opy_ (u"ࠬ࡫ࡸࡤ࡮ࡸࡨࡪ࡚ࡡࡨࡵࡌࡲ࡙࡫ࡳࡵ࡫ࡱ࡫ࡘࡩ࡯ࡱࡧࠪᙎ")], list) else []
    excluded = any(tag in exclude_tags for tag in test_tags)
    included = len(include_tags) == 0 or any(tag in include_tags for tag in test_tags)
    return not excluded and included
  except Exception as error:
    logger.debug(bstack111l11_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡽࡨࡪ࡮ࡨࠤࡻࡧ࡬ࡪࡦࡤࡸ࡮ࡴࡧࠡࡶࡨࡷࡹࠦࡣࡢࡵࡨࠤ࡫ࡵࡲࠡࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡤࡨࡪࡴࡸࡥࠡࡵࡦࡥࡳࡴࡩ࡯ࡩ࠱ࠤࡊࡸࡲࡰࡴࠣ࠾ࠥࠨᙏ") + str(error))
  return False
def bstack11ll11lllll_opy_(config, bstack11ll1l1l11l_opy_, bstack11ll1l11111_opy_, bstack11ll11l1lll_opy_):
  bstack11ll1l1l1l1_opy_ = bstack11ll1l11lll_opy_(config)
  bstack11ll11l1l1l_opy_ = bstack11ll1ll1ll1_opy_(config)
  if bstack11ll1l1l1l1_opy_ is None or bstack11ll11l1l1l_opy_ is None:
    logger.error(bstack111l11_opy_ (u"ࠧࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡻ࡭࡯࡬ࡦࠢࡦࡶࡪࡧࡴࡪࡰࡪࠤࡹ࡫ࡳࡵࠢࡵࡹࡳࠦࡦࡰࡴࠣࡆࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࠢࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡀࠠࡎ࡫ࡶࡷ࡮ࡴࡧࠡࡣࡸࡸ࡭࡫࡮ࡵ࡫ࡦࡥࡹ࡯࡯࡯ࠢࡷࡳࡰ࡫࡮ࠨᙐ"))
    return [None, None]
  try:
    settings = json.loads(os.getenv(bstack111l11_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡤࡇࡃࡄࡇࡖࡗࡎࡈࡉࡍࡋࡗ࡝ࡤࡉࡏࡏࡈࡌࡋ࡚ࡘࡁࡕࡋࡒࡒࡤ࡟ࡍࡍࠩᙑ"), bstack111l11_opy_ (u"ࠩࡾࢁࠬᙒ")))
    data = {
        bstack111l11_opy_ (u"ࠪࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠨᙓ"): config[bstack111l11_opy_ (u"ࠫࡵࡸ࡯࡫ࡧࡦࡸࡓࡧ࡭ࡦࠩᙔ")],
        bstack111l11_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨᙕ"): config.get(bstack111l11_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩᙖ"), os.path.basename(os.getcwd())),
        bstack111l11_opy_ (u"ࠧࡴࡶࡤࡶࡹ࡚ࡩ࡮ࡧࠪᙗ"): bstack11ll11lll_opy_(),
        bstack111l11_opy_ (u"ࠨࡦࡨࡷࡨࡸࡩࡱࡶ࡬ࡳࡳ࠭ᙘ"): config.get(bstack111l11_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡅࡧࡶࡧࡷ࡯ࡰࡵ࡫ࡲࡲࠬᙙ"), bstack111l11_opy_ (u"ࠪࠫᙚ")),
        bstack111l11_opy_ (u"ࠫࡸࡵࡵࡳࡥࡨࠫᙛ"): {
            bstack111l11_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡏࡣࡰࡩࠬᙜ"): bstack11ll1l1l11l_opy_,
            bstack111l11_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡘࡨࡶࡸ࡯࡯࡯ࠩᙝ"): bstack11ll1l11111_opy_,
            bstack111l11_opy_ (u"ࠧࡴࡦ࡮࡚ࡪࡸࡳࡪࡱࡱࠫᙞ"): __version__,
            bstack111l11_opy_ (u"ࠨ࡮ࡤࡲ࡬ࡻࡡࡨࡧࠪᙟ"): bstack111l11_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯ࠩᙠ"),
            bstack111l11_opy_ (u"ࠪࡸࡪࡹࡴࡇࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪᙡ"): bstack111l11_opy_ (u"ࠫࡸ࡫࡬ࡦࡰ࡬ࡹࡲ࠭ᙢ"),
            bstack111l11_opy_ (u"ࠬࡺࡥࡴࡶࡉࡶࡦࡳࡥࡸࡱࡵ࡯࡛࡫ࡲࡴ࡫ࡲࡲࠬᙣ"): bstack11ll11l1lll_opy_
        },
        bstack111l11_opy_ (u"࠭ࡳࡦࡶࡷ࡭ࡳ࡭ࡳࠨᙤ"): settings,
        bstack111l11_opy_ (u"ࠧࡷࡧࡵࡷ࡮ࡵ࡮ࡄࡱࡱࡸࡷࡵ࡬ࠨᙥ"): bstack11ll1l1ll1l_opy_(),
        bstack111l11_opy_ (u"ࠨࡥ࡬ࡍࡳ࡬࡯ࠨᙦ"): bstack1lll111ll1_opy_(),
        bstack111l11_opy_ (u"ࠩ࡫ࡳࡸࡺࡉ࡯ࡨࡲࠫᙧ"): get_host_info(),
        bstack111l11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠬᙨ"): bstack1lllll11ll_opy_(config)
    }
    headers = {
        bstack111l11_opy_ (u"ࠫࡈࡵ࡮ࡵࡧࡱࡸ࠲࡚ࡹࡱࡧࠪᙩ"): bstack111l11_opy_ (u"ࠬࡧࡰࡱ࡮࡬ࡧࡦࡺࡩࡰࡰ࠲࡮ࡸࡵ࡮ࠨᙪ"),
    }
    config = {
        bstack111l11_opy_ (u"࠭ࡡࡶࡶ࡫ࠫᙫ"): (bstack11ll1l1l1l1_opy_, bstack11ll11l1l1l_opy_),
        bstack111l11_opy_ (u"ࠧࡩࡧࡤࡨࡪࡸࡳࠨᙬ"): headers
    }
    response = bstack11ll1llll_opy_(bstack111l11_opy_ (u"ࠨࡒࡒࡗ࡙࠭᙭"), bstack11ll1l1ll11_opy_ + bstack111l11_opy_ (u"ࠩ࠲ࡺ࠷࠵ࡴࡦࡵࡷࡣࡷࡻ࡮ࡴࠩ᙮"), data, config)
    bstack11ll11ll1l1_opy_ = response.json()
    if bstack11ll11ll1l1_opy_[bstack111l11_opy_ (u"ࠪࡷࡺࡩࡣࡦࡵࡶࠫᙯ")]:
      parsed = json.loads(os.getenv(bstack111l11_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡠࡃࡆࡇࡊ࡙ࡓࡊࡄࡌࡐࡎ࡚࡙ࡠࡅࡒࡒࡋࡏࡇࡖࡔࡄࡘࡎࡕࡎࡠ࡛ࡐࡐࠬᙰ"), bstack111l11_opy_ (u"ࠬࢁࡽࠨᙱ")))
      parsed[bstack111l11_opy_ (u"࠭ࡳࡤࡣࡱࡲࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧᙲ")] = bstack11ll11ll1l1_opy_[bstack111l11_opy_ (u"ࠧࡥࡣࡷࡥࠬᙳ")][bstack111l11_opy_ (u"ࠨࡵࡦࡥࡳࡴࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩᙴ")]
      os.environ[bstack111l11_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡥࡁࡄࡅࡈࡗࡘࡏࡂࡊࡎࡌࡘ࡞ࡥࡃࡐࡐࡉࡍࡌ࡛ࡒࡂࡖࡌࡓࡓࡥ࡙ࡎࡎࠪᙵ")] = json.dumps(parsed)
      bstack11l1ll111l_opy_.bstack11ll1l1lll_opy_(bstack11ll11ll1l1_opy_[bstack111l11_opy_ (u"ࠪࡨࡦࡺࡡࠨᙶ")][bstack111l11_opy_ (u"ࠫࡸࡩࡲࡪࡲࡷࡷࠬᙷ")])
      bstack11l1ll111l_opy_.bstack11ll11lll1l_opy_(bstack11ll11ll1l1_opy_[bstack111l11_opy_ (u"ࠬࡪࡡࡵࡣࠪᙸ")][bstack111l11_opy_ (u"࠭ࡣࡰ࡯ࡰࡥࡳࡪࡳࠨᙹ")])
      bstack11l1ll111l_opy_.store()
      return bstack11ll11ll1l1_opy_[bstack111l11_opy_ (u"ࠧࡥࡣࡷࡥࠬᙺ")][bstack111l11_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡕࡱ࡮ࡩࡳ࠭ᙻ")], bstack11ll11ll1l1_opy_[bstack111l11_opy_ (u"ࠩࡧࡥࡹࡧࠧᙼ")][bstack111l11_opy_ (u"ࠪ࡭ࡩ࠭ᙽ")]
    else:
      logger.error(bstack111l11_opy_ (u"ࠫࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡸࡪ࡬ࡰࡪࠦࡲࡶࡰࡱ࡭ࡳ࡭ࠠࡃࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࠦࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰ࠽ࠤࠬᙾ") + bstack11ll11ll1l1_opy_[bstack111l11_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭ᙿ")])
      if bstack11ll11ll1l1_opy_[bstack111l11_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧ ")] == bstack111l11_opy_ (u"ࠧࡊࡰࡹࡥࡱ࡯ࡤࠡࡥࡲࡲ࡫࡯ࡧࡶࡴࡤࡸ࡮ࡵ࡮ࠡࡲࡤࡷࡸ࡫ࡤ࠯ࠩᚁ"):
        for bstack11ll1llll11_opy_ in bstack11ll11ll1l1_opy_[bstack111l11_opy_ (u"ࠨࡧࡵࡶࡴࡸࡳࠨᚂ")]:
          logger.error(bstack11ll1llll11_opy_[bstack111l11_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪᚃ")])
      return None, None
  except Exception as error:
    logger.error(bstack111l11_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡷࡩ࡫࡯ࡩࠥࡩࡲࡦࡣࡷ࡭ࡳ࡭ࠠࡵࡧࡶࡸࠥࡸࡵ࡯ࠢࡩࡳࡷࠦࡂࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯࠼ࠣࠦᚄ") +  str(error))
    return None, None
def bstack11ll1l111l1_opy_():
  if os.getenv(bstack111l11_opy_ (u"ࠫࡇ࡙࡟ࡂ࠳࠴࡝ࡤࡐࡗࡕࠩᚅ")) is None:
    return {
        bstack111l11_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬᚆ"): bstack111l11_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬᚇ"),
        bstack111l11_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨᚈ"): bstack111l11_opy_ (u"ࠨࡄࡸ࡭ࡱࡪࠠࡤࡴࡨࡥࡹ࡯࡯࡯ࠢ࡫ࡥࡩࠦࡦࡢ࡫࡯ࡩࡩ࠴ࠧᚉ")
    }
  data = {bstack111l11_opy_ (u"ࠩࡨࡲࡩ࡚ࡩ࡮ࡧࠪᚊ"): bstack11ll11lll_opy_()}
  headers = {
      bstack111l11_opy_ (u"ࠪࡅࡺࡺࡨࡰࡴ࡬ࡾࡦࡺࡩࡰࡰࠪᚋ"): bstack111l11_opy_ (u"ࠫࡇ࡫ࡡࡳࡧࡵࠤࠬᚌ") + os.getenv(bstack111l11_opy_ (u"ࠧࡈࡓࡠࡃ࠴࠵࡞ࡥࡊࡘࡖࠥᚍ")),
      bstack111l11_opy_ (u"࠭ࡃࡰࡰࡷࡩࡳࡺ࠭ࡕࡻࡳࡩࠬᚎ"): bstack111l11_opy_ (u"ࠧࡢࡲࡳࡰ࡮ࡩࡡࡵ࡫ࡲࡲ࠴ࡰࡳࡰࡰࠪᚏ")
  }
  response = bstack11ll1llll_opy_(bstack111l11_opy_ (u"ࠨࡒࡘࡘࠬᚐ"), bstack11ll1l1ll11_opy_ + bstack111l11_opy_ (u"ࠩ࠲ࡸࡪࡹࡴࡠࡴࡸࡲࡸ࠵ࡳࡵࡱࡳࠫᚑ"), data, { bstack111l11_opy_ (u"ࠪ࡬ࡪࡧࡤࡦࡴࡶࠫᚒ"): headers })
  try:
    if response.status_code == 200:
      logger.info(bstack111l11_opy_ (u"ࠦࡇࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠࡕࡧࡶࡸࠥࡘࡵ࡯ࠢࡰࡥࡷࡱࡥࡥࠢࡤࡷࠥࡩ࡯࡮ࡲ࡯ࡩࡹ࡫ࡤࠡࡣࡷࠤࠧᚓ") + bstack1111ll11ll_opy_().isoformat() + bstack111l11_opy_ (u"ࠬࡠࠧᚔ"))
      return {bstack111l11_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭ᚕ"): bstack111l11_opy_ (u"ࠧࡴࡷࡦࡧࡪࡹࡳࠨᚖ"), bstack111l11_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩᚗ"): bstack111l11_opy_ (u"ࠩࠪᚘ")}
    else:
      response.raise_for_status()
  except requests.RequestException as error:
    logger.error(bstack111l11_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡷࡩ࡫࡯ࡩࠥࡳࡡࡳ࡭࡬ࡲ࡬ࠦࡣࡰ࡯ࡳࡰࡪࡺࡩࡰࡰࠣࡳ࡫ࠦࡂࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡗࡩࡸࡺࠠࡓࡷࡱ࠾ࠥࠨᚙ") + str(error))
    return {
        bstack111l11_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫᚚ"): bstack111l11_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫ᚛"),
        bstack111l11_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧ᚜"): str(error)
    }
def bstack11ll1l1lll1_opy_(bstack11ll1ll111l_opy_):
    return re.match(bstack111l11_opy_ (u"ࡲࠨࡠ࡟ࡨ࠰࠮࡜࠯࡞ࡧ࠯࠮ࡅࠤࠨ᚝"), bstack11ll1ll111l_opy_.strip()) is not None
def bstack1llll1l1_opy_(caps, options, desired_capabilities={}, config=None):
    try:
        if options:
          bstack11ll1lllll1_opy_ = options.to_capabilities()
        elif desired_capabilities:
          bstack11ll1lllll1_opy_ = desired_capabilities
        else:
          bstack11ll1lllll1_opy_ = {}
        bstack1ll1111l11l_opy_ = (bstack11ll1lllll1_opy_.get(bstack111l11_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡑࡥࡲ࡫ࠧ᚞"), bstack111l11_opy_ (u"ࠩࠪ᚟")).lower() or caps.get(bstack111l11_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡓࡧ࡭ࡦࠩᚠ"), bstack111l11_opy_ (u"ࠫࠬᚡ")).lower())
        if bstack1ll1111l11l_opy_ == bstack111l11_opy_ (u"ࠬ࡯࡯ࡴࠩᚢ"):
            return True
        if bstack1ll1111l11l_opy_ == bstack111l11_opy_ (u"࠭ࡡ࡯ࡦࡵࡳ࡮ࡪࠧᚣ"):
            bstack1ll111l1l11_opy_ = str(float(caps.get(bstack111l11_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡘࡨࡶࡸ࡯࡯࡯ࠩᚤ")) or bstack11ll1lllll1_opy_.get(bstack111l11_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩᚥ"), {}).get(bstack111l11_opy_ (u"ࠩࡲࡷ࡛࡫ࡲࡴ࡫ࡲࡲࠬᚦ"),bstack111l11_opy_ (u"ࠪࠫᚧ"))))
            if bstack1ll1111l11l_opy_ == bstack111l11_opy_ (u"ࠫࡦࡴࡤࡳࡱ࡬ࡨࠬᚨ") and int(bstack1ll111l1l11_opy_.split(bstack111l11_opy_ (u"ࠬ࠴ࠧᚩ"))[0]) < float(bstack11ll1l1111l_opy_):
                logger.warning(str(bstack11ll11lll11_opy_))
                return False
            return True
        bstack1ll11l11l1l_opy_ = caps.get(bstack111l11_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧᚪ"), {}).get(bstack111l11_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࡎࡢ࡯ࡨࠫᚫ"), caps.get(bstack111l11_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࠨᚬ"), bstack111l11_opy_ (u"ࠩࠪᚭ")))
        if bstack1ll11l11l1l_opy_:
            logger.warning(bstack111l11_opy_ (u"ࠥࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠࡸ࡫࡯ࡰࠥࡸࡵ࡯ࠢࡲࡲࡱࡿࠠࡰࡰࠣࡈࡪࡹ࡫ࡵࡱࡳࠤࡧࡸ࡯ࡸࡵࡨࡶࡸ࠴ࠢᚮ"))
            return False
        browser = caps.get(bstack111l11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩᚯ"), bstack111l11_opy_ (u"ࠬ࠭ᚰ")).lower() or bstack11ll1lllll1_opy_.get(bstack111l11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫᚱ"), bstack111l11_opy_ (u"ࠧࠨᚲ")).lower()
        if browser != bstack111l11_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࠨᚳ"):
            logger.warning(bstack111l11_opy_ (u"ࠤࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࠦࡷࡪ࡮࡯ࠤࡷࡻ࡮ࠡࡱࡱࡰࡾࠦ࡯࡯ࠢࡆ࡬ࡷࡵ࡭ࡦࠢࡥࡶࡴࡽࡳࡦࡴࡶ࠲ࠧᚴ"))
            return False
        browser_version = caps.get(bstack111l11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫᚵ")) or caps.get(bstack111l11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ᚶ")) or bstack11ll1lllll1_opy_.get(bstack111l11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᚷ")) or bstack11ll1lllll1_opy_.get(bstack111l11_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧᚸ"), {}).get(bstack111l11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨᚹ")) or bstack11ll1lllll1_opy_.get(bstack111l11_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩᚺ"), {}).get(bstack111l11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡢࡺࡪࡸࡳࡪࡱࡱࠫᚻ"))
        bstack1ll111l1lll_opy_ = bstack11ll1l1llll_opy_.bstack1ll11ll1l1l_opy_
        bstack11ll1lll111_opy_ = False
        if config is not None:
          bstack11ll1lll111_opy_ = bstack111l11_opy_ (u"ࠪࡸࡺࡸࡢࡰࡕࡦࡥࡱ࡫ࠧᚼ") in config and str(config[bstack111l11_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨᚽ")]).lower() != bstack111l11_opy_ (u"ࠬ࡬ࡡ࡭ࡵࡨࠫᚾ")
        if os.environ.get(bstack111l11_opy_ (u"࠭ࡉࡔࡡࡑࡓࡓࡥࡂࡔࡖࡄࡇࡐࡥࡉࡏࡈࡕࡅࡤࡇ࠱࠲࡛ࡢࡗࡊ࡙ࡓࡊࡑࡑࠫᚿ"), bstack111l11_opy_ (u"ࠧࠨᛀ")).lower() == bstack111l11_opy_ (u"ࠨࡶࡵࡹࡪ࠭ᛁ") or bstack11ll1lll111_opy_:
          bstack1ll111l1lll_opy_ = bstack11ll1l1llll_opy_.bstack1ll1l11111l_opy_
        if browser_version and browser_version != bstack111l11_opy_ (u"ࠩ࡯ࡥࡹ࡫ࡳࡵࠩᛂ") and int(browser_version.split(bstack111l11_opy_ (u"ࠪ࠲ࠬᛃ"))[0]) <= bstack1ll111l1lll_opy_:
          logger.warning(bstack111111ll11_opy_ (u"ࠫࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡹ࡬ࡰࡱࠦࡲࡶࡰࠣࡳࡳࡲࡹࠡࡱࡱࠤࡈ࡮ࡲࡰ࡯ࡨࠤࡧࡸ࡯ࡸࡵࡨࡶࠥࡼࡥࡳࡵ࡬ࡳࡳࠦࡧࡳࡧࡤࡸࡪࡸࠠࡵࡪࡤࡲࠥࢁ࡭ࡪࡰࡢࡥ࠶࠷ࡹࡠࡵࡸࡴࡵࡵࡲࡵࡧࡧࡣࡨ࡮ࡲࡰ࡯ࡨࡣࡻ࡫ࡲࡴ࡫ࡲࡲࢂ࠴ࠧᛄ"))
          return False
        if not options:
          bstack1ll111llll1_opy_ = caps.get(bstack111l11_opy_ (u"ࠬ࡭࡯ࡰࡩ࠽ࡧ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪᛅ")) or bstack11ll1lllll1_opy_.get(bstack111l11_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫᛆ"), {})
          if bstack111l11_opy_ (u"ࠧ࠮࠯࡫ࡩࡦࡪ࡬ࡦࡵࡶࠫᛇ") in bstack1ll111llll1_opy_.get(bstack111l11_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭ᛈ"), []):
              logger.warning(bstack111l11_opy_ (u"ࠤࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࠦࡷࡪ࡮࡯ࠤࡳࡵࡴࠡࡴࡸࡲࠥࡵ࡮ࠡ࡮ࡨ࡫ࡦࡩࡹࠡࡪࡨࡥࡩࡲࡥࡴࡵࠣࡱࡴࡪࡥ࠯ࠢࡖࡻ࡮ࡺࡣࡩࠢࡷࡳࠥࡴࡥࡸࠢ࡫ࡩࡦࡪ࡬ࡦࡵࡶࠤࡲࡵࡤࡦࠢࡲࡶࠥࡧࡶࡰ࡫ࡧࠤࡺࡹࡩ࡯ࡩࠣ࡬ࡪࡧࡤ࡭ࡧࡶࡷࠥࡳ࡯ࡥࡧ࠱ࠦᛉ"))
              return False
        return True
    except Exception as error:
        logger.debug(bstack111l11_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡹࡥࡱ࡯ࡤࡢࡶࡨࠤࡦ࠷࠱ࡺࠢࡶࡹࡵࡶ࡯ࡳࡶࠣ࠾ࠧᛊ") + str(error))
        return False
def set_capabilities(caps, config):
  try:
    bstack1lll11l11ll_opy_ = config.get(bstack111l11_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡓࡵࡺࡩࡰࡰࡶࠫᛋ"), {})
    bstack1lll11l11ll_opy_[bstack111l11_opy_ (u"ࠬࡧࡵࡵࡪࡗࡳࡰ࡫࡮ࠨᛌ")] = os.getenv(bstack111l11_opy_ (u"࠭ࡂࡔࡡࡄ࠵࠶࡟࡟ࡋ࡙ࡗࠫᛍ"))
    bstack11ll1llll1l_opy_ = json.loads(os.getenv(bstack111l11_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡣࡆࡉࡃࡆࡕࡖࡍࡇࡏࡌࡊࡖ࡜ࡣࡈࡕࡎࡇࡋࡊ࡙ࡗࡇࡔࡊࡑࡑࡣ࡞ࡓࡌࠨᛎ"), bstack111l11_opy_ (u"ࠨࡽࢀࠫᛏ"))).get(bstack111l11_opy_ (u"ࠩࡶࡧࡦࡴ࡮ࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪᛐ"))
    if not config[bstack111l11_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡒࡵࡳࡩࡻࡣࡵࡏࡤࡴࠬᛑ")].get(bstack111l11_opy_ (u"ࠦࡦࡶࡰࡠࡣࡸࡸࡴࡳࡡࡵࡧࠥᛒ")):
      if bstack111l11_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࠿ࡵࡰࡵ࡫ࡲࡲࡸ࠭ᛓ") in caps:
        caps[bstack111l11_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧᛔ")][bstack111l11_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡏࡱࡶ࡬ࡳࡳࡹࠧᛕ")] = bstack1lll11l11ll_opy_
        caps[bstack111l11_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩᛖ")][bstack111l11_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩᛗ")][bstack111l11_opy_ (u"ࠪࡷࡨࡧ࡮࡯ࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫᛘ")] = bstack11ll1llll1l_opy_
      else:
        caps[bstack111l11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪᛙ")] = bstack1lll11l11ll_opy_
        caps[bstack111l11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡓࡵࡺࡩࡰࡰࡶࠫᛚ")][bstack111l11_opy_ (u"࠭ࡳࡤࡣࡱࡲࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧᛛ")] = bstack11ll1llll1l_opy_
  except Exception as error:
    logger.debug(bstack111l11_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡻ࡭࡯࡬ࡦࠢࡶࡩࡹࡺࡩ࡯ࡩࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠴ࠠࡆࡴࡵࡳࡷࡀࠠࠣᛜ") +  str(error))
def bstack1lllll1ll_opy_(driver, bstack11ll1lll1l1_opy_):
  try:
    setattr(driver, bstack111l11_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡂ࠳࠴ࡽࡘ࡮࡯ࡶ࡮ࡧࡗࡨࡧ࡮ࠨᛝ"), True)
    session = driver.session_id
    if session:
      bstack11ll11l1ll1_opy_ = True
      current_url = driver.current_url
      try:
        url = urlparse(current_url)
      except Exception as e:
        bstack11ll11l1ll1_opy_ = False
      bstack11ll11l1ll1_opy_ = url.scheme in [bstack111l11_opy_ (u"ࠤ࡫ࡸࡹࡶࠢᛞ"), bstack111l11_opy_ (u"ࠥ࡬ࡹࡺࡰࡴࠤᛟ")]
      if bstack11ll11l1ll1_opy_:
        if bstack11ll1lll1l1_opy_:
          logger.info(bstack111l11_opy_ (u"ࠦࡘ࡫ࡴࡶࡲࠣࡪࡴࡸࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡵࡧࡶࡸ࡮ࡴࡧࠡࡪࡤࡷࠥࡹࡴࡢࡴࡷࡩࡩ࠴ࠠࡂࡷࡷࡳࡲࡧࡴࡦࠢࡷࡩࡸࡺࠠࡤࡣࡶࡩࠥ࡫ࡸࡦࡥࡸࡸ࡮ࡵ࡮ࠡࡹ࡬ࡰࡱࠦࡢࡦࡩ࡬ࡲࠥࡳ࡯࡮ࡧࡱࡸࡦࡸࡩ࡭ࡻ࠱ࠦᛠ"))
      return bstack11ll1lll1l1_opy_
  except Exception as e:
    logger.error(bstack111l11_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡸࡺࡡࡳࡶ࡬ࡲ࡬ࠦࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡷࡨࡧ࡮ࠡࡨࡲࡶࠥࡺࡨࡪࡵࠣࡸࡪࡹࡴࠡࡥࡤࡷࡪࡀࠠࠣᛡ") + str(e))
    return False
def bstack111l1lll_opy_(driver, name, path):
  try:
    bstack1ll11ll11l1_opy_ = {
        bstack111l11_opy_ (u"࠭ࡴࡩࡖࡨࡷࡹࡘࡵ࡯ࡗࡸ࡭ࡩ࠭ᛢ"): threading.current_thread().current_test_uuid,
        bstack111l11_opy_ (u"ࠧࡵࡪࡅࡹ࡮ࡲࡤࡖࡷ࡬ࡨࠬᛣ"): os.environ.get(bstack111l11_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭ᛤ"), bstack111l11_opy_ (u"ࠩࠪᛥ")),
        bstack111l11_opy_ (u"ࠪࡸ࡭ࡐࡷࡵࡖࡲ࡯ࡪࡴࠧᛦ"): os.environ.get(bstack111l11_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣࡏ࡝ࡔࠨᛧ"), bstack111l11_opy_ (u"ࠬ࠭ᛨ"))
    }
    bstack1ll1111l1l1_opy_ = bstack1l1l1l1111_opy_.bstack1ll11l1ll1l_opy_(EVENTS.bstack11111ll1_opy_.value)
    logger.debug(bstack111l11_opy_ (u"࠭ࡐࡦࡴࡩࡳࡷࡳࡩ࡯ࡩࠣࡷࡨࡧ࡮ࠡࡤࡨࡪࡴࡸࡥࠡࡵࡤࡺ࡮ࡴࡧࠡࡴࡨࡷࡺࡲࡴࡴࠩᛩ"))
    try:
      if (bstack1l11lllll1_opy_(threading.current_thread(), bstack111l11_opy_ (u"ࠧࡪࡵࡄࡴࡵࡇ࠱࠲ࡻࡗࡩࡸࡺࠧᛪ"), None) and bstack1l11lllll1_opy_(threading.current_thread(), bstack111l11_opy_ (u"ࠨࡣࡳࡴࡆ࠷࠱ࡺࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪ᛫"), None)):
        scripts = {bstack111l11_opy_ (u"ࠩࡶࡧࡦࡴࠧ᛬"): bstack11l1ll111l_opy_.perform_scan}
        bstack11ll11llll1_opy_ = json.loads(scripts[bstack111l11_opy_ (u"ࠥࡷࡨࡧ࡮ࠣ᛭")].replace(bstack111l11_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࠢᛮ"), bstack111l11_opy_ (u"ࠧࠨᛯ")))
        bstack11ll11llll1_opy_[bstack111l11_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩᛰ")][bstack111l11_opy_ (u"ࠧ࡮ࡧࡷ࡬ࡴࡪࠧᛱ")] = None
        scripts[bstack111l11_opy_ (u"ࠣࡵࡦࡥࡳࠨᛲ")] = bstack111l11_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࠧᛳ") + json.dumps(bstack11ll11llll1_opy_)
        bstack11l1ll111l_opy_.bstack11ll1l1lll_opy_(scripts)
        bstack11l1ll111l_opy_.store()
        logger.debug(driver.execute_script(bstack11l1ll111l_opy_.perform_scan))
      else:
        logger.debug(driver.execute_async_script(bstack11l1ll111l_opy_.perform_scan, {bstack111l11_opy_ (u"ࠥࡱࡪࡺࡨࡰࡦࠥᛴ"): name}))
      bstack1l1l1l1111_opy_.end(EVENTS.bstack11111ll1_opy_.value, bstack1ll1111l1l1_opy_ + bstack111l11_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦᛵ"), bstack1ll1111l1l1_opy_ + bstack111l11_opy_ (u"ࠧࡀࡥ࡯ࡦࠥᛶ"), True, None)
    except Exception as error:
      bstack1l1l1l1111_opy_.end(EVENTS.bstack11111ll1_opy_.value, bstack1ll1111l1l1_opy_ + bstack111l11_opy_ (u"ࠨ࠺ࡴࡶࡤࡶࡹࠨᛷ"), bstack1ll1111l1l1_opy_ + bstack111l11_opy_ (u"ࠢ࠻ࡧࡱࡨࠧᛸ"), False, str(error))
    bstack1ll1111l1l1_opy_ = bstack1l1l1l1111_opy_.bstack11ll1l1l1ll_opy_(EVENTS.bstack1ll11ll1lll_opy_.value)
    bstack1l1l1l1111_opy_.mark(bstack1ll1111l1l1_opy_ + bstack111l11_opy_ (u"ࠣ࠼ࡶࡸࡦࡸࡴࠣ᛹"))
    try:
      if (bstack1l11lllll1_opy_(threading.current_thread(), bstack111l11_opy_ (u"ࠩ࡬ࡷࡆࡶࡰࡂ࠳࠴ࡽ࡙࡫ࡳࡵࠩ᛺"), None) and bstack1l11lllll1_opy_(threading.current_thread(), bstack111l11_opy_ (u"ࠪࡥࡵࡶࡁ࠲࠳ࡼࡔࡱࡧࡴࡧࡱࡵࡱࠬ᛻"), None)):
        scripts = {bstack111l11_opy_ (u"ࠫࡸࡩࡡ࡯ࠩ᛼"): bstack11l1ll111l_opy_.perform_scan}
        bstack11ll11llll1_opy_ = json.loads(scripts[bstack111l11_opy_ (u"ࠧࡹࡣࡢࡰࠥ᛽")].replace(bstack111l11_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࠤ᛾"), bstack111l11_opy_ (u"ࠢࠣ᛿")))
        bstack11ll11llll1_opy_[bstack111l11_opy_ (u"ࠨࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠫᜀ")][bstack111l11_opy_ (u"ࠩࡰࡩࡹ࡮࡯ࡥࠩᜁ")] = None
        scripts[bstack111l11_opy_ (u"ࠥࡷࡨࡧ࡮ࠣᜂ")] = bstack111l11_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࠢᜃ") + json.dumps(bstack11ll11llll1_opy_)
        bstack11l1ll111l_opy_.bstack11ll1l1lll_opy_(scripts)
        bstack11l1ll111l_opy_.store()
        logger.debug(driver.execute_script(bstack11l1ll111l_opy_.perform_scan))
      else:
        logger.debug(driver.execute_async_script(bstack11l1ll111l_opy_.bstack11ll1l1l111_opy_, bstack1ll11ll11l1_opy_))
      bstack1l1l1l1111_opy_.end(bstack1ll1111l1l1_opy_, bstack1ll1111l1l1_opy_ + bstack111l11_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧᜄ"), bstack1ll1111l1l1_opy_ + bstack111l11_opy_ (u"ࠨ࠺ࡦࡰࡧࠦᜅ"),True, None)
    except Exception as error:
      bstack1l1l1l1111_opy_.end(bstack1ll1111l1l1_opy_, bstack1ll1111l1l1_opy_ + bstack111l11_opy_ (u"ࠢ࠻ࡵࡷࡥࡷࡺࠢᜆ"), bstack1ll1111l1l1_opy_ + bstack111l11_opy_ (u"ࠣ࠼ࡨࡲࡩࠨᜇ"),False, str(error))
    logger.info(bstack111l11_opy_ (u"ࠤࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡷࡩࡸࡺࡩ࡯ࡩࠣࡪࡴࡸࠠࡵࡪ࡬ࡷࠥࡺࡥࡴࡶࠣࡧࡦࡹࡥࠡࡪࡤࡷࠥ࡫࡮ࡥࡧࡧ࠲ࠧᜈ"))
  except Exception as bstack1ll1111ll1l_opy_:
    logger.error(bstack111l11_opy_ (u"ࠥࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡶࡪࡹࡵ࡭ࡶࡶࠤࡨࡵࡵ࡭ࡦࠣࡲࡴࡺࠠࡣࡧࠣࡴࡷࡵࡣࡦࡵࡶࡩࡩࠦࡦࡰࡴࠣࡸ࡭࡫ࠠࡵࡧࡶࡸࠥࡩࡡࡴࡧ࠽ࠤࠧᜉ") + str(path) + bstack111l11_opy_ (u"ࠦࠥࡋࡲࡳࡱࡵࠤ࠿ࠨᜊ") + str(bstack1ll1111ll1l_opy_))
def bstack11ll1lll11l_opy_(driver):
    caps = driver.capabilities
    if caps.get(bstack111l11_opy_ (u"ࠧࡶ࡬ࡢࡶࡩࡳࡷࡳࡎࡢ࡯ࡨࠦᜋ")) and str(caps.get(bstack111l11_opy_ (u"ࠨࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡏࡣࡰࡩࠧᜌ"))).lower() == bstack111l11_opy_ (u"ࠢࡢࡰࡧࡶࡴ࡯ࡤࠣᜍ"):
        bstack1ll111l1l11_opy_ = caps.get(bstack111l11_opy_ (u"ࠣࡣࡳࡴ࡮ࡻ࡭࠻ࡲ࡯ࡥࡹ࡬࡯ࡳ࡯࡙ࡩࡷࡹࡩࡰࡰࠥᜎ")) or caps.get(bstack111l11_opy_ (u"ࠤࡳࡰࡦࡺࡦࡰࡴࡰ࡚ࡪࡸࡳࡪࡱࡱࠦᜏ"))
        if bstack1ll111l1l11_opy_ and int(str(bstack1ll111l1l11_opy_)) < bstack11ll1l1111l_opy_:
            return False
    return True
def bstack1llll1ll1_opy_(config):
  if bstack111l11_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪᜐ") in config:
        return config[bstack111l11_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᜑ")]
  for platform in config.get(bstack111l11_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨᜒ"), []):
      if bstack111l11_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ᜓ") in platform:
          return platform[bstack111l11_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿ᜔ࠧ")]
  return None
def bstack1ll1l11l11_opy_(bstack1l1ll11ll1_opy_):
  try:
    browser_name = bstack1l1ll11ll1_opy_[bstack111l11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡡࡱࡥࡲ࡫᜕ࠧ")]
    browser_version = bstack1l1ll11ll1_opy_[bstack111l11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡢࡺࡪࡸࡳࡪࡱࡱࠫ᜖")]
    chrome_options = bstack1l1ll11ll1_opy_[bstack111l11_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࡢࡳࡵࡺࡩࡰࡰࡶࠫ᜗")]
    try:
        bstack11ll1lll1ll_opy_ = int(browser_version.split(bstack111l11_opy_ (u"ࠫ࠳࠭᜘"))[0])
    except ValueError as e:
        logger.error(bstack111l11_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤࡼ࡮ࡩ࡭ࡧࠣࡧࡴࡴࡶࡦࡴࡷ࡭ࡳ࡭ࠠࡣࡴࡲࡻࡸ࡫ࡲࠡࡸࡨࡶࡸ࡯࡯࡯ࠤ᜙") + str(e))
        return False
    if not (browser_name and browser_name.lower() == bstack111l11_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪ࠭᜚")):
        logger.warning(bstack111l11_opy_ (u"ࠢࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡼ࡯࡬࡭ࠢࡵࡹࡳࠦ࡯࡯࡮ࡼࠤࡴࡴࠠࡄࡪࡵࡳࡲ࡫ࠠࡣࡴࡲࡻࡸ࡫ࡲࡴ࠰ࠥ᜛"))
        return False
    if bstack11ll1lll1ll_opy_ < bstack11ll1l1llll_opy_.bstack1ll1l11111l_opy_:
        logger.warning(bstack111111ll11_opy_ (u"ࠨࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠥࡸࡥࡲࡷ࡬ࡶࡪࡹࠠࡄࡪࡵࡳࡲ࡫ࠠࡷࡧࡵࡷ࡮ࡵ࡮ࠡࡽࡆࡓࡓ࡙ࡔࡂࡐࡗࡗ࠳ࡓࡉࡏࡋࡐ࡙ࡒࡥࡎࡐࡐࡢࡆࡘ࡚ࡁࡄࡍࡢࡍࡓࡌࡒࡂࡡࡄ࠵࠶࡟࡟ࡔࡗࡓࡔࡔࡘࡔࡆࡆࡢࡇࡍࡘࡏࡎࡇࡢ࡚ࡊࡘࡓࡊࡑࡑࢁࠥࡵࡲࠡࡪ࡬࡫࡭࡫ࡲ࠯ࠩ᜜"))
        return False
    if chrome_options and any(bstack111l11_opy_ (u"ࠩ࠰࠱࡭࡫ࡡࡥ࡮ࡨࡷࡸ࠭᜝") in value for value in chrome_options.values() if isinstance(value, str)):
        logger.warning(bstack111l11_opy_ (u"ࠥࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠࡸ࡫࡯ࡰࠥࡴ࡯ࡵࠢࡵࡹࡳࠦ࡯࡯ࠢ࡯ࡩ࡬ࡧࡣࡺࠢ࡫ࡩࡦࡪ࡬ࡦࡵࡶࠤࡲࡵࡤࡦ࠰ࠣࡗࡼ࡯ࡴࡤࡪࠣࡸࡴࠦ࡮ࡦࡹࠣ࡬ࡪࡧࡤ࡭ࡧࡶࡷࠥࡳ࡯ࡥࡧࠣࡳࡷࠦࡡࡷࡱ࡬ࡨࠥࡻࡳࡪࡰࡪࠤ࡭࡫ࡡࡥ࡮ࡨࡷࡸࠦ࡭ࡰࡦࡨ࠲ࠧ᜞"))
        return False
    return True
  except Exception as e:
    logger.error(bstack111l11_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡣࡩࡧࡦ࡯࡮ࡴࡧࠡࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࠣࡷࡺࡶࡰࡰࡴࡷࠤ࡫ࡵࡲࠡ࡮ࡲࡧࡦࡲࠠࡄࡪࡵࡳࡲ࡫࠺ࠡࠤᜟ") + str(e))
    return False
def bstack1ll111l1_opy_(bstack1l111llll_opy_, config):
    try:
      bstack1ll11llllll_opy_ = bstack111l11_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬᜠ") in config and config[bstack111l11_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ᜡ")] == True
      bstack11ll1lll111_opy_ = bstack111l11_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫᜢ") in config and str(config[bstack111l11_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬᜣ")]).lower() != bstack111l11_opy_ (u"ࠩࡩࡥࡱࡹࡥࠨᜤ")
      if not (bstack1ll11llllll_opy_ and (not bstack1lllll11ll_opy_(config) or bstack11ll1lll111_opy_)):
        return bstack1l111llll_opy_
      bstack11ll11ll11l_opy_ = bstack11l1ll111l_opy_.bstack11ll11l1l11_opy_
      if bstack11ll11ll11l_opy_ is None:
        logger.debug(bstack111l11_opy_ (u"ࠥࡋࡴࡵࡧ࡭ࡧࠣࡧ࡭ࡸ࡯࡮ࡧࠣࡳࡵࡺࡩࡰࡰࡶࠤࡦࡸࡥࠡࡐࡲࡲࡪࠨᜥ"))
        return bstack1l111llll_opy_
      bstack11ll11ll1ll_opy_ = int(str(bstack11ll1l11l1l_opy_()).split(bstack111l11_opy_ (u"ࠫ࠳࠭ᜦ"))[0])
      logger.debug(bstack111l11_opy_ (u"࡙ࠧࡥ࡭ࡧࡱ࡭ࡺࡳࠠࡷࡧࡵࡷ࡮ࡵ࡮ࠡࡦࡨࡸࡪࡩࡴࡦࡦ࠽ࠤࠧᜧ") + str(bstack11ll11ll1ll_opy_) + bstack111l11_opy_ (u"ࠨࠢᜨ"))
      if bstack11ll11ll1ll_opy_ == 3 and isinstance(bstack1l111llll_opy_, dict) and bstack111l11_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧᜩ") in bstack1l111llll_opy_ and bstack11ll11ll11l_opy_ is not None:
        if bstack111l11_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ᜪ") not in bstack1l111llll_opy_[bstack111l11_opy_ (u"ࠩࡧࡩࡸ࡯ࡲࡦࡦࡢࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠩᜫ")]:
          bstack1l111llll_opy_[bstack111l11_opy_ (u"ࠪࡨࡪࡹࡩࡳࡧࡧࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠪᜬ")][bstack111l11_opy_ (u"ࠫ࡬ࡵ࡯ࡨ࠼ࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩᜭ")] = {}
        if bstack111l11_opy_ (u"ࠬࡧࡲࡨࡵࠪᜮ") in bstack11ll11ll11l_opy_:
          if bstack111l11_opy_ (u"࠭ࡡࡳࡩࡶࠫᜯ") not in bstack1l111llll_opy_[bstack111l11_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧᜰ")][bstack111l11_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ᜱ")]:
            bstack1l111llll_opy_[bstack111l11_opy_ (u"ࠩࡧࡩࡸ࡯ࡲࡦࡦࡢࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠩᜲ")][bstack111l11_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨᜳ")][bstack111l11_opy_ (u"ࠫࡦࡸࡧࡴ᜴ࠩ")] = []
          for arg in bstack11ll11ll11l_opy_[bstack111l11_opy_ (u"ࠬࡧࡲࡨࡵࠪ᜵")]:
            if arg not in bstack1l111llll_opy_[bstack111l11_opy_ (u"࠭ࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠭᜶")][bstack111l11_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬ᜷")][bstack111l11_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭᜸")]:
              bstack1l111llll_opy_[bstack111l11_opy_ (u"ࠩࡧࡩࡸ࡯ࡲࡦࡦࡢࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠩ᜹")][bstack111l11_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨ᜺")][bstack111l11_opy_ (u"ࠫࡦࡸࡧࡴࠩ᜻")].append(arg)
        if bstack111l11_opy_ (u"ࠬ࡫ࡸࡵࡧࡱࡷ࡮ࡵ࡮ࡴࠩ᜼") in bstack11ll11ll11l_opy_:
          if bstack111l11_opy_ (u"࠭ࡥࡹࡶࡨࡲࡸ࡯࡯࡯ࡵࠪ᜽") not in bstack1l111llll_opy_[bstack111l11_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧ᜾")][bstack111l11_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭᜿")]:
            bstack1l111llll_opy_[bstack111l11_opy_ (u"ࠩࡧࡩࡸ࡯ࡲࡦࡦࡢࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠩᝀ")][bstack111l11_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨᝁ")][bstack111l11_opy_ (u"ࠫࡪࡾࡴࡦࡰࡶ࡭ࡴࡴࡳࠨᝂ")] = []
          for ext in bstack11ll11ll11l_opy_[bstack111l11_opy_ (u"ࠬ࡫ࡸࡵࡧࡱࡷ࡮ࡵ࡮ࡴࠩᝃ")]:
            if ext not in bstack1l111llll_opy_[bstack111l11_opy_ (u"࠭ࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠭ᝄ")][bstack111l11_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬᝅ")][bstack111l11_opy_ (u"ࠨࡧࡻࡸࡪࡴࡳࡪࡱࡱࡷࠬᝆ")]:
              bstack1l111llll_opy_[bstack111l11_opy_ (u"ࠩࡧࡩࡸ࡯ࡲࡦࡦࡢࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠩᝇ")][bstack111l11_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨᝈ")][bstack111l11_opy_ (u"ࠫࡪࡾࡴࡦࡰࡶ࡭ࡴࡴࡳࠨᝉ")].append(ext)
        if bstack111l11_opy_ (u"ࠬࡶࡲࡦࡨࡶࠫᝊ") in bstack11ll11ll11l_opy_:
          if bstack111l11_opy_ (u"࠭ࡰࡳࡧࡩࡷࠬᝋ") not in bstack1l111llll_opy_[bstack111l11_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧᝌ")][bstack111l11_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ᝍ")]:
            bstack1l111llll_opy_[bstack111l11_opy_ (u"ࠩࡧࡩࡸ࡯ࡲࡦࡦࡢࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠩᝎ")][bstack111l11_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨᝏ")][bstack111l11_opy_ (u"ࠫࡵࡸࡥࡧࡵࠪᝐ")] = {}
          bstack11ll1ll1lll_opy_(bstack1l111llll_opy_[bstack111l11_opy_ (u"ࠬࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬᝑ")][bstack111l11_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫᝒ")][bstack111l11_opy_ (u"ࠧࡱࡴࡨࡪࡸ࠭ᝓ")],
                    bstack11ll11ll11l_opy_[bstack111l11_opy_ (u"ࠨࡲࡵࡩ࡫ࡹࠧ᝔")])
        os.environ[bstack111l11_opy_ (u"ࠩࡌࡗࡤࡔࡏࡏࡡࡅࡗ࡙ࡇࡃࡌࡡࡌࡒࡋࡘࡁࡠࡃ࠴࠵࡞ࡥࡓࡆࡕࡖࡍࡔࡔࠧ᝕")] = bstack111l11_opy_ (u"ࠪࡸࡷࡻࡥࠨ᝖")
        return bstack1l111llll_opy_
      else:
        chrome_options = None
        if isinstance(bstack1l111llll_opy_, ChromeOptions):
          chrome_options = bstack1l111llll_opy_
        elif isinstance(bstack1l111llll_opy_, dict):
          for value in bstack1l111llll_opy_.values():
            if isinstance(value, ChromeOptions):
              chrome_options = value
              break
        if chrome_options is None:
          chrome_options = ChromeOptions()
          if isinstance(bstack1l111llll_opy_, dict):
            bstack1l111llll_opy_[bstack111l11_opy_ (u"ࠫࡴࡶࡴࡪࡱࡱࡷࠬ᝗")] = chrome_options
          else:
            bstack1l111llll_opy_ = chrome_options
        if bstack11ll11ll11l_opy_ is not None:
          if bstack111l11_opy_ (u"ࠬࡧࡲࡨࡵࠪ᝘") in bstack11ll11ll11l_opy_:
                bstack11ll1ll1l11_opy_ = chrome_options.arguments or []
                new_args = bstack11ll11ll11l_opy_[bstack111l11_opy_ (u"࠭ࡡࡳࡩࡶࠫ᝙")]
                for arg in new_args:
                    if arg not in bstack11ll1ll1l11_opy_:
                        chrome_options.add_argument(arg)
          if bstack111l11_opy_ (u"ࠧࡦࡺࡷࡩࡳࡹࡩࡰࡰࡶࠫ᝚") in bstack11ll11ll11l_opy_:
                existing_extensions = chrome_options.experimental_options.get(bstack111l11_opy_ (u"ࠨࡧࡻࡸࡪࡴࡳࡪࡱࡱࡷࠬ᝛"), [])
                bstack11ll1ll1111_opy_ = bstack11ll11ll11l_opy_[bstack111l11_opy_ (u"ࠩࡨࡼࡹ࡫࡮ࡴ࡫ࡲࡲࡸ࠭᝜")]
                for extension in bstack11ll1ll1111_opy_:
                    if extension not in existing_extensions:
                        chrome_options.add_encoded_extension(extension)
          if bstack111l11_opy_ (u"ࠪࡴࡷ࡫ࡦࡴࠩ᝝") in bstack11ll11ll11l_opy_:
                bstack11ll11ll111_opy_ = chrome_options.experimental_options.get(bstack111l11_opy_ (u"ࠫࡵࡸࡥࡧࡵࠪ᝞"), {})
                bstack11ll1l11ll1_opy_ = bstack11ll11ll11l_opy_[bstack111l11_opy_ (u"ࠬࡶࡲࡦࡨࡶࠫ᝟")]
                bstack11ll1ll1lll_opy_(bstack11ll11ll111_opy_, bstack11ll1l11ll1_opy_)
                chrome_options.add_experimental_option(bstack111l11_opy_ (u"࠭ࡰࡳࡧࡩࡷࠬᝠ"), bstack11ll11ll111_opy_)
        os.environ[bstack111l11_opy_ (u"ࠧࡊࡕࡢࡒࡔࡔ࡟ࡃࡕࡗࡅࡈࡑ࡟ࡊࡐࡉࡖࡆࡥࡁ࠲࠳࡜ࡣࡘࡋࡓࡔࡋࡒࡒࠬᝡ")] = bstack111l11_opy_ (u"ࠨࡶࡵࡹࡪ࠭ᝢ")
        return bstack1l111llll_opy_
    except Exception as e:
      logger.error(bstack111l11_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫࡭ࡱ࡫ࠠࡢࡦࡧ࡭ࡳ࡭ࠠ࡯ࡱࡱ࠱ࡇ࡙ࠠࡪࡰࡩࡶࡦࠦࡡ࠲࠳ࡼࠤࡨ࡮ࡲࡰ࡯ࡨࠤࡴࡶࡴࡪࡱࡱࡷ࠿ࠦࠢᝣ") + str(e))
      return bstack1l111llll_opy_