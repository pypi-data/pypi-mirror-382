import argparse
from dataclasses import dataclass
from typing import Union, List, Sequence, TypeAlias

T: TypeAlias = type[str] | type[bool] | type[int] | type[float]


@dataclass(frozen=True)
class InParam:
    param_value: bool | str | int | float
    param_name: str


def boolean_string(s: str) -> bool:
    return s.lower() in {"true", "yes", "y"}


class InParamFactory:

    @staticmethod
    def from_cli(
        name: str,
        required: bool,
        param_type: T,
        n: int = 1,
        argv: Sequence[str] | None = None,
    ) -> Union[List["InParam"], "InParam"]:
        if param_type is bool:
            param_type = boolean_string
        parser = argparse.ArgumentParser(add_help=False)
        if n != 1:
            objs = []
            for i in range(1, n + 1):
                parser.add_argument(
                    f"--{name}-{i}",
                    dest=f"{name}_{i}",
                    required=required,
                    type=param_type,
                )
            # if None, argparse will read from the sys.argv[1:]
            # this is good so that it can be passed for testing
            args, _ = parser.parse_known_args(argv)
            for i in range(1, n + 1):
                objs.append(
                    InParam(
                        param_name=f"{name}_{i}",
                        param_value=getattr(args, f"{name}_{i}"),
                    )
                )
            return objs
        else:
            parser.add_argument(
                f"--{name}", dest=f"{name}", required=required, type=param_type
            )
            args, _ = parser.parse_known_args(argv)
            return InParam(param_name=f"{name}", param_value=getattr(args, f"{name}"))
