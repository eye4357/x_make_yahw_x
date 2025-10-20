"""x_make_yahw_x package wrapper."""

from importlib import import_module

_module = import_module(".x_cls_make_yahw_x", __name__)

XClsMakeYahwX = _module.XClsMakeYahwX
main = _module.main
main_json = _module.main_json
x_cls_make_yahw_x = _module

__all__ = ["XClsMakeYahwX", "main", "main_json", "x_cls_make_yahw_x"]
