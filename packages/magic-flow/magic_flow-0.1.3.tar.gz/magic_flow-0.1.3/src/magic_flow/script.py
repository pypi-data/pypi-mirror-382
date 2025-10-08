from __future__ import annotations
import logging

from magic_flow.cadence.types import Value
from magic_flow.exceptions import NotCadenceValueError

log = logging.getLogger(__name__)


class Script(object):
    """The Script object used for sending scripts to the Flow blockchain

    This is mainly just a wrapper around a script code and the code arguments.

    Attributes
    ----------
    code : str
        The code of the script.

    arguments : list[Value]
        arguments will be passed to the script when it is being executed. The order of the arguments is important.
        Arguments are verified to be cadence.Value(s).
    """

    def __init__(self, *, code: str, arguments: list[Value] = None) -> None:
        super().__init__()
        self.code: str = code
        self.arguments: list[Value] = []
        if arguments:
            self.add_arguments(*arguments)

    def add_arguments(self, *args: Value) -> Script:
        """Add arguments to the script.

        Parameters
        ----------
        args
            The arguments to add to the script.

        Returns
        -------
            Returns the script object itself. This is used for chaining.
        """
        for arg in args:
            if not isinstance(arg, Value):
                raise NotCadenceValueError.from_value(arg)
        self.arguments.extend(args)
        return self
