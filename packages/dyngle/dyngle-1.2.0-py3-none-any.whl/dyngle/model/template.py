from dataclasses import dataclass
from functools import partial
import re

from dyngle.error import DyngleError
from dyngle.model.live_data import LiveData


PATTERN = re.compile(r'\{\{\s*([^}]+)\s*\}\}')


@dataclass
class Template:

    template: str

    def render(self, live_data: LiveData | dict | None = None) -> str:
        """Render the template with the provided LiveData (raw data and
        expressions)."""

        live_data = LiveData(live_data)
        resolver = partial(self._resolve, live_data=live_data)
        return PATTERN.sub(resolver, self.template)

    def _resolve(self, match, *, live_data: LiveData):
        """Resolve a single name/path from the template. The argument is a
        merge of the raw data and the expressions, either of which are valid
        substitutions."""
        key = match.group(1).strip()
        return live_data.resolve(key)
