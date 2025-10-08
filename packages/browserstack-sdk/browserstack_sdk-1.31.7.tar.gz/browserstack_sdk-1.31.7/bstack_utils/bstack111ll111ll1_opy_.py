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
from _pytest import fixtures
from _pytest.python import _call_with_optional_argument
from pytest import Module, Class
from bstack_utils.helper import Result, bstack111lllll1ll_opy_
from browserstack_sdk.bstack1l1ll1l11l_opy_ import bstack1ll1111l_opy_
def _111ll11l111_opy_(method, this, arg):
    arg_count = method.__code__.co_argcount
    if arg_count > 1:
        method(this, arg)
    else:
        method(this)
class bstack111ll11111l_opy_:
    def __init__(self, handler):
        self._111l1llll11_opy_ = {}
        self._111ll111l11_opy_ = {}
        self.handler = handler
        self.patch()
        pass
    def patch(self):
        pytest_version = bstack1ll1111l_opy_.version()
        if bstack111lllll1ll_opy_(pytest_version, bstack111l11_opy_ (u"ࠦ࠽࠴࠱࠯࠳ࠥᶌ")) >= 0:
            self._111l1llll11_opy_[bstack111l11_opy_ (u"ࠬ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨᶍ")] = Module._register_setup_function_fixture
            self._111l1llll11_opy_[bstack111l11_opy_ (u"࠭࡭ࡰࡦࡸࡰࡪࡥࡦࡪࡺࡷࡹࡷ࡫ࠧᶎ")] = Module._register_setup_module_fixture
            self._111l1llll11_opy_[bstack111l11_opy_ (u"ࠧࡤ࡮ࡤࡷࡸࡥࡦࡪࡺࡷࡹࡷ࡫ࠧᶏ")] = Class._register_setup_class_fixture
            self._111l1llll11_opy_[bstack111l11_opy_ (u"ࠨ࡯ࡨࡸ࡭ࡵࡤࡠࡨ࡬ࡼࡹࡻࡲࡦࠩᶐ")] = Class._register_setup_method_fixture
            Module._register_setup_function_fixture = self.bstack111ll111l1l_opy_(bstack111l11_opy_ (u"ࠩࡩࡹࡳࡩࡴࡪࡱࡱࡣ࡫࡯ࡸࡵࡷࡵࡩࠬᶑ"))
            Module._register_setup_module_fixture = self.bstack111ll111l1l_opy_(bstack111l11_opy_ (u"ࠪࡱࡴࡪࡵ࡭ࡧࡢࡪ࡮ࡾࡴࡶࡴࡨࠫᶒ"))
            Class._register_setup_class_fixture = self.bstack111ll111l1l_opy_(bstack111l11_opy_ (u"ࠫࡨࡲࡡࡴࡵࡢࡪ࡮ࡾࡴࡶࡴࡨࠫᶓ"))
            Class._register_setup_method_fixture = self.bstack111ll111l1l_opy_(bstack111l11_opy_ (u"ࠬࡳࡥࡵࡪࡲࡨࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭ᶔ"))
        else:
            self._111l1llll11_opy_[bstack111l11_opy_ (u"࠭ࡦࡶࡰࡦࡸ࡮ࡵ࡮ࡠࡨ࡬ࡼࡹࡻࡲࡦࠩᶕ")] = Module._inject_setup_function_fixture
            self._111l1llll11_opy_[bstack111l11_opy_ (u"ࠧ࡮ࡱࡧࡹࡱ࡫࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨᶖ")] = Module._inject_setup_module_fixture
            self._111l1llll11_opy_[bstack111l11_opy_ (u"ࠨࡥ࡯ࡥࡸࡹ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨᶗ")] = Class._inject_setup_class_fixture
            self._111l1llll11_opy_[bstack111l11_opy_ (u"ࠩࡰࡩࡹ࡮࡯ࡥࡡࡩ࡭ࡽࡺࡵࡳࡧࠪᶘ")] = Class._inject_setup_method_fixture
            Module._inject_setup_function_fixture = self.bstack111ll111l1l_opy_(bstack111l11_opy_ (u"ࠪࡪࡺࡴࡣࡵ࡫ࡲࡲࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭ᶙ"))
            Module._inject_setup_module_fixture = self.bstack111ll111l1l_opy_(bstack111l11_opy_ (u"ࠫࡲࡵࡤࡶ࡮ࡨࡣ࡫࡯ࡸࡵࡷࡵࡩࠬᶚ"))
            Class._inject_setup_class_fixture = self.bstack111ll111l1l_opy_(bstack111l11_opy_ (u"ࠬࡩ࡬ࡢࡵࡶࡣ࡫࡯ࡸࡵࡷࡵࡩࠬᶛ"))
            Class._inject_setup_method_fixture = self.bstack111ll111l1l_opy_(bstack111l11_opy_ (u"࠭࡭ࡦࡶ࡫ࡳࡩࡥࡦࡪࡺࡷࡹࡷ࡫ࠧᶜ"))
    def bstack111l1lll11l_opy_(self, bstack111l1llllll_opy_, hook_type):
        bstack111l1lll1l1_opy_ = id(bstack111l1llllll_opy_.__class__)
        if (bstack111l1lll1l1_opy_, hook_type) in self._111ll111l11_opy_:
            return
        meth = getattr(bstack111l1llllll_opy_, hook_type, None)
        if meth is not None and fixtures.getfixturemarker(meth) is None:
            self._111ll111l11_opy_[(bstack111l1lll1l1_opy_, hook_type)] = meth
            setattr(bstack111l1llllll_opy_, hook_type, self.bstack111ll1111l1_opy_(hook_type, bstack111l1lll1l1_opy_))
    def bstack111ll111111_opy_(self, instance, bstack111ll111lll_opy_):
        if bstack111ll111lll_opy_ == bstack111l11_opy_ (u"ࠢࡧࡷࡱࡧࡹ࡯࡯࡯ࡡࡩ࡭ࡽࡺࡵࡳࡧࠥᶝ"):
            self.bstack111l1lll11l_opy_(instance.obj, bstack111l11_opy_ (u"ࠣࡵࡨࡸࡺࡶ࡟ࡧࡷࡱࡧࡹ࡯࡯࡯ࠤᶞ"))
            self.bstack111l1lll11l_opy_(instance.obj, bstack111l11_opy_ (u"ࠤࡷࡩࡦࡸࡤࡰࡹࡱࡣ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࠨᶟ"))
        if bstack111ll111lll_opy_ == bstack111l11_opy_ (u"ࠥࡱࡴࡪࡵ࡭ࡧࡢࡪ࡮ࡾࡴࡶࡴࡨࠦᶠ"):
            self.bstack111l1lll11l_opy_(instance.obj, bstack111l11_opy_ (u"ࠦࡸ࡫ࡴࡶࡲࡢࡱࡴࡪࡵ࡭ࡧࠥᶡ"))
            self.bstack111l1lll11l_opy_(instance.obj, bstack111l11_opy_ (u"ࠧࡺࡥࡢࡴࡧࡳࡼࡴ࡟࡮ࡱࡧࡹࡱ࡫ࠢᶢ"))
        if bstack111ll111lll_opy_ == bstack111l11_opy_ (u"ࠨࡣ࡭ࡣࡶࡷࡤ࡬ࡩࡹࡶࡸࡶࡪࠨᶣ"):
            self.bstack111l1lll11l_opy_(instance.obj, bstack111l11_opy_ (u"ࠢࡴࡧࡷࡹࡵࡥࡣ࡭ࡣࡶࡷࠧᶤ"))
            self.bstack111l1lll11l_opy_(instance.obj, bstack111l11_opy_ (u"ࠣࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡧࡱࡧࡳࡴࠤᶥ"))
        if bstack111ll111lll_opy_ == bstack111l11_opy_ (u"ࠤࡰࡩࡹ࡮࡯ࡥࡡࡩ࡭ࡽࡺࡵࡳࡧࠥᶦ"):
            self.bstack111l1lll11l_opy_(instance.obj, bstack111l11_opy_ (u"ࠥࡷࡪࡺࡵࡱࡡࡰࡩࡹ࡮࡯ࡥࠤᶧ"))
            self.bstack111l1lll11l_opy_(instance.obj, bstack111l11_opy_ (u"ࠦࡹ࡫ࡡࡳࡦࡲࡻࡳࡥ࡭ࡦࡶ࡫ࡳࡩࠨᶨ"))
    @staticmethod
    def bstack111ll1111ll_opy_(hook_type, func, args):
        if hook_type in [bstack111l11_opy_ (u"ࠬࡹࡥࡵࡷࡳࡣࡲ࡫ࡴࡩࡱࡧࠫᶩ"), bstack111l11_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮ࡠ࡯ࡨࡸ࡭ࡵࡤࠨᶪ")]:
            _111ll11l111_opy_(func, args[0], args[1])
            return
        _call_with_optional_argument(func, args[0])
    def bstack111ll1111l1_opy_(self, hook_type, bstack111l1lll1l1_opy_):
        def bstack111l1lll1ll_opy_(arg=None):
            self.handler(hook_type, bstack111l11_opy_ (u"ࠧࡣࡧࡩࡳࡷ࡫ࠧᶫ"))
            result = None
            try:
                bstack1llllll1lll_opy_ = self._111ll111l11_opy_[(bstack111l1lll1l1_opy_, hook_type)]
                self.bstack111ll1111ll_opy_(hook_type, bstack1llllll1lll_opy_, (arg,))
                result = Result(result=bstack111l11_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨᶬ"))
            except Exception as e:
                result = Result(result=bstack111l11_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩᶭ"), exception=e)
                self.handler(hook_type, bstack111l11_opy_ (u"ࠪࡥ࡫ࡺࡥࡳࠩᶮ"), result)
                raise e.with_traceback(e.__traceback__)
            self.handler(hook_type, bstack111l11_opy_ (u"ࠫࡦ࡬ࡴࡦࡴࠪᶯ"), result)
        def bstack111l1llll1l_opy_(this, arg=None):
            self.handler(hook_type, bstack111l11_opy_ (u"ࠬࡨࡥࡧࡱࡵࡩࠬᶰ"))
            result = None
            exception = None
            try:
                self.bstack111ll1111ll_opy_(hook_type, self._111ll111l11_opy_[hook_type], (this, arg))
                result = Result(result=bstack111l11_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭ᶱ"))
            except Exception as e:
                result = Result(result=bstack111l11_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧᶲ"), exception=e)
                self.handler(hook_type, bstack111l11_opy_ (u"ࠨࡣࡩࡸࡪࡸࠧᶳ"), result)
                raise e.with_traceback(e.__traceback__)
            self.handler(hook_type, bstack111l11_opy_ (u"ࠩࡤࡪࡹ࡫ࡲࠨᶴ"), result)
        if hook_type in [bstack111l11_opy_ (u"ࠪࡷࡪࡺࡵࡱࡡࡰࡩࡹ࡮࡯ࡥࠩᶵ"), bstack111l11_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳࡥ࡭ࡦࡶ࡫ࡳࡩ࠭ᶶ")]:
            return bstack111l1llll1l_opy_
        return bstack111l1lll1ll_opy_
    def bstack111ll111l1l_opy_(self, bstack111ll111lll_opy_):
        def bstack111l1lllll1_opy_(this, *args, **kwargs):
            self.bstack111ll111111_opy_(this, bstack111ll111lll_opy_)
            self._111l1llll11_opy_[bstack111ll111lll_opy_](this, *args, **kwargs)
        return bstack111l1lllll1_opy_