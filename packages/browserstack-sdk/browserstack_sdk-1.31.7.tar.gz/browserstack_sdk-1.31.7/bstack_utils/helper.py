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
import collections
import datetime
import json
import os
import platform
import re
import subprocess
import traceback
import tempfile
import multiprocessing
import threading
import sys
import logging
from math import ceil
from unittest import result
import urllib
from urllib.parse import urlparse
import copy
import zipfile
import git
import requests
from packaging import version
from bstack_utils.config import Config
from bstack_utils.constants import (bstack1l1lll1l1l_opy_, bstack1l1llllll_opy_, bstack1l11l111l1_opy_,
                                    bstack11l1ll11111_opy_, bstack11l1llll11l_opy_, bstack11l1llll1l1_opy_, bstack11l1lll1ll1_opy_)
from bstack_utils.measure import measure
from bstack_utils.messages import bstack1lllll1111_opy_, bstack11lll1l11l_opy_
from bstack_utils.proxy import bstack111lllll11_opy_, bstack1l11l11l_opy_
from bstack_utils.constants import *
from bstack_utils import bstack11l1l1111_opy_
from bstack_utils.bstack1l1l1ll11l_opy_ import bstack11l1l11l1l_opy_
from browserstack_sdk._version import __version__
bstack1llll1111_opy_ = Config.bstack1lll111l11_opy_()
logger = bstack11l1l1111_opy_.get_logger(__name__, bstack11l1l1111_opy_.bstack1ll1ll11l1l_opy_())
def bstack11ll1l11lll_opy_(config):
    return config[bstack111l11_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭ᬖ")]
def bstack11ll1ll1ll1_opy_(config):
    return config[bstack111l11_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨᬗ")]
def bstack11l1l1l1_opy_():
    try:
        import playwright
        return True
    except ImportError:
        return False
def bstack111lll1ll1l_opy_(obj):
    values = []
    bstack11l11l1ll11_opy_ = re.compile(bstack111l11_opy_ (u"ࡸࠢ࡟ࡅࡘࡗ࡙ࡕࡍࡠࡖࡄࡋࡤࡢࡤࠬࠦࠥᬘ"), re.I)
    for key in obj.keys():
        if bstack11l11l1ll11_opy_.match(key):
            values.append(obj[key])
    return values
def bstack11l11ll1111_opy_(config):
    tags = []
    tags.extend(bstack111lll1ll1l_opy_(os.environ))
    tags.extend(bstack111lll1ll1l_opy_(config))
    return tags
def bstack11l111lllll_opy_(markers):
    tags = []
    for marker in markers:
        tags.append(marker.name)
    return tags
def bstack11l11l1111l_opy_(bstack111ll11lll1_opy_):
    if not bstack111ll11lll1_opy_:
        return bstack111l11_opy_ (u"ࠧࠨᬙ")
    return bstack111l11_opy_ (u"ࠣࡽࢀࠤ࠭ࢁࡽࠪࠤᬚ").format(bstack111ll11lll1_opy_.name, bstack111ll11lll1_opy_.email)
def bstack11ll1l1ll1l_opy_():
    try:
        repo = git.Repo(search_parent_directories=True)
        bstack111ll1lll1l_opy_ = repo.common_dir
        info = {
            bstack111l11_opy_ (u"ࠤࡶ࡬ࡦࠨᬛ"): repo.head.commit.hexsha,
            bstack111l11_opy_ (u"ࠥࡷ࡭ࡵࡲࡵࡡࡶ࡬ࡦࠨᬜ"): repo.git.rev_parse(repo.head.commit, short=True),
            bstack111l11_opy_ (u"ࠦࡧࡸࡡ࡯ࡥ࡫ࠦᬝ"): repo.active_branch.name,
            bstack111l11_opy_ (u"ࠧࡺࡡࡨࠤᬞ"): repo.git.describe(all=True, tags=True, exact_match=True),
            bstack111l11_opy_ (u"ࠨࡣࡰ࡯ࡰ࡭ࡹࡺࡥࡳࠤᬟ"): bstack11l11l1111l_opy_(repo.head.commit.committer),
            bstack111l11_opy_ (u"ࠢࡤࡱࡰࡱ࡮ࡺࡴࡦࡴࡢࡨࡦࡺࡥࠣᬠ"): repo.head.commit.committed_datetime.isoformat(),
            bstack111l11_opy_ (u"ࠣࡣࡸࡸ࡭ࡵࡲࠣᬡ"): bstack11l11l1111l_opy_(repo.head.commit.author),
            bstack111l11_opy_ (u"ࠤࡤࡹࡹ࡮࡯ࡳࡡࡧࡥࡹ࡫ࠢᬢ"): repo.head.commit.authored_datetime.isoformat(),
            bstack111l11_opy_ (u"ࠥࡧࡴࡳ࡭ࡪࡶࡢࡱࡪࡹࡳࡢࡩࡨࠦᬣ"): repo.head.commit.message,
            bstack111l11_opy_ (u"ࠦࡷࡵ࡯ࡵࠤᬤ"): repo.git.rev_parse(bstack111l11_opy_ (u"ࠧ࠳࠭ࡴࡪࡲࡻ࠲ࡺ࡯ࡱ࡮ࡨࡺࡪࡲࠢᬥ")),
            bstack111l11_opy_ (u"ࠨࡣࡰ࡯ࡰࡳࡳࡥࡧࡪࡶࡢࡨ࡮ࡸࠢᬦ"): bstack111ll1lll1l_opy_,
            bstack111l11_opy_ (u"ࠢࡸࡱࡵ࡯ࡹࡸࡥࡦࡡࡪ࡭ࡹࡥࡤࡪࡴࠥᬧ"): subprocess.check_output([bstack111l11_opy_ (u"ࠣࡩ࡬ࡸࠧᬨ"), bstack111l11_opy_ (u"ࠤࡵࡩࡻ࠳ࡰࡢࡴࡶࡩࠧᬩ"), bstack111l11_opy_ (u"ࠥ࠱࠲࡭ࡩࡵ࠯ࡦࡳࡲࡳ࡯࡯࠯ࡧ࡭ࡷࠨᬪ")]).strip().decode(
                bstack111l11_opy_ (u"ࠫࡺࡺࡦ࠮࠺ࠪᬫ")),
            bstack111l11_opy_ (u"ࠧࡲࡡࡴࡶࡢࡸࡦ࡭ࠢᬬ"): repo.git.describe(tags=True, abbrev=0, always=True),
            bstack111l11_opy_ (u"ࠨࡣࡰ࡯ࡰ࡭ࡹࡹ࡟ࡴ࡫ࡱࡧࡪࡥ࡬ࡢࡵࡷࡣࡹࡧࡧࠣᬭ"): repo.git.rev_list(
                bstack111l11_opy_ (u"ࠢࡼࡿ࠱࠲ࢀࢃࠢᬮ").format(repo.head.commit, repo.git.describe(tags=True, abbrev=0, always=True)), count=True)
        }
        remotes = repo.remotes
        bstack111lll1ll11_opy_ = []
        for remote in remotes:
            bstack11l11ll1ll1_opy_ = {
                bstack111l11_opy_ (u"ࠣࡰࡤࡱࡪࠨᬯ"): remote.name,
                bstack111l11_opy_ (u"ࠤࡸࡶࡱࠨᬰ"): remote.url,
            }
            bstack111lll1ll11_opy_.append(bstack11l11ll1ll1_opy_)
        bstack11l111lll1l_opy_ = {
            bstack111l11_opy_ (u"ࠥࡲࡦࡳࡥࠣᬱ"): bstack111l11_opy_ (u"ࠦ࡬࡯ࡴࠣᬲ"),
            **info,
            bstack111l11_opy_ (u"ࠧࡸࡥ࡮ࡱࡷࡩࡸࠨᬳ"): bstack111lll1ll11_opy_
        }
        bstack11l111lll1l_opy_ = bstack11l111ll11l_opy_(bstack11l111lll1l_opy_)
        return bstack11l111lll1l_opy_
    except git.InvalidGitRepositoryError:
        return {}
    except Exception as err:
        print(bstack111l11_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶ࡯ࡱࡷ࡯ࡥࡹ࡯࡮ࡨࠢࡊ࡭ࡹࠦ࡭ࡦࡶࡤࡨࡦࡺࡡࠡࡹ࡬ࡸ࡭ࠦࡥࡳࡴࡲࡶ࠿ࠦࡻࡾࠤ᬴").format(err))
        return {}
def bstack111ll1l1lll_opy_(bstack111ll11llll_opy_=None):
    bstack111l11_opy_ (u"ࠢࠣࠤࠍࠤࠥࠦࠠࡈࡧࡷࠤ࡬࡯ࡴࠡ࡯ࡨࡸࡦࡪࡡࡵࡣࠣࡷࡵ࡫ࡣࡪࡨ࡬ࡧࡦࡲ࡬ࡺࠢࡩࡳࡷࡳࡡࡵࡶࡨࡨࠥ࡬࡯ࡳࠢࡄࡍࠥࡹࡥ࡭ࡧࡦࡸ࡮ࡵ࡮ࠡࡷࡶࡩࠥࡩࡡࡴࡧࡶࠤ࡫ࡵࡲࠡࡧࡤࡧ࡭ࠦࡦࡰ࡮ࡧࡩࡷࠦࡩ࡯ࠢࡷ࡬ࡪࠦ࡬ࡪࡵࡷ࠲ࠏࠦࠠࠡࠢࡄࡶ࡬ࡹ࠺ࠋࠢࠣࠤࠥࠦࠠࠡࠢࡩࡳࡱࡪࡥࡳࡵࠣࠬࡱ࡯ࡳࡵ࠮ࠣࡳࡵࡺࡩࡰࡰࡤࡰ࠮ࡀࠠࡍ࡫ࡶࡸࠥࡵࡦࠡࡨࡲࡰࡩ࡫ࡲࠡࡲࡤࡸ࡭ࡹࠠࡵࡱࠣࡩࡽࡺࡲࡢࡥࡷࠤ࡬࡯ࡴࠡ࡯ࡨࡸࡦࡪࡡࡵࡣࠣࡪࡷࡵ࡭࠯ࠢࡇࡩ࡫ࡧࡵ࡭ࡶࡶࠤࡹࡵࠠ࡜ࡱࡶ࠲࡬࡫ࡴࡤࡹࡧࠬ࠮ࡣ࠮ࠋࠢࠣࠤࠥࡘࡥࡵࡷࡵࡲࡸࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡ࡮࡬ࡷࡹࡀࠠࡍ࡫ࡶࡸࠥࡵࡦࠡࡦ࡬ࡧࡹࡹࠬࠡࡧࡤࡧ࡭ࠦࡣࡰࡰࡷࡥ࡮ࡴࡩ࡯ࡩࠣ࡫࡮ࡺࠠ࡮ࡧࡷࡥࡩࡧࡴࡢࠢࡩࡳࡷࠦࡡࠡࡨࡲࡰࡩ࡫ࡲ࠯ࠌࠣࠤࠥࠦࠢࠣࠤᬵ")
    if not bstack111ll11llll_opy_: # bstack11l11l1llll_opy_ for bstack11l1111lll1_opy_-repo
        bstack111ll11llll_opy_ = [os.getcwd()]
    results = []
    for folder in bstack111ll11llll_opy_:
        try:
            repo = git.Repo(folder, search_parent_directories=True)
            result = {
                bstack111l11_opy_ (u"ࠣࡲࡵࡍࡩࠨᬶ"): bstack111l11_opy_ (u"ࠤࠥᬷ"),
                bstack111l11_opy_ (u"ࠥࡪ࡮ࡲࡥࡴࡅ࡫ࡥࡳ࡭ࡥࡥࠤᬸ"): [],
                bstack111l11_opy_ (u"ࠦࡦࡻࡴࡩࡱࡵࡷࠧᬹ"): [],
                bstack111l11_opy_ (u"ࠧࡶࡲࡅࡣࡷࡩࠧᬺ"): bstack111l11_opy_ (u"ࠨࠢᬻ"),
                bstack111l11_opy_ (u"ࠢࡤࡱࡰࡱ࡮ࡺࡍࡦࡵࡶࡥ࡬࡫ࡳࠣᬼ"): [],
                bstack111l11_opy_ (u"ࠣࡲࡵࡘ࡮ࡺ࡬ࡦࠤᬽ"): bstack111l11_opy_ (u"ࠤࠥᬾ"),
                bstack111l11_opy_ (u"ࠥࡴࡷࡊࡥࡴࡥࡵ࡭ࡵࡺࡩࡰࡰࠥᬿ"): bstack111l11_opy_ (u"ࠦࠧᭀ"),
                bstack111l11_opy_ (u"ࠧࡶࡲࡓࡣࡺࡈ࡮࡬ࡦࠣᭁ"): bstack111l11_opy_ (u"ࠨࠢᭂ")
            }
            bstack11l11lll1l1_opy_ = repo.active_branch.name
            bstack11l111l1ll1_opy_ = repo.head.commit
            result[bstack111l11_opy_ (u"ࠢࡱࡴࡌࡨࠧᭃ")] = bstack11l111l1ll1_opy_.hexsha
            bstack111llll111l_opy_ = _111llllll11_opy_(repo)
            logger.debug(bstack111l11_opy_ (u"ࠣࡄࡤࡷࡪࠦࡢࡳࡣࡱࡧ࡭ࠦࡦࡰࡴࠣࡧࡴࡳࡰࡢࡴ࡬ࡷࡴࡴ࠺ࠡࠤ᭄") + str(bstack111llll111l_opy_) + bstack111l11_opy_ (u"ࠤࠥᭅ"))
            if bstack111llll111l_opy_:
                try:
                    bstack11l1111l1l1_opy_ = repo.git.diff(bstack111l11_opy_ (u"ࠥ࠱࠲ࡴࡡ࡮ࡧ࠰ࡳࡳࡲࡹࠣᭆ"), bstack111111ll11_opy_ (u"ࠦࢀࡨࡡࡴࡧࡢࡦࡷࡧ࡮ࡤࡪࢀ࠲࠳࠴ࡻࡤࡷࡵࡶࡪࡴࡴࡠࡤࡵࡥࡳࡩࡨࡾࠤᭇ")).split(bstack111l11_opy_ (u"ࠬࡢ࡮ࠨᭈ"))
                    logger.debug(bstack111l11_opy_ (u"ࠨࡃࡩࡣࡱ࡫ࡪࡪࠠࡧ࡫࡯ࡩࡸࠦࡢࡦࡶࡺࡩࡪࡴࠠࡼࡤࡤࡷࡪࡥࡢࡳࡣࡱࡧ࡭ࢃࠠࡢࡰࡧࠤࢀࡩࡵࡳࡴࡨࡲࡹࡥࡢࡳࡣࡱࡧ࡭ࢃ࠺ࠡࠤᭉ") + str(bstack11l1111l1l1_opy_) + bstack111l11_opy_ (u"ࠢࠣᭊ"))
                    result[bstack111l11_opy_ (u"ࠣࡨ࡬ࡰࡪࡹࡃࡩࡣࡱ࡫ࡪࡪࠢᭋ")] = [f.strip() for f in bstack11l1111l1l1_opy_ if f.strip()]
                    commits = list(repo.iter_commits(bstack111111ll11_opy_ (u"ࠤࡾࡦࡦࡹࡥࡠࡤࡵࡥࡳࡩࡨࡾ࠰࠱ࡿࡨࡻࡲࡳࡧࡱࡸࡤࡨࡲࡢࡰࡦ࡬ࢂࠨᭌ")))
                except Exception:
                    logger.debug(bstack111l11_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡧࡦࡶࠣࡧ࡭ࡧ࡮ࡨࡧࡧࠤ࡫࡯࡬ࡦࡵࠣࡪࡷࡵ࡭ࠡࡤࡵࡥࡳࡩࡨࠡࡥࡲࡱࡵࡧࡲࡪࡵࡲࡲ࠳ࠦࡆࡢ࡮࡯࡭ࡳ࡭ࠠࡣࡣࡦ࡯ࠥࡺ࡯ࠡࡴࡨࡧࡪࡴࡴࠡࡥࡲࡱࡲ࡯ࡴࡴ࠰ࠥ᭍"))
                    commits = list(repo.iter_commits(max_count=10))
                    if commits:
                        result[bstack111l11_opy_ (u"ࠦ࡫࡯࡬ࡦࡵࡆ࡬ࡦࡴࡧࡦࡦࠥ᭎")] = _11l111l1111_opy_(commits[:5])
            else:
                commits = list(repo.iter_commits(max_count=10))
                if commits:
                    result[bstack111l11_opy_ (u"ࠧ࡬ࡩ࡭ࡧࡶࡇ࡭ࡧ࡮ࡨࡧࡧࠦ᭏")] = _11l111l1111_opy_(commits[:5])
            bstack111llll1l11_opy_ = set()
            bstack111ll1l11l1_opy_ = []
            for commit in commits:
                logger.debug(bstack111l11_opy_ (u"ࠨࡐࡳࡱࡦࡩࡸࡹࡩ࡯ࡩࠣࡧࡴࡳ࡭ࡪࡶ࠽ࠤࠧ᭐") + str(commit.message) + bstack111l11_opy_ (u"ࠢࠣ᭑"))
                bstack11l11l1l11l_opy_ = commit.author.name if commit.author else bstack111l11_opy_ (u"ࠣࡗࡱ࡯ࡳࡵࡷ࡯ࠤ᭒")
                bstack111llll1l11_opy_.add(bstack11l11l1l11l_opy_)
                bstack111ll1l11l1_opy_.append({
                    bstack111l11_opy_ (u"ࠤࡰࡩࡸࡹࡡࡨࡧࠥ᭓"): commit.message.strip(),
                    bstack111l11_opy_ (u"ࠥࡹࡸ࡫ࡲࠣ᭔"): bstack11l11l1l11l_opy_
                })
            result[bstack111l11_opy_ (u"ࠦࡦࡻࡴࡩࡱࡵࡷࠧ᭕")] = list(bstack111llll1l11_opy_)
            result[bstack111l11_opy_ (u"ࠧࡩ࡯࡮࡯࡬ࡸࡒ࡫ࡳࡴࡣࡪࡩࡸࠨ᭖")] = bstack111ll1l11l1_opy_
            result[bstack111l11_opy_ (u"ࠨࡰࡳࡆࡤࡸࡪࠨ᭗")] = bstack11l111l1ll1_opy_.committed_datetime.strftime(bstack111l11_opy_ (u"࡛ࠢࠦ࠰ࠩࡲ࠳ࠥࡥࠤ᭘"))
            if (not result[bstack111l11_opy_ (u"ࠣࡲࡵࡘ࡮ࡺ࡬ࡦࠤ᭙")] or result[bstack111l11_opy_ (u"ࠤࡳࡶ࡙࡯ࡴ࡭ࡧࠥ᭚")].strip() == bstack111l11_opy_ (u"ࠥࠦ᭛")) and bstack11l111l1ll1_opy_.message:
                bstack111llll1ll1_opy_ = bstack11l111l1ll1_opy_.message.strip().splitlines()
                result[bstack111l11_opy_ (u"ࠦࡵࡸࡔࡪࡶ࡯ࡩࠧ᭜")] = bstack111llll1ll1_opy_[0] if bstack111llll1ll1_opy_ else bstack111l11_opy_ (u"ࠧࠨ᭝")
                if len(bstack111llll1ll1_opy_) > 2:
                    result[bstack111l11_opy_ (u"ࠨࡰࡳࡆࡨࡷࡨࡸࡩࡱࡶ࡬ࡳࡳࠨ᭞")] = bstack111l11_opy_ (u"ࠧ࡝ࡰࠪ᭟").join(bstack111llll1ll1_opy_[2:]).strip()
            results.append(result)
        except Exception as err:
            logger.error(bstack111l11_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱࡱࡳࡹࡱࡧࡴࡪࡰࡪࠤࡌ࡯ࡴࠡ࡯ࡨࡸࡦࡪࡡࡵࡣࠣࡪࡴࡸࠠࡂࡋࠣࡷࡪࡲࡥࡤࡶ࡬ࡳࡳࠦࠨࡧࡱ࡯ࡨࡪࡸ࠺ࠡࡽࡩࡳࡱࡪࡥࡳࡿࠬ࠾ࠥࠨ᭠") + str(err) + bstack111l11_opy_ (u"ࠤࠥ᭡"))
    filtered_results = [
        r
        for r in results
        if _11l11l1l1ll_opy_(r)
    ]
    return filtered_results
def _11l11l1l1ll_opy_(result):
    bstack111l11_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࡌࡪࡲࡰࡦࡴࠣࡸࡴࠦࡣࡩࡧࡦ࡯ࠥ࡯ࡦࠡࡣࠣ࡫࡮ࡺࠠ࡮ࡧࡷࡥࡩࡧࡴࡢࠢࡵࡩࡸࡻ࡬ࡵࠢ࡬ࡷࠥࡼࡡ࡭࡫ࡧࠤ࠭ࡴ࡯࡯࠯ࡨࡱࡵࡺࡹࠡࡨ࡬ࡰࡪࡹࡃࡩࡣࡱ࡫ࡪࡪࠠࡢࡰࡧࠤࡦࡻࡴࡩࡱࡵࡷ࠮࠴ࠊࠡࠢࠣࠤࠧࠨࠢ᭢")
    return (
        isinstance(result.get(bstack111l11_opy_ (u"ࠦ࡫࡯࡬ࡦࡵࡆ࡬ࡦࡴࡧࡦࡦࠥ᭣"), None), list)
        and len(result[bstack111l11_opy_ (u"ࠧ࡬ࡩ࡭ࡧࡶࡇ࡭ࡧ࡮ࡨࡧࡧࠦ᭤")]) > 0
        and isinstance(result.get(bstack111l11_opy_ (u"ࠨࡡࡶࡶ࡫ࡳࡷࡹࠢ᭥"), None), list)
        and len(result[bstack111l11_opy_ (u"ࠢࡢࡷࡷ࡬ࡴࡸࡳࠣ᭦")]) > 0
    )
def _111llllll11_opy_(repo):
    bstack111l11_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࡖࡵࡽࠥࡺ࡯ࠡࡦࡨࡸࡪࡸ࡭ࡪࡰࡨࠤࡹ࡮ࡥࠡࡤࡤࡷࡪࠦࡢࡳࡣࡱࡧ࡭ࠦࡦࡰࡴࠣࡸ࡭࡫ࠠࡨ࡫ࡹࡩࡳࠦࡲࡦࡲࡲࠤࡼ࡯ࡴࡩࡱࡸࡸࠥ࡮ࡡࡳࡦࡦࡳࡩ࡫ࡤࠡࡰࡤࡱࡪࡹࠠࡢࡰࡧࠤࡼࡵࡲ࡬ࠢࡺ࡭ࡹ࡮ࠠࡢ࡮࡯ࠤ࡛ࡉࡓࠡࡲࡵࡳࡻ࡯ࡤࡦࡴࡶ࠲ࠏࠦࠠࠡࠢࡕࡩࡹࡻࡲ࡯ࡵࠣࡸ࡭࡫ࠠࡥࡧࡩࡥࡺࡲࡴࠡࡤࡵࡥࡳࡩࡨࠡ࡫ࡩࠤࡵࡵࡳࡴ࡫ࡥࡰࡪ࠲ࠠࡦ࡮ࡶࡩࠥࡔ࡯࡯ࡧ࠱ࠎࠥࠦࠠࠡࠤࠥࠦ᭧")
    try:
        try:
            origin = repo.remotes.origin
            bstack111llll11l1_opy_ = origin.refs[bstack111l11_opy_ (u"ࠩࡋࡉࡆࡊࠧ᭨")]
            target = bstack111llll11l1_opy_.reference.name
            if target.startswith(bstack111l11_opy_ (u"ࠪࡳࡷ࡯ࡧࡪࡰ࠲ࠫ᭩")):
                return target
        except Exception:
            pass
        if repo.heads:
            return repo.heads[0].name
        if repo.remotes and repo.remotes.origin.refs:
            for ref in repo.remotes.origin.refs:
                if ref.name.startswith(bstack111l11_opy_ (u"ࠫࡴࡸࡩࡨ࡫ࡱ࠳ࠬ᭪")):
                    return ref.name
    except Exception:
        pass
    return None
def _11l111l1111_opy_(commits):
    bstack111l11_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࡍࡥࡵࠢ࡯࡭ࡸࡺࠠࡰࡨࠣࡧ࡭ࡧ࡮ࡨࡧࡧࠤ࡫࡯࡬ࡦࡵࠣࡪࡷࡵ࡭ࠡࡣࠣࡰ࡮ࡹࡴࠡࡱࡩࠤࡨࡵ࡭࡮࡫ࡷࡷ࠳ࠐࠠࠡࠢࠣࠦࠧࠨ᭫")
    bstack11l1111l1l1_opy_ = set()
    try:
        for commit in commits:
            if commit.parents:
                for parent in commit.parents:
                    diff = commit.diff(parent)
                    for bstack11l11l111ll_opy_ in diff:
                        if bstack11l11l111ll_opy_.a_path:
                            bstack11l1111l1l1_opy_.add(bstack11l11l111ll_opy_.a_path)
                        if bstack11l11l111ll_opy_.b_path:
                            bstack11l1111l1l1_opy_.add(bstack11l11l111ll_opy_.b_path)
    except Exception:
        pass
    return list(bstack11l1111l1l1_opy_)
def bstack11l111ll11l_opy_(bstack11l111lll1l_opy_):
    bstack111lllll111_opy_ = bstack11l111111l1_opy_(bstack11l111lll1l_opy_)
    if bstack111lllll111_opy_ and bstack111lllll111_opy_ > bstack11l1ll11111_opy_:
        bstack11l11111l11_opy_ = bstack111lllll111_opy_ - bstack11l1ll11111_opy_
        bstack11l1111111l_opy_ = bstack11l11lll1ll_opy_(bstack11l111lll1l_opy_[bstack111l11_opy_ (u"ࠨࡣࡰ࡯ࡰ࡭ࡹࡥ࡭ࡦࡵࡶࡥ࡬࡫᭬ࠢ")], bstack11l11111l11_opy_)
        bstack11l111lll1l_opy_[bstack111l11_opy_ (u"ࠢࡤࡱࡰࡱ࡮ࡺ࡟࡮ࡧࡶࡷࡦ࡭ࡥࠣ᭭")] = bstack11l1111111l_opy_
        logger.info(bstack111l11_opy_ (u"ࠣࡖ࡫ࡩࠥࡩ࡯࡮࡯࡬ࡸࠥ࡮ࡡࡴࠢࡥࡩࡪࡴࠠࡵࡴࡸࡲࡨࡧࡴࡦࡦ࠱ࠤࡘ࡯ࡺࡦࠢࡲࡪࠥࡩ࡯࡮࡯࡬ࡸࠥࡧࡦࡵࡧࡵࠤࡹࡸࡵ࡯ࡥࡤࡸ࡮ࡵ࡮ࠡ࡫ࡶࠤࢀࢃࠠࡌࡄࠥ᭮")
                    .format(bstack11l111111l1_opy_(bstack11l111lll1l_opy_) / 1024))
    return bstack11l111lll1l_opy_
def bstack11l111111l1_opy_(bstack111111111_opy_):
    try:
        if bstack111111111_opy_:
            bstack111ll1ll1ll_opy_ = json.dumps(bstack111111111_opy_)
            bstack11l11ll1l11_opy_ = sys.getsizeof(bstack111ll1ll1ll_opy_)
            return bstack11l11ll1l11_opy_
    except Exception as e:
        logger.debug(bstack111l11_opy_ (u"ࠤࡖࡳࡲ࡫ࡴࡩ࡫ࡱ࡫ࠥࡽࡥ࡯ࡶࠣࡻࡷࡵ࡮ࡨࠢࡺ࡬࡮ࡲࡥࠡࡥࡤࡰࡨࡻ࡬ࡢࡶ࡬ࡲ࡬ࠦࡳࡪࡼࡨࠤࡴ࡬ࠠࡋࡕࡒࡒࠥࡵࡢ࡫ࡧࡦࡸ࠿ࠦࡻࡾࠤ᭯").format(e))
    return -1
def bstack11l11lll1ll_opy_(field, bstack111lll11ll1_opy_):
    try:
        bstack11l111l1l1l_opy_ = len(bytes(bstack11l1llll11l_opy_, bstack111l11_opy_ (u"ࠪࡹࡹ࡬࠭࠹ࠩ᭰")))
        bstack11l11ll1l1l_opy_ = bytes(field, bstack111l11_opy_ (u"ࠫࡺࡺࡦ࠮࠺ࠪ᭱"))
        bstack11l11111lll_opy_ = len(bstack11l11ll1l1l_opy_)
        bstack11l111l11ll_opy_ = ceil(bstack11l11111lll_opy_ - bstack111lll11ll1_opy_ - bstack11l111l1l1l_opy_)
        if bstack11l111l11ll_opy_ > 0:
            bstack111lll111ll_opy_ = bstack11l11ll1l1l_opy_[:bstack11l111l11ll_opy_].decode(bstack111l11_opy_ (u"ࠬࡻࡴࡧ࠯࠻ࠫ᭲"), errors=bstack111l11_opy_ (u"࠭ࡩࡨࡰࡲࡶࡪ࠭᭳")) + bstack11l1llll11l_opy_
            return bstack111lll111ll_opy_
    except Exception as e:
        logger.debug(bstack111l11_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡷࡩ࡫࡯ࡩࠥࡺࡲࡶࡰࡦࡥࡹ࡯࡮ࡨࠢࡩ࡭ࡪࡲࡤ࠭ࠢࡱࡳࡹ࡮ࡩ࡯ࡩࠣࡻࡦࡹࠠࡵࡴࡸࡲࡨࡧࡴࡦࡦࠣ࡬ࡪࡸࡥ࠻ࠢࡾࢁࠧ᭴").format(e))
    return field
def bstack1lll111ll1_opy_():
    env = os.environ
    if (bstack111l11_opy_ (u"ࠣࡌࡈࡒࡐࡏࡎࡔࡡࡘࡖࡑࠨ᭵") in env and len(env[bstack111l11_opy_ (u"ࠤࡍࡉࡓࡑࡉࡏࡕࡢ࡙ࡗࡒࠢ᭶")]) > 0) or (
            bstack111l11_opy_ (u"ࠥࡎࡊࡔࡋࡊࡐࡖࡣࡍࡕࡍࡆࠤ᭷") in env and len(env[bstack111l11_opy_ (u"ࠦࡏࡋࡎࡌࡋࡑࡗࡤࡎࡏࡎࡇࠥ᭸")]) > 0):
        return {
            bstack111l11_opy_ (u"ࠧࡴࡡ࡮ࡧࠥ᭹"): bstack111l11_opy_ (u"ࠨࡊࡦࡰ࡮࡭ࡳࡹࠢ᭺"),
            bstack111l11_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥ᭻"): env.get(bstack111l11_opy_ (u"ࠣࡄࡘࡍࡑࡊ࡟ࡖࡔࡏࠦ᭼")),
            bstack111l11_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦ᭽"): env.get(bstack111l11_opy_ (u"ࠥࡎࡔࡈ࡟ࡏࡃࡐࡉࠧ᭾")),
            bstack111l11_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥ᭿"): env.get(bstack111l11_opy_ (u"ࠧࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࡃࡇࡕࠦᮀ"))
        }
    if env.get(bstack111l11_opy_ (u"ࠨࡃࡊࠤᮁ")) == bstack111l11_opy_ (u"ࠢࡵࡴࡸࡩࠧᮂ") and bstack11ll1l11_opy_(env.get(bstack111l11_opy_ (u"ࠣࡅࡌࡖࡈࡒࡅࡄࡋࠥᮃ"))):
        return {
            bstack111l11_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᮄ"): bstack111l11_opy_ (u"ࠥࡇ࡮ࡸࡣ࡭ࡧࡆࡍࠧᮅ"),
            bstack111l11_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᮆ"): env.get(bstack111l11_opy_ (u"ࠧࡉࡉࡓࡅࡏࡉࡤࡈࡕࡊࡎࡇࡣ࡚ࡘࡌࠣᮇ")),
            bstack111l11_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᮈ"): env.get(bstack111l11_opy_ (u"ࠢࡄࡋࡕࡇࡑࡋ࡟ࡋࡑࡅࠦᮉ")),
            bstack111l11_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᮊ"): env.get(bstack111l11_opy_ (u"ࠤࡆࡍࡗࡉࡌࡆࡡࡅ࡙ࡎࡒࡄࡠࡐࡘࡑࠧᮋ"))
        }
    if env.get(bstack111l11_opy_ (u"ࠥࡇࡎࠨᮌ")) == bstack111l11_opy_ (u"ࠦࡹࡸࡵࡦࠤᮍ") and bstack11ll1l11_opy_(env.get(bstack111l11_opy_ (u"࡚ࠧࡒࡂࡘࡌࡗࠧᮎ"))):
        return {
            bstack111l11_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᮏ"): bstack111l11_opy_ (u"ࠢࡕࡴࡤࡺ࡮ࡹࠠࡄࡋࠥᮐ"),
            bstack111l11_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᮑ"): env.get(bstack111l11_opy_ (u"ࠤࡗࡖࡆ࡜ࡉࡔࡡࡅ࡙ࡎࡒࡄࡠ࡙ࡈࡆࡤ࡛ࡒࡍࠤᮒ")),
            bstack111l11_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᮓ"): env.get(bstack111l11_opy_ (u"࡙ࠦࡘࡁࡗࡋࡖࡣࡏࡕࡂࡠࡐࡄࡑࡊࠨᮔ")),
            bstack111l11_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᮕ"): env.get(bstack111l11_opy_ (u"ࠨࡔࡓࡃ࡙ࡍࡘࡥࡂࡖࡋࡏࡈࡤࡔࡕࡎࡄࡈࡖࠧᮖ"))
        }
    if env.get(bstack111l11_opy_ (u"ࠢࡄࡋࠥᮗ")) == bstack111l11_opy_ (u"ࠣࡶࡵࡹࡪࠨᮘ") and env.get(bstack111l11_opy_ (u"ࠤࡆࡍࡤࡔࡁࡎࡇࠥᮙ")) == bstack111l11_opy_ (u"ࠥࡧࡴࡪࡥࡴࡪ࡬ࡴࠧᮚ"):
        return {
            bstack111l11_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᮛ"): bstack111l11_opy_ (u"ࠧࡉ࡯ࡥࡧࡶ࡬࡮ࡶࠢᮜ"),
            bstack111l11_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤᮝ"): None,
            bstack111l11_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᮞ"): None,
            bstack111l11_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᮟ"): None
        }
    if env.get(bstack111l11_opy_ (u"ࠤࡅࡍ࡙ࡈࡕࡄࡍࡈࡘࡤࡈࡒࡂࡐࡆࡌࠧᮠ")) and env.get(bstack111l11_opy_ (u"ࠥࡆࡎ࡚ࡂࡖࡅࡎࡉ࡙ࡥࡃࡐࡏࡐࡍ࡙ࠨᮡ")):
        return {
            bstack111l11_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᮢ"): bstack111l11_opy_ (u"ࠧࡈࡩࡵࡤࡸࡧࡰ࡫ࡴࠣᮣ"),
            bstack111l11_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤᮤ"): env.get(bstack111l11_opy_ (u"ࠢࡃࡋࡗࡆ࡚ࡉࡋࡆࡖࡢࡋࡎ࡚࡟ࡉࡖࡗࡔࡤࡕࡒࡊࡉࡌࡒࠧᮥ")),
            bstack111l11_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᮦ"): None,
            bstack111l11_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᮧ"): env.get(bstack111l11_opy_ (u"ࠥࡆࡎ࡚ࡂࡖࡅࡎࡉ࡙ࡥࡂࡖࡋࡏࡈࡤࡔࡕࡎࡄࡈࡖࠧᮨ"))
        }
    if env.get(bstack111l11_opy_ (u"ࠦࡈࡏࠢᮩ")) == bstack111l11_opy_ (u"ࠧࡺࡲࡶࡧ᮪ࠥ") and bstack11ll1l11_opy_(env.get(bstack111l11_opy_ (u"ࠨࡄࡓࡑࡑࡉ᮫ࠧ"))):
        return {
            bstack111l11_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᮬ"): bstack111l11_opy_ (u"ࠣࡆࡵࡳࡳ࡫ࠢᮭ"),
            bstack111l11_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᮮ"): env.get(bstack111l11_opy_ (u"ࠥࡈࡗࡕࡎࡆࡡࡅ࡙ࡎࡒࡄࡠࡎࡌࡒࡐࠨᮯ")),
            bstack111l11_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨ᮰"): None,
            bstack111l11_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦ᮱"): env.get(bstack111l11_opy_ (u"ࠨࡄࡓࡑࡑࡉࡤࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࡃࡇࡕࠦ᮲"))
        }
    if env.get(bstack111l11_opy_ (u"ࠢࡄࡋࠥ᮳")) == bstack111l11_opy_ (u"ࠣࡶࡵࡹࡪࠨ᮴") and bstack11ll1l11_opy_(env.get(bstack111l11_opy_ (u"ࠤࡖࡉࡒࡇࡐࡉࡑࡕࡉࠧ᮵"))):
        return {
            bstack111l11_opy_ (u"ࠥࡲࡦࡳࡥࠣ᮶"): bstack111l11_opy_ (u"ࠦࡘ࡫࡭ࡢࡲ࡫ࡳࡷ࡫ࠢ᮷"),
            bstack111l11_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣ᮸"): env.get(bstack111l11_opy_ (u"ࠨࡓࡆࡏࡄࡔࡍࡕࡒࡆࡡࡒࡖࡌࡇࡎࡊ࡜ࡄࡘࡎࡕࡎࡠࡗࡕࡐࠧ᮹")),
            bstack111l11_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᮺ"): env.get(bstack111l11_opy_ (u"ࠣࡕࡈࡑࡆࡖࡈࡐࡔࡈࡣࡏࡕࡂࡠࡐࡄࡑࡊࠨᮻ")),
            bstack111l11_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᮼ"): env.get(bstack111l11_opy_ (u"ࠥࡗࡊࡓࡁࡑࡊࡒࡖࡊࡥࡊࡐࡄࡢࡍࡉࠨᮽ"))
        }
    if env.get(bstack111l11_opy_ (u"ࠦࡈࡏࠢᮾ")) == bstack111l11_opy_ (u"ࠧࡺࡲࡶࡧࠥᮿ") and bstack11ll1l11_opy_(env.get(bstack111l11_opy_ (u"ࠨࡇࡊࡖࡏࡅࡇࡥࡃࡊࠤᯀ"))):
        return {
            bstack111l11_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᯁ"): bstack111l11_opy_ (u"ࠣࡉ࡬ࡸࡑࡧࡢࠣᯂ"),
            bstack111l11_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᯃ"): env.get(bstack111l11_opy_ (u"ࠥࡇࡎࡥࡊࡐࡄࡢ࡙ࡗࡒࠢᯄ")),
            bstack111l11_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᯅ"): env.get(bstack111l11_opy_ (u"ࠧࡉࡉࡠࡌࡒࡆࡤࡔࡁࡎࡇࠥᯆ")),
            bstack111l11_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧᯇ"): env.get(bstack111l11_opy_ (u"ࠢࡄࡋࡢࡎࡔࡈ࡟ࡊࡆࠥᯈ"))
        }
    if env.get(bstack111l11_opy_ (u"ࠣࡅࡌࠦᯉ")) == bstack111l11_opy_ (u"ࠤࡷࡶࡺ࡫ࠢᯊ") and bstack11ll1l11_opy_(env.get(bstack111l11_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡍࡌࡘࡊࠨᯋ"))):
        return {
            bstack111l11_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᯌ"): bstack111l11_opy_ (u"ࠧࡈࡵࡪ࡮ࡧ࡯࡮ࡺࡥࠣᯍ"),
            bstack111l11_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤᯎ"): env.get(bstack111l11_opy_ (u"ࠢࡃࡗࡌࡐࡉࡑࡉࡕࡇࡢࡆ࡚ࡏࡌࡅࡡࡘࡖࡑࠨᯏ")),
            bstack111l11_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᯐ"): env.get(bstack111l11_opy_ (u"ࠤࡅ࡙ࡎࡒࡄࡌࡋࡗࡉࡤࡒࡁࡃࡇࡏࠦᯑ")) or env.get(bstack111l11_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡍࡌࡘࡊࡥࡐࡊࡒࡈࡐࡎࡔࡅࡠࡐࡄࡑࡊࠨᯒ")),
            bstack111l11_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᯓ"): env.get(bstack111l11_opy_ (u"ࠧࡈࡕࡊࡎࡇࡏࡎ࡚ࡅࡠࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࠢᯔ"))
        }
    if bstack11ll1l11_opy_(env.get(bstack111l11_opy_ (u"ࠨࡔࡇࡡࡅ࡙ࡎࡒࡄࠣᯕ"))):
        return {
            bstack111l11_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᯖ"): bstack111l11_opy_ (u"ࠣࡘ࡬ࡷࡺࡧ࡬ࠡࡕࡷࡹࡩ࡯࡯ࠡࡖࡨࡥࡲࠦࡓࡦࡴࡹ࡭ࡨ࡫ࡳࠣᯗ"),
            bstack111l11_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᯘ"): bstack111l11_opy_ (u"ࠥࡿࢂࢁࡽࠣᯙ").format(env.get(bstack111l11_opy_ (u"ࠫࡘ࡟ࡓࡕࡇࡐࡣ࡙ࡋࡁࡎࡈࡒ࡙ࡓࡊࡁࡕࡋࡒࡒࡘࡋࡒࡗࡇࡕ࡙ࡗࡏࠧᯚ")), env.get(bstack111l11_opy_ (u"࡙࡙ࠬࡔࡖࡈࡑࡤ࡚ࡅࡂࡏࡓࡖࡔࡐࡅࡄࡖࡌࡈࠬᯛ"))),
            bstack111l11_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᯜ"): env.get(bstack111l11_opy_ (u"ࠢࡔ࡛ࡖࡘࡊࡓ࡟ࡅࡇࡉࡍࡓࡏࡔࡊࡑࡑࡍࡉࠨᯝ")),
            bstack111l11_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᯞ"): env.get(bstack111l11_opy_ (u"ࠤࡅ࡙ࡎࡒࡄࡠࡄࡘࡍࡑࡊࡉࡅࠤᯟ"))
        }
    if bstack11ll1l11_opy_(env.get(bstack111l11_opy_ (u"ࠥࡅࡕࡖࡖࡆ࡛ࡒࡖࠧᯠ"))):
        return {
            bstack111l11_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᯡ"): bstack111l11_opy_ (u"ࠧࡇࡰࡱࡸࡨࡽࡴࡸࠢᯢ"),
            bstack111l11_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤᯣ"): bstack111l11_opy_ (u"ࠢࡼࡿ࠲ࡴࡷࡵࡪࡦࡥࡷ࠳ࢀࢃ࠯ࡼࡿ࠲ࡦࡺ࡯࡬ࡥࡵ࠲ࡿࢂࠨᯤ").format(env.get(bstack111l11_opy_ (u"ࠨࡃࡓࡔ࡛ࡋ࡙ࡐࡔࡢ࡙ࡗࡒࠧᯥ")), env.get(bstack111l11_opy_ (u"ࠩࡄࡔࡕ࡜ࡅ࡚ࡑࡕࡣࡆࡉࡃࡐࡗࡑࡘࡤࡔࡁࡎࡇ᯦ࠪ")), env.get(bstack111l11_opy_ (u"ࠪࡅࡕࡖࡖࡆ࡛ࡒࡖࡤࡖࡒࡐࡌࡈࡇ࡙ࡥࡓࡍࡗࡊࠫᯧ")), env.get(bstack111l11_opy_ (u"ࠫࡆࡖࡐࡗࡇ࡜ࡓࡗࡥࡂࡖࡋࡏࡈࡤࡏࡄࠨᯨ"))),
            bstack111l11_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᯩ"): env.get(bstack111l11_opy_ (u"ࠨࡁࡑࡒ࡙ࡉ࡞ࡕࡒࡠࡌࡒࡆࡤࡔࡁࡎࡇࠥᯪ")),
            bstack111l11_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᯫ"): env.get(bstack111l11_opy_ (u"ࠣࡃࡓࡔ࡛ࡋ࡙ࡐࡔࡢࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࠤᯬ"))
        }
    if env.get(bstack111l11_opy_ (u"ࠤࡄ࡞࡚ࡘࡅࡠࡊࡗࡘࡕࡥࡕࡔࡇࡕࡣࡆࡍࡅࡏࡖࠥᯭ")) and env.get(bstack111l11_opy_ (u"ࠥࡘࡋࡥࡂࡖࡋࡏࡈࠧᯮ")):
        return {
            bstack111l11_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᯯ"): bstack111l11_opy_ (u"ࠧࡇࡺࡶࡴࡨࠤࡈࡏࠢᯰ"),
            bstack111l11_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤᯱ"): bstack111l11_opy_ (u"ࠢࡼࡿࡾࢁ࠴ࡥࡢࡶ࡫࡯ࡨ࠴ࡸࡥࡴࡷ࡯ࡸࡸࡅࡢࡶ࡫࡯ࡨࡎࡪ࠽ࡼࡿ᯲ࠥ").format(env.get(bstack111l11_opy_ (u"ࠨࡕ࡜ࡗ࡙ࡋࡍࡠࡖࡈࡅࡒࡌࡏࡖࡐࡇࡅ࡙ࡏࡏࡏࡕࡈࡖ࡛ࡋࡒࡖࡔࡌ᯳ࠫ")), env.get(bstack111l11_opy_ (u"ࠩࡖ࡝ࡘ࡚ࡅࡎࡡࡗࡉࡆࡓࡐࡓࡑࡍࡉࡈ࡚ࠧ᯴")), env.get(bstack111l11_opy_ (u"ࠪࡆ࡚ࡏࡌࡅࡡࡅ࡙ࡎࡒࡄࡊࡆࠪ᯵"))),
            bstack111l11_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨ᯶"): env.get(bstack111l11_opy_ (u"ࠧࡈࡕࡊࡎࡇࡣࡇ࡛ࡉࡍࡆࡌࡈࠧ᯷")),
            bstack111l11_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧ᯸"): env.get(bstack111l11_opy_ (u"ࠢࡃࡗࡌࡐࡉࡥࡂࡖࡋࡏࡈࡎࡊࠢ᯹"))
        }
    if any([env.get(bstack111l11_opy_ (u"ࠣࡅࡒࡈࡊࡈࡕࡊࡎࡇࡣࡇ࡛ࡉࡍࡆࡢࡍࡉࠨ᯺")), env.get(bstack111l11_opy_ (u"ࠤࡆࡓࡉࡋࡂࡖࡋࡏࡈࡤࡘࡅࡔࡑࡏ࡚ࡊࡊ࡟ࡔࡑࡘࡖࡈࡋ࡟ࡗࡇࡕࡗࡎࡕࡎࠣ᯻")), env.get(bstack111l11_opy_ (u"ࠥࡇࡔࡊࡅࡃࡗࡌࡐࡉࡥࡓࡐࡗࡕࡇࡊࡥࡖࡆࡔࡖࡍࡔࡔࠢ᯼"))]):
        return {
            bstack111l11_opy_ (u"ࠦࡳࡧ࡭ࡦࠤ᯽"): bstack111l11_opy_ (u"ࠧࡇࡗࡔࠢࡆࡳࡩ࡫ࡂࡶ࡫࡯ࡨࠧ᯾"),
            bstack111l11_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤ᯿"): env.get(bstack111l11_opy_ (u"ࠢࡄࡑࡇࡉࡇ࡛ࡉࡍࡆࡢࡔ࡚ࡈࡌࡊࡅࡢࡆ࡚ࡏࡌࡅࡡࡘࡖࡑࠨᰀ")),
            bstack111l11_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᰁ"): env.get(bstack111l11_opy_ (u"ࠤࡆࡓࡉࡋࡂࡖࡋࡏࡈࡤࡈࡕࡊࡎࡇࡣࡎࡊࠢᰂ")),
            bstack111l11_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᰃ"): env.get(bstack111l11_opy_ (u"ࠦࡈࡕࡄࡆࡄࡘࡍࡑࡊ࡟ࡃࡗࡌࡐࡉࡥࡉࡅࠤᰄ"))
        }
    if env.get(bstack111l11_opy_ (u"ࠧࡨࡡ࡮ࡤࡲࡳࡤࡨࡵࡪ࡮ࡧࡒࡺࡳࡢࡦࡴࠥᰅ")):
        return {
            bstack111l11_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᰆ"): bstack111l11_opy_ (u"ࠢࡃࡣࡰࡦࡴࡵࠢᰇ"),
            bstack111l11_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᰈ"): env.get(bstack111l11_opy_ (u"ࠤࡥࡥࡲࡨ࡯ࡰࡡࡥࡹ࡮ࡲࡤࡓࡧࡶࡹࡱࡺࡳࡖࡴ࡯ࠦᰉ")),
            bstack111l11_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᰊ"): env.get(bstack111l11_opy_ (u"ࠦࡧࡧ࡭ࡣࡱࡲࡣࡸ࡮࡯ࡳࡶࡍࡳࡧࡔࡡ࡮ࡧࠥᰋ")),
            bstack111l11_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᰌ"): env.get(bstack111l11_opy_ (u"ࠨࡢࡢ࡯ࡥࡳࡴࡥࡢࡶ࡫࡯ࡨࡓࡻ࡭ࡣࡧࡵࠦᰍ"))
        }
    if env.get(bstack111l11_opy_ (u"ࠢࡘࡇࡕࡇࡐࡋࡒࠣᰎ")) or env.get(bstack111l11_opy_ (u"࡙ࠣࡈࡖࡈࡑࡅࡓࡡࡐࡅࡎࡔ࡟ࡑࡋࡓࡉࡑࡏࡎࡆࡡࡖࡘࡆࡘࡔࡆࡆࠥᰏ")):
        return {
            bstack111l11_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᰐ"): bstack111l11_opy_ (u"࡛ࠥࡪࡸࡣ࡬ࡧࡵࠦᰑ"),
            bstack111l11_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᰒ"): env.get(bstack111l11_opy_ (u"ࠧ࡝ࡅࡓࡅࡎࡉࡗࡥࡂࡖࡋࡏࡈࡤ࡛ࡒࡍࠤᰓ")),
            bstack111l11_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᰔ"): bstack111l11_opy_ (u"ࠢࡎࡣ࡬ࡲࠥࡖࡩࡱࡧ࡯࡭ࡳ࡫ࠢᰕ") if env.get(bstack111l11_opy_ (u"࡙ࠣࡈࡖࡈࡑࡅࡓࡡࡐࡅࡎࡔ࡟ࡑࡋࡓࡉࡑࡏࡎࡆࡡࡖࡘࡆࡘࡔࡆࡆࠥᰖ")) else None,
            bstack111l11_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᰗ"): env.get(bstack111l11_opy_ (u"࡛ࠥࡊࡘࡃࡌࡇࡕࡣࡌࡏࡔࡠࡅࡒࡑࡒࡏࡔࠣᰘ"))
        }
    if any([env.get(bstack111l11_opy_ (u"ࠦࡌࡉࡐࡠࡒࡕࡓࡏࡋࡃࡕࠤᰙ")), env.get(bstack111l11_opy_ (u"ࠧࡍࡃࡍࡑࡘࡈࡤࡖࡒࡐࡌࡈࡇ࡙ࠨᰚ")), env.get(bstack111l11_opy_ (u"ࠨࡇࡐࡑࡊࡐࡊࡥࡃࡍࡑࡘࡈࡤࡖࡒࡐࡌࡈࡇ࡙ࠨᰛ"))]):
        return {
            bstack111l11_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᰜ"): bstack111l11_opy_ (u"ࠣࡉࡲࡳ࡬ࡲࡥࠡࡅ࡯ࡳࡺࡪࠢᰝ"),
            bstack111l11_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᰞ"): None,
            bstack111l11_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᰟ"): env.get(bstack111l11_opy_ (u"ࠦࡕࡘࡏࡋࡇࡆࡘࡤࡏࡄࠣᰠ")),
            bstack111l11_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᰡ"): env.get(bstack111l11_opy_ (u"ࠨࡂࡖࡋࡏࡈࡤࡏࡄࠣᰢ"))
        }
    if env.get(bstack111l11_opy_ (u"ࠢࡔࡊࡌࡔࡕࡇࡂࡍࡇࠥᰣ")):
        return {
            bstack111l11_opy_ (u"ࠣࡰࡤࡱࡪࠨᰤ"): bstack111l11_opy_ (u"ࠤࡖ࡬࡮ࡶࡰࡢࡤ࡯ࡩࠧᰥ"),
            bstack111l11_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᰦ"): env.get(bstack111l11_opy_ (u"ࠦࡘࡎࡉࡑࡒࡄࡆࡑࡋ࡟ࡃࡗࡌࡐࡉࡥࡕࡓࡎࠥᰧ")),
            bstack111l11_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᰨ"): bstack111l11_opy_ (u"ࠨࡊࡰࡤࠣࠧࢀࢃࠢᰩ").format(env.get(bstack111l11_opy_ (u"ࠧࡔࡊࡌࡔࡕࡇࡂࡍࡇࡢࡎࡔࡈ࡟ࡊࡆࠪᰪ"))) if env.get(bstack111l11_opy_ (u"ࠣࡕࡋࡍࡕࡖࡁࡃࡎࡈࡣࡏࡕࡂࡠࡋࡇࠦᰫ")) else None,
            bstack111l11_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᰬ"): env.get(bstack111l11_opy_ (u"ࠥࡗࡍࡏࡐࡑࡃࡅࡐࡊࡥࡂࡖࡋࡏࡈࡤࡔࡕࡎࡄࡈࡖࠧᰭ"))
        }
    if bstack11ll1l11_opy_(env.get(bstack111l11_opy_ (u"ࠦࡓࡋࡔࡍࡋࡉ࡝ࠧᰮ"))):
        return {
            bstack111l11_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᰯ"): bstack111l11_opy_ (u"ࠨࡎࡦࡶ࡯࡭࡫ࡿࠢᰰ"),
            bstack111l11_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥᰱ"): env.get(bstack111l11_opy_ (u"ࠣࡆࡈࡔࡑࡕ࡙ࡠࡗࡕࡐࠧᰲ")),
            bstack111l11_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᰳ"): env.get(bstack111l11_opy_ (u"ࠥࡗࡎ࡚ࡅࡠࡐࡄࡑࡊࠨᰴ")),
            bstack111l11_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᰵ"): env.get(bstack111l11_opy_ (u"ࠧࡈࡕࡊࡎࡇࡣࡎࡊࠢᰶ"))
        }
    if bstack11ll1l11_opy_(env.get(bstack111l11_opy_ (u"ࠨࡇࡊࡖࡋ࡙ࡇࡥࡁࡄࡖࡌࡓࡓ᰷࡙ࠢ"))):
        return {
            bstack111l11_opy_ (u"ࠢ࡯ࡣࡰࡩࠧ᰸"): bstack111l11_opy_ (u"ࠣࡉ࡬ࡸࡍࡻࡢࠡࡃࡦࡸ࡮ࡵ࡮ࡴࠤ᰹"),
            bstack111l11_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧ᰺"): bstack111l11_opy_ (u"ࠥࡿࢂ࠵ࡻࡾ࠱ࡤࡧࡹ࡯࡯࡯ࡵ࠲ࡶࡺࡴࡳ࠰ࡽࢀࠦ᰻").format(env.get(bstack111l11_opy_ (u"ࠫࡌࡏࡔࡉࡗࡅࡣࡘࡋࡒࡗࡇࡕࡣ࡚ࡘࡌࠨ᰼")), env.get(bstack111l11_opy_ (u"ࠬࡍࡉࡕࡊࡘࡆࡤࡘࡅࡑࡑࡖࡍ࡙ࡕࡒ࡚ࠩ᰽")), env.get(bstack111l11_opy_ (u"࠭ࡇࡊࡖࡋ࡙ࡇࡥࡒࡖࡐࡢࡍࡉ࠭᰾"))),
            bstack111l11_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤ᰿"): env.get(bstack111l11_opy_ (u"ࠣࡉࡌࡘࡍ࡛ࡂࡠ࡙ࡒࡖࡐࡌࡌࡐ࡙ࠥ᱀")),
            bstack111l11_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣ᱁"): env.get(bstack111l11_opy_ (u"ࠥࡋࡎ࡚ࡈࡖࡄࡢࡖ࡚ࡔ࡟ࡊࡆࠥ᱂"))
        }
    if env.get(bstack111l11_opy_ (u"ࠦࡈࡏࠢ᱃")) == bstack111l11_opy_ (u"ࠧࡺࡲࡶࡧࠥ᱄") and env.get(bstack111l11_opy_ (u"ࠨࡖࡆࡔࡆࡉࡑࠨ᱅")) == bstack111l11_opy_ (u"ࠢ࠲ࠤ᱆"):
        return {
            bstack111l11_opy_ (u"ࠣࡰࡤࡱࡪࠨ᱇"): bstack111l11_opy_ (u"ࠤ࡙ࡩࡷࡩࡥ࡭ࠤ᱈"),
            bstack111l11_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨ᱉"): bstack111l11_opy_ (u"ࠦ࡭ࡺࡴࡱ࠼࠲࠳ࢀࢃࠢ᱊").format(env.get(bstack111l11_opy_ (u"ࠬ࡜ࡅࡓࡅࡈࡐࡤ࡛ࡒࡍࠩ᱋"))),
            bstack111l11_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣ᱌"): None,
            bstack111l11_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᱍ"): None,
        }
    if env.get(bstack111l11_opy_ (u"ࠣࡖࡈࡅࡒࡉࡉࡕ࡛ࡢ࡚ࡊࡘࡓࡊࡑࡑࠦᱎ")):
        return {
            bstack111l11_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᱏ"): bstack111l11_opy_ (u"ࠥࡘࡪࡧ࡭ࡤ࡫ࡷࡽࠧ᱐"),
            bstack111l11_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢ᱑"): None,
            bstack111l11_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢ᱒"): env.get(bstack111l11_opy_ (u"ࠨࡔࡆࡃࡐࡇࡎ࡚࡙ࡠࡒࡕࡓࡏࡋࡃࡕࡡࡑࡅࡒࡋࠢ᱓")),
            bstack111l11_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨ᱔"): env.get(bstack111l11_opy_ (u"ࠣࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࠢ᱕"))
        }
    if any([env.get(bstack111l11_opy_ (u"ࠤࡆࡓࡓࡉࡏࡖࡔࡖࡉࠧ᱖")), env.get(bstack111l11_opy_ (u"ࠥࡇࡔࡔࡃࡐࡗࡕࡗࡊࡥࡕࡓࡎࠥ᱗")), env.get(bstack111l11_opy_ (u"ࠦࡈࡕࡎࡄࡑࡘࡖࡘࡋ࡟ࡖࡕࡈࡖࡓࡇࡍࡆࠤ᱘")), env.get(bstack111l11_opy_ (u"ࠧࡉࡏࡏࡅࡒ࡙ࡗ࡙ࡅࡠࡖࡈࡅࡒࠨ᱙"))]):
        return {
            bstack111l11_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᱚ"): bstack111l11_opy_ (u"ࠢࡄࡱࡱࡧࡴࡻࡲࡴࡧࠥᱛ"),
            bstack111l11_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᱜ"): None,
            bstack111l11_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᱝ"): env.get(bstack111l11_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡡࡍࡓࡇࡥࡎࡂࡏࡈࠦᱞ")) or None,
            bstack111l11_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᱟ"): env.get(bstack111l11_opy_ (u"ࠧࡈࡕࡊࡎࡇࡣࡎࡊࠢᱠ"), 0)
        }
    if env.get(bstack111l11_opy_ (u"ࠨࡇࡐࡡࡍࡓࡇࡥࡎࡂࡏࡈࠦᱡ")):
        return {
            bstack111l11_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᱢ"): bstack111l11_opy_ (u"ࠣࡉࡲࡇࡉࠨᱣ"),
            bstack111l11_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᱤ"): None,
            bstack111l11_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᱥ"): env.get(bstack111l11_opy_ (u"ࠦࡌࡕ࡟ࡋࡑࡅࡣࡓࡇࡍࡆࠤᱦ")),
            bstack111l11_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᱧ"): env.get(bstack111l11_opy_ (u"ࠨࡇࡐࡡࡓࡍࡕࡋࡌࡊࡐࡈࡣࡈࡕࡕࡏࡖࡈࡖࠧᱨ"))
        }
    if env.get(bstack111l11_opy_ (u"ࠢࡄࡈࡢࡆ࡚ࡏࡌࡅࡡࡌࡈࠧᱩ")):
        return {
            bstack111l11_opy_ (u"ࠣࡰࡤࡱࡪࠨᱪ"): bstack111l11_opy_ (u"ࠤࡆࡳࡩ࡫ࡆࡳࡧࡶ࡬ࠧᱫ"),
            bstack111l11_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᱬ"): env.get(bstack111l11_opy_ (u"ࠦࡈࡌ࡟ࡃࡗࡌࡐࡉࡥࡕࡓࡎࠥᱭ")),
            bstack111l11_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᱮ"): env.get(bstack111l11_opy_ (u"ࠨࡃࡇࡡࡓࡍࡕࡋࡌࡊࡐࡈࡣࡓࡇࡍࡆࠤᱯ")),
            bstack111l11_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᱰ"): env.get(bstack111l11_opy_ (u"ࠣࡅࡉࡣࡇ࡛ࡉࡍࡆࡢࡍࡉࠨᱱ"))
        }
    return {bstack111l11_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᱲ"): None}
def get_host_info():
    return {
        bstack111l11_opy_ (u"ࠥ࡬ࡴࡹࡴ࡯ࡣࡰࡩࠧᱳ"): platform.node(),
        bstack111l11_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲࠨᱴ"): platform.system(),
        bstack111l11_opy_ (u"ࠧࡺࡹࡱࡧࠥᱵ"): platform.machine(),
        bstack111l11_opy_ (u"ࠨࡶࡦࡴࡶ࡭ࡴࡴࠢᱶ"): platform.version(),
        bstack111l11_opy_ (u"ࠢࡢࡴࡦ࡬ࠧᱷ"): platform.architecture()[0]
    }
def bstack11llll1111_opy_():
    try:
        import selenium
        return True
    except ImportError:
        return False
def bstack111lll1l111_opy_():
    if bstack1llll1111_opy_.get_property(bstack111l11_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡠࡵࡨࡷࡸ࡯࡯࡯ࠩᱸ")):
        return bstack111l11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨᱹ")
    return bstack111l11_opy_ (u"ࠪࡹࡳࡱ࡮ࡰࡹࡱࡣ࡬ࡸࡩࡥࠩᱺ")
def bstack11l1111l1ll_opy_(driver):
    info = {
        bstack111l11_opy_ (u"ࠫࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠪᱻ"): driver.capabilities,
        bstack111l11_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡥࡩࡥࠩᱼ"): driver.session_id,
        bstack111l11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࠧᱽ"): driver.capabilities.get(bstack111l11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠬ᱾"), None),
        bstack111l11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡡࡹࡩࡷࡹࡩࡰࡰࠪ᱿"): driver.capabilities.get(bstack111l11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪᲀ"), None),
        bstack111l11_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࠬᲁ"): driver.capabilities.get(bstack111l11_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡔࡡ࡮ࡧࠪᲂ"), None),
        bstack111l11_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨᲃ"):driver.capabilities.get(bstack111l11_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠨᲄ"), None),
    }
    if bstack111lll1l111_opy_() == bstack111l11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ᲅ"):
        if bstack1lllll11l_opy_():
            info[bstack111l11_opy_ (u"ࠨࡲࡵࡳࡩࡻࡣࡵࠩᲆ")] = bstack111l11_opy_ (u"ࠩࡤࡴࡵ࠳ࡡࡶࡶࡲࡱࡦࡺࡥࠨᲇ")
        elif driver.capabilities.get(bstack111l11_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫᲈ"), {}).get(bstack111l11_opy_ (u"ࠫࡹࡻࡲࡣࡱࡶࡧࡦࡲࡥࠨᲉ"), False):
            info[bstack111l11_opy_ (u"ࠬࡶࡲࡰࡦࡸࡧࡹ࠭ᲊ")] = bstack111l11_opy_ (u"࠭ࡴࡶࡴࡥࡳࡸࡩࡡ࡭ࡧࠪ᲋")
        else:
            info[bstack111l11_opy_ (u"ࠧࡱࡴࡲࡨࡺࡩࡴࠨ᲌")] = bstack111l11_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵࡧࠪ᲍")
    return info
def bstack1lllll11l_opy_():
    if bstack1llll1111_opy_.get_property(bstack111l11_opy_ (u"ࠩࡤࡴࡵࡥࡡࡶࡶࡲࡱࡦࡺࡥࠨ᲎")):
        return True
    if bstack11ll1l11_opy_(os.environ.get(bstack111l11_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡌࡗࡤࡇࡐࡑࡡࡄ࡙࡙ࡕࡍࡂࡖࡈࠫ᲏"), None)):
        return True
    return False
def bstack11ll1llll_opy_(bstack111ll1lll11_opy_, url, data, config):
    headers = config.get(bstack111l11_opy_ (u"ࠫ࡭࡫ࡡࡥࡧࡵࡷࠬᲐ"), None)
    proxies = bstack111lllll11_opy_(config, url)
    auth = config.get(bstack111l11_opy_ (u"ࠬࡧࡵࡵࡪࠪᲑ"), None)
    response = requests.request(
            bstack111ll1lll11_opy_,
            url=url,
            headers=headers,
            auth=auth,
            json=data,
            proxies=proxies
        )
    return response
def bstack1lll111l_opy_(bstack11111ll1l_opy_, size):
    bstack1l1lll1l11_opy_ = []
    while len(bstack11111ll1l_opy_) > size:
        bstack1lll1l1l11_opy_ = bstack11111ll1l_opy_[:size]
        bstack1l1lll1l11_opy_.append(bstack1lll1l1l11_opy_)
        bstack11111ll1l_opy_ = bstack11111ll1l_opy_[size:]
    bstack1l1lll1l11_opy_.append(bstack11111ll1l_opy_)
    return bstack1l1lll1l11_opy_
def bstack111ll1lllll_opy_(message, bstack11l111ll1ll_opy_=False):
    os.write(1, bytes(message, bstack111l11_opy_ (u"࠭ࡵࡵࡨ࠰࠼ࠬᲒ")))
    os.write(1, bytes(bstack111l11_opy_ (u"ࠧ࡝ࡰࠪᲓ"), bstack111l11_opy_ (u"ࠨࡷࡷࡪ࠲࠾ࠧᲔ")))
    if bstack11l111ll1ll_opy_:
        with open(bstack111l11_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠯ࡲ࠵࠶ࡿ࠭ࠨᲕ") + os.environ[bstack111l11_opy_ (u"ࠪࡆࡘࡥࡔࡆࡕࡗࡓࡕ࡙࡟ࡃࡗࡌࡐࡉࡥࡈࡂࡕࡋࡉࡉࡥࡉࡅࠩᲖ")] + bstack111l11_opy_ (u"ࠫ࠳ࡲ࡯ࡨࠩᲗ"), bstack111l11_opy_ (u"ࠬࡧࠧᲘ")) as f:
            f.write(message + bstack111l11_opy_ (u"࠭࡜࡯ࠩᲙ"))
def bstack1l1l1ll11ll_opy_():
    return os.environ[bstack111l11_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡁࡖࡖࡒࡑࡆ࡚ࡉࡐࡐࠪᲚ")].lower() == bstack111l11_opy_ (u"ࠨࡶࡵࡹࡪ࠭Მ")
def bstack11ll11lll_opy_():
    return bstack1111ll11ll_opy_().replace(tzinfo=None).isoformat() + bstack111l11_opy_ (u"ࠩ࡝ࠫᲜ")
def bstack111ll11l1l1_opy_(start, finish):
    return (datetime.datetime.fromisoformat(finish.rstrip(bstack111l11_opy_ (u"ࠪ࡞ࠬᲝ"))) - datetime.datetime.fromisoformat(start.rstrip(bstack111l11_opy_ (u"ࠫ࡟࠭Პ")))).total_seconds() * 1000
def bstack111llllll1l_opy_(timestamp):
    return bstack11l11l11111_opy_(timestamp).isoformat() + bstack111l11_opy_ (u"ࠬࡠࠧᲟ")
def bstack11l11l11ll1_opy_(bstack11l111lll11_opy_):
    date_format = bstack111l11_opy_ (u"࡚࠭ࠥࠧࡰࠩࡩࠦࠥࡉ࠼ࠨࡑ࠿ࠫࡓ࠯ࠧࡩࠫᲠ")
    bstack111llllllll_opy_ = datetime.datetime.strptime(bstack11l111lll11_opy_, date_format)
    return bstack111llllllll_opy_.isoformat() + bstack111l11_opy_ (u"࡛ࠧࠩᲡ")
def bstack11l111llll1_opy_(outcome):
    _, exception, _ = outcome.excinfo or (None, None, None)
    if exception:
        return bstack111l11_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨᲢ")
    else:
        return bstack111l11_opy_ (u"ࠩࡳࡥࡸࡹࡥࡥࠩᲣ")
def bstack11ll1l11_opy_(val):
    if val is None:
        return False
    return val.__str__().lower() == bstack111l11_opy_ (u"ࠪࡸࡷࡻࡥࠨᲤ")
def bstack11l11l111l1_opy_(val):
    return val.__str__().lower() == bstack111l11_opy_ (u"ࠫ࡫ࡧ࡬ࡴࡧࠪᲥ")
def error_handler(bstack11l111ll111_opy_=Exception, class_method=False, default_value=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except bstack11l111ll111_opy_ as e:
                print(bstack111l11_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࠦࡻࡾࠢ࠰ࡂࠥࢁࡽ࠻ࠢࡾࢁࠧᲦ").format(func.__name__, bstack11l111ll111_opy_.__name__, str(e)))
                return default_value
        return wrapper
    def bstack111ll1ll1l1_opy_(bstack11l11ll1lll_opy_):
        def wrapped(cls, *args, **kwargs):
            try:
                return bstack11l11ll1lll_opy_(cls, *args, **kwargs)
            except bstack11l111ll111_opy_ as e:
                print(bstack111l11_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴࠠࡼࡿࠣ࠱ࡃࠦࡻࡾ࠼ࠣࡿࢂࠨᲧ").format(bstack11l11ll1lll_opy_.__name__, bstack11l111ll111_opy_.__name__, str(e)))
                return default_value
        return wrapped
    if class_method:
        return bstack111ll1ll1l1_opy_
    else:
        return decorator
def bstack1lllll11ll_opy_(bstack1111l11l11_opy_):
    if os.getenv(bstack111l11_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡁࡖࡖࡒࡑࡆ࡚ࡉࡐࡐࠪᲨ")) is not None:
        return bstack11ll1l11_opy_(os.getenv(bstack111l11_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡗࡗࡓࡒࡇࡔࡊࡑࡑࠫᲩ")))
    if bstack111l11_opy_ (u"ࠩࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭Ც") in bstack1111l11l11_opy_ and bstack11l11l111l1_opy_(bstack1111l11l11_opy_[bstack111l11_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧᲫ")]):
        return False
    if bstack111l11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭Წ") in bstack1111l11l11_opy_ and bstack11l11l111l1_opy_(bstack1111l11l11_opy_[bstack111l11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧᲭ")]):
        return False
    return True
def bstack11l11l111_opy_():
    try:
        from pytest_bdd import reporting
        bstack111lll1lll1_opy_ = os.environ.get(bstack111l11_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡛ࡓࡆࡔࡢࡊࡗࡇࡍࡆ࡙ࡒࡖࡐࠨᲮ"), None)
        return bstack111lll1lll1_opy_ is None or bstack111lll1lll1_opy_ == bstack111l11_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠦᲯ")
    except Exception as e:
        return False
def bstack11l1l1lll_opy_(hub_url, CONFIG):
    if bstack1l11111ll1_opy_() <= version.parse(bstack111l11_opy_ (u"ࠨ࠵࠱࠵࠸࠴࠰ࠨᲰ")):
        if hub_url:
            return bstack111l11_opy_ (u"ࠤ࡫ࡸࡹࡶ࠺࠰࠱ࠥᲱ") + hub_url + bstack111l11_opy_ (u"ࠥ࠾࠽࠶࠯ࡸࡦ࠲࡬ࡺࡨࠢᲲ")
        return bstack1l1llllll_opy_
    if hub_url:
        return bstack111l11_opy_ (u"ࠦ࡭ࡺࡴࡱࡵ࠽࠳࠴ࠨᲳ") + hub_url + bstack111l11_opy_ (u"ࠧ࠵ࡷࡥ࠱࡫ࡹࡧࠨᲴ")
    return bstack1l11l111l1_opy_
def bstack111lll1l11l_opy_():
    return isinstance(os.getenv(bstack111l11_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖ࡙ࡕࡇࡖࡘࡤࡖࡌࡖࡉࡌࡒࠬᲵ")), str)
def bstack11ll1lll_opy_(url):
    return urlparse(url).hostname
def bstack1ll1l1l111_opy_(hostname):
    for bstack11l1lll1l1_opy_ in bstack1l1lll1l1l_opy_:
        regex = re.compile(bstack11l1lll1l1_opy_)
        if regex.match(hostname):
            return True
    return False
def bstack11l11llll11_opy_(bstack111llll1111_opy_, file_name, logger):
    bstack1l111111ll_opy_ = os.path.join(os.path.expanduser(bstack111l11_opy_ (u"ࠧࡿࠩᲶ")), bstack111llll1111_opy_)
    try:
        if not os.path.exists(bstack1l111111ll_opy_):
            os.makedirs(bstack1l111111ll_opy_)
        file_path = os.path.join(os.path.expanduser(bstack111l11_opy_ (u"ࠨࢀࠪᲷ")), bstack111llll1111_opy_, file_name)
        if not os.path.isfile(file_path):
            with open(file_path, bstack111l11_opy_ (u"ࠩࡺࠫᲸ")):
                pass
            with open(file_path, bstack111l11_opy_ (u"ࠥࡻ࠰ࠨᲹ")) as outfile:
                json.dump({}, outfile)
        return file_path
    except Exception as e:
        logger.debug(bstack1lllll1111_opy_.format(str(e)))
def bstack11l11l1lll1_opy_(file_name, key, value, logger):
    file_path = bstack11l11llll11_opy_(bstack111l11_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫᲺ"), file_name, logger)
    if file_path != None:
        if os.path.exists(file_path):
            bstack1l1llll1ll_opy_ = json.load(open(file_path, bstack111l11_opy_ (u"ࠬࡸࡢࠨ᲻")))
        else:
            bstack1l1llll1ll_opy_ = {}
        bstack1l1llll1ll_opy_[key] = value
        with open(file_path, bstack111l11_opy_ (u"ࠨࡷࠬࠤ᲼")) as outfile:
            json.dump(bstack1l1llll1ll_opy_, outfile)
def bstack1l1l1lll1l_opy_(file_name, logger):
    file_path = bstack11l11llll11_opy_(bstack111l11_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧᲽ"), file_name, logger)
    bstack1l1llll1ll_opy_ = {}
    if file_path != None and os.path.exists(file_path):
        with open(file_path, bstack111l11_opy_ (u"ࠨࡴࠪᲾ")) as bstack1ll1ll1111_opy_:
            bstack1l1llll1ll_opy_ = json.load(bstack1ll1ll1111_opy_)
    return bstack1l1llll1ll_opy_
def bstack1l11111l1l_opy_(file_path, logger):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.debug(bstack111l11_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡩ࡫࡬ࡦࡶ࡬ࡲ࡬ࠦࡦࡪ࡮ࡨ࠾ࠥ࠭Ჿ") + file_path + bstack111l11_opy_ (u"ࠪࠤࠬ᳀") + str(e))
def bstack1l11111ll1_opy_():
    from selenium import webdriver
    return version.parse(webdriver.__version__)
class Notset:
    def __repr__(self):
        return bstack111l11_opy_ (u"ࠦࡁࡔࡏࡕࡕࡈࡘࡃࠨ᳁")
def bstack1l111l111_opy_(config):
    if bstack111l11_opy_ (u"ࠬ࡯ࡳࡑ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠫ᳂") in config:
        del (config[bstack111l11_opy_ (u"࠭ࡩࡴࡒ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࠬ᳃")])
        return False
    if bstack1l11111ll1_opy_() < version.parse(bstack111l11_opy_ (u"ࠧ࠴࠰࠷࠲࠵࠭᳄")):
        return False
    if bstack1l11111ll1_opy_() >= version.parse(bstack111l11_opy_ (u"ࠨ࠶࠱࠵࠳࠻ࠧ᳅")):
        return True
    if bstack111l11_opy_ (u"ࠩࡸࡷࡪ࡝࠳ࡄࠩ᳆") in config and config[bstack111l11_opy_ (u"ࠪࡹࡸ࡫ࡗ࠴ࡅࠪ᳇")] is False:
        return False
    else:
        return True
def bstack111l1lll1_opy_(args_list, bstack111ll1l1ll1_opy_):
    index = -1
    for value in bstack111ll1l1ll1_opy_:
        try:
            index = args_list.index(value)
            return index
        except Exception as e:
            return index
    return index
def bstack11ll1ll1lll_opy_(a, b):
  for k, v in b.items():
    if isinstance(v, dict) and k in a and isinstance(a[k], dict):
        bstack11ll1ll1lll_opy_(a[k], v)
    else:
        a[k] = v
class Result:
    def __init__(self, result=None, duration=None, exception=None, bstack111ll11lll_opy_=None):
        self.result = result
        self.duration = duration
        self.exception = exception
        self.exception_type = type(self.exception).__name__ if exception else None
        self.bstack111ll11lll_opy_ = bstack111ll11lll_opy_
    @classmethod
    def passed(cls):
        return Result(result=bstack111l11_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫ᳈"))
    @classmethod
    def failed(cls, exception=None):
        return Result(result=bstack111l11_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ᳉"), exception=exception)
    def bstack1111111l1l_opy_(self):
        if self.result != bstack111l11_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭᳊"):
            return None
        if isinstance(self.exception_type, str) and bstack111l11_opy_ (u"ࠢࡂࡵࡶࡩࡷࡺࡩࡰࡰࠥ᳋") in self.exception_type:
            return bstack111l11_opy_ (u"ࠣࡃࡶࡷࡪࡸࡴࡪࡱࡱࡉࡷࡸ࡯ࡳࠤ᳌")
        return bstack111l11_opy_ (u"ࠤࡘࡲ࡭ࡧ࡮ࡥ࡮ࡨࡨࡊࡸࡲࡰࡴࠥ᳍")
    def bstack11l1111l111_opy_(self):
        if self.result != bstack111l11_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪ᳎"):
            return None
        if self.bstack111ll11lll_opy_:
            return self.bstack111ll11lll_opy_
        return bstack111lll11l11_opy_(self.exception)
def bstack111lll11l11_opy_(exc):
    return [traceback.format_exception(exc)]
def bstack11l11l11l1l_opy_(message):
    if isinstance(message, str):
        return not bool(message and message.strip())
    return True
def bstack1l11lllll1_opy_(object, key, default_value):
    if not object or not object.__dict__:
        return default_value
    if key in object.__dict__.keys():
        return object.__dict__.get(key)
    return default_value
def bstack1ll1l1l1ll_opy_(config, logger):
    try:
        import playwright
        bstack111ll1l1l1l_opy_ = playwright.__file__
        bstack111ll11l11l_opy_ = os.path.split(bstack111ll1l1l1l_opy_)
        bstack111lll1l1ll_opy_ = bstack111ll11l11l_opy_[0] + bstack111l11_opy_ (u"ࠫ࠴ࡪࡲࡪࡸࡨࡶ࠴ࡶࡡࡤ࡭ࡤ࡫ࡪ࠵࡬ࡪࡤ࠲ࡧࡱ࡯࠯ࡤ࡮࡬࠲࡯ࡹࠧ᳏")
        os.environ[bstack111l11_opy_ (u"ࠬࡍࡌࡐࡄࡄࡐࡤࡇࡇࡆࡐࡗࡣࡍ࡚ࡔࡑࡡࡓࡖࡔ࡞࡙ࠨ᳐")] = bstack1l11l11l_opy_(config)
        with open(bstack111lll1l1ll_opy_, bstack111l11_opy_ (u"࠭ࡲࠨ᳑")) as f:
            bstack11ll111l1l_opy_ = f.read()
            bstack111lllll1l1_opy_ = bstack111l11_opy_ (u"ࠧࡨ࡮ࡲࡦࡦࡲ࠭ࡢࡩࡨࡲࡹ࠭᳒")
            bstack11l11111ll1_opy_ = bstack11ll111l1l_opy_.find(bstack111lllll1l1_opy_)
            if bstack11l11111ll1_opy_ == -1:
              process = subprocess.Popen(bstack111l11_opy_ (u"ࠣࡰࡳࡱࠥ࡯࡮ࡴࡶࡤࡰࡱࠦࡧ࡭ࡱࡥࡥࡱ࠳ࡡࡨࡧࡱࡸࠧ᳓"), shell=True, cwd=bstack111ll11l11l_opy_[0])
              process.wait()
              bstack111lll11111_opy_ = bstack111l11_opy_ (u"ࠩࠥࡹࡸ࡫ࠠࡴࡶࡵ࡭ࡨࡺࠢ࠼᳔ࠩ")
              bstack11l11111l1l_opy_ = bstack111l11_opy_ (u"ࠥࠦࠧࠦ࡜ࠣࡷࡶࡩࠥࡹࡴࡳ࡫ࡦࡸࡡࠨ࠻ࠡࡥࡲࡲࡸࡺࠠࡼࠢࡥࡳࡴࡺࡳࡵࡴࡤࡴࠥࢃࠠ࠾ࠢࡵࡩࡶࡻࡩࡳࡧࠫࠫ࡬ࡲ࡯ࡣࡣ࡯࠱ࡦ࡭ࡥ࡯ࡶࠪ࠭ࡀࠦࡩࡧࠢࠫࡴࡷࡵࡣࡦࡵࡶ࠲ࡪࡴࡶ࠯ࡉࡏࡓࡇࡇࡌࡠࡃࡊࡉࡓ࡚࡟ࡉࡖࡗࡔࡤࡖࡒࡐ࡚࡜࠭ࠥࡨ࡯ࡰࡶࡶࡸࡷࡧࡰࠩࠫ࠾ࠤࠧࠨ᳕ࠢ")
              bstack11l111111ll_opy_ = bstack11ll111l1l_opy_.replace(bstack111lll11111_opy_, bstack11l11111l1l_opy_)
              with open(bstack111lll1l1ll_opy_, bstack111l11_opy_ (u"ࠫࡼ᳖࠭")) as f:
                f.write(bstack11l111111ll_opy_)
    except Exception as e:
        logger.error(bstack11lll1l11l_opy_.format(str(e)))
def bstack1ll11111l_opy_():
  try:
    bstack111lll11lll_opy_ = os.path.join(tempfile.gettempdir(), bstack111l11_opy_ (u"ࠬࡵࡰࡵ࡫ࡰࡥࡱࡥࡨࡶࡤࡢࡹࡷࡲ࠮࡫ࡵࡲࡲ᳗ࠬ"))
    bstack11l11lll111_opy_ = []
    if os.path.exists(bstack111lll11lll_opy_):
      with open(bstack111lll11lll_opy_) as f:
        bstack11l11lll111_opy_ = json.load(f)
      os.remove(bstack111lll11lll_opy_)
    return bstack11l11lll111_opy_
  except:
    pass
  return []
def bstack1ll1l1ll1_opy_(bstack1ll11l1l1_opy_):
  try:
    bstack11l11lll111_opy_ = []
    bstack111lll11lll_opy_ = os.path.join(tempfile.gettempdir(), bstack111l11_opy_ (u"࠭࡯ࡱࡶ࡬ࡱࡦࡲ࡟ࡩࡷࡥࡣࡺࡸ࡬࠯࡬ࡶࡳࡳ᳘࠭"))
    if os.path.exists(bstack111lll11lll_opy_):
      with open(bstack111lll11lll_opy_) as f:
        bstack11l11lll111_opy_ = json.load(f)
    bstack11l11lll111_opy_.append(bstack1ll11l1l1_opy_)
    with open(bstack111lll11lll_opy_, bstack111l11_opy_ (u"ࠧࡸ᳙ࠩ")) as f:
        json.dump(bstack11l11lll111_opy_, f)
  except:
    pass
def bstack1111lll1l_opy_(logger, bstack11l1111ll11_opy_ = False):
  try:
    test_name = os.environ.get(bstack111l11_opy_ (u"ࠨࡒ࡜ࡘࡊ࡙ࡔࡠࡖࡈࡗ࡙ࡥࡎࡂࡏࡈࠫ᳚"), bstack111l11_opy_ (u"ࠩࠪ᳛"))
    if test_name == bstack111l11_opy_ (u"᳜ࠪࠫ"):
        test_name = threading.current_thread().__dict__.get(bstack111l11_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࡆࡩࡪ࡟ࡵࡧࡶࡸࡤࡴࡡ࡮ࡧ᳝ࠪ"), bstack111l11_opy_ (u"᳞ࠬ࠭"))
    bstack11l1111l11l_opy_ = bstack111l11_opy_ (u"᳟࠭ࠬࠡࠩ").join(threading.current_thread().bstackTestErrorMessages)
    if bstack11l1111ll11_opy_:
        bstack1l1ll1lll_opy_ = os.environ.get(bstack111l11_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡍࡃࡗࡊࡔࡘࡍࡠࡋࡑࡈࡊ࡞ࠧ᳠"), bstack111l11_opy_ (u"ࠨ࠲ࠪ᳡"))
        bstack1l1111l1ll_opy_ = {bstack111l11_opy_ (u"ࠩࡱࡥࡲ࡫᳢ࠧ"): test_name, bstack111l11_opy_ (u"ࠪࡩࡷࡸ࡯ࡳ᳣ࠩ"): bstack11l1111l11l_opy_, bstack111l11_opy_ (u"ࠫ࡮ࡴࡤࡦࡺ᳤ࠪ"): bstack1l1ll1lll_opy_}
        bstack111lllllll1_opy_ = []
        bstack111lll111l1_opy_ = os.path.join(tempfile.gettempdir(), bstack111l11_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࡤࡶࡰࡱࡡࡨࡶࡷࡵࡲࡠ࡮࡬ࡷࡹ࠴ࡪࡴࡱࡱ᳥ࠫ"))
        if os.path.exists(bstack111lll111l1_opy_):
            with open(bstack111lll111l1_opy_) as f:
                bstack111lllllll1_opy_ = json.load(f)
        bstack111lllllll1_opy_.append(bstack1l1111l1ll_opy_)
        with open(bstack111lll111l1_opy_, bstack111l11_opy_ (u"࠭ࡷࠨ᳦")) as f:
            json.dump(bstack111lllllll1_opy_, f)
    else:
        bstack1l1111l1ll_opy_ = {bstack111l11_opy_ (u"ࠧ࡯ࡣࡰࡩ᳧ࠬ"): test_name, bstack111l11_opy_ (u"ࠨࡧࡵࡶࡴࡸ᳨ࠧ"): bstack11l1111l11l_opy_, bstack111l11_opy_ (u"ࠩ࡬ࡲࡩ࡫ࡸࠨᳩ"): str(multiprocessing.current_process().name)}
        if bstack111l11_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡢࡩࡷࡸ࡯ࡳࡡ࡯࡭ࡸࡺࠧᳪ") not in multiprocessing.current_process().__dict__.keys():
            multiprocessing.current_process().bstack_error_list = []
        multiprocessing.current_process().bstack_error_list.append(bstack1l1111l1ll_opy_)
  except Exception as e:
      logger.warn(bstack111l11_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡴࡶࡲࡶࡪࠦࡰࡺࡶࡨࡷࡹࠦࡦࡶࡰࡱࡩࡱࠦࡤࡢࡶࡤ࠾ࠥࢁࡽࠣᳫ").format(e))
def bstack1l1l1l111l_opy_(error_message, test_name, index, logger):
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack111l11_opy_ (u"ࠬ࡬ࡩ࡭ࡧ࡯ࡳࡨࡱࠠ࡯ࡱࡷࠤࡦࡼࡡࡪ࡮ࡤࡦࡱ࡫ࠬࠡࡷࡶ࡭ࡳ࡭ࠠࡣࡣࡶ࡭ࡨࠦࡦࡪ࡮ࡨࠤࡴࡶࡥࡳࡣࡷ࡭ࡴࡴࡳࠨᳬ"))
    try:
      bstack11l11lll11l_opy_ = []
      bstack1l1111l1ll_opy_ = {bstack111l11_opy_ (u"࠭࡮ࡢ࡯ࡨ᳭ࠫ"): test_name, bstack111l11_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭ᳮ"): error_message, bstack111l11_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧᳯ"): index}
      bstack111ll1ll111_opy_ = os.path.join(tempfile.gettempdir(), bstack111l11_opy_ (u"ࠩࡵࡳࡧࡵࡴࡠࡧࡵࡶࡴࡸ࡟࡭࡫ࡶࡸ࠳ࡰࡳࡰࡰࠪᳰ"))
      if os.path.exists(bstack111ll1ll111_opy_):
          with open(bstack111ll1ll111_opy_) as f:
              bstack11l11lll11l_opy_ = json.load(f)
      bstack11l11lll11l_opy_.append(bstack1l1111l1ll_opy_)
      with open(bstack111ll1ll111_opy_, bstack111l11_opy_ (u"ࠪࡻࠬᳱ")) as f:
          json.dump(bstack11l11lll11l_opy_, f)
    except Exception as e:
      logger.warn(bstack111l11_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡴࡶࡲࡶࡪࠦࡲࡰࡤࡲࡸࠥ࡬ࡵ࡯ࡰࡨࡰࠥࡪࡡࡵࡣ࠽ࠤࢀࢃࠢᳲ").format(e))
    return
  bstack11l11lll11l_opy_ = []
  bstack1l1111l1ll_opy_ = {bstack111l11_opy_ (u"ࠬࡴࡡ࡮ࡧࠪᳳ"): test_name, bstack111l11_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬ᳴"): error_message, bstack111l11_opy_ (u"ࠧࡪࡰࡧࡩࡽ࠭ᳵ"): index}
  bstack111ll1ll111_opy_ = os.path.join(tempfile.gettempdir(), bstack111l11_opy_ (u"ࠨࡴࡲࡦࡴࡺ࡟ࡦࡴࡵࡳࡷࡥ࡬ࡪࡵࡷ࠲࡯ࡹ࡯࡯ࠩᳶ"))
  lock_file = bstack111ll1ll111_opy_ + bstack111l11_opy_ (u"ࠩ࠱ࡰࡴࡩ࡫ࠨ᳷")
  try:
    with FileLock(lock_file, timeout=10):
      if os.path.exists(bstack111ll1ll111_opy_):
          with open(bstack111ll1ll111_opy_, bstack111l11_opy_ (u"ࠪࡶࠬ᳸")) as f:
              content = f.read().strip()
              if content:
                  bstack11l11lll11l_opy_ = json.load(open(bstack111ll1ll111_opy_))
      bstack11l11lll11l_opy_.append(bstack1l1111l1ll_opy_)
      with open(bstack111ll1ll111_opy_, bstack111l11_opy_ (u"ࠫࡼ࠭᳹")) as f:
          json.dump(bstack11l11lll11l_opy_, f)
  except Exception as e:
    logger.warn(bstack111l11_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡵࡷࡳࡷ࡫ࠠࡳࡱࡥࡳࡹࠦࡦࡶࡰࡱࡩࡱࠦࡤࡢࡶࡤࠤࡼ࡯ࡴࡩࠢࡩ࡭ࡱ࡫ࠠ࡭ࡱࡦ࡯࡮ࡴࡧ࠻ࠢࡾࢁࠧᳺ").format(e))
def bstack1lll111lll_opy_(bstack1l1l1lllll_opy_, name, logger):
  try:
    bstack1l1111l1ll_opy_ = {bstack111l11_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ᳻"): name, bstack111l11_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭᳼"): bstack1l1l1lllll_opy_, bstack111l11_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧ᳽"): str(threading.current_thread()._name)}
    return bstack1l1111l1ll_opy_
  except Exception as e:
    logger.warn(bstack111l11_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥࡹࡴࡰࡴࡨࠤࡧ࡫ࡨࡢࡸࡨࠤ࡫ࡻ࡮࡯ࡧ࡯ࠤࡩࡧࡴࡢ࠼ࠣࡿࢂࠨ᳾").format(e))
  return
def bstack111llll1lll_opy_():
    return platform.system() == bstack111l11_opy_ (u"࡛ࠪ࡮ࡴࡤࡰࡹࡶࠫ᳿")
def bstack11lll1111_opy_(bstack111ll11ll1l_opy_, config, logger):
    bstack11l11l1ll1l_opy_ = {}
    try:
        return {key: config[key] for key in config if bstack111ll11ll1l_opy_.match(key)}
    except Exception as e:
        logger.debug(bstack111l11_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡧ࡫࡯ࡸࡪࡸࠠࡤࡱࡱࡪ࡮࡭ࠠ࡬ࡧࡼࡷࠥࡨࡹࠡࡴࡨ࡫ࡪࡾࠠ࡮ࡣࡷࡧ࡭ࡀࠠࡼࡿࠥᴀ").format(e))
    return bstack11l11l1ll1l_opy_
def bstack111lllll1ll_opy_(bstack111lll1111l_opy_, bstack111ll1llll1_opy_):
    bstack111ll1l1l11_opy_ = version.parse(bstack111lll1111l_opy_)
    bstack11l111l1l11_opy_ = version.parse(bstack111ll1llll1_opy_)
    if bstack111ll1l1l11_opy_ > bstack11l111l1l11_opy_:
        return 1
    elif bstack111ll1l1l11_opy_ < bstack11l111l1l11_opy_:
        return -1
    else:
        return 0
def bstack1111ll11ll_opy_():
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
def bstack11l11l11111_opy_(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).replace(tzinfo=None)
def bstack111ll11ll11_opy_(framework):
    from browserstack_sdk._version import __version__
    return str(framework) + str(__version__)
def bstack1ll111llll_opy_(options, framework, config, bstack111l111l_opy_={}):
    if options is None:
        return
    if getattr(options, bstack111l11_opy_ (u"ࠬ࡭ࡥࡵࠩᴁ"), None):
        caps = options
    else:
        caps = options.to_capabilities()
    bstack1ll1ll1ll1_opy_ = caps.get(bstack111l11_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧᴂ"))
    bstack11l11l11lll_opy_ = True
    bstack111ll1l11_opy_ = os.environ[bstack111l11_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬᴃ")]
    bstack1ll11llllll_opy_ = config.get(bstack111l11_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨᴄ"), False)
    if bstack1ll11llllll_opy_:
        bstack1lll11l11ll_opy_ = config.get(bstack111l11_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩᴅ"), {})
        bstack1lll11l11ll_opy_[bstack111l11_opy_ (u"ࠪࡥࡺࡺࡨࡕࡱ࡮ࡩࡳ࠭ᴆ")] = os.getenv(bstack111l11_opy_ (u"ࠫࡇ࡙࡟ࡂ࠳࠴࡝ࡤࡐࡗࡕࠩᴇ"))
        bstack11ll1llll1l_opy_ = json.loads(os.getenv(bstack111l11_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡡࡄࡇࡈࡋࡓࡔࡋࡅࡍࡑࡏࡔ࡚ࡡࡆࡓࡓࡌࡉࡈࡗࡕࡅ࡙ࡏࡏࡏࡡ࡜ࡑࡑ࠭ᴈ"), bstack111l11_opy_ (u"࠭ࡻࡾࠩᴉ"))).get(bstack111l11_opy_ (u"ࠧࡴࡥࡤࡲࡳ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨᴊ"))
    if bstack11l11l111l1_opy_(caps.get(bstack111l11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡶࡵࡨ࡛࠸ࡉࠧᴋ"))) or bstack11l11l111l1_opy_(caps.get(bstack111l11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡷࡶࡩࡤࡽ࠳ࡤࠩᴌ"))):
        bstack11l11l11lll_opy_ = False
    if bstack1l111l111_opy_({bstack111l11_opy_ (u"ࠥࡹࡸ࡫ࡗ࠴ࡅࠥᴍ"): bstack11l11l11lll_opy_}):
        bstack1ll1ll1ll1_opy_ = bstack1ll1ll1ll1_opy_ or {}
        bstack1ll1ll1ll1_opy_[bstack111l11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡖࡈࡐ࠭ᴎ")] = bstack111ll11ll11_opy_(framework)
        bstack1ll1ll1ll1_opy_[bstack111l11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧᴏ")] = bstack1l1l1ll11ll_opy_()
        bstack1ll1ll1ll1_opy_[bstack111l11_opy_ (u"࠭ࡴࡦࡵࡷ࡬ࡺࡨࡂࡶ࡫࡯ࡨ࡚ࡻࡩࡥࠩᴐ")] = bstack111ll1l11_opy_
        bstack1ll1ll1ll1_opy_[bstack111l11_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡖࡲࡰࡦࡸࡧࡹࡓࡡࡱࠩᴑ")] = bstack111l111l_opy_
        if bstack1ll11llllll_opy_:
            bstack1ll1ll1ll1_opy_[bstack111l11_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨᴒ")] = bstack1ll11llllll_opy_
            bstack1ll1ll1ll1_opy_[bstack111l11_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩᴓ")] = bstack1lll11l11ll_opy_
            bstack1ll1ll1ll1_opy_[bstack111l11_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪᴔ")][bstack111l11_opy_ (u"ࠫࡸࡩࡡ࡯ࡰࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬᴕ")] = bstack11ll1llll1l_opy_
        if getattr(options, bstack111l11_opy_ (u"ࠬࡹࡥࡵࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸࡾ࠭ᴖ"), None):
            options.set_capability(bstack111l11_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧᴗ"), bstack1ll1ll1ll1_opy_)
        else:
            options[bstack111l11_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨᴘ")] = bstack1ll1ll1ll1_opy_
    else:
        if getattr(options, bstack111l11_opy_ (u"ࠨࡵࡨࡸࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡺࠩᴙ"), None):
            options.set_capability(bstack111l11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡓࡅࡍࠪᴚ"), bstack111ll11ll11_opy_(framework))
            options.set_capability(bstack111l11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠫᴛ"), bstack1l1l1ll11ll_opy_())
            options.set_capability(bstack111l11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡸࡪࡹࡴࡩࡷࡥࡆࡺ࡯࡬ࡥࡗࡸ࡭ࡩ࠭ᴜ"), bstack111ll1l11_opy_)
            options.set_capability(bstack111l11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡧࡻࡩ࡭ࡦࡓࡶࡴࡪࡵࡤࡶࡐࡥࡵ࠭ᴝ"), bstack111l111l_opy_)
            if bstack1ll11llllll_opy_:
                options.set_capability(bstack111l11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬᴞ"), bstack1ll11llllll_opy_)
                options.set_capability(bstack111l11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭ᴟ"), bstack1lll11l11ll_opy_)
                options.set_capability(bstack111l11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡏࡱࡶ࡬ࡳࡳࡹ࠮ࡴࡥࡤࡲࡳ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨᴠ"), bstack11ll1llll1l_opy_)
        else:
            options[bstack111l11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡓࡅࡍࠪᴡ")] = bstack111ll11ll11_opy_(framework)
            options[bstack111l11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠫᴢ")] = bstack1l1l1ll11ll_opy_()
            options[bstack111l11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡸࡪࡹࡴࡩࡷࡥࡆࡺ࡯࡬ࡥࡗࡸ࡭ࡩ࠭ᴣ")] = bstack111ll1l11_opy_
            options[bstack111l11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡧࡻࡩ࡭ࡦࡓࡶࡴࡪࡵࡤࡶࡐࡥࡵ࠭ᴤ")] = bstack111l111l_opy_
            if bstack1ll11llllll_opy_:
                options[bstack111l11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬᴥ")] = bstack1ll11llllll_opy_
                options[bstack111l11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭ᴦ")] = bstack1lll11l11ll_opy_
                options[bstack111l11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡏࡱࡶ࡬ࡳࡳࡹࠧᴧ")][bstack111l11_opy_ (u"ࠩࡶࡧࡦࡴ࡮ࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪᴨ")] = bstack11ll1llll1l_opy_
    return options
def bstack11l11l1l111_opy_(bstack111llll11ll_opy_, framework):
    bstack111l111l_opy_ = bstack1llll1111_opy_.get_property(bstack111l11_opy_ (u"ࠥࡔࡑࡇ࡙ࡘࡔࡌࡋࡍ࡚࡟ࡑࡔࡒࡈ࡚ࡉࡔࡠࡏࡄࡔࠧᴩ"))
    if bstack111llll11ll_opy_ and len(bstack111llll11ll_opy_.split(bstack111l11_opy_ (u"ࠫࡨࡧࡰࡴ࠿ࠪᴪ"))) > 1:
        ws_url = bstack111llll11ll_opy_.split(bstack111l11_opy_ (u"ࠬࡩࡡࡱࡵࡀࠫᴫ"))[0]
        if bstack111l11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮ࠩᴬ") in ws_url:
            from browserstack_sdk._version import __version__
            bstack111lll1l1l1_opy_ = json.loads(urllib.parse.unquote(bstack111llll11ll_opy_.split(bstack111l11_opy_ (u"ࠧࡤࡣࡳࡷࡂ࠭ᴭ"))[1]))
            bstack111lll1l1l1_opy_ = bstack111lll1l1l1_opy_ or {}
            bstack111ll1l11_opy_ = os.environ[bstack111l11_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭ᴮ")]
            bstack111lll1l1l1_opy_[bstack111l11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡓࡅࡍࠪᴯ")] = str(framework) + str(__version__)
            bstack111lll1l1l1_opy_[bstack111l11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠫᴰ")] = bstack1l1l1ll11ll_opy_()
            bstack111lll1l1l1_opy_[bstack111l11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡸࡪࡹࡴࡩࡷࡥࡆࡺ࡯࡬ࡥࡗࡸ࡭ࡩ࠭ᴱ")] = bstack111ll1l11_opy_
            bstack111lll1l1l1_opy_[bstack111l11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡧࡻࡩ࡭ࡦࡓࡶࡴࡪࡵࡤࡶࡐࡥࡵ࠭ᴲ")] = bstack111l111l_opy_
            bstack111llll11ll_opy_ = bstack111llll11ll_opy_.split(bstack111l11_opy_ (u"࠭ࡣࡢࡲࡶࡁࠬᴳ"))[0] + bstack111l11_opy_ (u"ࠧࡤࡣࡳࡷࡂ࠭ᴴ") + urllib.parse.quote(json.dumps(bstack111lll1l1l1_opy_))
    return bstack111llll11ll_opy_
def bstack111l11l1_opy_():
    global bstack1lll1111ll_opy_
    from playwright._impl._browser_type import BrowserType
    bstack1lll1111ll_opy_ = BrowserType.connect
    return bstack1lll1111ll_opy_
def bstack11l1ll11l1_opy_(framework_name):
    global bstack1l1llll11l_opy_
    bstack1l1llll11l_opy_ = framework_name
    return framework_name
def bstack11ll1l1ll1_opy_(self, *args, **kwargs):
    global bstack1lll1111ll_opy_
    try:
        global bstack1l1llll11l_opy_
        if bstack111l11_opy_ (u"ࠨࡹࡶࡉࡳࡪࡰࡰ࡫ࡱࡸࠬᴵ") in kwargs:
            kwargs[bstack111l11_opy_ (u"ࠩࡺࡷࡊࡴࡤࡱࡱ࡬ࡲࡹ࠭ᴶ")] = bstack11l11l1l111_opy_(
                kwargs.get(bstack111l11_opy_ (u"ࠪࡻࡸࡋ࡮ࡥࡲࡲ࡭ࡳࡺࠧᴷ"), None),
                bstack1l1llll11l_opy_
            )
    except Exception as e:
        logger.error(bstack111l11_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡻ࡭࡫࡮ࠡࡲࡵࡳࡨ࡫ࡳࡴ࡫ࡱ࡫࡙ࠥࡄࡌࠢࡦࡥࡵࡹ࠺ࠡࡽࢀࠦᴸ").format(str(e)))
    return bstack1lll1111ll_opy_(self, *args, **kwargs)
def bstack111lll11l1l_opy_(bstack11l11111111_opy_, proxies):
    proxy_settings = {}
    try:
        if not proxies:
            proxies = bstack111lllll11_opy_(bstack11l11111111_opy_, bstack111l11_opy_ (u"ࠧࠨᴹ"))
        if proxies and proxies.get(bstack111l11_opy_ (u"ࠨࡨࡵࡶࡳࡷࠧᴺ")):
            parsed_url = urlparse(proxies.get(bstack111l11_opy_ (u"ࠢࡩࡶࡷࡴࡸࠨᴻ")))
            if parsed_url and parsed_url.hostname: proxy_settings[bstack111l11_opy_ (u"ࠨࡲࡵࡳࡽࡿࡈࡰࡵࡷࠫᴼ")] = str(parsed_url.hostname)
            if parsed_url and parsed_url.port: proxy_settings[bstack111l11_opy_ (u"ࠩࡳࡶࡴࡾࡹࡑࡱࡵࡸࠬᴽ")] = str(parsed_url.port)
            if parsed_url and parsed_url.username: proxy_settings[bstack111l11_opy_ (u"ࠪࡴࡷࡵࡸࡺࡗࡶࡩࡷ࠭ᴾ")] = str(parsed_url.username)
            if parsed_url and parsed_url.password: proxy_settings[bstack111l11_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡓࡥࡸࡹࠧᴿ")] = str(parsed_url.password)
        return proxy_settings
    except:
        return proxy_settings
def bstack1ll11111_opy_(bstack11l11111111_opy_):
    bstack11l11l11l11_opy_ = {
        bstack11l1lll1ll1_opy_[bstack11l11ll11ll_opy_]: bstack11l11111111_opy_[bstack11l11ll11ll_opy_]
        for bstack11l11ll11ll_opy_ in bstack11l11111111_opy_
        if bstack11l11ll11ll_opy_ in bstack11l1lll1ll1_opy_
    }
    bstack11l11l11l11_opy_[bstack111l11_opy_ (u"ࠧࡶࡲࡰࡺࡼࡗࡪࡺࡴࡪࡰࡪࡷࠧᵀ")] = bstack111lll11l1l_opy_(bstack11l11111111_opy_, bstack1llll1111_opy_.get_property(bstack111l11_opy_ (u"ࠨࡰࡳࡱࡻࡽࡘ࡫ࡴࡵ࡫ࡱ࡫ࡸࠨᵁ")))
    bstack11l1111llll_opy_ = [element.lower() for element in bstack11l1llll1l1_opy_]
    bstack111ll1l111l_opy_(bstack11l11l11l11_opy_, bstack11l1111llll_opy_)
    return bstack11l11l11l11_opy_
def bstack111ll1l111l_opy_(d, keys):
    for key in list(d.keys()):
        if key.lower() in keys:
            d[key] = bstack111l11_opy_ (u"ࠢࠫࠬ࠭࠮ࠧᵂ")
    for value in d.values():
        if isinstance(value, dict):
            bstack111ll1l111l_opy_(value, keys)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    bstack111ll1l111l_opy_(item, keys)
def bstack1l1lll1111l_opy_():
    bstack11l11l1l1l1_opy_ = [os.environ.get(bstack111l11_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡇࡋࡏࡉࡘࡥࡄࡊࡔࠥᵃ")), os.path.join(os.path.expanduser(bstack111l11_opy_ (u"ࠤࢁࠦᵄ")), bstack111l11_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪᵅ")), os.path.join(bstack111l11_opy_ (u"ࠫ࠴ࡺ࡭ࡱࠩᵆ"), bstack111l11_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬᵇ"))]
    for path in bstack11l11l1l1l1_opy_:
        if path is None:
            continue
        try:
            if os.path.exists(path):
                logger.debug(bstack111l11_opy_ (u"ࠨࡆࡪ࡮ࡨࠤࠬࠨᵈ") + str(path) + bstack111l11_opy_ (u"ࠢࠨࠢࡨࡼ࡮ࡹࡴࡴ࠰ࠥᵉ"))
                if not os.access(path, os.W_OK):
                    logger.debug(bstack111l11_opy_ (u"ࠣࡉ࡬ࡺ࡮ࡴࡧࠡࡲࡨࡶࡲ࡯ࡳࡴ࡫ࡲࡲࡸࠦࡦࡰࡴࠣࠫࠧᵊ") + str(path) + bstack111l11_opy_ (u"ࠤࠪࠦᵋ"))
                    os.chmod(path, 0o777)
                else:
                    logger.debug(bstack111l11_opy_ (u"ࠥࡊ࡮ࡲࡥࠡࠩࠥᵌ") + str(path) + bstack111l11_opy_ (u"ࠦࠬࠦࡡ࡭ࡴࡨࡥࡩࡿࠠࡩࡣࡶࠤࡹ࡮ࡥࠡࡴࡨࡵࡺ࡯ࡲࡦࡦࠣࡴࡪࡸ࡭ࡪࡵࡶ࡭ࡴࡴࡳ࠯ࠤᵍ"))
            else:
                logger.debug(bstack111l11_opy_ (u"ࠧࡉࡲࡦࡣࡷ࡭ࡳ࡭ࠠࡧ࡫࡯ࡩࠥ࠭ࠢᵎ") + str(path) + bstack111l11_opy_ (u"ࠨࠧࠡࡹ࡬ࡸ࡭ࠦࡷࡳ࡫ࡷࡩࠥࡶࡥࡳ࡯࡬ࡷࡸ࡯࡯࡯࠰ࠥᵏ"))
                os.makedirs(path, exist_ok=True)
                os.chmod(path, 0o777)
            logger.debug(bstack111l11_opy_ (u"ࠢࡐࡲࡨࡶࡦࡺࡩࡰࡰࠣࡷࡺࡩࡣࡦࡧࡧࡩࡩࠦࡦࡰࡴࠣࠫࠧᵐ") + str(path) + bstack111l11_opy_ (u"ࠣࠩ࠱ࠦᵑ"))
            return path
        except Exception as e:
            logger.debug(bstack111l11_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡹࡥࡵࠢࡸࡴࠥ࡬ࡩ࡭ࡧࠣࠫࢀࡶࡡࡵࡪࢀࠫ࠿ࠦࠢᵒ") + str(e) + bstack111l11_opy_ (u"ࠥࠦᵓ"))
    logger.debug(bstack111l11_opy_ (u"ࠦࡆࡲ࡬ࠡࡲࡤࡸ࡭ࡹࠠࡧࡣ࡬ࡰࡪࡪ࠮ࠣᵔ"))
    return None
@measure(event_name=EVENTS.bstack11l1l1l1lll_opy_, stage=STAGE.bstack111lllll1_opy_)
def bstack1lll111l111_opy_(binary_path, bstack1ll1l1lll1l_opy_, bs_config):
    logger.debug(bstack111l11_opy_ (u"ࠧࡉࡵࡳࡴࡨࡲࡹࠦࡃࡍࡋࠣࡔࡦࡺࡨࠡࡨࡲࡹࡳࡪ࠺ࠡࡽࢀࠦᵕ").format(binary_path))
    bstack11l1111ll1l_opy_ = bstack111l11_opy_ (u"࠭ࠧᵖ")
    bstack111ll11l1ll_opy_ = {
        bstack111l11_opy_ (u"ࠧࡴࡦ࡮ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬᵗ"): __version__,
        bstack111l11_opy_ (u"ࠣࡱࡶࠦᵘ"): platform.system(),
        bstack111l11_opy_ (u"ࠤࡲࡷࡤࡧࡲࡤࡪࠥᵙ"): platform.machine(),
        bstack111l11_opy_ (u"ࠥࡧࡱ࡯࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠣᵚ"): bstack111l11_opy_ (u"ࠫ࠵࠭ᵛ"),
        bstack111l11_opy_ (u"ࠧࡹࡤ࡬ࡡ࡯ࡥࡳ࡭ࡵࡢࡩࡨࠦᵜ"): bstack111l11_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭ᵝ")
    }
    bstack11l111ll1l1_opy_(bstack111ll11l1ll_opy_)
    try:
        if binary_path:
            bstack111ll11l1ll_opy_[bstack111l11_opy_ (u"ࠧࡤ࡮࡬ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬᵞ")] = subprocess.check_output([binary_path, bstack111l11_opy_ (u"ࠣࡸࡨࡶࡸ࡯࡯࡯ࠤᵟ")]).strip().decode(bstack111l11_opy_ (u"ࠩࡸࡸ࡫࠳࠸ࠨᵠ"))
        response = requests.request(
            bstack111l11_opy_ (u"ࠪࡋࡊ࡚ࠧᵡ"),
            url=bstack11l1l11l1l_opy_(bstack11l1ll11l11_opy_),
            headers=None,
            auth=(bs_config[bstack111l11_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭ᵢ")], bs_config[bstack111l11_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨᵣ")]),
            json=None,
            params=bstack111ll11l1ll_opy_
        )
        data = response.json()
        if response.status_code == 200 and bstack111l11_opy_ (u"࠭ࡵࡳ࡮ࠪᵤ") in data.keys() and bstack111l11_opy_ (u"ࠧࡶࡲࡧࡥࡹ࡫ࡤࡠࡥ࡯࡭ࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ᵥ") in data.keys():
            logger.debug(bstack111l11_opy_ (u"ࠣࡐࡨࡩࡩࠦࡴࡰࠢࡸࡴࡩࡧࡴࡦࠢࡥ࡭ࡳࡧࡲࡺ࠮ࠣࡧࡺࡸࡲࡦࡰࡷࠤࡧ࡯࡮ࡢࡴࡼࠤࡻ࡫ࡲࡴ࡫ࡲࡲ࠿ࠦࡻࡾࠤᵦ").format(bstack111ll11l1ll_opy_[bstack111l11_opy_ (u"ࠩࡦࡰ࡮ࡥࡶࡦࡴࡶ࡭ࡴࡴࠧᵧ")]))
            if bstack111l11_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡅࡍࡓࡇࡒ࡚ࡡࡘࡖࡑ࠭ᵨ") in os.environ:
                logger.debug(bstack111l11_opy_ (u"ࠦࡘࡱࡩࡱࡲ࡬ࡲ࡬ࠦࡢࡪࡰࡤࡶࡾࠦࡤࡰࡹࡱࡰࡴࡧࡤࠡࡣࡶࠤࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡆࡎࡔࡁࡓ࡛ࡢ࡙ࡗࡒࠠࡪࡵࠣࡷࡪࡺࠢᵩ"))
                data[bstack111l11_opy_ (u"ࠬࡻࡲ࡭ࠩᵪ")] = os.environ[bstack111l11_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡈࡉࡏࡃࡕ࡝ࡤ࡛ࡒࡍࠩᵫ")]
            bstack11l111l1lll_opy_ = bstack111lll1llll_opy_(data[bstack111l11_opy_ (u"ࠧࡶࡴ࡯ࠫᵬ")], bstack1ll1l1lll1l_opy_)
            bstack11l1111ll1l_opy_ = os.path.join(bstack1ll1l1lll1l_opy_, bstack11l111l1lll_opy_)
            os.chmod(bstack11l1111ll1l_opy_, 0o777) # bstack11l111l111l_opy_ permission
            return bstack11l1111ll1l_opy_
    except Exception as e:
        logger.debug(bstack111l11_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦࡤࡰࡹࡱࡰࡴࡧࡤࡪࡰࡪࠤࡳ࡫ࡷࠡࡕࡇࡏࠥࢁࡽࠣᵭ").format(e))
    return binary_path
def bstack11l111ll1l1_opy_(bstack111ll11l1ll_opy_):
    try:
        if bstack111l11_opy_ (u"ࠩ࡯࡭ࡳࡻࡸࠨᵮ") not in bstack111ll11l1ll_opy_[bstack111l11_opy_ (u"ࠪࡳࡸ࠭ᵯ")].lower():
            return
        if os.path.exists(bstack111l11_opy_ (u"ࠦ࠴࡫ࡴࡤ࠱ࡲࡷ࠲ࡸࡥ࡭ࡧࡤࡷࡪࠨᵰ")):
            with open(bstack111l11_opy_ (u"ࠧ࠵ࡥࡵࡥ࠲ࡳࡸ࠳ࡲࡦ࡮ࡨࡥࡸ࡫ࠢᵱ"), bstack111l11_opy_ (u"ࠨࡲࠣᵲ")) as f:
                bstack111ll1l11ll_opy_ = {}
                for line in f:
                    if bstack111l11_opy_ (u"ࠢ࠾ࠤᵳ") in line:
                        key, value = line.rstrip().split(bstack111l11_opy_ (u"ࠣ࠿ࠥᵴ"), 1)
                        bstack111ll1l11ll_opy_[key] = value.strip(bstack111l11_opy_ (u"ࠩࠥࡠࠬ࠭ᵵ"))
                bstack111ll11l1ll_opy_[bstack111l11_opy_ (u"ࠪࡨ࡮ࡹࡴࡳࡱࠪᵶ")] = bstack111ll1l11ll_opy_.get(bstack111l11_opy_ (u"ࠦࡎࡊࠢᵷ"), bstack111l11_opy_ (u"ࠧࠨᵸ"))
        elif os.path.exists(bstack111l11_opy_ (u"ࠨ࠯ࡦࡶࡦ࠳ࡦࡲࡰࡪࡰࡨ࠱ࡷ࡫࡬ࡦࡣࡶࡩࠧᵹ")):
            bstack111ll11l1ll_opy_[bstack111l11_opy_ (u"ࠧࡥ࡫ࡶࡸࡷࡵࠧᵺ")] = bstack111l11_opy_ (u"ࠨࡣ࡯ࡴ࡮ࡴࡥࠨᵻ")
    except Exception as e:
        logger.debug(bstack111l11_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥ࡭ࡥࡵࠢࡧ࡭ࡸࡺࡲࡰࠢࡲࡪࠥࡲࡩ࡯ࡷࡻࠦᵼ") + e)
@measure(event_name=EVENTS.bstack11l1l1lll11_opy_, stage=STAGE.bstack111lllll1_opy_)
def bstack111lll1llll_opy_(bstack111ll1l1111_opy_, bstack11l11ll111l_opy_):
    logger.debug(bstack111l11_opy_ (u"ࠥࡈࡴࡽ࡮࡭ࡱࡤࡨ࡮ࡴࡧࠡࡕࡇࡏࠥࡨࡩ࡯ࡣࡵࡽࠥ࡬ࡲࡰ࡯࠽ࠤࠧᵽ") + str(bstack111ll1l1111_opy_) + bstack111l11_opy_ (u"ࠦࠧᵾ"))
    zip_path = os.path.join(bstack11l11ll111l_opy_, bstack111l11_opy_ (u"ࠧࡪ࡯ࡸࡰ࡯ࡳࡦࡪࡥࡥࡡࡩ࡭ࡱ࡫࠮ࡻ࡫ࡳࠦᵿ"))
    bstack11l111l1lll_opy_ = bstack111l11_opy_ (u"࠭ࠧᶀ")
    with requests.get(bstack111ll1l1111_opy_, stream=True) as response:
        response.raise_for_status()
        with open(zip_path, bstack111l11_opy_ (u"ࠢࡸࡤࠥᶁ")) as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        logger.debug(bstack111l11_opy_ (u"ࠣࡈ࡬ࡰࡪࠦࡤࡰࡹࡱࡰࡴࡧࡤࡦࡦࠣࡷࡺࡩࡣࡦࡵࡶࡪࡺࡲ࡬ࡺ࠰ࠥᶂ"))
    with zipfile.ZipFile(zip_path, bstack111l11_opy_ (u"ࠩࡵࠫᶃ")) as zip_ref:
        bstack11l11ll11l1_opy_ = zip_ref.namelist()
        if len(bstack11l11ll11l1_opy_) > 0:
            bstack11l111l1lll_opy_ = bstack11l11ll11l1_opy_[0] # bstack11l111l11l1_opy_ bstack11l1ll111ll_opy_ will be bstack1111l1l111_opy_ 1 file i.e. the binary in the zip
        zip_ref.extractall(bstack11l11ll111l_opy_)
        logger.debug(bstack111l11_opy_ (u"ࠥࡊ࡮ࡲࡥࡴࠢࡶࡹࡨࡩࡥࡴࡵࡩࡹࡱࡲࡹࠡࡧࡻࡸࡷࡧࡣࡵࡧࡧࠤࡹࡵࠠࠨࠤᶄ") + str(bstack11l11ll111l_opy_) + bstack111l11_opy_ (u"ࠦࠬࠨᶅ"))
    os.remove(zip_path)
    return bstack11l111l1lll_opy_
def get_cli_dir():
    bstack111llll1l1l_opy_ = bstack1l1lll1111l_opy_()
    if bstack111llll1l1l_opy_:
        bstack1ll1l1lll1l_opy_ = os.path.join(bstack111llll1l1l_opy_, bstack111l11_opy_ (u"ࠧࡩ࡬ࡪࠤᶆ"))
        if not os.path.exists(bstack1ll1l1lll1l_opy_):
            os.makedirs(bstack1ll1l1lll1l_opy_, mode=0o777, exist_ok=True)
        return bstack1ll1l1lll1l_opy_
    else:
        raise FileNotFoundError(bstack111l11_opy_ (u"ࠨࡎࡰࠢࡺࡶ࡮ࡺࡡࡣ࡮ࡨࠤࡩ࡯ࡲࡦࡥࡷࡳࡷࡿࠠࡢࡸࡤ࡭ࡱࡧࡢ࡭ࡧࠣࡪࡴࡸࠠࡵࡪࡨࠤࡘࡊࡋࠡࡤ࡬ࡲࡦࡸࡹ࠯ࠤᶇ"))
def bstack1lll11ll1l1_opy_(bstack1ll1l1lll1l_opy_):
    bstack111l11_opy_ (u"ࠢࠣࠤࡊࡩࡹࠦࡴࡩࡧࠣࡴࡦࡺࡨࠡࡨࡲࡶࠥࡺࡨࡦࠢࡅࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࠡࡕࡇࡏࠥࡨࡩ࡯ࡣࡵࡽࠥ࡯࡮ࠡࡣࠣࡻࡷ࡯ࡴࡢࡤ࡯ࡩࠥࡪࡩࡳࡧࡦࡸࡴࡸࡹ࠯ࠤࠥࠦᶈ")
    bstack111ll1ll11l_opy_ = [
        os.path.join(bstack1ll1l1lll1l_opy_, f)
        for f in os.listdir(bstack1ll1l1lll1l_opy_)
        if os.path.isfile(os.path.join(bstack1ll1l1lll1l_opy_, f)) and f.startswith(bstack111l11_opy_ (u"ࠣࡤ࡬ࡲࡦࡸࡹ࠮ࠤᶉ"))
    ]
    if len(bstack111ll1ll11l_opy_) > 0:
        return max(bstack111ll1ll11l_opy_, key=os.path.getmtime) # get bstack111lllll11l_opy_ binary
    return bstack111l11_opy_ (u"ࠤࠥᶊ")
def bstack11ll1l11l1l_opy_():
  from selenium import webdriver
  return version.parse(webdriver.__version__)
def bstack1ll11l1l11l_opy_(d, u):
  for k, v in u.items():
    if isinstance(v, collections.abc.Mapping):
      d[k] = bstack1ll11l1l11l_opy_(d.get(k, {}), v)
    else:
      if isinstance(v, list):
        d[k] = d.get(k, []) + v
      else:
        d[k] = v
  return d
def bstack1l1ll1lll1_opy_(data, keys, default=None):
    bstack111l11_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࡗࡦ࡬ࡥ࡭ࡻࠣ࡫ࡪࡺࠠࡢࠢࡱࡩࡸࡺࡥࡥࠢࡹࡥࡱࡻࡥࠡࡨࡵࡳࡲࠦࡡࠡࡦ࡬ࡧࡹ࡯࡯࡯ࡣࡵࡽࠥࡵࡲࠡ࡮࡬ࡷࡹ࠴ࠊࠡࠢࠣࠤ࠿ࡶࡡࡳࡣࡰࠤࡩࡧࡴࡢ࠼ࠣࡘ࡭࡫ࠠࡥ࡫ࡦࡸ࡮ࡵ࡮ࡢࡴࡼࠤࡴࡸࠠ࡭࡫ࡶࡸࠥࡺ࡯ࠡࡶࡵࡥࡻ࡫ࡲࡴࡧ࠱ࠎࠥࠦࠠࠡ࠼ࡳࡥࡷࡧ࡭ࠡ࡭ࡨࡽࡸࡀࠠࡂࠢ࡯࡭ࡸࡺࠠࡰࡨࠣ࡯ࡪࡿࡳ࠰࡫ࡱࡨ࡮ࡩࡥࡴࠢࡵࡩࡵࡸࡥࡴࡧࡱࡸ࡮ࡴࡧࠡࡶ࡫ࡩࠥࡶࡡࡵࡪ࠱ࠎࠥࠦࠠࠡ࠼ࡳࡥࡷࡧ࡭ࠡࡦࡨࡪࡦࡻ࡬ࡵ࠼࡚ࠣࡦࡲࡵࡦࠢࡷࡳࠥࡸࡥࡵࡷࡵࡲࠥ࡯ࡦࠡࡶ࡫ࡩࠥࡶࡡࡵࡪࠣࡨࡴ࡫ࡳࠡࡰࡲࡸࠥ࡫ࡸࡪࡵࡷ࠲ࠏࠦࠠࠡࠢ࠽ࡶࡪࡺࡵࡳࡰ࠽ࠤ࡙࡮ࡥࠡࡸࡤࡰࡺ࡫ࠠࡢࡶࠣࡸ࡭࡫ࠠ࡯ࡧࡶࡸࡪࡪࠠࡱࡣࡷ࡬࠱ࠦ࡯ࡳࠢࡧࡩ࡫ࡧࡵ࡭ࡶࠣ࡭࡫ࠦ࡮ࡰࡶࠣࡪࡴࡻ࡮ࡥ࠰ࠍࠤࠥࠦࠠࠣࠤࠥᶋ")
    if not data:
        return default
    current = data
    try:
        for key in keys:
            if isinstance(current, dict):
                current = current[key]
            elif isinstance(current, list) and isinstance(key, int):
                current = current[key]
            else:
                return default
        return current
    except (KeyError, IndexError, TypeError):
        return default