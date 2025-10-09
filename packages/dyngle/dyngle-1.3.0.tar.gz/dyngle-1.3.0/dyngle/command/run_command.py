import shlex
import subprocess
from wizlib.parser import WizParser
from yaml import safe_load

from dyngle.command import DyngleCommand
from dyngle.model.expression import expression
from dyngle.model.template import Template
from dyngle.error import DyngleError


class RunCommand(DyngleCommand):
    """Run a workflow defined in the configuration"""

    name = 'run'

    @classmethod
    def add_args(cls, parser: WizParser):
        super().add_args(parser)
        parser.add_argument('operation', help='Operation name to run')
        parser.add_argument(
            'args', nargs='*', help='Optional operation arguments')

    def handle_vals(self):
        super().handle_vals()

    def _validate_operation_exists(self, operations):
        """Validate that the requested operation exists in configuration"""
        if self.operation not in operations:
            available_operations = ', '.join(operations.keys())
            raise DyngleError(
                f"Operation '{self.operation}' not found. " +
                f"Available operations: {available_operations}")

    @DyngleCommand.wrap
    def execute(self):
        data_string = self.app.stream.text
        data = safe_load(data_string) or {}
        data['args'] = self.args

        operations = self.app.operations
        self._validate_operation_exists(operations)
        operation = operations[self.operation]

        operation.run(data, self.app.globals)

        return f'Operation "{self.operation}" completed successfully'
