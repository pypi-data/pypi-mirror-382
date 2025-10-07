from functools import cached_property
from pathlib import Path
from wizlib.app import WizApp
from wizlib.stream_handler import StreamHandler
from wizlib.config_handler import ConfigHandler
from wizlib.ui_handler import UIHandler

from dyngle.command import DyngleCommand
from dyngle.error import DyngleError
from dyngle.model.expression import expression
from dyngle.model.operation import Operation
from dyngle.model.template import Template


class DyngleApp(WizApp):

    base = DyngleCommand
    name = 'dyngle'
    handlers = [StreamHandler, ConfigHandler, UIHandler]

    # For possible upstreaming to WizLib, a mechanism to "import" configuration
    # settings from external files.

    @property
    def _imported_configrations(self):
        if not hasattr(self, '__imported_configurations'):
            imports = self.config.get('dyngle-imports')
            confs = []
            if imports:
                for filename in imports:
                    full_filename = Path(filename).expanduser()
                    confs.append(ConfigHandler(full_filename))
            self.__imported_configurations = confs
        return self.__imported_configurations

    def _get_configuration_details(self, type: str):
        label = f'dyngle-{type}'
        details = {}
        for conf in self._imported_configrations:
            if (imported_details := conf.get(label)):
                details |= imported_details
        configured_details = self.config.get(label)
        if configured_details:
            details |= configured_details
        return details

    @cached_property
    def operations(self):
        operations_configs = self._get_configuration_details('operations')
        if not operations_configs:
            raise DyngleError("No operations defined in configuration")
        operations = {}
        for key, config in operations_configs.items():
            if isinstance(config, list):
                operation = Operation({}, config)
            elif isinstance(config, dict):
                expr_texts = config.get('expressions') or {}
                expressions = _expressions_from_texts(expr_texts)
                values = config.get('values') or {}
                steps = config.get('steps') or []
                operation = Operation(expressions | values, steps)
            else:
                raise DyngleError(f"Invalid operation configuration for {key}")
            operations[key] = operation
        return operations

    @cached_property
    def globals(self):
        expr_texts = self._get_configuration_details('expressions')
        expressions = _expressions_from_texts(expr_texts)
        values = self._get_configuration_details('values')
        return expressions | (values if values else {})


def _expressions_from_texts(expr_texts):
    if expr_texts:
        return {k: expression(t) for k, t in expr_texts.items()}
    else:
        return {}
