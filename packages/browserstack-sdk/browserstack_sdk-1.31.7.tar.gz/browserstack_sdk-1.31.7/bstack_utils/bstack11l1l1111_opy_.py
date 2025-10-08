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
import sys
import logging
import tarfile
import io
import os
import time
import requests
import re
from requests_toolbelt.multipart.encoder import MultipartEncoder
from bstack_utils.constants import bstack11l1lll111l_opy_, bstack11l1lll11ll_opy_, bstack11l1llll1l1_opy_
import tempfile
import json
bstack111l1ll11ll_opy_ = os.getenv(bstack111l11_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡑࡕࡇࡠࡈࡌࡐࡊࠨᶷ"), None) or os.path.join(tempfile.gettempdir(), bstack111l11_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡪࡥࡣࡷࡪ࠲ࡱࡵࡧࠣᶸ"))
bstack111l1ll111l_opy_ = os.path.join(bstack111l11_opy_ (u"ࠢ࡭ࡱࡪࠦᶹ"), bstack111l11_opy_ (u"ࠨࡵࡧ࡯࠲ࡩ࡬ࡪ࠯ࡧࡩࡧࡻࡧ࠯࡮ࡲ࡫ࠬᶺ"))
logging.Formatter.converter = time.gmtime
def get_logger(name=__name__, level=None):
  logger = logging.getLogger(name)
  if level:
    logging.basicConfig(
      level=level,
      format=bstack111l11_opy_ (u"ࠩࠨࠬࡦࡹࡣࡵ࡫ࡰࡩ࠮ࡹࠠ࡜ࠧࠫࡲࡦࡳࡥࠪࡵࡠ࡟ࠪ࠮࡬ࡦࡸࡨࡰࡳࡧ࡭ࡦࠫࡶࡡࠥ࠳ࠠࠦࠪࡰࡩࡸࡹࡡࡨࡧࠬࡷࠬᶻ"),
      datefmt=bstack111l11_opy_ (u"ࠪࠩ࡞࠳ࠥ࡮࠯ࠨࡨ࡙ࠫࡈ࠻ࠧࡐ࠾࡙࡚ࠪࠨᶼ"),
      stream=sys.stdout
    )
  return logger
def bstack1ll1ll11l1l_opy_():
  bstack111l1l11l11_opy_ = os.environ.get(bstack111l11_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡆࡎࡔࡁࡓ࡛ࡢࡈࡊࡈࡕࡈࠤᶽ"), bstack111l11_opy_ (u"ࠧ࡬ࡡ࡭ࡵࡨࠦᶾ"))
  return logging.DEBUG if bstack111l1l11l11_opy_.lower() == bstack111l11_opy_ (u"ࠨࡴࡳࡷࡨࠦᶿ") else logging.INFO
def bstack1l1lll11l11_opy_():
  global bstack111l1ll11ll_opy_
  if os.path.exists(bstack111l1ll11ll_opy_):
    os.remove(bstack111l1ll11ll_opy_)
  if os.path.exists(bstack111l1ll111l_opy_):
    os.remove(bstack111l1ll111l_opy_)
def bstack11lll1ll1l_opy_():
  for handler in logging.getLogger().handlers:
    logging.getLogger().removeHandler(handler)
def configure_logger(config, log_level):
  bstack111l1l1l1ll_opy_ = log_level
  if bstack111l11_opy_ (u"ࠧ࡭ࡱࡪࡐࡪࡼࡥ࡭ࠩ᷀") in config and config[bstack111l11_opy_ (u"ࠨ࡮ࡲ࡫ࡑ࡫ࡶࡦ࡮ࠪ᷁")] in bstack11l1lll11ll_opy_:
    bstack111l1l1l1ll_opy_ = bstack11l1lll11ll_opy_[config[bstack111l11_opy_ (u"ࠩ࡯ࡳ࡬ࡒࡥࡷࡧ࡯᷂ࠫ")]]
  if config.get(bstack111l11_opy_ (u"ࠪࡨ࡮ࡹࡡࡣ࡮ࡨࡅࡺࡺ࡯ࡄࡣࡳࡸࡺࡸࡥࡍࡱࡪࡷࠬ᷃"), False):
    logging.getLogger().setLevel(bstack111l1l1l1ll_opy_)
    return bstack111l1l1l1ll_opy_
  global bstack111l1ll11ll_opy_
  bstack11lll1ll1l_opy_()
  bstack111l1ll1l11_opy_ = logging.Formatter(
    fmt=bstack111l11_opy_ (u"ࠫࠪ࠮ࡡࡴࡥࡷ࡭ࡲ࡫ࠩࡴࠢ࡞ࠩ࠭ࡴࡡ࡮ࡧࠬࡷࡢࡡࠥࠩ࡮ࡨࡺࡪࡲ࡮ࡢ࡯ࡨ࠭ࡸࡣࠠ࠮ࠢࠨࠬࡲ࡫ࡳࡴࡣࡪࡩ࠮ࡹࠧ᷄"),
    datefmt=bstack111l11_opy_ (u"࡙ࠬࠫ࠮ࠧࡰ࠱ࠪࡪࡔࠦࡊ࠽ࠩࡒࡀࠥࡔ࡜ࠪ᷅"),
  )
  bstack111l1ll1l1l_opy_ = logging.StreamHandler(sys.stdout)
  file_handler = logging.FileHandler(bstack111l1ll11ll_opy_)
  file_handler.setFormatter(bstack111l1ll1l11_opy_)
  bstack111l1ll1l1l_opy_.setFormatter(bstack111l1ll1l11_opy_)
  file_handler.setLevel(logging.DEBUG)
  bstack111l1ll1l1l_opy_.setLevel(log_level)
  file_handler.addFilter(lambda r: r.name != bstack111l11_opy_ (u"࠭ࡳࡦ࡮ࡨࡲ࡮ࡻ࡭࠯ࡹࡨࡦࡩࡸࡩࡷࡧࡵ࠲ࡷ࡫࡭ࡰࡶࡨ࠲ࡷ࡫࡭ࡰࡶࡨࡣࡨࡵ࡮࡯ࡧࡦࡸ࡮ࡵ࡮ࠨ᷆"))
  logging.getLogger().setLevel(logging.DEBUG)
  bstack111l1ll1l1l_opy_.setLevel(bstack111l1l1l1ll_opy_)
  logging.getLogger().addHandler(bstack111l1ll1l1l_opy_)
  logging.getLogger().addHandler(file_handler)
  return bstack111l1l1l1ll_opy_
def bstack111l1l1ll1l_opy_(config):
  try:
    bstack111l1ll11l1_opy_ = set(bstack11l1llll1l1_opy_)
    bstack111l1l11l1l_opy_ = bstack111l11_opy_ (u"ࠧࠨ᷇")
    with open(bstack111l11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡺ࡯࡯ࠫ᷈")) as bstack111l1l1l111_opy_:
      bstack111l1ll1ll1_opy_ = bstack111l1l1l111_opy_.read()
      bstack111l1l11l1l_opy_ = re.sub(bstack111l11_opy_ (u"ࡴࠪࡢ࠭ࡢࡳࠬࠫࡂࠧ࠳࠰ࠤ࡝ࡰࠪ᷉"), bstack111l11_opy_ (u"᷊ࠪࠫ"), bstack111l1ll1ll1_opy_, flags=re.M)
      bstack111l1l11l1l_opy_ = re.sub(
        bstack111l11_opy_ (u"ࡶࠬࡤࠨ࡝ࡵ࠮࠭ࡄ࠮ࠧ᷋") + bstack111l11_opy_ (u"ࠬࢂࠧ᷌").join(bstack111l1ll11l1_opy_) + bstack111l11_opy_ (u"࠭ࠩ࠯ࠬࠧࠫ᷍"),
        bstack111l11_opy_ (u"ࡲࠨ࡞࠵࠾ࠥࡡࡒࡆࡆࡄࡇ࡙ࡋࡄ࡞᷎ࠩ"),
        bstack111l1l11l1l_opy_, flags=re.M | re.I
      )
    def bstack111l1ll1111_opy_(dic):
      bstack111l1lll111_opy_ = {}
      for key, value in dic.items():
        if key in bstack111l1ll11l1_opy_:
          bstack111l1lll111_opy_[key] = bstack111l11_opy_ (u"ࠨ࡝ࡕࡉࡉࡇࡃࡕࡇࡇࡡ᷏ࠬ")
        else:
          if isinstance(value, dict):
            bstack111l1lll111_opy_[key] = bstack111l1ll1111_opy_(value)
          else:
            bstack111l1lll111_opy_[key] = value
      return bstack111l1lll111_opy_
    bstack111l1lll111_opy_ = bstack111l1ll1111_opy_(config)
    return {
      bstack111l11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡻࡰࡰ᷐ࠬ"): bstack111l1l11l1l_opy_,
      bstack111l11_opy_ (u"ࠪࡪ࡮ࡴࡡ࡭ࡥࡲࡲ࡫࡯ࡧ࠯࡬ࡶࡳࡳ࠭᷑"): json.dumps(bstack111l1lll111_opy_)
    }
  except Exception as e:
    return {}
def bstack111l1l1llll_opy_(inipath, rootpath):
  log_dir = os.path.join(os.getcwd(), bstack111l11_opy_ (u"ࠫࡱࡵࡧࠨ᷒"))
  if not os.path.exists(log_dir):
    os.makedirs(log_dir)
  bstack111l1l1lll1_opy_ = os.path.join(log_dir, bstack111l11_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࡤࡩ࡯࡯ࡨ࡬࡫ࡸ࠭ᷓ"))
  if not os.path.exists(bstack111l1l1lll1_opy_):
    bstack111l1l111l1_opy_ = {
      bstack111l11_opy_ (u"ࠨࡩ࡯࡫ࡳࡥࡹ࡮ࠢᷔ"): str(inipath),
      bstack111l11_opy_ (u"ࠢࡳࡱࡲࡸࡵࡧࡴࡩࠤᷕ"): str(rootpath)
    }
    with open(os.path.join(log_dir, bstack111l11_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡠࡥࡲࡲ࡫࡯ࡧࡴ࠰࡭ࡷࡴࡴࠧᷖ")), bstack111l11_opy_ (u"ࠩࡺࠫᷗ")) as bstack111l1l1ll11_opy_:
      bstack111l1l1ll11_opy_.write(json.dumps(bstack111l1l111l1_opy_))
def bstack111l1l1111l_opy_():
  try:
    bstack111l1l1lll1_opy_ = os.path.join(os.getcwd(), bstack111l11_opy_ (u"ࠪࡰࡴ࡭ࠧᷘ"), bstack111l11_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࡣࡨࡵ࡮ࡧ࡫ࡪࡷ࠳ࡰࡳࡰࡰࠪᷙ"))
    if os.path.exists(bstack111l1l1lll1_opy_):
      with open(bstack111l1l1lll1_opy_, bstack111l11_opy_ (u"ࠬࡸࠧᷚ")) as bstack111l1l1ll11_opy_:
        bstack111l1l11lll_opy_ = json.load(bstack111l1l1ll11_opy_)
      return bstack111l1l11lll_opy_.get(bstack111l11_opy_ (u"࠭ࡩ࡯࡫ࡳࡥࡹ࡮ࠧᷛ"), bstack111l11_opy_ (u"ࠧࠨᷜ")), bstack111l1l11lll_opy_.get(bstack111l11_opy_ (u"ࠨࡴࡲࡳࡹࡶࡡࡵࡪࠪᷝ"), bstack111l11_opy_ (u"ࠩࠪᷞ"))
  except:
    pass
  return None, None
def bstack111l1l11ll1_opy_():
  try:
    bstack111l1l1lll1_opy_ = os.path.join(os.getcwd(), bstack111l11_opy_ (u"ࠪࡰࡴ࡭ࠧᷟ"), bstack111l11_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࡣࡨࡵ࡮ࡧ࡫ࡪࡷ࠳ࡰࡳࡰࡰࠪᷠ"))
    if os.path.exists(bstack111l1l1lll1_opy_):
      os.remove(bstack111l1l1lll1_opy_)
  except:
    pass
def bstack11l1ll111_opy_(config):
  try:
    from bstack_utils.helper import bstack1llll1111_opy_, bstack1l1ll1lll1_opy_
    from browserstack_sdk.sdk_cli.cli import cli
    global bstack111l1ll11ll_opy_
    if config.get(bstack111l11_opy_ (u"ࠬࡪࡩࡴࡣࡥࡰࡪࡇࡵࡵࡱࡆࡥࡵࡺࡵࡳࡧࡏࡳ࡬ࡹࠧᷡ"), False):
      return
    uuid = os.getenv(bstack111l11_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫᷢ")) if os.getenv(bstack111l11_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬᷣ")) else bstack1llll1111_opy_.get_property(bstack111l11_opy_ (u"ࠣࡵࡧ࡯ࡗࡻ࡮ࡊࡦࠥᷤ"))
    if not uuid or uuid == bstack111l11_opy_ (u"ࠩࡱࡹࡱࡲࠧᷥ"):
      return
    bstack111l1l1l1l1_opy_ = [bstack111l11_opy_ (u"ࠪࡶࡪࡷࡵࡪࡴࡨࡱࡪࡴࡴࡴ࠰ࡷࡼࡹ࠭ᷦ"), bstack111l11_opy_ (u"ࠫࡕ࡯ࡰࡧ࡫࡯ࡩࠬᷧ"), bstack111l11_opy_ (u"ࠬࡶࡹࡱࡴࡲ࡮ࡪࡩࡴ࠯ࡶࡲࡱࡱ࠭ᷨ"), bstack111l1ll11ll_opy_, bstack111l1ll111l_opy_]
    bstack111l1ll1lll_opy_, root_path = bstack111l1l1111l_opy_()
    if bstack111l1ll1lll_opy_ != None:
      bstack111l1l1l1l1_opy_.append(bstack111l1ll1lll_opy_)
    if root_path != None:
      bstack111l1l1l1l1_opy_.append(os.path.join(root_path, bstack111l11_opy_ (u"࠭ࡣࡰࡰࡩࡸࡪࡹࡴ࠯ࡲࡼࠫᷩ")))
    bstack11lll1ll1l_opy_()
    logging.shutdown()
    output_file = os.path.join(tempfile.gettempdir(), bstack111l11_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠭࡭ࡱࡪࡷ࠲࠭ᷪ") + uuid + bstack111l11_opy_ (u"ࠨ࠰ࡷࡥࡷ࠴ࡧࡻࠩᷫ"))
    with tarfile.open(output_file, bstack111l11_opy_ (u"ࠤࡺ࠾࡬ࢀࠢᷬ")) as archive:
      for file in filter(lambda f: os.path.exists(f), bstack111l1l1l1l1_opy_):
        try:
          archive.add(file,  arcname=os.path.basename(file))
        except:
          pass
      for name, data in bstack111l1l1ll1l_opy_(config).items():
        tarinfo = tarfile.TarInfo(name)
        bstack111l1l1l11l_opy_ = data.encode()
        tarinfo.size = len(bstack111l1l1l11l_opy_)
        archive.addfile(tarinfo, io.BytesIO(bstack111l1l1l11l_opy_))
    bstack111ll111_opy_ = MultipartEncoder(
      fields= {
        bstack111l11_opy_ (u"ࠪࡨࡦࡺࡡࠨᷭ"): (os.path.basename(output_file), open(os.path.abspath(output_file), bstack111l11_opy_ (u"ࠫࡷࡨࠧᷮ")), bstack111l11_opy_ (u"ࠬࡧࡰࡱ࡮࡬ࡧࡦࡺࡩࡰࡰ࠲ࡼ࠲࡭ࡺࡪࡲࠪᷯ")),
        bstack111l11_opy_ (u"࠭ࡣ࡭࡫ࡨࡲࡹࡈࡵࡪ࡮ࡧ࡙ࡺ࡯ࡤࠨᷰ"): uuid
      }
    )
    bstack111l1l111ll_opy_ = bstack1l1ll1lll1_opy_(cli.config, [bstack111l11_opy_ (u"ࠢࡢࡲ࡬ࡷࠧᷱ"), bstack111l11_opy_ (u"ࠣࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࠣᷲ"), bstack111l11_opy_ (u"ࠤࡸࡴࡱࡵࡡࡥࠤᷳ")], bstack11l1lll111l_opy_)
    response = requests.post(
      bstack111l11_opy_ (u"ࠥࡿࢂ࠵ࡣ࡭࡫ࡨࡲࡹ࠳࡬ࡰࡩࡶ࠳ࡺࡶ࡬ࡰࡣࡧࠦᷴ").format(bstack111l1l111ll_opy_),
      data=bstack111ll111_opy_,
      headers={bstack111l11_opy_ (u"ࠫࡈࡵ࡮ࡵࡧࡱࡸ࠲࡚ࡹࡱࡧࠪ᷵"): bstack111ll111_opy_.content_type},
      auth=(config[bstack111l11_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧ᷶")], config[bstack111l11_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺ᷷ࠩ")])
    )
    os.remove(output_file)
    if response.status_code != 200:
      get_logger().debug(bstack111l11_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡵࡱ࡮ࡲࡥࡩࠦ࡬ࡰࡩࡶ࠾᷸ࠥ࠭") + response.status_code)
  except Exception as e:
    get_logger().debug(bstack111l11_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡴࡧࡱࡨ࡮ࡴࡧࠡ࡮ࡲ࡫ࡸࡀ᷹ࠧ") + str(e))
  finally:
    try:
      bstack1l1lll11l11_opy_()
      bstack111l1l11ll1_opy_()
    except:
      pass