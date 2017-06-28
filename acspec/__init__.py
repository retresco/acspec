import os

from acspec.base import Acspec  # noqa
from acspec.yspec import Yspec  # noqa

__version__ = "0.1.2"

package_root = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '..'
)
