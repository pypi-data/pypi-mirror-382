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
import re
import sys
import json
import time
import shutil
import tempfile
import requests
import subprocess
from threading import Thread
from os.path import expanduser
from bstack_utils.constants import *
from requests.auth import HTTPBasicAuth
from bstack_utils.helper import bstack11ll1llll_opy_
from bstack_utils.measure import measure
from bstack_utils.bstack1l1l1ll11l_opy_ import bstack11l1l11l1l_opy_
class bstack1ll11l1lll_opy_:
  working_dir = os.getcwd()
  bstack1lllll11l_opy_ = False
  config = {}
  bstack11l111l1lll_opy_ = bstack111l11_opy_ (u"ࠬ࠭ẳ")
  binary_path = bstack111l11_opy_ (u"࠭ࠧẴ")
  bstack1111l1lll1l_opy_ = bstack111l11_opy_ (u"ࠧࠨẵ")
  bstack1l111l1111_opy_ = False
  bstack11111ll11ll_opy_ = None
  bstack1111l111ll1_opy_ = {}
  bstack1111l1111ll_opy_ = 300
  bstack11111lll111_opy_ = False
  logger = None
  bstack11111l1l1l1_opy_ = False
  bstack1l111l1lll_opy_ = False
  percy_build_id = None
  bstack1111l1l1lll_opy_ = bstack111l11_opy_ (u"ࠨࠩẶ")
  bstack11111l1l1ll_opy_ = {
    bstack111l11_opy_ (u"ࠩࡦ࡬ࡷࡵ࡭ࡦࠩặ") : 1,
    bstack111l11_opy_ (u"ࠪࡪ࡮ࡸࡥࡧࡱࡻࠫẸ") : 2,
    bstack111l11_opy_ (u"ࠫࡪࡪࡧࡦࠩẹ") : 3,
    bstack111l11_opy_ (u"ࠬࡹࡡࡧࡣࡵ࡭ࠬẺ") : 4
  }
  def __init__(self) -> None: pass
  def bstack11111ll1ll1_opy_(self):
    bstack1111l11lll1_opy_ = bstack111l11_opy_ (u"࠭ࠧẻ")
    bstack1111l1l1ll1_opy_ = sys.platform
    bstack11111l111ll_opy_ = bstack111l11_opy_ (u"ࠧࡱࡧࡵࡧࡾ࠭Ẽ")
    if re.match(bstack111l11_opy_ (u"ࠣࡦࡤࡶࡼ࡯࡮ࡽ࡯ࡤࡧࠥࡵࡳࠣẽ"), bstack1111l1l1ll1_opy_) != None:
      bstack1111l11lll1_opy_ = bstack11l1lll1l11_opy_ + bstack111l11_opy_ (u"ࠤ࠲ࡴࡪࡸࡣࡺ࠯ࡲࡷࡽ࠴ࡺࡪࡲࠥẾ")
      self.bstack1111l1l1lll_opy_ = bstack111l11_opy_ (u"ࠪࡱࡦࡩࠧế")
    elif re.match(bstack111l11_opy_ (u"ࠦࡲࡹࡷࡪࡰࡿࡱࡸࡿࡳࡽ࡯࡬ࡲ࡬ࡽࡼࡤࡻࡪࡻ࡮ࡴࡼࡣࡥࡦࡻ࡮ࡴࡼࡸ࡫ࡱࡧࡪࢂࡥ࡮ࡥࡿࡻ࡮ࡴ࠳࠳ࠤỀ"), bstack1111l1l1ll1_opy_) != None:
      bstack1111l11lll1_opy_ = bstack11l1lll1l11_opy_ + bstack111l11_opy_ (u"ࠧ࠵ࡰࡦࡴࡦࡽ࠲ࡽࡩ࡯࠰ࡽ࡭ࡵࠨề")
      bstack11111l111ll_opy_ = bstack111l11_opy_ (u"ࠨࡰࡦࡴࡦࡽ࠳࡫ࡸࡦࠤỂ")
      self.bstack1111l1l1lll_opy_ = bstack111l11_opy_ (u"ࠧࡸ࡫ࡱࠫể")
    else:
      bstack1111l11lll1_opy_ = bstack11l1lll1l11_opy_ + bstack111l11_opy_ (u"ࠣ࠱ࡳࡩࡷࡩࡹ࠮࡮࡬ࡲࡺࡾ࠮ࡻ࡫ࡳࠦỄ")
      self.bstack1111l1l1lll_opy_ = bstack111l11_opy_ (u"ࠩ࡯࡭ࡳࡻࡸࠨễ")
    return bstack1111l11lll1_opy_, bstack11111l111ll_opy_
  def bstack11111ll111l_opy_(self):
    try:
      bstack1111l111l1l_opy_ = [os.path.join(expanduser(bstack111l11_opy_ (u"ࠥࢂࠧỆ")), bstack111l11_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫệ")), self.working_dir, tempfile.gettempdir()]
      for path in bstack1111l111l1l_opy_:
        if(self.bstack1111l11llll_opy_(path)):
          return path
      raise bstack111l11_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡦࡲࡻࡳࡲ࡯ࡢࡦࠣࡴࡪࡸࡣࡺࠢࡥ࡭ࡳࡧࡲࡺࠤỈ")
    except Exception as e:
      self.logger.error(bstack111l11_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡩ࡭ࡳࡪࠠࡢࡸࡤ࡭ࡱࡧࡢ࡭ࡧࠣࡴࡦࡺࡨࠡࡨࡲࡶࠥࡶࡥࡳࡥࡼࠤࡩࡵࡷ࡯࡮ࡲࡥࡩ࠲ࠠࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࠱ࠥࢁࡽࠣỉ").format(e))
  def bstack1111l11llll_opy_(self, path):
    try:
      if not os.path.exists(path):
        os.makedirs(path)
      return True
    except:
      return False
  def bstack11111l1111l_opy_(self, bstack111111llll1_opy_):
    return os.path.join(bstack111111llll1_opy_, self.bstack11l111l1lll_opy_ + bstack111l11_opy_ (u"ࠢ࠯ࡧࡷࡥ࡬ࠨỊ"))
  def bstack11111ll11l1_opy_(self, bstack111111llll1_opy_, bstack111111lll1l_opy_):
    if not bstack111111lll1l_opy_: return
    try:
      bstack1111l11l1ll_opy_ = self.bstack11111l1111l_opy_(bstack111111llll1_opy_)
      with open(bstack1111l11l1ll_opy_, bstack111l11_opy_ (u"ࠣࡹࠥị")) as f:
        f.write(bstack111111lll1l_opy_)
        self.logger.debug(bstack111l11_opy_ (u"ࠤࡖࡥࡻ࡫ࡤࠡࡰࡨࡻࠥࡋࡔࡢࡩࠣࡪࡴࡸࠠࡱࡧࡵࡧࡾࠨỌ"))
    except Exception as e:
      self.logger.error(bstack111l11_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡳࡢࡸࡨࠤࡹ࡮ࡥࠡࡧࡷࡥ࡬࠲ࠠࡦࡴࡵࡳࡷࡀࠠࡼࡿࠥọ").format(e))
  def bstack11111l11l11_opy_(self, bstack111111llll1_opy_):
    try:
      bstack1111l11l1ll_opy_ = self.bstack11111l1111l_opy_(bstack111111llll1_opy_)
      if os.path.exists(bstack1111l11l1ll_opy_):
        with open(bstack1111l11l1ll_opy_, bstack111l11_opy_ (u"ࠦࡷࠨỎ")) as f:
          bstack111111lll1l_opy_ = f.read().strip()
          return bstack111111lll1l_opy_ if bstack111111lll1l_opy_ else None
    except Exception as e:
      self.logger.error(bstack111l11_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡲ࡯ࡢࡦ࡬ࡲ࡬ࠦࡅࡕࡣࡪ࠰ࠥ࡫ࡲࡳࡱࡵ࠾ࠥࢁࡽࠣỏ").format(e))
  def bstack1111l111l11_opy_(self, bstack111111llll1_opy_, bstack1111l11lll1_opy_):
    bstack1111l11ll11_opy_ = self.bstack11111l11l11_opy_(bstack111111llll1_opy_)
    if bstack1111l11ll11_opy_:
      try:
        bstack1111l1l11ll_opy_ = self.bstack11111l11ll1_opy_(bstack1111l11ll11_opy_, bstack1111l11lll1_opy_)
        if not bstack1111l1l11ll_opy_:
          self.logger.debug(bstack111l11_opy_ (u"ࠨࡐࡦࡴࡦࡽࠥࡨࡩ࡯ࡣࡵࡽࠥ࡯ࡳࠡࡷࡳࠤࡹࡵࠠࡥࡣࡷࡩࠥ࠮ࡅࡕࡣࡪࠤࡺࡴࡣࡩࡣࡱ࡫ࡪࡪࠩࠣỐ"))
          return True
        self.logger.debug(bstack111l11_opy_ (u"ࠢࡏࡧࡺࠤࡕ࡫ࡲࡤࡻࠣࡦ࡮ࡴࡡࡳࡻࠣࡺࡪࡸࡳࡪࡱࡱࠤࡦࡼࡡࡪ࡮ࡤࡦࡱ࡫ࠬࠡࡦࡲࡻࡳࡲ࡯ࡢࡦ࡬ࡲ࡬ࠦࡵࡱࡦࡤࡸࡪࠨố"))
        return False
      except Exception as e:
        self.logger.warn(bstack111l11_opy_ (u"ࠣࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡨ࡮ࡥࡤ࡭ࠣࡪࡴࡸࠠࡣ࡫ࡱࡥࡷࡿࠠࡶࡲࡧࡥࡹ࡫ࡳ࠭ࠢࡸࡷ࡮ࡴࡧࠡࡧࡻ࡭ࡸࡺࡩ࡯ࡩࠣࡦ࡮ࡴࡡࡳࡻ࠽ࠤࢀࢃࠢỒ").format(e))
    return False
  def bstack11111l11ll1_opy_(self, bstack1111l11ll11_opy_, bstack1111l11lll1_opy_):
    try:
      headers = {
        bstack111l11_opy_ (u"ࠤࡌࡪ࠲ࡔ࡯࡯ࡧ࠰ࡑࡦࡺࡣࡩࠤồ"): bstack1111l11ll11_opy_
      }
      response = bstack11ll1llll_opy_(bstack111l11_opy_ (u"ࠪࡋࡊ࡚ࠧỔ"), bstack1111l11lll1_opy_, {}, {bstack111l11_opy_ (u"ࠦ࡭࡫ࡡࡥࡧࡵࡷࠧổ"): headers})
      if response.status_code == 304:
        return False
      return True
    except Exception as e:
      raise(bstack111l11_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤࡨ࡮ࡥࡤ࡭࡬ࡲ࡬ࠦࡦࡰࡴࠣࡔࡪࡸࡣࡺࠢࡥ࡭ࡳࡧࡲࡺࠢࡸࡴࡩࡧࡴࡦࡵ࠽ࠤࢀࢃࠢỖ").format(e))
  @measure(event_name=EVENTS.bstack11l1ll1l111_opy_, stage=STAGE.bstack111lllll1_opy_)
  def bstack11111l1ll11_opy_(self, bstack1111l11lll1_opy_, bstack11111l111ll_opy_):
    try:
      bstack1111l1l1111_opy_ = self.bstack11111ll111l_opy_()
      bstack1111l1l111l_opy_ = os.path.join(bstack1111l1l1111_opy_, bstack111l11_opy_ (u"࠭ࡰࡦࡴࡦࡽ࠳ࢀࡩࡱࠩỗ"))
      bstack1111l1ll1ll_opy_ = os.path.join(bstack1111l1l1111_opy_, bstack11111l111ll_opy_)
      if self.bstack1111l111l11_opy_(bstack1111l1l1111_opy_, bstack1111l11lll1_opy_): # if bstack1111l11l11l_opy_, bstack1l1l111l111_opy_ bstack111111lll1l_opy_ is bstack1111l11111l_opy_ to bstack111lllll11l_opy_ version available (response 304)
        if os.path.exists(bstack1111l1ll1ll_opy_):
          self.logger.info(bstack111l11_opy_ (u"ࠢࡑࡧࡵࡧࡾࠦࡢࡪࡰࡤࡶࡾࠦࡦࡰࡷࡱࡨࠥ࡯࡮ࠡࡽࢀ࠰ࠥࡹ࡫ࡪࡲࡳ࡭ࡳ࡭ࠠࡥࡱࡺࡲࡱࡵࡡࡥࠤỘ").format(bstack1111l1ll1ll_opy_))
          return bstack1111l1ll1ll_opy_
        if os.path.exists(bstack1111l1l111l_opy_):
          self.logger.info(bstack111l11_opy_ (u"ࠣࡒࡨࡶࡨࡿࠠࡻ࡫ࡳࠤ࡫ࡵࡵ࡯ࡦࠣ࡭ࡳࠦࡻࡾ࠮ࠣࡹࡳࢀࡩࡱࡲ࡬ࡲ࡬ࠨộ").format(bstack1111l1l111l_opy_))
          return self.bstack11111l1l111_opy_(bstack1111l1l111l_opy_, bstack11111l111ll_opy_)
      self.logger.info(bstack111l11_opy_ (u"ࠤࡇࡳࡼࡴ࡬ࡰࡣࡧ࡭ࡳ࡭ࠠࡱࡧࡵࡧࡾࠦࡢࡪࡰࡤࡶࡾࠦࡦࡳࡱࡰࠤࢀࢃࠢỚ").format(bstack1111l11lll1_opy_))
      response = bstack11ll1llll_opy_(bstack111l11_opy_ (u"ࠪࡋࡊ࡚ࠧớ"), bstack1111l11lll1_opy_, {}, {})
      if response.status_code == 200:
        bstack11111ll1l11_opy_ = response.headers.get(bstack111l11_opy_ (u"ࠦࡊ࡚ࡡࡨࠤỜ"), bstack111l11_opy_ (u"ࠧࠨờ"))
        if bstack11111ll1l11_opy_:
          self.bstack11111ll11l1_opy_(bstack1111l1l1111_opy_, bstack11111ll1l11_opy_)
        with open(bstack1111l1l111l_opy_, bstack111l11_opy_ (u"࠭ࡷࡣࠩỞ")) as file:
          file.write(response.content)
        self.logger.info(bstack111l11_opy_ (u"ࠢࡅࡱࡺࡲࡱࡵࡡࡥࡧࡧࠤࡵ࡫ࡲࡤࡻࠣࡦ࡮ࡴࡡࡳࡻࠣࡥࡳࡪࠠࡴࡣࡹࡩࡩࠦࡡࡵࠢࡾࢁࠧở").format(bstack1111l1l111l_opy_))
        return self.bstack11111l1l111_opy_(bstack1111l1l111l_opy_, bstack11111l111ll_opy_)
      else:
        raise(bstack111l11_opy_ (u"ࠣࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡩࡵࡷ࡯࡮ࡲࡥࡩࠦࡴࡩࡧࠣࡪ࡮ࡲࡥ࠯ࠢࡖࡸࡦࡺࡵࡴࠢࡦࡳࡩ࡫࠺ࠡࡽࢀࠦỠ").format(response.status_code))
    except Exception as e:
      self.logger.error(bstack111l11_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥࡪ࡯ࡸࡰ࡯ࡳࡦࡪࠠࡱࡧࡵࡧࡾࠦࡢࡪࡰࡤࡶࡾࡀࠠࡼࡿࠥỡ").format(e))
  def bstack11111llll1l_opy_(self, bstack1111l11lll1_opy_, bstack11111l111ll_opy_):
    try:
      retry = 2
      bstack1111l1ll1ll_opy_ = None
      bstack11111l111l1_opy_ = False
      while retry > 0:
        bstack1111l1ll1ll_opy_ = self.bstack11111l1ll11_opy_(bstack1111l11lll1_opy_, bstack11111l111ll_opy_)
        bstack11111l111l1_opy_ = self.bstack1111l11ll1l_opy_(bstack1111l11lll1_opy_, bstack11111l111ll_opy_, bstack1111l1ll1ll_opy_)
        if bstack11111l111l1_opy_:
          break
        retry -= 1
      return bstack1111l1ll1ll_opy_, bstack11111l111l1_opy_
    except Exception as e:
      self.logger.error(bstack111l11_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡧࡦࡶࠣࡴࡪࡸࡣࡺࠢࡥ࡭ࡳࡧࡲࡺࠢࡳࡥࡹ࡮ࠢỢ").format(e))
    return bstack1111l1ll1ll_opy_, False
  def bstack1111l11ll1l_opy_(self, bstack1111l11lll1_opy_, bstack11111l111ll_opy_, bstack1111l1ll1ll_opy_, bstack1111l1llll1_opy_ = 0):
    if bstack1111l1llll1_opy_ > 1:
      return False
    if bstack1111l1ll1ll_opy_ == None or os.path.exists(bstack1111l1ll1ll_opy_) == False:
      self.logger.warn(bstack111l11_opy_ (u"ࠦࡕ࡫ࡲࡤࡻࠣࡴࡦࡺࡨࠡࡰࡲࡸࠥ࡬࡯ࡶࡰࡧ࠰ࠥࡸࡥࡵࡴࡼ࡭ࡳ࡭ࠠࡥࡱࡺࡲࡱࡵࡡࡥࠤợ"))
      return False
    bstack11111l1lll1_opy_ = bstack111l11_opy_ (u"ࡷࠨ࡞࠯ࠬࡃࡴࡪࡸࡣࡺ࠱ࡦࡰ࡮ࠦ࡜ࡥ࠭࡟࠲ࡡࡪࠫ࡝࠰࡟ࡨ࠰ࠨỤ")
    command = bstack111l11_opy_ (u"࠭ࡻࡾࠢ࠰࠱ࡻ࡫ࡲࡴ࡫ࡲࡲࠬụ").format(bstack1111l1ll1ll_opy_)
    bstack1111l1ll11l_opy_ = subprocess.check_output(command, shell=True, text=True)
    if re.match(bstack11111l1lll1_opy_, bstack1111l1ll11l_opy_) != None:
      return True
    else:
      self.logger.error(bstack111l11_opy_ (u"ࠢࡑࡧࡵࡧࡾࠦࡶࡦࡴࡶ࡭ࡴࡴࠠࡤࡪࡨࡧࡰࠦࡦࡢ࡫࡯ࡩࡩࠨỦ"))
      return False
  def bstack11111l1l111_opy_(self, bstack1111l1l111l_opy_, bstack11111l111ll_opy_):
    try:
      working_dir = os.path.dirname(bstack1111l1l111l_opy_)
      shutil.unpack_archive(bstack1111l1l111l_opy_, working_dir)
      bstack1111l1ll1ll_opy_ = os.path.join(working_dir, bstack11111l111ll_opy_)
      os.chmod(bstack1111l1ll1ll_opy_, 0o755)
      return bstack1111l1ll1ll_opy_
    except Exception as e:
      self.logger.error(bstack111l11_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤࡺࡴࡺࡪࡲࠣࡴࡪࡸࡣࡺࠢࡥ࡭ࡳࡧࡲࡺࠤủ"))
  def bstack1111l1ll111_opy_(self):
    try:
      bstack11111l11lll_opy_ = self.config.get(bstack111l11_opy_ (u"ࠩࡳࡩࡷࡩࡹࠨỨ"))
      bstack1111l1ll111_opy_ = bstack11111l11lll_opy_ or (bstack11111l11lll_opy_ is None and self.bstack1lllll11l_opy_)
      if not bstack1111l1ll111_opy_ or self.config.get(bstack111l11_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭ứ"), None) not in bstack11l1ll1ll1l_opy_:
        return False
      self.bstack1l111l1111_opy_ = True
      return True
    except Exception as e:
      self.logger.error(bstack111l11_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡥࡧࡷࡩࡨࡺࠠࡱࡧࡵࡧࡾ࠲ࠠࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡿࢂࠨỪ").format(e))
  def bstack11111lll1ll_opy_(self):
    try:
      bstack11111lll1ll_opy_ = self.percy_capture_mode
      return bstack11111lll1ll_opy_
    except Exception as e:
      self.logger.error(bstack111l11_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡦࡨࡸࡪࡩࡴࠡࡲࡨࡶࡨࡿࠠࡤࡣࡳࡸࡺࡸࡥࠡ࡯ࡲࡨࡪ࠲ࠠࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡿࢂࠨừ").format(e))
  def init(self, bstack1lllll11l_opy_, config, logger):
    self.bstack1lllll11l_opy_ = bstack1lllll11l_opy_
    self.config = config
    self.logger = logger
    if not self.bstack1111l1ll111_opy_():
      return
    self.bstack1111l111ll1_opy_ = config.get(bstack111l11_opy_ (u"࠭ࡰࡦࡴࡦࡽࡔࡶࡴࡪࡱࡱࡷࠬỬ"), {})
    self.percy_capture_mode = config.get(bstack111l11_opy_ (u"ࠧࡱࡧࡵࡧࡾࡉࡡࡱࡶࡸࡶࡪࡓ࡯ࡥࡧࠪử"))
    try:
      bstack1111l11lll1_opy_, bstack11111l111ll_opy_ = self.bstack11111ll1ll1_opy_()
      self.bstack11l111l1lll_opy_ = bstack11111l111ll_opy_
      bstack1111l1ll1ll_opy_, bstack11111l111l1_opy_ = self.bstack11111llll1l_opy_(bstack1111l11lll1_opy_, bstack11111l111ll_opy_)
      if bstack11111l111l1_opy_:
        self.binary_path = bstack1111l1ll1ll_opy_
        thread = Thread(target=self.bstack11111l11111_opy_)
        thread.start()
      else:
        self.bstack11111l1l1l1_opy_ = True
        self.logger.error(bstack111l11_opy_ (u"ࠣࡋࡱࡺࡦࡲࡩࡥࠢࡳࡩࡷࡩࡹࠡࡲࡤࡸ࡭ࠦࡦࡰࡷࡱࡨࠥ࠳ࠠࡼࡿ࠯ࠤ࡚ࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡴࡶࡤࡶࡹࠦࡐࡦࡴࡦࡽࠧỮ").format(bstack1111l1ll1ll_opy_))
    except Exception as e:
      self.logger.error(bstack111l11_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥࡹࡴࡢࡴࡷࠤࡵ࡫ࡲࡤࡻ࠯ࠤࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡼࡿࠥữ").format(e))
  def bstack11111llll11_opy_(self):
    try:
      logfile = os.path.join(self.working_dir, bstack111l11_opy_ (u"ࠪࡰࡴ࡭ࠧỰ"), bstack111l11_opy_ (u"ࠫࡵ࡫ࡲࡤࡻ࠱ࡰࡴ࡭ࠧự"))
      os.makedirs(os.path.dirname(logfile)) if not os.path.exists(os.path.dirname(logfile)) else None
      self.logger.debug(bstack111l11_opy_ (u"ࠧࡖࡵࡴࡪ࡬ࡲ࡬ࠦࡰࡦࡴࡦࡽࠥࡲ࡯ࡨࡵࠣࡥࡹࠦࡻࡾࠤỲ").format(logfile))
      self.bstack1111l1lll1l_opy_ = logfile
    except Exception as e:
      self.logger.error(bstack111l11_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡶࡩࡹࠦࡰࡦࡴࡦࡽࠥࡲ࡯ࡨࠢࡳࡥࡹ࡮ࠬࠡࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࢀࢃࠢỳ").format(e))
  @measure(event_name=EVENTS.bstack11l1l1l11ll_opy_, stage=STAGE.bstack111lllll1_opy_)
  def bstack11111l11111_opy_(self):
    bstack1111l1l11l1_opy_ = self.bstack1111l111lll_opy_()
    if bstack1111l1l11l1_opy_ == None:
      self.bstack11111l1l1l1_opy_ = True
      self.logger.error(bstack111l11_opy_ (u"ࠢࡑࡧࡵࡧࡾࠦࡴࡰ࡭ࡨࡲࠥࡴ࡯ࡵࠢࡩࡳࡺࡴࡤ࠭ࠢࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡹࡴࡢࡴࡷࠤࡵ࡫ࡲࡤࡻࠥỴ"))
      return False
    bstack111111lllll_opy_ = [bstack111l11_opy_ (u"ࠣࡣࡳࡴ࠿࡫ࡸࡦࡥ࠽ࡷࡹࡧࡲࡵࠤỵ") if self.bstack1lllll11l_opy_ else bstack111l11_opy_ (u"ࠩࡨࡼࡪࡩ࠺ࡴࡶࡤࡶࡹ࠭Ỷ")]
    bstack111l1l1lll1_opy_ = self.bstack1111l1lll11_opy_()
    if bstack111l1l1lll1_opy_ != None:
      bstack111111lllll_opy_.append(bstack111l11_opy_ (u"ࠥ࠱ࡨࠦࡻࡾࠤỷ").format(bstack111l1l1lll1_opy_))
    env = os.environ.copy()
    env[bstack111l11_opy_ (u"ࠦࡕࡋࡒࡄ࡛ࡢࡘࡔࡑࡅࡏࠤỸ")] = bstack1111l1l11l1_opy_
    env[bstack111l11_opy_ (u"࡚ࠧࡈࡠࡄࡘࡍࡑࡊ࡟ࡖࡗࡌࡈࠧỹ")] = os.environ.get(bstack111l11_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫỺ"), bstack111l11_opy_ (u"ࠧࠨỻ"))
    bstack11111l1l11l_opy_ = [self.binary_path]
    self.bstack11111llll11_opy_()
    self.bstack11111ll11ll_opy_ = self.bstack1111l1l1l1l_opy_(bstack11111l1l11l_opy_ + bstack111111lllll_opy_, env)
    self.logger.debug(bstack111l11_opy_ (u"ࠣࡕࡷࡥࡷࡺࡩ࡯ࡩࠣࡌࡪࡧ࡬ࡵࡪࠣࡇ࡭࡫ࡣ࡬ࠤỼ"))
    bstack1111l1llll1_opy_ = 0
    while self.bstack11111ll11ll_opy_.poll() == None:
      bstack1111l11l1l1_opy_ = self.bstack11111llllll_opy_()
      if bstack1111l11l1l1_opy_:
        self.logger.debug(bstack111l11_opy_ (u"ࠤࡋࡩࡦࡲࡴࡩࠢࡆ࡬ࡪࡩ࡫ࠡࡵࡸࡧࡨ࡫ࡳࡴࡨࡸࡰࠧỽ"))
        self.bstack11111lll111_opy_ = True
        return True
      bstack1111l1llll1_opy_ += 1
      self.logger.debug(bstack111l11_opy_ (u"ࠥࡌࡪࡧ࡬ࡵࡪࠣࡇ࡭࡫ࡣ࡬ࠢࡕࡩࡹࡸࡹࠡ࠯ࠣࡿࢂࠨỾ").format(bstack1111l1llll1_opy_))
      time.sleep(2)
    self.logger.error(bstack111l11_opy_ (u"ࠦࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡴࡶࡤࡶࡹࠦࡰࡦࡴࡦࡽ࠱ࠦࡈࡦࡣ࡯ࡸ࡭ࠦࡃࡩࡧࡦ࡯ࠥࡌࡡࡪ࡮ࡨࡨࠥࡧࡦࡵࡧࡵࠤࢀࢃࠠࡢࡶࡷࡩࡲࡶࡴࡴࠤỿ").format(bstack1111l1llll1_opy_))
    self.bstack11111l1l1l1_opy_ = True
    return False
  def bstack11111llllll_opy_(self, bstack1111l1llll1_opy_ = 0):
    if bstack1111l1llll1_opy_ > 10:
      return False
    try:
      bstack11111lllll1_opy_ = os.environ.get(bstack111l11_opy_ (u"ࠬࡖࡅࡓࡅ࡜ࡣࡘࡋࡒࡗࡇࡕࡣࡆࡊࡄࡓࡇࡖࡗࠬἀ"), bstack111l11_opy_ (u"࠭ࡨࡵࡶࡳ࠾࠴࠵࡬ࡰࡥࡤࡰ࡭ࡵࡳࡵ࠼࠸࠷࠸࠾ࠧἁ"))
      bstack11111ll1l1l_opy_ = bstack11111lllll1_opy_ + bstack11l1l1l1ll1_opy_
      response = requests.get(bstack11111ll1l1l_opy_)
      data = response.json()
      self.percy_build_id = data.get(bstack111l11_opy_ (u"ࠧࡣࡷ࡬ࡰࡩ࠭ἂ"), {}).get(bstack111l11_opy_ (u"ࠨ࡫ࡧࠫἃ"), None)
      return True
    except:
      self.logger.debug(bstack111l11_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡱࡦࡧࡺࡸࡲࡦࡦࠣࡻ࡭࡯࡬ࡦࠢࡳࡶࡴࡩࡥࡴࡵ࡬ࡲ࡬ࠦࡨࡦࡣ࡯ࡸ࡭ࠦࡣࡩࡧࡦ࡯ࠥࡸࡥࡴࡲࡲࡲࡸ࡫ࠢἄ"))
      return False
  def bstack1111l111lll_opy_(self):
    bstack1111l1l1l11_opy_ = bstack111l11_opy_ (u"ࠪࡥࡵࡶࠧἅ") if self.bstack1lllll11l_opy_ else bstack111l11_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭ἆ")
    bstack1111l11l111_opy_ = bstack111l11_opy_ (u"ࠧࡻ࡮ࡥࡧࡩ࡭ࡳ࡫ࡤࠣἇ") if self.config.get(bstack111l11_opy_ (u"࠭ࡰࡦࡴࡦࡽࠬἈ")) is None else True
    bstack11ll111lll1_opy_ = bstack111l11_opy_ (u"ࠢࡢࡲ࡬࠳ࡦࡶࡰࡠࡲࡨࡶࡨࡿ࠯ࡨࡧࡷࡣࡵࡸ࡯࡫ࡧࡦࡸࡤࡺ࡯࡬ࡧࡱࡃࡳࡧ࡭ࡦ࠿ࡾࢁࠫࡺࡹࡱࡧࡀࡿࢂࠬࡰࡦࡴࡦࡽࡂࢁࡽࠣἉ").format(self.config[bstack111l11_opy_ (u"ࠨࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪ࠭Ἂ")], bstack1111l1l1l11_opy_, bstack1111l11l111_opy_)
    if self.percy_capture_mode:
      bstack11ll111lll1_opy_ += bstack111l11_opy_ (u"ࠤࠩࡴࡪࡸࡣࡺࡡࡦࡥࡵࡺࡵࡳࡧࡢࡱࡴࡪࡥ࠾ࡽࢀࠦἋ").format(self.percy_capture_mode)
    uri = bstack11l1l11l1l_opy_(bstack11ll111lll1_opy_)
    try:
      response = bstack11ll1llll_opy_(bstack111l11_opy_ (u"ࠪࡋࡊ࡚ࠧἌ"), uri, {}, {bstack111l11_opy_ (u"ࠫࡦࡻࡴࡩࠩἍ"): (self.config[bstack111l11_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧἎ")], self.config[bstack111l11_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩἏ")])})
      if response.status_code == 200:
        data = response.json()
        self.bstack1l111l1111_opy_ = data.get(bstack111l11_opy_ (u"ࠧࡴࡷࡦࡧࡪࡹࡳࠨἐ"))
        self.percy_capture_mode = data.get(bstack111l11_opy_ (u"ࠨࡲࡨࡶࡨࡿ࡟ࡤࡣࡳࡸࡺࡸࡥࡠ࡯ࡲࡨࡪ࠭ἑ"))
        os.environ[bstack111l11_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡈࡖࡈ࡟ࠧἒ")] = str(self.bstack1l111l1111_opy_)
        os.environ[bstack111l11_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡉࡗࡉ࡙ࡠࡅࡄࡔ࡙࡛ࡒࡆࡡࡐࡓࡉࡋࠧἓ")] = str(self.percy_capture_mode)
        if bstack1111l11l111_opy_ == bstack111l11_opy_ (u"ࠦࡺࡴࡤࡦࡨ࡬ࡲࡪࡪࠢἔ") and str(self.bstack1l111l1111_opy_).lower() == bstack111l11_opy_ (u"ࠧࡺࡲࡶࡧࠥἕ"):
          self.bstack1l111l1lll_opy_ = True
        if bstack111l11_opy_ (u"ࠨࡴࡰ࡭ࡨࡲࠧ἖") in data:
          return data[bstack111l11_opy_ (u"ࠢࡵࡱ࡮ࡩࡳࠨ἗")]
        else:
          raise bstack111l11_opy_ (u"ࠨࡖࡲ࡯ࡪࡴࠠࡏࡱࡷࠤࡋࡵࡵ࡯ࡦࠣ࠱ࠥࢁࡽࠨἘ").format(data)
      else:
        raise bstack111l11_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥ࡬ࡥࡵࡥ࡫ࠤࡵ࡫ࡲࡤࡻࠣࡸࡴࡱࡥ࡯࠮ࠣࡖࡪࡹࡰࡰࡰࡶࡩࠥࡹࡴࡢࡶࡸࡷࠥ࠳ࠠࡼࡿ࠯ࠤࡗ࡫ࡳࡱࡱࡱࡷࡪࠦࡂࡰࡦࡼࠤ࠲ࠦࡻࡾࠤἙ").format(response.status_code, response.json())
    except Exception as e:
      self.logger.error(bstack111l11_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡦࡶࡪࡧࡴࡪࡰࡪࠤࡵ࡫ࡲࡤࡻࠣࡴࡷࡵࡪࡦࡥࡷࠦἚ").format(e))
  def bstack1111l1lll11_opy_(self):
    bstack1111l1111l1_opy_ = os.path.join(tempfile.gettempdir(), bstack111l11_opy_ (u"ࠦࡵ࡫ࡲࡤࡻࡆࡳࡳ࡬ࡩࡨ࠰࡭ࡷࡴࡴࠢἛ"))
    try:
      if bstack111l11_opy_ (u"ࠬࡼࡥࡳࡵ࡬ࡳࡳ࠭Ἔ") not in self.bstack1111l111ll1_opy_:
        self.bstack1111l111ll1_opy_[bstack111l11_opy_ (u"࠭ࡶࡦࡴࡶ࡭ࡴࡴࠧἝ")] = 2
      with open(bstack1111l1111l1_opy_, bstack111l11_opy_ (u"ࠧࡸࠩ἞")) as fp:
        json.dump(self.bstack1111l111ll1_opy_, fp)
      return bstack1111l1111l1_opy_
    except Exception as e:
      self.logger.error(bstack111l11_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤࡨࡸࡥࡢࡶࡨࠤࡵ࡫ࡲࡤࡻࠣࡧࡴࡴࡦ࠭ࠢࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࢁࡽࠣ἟").format(e))
  def bstack1111l1l1l1l_opy_(self, cmd, env = os.environ.copy()):
    try:
      if self.bstack1111l1l1lll_opy_ == bstack111l11_opy_ (u"ࠩࡺ࡭ࡳ࠭ἠ"):
        bstack11111ll1lll_opy_ = [bstack111l11_opy_ (u"ࠪࡧࡲࡪ࠮ࡦࡺࡨࠫἡ"), bstack111l11_opy_ (u"ࠫ࠴ࡩࠧἢ")]
        cmd = bstack11111ll1lll_opy_ + cmd
      cmd = bstack111l11_opy_ (u"ࠬࠦࠧἣ").join(cmd)
      self.logger.debug(bstack111l11_opy_ (u"ࠨࡒࡶࡰࡱ࡭ࡳ࡭ࠠࡼࡿࠥἤ").format(cmd))
      with open(self.bstack1111l1lll1l_opy_, bstack111l11_opy_ (u"ࠢࡢࠤἥ")) as bstack11111lll1l1_opy_:
        process = subprocess.Popen(cmd, shell=True, stdout=bstack11111lll1l1_opy_, text=True, stderr=bstack11111lll1l1_opy_, env=env, universal_newlines=True)
      return process
    except Exception as e:
      self.bstack11111l1l1l1_opy_ = True
      self.logger.error(bstack111l11_opy_ (u"ࠣࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡸࡺࡡࡳࡶࠣࡴࡪࡸࡣࡺࠢࡺ࡭ࡹ࡮ࠠࡤ࡯ࡧࠤ࠲ࠦࡻࡾ࠮ࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࡀࠠࡼࡿࠥἦ").format(cmd, e))
  def shutdown(self):
    try:
      if self.bstack11111lll111_opy_:
        self.logger.info(bstack111l11_opy_ (u"ࠤࡖࡸࡴࡶࡰࡪࡰࡪࠤࡕ࡫ࡲࡤࡻࠥἧ"))
        cmd = [self.binary_path, bstack111l11_opy_ (u"ࠥࡩࡽ࡫ࡣ࠻ࡵࡷࡳࡵࠨἨ")]
        self.bstack1111l1l1l1l_opy_(cmd)
        self.bstack11111lll111_opy_ = False
    except Exception as e:
      self.logger.error(bstack111l11_opy_ (u"ࠦࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡴࡶࡲࡴࠥࡹࡥࡴࡵ࡬ࡳࡳࠦࡷࡪࡶ࡫ࠤࡨࡵ࡭࡮ࡣࡱࡨࠥ࠳ࠠࡼࡿ࠯ࠤࡊࡾࡣࡦࡲࡷ࡭ࡴࡴ࠺ࠡࡽࢀࠦἩ").format(cmd, e))
  def bstack1llllllll1_opy_(self):
    if not self.bstack1l111l1111_opy_:
      return
    try:
      bstack11111ll1111_opy_ = 0
      while not self.bstack11111lll111_opy_ and bstack11111ll1111_opy_ < self.bstack1111l1111ll_opy_:
        if self.bstack11111l1l1l1_opy_:
          self.logger.info(bstack111l11_opy_ (u"ࠧࡖࡥࡳࡥࡼࠤࡸ࡫ࡴࡶࡲࠣࡪࡦ࡯࡬ࡦࡦࠥἪ"))
          return
        time.sleep(1)
        bstack11111ll1111_opy_ += 1
      os.environ[bstack111l11_opy_ (u"࠭ࡐࡆࡔࡆ࡝ࡤࡈࡅࡔࡖࡢࡔࡑࡇࡔࡇࡑࡕࡑࠬἫ")] = str(self.bstack11111l1llll_opy_())
      self.logger.info(bstack111l11_opy_ (u"ࠢࡑࡧࡵࡧࡾࠦࡳࡦࡶࡸࡴࠥࡩ࡯࡮ࡲ࡯ࡩࡹ࡫ࡤࠣἬ"))
    except Exception as e:
      self.logger.error(bstack111l11_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤࡸ࡫ࡴࡶࡲࠣࡴࡪࡸࡣࡺ࠮ࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡻࡾࠤἭ").format(e))
  def bstack11111l1llll_opy_(self):
    if self.bstack1lllll11l_opy_:
      return
    try:
      bstack111111lll11_opy_ = [platform[bstack111l11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧἮ")].lower() for platform in self.config.get(bstack111l11_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭Ἧ"), [])]
      bstack1111l1ll1l1_opy_ = sys.maxsize
      bstack1111l111111_opy_ = bstack111l11_opy_ (u"ࠫࠬἰ")
      for browser in bstack111111lll11_opy_:
        if browser in self.bstack11111l1l1ll_opy_:
          bstack11111l11l1l_opy_ = self.bstack11111l1l1ll_opy_[browser]
        if bstack11111l11l1l_opy_ < bstack1111l1ll1l1_opy_:
          bstack1111l1ll1l1_opy_ = bstack11111l11l1l_opy_
          bstack1111l111111_opy_ = browser
      return bstack1111l111111_opy_
    except Exception as e:
      self.logger.error(bstack111l11_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡨ࡬ࡲࡩࠦࡢࡦࡵࡷࠤࡵࡲࡡࡵࡨࡲࡶࡲ࠲ࠠࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡿࢂࠨἱ").format(e))
  @classmethod
  def bstack11l11ll1ll_opy_(self):
    return os.getenv(bstack111l11_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡅࡓࡅ࡜ࠫἲ"), bstack111l11_opy_ (u"ࠧࡇࡣ࡯ࡷࡪ࠭ἳ")).lower()
  @classmethod
  def bstack1lll1111l_opy_(self):
    return os.getenv(bstack111l11_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡇࡕࡇ࡞ࡥࡃࡂࡒࡗ࡙ࡗࡋ࡟ࡎࡑࡇࡉࠬἴ"), bstack111l11_opy_ (u"ࠩࠪἵ"))
  @classmethod
  def bstack1l1l11ll1l1_opy_(cls, value):
    cls.bstack1l111l1lll_opy_ = value
  @classmethod
  def bstack11111l1ll1l_opy_(cls):
    return cls.bstack1l111l1lll_opy_
  @classmethod
  def bstack1l1l11llll1_opy_(cls, value):
    cls.percy_build_id = value
  @classmethod
  def bstack11111lll11l_opy_(cls):
    return cls.percy_build_id