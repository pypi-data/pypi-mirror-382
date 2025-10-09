__all__ = ["isr", "tag", "revalidate_by_tags"]
__version__ = "0.0.1"

from .decorators import isr  # noqa: F401
from .tags import tag  # noqa: F401
from .revalidate.tasks import revalidate_by_tags  # noqa: F401
