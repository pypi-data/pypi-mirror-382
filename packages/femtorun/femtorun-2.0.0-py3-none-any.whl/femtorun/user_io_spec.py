from typing import Optional
from .io_spec_data import IOSpecInout, IOSpecQuant, IOSpecSimpleSequence, IOSpecData
from .io_spec import IOSpec
import yaml
from collections import defaultdict


class UserIOSpec:
    """User-facing IOSpec Object. Implements an interface to construct IOSpec for simple sequences."""

    def __init__(self):
        self.inputs: dict[str, IOSpecInout] = {}
        self.outputs: dict[str, IOSpecInout] = {}
        self.signatures: list[IOSpecSimpleSequence] = []

    @classmethod
    def from_data(cls, data: IOSpecData):
        iospec = cls()

        def _copy_section(key, target):
            if section in data:
                for key, entry in data[section].items():
                    target[key] = entry

        _copy_section("inputs", iospec.inputs)
        _copy_section("outputs", iospec.outputs)
        _copy_section("simple_sequences", iospec.simple_sequences)

        if "complex_sequences" in data:
            raise NotImplementedError(
                "complex_sequence not yet supported by UserIOSpec"
            )

        return iospec

    def add_input(
        self,
        varname: str,
        length: int,
        precision: int,
        quant_scale: Optional[float] = None,
        quant_zp: Optional[int] = None,
        comments: Optional[dict[str, str]] = None,
        padded_length: Optional[int] = None,
    ):
        if varname in self.inputs:
            raise ValueError(f"input with name {varname} already exists")

        if comments is None:
            comments = {}

        self.inputs[varname] = IOSpecInout(
            type="input",
            varname=varname,
            length=length,
            precision=precision,
            padded_length=padded_length,
            quantization=IOSpecQuant(scale=quant_scale, zero_pt=quant_zp),
            comments=comments,
        )

    def set_padded_length(self, name: str, padded_length: int):
        if name in self.inputs:
            self.inputs[name]["padded_length"] = padded_length
        elif name in self.outputs:
            self.outputs[name]["padded_length"] = padded_length
        else:
            raise KeyError(f"name: {name} not in inputs or outputs")

    def add_output(
        self,
        varname: str,
        length: int,
        precision: int,
        quant_scale: Optional[float] = None,
        quant_zp: Optional[int] = None,
        comments: Optional[dict[str, str]] = None,
        padded_length: Optional[int] = None,
    ):
        if varname in self.outputs:
            raise ValueError(f"output with name {varname} already exists")

        if comments is None:
            comments = {}

        self.outputs[varname] = IOSpecInout(
            type="output",
            varname=varname,
            length=length,
            precision=precision,
            padded_length=padded_length,
            quantization=IOSpecQuant(scale=quant_scale, zero_pt=quant_zp),
            comments=comments,
        )

    def add_signature(
        self,
        inputs: list[str],
        latched_inputs: list[str],
        outputs: list[str],
        comments: Optional[dict[str, str]] = None,
    ):
        if comments is None:
            comments = {}

        for x in inputs:
            if x not in self.inputs:
                raise ValueError(f"input {x} has not been added")

        for x in latched_inputs:
            if x not in self.inputs:
                raise ValueError(f"latched-input {x} has not been added")

        for x in outputs:
            if x not in self.outputs:
                raise ValueError(f"output {x} has not been added")

        self.signatures.append(
            IOSpecSimpleSequence(
                type="simple_sequence",
                inputs=inputs,
                outputs=outputs,
                comments=comments,
            )
        )

        for x in latched_inputs:
            self.signatures.append(
                IOSpecSimpleSequence(
                    type="simple_sequence", inputs=[x], outputs=[], comments=comments
                )
            )

    def latched_input_names(self) -> list[str]:
        names = set(list(self.inputs.keys()))
        for sig in self.signatures:
            if len(sig["outputs"]) > 0:
                for x in sig["inputs"]:
                    if x in names:
                        names.remove(x)

        return list(names)

    def data(self) -> IOSpecData:
        """Converts UserIOSpec into a data dictionary"""
        data: IOSpecData = defaultdict(dict)
        for name, spec in self.inputs.items():
            data["inputs"][name] = spec
        for name, spec in self.outputs.items():
            data["outputs"][name] = spec
        for i, sig in enumerate(self.signatures):
            data["simple_sequences"][i] = sig

        return dict(data)  # yaml pkg expects a plain dict

    def verify(self):
        """Verifies that the UserIOSpec is correctly constructed"""
        # IOSpec constructor verifies upon construction
        IOSpec(self.data())

    def save(self, file_name: str):
        data = self.data()
        with open(file_name, "w") as f:
            yaml.dump(data, f, sort_keys=False)
