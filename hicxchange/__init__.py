from __future__ import absolute_import
from .hic2cool_utils import (
    hic2cool_convert,
    hic2cool_update,
    hic2cool_extractnorms,
    cool2hic_convert,
    print_stderr as hic2cool_print_stderr,
    force_exit as hic2cool_force_exit
)
from ._version import __version__
# The submodules hic2cool 1.0.1 exposes on the package.
from . import hic2cool_config, hic2cool_updates, hic2cool_utils  # noqa: F401
