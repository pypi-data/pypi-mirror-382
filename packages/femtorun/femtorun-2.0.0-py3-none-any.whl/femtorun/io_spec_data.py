from typing import *

OPTIONAL_KEYS = [
    "comments",
    "quantization",
    "mailbox_id",
    "length_64b_words",
    "core_id",
    "pc",
]


class IOSpecQuant(TypedDict):
    scale: float
    zero_pt: float


class IOSpecInout(TypedDict):
    type: Literal["input", "output"]
    varname: str
    length: int
    precision: int
    padded_length: Optional[int]
    quantization: IOSpecQuant
    length_64b_words: Optional[int]
    mailbox_id: Optional[int]
    core_id: Optional[int]
    pc: Optional[int]
    comments: Dict[str, str]


class IOSpecSimpleSequence(TypedDict):
    type: Literal["simple_sequence"]
    outputs: List[str]
    inputs: List[str]
    comments: Dict[str, str]


class IOSpecComplexSequence(TypedDict):
    type: Literal["complex_sequence"]
    outputs: Dict[str, int]
    inputs: Dict[str, int]
    comments: Dict[str, str]


IOSpecData = Dict[
    str, Dict[str, Union[IOSpecInout, IOSpecSimpleSequence, IOSpecComplexSequence]]
]


def _check_TypedDict(D, TypedDictCls):
    # check if needed keys present
    # doesn't check if there are extra keys
    for k, objtype in TypedDictCls.__annotations__.items():
        if k not in OPTIONAL_KEYS:
            if k not in D:
                raise ValueError(f"{TypedDictCls.__name__} requires key {k}")
            if objtype in [str, int, float]:
                if not isinstance(D[k], objtype):
                    raise ValueError(
                        f"{TypedDictCls.__name__} requires key {k} to be of type {objtype}, saw {type(D[k])}"
                    )
            elif objtype == List[str]:
                ok = [isinstance(el, str) for el in D[k]]
                if not all(ok):
                    raise ValueError(
                        f"{TypedDictCls.__name__} requires key {k} to be list of str, saw something else"
                    )
            elif objtype == Dict[str, str]:
                ok = [
                    isinstance(k, int) and isinstance(v, int) for k, v in D[k].items()
                ]
                if not all(ok):
                    raise ValueError(
                        f"{TypedDictCls.__name__} requires key {k} to be Dict[str:int], saw something else"
                    )
            elif objtype == IOSpecQuant:
                _check_TypedDict(D[k], IOSpecQuant)


def check_IOSpecData(data: IOSpecData):
    """checks that all keys are present
    no comprehensive type checking yet
    """
    base_types = ["inputs", "outputs", "simple_sequences", "complex_sequences"]

    for k in data:
        if k not in ["inputs", "outputs", "simple_sequences", "complex_sequences"]:
            raise ValueError(f"undefined IOSpec section header {k}")

    if "inputs" in data:
        for objname, obj in data["inputs"].items():
            _check_TypedDict(obj, IOSpecInout)

    if "outputs" in data:
        for objname, obj in data["outputs"].items():
            _check_TypedDict(obj, IOSpecInout)

    if "simple_sequences" in data:
        for objname, obj in data["simple_sequences"].items():
            _check_TypedDict(obj, IOSpecSimpleSequence)

    if "complex_sequences" in data:
        for objname, obj in data["complex_sequences"].items():
            _check_TypedDict(obj, IOSpecComplexSequence)
