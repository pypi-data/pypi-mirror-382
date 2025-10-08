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
import subprocess
import threading
import time
import sys
import grpc
import os
from browserstack_sdk import sdk_pb2_grpc
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1llllllllll_opy_ import bstack1111111111_opy_
from browserstack_sdk.sdk_cli.bstack1lll111ll1l_opy_ import bstack1ll1ll1lll1_opy_
from browserstack_sdk.sdk_cli.bstack1lll11l1lll_opy_ import bstack1lll1l11l1l_opy_
from browserstack_sdk.sdk_cli.bstack1ll1l1l11l1_opy_ import bstack1lll1ll1l11_opy_
from browserstack_sdk.sdk_cli.bstack1ll1ll111ll_opy_ import bstack1ll1l1llll1_opy_
from browserstack_sdk.sdk_cli.bstack1ll1lll1l1l_opy_ import bstack1lll11l111l_opy_
from browserstack_sdk.sdk_cli.bstack1ll1l1l1lll_opy_ import bstack1lll111lll1_opy_
from browserstack_sdk.sdk_cli.bstack1lll1ll1l1l_opy_ import bstack1lll1l1l1ll_opy_
from browserstack_sdk.sdk_cli.bstack1lll11l1ll1_opy_ import bstack1ll1llllll1_opy_
from browserstack_sdk.sdk_cli.bstack1llll11111l_opy_ import bstack1lll111l1ll_opy_
from browserstack_sdk.sdk_cli.bstack1lll11l1_opy_ import bstack1lll11l1_opy_, bstack1l111l1l11_opy_, bstack11l11ll111_opy_
from browserstack_sdk.sdk_cli.pytest_bdd_framework import PytestBDDFramework
from browserstack_sdk.sdk_cli.bstack1lll11lll11_opy_ import bstack1ll1lll11ll_opy_
from browserstack_sdk.sdk_cli.bstack1ll1l1ll111_opy_ import bstack1ll1ll1l11l_opy_
from browserstack_sdk.sdk_cli.bstack1lllll11l1l_opy_ import bstack1lllll1l1l1_opy_
from browserstack_sdk.sdk_cli.bstack1ll1ll11l11_opy_ import bstack1ll1ll11111_opy_
from bstack_utils.helper import Notset, bstack1lll111l111_opy_, get_cli_dir, bstack1lll11ll1l1_opy_, bstack11l11l111_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework
from browserstack_sdk.sdk_cli.utils.bstack1lll1l1lll1_opy_ import bstack1lll1l1l1l1_opy_
from browserstack_sdk.sdk_cli.utils.bstack11l11l11l_opy_ import bstack11llll11ll_opy_
from bstack_utils.helper import Notset, bstack1lll111l111_opy_, get_cli_dir, bstack1lll11ll1l1_opy_, bstack11l11l111_opy_, bstack11ll1llll_opy_, bstack11l1l1l1_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1lll11ll111_opy_, bstack1lll1llll1l_opy_, bstack1lll1lll111_opy_, bstack1ll1lll1111_opy_
from browserstack_sdk.sdk_cli.bstack1lllll11l1l_opy_ import bstack1lllll1ll1l_opy_, bstack1llllll111l_opy_, bstack1llll1l111l_opy_
from bstack_utils.constants import *
from bstack_utils.bstack1l1l1ll11l_opy_ import bstack11l1l11l1l_opy_
from bstack_utils import bstack11l1l1111_opy_
from typing import Any, List, Union, Dict
import traceback
from google.protobuf.json_format import MessageToDict
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
from functools import wraps
from bstack_utils.measure import measure
from bstack_utils.messages import bstack11l11llll1_opy_, bstack1ll1lll1l_opy_
logger = bstack11l1l1111_opy_.get_logger(__name__, bstack11l1l1111_opy_.bstack1ll1ll11l1l_opy_())
def bstack1lll1l111l1_opy_(bs_config):
    bstack1ll1ll1llll_opy_ = None
    bstack1ll1l1lll1l_opy_ = None
    try:
        bstack1ll1l1lll1l_opy_ = get_cli_dir()
        bstack1ll1ll1llll_opy_ = bstack1lll11ll1l1_opy_(bstack1ll1l1lll1l_opy_)
        bstack1lll1l11l11_opy_ = bstack1lll111l111_opy_(bstack1ll1ll1llll_opy_, bstack1ll1l1lll1l_opy_, bs_config)
        bstack1ll1ll1llll_opy_ = bstack1lll1l11l11_opy_ if bstack1lll1l11l11_opy_ else bstack1ll1ll1llll_opy_
        if not bstack1ll1ll1llll_opy_:
            raise ValueError(bstack111l11_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡩ࡭ࡳࡪࠠࡔࡆࡎࡣࡈࡒࡉࡠࡄࡌࡒࡤࡖࡁࡕࡊࠥႴ"))
    except Exception as ex:
        logger.debug(bstack111l11_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡷࡩ࡫࡯ࡩࠥࡪ࡯ࡸࡰ࡯ࡳࡦࡪࡩ࡯ࡩࠣࡸ࡭࡫ࠠ࡭ࡣࡷࡩࡸࡺࠠࡣ࡫ࡱࡥࡷࡿࠠࡼࡿࠥႵ").format(ex))
        bstack1ll1ll1llll_opy_ = os.environ.get(bstack111l11_opy_ (u"ࠣࡕࡇࡏࡤࡉࡌࡊࡡࡅࡍࡓࡥࡐࡂࡖࡋࠦႶ"))
        if bstack1ll1ll1llll_opy_:
            logger.debug(bstack111l11_opy_ (u"ࠤࡉࡥࡱࡲࡩ࡯ࡩࠣࡦࡦࡩ࡫ࠡࡶࡲࠤࡘࡊࡋࡠࡅࡏࡍࡤࡈࡉࡏࡡࡓࡅ࡙ࡎࠠࡧࡴࡲࡱࠥ࡫࡮ࡷ࡫ࡵࡳࡳࡳࡥ࡯ࡶ࠽ࠤࠧႷ") + str(bstack1ll1ll1llll_opy_) + bstack111l11_opy_ (u"ࠥࠦႸ"))
        else:
            logger.debug(bstack111l11_opy_ (u"ࠦࡓࡵࠠࡷࡣ࡯࡭ࡩࠦࡓࡅࡍࡢࡇࡑࡏ࡟ࡃࡋࡑࡣࡕࡇࡔࡉࠢࡩࡳࡺࡴࡤࠡ࡫ࡱࠤࡪࡴࡶࡪࡴࡲࡲࡲ࡫࡮ࡵ࠽ࠣࡷࡪࡺࡵࡱࠢࡰࡥࡾࠦࡢࡦࠢ࡬ࡲࡨࡵ࡭ࡱ࡮ࡨࡸࡪ࠴ࠢႹ"))
    return bstack1ll1ll1llll_opy_, bstack1ll1l1lll1l_opy_
bstack1lll11ll11l_opy_ = bstack111l11_opy_ (u"ࠧ࠿࠹࠺࠻ࠥႺ")
bstack1ll1ll1ll11_opy_ = bstack111l11_opy_ (u"ࠨࡲࡦࡣࡧࡽࠧႻ")
bstack1ll1l1l1ll1_opy_ = bstack111l11_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡃࡍࡋࡢࡆࡎࡔ࡟ࡔࡇࡖࡗࡎࡕࡎࡠࡋࡇࠦႼ")
bstack1lll1ll1lll_opy_ = bstack111l11_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡄࡎࡌࡣࡇࡏࡎࡠࡎࡌࡗ࡙ࡋࡎࡠࡃࡇࡈࡗࠨႽ")
bstack11111111_opy_ = bstack111l11_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡃࡘࡘࡔࡓࡁࡕࡋࡒࡒࠧႾ")
bstack1ll1l1ll1ll_opy_ = re.compile(bstack111l11_opy_ (u"ࡵࠦ࠭ࡅࡩࠪ࠰࠭ࠬࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡿࡆࡘ࠯࠮ࠫࠤႿ"))
bstack1lll1l1llll_opy_ = bstack111l11_opy_ (u"ࠦࡩ࡫ࡶࡦ࡮ࡲࡴࡲ࡫࡮ࡵࠤჀ")
bstack1lll11lll1l_opy_ = bstack111l11_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡋࡕࡒࡄࡇࡢࡊࡆࡒࡌࡃࡃࡆࡏࠧჁ")
bstack1lll11111ll_opy_ = [
    bstack1l111l1l11_opy_.bstack111111l1_opy_,
    bstack1l111l1l11_opy_.CONNECT,
    bstack1l111l1l11_opy_.bstack1111lll1_opy_,
]
class SDKCLI:
    _1ll1l11lll1_opy_ = None
    process: Union[None, Any]
    bstack1ll1lll1ll1_opy_: bool
    bstack1lll1llll11_opy_: bool
    bstack1llll11l1ll_opy_: bool
    bin_session_id: Union[None, str]
    cli_bin_session_id: Union[None, str]
    cli_listen_addr: Union[None, str]
    bstack1ll1ll11ll1_opy_: Union[None, grpc.Channel]
    bstack1lll1ll111l_opy_: str
    test_framework: TestFramework
    bstack1lllll11l1l_opy_: bstack1lllll1l1l1_opy_
    session_framework: str
    config: Union[None, Dict[str, Any]]
    bstack1ll1lllll1l_opy_: bstack1lll111l1ll_opy_
    accessibility: bstack1lll1l11l1l_opy_
    bstack11l11l11l_opy_: bstack11llll11ll_opy_
    ai: bstack1lll1ll1l11_opy_
    bstack1lll1l1111l_opy_: bstack1ll1l1llll1_opy_
    bstack1ll1l11llll_opy_: List[bstack1ll1ll1lll1_opy_]
    config_testhub: Any
    config_observability: Any
    config_accessibility: Any
    bstack1lll1ll11l1_opy_: Any
    bstack1ll1lllllll_opy_: Dict[str, timedelta]
    bstack1lll1l11111_opy_: str
    bstack1llllllllll_opy_: bstack1111111111_opy_
    def __new__(cls):
        if not cls._1ll1l11lll1_opy_:
            cls._1ll1l11lll1_opy_ = super(SDKCLI, cls).__new__(cls)
        return cls._1ll1l11lll1_opy_
    def __init__(self):
        self.process = None
        self.bstack1ll1lll1ll1_opy_ = False
        self.bstack1ll1ll11ll1_opy_ = None
        self.bstack1ll1ll1ll1l_opy_ = None
        self.cli_bin_session_id = None
        self.cli_listen_addr = os.environ.get(bstack1lll1ll1lll_opy_, None)
        self.bstack1lll111l11l_opy_ = os.environ.get(bstack1ll1l1l1ll1_opy_, bstack111l11_opy_ (u"ࠨࠢჂ")) == bstack111l11_opy_ (u"ࠢࠣჃ")
        self.bstack1lll1llll11_opy_ = False
        self.bstack1llll11l1ll_opy_ = False
        self.config = None
        self.config_testhub = None
        self.config_observability = None
        self.config_accessibility = None
        self.bstack1lll1ll11l1_opy_ = None
        self.test_framework = None
        self.bstack1lllll11l1l_opy_ = None
        self.bstack1lll1ll111l_opy_=bstack111l11_opy_ (u"ࠣࠤჄ")
        self.session_framework = None
        self.logger = bstack11l1l1111_opy_.get_logger(self.__class__.__name__, bstack11l1l1111_opy_.bstack1ll1ll11l1l_opy_())
        self.bstack1ll1lllllll_opy_ = defaultdict(lambda: timedelta(microseconds=0))
        self.bstack1llllllllll_opy_ = bstack1111111111_opy_()
        self.bstack1lll11lllll_opy_ = None
        self.bstack1llll11l1l1_opy_ = None
        self.bstack1ll1lllll1l_opy_ = None
        self.accessibility = None
        self.ai = None
        self.percy = None
        self.bstack1ll1l11llll_opy_ = []
    def bstack1lllll11ll_opy_(self):
        return os.environ.get(bstack11111111_opy_).lower().__eq__(bstack111l11_opy_ (u"ࠤࡷࡶࡺ࡫ࠢჅ"))
    def is_enabled(self, config):
        if os.environ.get(bstack1lll11lll1l_opy_, bstack111l11_opy_ (u"ࠪࠫ჆")).lower() in [bstack111l11_opy_ (u"ࠫࡹࡸࡵࡦࠩჇ"), bstack111l11_opy_ (u"ࠬ࠷ࠧ჈"), bstack111l11_opy_ (u"࠭ࡹࡦࡵࠪ჉")]:
            self.logger.debug(bstack111l11_opy_ (u"ࠢࡇࡱࡵࡧ࡮ࡴࡧࠡࡨࡤࡰࡱࡨࡡࡤ࡭ࠣࡱࡴࡪࡥࠡࡦࡸࡩࠥࡺ࡯ࠡࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡇࡑࡕࡇࡊࡥࡆࡂࡎࡏࡆࡆࡉࡋࠡࡧࡱࡺ࡮ࡸ࡯࡯࡯ࡨࡲࡹࠦࡶࡢࡴ࡬ࡥࡧࡲࡥࠣ჊"))
            os.environ[bstack111l11_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡃࡋࡑࡅࡗ࡟࡟ࡊࡕࡢࡖ࡚ࡔࡎࡊࡐࡊࠦ჋")] = bstack111l11_opy_ (u"ࠤࡉࡥࡱࡹࡥࠣ჌")
            return False
        if bstack111l11_opy_ (u"ࠪࡸࡺࡸࡢࡰࡕࡦࡥࡱ࡫ࠧჍ") in config and str(config[bstack111l11_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨ჎")]).lower() != bstack111l11_opy_ (u"ࠬ࡬ࡡ࡭ࡵࡨࠫ჏"):
            return False
        bstack1ll1l1l11ll_opy_ = [bstack111l11_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹࠨა"), bstack111l11_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠦბ")]
        bstack1llll11ll11_opy_ = config.get(bstack111l11_opy_ (u"ࠣࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠦგ")) in bstack1ll1l1l11ll_opy_ or os.environ.get(bstack111l11_opy_ (u"ࠩࡉࡖࡆࡓࡅࡘࡑࡕࡏࡤ࡛ࡓࡆࡆࠪდ")) in bstack1ll1l1l11ll_opy_
        os.environ[bstack111l11_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡅࡍࡓࡇࡒ࡚ࡡࡌࡗࡤࡘࡕࡏࡐࡌࡒࡌࠨე")] = str(bstack1llll11ll11_opy_) # bstack1lll1ll1111_opy_ bstack1ll1llll111_opy_ VAR to bstack1ll1ll1l111_opy_ is binary running
        return bstack1llll11ll11_opy_
    def bstack11l1ll1l1l_opy_(self):
        for event in bstack1lll11111ll_opy_:
            bstack1lll11l1_opy_.register(
                event, lambda event_name, *args, **kwargs: bstack1lll11l1_opy_.logger.debug(bstack111l11_opy_ (u"ࠦࢀ࡫ࡶࡦࡰࡷࡣࡳࡧ࡭ࡦࡿࠣࡁࡃࠦࡻࡢࡴࡪࡷࢂࠦࠢვ") + str(kwargs) + bstack111l11_opy_ (u"ࠧࠨზ"))
            )
        bstack1lll11l1_opy_.register(bstack1l111l1l11_opy_.bstack111111l1_opy_, self.__1lll1l1l11l_opy_)
        bstack1lll11l1_opy_.register(bstack1l111l1l11_opy_.CONNECT, self.__1llll111lll_opy_)
        bstack1lll11l1_opy_.register(bstack1l111l1l11_opy_.bstack1111lll1_opy_, self.__1ll1llll1l1_opy_)
        bstack1lll11l1_opy_.register(bstack1l111l1l11_opy_.bstack11lllll1l1_opy_, self.__1ll1l1l1111_opy_)
    def bstack111lllll1l_opy_(self):
        return not self.bstack1lll111l11l_opy_ and os.environ.get(bstack1ll1l1l1ll1_opy_, bstack111l11_opy_ (u"ࠨࠢთ")) != bstack111l11_opy_ (u"ࠢࠣი")
    def is_running(self):
        if self.bstack1lll111l11l_opy_:
            return self.bstack1ll1lll1ll1_opy_
        else:
            return bool(self.bstack1ll1ll11ll1_opy_)
    def bstack1lll111111l_opy_(self, module):
        return any(isinstance(m, module) for m in self.bstack1ll1l11llll_opy_) and cli.is_running()
    def __1ll1lll111l_opy_(self, bstack1llll1111ll_opy_=10):
        if self.bstack1ll1ll1ll1l_opy_:
            return
        bstack11l1ll1l_opy_ = datetime.now()
        cli_listen_addr = os.environ.get(bstack1lll1ll1lll_opy_, self.cli_listen_addr)
        self.logger.debug(bstack111l11_opy_ (u"ࠣ࡝ࠥკ") + str(id(self)) + bstack111l11_opy_ (u"ࠤࡠࠤࡨࡵ࡮࡯ࡧࡦࡸ࡮ࡴࡧࠣლ"))
        channel = grpc.insecure_channel(cli_listen_addr, options=[(bstack111l11_opy_ (u"ࠥ࡫ࡷࡶࡣ࠯ࡧࡱࡥࡧࡲࡥࡠࡪࡷࡸࡵࡥࡰࡳࡱࡻࡽࠧმ"), 0), (bstack111l11_opy_ (u"ࠦ࡬ࡸࡰࡤ࠰ࡨࡲࡦࡨ࡬ࡦࡡ࡫ࡸࡹࡶࡳࡠࡲࡵࡳࡽࡿࠢნ"), 0)])
        grpc.channel_ready_future(channel).result(timeout=bstack1llll1111ll_opy_)
        self.bstack1ll1ll11ll1_opy_ = channel
        self.bstack1ll1ll1ll1l_opy_ = sdk_pb2_grpc.SDKStub(self.bstack1ll1ll11ll1_opy_)
        self.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠧ࡭ࡲࡱࡥ࠽ࡧࡴࡴ࡮ࡦࡥࡷࠦო"), datetime.now() - bstack11l1ll1l_opy_)
        self.cli_listen_addr = cli_listen_addr
        os.environ[bstack1lll1ll1lll_opy_] = self.cli_listen_addr
        self.logger.debug(bstack111l11_opy_ (u"ࠨ࡛ࡼ࡫ࡧࠬࡸ࡫࡬ࡧࠫࢀࡡࠥࡩ࡯࡯ࡰࡨࡧࡹ࡫ࡤ࠻ࠢ࡬ࡷࡤࡩࡨࡪ࡮ࡧࡣࡵࡸ࡯ࡤࡧࡶࡷࡂࠨპ") + str(self.bstack111lllll1l_opy_()) + bstack111l11_opy_ (u"ࠢࠣჟ"))
    def __1ll1llll1l1_opy_(self, event_name):
        if self.bstack111lllll1l_opy_():
            self.logger.debug(bstack111l11_opy_ (u"ࠣࡥ࡫࡭ࡱࡪ࠭ࡱࡴࡲࡧࡪࡹࡳ࠻ࠢࡶࡸࡴࡶࡰࡪࡰࡪࠤࡈࡒࡉࠣრ"))
        self.__1lll1llllll_opy_()
    def __1ll1l1l1111_opy_(self, event_name, bstack1ll1llll11l_opy_ = None, exit_code=1):
        if exit_code == 1:
            self.logger.error(bstack111l11_opy_ (u"ࠤࡖࡳࡲ࡫ࡴࡩ࡫ࡱ࡫ࠥࡽࡥ࡯ࡶࠣࡻࡷࡵ࡮ࡨࠤს"))
        bstack1llll111l1l_opy_ = Path(bstack111111ll11_opy_ (u"ࠥࡿࡸ࡫࡬ࡧ࠰ࡦࡰ࡮ࡥࡤࡪࡴࢀ࠳ࡺࡴࡨࡢࡰࡧࡰࡪࡪࡅࡳࡴࡲࡶࡸ࠴ࡪࡴࡱࡱࠦტ"))
        if self.bstack1ll1l1lll1l_opy_ and bstack1llll111l1l_opy_.exists():
            with open(bstack1llll111l1l_opy_, bstack111l11_opy_ (u"ࠫࡷ࠭უ"), encoding=bstack111l11_opy_ (u"ࠬࡻࡴࡧ࠯࠻ࠫფ")) as fp:
                data = json.load(fp)
                try:
                    bstack11ll1llll_opy_(bstack111l11_opy_ (u"࠭ࡐࡐࡕࡗࠫქ"), bstack11l1l11l1l_opy_(bstack1lllll1l11_opy_), data, {
                        bstack111l11_opy_ (u"ࠧࡢࡷࡷ࡬ࠬღ"): (self.config[bstack111l11_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪყ")], self.config[bstack111l11_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬშ")])
                    })
                except Exception as e:
                    logger.debug(bstack1ll1lll1l_opy_.format(str(e)))
            bstack1llll111l1l_opy_.unlink()
        sys.exit(exit_code)
    @measure(event_name=EVENTS.bstack1lll1lll1l1_opy_, stage=STAGE.bstack111lllll1_opy_)
    def __1lll1l1l11l_opy_(self, event_name: str, data):
        from bstack_utils.bstack1l1l1l1111_opy_ import bstack1ll1l1ll1l1_opy_
        self.bstack1lll1ll111l_opy_, self.bstack1ll1l1lll1l_opy_ = bstack1lll1l111l1_opy_(data.bs_config)
        os.environ[bstack111l11_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡ࡚ࡖࡎ࡚ࡁࡃࡎࡈࡣࡉࡏࡒࠨჩ")] = self.bstack1ll1l1lll1l_opy_
        if not self.bstack1lll1ll111l_opy_ or not self.bstack1ll1l1lll1l_opy_:
            raise ValueError(bstack111l11_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡧ࡫ࡱࡨࠥࡺࡨࡦࠢࡖࡈࡐࠦࡃࡍࡋࠣࡦ࡮ࡴࡡࡳࡻࠥც"))
        if self.bstack111lllll1l_opy_():
            self.__1llll111lll_opy_(event_name, bstack11l11ll111_opy_())
            return
        try:
            bstack1ll1l1ll1l1_opy_.end(EVENTS.bstack11lll11l1_opy_.value, EVENTS.bstack11lll11l1_opy_.value + bstack111l11_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧძ"), EVENTS.bstack11lll11l1_opy_.value + bstack111l11_opy_ (u"ࠨ࠺ࡦࡰࡧࠦწ"), status=True, failure=None, test_name=None)
            logger.debug(bstack111l11_opy_ (u"ࠢࡄࡱࡰࡴࡱ࡫ࡴࡦࠢࡖࡈࡐࠦࡓࡦࡶࡸࡴ࠳ࠨჭ"))
        except Exception as e:
            logger.debug(bstack111l11_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࡼ࡮ࡩ࡭ࡧࠣࡱࡦࡸ࡫ࡪࡰࡪࠤࡰ࡫ࡹࠡ࡯ࡨࡸࡷ࡯ࡣࡴࠢࡾࢁࠧხ").format(e))
        start = datetime.now()
        is_started = self.__1lll1ll11ll_opy_()
        self.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠤࡶࡴࡦࡽ࡮ࡠࡶ࡬ࡱࡪࠨჯ"), datetime.now() - start)
        if is_started:
            start = datetime.now()
            self.__1ll1lll111l_opy_()
            self.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠥࡧࡴࡴ࡮ࡦࡥࡷࡣࡹ࡯࡭ࡦࠤჰ"), datetime.now() - start)
            start = datetime.now()
            self.__1ll1ll1l1ll_opy_(data)
            self.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠦࡸࡺࡡࡳࡶࡢࡷࡪࡹࡳࡪࡱࡱࡣࡹ࡯࡭ࡦࠤჱ"), datetime.now() - start)
    @measure(event_name=EVENTS.bstack1lll111l1l1_opy_, stage=STAGE.bstack111lllll1_opy_)
    def __1llll111lll_opy_(self, event_name: str, data: bstack11l11ll111_opy_):
        if not self.bstack111lllll1l_opy_():
            self.logger.debug(bstack111l11_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡥࡲࡲࡳ࡫ࡣࡵ࠼ࠣࡲࡴࡺࠠࡢࠢࡦ࡬࡮ࡲࡤ࠮ࡲࡵࡳࡨ࡫ࡳࡴࠤჲ"))
            return
        bin_session_id = os.environ.get(bstack1ll1l1l1ll1_opy_)
        start = datetime.now()
        self.__1ll1lll111l_opy_()
        self.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠨࡣࡰࡰࡱࡩࡨࡺ࡟ࡵ࡫ࡰࡩࠧჳ"), datetime.now() - start)
        self.cli_bin_session_id = bin_session_id
        self.logger.debug(bstack111l11_opy_ (u"ࠢ࡜ࡽ࡬ࡨ࠭ࡹࡥ࡭ࡨࠬࢁࡢࠦࡣࡩ࡫࡯ࡨ࠲ࡶࡲࡰࡥࡨࡷࡸࡀࠠࡤࡱࡱࡲࡪࡩࡴࡦࡦࠣࡸࡴࠦࡥࡹ࡫ࡶࡸ࡮ࡴࡧࠡࡅࡏࡍࠥࠨჴ") + str(bin_session_id) + bstack111l11_opy_ (u"ࠣࠤჵ"))
        start = datetime.now()
        self.__1lll1l11lll_opy_()
        self.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠤࡶࡸࡦࡸࡴࡠࡵࡨࡷࡸ࡯࡯࡯ࡡࡷ࡭ࡲ࡫ࠢჶ"), datetime.now() - start)
    def __1lll1111lll_opy_(self):
        if not self.bstack1ll1ll1ll1l_opy_ or not self.cli_bin_session_id:
            self.logger.debug(bstack111l11_opy_ (u"ࠥࡧࡦࡴ࡮ࡰࡶࠣࡧࡴࡴࡦࡪࡩࡸࡶࡪࠦ࡭ࡰࡦࡸࡰࡪࡹࠢჷ"))
            return
        bstack1llll11ll1l_opy_ = {
            bstack111l11_opy_ (u"ࠦࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠣჸ"): (bstack1lll1l1l1ll_opy_, bstack1ll1llllll1_opy_, bstack1ll1ll11111_opy_),
            bstack111l11_opy_ (u"ࠧࡹࡥ࡭ࡧࡱ࡭ࡺࡳࠢჹ"): (bstack1lll11l111l_opy_, bstack1lll111lll1_opy_, bstack1ll1ll1l11l_opy_),
        }
        if not self.bstack1lll11lllll_opy_ and self.session_framework in bstack1llll11ll1l_opy_:
            bstack1ll1l1l1l11_opy_, bstack1lll11l1l11_opy_, bstack1lll1111l11_opy_ = bstack1llll11ll1l_opy_[self.session_framework]
            bstack1ll1l11ll1l_opy_ = bstack1lll11l1l11_opy_()
            self.bstack1llll11l1l1_opy_ = bstack1ll1l11ll1l_opy_
            self.bstack1lll11lllll_opy_ = bstack1lll1111l11_opy_
            self.bstack1ll1l11llll_opy_.append(bstack1ll1l11ll1l_opy_)
            self.bstack1ll1l11llll_opy_.append(bstack1ll1l1l1l11_opy_(self.bstack1llll11l1l1_opy_))
        if not self.bstack1ll1lllll1l_opy_ and self.config_observability and self.config_observability.success: # bstack1lll1l1ll11_opy_
            self.bstack1ll1lllll1l_opy_ = bstack1lll111l1ll_opy_(self.bstack1lll11lllll_opy_, self.bstack1llll11l1l1_opy_) # bstack1ll1llll1ll_opy_
            self.bstack1ll1l11llll_opy_.append(self.bstack1ll1lllll1l_opy_)
        if not self.accessibility and self.config_accessibility and self.config_accessibility.success:
            self.accessibility = bstack1lll1l11l1l_opy_(self.bstack1lll11lllll_opy_, self.bstack1llll11l1l1_opy_)
            self.bstack1ll1l11llll_opy_.append(self.accessibility)
        if not self.ai and isinstance(self.config, dict) and self.config.get(bstack111l11_opy_ (u"ࠨࡳࡦ࡮ࡩࡌࡪࡧ࡬ࠣჺ"), False) == True:
            self.ai = bstack1lll1ll1l11_opy_()
            self.bstack1ll1l11llll_opy_.append(self.ai)
        if not self.percy and self.bstack1lll1ll11l1_opy_ and self.bstack1lll1ll11l1_opy_.success:
            self.percy = bstack1ll1l1llll1_opy_(self.bstack1lll1ll11l1_opy_)
            self.bstack1ll1l11llll_opy_.append(self.percy)
        for mod in self.bstack1ll1l11llll_opy_:
            if not mod.bstack1lll1111111_opy_():
                mod.configure(self.bstack1ll1ll1ll1l_opy_, self.config, self.cli_bin_session_id, self.bstack1llllllllll_opy_)
    def __1lll11111l1_opy_(self):
        for mod in self.bstack1ll1l11llll_opy_:
            if mod.bstack1lll1111111_opy_():
                mod.configure(self.bstack1ll1ll1ll1l_opy_, None, None, None)
    @measure(event_name=EVENTS.bstack1lll11l1111_opy_, stage=STAGE.bstack111lllll1_opy_)
    def __1ll1ll1l1ll_opy_(self, data):
        if not self.cli_bin_session_id or self.bstack1lll1llll11_opy_:
            return
        self.__1ll1lll11l1_opy_(data)
        bstack11l1ll1l_opy_ = datetime.now()
        req = structs.StartBinSessionRequest()
        req.bin_session_id = self.cli_bin_session_id
        req.path_project = os.getcwd()
        req.language = bstack111l11_opy_ (u"ࠢࡱࡻࡷ࡬ࡴࡴࠢ჻")
        req.sdk_language = bstack111l11_opy_ (u"ࠣࡲࡼࡸ࡭ࡵ࡮ࠣჼ")
        req.path_config = data.path_config
        req.sdk_version = data.sdk_version
        req.test_framework = data.test_framework
        req.frameworks.extend(data.frameworks)
        req.framework_versions.update(data.framework_versions)
        req.env_vars.update({key: value for key, value in os.environ.items() if bool(bstack1ll1l1ll1ll_opy_.search(key))})
        req.cli_args.extend(sys.argv)
        try:
            self.logger.debug(bstack111l11_opy_ (u"ࠤ࡞ࠦჽ") + str(id(self)) + bstack111l11_opy_ (u"ࠥࡡࠥࡳࡡࡪࡰ࠰ࡴࡷࡵࡣࡦࡵࡶ࠾ࠥࡹࡴࡢࡴࡷࡣࡧ࡯࡮ࡠࡵࡨࡷࡸ࡯࡯࡯ࠤჾ"))
            r = self.bstack1ll1ll1ll1l_opy_.StartBinSession(req)
            self.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠦ࡬ࡸࡰࡤ࠼ࡶࡸࡦࡸࡴࡠࡤ࡬ࡲࡤࡹࡥࡴࡵ࡬ࡳࡳࠨჿ"), datetime.now() - bstack11l1ll1l_opy_)
            os.environ[bstack1ll1l1l1ll1_opy_] = r.bin_session_id
            self.__1lll1111l1l_opy_(r)
            self.__1lll1111lll_opy_()
            self.bstack1llllllllll_opy_.start()
            self.bstack1lll1llll11_opy_ = True
            self.logger.debug(bstack111l11_opy_ (u"ࠧࡡࠢᄀ") + str(id(self)) + bstack111l11_opy_ (u"ࠨ࡝ࠡ࡯ࡤ࡭ࡳ࠳ࡰࡳࡱࡦࡩࡸࡹ࠺ࠡࡥࡲࡲࡳ࡫ࡣࡵࡧࡧࠦᄁ"))
        except grpc.bstack1llll11l11l_opy_ as bstack1lll1l111ll_opy_:
            self.logger.error(bstack111l11_opy_ (u"ࠢ࡜ࡽ࡬ࡨ࠭ࡹࡥ࡭ࡨࠬࢁࡢࠦࡴࡪ࡯ࡨࡳࡪࡻࡴ࠮ࡧࡵࡶࡴࡸ࠺ࠡࠤᄂ") + str(bstack1lll1l111ll_opy_) + bstack111l11_opy_ (u"ࠣࠤᄃ"))
            traceback.print_exc()
            raise bstack1lll1l111ll_opy_
        except grpc.RpcError as e:
            self.logger.error(bstack111l11_opy_ (u"ࠤ࡞ࡿ࡮ࡪࠨࡴࡧ࡯ࡪ࠮ࢃ࡝ࠡࡴࡳࡧ࠲࡫ࡲࡳࡱࡵ࠾ࠥࠨᄄ") + str(e) + bstack111l11_opy_ (u"ࠥࠦᄅ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1ll1lllll11_opy_, stage=STAGE.bstack111lllll1_opy_)
    def __1lll1l11lll_opy_(self):
        if not self.bstack111lllll1l_opy_() or not self.cli_bin_session_id or self.bstack1llll11l1ll_opy_:
            return
        bstack11l1ll1l_opy_ = datetime.now()
        req = structs.ConnectBinSessionRequest()
        req.bin_session_id = self.cli_bin_session_id
        req.platform_index = int(os.environ.get(bstack111l11_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠫᄆ"), bstack111l11_opy_ (u"ࠬ࠶ࠧᄇ")))
        try:
            self.logger.debug(bstack111l11_opy_ (u"ࠨ࡛ࠣᄈ") + str(id(self)) + bstack111l11_opy_ (u"ࠢ࡞ࠢࡦ࡬࡮ࡲࡤ࠮ࡲࡵࡳࡨ࡫ࡳࡴ࠼ࠣࡧࡴࡴ࡮ࡦࡥࡷࡣࡧ࡯࡮ࡠࡵࡨࡷࡸ࡯࡯࡯ࠤᄉ"))
            r = self.bstack1ll1ll1ll1l_opy_.ConnectBinSession(req)
            self.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠣࡩࡵࡴࡨࡀࡣࡰࡰࡱࡩࡨࡺ࡟ࡣ࡫ࡱࡣࡸ࡫ࡳࡴ࡫ࡲࡲࠧᄊ"), datetime.now() - bstack11l1ll1l_opy_)
            self.__1lll1111l1l_opy_(r)
            self.__1lll1111lll_opy_()
            self.bstack1llllllllll_opy_.start()
            self.bstack1llll11l1ll_opy_ = True
            self.logger.debug(bstack111l11_opy_ (u"ࠤ࡞ࠦᄋ") + str(id(self)) + bstack111l11_opy_ (u"ࠥࡡࠥࡩࡨࡪ࡮ࡧ࠱ࡵࡸ࡯ࡤࡧࡶࡷ࠿ࠦࡣࡰࡰࡱࡩࡨࡺࡥࡥࠤᄌ"))
        except grpc.bstack1llll11l11l_opy_ as bstack1lll1l111ll_opy_:
            self.logger.error(bstack111l11_opy_ (u"ࠦࡠࢁࡩࡥࠪࡶࡩࡱ࡬ࠩࡾ࡟ࠣࡸ࡮ࡳࡥࡰࡧࡸࡸ࠲࡫ࡲࡳࡱࡵ࠾ࠥࠨᄍ") + str(bstack1lll1l111ll_opy_) + bstack111l11_opy_ (u"ࠧࠨᄎ"))
            traceback.print_exc()
            raise bstack1lll1l111ll_opy_
        except grpc.RpcError as e:
            self.logger.error(bstack111l11_opy_ (u"ࠨ࡛ࡼ࡫ࡧࠬࡸ࡫࡬ࡧࠫࢀࡡࠥࡸࡰࡤ࠯ࡨࡶࡷࡵࡲ࠻ࠢࠥᄏ") + str(e) + bstack111l11_opy_ (u"ࠢࠣᄐ"))
            traceback.print_exc()
            raise e
    def __1lll1111l1l_opy_(self, r):
        self.bstack1lll1111ll1_opy_(r)
        if not r.bin_session_id or not r.config or not isinstance(r.config, str):
            raise ValueError(bstack111l11_opy_ (u"ࠣࡷࡱࡩࡽࡶࡥࡤࡶࡨࡨࠥࡹࡥࡳࡸࡨࡶࠥࡸࡥࡴࡲࡲࡲࡸ࡫ࠢᄑ") + str(r))
        self.config = json.loads(r.config)
        if not self.config:
            raise ValueError(bstack111l11_opy_ (u"ࠤࡨࡱࡵࡺࡹࠡࡥࡲࡲ࡫࡯ࡧࠡࡨࡲࡹࡳࡪࠢᄒ"))
        self.session_framework = r.session_framework
        self.config_testhub = r.testhub
        self.config_observability = r.observability
        self.config_accessibility = r.accessibility
        bstack111l11_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠࡑࡧࡵࡧࡾࠦࡩࡴࠢࡶࡩࡳࡺࠠࡰࡰ࡯ࡽࠥࡧࡳࠡࡲࡤࡶࡹࠦ࡯ࡧࠢࡷ࡬ࡪࠦࠢࡄࡱࡱࡲࡪࡩࡴࡃ࡫ࡱࡗࡪࡹࡳࡪࡱࡱ࠰ࠧࠦࡡ࡯ࡦࠣࡸ࡭࡯ࡳࠡࡨࡸࡲࡨࡺࡩࡰࡰࠣ࡭ࡸࠦࡡ࡭ࡵࡲࠤࡺࡹࡥࡥࠢࡥࡽ࡙ࠥࡴࡢࡴࡷࡆ࡮ࡴࡓࡦࡵࡶ࡭ࡴࡴ࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࡗ࡬ࡪࡸࡥࡧࡱࡵࡩ࠱ࠦࡎࡰࡰࡨࠤ࡭ࡧ࡮ࡥ࡮࡬ࡲ࡬ࠦࡩࡴࠢ࡬ࡱࡵࡲࡥ࡮ࡧࡱࡸࡪࡪ࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠥࠦࠧᄓ")
        self.bstack1lll1ll11l1_opy_ = getattr(r, bstack111l11_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࠪᄔ"), None)
        self.cli_bin_session_id = r.bin_session_id
        os.environ[bstack111l11_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤࡐࡗࡕࠩᄕ")] = self.config_testhub.jwt
        os.environ[bstack111l11_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫᄖ")] = self.config_testhub.build_hashed_id
    def bstack1ll1ll1l1l1_opy_(event_name: EVENTS, stage: STAGE):
        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                if self.bstack1ll1lll1ll1_opy_:
                    return func(self, *args, **kwargs)
                @measure(event_name=event_name, stage=stage)
                def bstack1lll1l1l111_opy_(*a, **kw):
                    return func(self, *a, **kw)
                return bstack1lll1l1l111_opy_(*args, **kwargs)
            return wrapper
        return decorator
    @bstack1ll1ll1l1l1_opy_(event_name=EVENTS.bstack1lll1l1ll1l_opy_, stage=STAGE.bstack111lllll1_opy_)
    def __1lll1ll11ll_opy_(self, bstack1llll1111ll_opy_=10):
        if self.bstack1ll1lll1ll1_opy_:
            self.logger.debug(bstack111l11_opy_ (u"ࠢࡴࡶࡤࡶࡹࡀࠠࡢ࡮ࡵࡩࡦࡪࡹࠡࡴࡸࡲࡳ࡯࡮ࡨࠤᄗ"))
            return True
        self.logger.debug(bstack111l11_opy_ (u"ࠣࡵࡷࡥࡷࡺࠢᄘ"))
        if os.getenv(bstack111l11_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡅࡏࡍࡤࡋࡎࡗࠤᄙ")) == bstack1lll1l1llll_opy_:
            self.cli_bin_session_id = bstack1lll1l1llll_opy_
            self.cli_listen_addr = bstack111l11_opy_ (u"ࠥࡹࡳ࡯ࡸ࠻࠱ࡷࡱࡵ࠵ࡳࡥ࡭࠰ࡴࡱࡧࡴࡧࡱࡵࡱ࠲ࠫࡳ࠯ࡵࡲࡧࡰࠨᄚ") % (self.cli_bin_session_id)
            self.bstack1ll1lll1ll1_opy_ = True
            return True
        self.process = subprocess.Popen(
            [self.bstack1lll1ll111l_opy_, bstack111l11_opy_ (u"ࠦࡸࡪ࡫ࠣᄛ")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=dict(os.environ),
            text=True,
            universal_newlines=True, # bstack1lll111ll11_opy_ compat for text=True in bstack1ll1ll111l1_opy_ python
            encoding=bstack111l11_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦᄜ"),
            bufsize=1,
            close_fds=True,
        )
        bstack1llll11l111_opy_ = threading.Thread(target=self.__1llll1111l1_opy_, args=(bstack1llll1111ll_opy_,))
        bstack1llll11l111_opy_.start()
        bstack1llll11l111_opy_.join()
        if self.process.returncode is not None:
            self.logger.debug(bstack111l11_opy_ (u"ࠨ࡛ࡼ࡫ࡧࠬࡸ࡫࡬ࡧࠫࢀࡡࠥࡹࡰࡢࡹࡱ࠾ࠥࡸࡥࡵࡷࡵࡲࡨࡵࡤࡦ࠿ࡾࡷࡪࡲࡦ࠯ࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡵࡩࡹࡻࡲ࡯ࡥࡲࡨࡪࢃࠠࡰࡷࡷࡁࢀࡹࡥ࡭ࡨ࠱ࡴࡷࡵࡣࡦࡵࡶ࠲ࡸࡺࡤࡰࡷࡷ࠲ࡷ࡫ࡡࡥࠪࠬࢁࠥ࡫ࡲࡳ࠿ࠥᄝ") + str(self.process.stderr.read()) + bstack111l11_opy_ (u"ࠢࠣᄞ"))
        if not self.bstack1ll1lll1ll1_opy_:
            self.logger.debug(bstack111l11_opy_ (u"ࠣ࡝ࠥᄟ") + str(id(self)) + bstack111l11_opy_ (u"ࠤࡠࠤࡨࡲࡥࡢࡰࡸࡴࠧᄠ"))
            self.__1lll1llllll_opy_()
        self.logger.debug(bstack111l11_opy_ (u"ࠥ࡟ࢀ࡯ࡤࠩࡵࡨࡰ࡫࠯ࡽ࡞ࠢࡳࡶࡴࡩࡥࡴࡵࡢࡶࡪࡧࡤࡺ࠼ࠣࠦᄡ") + str(self.bstack1ll1lll1ll1_opy_) + bstack111l11_opy_ (u"ࠦࠧᄢ"))
        return self.bstack1ll1lll1ll1_opy_
    def __1llll1111l1_opy_(self, bstack1lll1ll1ll1_opy_=10):
        bstack1ll1lll1l11_opy_ = time.time()
        while self.process and time.time() - bstack1ll1lll1l11_opy_ < bstack1lll1ll1ll1_opy_:
            try:
                line = self.process.stdout.readline()
                if bstack111l11_opy_ (u"ࠧ࡯ࡤ࠾ࠤᄣ") in line:
                    self.cli_bin_session_id = line.split(bstack111l11_opy_ (u"ࠨࡩࡥ࠿ࠥᄤ"))[-1:][0].strip()
                    self.logger.debug(bstack111l11_opy_ (u"ࠢࡤ࡮࡬ࡣࡧ࡯࡮ࡠࡵࡨࡷࡸ࡯࡯࡯ࡡ࡬ࡨ࠿ࠨᄥ") + str(self.cli_bin_session_id) + bstack111l11_opy_ (u"ࠣࠤᄦ"))
                    continue
                if bstack111l11_opy_ (u"ࠤ࡯࡭ࡸࡺࡥ࡯࠿ࠥᄧ") in line:
                    self.cli_listen_addr = line.split(bstack111l11_opy_ (u"ࠥࡰ࡮ࡹࡴࡦࡰࡀࠦᄨ"))[-1:][0].strip()
                    self.logger.debug(bstack111l11_opy_ (u"ࠦࡨࡲࡩࡠ࡮࡬ࡷࡹ࡫࡮ࡠࡣࡧࡨࡷࡀࠢᄩ") + str(self.cli_listen_addr) + bstack111l11_opy_ (u"ࠧࠨᄪ"))
                    continue
                if bstack111l11_opy_ (u"ࠨࡰࡰࡴࡷࡁࠧᄫ") in line:
                    port = line.split(bstack111l11_opy_ (u"ࠢࡱࡱࡵࡸࡂࠨᄬ"))[-1:][0].strip()
                    self.logger.debug(bstack111l11_opy_ (u"ࠣࡲࡲࡶࡹࡀࠢᄭ") + str(port) + bstack111l11_opy_ (u"ࠤࠥᄮ"))
                    continue
                if line.strip() == bstack1ll1ll1ll11_opy_ and self.cli_bin_session_id and self.cli_listen_addr:
                    if os.getenv(bstack111l11_opy_ (u"ࠥࡗࡉࡑ࡟ࡄࡎࡌࡣࡋࡒࡁࡈࡡࡌࡓࡤ࡙ࡔࡓࡇࡄࡑࠧᄯ"), bstack111l11_opy_ (u"ࠦ࠶ࠨᄰ")) == bstack111l11_opy_ (u"ࠧ࠷ࠢᄱ"):
                        if not self.process.stdout.closed:
                            self.process.stdout.close()
                        if not self.process.stderr.closed:
                            self.process.stderr.close()
                    self.bstack1ll1lll1ll1_opy_ = True
                    return True
            except Exception as e:
                self.logger.debug(bstack111l11_opy_ (u"ࠨࡥࡳࡴࡲࡶ࠿ࠦࠢᄲ") + str(e) + bstack111l11_opy_ (u"ࠢࠣᄳ"))
        return False
    @measure(event_name=EVENTS.bstack1lll1lll11l_opy_, stage=STAGE.bstack111lllll1_opy_)
    def __1lll1llllll_opy_(self):
        if self.bstack1ll1ll11ll1_opy_:
            self.bstack1llllllllll_opy_.stop()
            start = datetime.now()
            if self.bstack1lll111llll_opy_():
                self.cli_bin_session_id = None
                if self.bstack1llll11l1ll_opy_:
                    self.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠣࡵࡷࡳࡵࡥࡳࡦࡵࡶ࡭ࡴࡴ࡟ࡵ࡫ࡰࡩࠧᄴ"), datetime.now() - start)
                else:
                    self.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠤࡶࡸࡴࡶ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠࡶ࡬ࡱࡪࠨᄵ"), datetime.now() - start)
            self.__1lll11111l1_opy_()
            start = datetime.now()
            self.bstack1ll1ll11ll1_opy_.close()
            self.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠥࡨ࡮ࡹࡣࡰࡰࡱࡩࡨࡺ࡟ࡵ࡫ࡰࡩࠧᄶ"), datetime.now() - start)
            self.bstack1ll1ll11ll1_opy_ = None
        if self.process:
            self.logger.debug(bstack111l11_opy_ (u"ࠦࡸࡺ࡯ࡱࠤᄷ"))
            start = datetime.now()
            self.process.terminate()
            self.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠧࡱࡩ࡭࡮ࡢࡸ࡮ࡳࡥࠣᄸ"), datetime.now() - start)
            self.process = None
            if self.bstack1lll111l11l_opy_ and self.config_observability and self.config_testhub and self.config_testhub.testhub_events:
                self.bstack11llll11l1_opy_()
                self.logger.info(
                    bstack111l11_opy_ (u"ࠨࡖࡪࡵ࡬ࡸࠥ࡮ࡴࡵࡲࡶ࠾࠴࠵ࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵ࡢࡶ࡫࡯ࡨࡸ࠵ࡻࡾࠢࡷࡳࠥࡼࡩࡦࡹࠣࡦࡺ࡯࡬ࡥࠢࡵࡩࡵࡵࡲࡵ࠮ࠣ࡭ࡳࡹࡩࡨࡪࡷࡷ࠱ࠦࡡ࡯ࡦࠣࡱࡦࡴࡹࠡ࡯ࡲࡶࡪࠦࡤࡦࡤࡸ࡫࡬࡯࡮ࡨࠢ࡬ࡲ࡫ࡵࡲ࡮ࡣࡷ࡭ࡴࡴࠠࡢ࡮࡯ࠤࡦࡺࠠࡰࡰࡨࠤࡵࡲࡡࡤࡧࠤࡠࡳࠨᄹ").format(
                        self.config_testhub.build_hashed_id
                    )
                )
                os.environ[bstack111l11_opy_ (u"ࠧࡃࡕࡢࡘࡊ࡙ࡔࡐࡒࡖࡣࡇ࡛ࡉࡍࡆࡢࡌࡆ࡙ࡈࡆࡆࡢࡍࡉ࠭ᄺ")] = self.config_testhub.build_hashed_id
        self.bstack1ll1lll1ll1_opy_ = False
    def __1ll1lll11l1_opy_(self, data):
        try:
            import selenium
            data.framework_versions[bstack111l11_opy_ (u"ࠣࡵࡨࡰࡪࡴࡩࡶ࡯ࠥᄻ")] = selenium.__version__
            data.frameworks.append(bstack111l11_opy_ (u"ࠤࡶࡩࡱ࡫࡮ࡪࡷࡰࠦᄼ"))
        except:
            pass
        try:
            from playwright._repo_version import __version__
            data.framework_versions[bstack111l11_opy_ (u"ࠥࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠢᄽ")] = __version__
            data.frameworks.append(bstack111l11_opy_ (u"ࠦࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠣᄾ"))
        except:
            pass
    def bstack1ll1l1ll11l_opy_(self, hub_url: str, platform_index: int, bstack1ll1lllll_opy_: Any):
        if self.bstack1lllll11l1l_opy_:
            self.logger.debug(bstack111l11_opy_ (u"ࠧࡹ࡫ࡪࡲࡳࡩࡩࠦࡳࡦࡶࡸࡴࠥࡹࡥ࡭ࡧࡱ࡭ࡺࡳ࠺ࠡࡣ࡯ࡶࡪࡧࡤࡺࠢࡶࡩࡹࠦࡵࡱࠤᄿ"))
            return
        try:
            bstack11l1ll1l_opy_ = datetime.now()
            import selenium
            from selenium.webdriver.remote.webdriver import WebDriver
            from selenium.webdriver.common.service import Service
            framework = bstack111l11_opy_ (u"ࠨࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࠣᅀ")
            self.bstack1lllll11l1l_opy_ = bstack1ll1ll1l11l_opy_(
                cli.config.get(bstack111l11_opy_ (u"ࠢࡩࡷࡥ࡙ࡷࡲࠢᅁ"), hub_url),
                platform_index,
                framework_name=framework,
                framework_version=selenium.__version__,
                classes=[WebDriver],
                bstack1llll111111_opy_={bstack111l11_opy_ (u"ࠣࡥࡵࡩࡦࡺࡥࡠࡱࡳࡸ࡮ࡵ࡮ࡴࡡࡩࡶࡴࡳ࡟ࡤࡣࡳࡷࠧᅂ"): bstack1ll1lllll_opy_}
            )
            def bstack1lll11llll1_opy_(self):
                return
            if self.config.get(bstack111l11_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠦᅃ"), True):
                Service.start = bstack1lll11llll1_opy_
                Service.stop = bstack1lll11llll1_opy_
            def get_accessibility_results(driver):
                if self.accessibility and self.accessibility.is_enabled():
                    return self.accessibility.get_accessibility_results(driver, framework_name=framework)
            def get_accessibility_results_summary(driver):
                if self.accessibility and self.accessibility.is_enabled():
                    return self.accessibility.get_accessibility_results_summary(driver, framework_name=framework)
            def perform_scan(driver):
                if self.accessibility and self.accessibility.is_enabled():
                    return self.accessibility.perform_scan(driver, method=None, framework_name=framework)
            WebDriver.getAccessibilityResults = get_accessibility_results
            WebDriver.get_accessibility_results = get_accessibility_results
            WebDriver.getAccessibilityResultsSummary = get_accessibility_results_summary
            WebDriver.get_accessibility_results_summary = get_accessibility_results_summary
            WebDriver.upload_attachment = staticmethod(bstack11llll11ll_opy_.upload_attachment)
            WebDriver.set_custom_tag = staticmethod(bstack1lll1l1l1l1_opy_.set_custom_tag)
            WebDriver.performScan = perform_scan
            WebDriver.perform_scan = perform_scan
            self.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠥࡷࡪࡺࡵࡱࡡࡶࡩࡱ࡫࡮ࡪࡷࡰࠦᅄ"), datetime.now() - bstack11l1ll1l_opy_)
        except Exception as e:
            self.logger.error(bstack111l11_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡴࡧࡷࡹࡵࠦࡳࡦ࡮ࡨࡲ࡮ࡻ࡭࠻ࠢࠥᅅ") + str(e) + bstack111l11_opy_ (u"ࠧࠨᅆ"))
    def bstack1ll1l1l1l1l_opy_(self, platform_index: int):
        try:
            from playwright.sync_api import BrowserType
            from playwright.sync_api import BrowserContext
            from playwright._impl._connection import Connection
            from playwright._repo_version import __version__
            from bstack_utils.helper import bstack11ll1l1ll1_opy_
            self.bstack1lllll11l1l_opy_ = bstack1ll1ll11111_opy_(
                platform_index,
                framework_name=bstack111l11_opy_ (u"ࠨࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠥᅇ"),
                framework_version=__version__,
                classes=[BrowserType, BrowserContext, Connection],
            )
        except Exception as e:
            self.logger.error(bstack111l11_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡪࡺࡵࡱࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࡀࠠࠣᅈ") + str(e) + bstack111l11_opy_ (u"ࠣࠤᅉ"))
            pass
    def bstack1llll111ll1_opy_(self):
        if self.test_framework:
            self.logger.debug(bstack111l11_opy_ (u"ࠤࡶ࡯࡮ࡶࡰࡦࡦࠣࡷࡪࡺࡵࡱࠢࡳࡽࡹ࡫ࡳࡵ࠼ࠣࡥࡱࡸࡥࡢࡦࡼࠤࡸ࡫ࡴࠡࡷࡳࠦᅊ"))
            return
        if bstack11l11l111_opy_():
            import pytest
            self.test_framework = PytestBDDFramework({ bstack111l11_opy_ (u"ࠥࡴࡾࡺࡥࡴࡶࠥᅋ"): pytest.__version__ }, [bstack111l11_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠣᅌ")], self.bstack1llllllllll_opy_, self.bstack1ll1ll1ll1l_opy_)
            return
        try:
            import pytest
            self.test_framework = bstack1ll1lll11ll_opy_({ bstack111l11_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸࠧᅍ"): pytest.__version__ }, [bstack111l11_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹࠨᅎ")], self.bstack1llllllllll_opy_, self.bstack1ll1ll1ll1l_opy_)
        except Exception as e:
            self.logger.error(bstack111l11_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡪࡺࡵࡱࠢࡳࡽࡹ࡫ࡳࡵ࠼ࠣࠦᅏ") + str(e) + bstack111l11_opy_ (u"ࠣࠤᅐ"))
        self.bstack1ll1l1l111l_opy_()
    def bstack1ll1l1l111l_opy_(self):
        if not self.bstack1lllll11ll_opy_():
            return
        bstack1l1111l1_opy_ = None
        def bstack11ll1lllll_opy_(config, startdir):
            return bstack111l11_opy_ (u"ࠤࡧࡶ࡮ࡼࡥࡳ࠼ࠣࡿ࠵ࢃࠢᅑ").format(bstack111l11_opy_ (u"ࠥࡆࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࠤᅒ"))
        def bstack11l1l1ll1_opy_():
            return
        def bstack1l1111l11_opy_(self, name: str, default=Notset(), skip: bool = False):
            if str(name).lower() == bstack111l11_opy_ (u"ࠫࡩࡸࡩࡷࡧࡵࠫᅓ"):
                return bstack111l11_opy_ (u"ࠧࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠦᅔ")
            else:
                return bstack1l1111l1_opy_(self, name, default, skip)
        try:
            from pytest_selenium import pytest_selenium
            from _pytest.config import Config
            bstack1l1111l1_opy_ = Config.getoption
            pytest_selenium.pytest_report_header = bstack11ll1lllll_opy_
            from pytest_selenium.drivers import browserstack
            browserstack.pytest_selenium_runtest_makereport = bstack11l1l1ll1_opy_
            Config.getoption = bstack1l1111l11_opy_
        except Exception as e:
            self.logger.error(bstack111l11_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡳࡥࡹࡩࡨࠡࡲࡼࡸࡪࡹࡴࠡࡵࡨࡰࡪࡴࡩࡶ࡯ࠣࡪࡴࡸࠠࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡀࠠࠣᅕ") + str(e) + bstack111l11_opy_ (u"ࠢࠣᅖ"))
    def bstack1lll1lllll1_opy_(self):
        bstack11ll1ll11_opy_ = MessageToDict(cli.config_testhub, preserving_proto_field_name=True)
        if isinstance(bstack11ll1ll11_opy_, dict):
            if cli.config_observability:
                bstack11ll1ll11_opy_.update(
                    {bstack111l11_opy_ (u"ࠣࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࠣᅗ"): MessageToDict(cli.config_observability, preserving_proto_field_name=True)}
                )
            if cli.config_accessibility:
                accessibility = MessageToDict(cli.config_accessibility, preserving_proto_field_name=True)
                if isinstance(accessibility, dict) and bstack111l11_opy_ (u"ࠤࡦࡳࡲࡳࡡ࡯ࡦࡶࡣࡹࡵ࡟ࡸࡴࡤࡴࠧᅘ") in accessibility.get(bstack111l11_opy_ (u"ࠥࡳࡵࡺࡩࡰࡰࡶࠦᅙ"), {}):
                    bstack1lll11l11ll_opy_ = accessibility.get(bstack111l11_opy_ (u"ࠦࡴࡶࡴࡪࡱࡱࡷࠧᅚ"))
                    bstack1lll11l11ll_opy_.update({ bstack111l11_opy_ (u"ࠧࡩ࡯࡮࡯ࡤࡲࡩࡹࡔࡰ࡙ࡵࡥࡵࠨᅛ"): bstack1lll11l11ll_opy_.pop(bstack111l11_opy_ (u"ࠨࡣࡰ࡯ࡰࡥࡳࡪࡳࡠࡶࡲࡣࡼࡸࡡࡱࠤᅜ")) })
                bstack11ll1ll11_opy_.update({bstack111l11_opy_ (u"ࠢࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠢᅝ"): accessibility })
        return bstack11ll1ll11_opy_
    @measure(event_name=EVENTS.bstack1ll1l1lll11_opy_, stage=STAGE.bstack111lllll1_opy_)
    def bstack1lll111llll_opy_(self, bstack1lll1l11ll1_opy_: str = None, bstack1ll1ll11lll_opy_: str = None, exit_code: int = None):
        if not self.cli_bin_session_id or not self.bstack1ll1ll1ll1l_opy_:
            return
        bstack11l1ll1l_opy_ = datetime.now()
        req = structs.StopBinSessionRequest()
        req.bin_session_id = self.cli_bin_session_id
        if exit_code:
            req.exit_code = exit_code
        if bstack1lll1l11ll1_opy_:
            req.bstack1lll1l11ll1_opy_ = bstack1lll1l11ll1_opy_
        if bstack1ll1ll11lll_opy_:
            req.bstack1ll1ll11lll_opy_ = bstack1ll1ll11lll_opy_
        try:
            r = self.bstack1ll1ll1ll1l_opy_.StopBinSession(req)
            SDKCLI.automate_buildlink = r.automate_buildlink
            SDKCLI.hashed_id = r.hashed_id
            self.bstack111llll1ll_opy_(bstack111l11_opy_ (u"ࠣࡩࡵࡴࡨࡀࡳࡵࡱࡳࡣࡧ࡯࡮ࡠࡵࡨࡷࡸ࡯࡯࡯ࠤᅞ"), datetime.now() - bstack11l1ll1l_opy_)
            return r.success
        except grpc.RpcError as e:
            traceback.print_exc()
            raise e
    def bstack111llll1ll_opy_(self, key: str, value: timedelta):
        tag = bstack111l11_opy_ (u"ࠤࡦ࡬࡮ࡲࡤ࠮ࡲࡵࡳࡨ࡫ࡳࡴࠤᅟ") if self.bstack111lllll1l_opy_() else bstack111l11_opy_ (u"ࠥࡱࡦ࡯࡮࠮ࡲࡵࡳࡨ࡫ࡳࡴࠤᅠ")
        self.bstack1ll1lllllll_opy_[bstack111l11_opy_ (u"ࠦ࠿ࠨᅡ").join([tag + bstack111l11_opy_ (u"ࠧ࠳ࠢᅢ") + str(id(self)), key])] += value
    def bstack11llll11l1_opy_(self):
        if not os.getenv(bstack111l11_opy_ (u"ࠨࡄࡆࡄࡘࡋࡤࡖࡅࡓࡈࠥᅣ"), bstack111l11_opy_ (u"ࠢ࠱ࠤᅤ")) == bstack111l11_opy_ (u"ࠣ࠳ࠥᅥ"):
            return
        bstack1llll111l11_opy_ = dict()
        bstack1lllll111l1_opy_ = []
        if self.test_framework:
            bstack1lllll111l1_opy_.extend(list(self.test_framework.bstack1lllll111l1_opy_.values()))
        if self.bstack1lllll11l1l_opy_:
            bstack1lllll111l1_opy_.extend(list(self.bstack1lllll11l1l_opy_.bstack1lllll111l1_opy_.values()))
        for instance in bstack1lllll111l1_opy_:
            if not instance.platform_index in bstack1llll111l11_opy_:
                bstack1llll111l11_opy_[instance.platform_index] = defaultdict(lambda: timedelta(microseconds=0))
            report = bstack1llll111l11_opy_[instance.platform_index]
            for k, v in instance.bstack1ll1ll1111l_opy_().items():
                report[k] += v
                report[k.split(bstack111l11_opy_ (u"ࠤ࠽ࠦᅦ"))[0]] += v
        bstack1ll1l1lllll_opy_ = sorted([(k, v) for k, v in self.bstack1ll1lllllll_opy_.items()], key=lambda o: o[1], reverse=True)
        bstack1ll1lll1lll_opy_ = 0
        for r in bstack1ll1l1lllll_opy_:
            bstack1lll1lll1ll_opy_ = r[1].total_seconds()
            bstack1ll1lll1lll_opy_ += bstack1lll1lll1ll_opy_
            self.logger.debug(bstack111l11_opy_ (u"ࠥ࡟ࡵ࡫ࡲࡧ࡟ࠣࡧࡱ࡯࠺ࡼࡴ࡞࠴ࡢࢃ࠽ࠣᅧ") + str(bstack1lll1lll1ll_opy_) + bstack111l11_opy_ (u"ࠦࠧᅨ"))
        self.logger.debug(bstack111l11_opy_ (u"ࠧ࠳࠭ࠣᅩ"))
        bstack1lll11ll1ll_opy_ = []
        for platform_index, report in bstack1llll111l11_opy_.items():
            bstack1lll11ll1ll_opy_.extend([(platform_index, k, v) for k, v in report.items()])
        bstack1lll11ll1ll_opy_.sort(key=lambda o: o[2], reverse=True)
        bstack1l1111llll_opy_ = set()
        bstack1lll11l1l1l_opy_ = 0
        for r in bstack1lll11ll1ll_opy_:
            bstack1lll1lll1ll_opy_ = r[2].total_seconds()
            bstack1lll11l1l1l_opy_ += bstack1lll1lll1ll_opy_
            bstack1l1111llll_opy_.add(r[0])
            self.logger.debug(bstack111l11_opy_ (u"ࠨ࡛ࡱࡧࡵࡪࡢࠦࡴࡦࡵࡷ࠾ࡵࡲࡡࡵࡨࡲࡶࡲ࠳ࡻࡳ࡝࠳ࡡࢂࡀࡻࡳ࡝࠴ࡡࢂࡃࠢᅪ") + str(bstack1lll1lll1ll_opy_) + bstack111l11_opy_ (u"ࠢࠣᅫ"))
        if self.bstack111lllll1l_opy_():
            self.logger.debug(bstack111l11_opy_ (u"ࠣ࠯࠰ࠦᅬ"))
            self.logger.debug(bstack111l11_opy_ (u"ࠤ࡞ࡴࡪࡸࡦ࡞ࠢࡦࡰ࡮ࡀࡣࡩ࡫࡯ࡨ࠲ࡶࡲࡰࡥࡨࡷࡸࡃࡻࡵࡱࡷࡥࡱࡥࡣ࡭࡫ࢀࠤࡹ࡫ࡳࡵ࠼ࡳࡰࡦࡺࡦࡰࡴࡰࡷ࠲ࢁࡳࡵࡴࠫࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠯ࡽ࠾ࠤᅭ") + str(bstack1lll11l1l1l_opy_) + bstack111l11_opy_ (u"ࠥࠦᅮ"))
        else:
            self.logger.debug(bstack111l11_opy_ (u"ࠦࡠࡶࡥࡳࡨࡠࠤࡨࡲࡩ࠻࡯ࡤ࡭ࡳ࠳ࡰࡳࡱࡦࡩࡸࡹ࠽ࠣᅯ") + str(bstack1ll1lll1lll_opy_) + bstack111l11_opy_ (u"ࠧࠨᅰ"))
        self.logger.debug(bstack111l11_opy_ (u"ࠨ࠭࠮ࠤᅱ"))
    def test_orchestration_session(self, test_files: list, orchestration_strategy: str):
        request = structs.TestOrchestrationRequest(
            bin_session_id=self.cli_bin_session_id,
            orchestration_strategy=orchestration_strategy,
            test_files=test_files
        )
        if not self.bstack1ll1ll1ll1l_opy_:
            self.logger.error(bstack111l11_opy_ (u"ࠢࡤ࡮࡬ࡣࡸ࡫ࡲࡷ࡫ࡦࡩࠥ࡯ࡳࠡࡰࡲࡸࠥ࡯࡮ࡪࡶ࡬ࡥࡱ࡯ࡺࡦࡦ࠱ࠤࡈࡧ࡮࡯ࡱࡷࠤࡵ࡫ࡲࡧࡱࡵࡱࠥࡺࡥࡴࡶࠣࡳࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰ࠱ࠦᅲ"))
            return None
        response = self.bstack1ll1ll1ll1l_opy_.TestOrchestration(request)
        self.logger.debug(bstack111l11_opy_ (u"ࠣࡶࡨࡷࡹ࠳࡯ࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳ࠳ࡳࡦࡵࡶ࡭ࡴࡴ࠽ࡼࡿࠥᅳ").format(response))
        if response.success:
            return list(response.ordered_test_files)
        return None
    def bstack1lll1111ll1_opy_(self, r):
        if r is not None and getattr(r, bstack111l11_opy_ (u"ࠩࡷࡩࡸࡺࡨࡶࡤࠪᅴ"), None) and getattr(r.testhub, bstack111l11_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࡵࠪᅵ"), None):
            errors = json.loads(r.testhub.errors.decode(bstack111l11_opy_ (u"ࠦࡺࡺࡦ࠮࠺ࠥᅶ")))
            for bstack1lll11l11l1_opy_, err in errors.items():
                if err[bstack111l11_opy_ (u"ࠬࡺࡹࡱࡧࠪᅷ")] == bstack111l11_opy_ (u"࠭ࡩ࡯ࡨࡲࠫᅸ"):
                    self.logger.info(err[bstack111l11_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨᅹ")])
                else:
                    self.logger.error(err[bstack111l11_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩᅺ")])
    def bstack1ll1ll1ll_opy_(self):
        return SDKCLI.automate_buildlink, SDKCLI.hashed_id
cli = SDKCLI()