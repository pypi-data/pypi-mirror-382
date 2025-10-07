from dataclasses import dataclass
from functools import cached_property
import re
import shlex
import subprocess

from dyngle.error import DyngleError
from dyngle.model.live_data import LiveData
from dyngle.model.template import Template


@dataclass
class Operation:

    # Expressions and values defined within the operation
    locals: dict

    steps: list

    def run(self, data: dict, globals: dict):
        live_data = LiveData(globals) | self.locals | data
        for markup in self.steps:
            step = Step(markup)
            step.run(live_data)


STEP_PATTERN = re.compile(
    r'^\s*(?:([\w.-]+)\s+->\s+)?(.+?)(?:\s+=>\s+([\w.-]+))?\s*$')


def parse_step(markup):
    if match := STEP_PATTERN.match(markup):
        input, command_text, output = match.groups()
        command_template = shlex.split(command_text.strip())
        return input, command_template, output
    else:
        raise DyngleError(f"Invalid step markup {{markup}}")


@dataclass
class Step:

    markup: str

    def __post_init__(self):
        self.input, self.command_template, self.output = \
            parse_step(self.markup)

    def run(self, live_data: LiveData):
        command = [Template(word).render(live_data).strip()
                   for word in self.command_template]
        pipes = {}
        if self.input:
            pipes["input"] = live_data.resolve(self.input)
        if self.output:
            pipes['stdout'] = subprocess.PIPE
        result = subprocess.run(command, text=True, **pipes)
        if result.returncode != 0:
            raise DyngleError(
                f'Step failed with code {result.returncode}: {self.markup}')
        if self.output:
            live_data[self.output] = result.stdout.rstrip()
