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
from uuid import uuid4
from bstack_utils.helper import bstack11ll11lll_opy_, bstack111ll11l1l1_opy_
from bstack_utils.bstack1111111l1_opy_ import bstack1lllllllll1l_opy_
class bstack111l11l1ll_opy_:
    def __init__(self, name=None, code=None, uuid=None, file_path=None, started_at=None, framework=None, tags=[], scope=[], bstack1lllll11ll11_opy_=None, bstack1lllll111ll1_opy_=True, bstack1l1111lll11_opy_=None, bstack1l1lll1ll_opy_=None, result=None, duration=None, bstack111l111ll1_opy_=None, meta={}):
        self.bstack111l111ll1_opy_ = bstack111l111ll1_opy_
        self.name = name
        self.code = code
        self.file_path = file_path
        self.uuid = uuid
        if not self.uuid and bstack1lllll111ll1_opy_:
            self.uuid = uuid4().__str__()
        self.started_at = started_at
        self.framework = framework
        self.tags = tags
        self.scope = scope
        self.bstack1lllll11ll11_opy_ = bstack1lllll11ll11_opy_
        self.bstack1l1111lll11_opy_ = bstack1l1111lll11_opy_
        self.bstack1l1lll1ll_opy_ = bstack1l1lll1ll_opy_
        self.result = result
        self.duration = duration
        self.meta = meta
        self.hooks = []
    def bstack1111llll1l_opy_(self):
        if self.uuid:
            return self.uuid
        self.uuid = uuid4().__str__()
        return self.uuid
    def bstack111ll1llll_opy_(self, meta):
        self.meta = meta
    def bstack111ll1ll11_opy_(self, hooks):
        self.hooks = hooks
    def bstack1lllll11ll1l_opy_(self):
        bstack1lllll11lll1_opy_ = os.path.relpath(self.file_path, start=os.getcwd())
        return {
            bstack111l11_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪ "): bstack1lllll11lll1_opy_,
            bstack111l11_opy_ (u"ࠨ࡮ࡲࡧࡦࡺࡩࡰࡰࠪ‰"): bstack1lllll11lll1_opy_,
            bstack111l11_opy_ (u"ࠩࡹࡧࡤ࡬ࡩ࡭ࡧࡳࡥࡹ࡮ࠧ‱"): bstack1lllll11lll1_opy_
        }
    def set(self, **kwargs):
        for key, val in kwargs.items():
            if not hasattr(self, key):
                raise TypeError(bstack111l11_opy_ (u"࡙ࠥࡳ࡫ࡸࡱࡧࡦࡸࡪࡪࠠࡢࡴࡪࡹࡲ࡫࡮ࡵ࠼ࠣࠦ′") + key)
            setattr(self, key, val)
    def bstack1lllll11l1l1_opy_(self):
        return {
            bstack111l11_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ″"): self.name,
            bstack111l11_opy_ (u"ࠬࡨ࡯ࡥࡻࠪ‴"): {
                bstack111l11_opy_ (u"࠭࡬ࡢࡰࡪࠫ‵"): bstack111l11_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴࠧ‶"),
                bstack111l11_opy_ (u"ࠨࡥࡲࡨࡪ࠭‷"): self.code
            },
            bstack111l11_opy_ (u"ࠩࡶࡧࡴࡶࡥࡴࠩ‸"): self.scope,
            bstack111l11_opy_ (u"ࠪࡸࡦ࡭ࡳࠨ‹"): self.tags,
            bstack111l11_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧ›"): self.framework,
            bstack111l11_opy_ (u"ࠬࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠩ※"): self.started_at
        }
    def bstack1lllll11l1ll_opy_(self):
        return {
         bstack111l11_opy_ (u"࠭࡭ࡦࡶࡤࠫ‼"): self.meta
        }
    def bstack1lllll1l11l1_opy_(self):
        return {
            bstack111l11_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳࡒࡦࡴࡸࡲࡕࡧࡲࡢ࡯ࠪ‽"): {
                bstack111l11_opy_ (u"ࠨࡴࡨࡶࡺࡴ࡟࡯ࡣࡰࡩࠬ‾"): self.bstack1lllll11ll11_opy_
            }
        }
    def bstack1lllll1l11ll_opy_(self, bstack1lllll111lll_opy_, details):
        step = next(filter(lambda st: st[bstack111l11_opy_ (u"ࠩ࡬ࡨࠬ‿")] == bstack1lllll111lll_opy_, self.meta[bstack111l11_opy_ (u"ࠪࡷࡹ࡫ࡰࡴࠩ⁀")]), None)
        step.update(details)
    def bstack11ll11lll1_opy_(self, bstack1lllll111lll_opy_):
        step = next(filter(lambda st: st[bstack111l11_opy_ (u"ࠫ࡮ࡪࠧ⁁")] == bstack1lllll111lll_opy_, self.meta[bstack111l11_opy_ (u"ࠬࡹࡴࡦࡲࡶࠫ⁂")]), None)
        step.update({
            bstack111l11_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪ⁃"): bstack11ll11lll_opy_()
        })
    def bstack111ll11111_opy_(self, bstack1lllll111lll_opy_, result, duration=None):
        bstack1l1111lll11_opy_ = bstack11ll11lll_opy_()
        if bstack1lllll111lll_opy_ is not None and self.meta.get(bstack111l11_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭⁄")):
            step = next(filter(lambda st: st[bstack111l11_opy_ (u"ࠨ࡫ࡧࠫ⁅")] == bstack1lllll111lll_opy_, self.meta[bstack111l11_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨ⁆")]), None)
            step.update({
                bstack111l11_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨ⁇"): bstack1l1111lll11_opy_,
                bstack111l11_opy_ (u"ࠫࡩࡻࡲࡢࡶ࡬ࡳࡳ࠭⁈"): duration if duration else bstack111ll11l1l1_opy_(step[bstack111l11_opy_ (u"ࠬࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠩ⁉")], bstack1l1111lll11_opy_),
                bstack111l11_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭⁊"): result.result,
                bstack111l11_opy_ (u"ࠧࡧࡣ࡬ࡰࡺࡸࡥࠨ⁋"): str(result.exception) if result.exception else None
            })
    def add_step(self, bstack1lllll1111ll_opy_):
        if self.meta.get(bstack111l11_opy_ (u"ࠨࡵࡷࡩࡵࡹࠧ⁌")):
            self.meta[bstack111l11_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨ⁍")].append(bstack1lllll1111ll_opy_)
        else:
            self.meta[bstack111l11_opy_ (u"ࠪࡷࡹ࡫ࡰࡴࠩ⁎")] = [ bstack1lllll1111ll_opy_ ]
    def bstack1lllll11llll_opy_(self):
        return {
            bstack111l11_opy_ (u"ࠫࡺࡻࡩࡥࠩ⁏"): self.bstack1111llll1l_opy_(),
            **self.bstack1lllll11l1l1_opy_(),
            **self.bstack1lllll11ll1l_opy_(),
            **self.bstack1lllll11l1ll_opy_()
        }
    def bstack1lllll1l111l_opy_(self):
        if not self.result:
            return {}
        data = {
            bstack111l11_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪ⁐"): self.bstack1l1111lll11_opy_,
            bstack111l11_opy_ (u"࠭ࡤࡶࡴࡤࡸ࡮ࡵ࡮ࡠ࡫ࡱࡣࡲࡹࠧ⁑"): self.duration,
            bstack111l11_opy_ (u"ࠧࡳࡧࡶࡹࡱࡺࠧ⁒"): self.result.result
        }
        if data[bstack111l11_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨ⁓")] == bstack111l11_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ⁔"):
            data[bstack111l11_opy_ (u"ࠪࡪࡦ࡯࡬ࡶࡴࡨࡣࡹࡿࡰࡦࠩ⁕")] = self.result.bstack1111111l1l_opy_()
            data[bstack111l11_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡷࡵࡩࠬ⁖")] = [{bstack111l11_opy_ (u"ࠬࡨࡡࡤ࡭ࡷࡶࡦࡩࡥࠨ⁗"): self.result.bstack11l1111l111_opy_()}]
        return data
    def bstack1lllll111l1l_opy_(self):
        return {
            bstack111l11_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ⁘"): self.bstack1111llll1l_opy_(),
            **self.bstack1lllll11l1l1_opy_(),
            **self.bstack1lllll11ll1l_opy_(),
            **self.bstack1lllll1l111l_opy_(),
            **self.bstack1lllll11l1ll_opy_()
        }
    def bstack1111ll1l1l_opy_(self, event, result=None):
        if result:
            self.result = result
        if bstack111l11_opy_ (u"ࠧࡔࡶࡤࡶࡹ࡫ࡤࠨ⁙") in event:
            return self.bstack1lllll11llll_opy_()
        elif bstack111l11_opy_ (u"ࠨࡈ࡬ࡲ࡮ࡹࡨࡦࡦࠪ⁚") in event:
            return self.bstack1lllll111l1l_opy_()
    def bstack111l11111l_opy_(self):
        pass
    def stop(self, time=None, duration=None, result=None):
        self.bstack1l1111lll11_opy_ = time if time else bstack11ll11lll_opy_()
        self.duration = duration if duration else bstack111ll11l1l1_opy_(self.started_at, self.bstack1l1111lll11_opy_)
        if result:
            self.result = result
class bstack111lll11l1_opy_(bstack111l11l1ll_opy_):
    def __init__(self, hooks=[], bstack111l1lll1l_opy_={}, *args, **kwargs):
        self.hooks = hooks
        self.bstack111l1lll1l_opy_ = bstack111l1lll1l_opy_
        super().__init__(*args, **kwargs, bstack1l1lll1ll_opy_=bstack111l11_opy_ (u"ࠩࡷࡩࡸࡺࠧ⁛"))
    @classmethod
    def bstack1lllll111l11_opy_(cls, scenario, feature, test, **kwargs):
        steps = []
        for step in scenario.steps:
            steps.append({
                bstack111l11_opy_ (u"ࠪ࡭ࡩ࠭⁜"): id(step),
                bstack111l11_opy_ (u"ࠫࡹ࡫ࡸࡵࠩ⁝"): step.name,
                bstack111l11_opy_ (u"ࠬࡱࡥࡺࡹࡲࡶࡩ࠭⁞"): step.keyword,
            })
        return bstack111lll11l1_opy_(
            **kwargs,
            meta={
                bstack111l11_opy_ (u"࠭ࡦࡦࡣࡷࡹࡷ࡫ࠧ "): {
                    bstack111l11_opy_ (u"ࠧ࡯ࡣࡰࡩࠬ⁠"): feature.name,
                    bstack111l11_opy_ (u"ࠨࡲࡤࡸ࡭࠭⁡"): feature.filename,
                    bstack111l11_opy_ (u"ࠩࡧࡩࡸࡩࡲࡪࡲࡷ࡭ࡴࡴࠧ⁢"): feature.description
                },
                bstack111l11_opy_ (u"ࠪࡷࡨ࡫࡮ࡢࡴ࡬ࡳࠬ⁣"): {
                    bstack111l11_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ⁤"): scenario.name
                },
                bstack111l11_opy_ (u"ࠬࡹࡴࡦࡲࡶࠫ⁥"): steps,
                bstack111l11_opy_ (u"࠭ࡥࡹࡣࡰࡴࡱ࡫ࡳࠨ⁦"): bstack1lllllllll1l_opy_(test)
            }
        )
    def bstack1lllll1l1111_opy_(self):
        return {
            bstack111l11_opy_ (u"ࠧࡩࡱࡲ࡯ࡸ࠭⁧"): self.hooks
        }
    def bstack1lllll11l111_opy_(self):
        if self.bstack111l1lll1l_opy_:
            return {
                bstack111l11_opy_ (u"ࠨ࡫ࡱࡸࡪ࡭ࡲࡢࡶ࡬ࡳࡳࡹࠧ⁨"): self.bstack111l1lll1l_opy_
            }
        return {}
    def bstack1lllll111l1l_opy_(self):
        return {
            **super().bstack1lllll111l1l_opy_(),
            **self.bstack1lllll1l1111_opy_()
        }
    def bstack1lllll11llll_opy_(self):
        return {
            **super().bstack1lllll11llll_opy_(),
            **self.bstack1lllll11l111_opy_()
        }
    def bstack111l11111l_opy_(self):
        return bstack111l11_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࠫ⁩")
class bstack111ll111l1_opy_(bstack111l11l1ll_opy_):
    def __init__(self, hook_type, *args,bstack111l1lll1l_opy_={}, **kwargs):
        self.hook_type = hook_type
        self.bstack1ll11ll1111_opy_ = None
        self.bstack111l1lll1l_opy_ = bstack111l1lll1l_opy_
        super().__init__(*args, **kwargs, bstack1l1lll1ll_opy_=bstack111l11_opy_ (u"ࠪ࡬ࡴࡵ࡫ࠨ⁪"))
    def bstack111l11l1l1_opy_(self):
        return self.hook_type
    def bstack1lllll11l11l_opy_(self):
        return {
            bstack111l11_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡷࡽࡵ࡫ࠧ⁫"): self.hook_type
        }
    def bstack1lllll111l1l_opy_(self):
        return {
            **super().bstack1lllll111l1l_opy_(),
            **self.bstack1lllll11l11l_opy_()
        }
    def bstack1lllll11llll_opy_(self):
        return {
            **super().bstack1lllll11llll_opy_(),
            bstack111l11_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡪࡦࠪ⁬"): self.bstack1ll11ll1111_opy_,
            **self.bstack1lllll11l11l_opy_()
        }
    def bstack111l11111l_opy_(self):
        return bstack111l11_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡷࡻ࡮ࠨ⁭")
    def bstack111ll1111l_opy_(self, bstack1ll11ll1111_opy_):
        self.bstack1ll11ll1111_opy_ = bstack1ll11ll1111_opy_