import yaml
import networkx as nx
from typing import Optional
from femtorun.io_spec_data import check_IOSpecData, IOSpecData
from femtorun.io_spec_data import IOSpecInout, IOSpecQuant, IOSpecSimpleSequence


class IOSpec:
    def __init__(self, fname_or_data: None | str | IOSpecData = None):
        """IOSpec adds utility methods around the IO spec file contents,
        and has methods to allow an IO spec to be written programatically

        args:
            fname_or_data:
                either the filename of the yaml to initialize from,
                or an already-constructed data dict
        """

        if fname_or_data is None:
            self.data = {}
        elif isinstance(fname_or_data, str):
            self.data: dict = yaml.safe_load(open(fname_or_data, "r"))
        else:
            self.data = fname_or_data

        self.check()

        # "simple" specs are 1:1 inputs:outputs
        # used by legacy femtorunner APIs
        # whether or not the spec only has a single simple_sequence
        self.is_simple: bool = False
        self.simple_action: Optional[
            str
        ] = None  # name of the graph node that represents the simple action
        self.simple_inputs: Optional[list[str]] = None
        self.simple_outputs: Optional[list[str]] = None

        # as long as variables can have un-yaml'able names,
        # we need a varname field and need these
        self.node_to_var: dict[str, str] = {}
        self.var_to_node: dict[str, str] = {}

        # dataflow graph, shows dependencies encoded by sequences
        self.G: nx.DiGraph = nx.DiGraph()
        self._init_graph()

    ###############################
    # misc utilities

    def _set_if_simple(self):
        """if the spec only contains a single simple_sequence,
        (or something equivalent to it) it is "simple",
        and can be processed using the legacy FR APIs"""
        self.is_simple = True
        self.simple_action = None

        # fail if any complex sequences with more than frequency 1
        for objname, obj in self.complex_sequences.items():
            for io, val in obj["inputs"].items():
                if val > 1:
                    self.is_simple = False
                    return
            for io, val in obj["outputs"].items():
                if val > 1:
                    self.is_simple = False
                    return

        # fail if there's more than one sequence
        # ignore sequences with no outputs
        # these are likely parameter-setting
        seq_ct = 0
        for objname, obj in (self.simple_sequences | self.complex_sequences).items():
            if len(obj["outputs"]) > 0:
                seq_ct += 1

        if seq_ct != 1:
            self.is_simple = False
            return

        # fell through, we made it
        # find what should be the only sequence, record that action name
        # can use this later to figure out the "relevant" inputs for step
        for objname, obj in (self.simple_sequences | self.complex_sequences).items():
            self.simple_action = objname
            # collect dict keys or just copy the list
            self.simple_inputs = list(obj["inputs"])
            self.simple_outputs = list(obj["outputs"])

    def _get_io_padding(self, io_type) -> dict[str, tuple[int, int]]:
        pad_dict = {}
        if io_type in self.data:
            for objname, obj in self.data[io_type].items():
                pad_dict[obj["varname"]] = ((obj["length"],), (obj["padded_length"],))
        return pad_dict

    @property
    def input_padding(self):
        return self._get_io_padding("inputs")

    @property
    def output_padding(self):
        return self._get_io_padding("outputs")

    def check(self):
        """check that the types in the dictionary are correct
        self.data is fundamentally a TypedDict
        see io_spec_data.py
        """
        check_IOSpecData(self.data)

    def _level_one_data(self, key):
        # make this behave like a defaultdict
        # may initialize some empty dicts for unused keys
        #  e.g. a model that has no complex_sequences will still have the header
        # that is probably OK
        if key not in self.data:
            self.data[key] = {}
        return self.data[key]

    @property
    def inputs(self):
        return self._level_one_data("inputs")

    @property
    def outputs(self):
        return self._level_one_data("outputs")

    @property
    def simple_sequences(self):
        return self._level_one_data("simple_sequences")

    @property
    def complex_sequences(self):
        return self._level_one_data("complex_sequences")

    ###############################
    # sequence "runtime" stuff
    # protocol checking--run in parallel with other FemtoRunners,
    # make sure that sequences are being respected

    def _init_graph(self) -> nx.DiGraph:
        """processes the IO graph into a networkx digraph,
        checks dagness, can be used to make plots"""
        self._set_if_simple()
        self._make_G()
        self._verify_dag()

    def _make_G(self):
        """process the yaml's Sequences into a Graph"""

        # nodes first
        for objname, obj in (self.inputs | self.outputs).items():
            varname = obj["varname"]
            assert objname not in self.node_to_var
            assert varname not in self.var_to_node
            self.node_to_var[objname] = varname
            self.var_to_node[varname] = objname
            self.G.add_node(objname, attr=obj)

        # then sequences, which are like edges
        for objname, obj in self.simple_sequences.items():
            action = objname
            self.G.add_node(action)  # no attributes

            for o in obj["outputs"]:
                self.G.add_edge(action, o, frequency=1)
            for i in obj["inputs"]:
                self.G.add_edge(i, action, frequency=1)

        for objname, obj in self.complex_sequences.items():
            action = objname
            self.G.add_node(action)  # no attributes

            for o, ct in obj["outputs"].items():
                self.G.add_edge(action, o, frequency=ct)
            for i, ct in obj["inputs"].items():
                self.G.add_edge(i, action, frequency=ct)

    def _verify_dag(self):
        """make sure the graph is DAG"""
        # verify DAG-ness
        if not nx.is_directed_acyclic_graph(self.G):
            raise ValueError("IO spec does not contain a graph without cycles")
        # can dump graph plot

    def _recurse_node(self, node: str):
        # increment outgoing edge scores by 1, see if each child is satisfied
        # recurse if this is the case
        # also check that we don't see count > freq
        # this isn't the most efficient solution,
        #  but it's simple, and these graphs are very small
        for succ in self.G.successors(node):
            # increment count on edge towards each child
            edge = (node, succ)
            self.G.edges[edge]["count"] += 1

            # look back towards all that child's parents
            # see if it's fully satisfied (freq == count)
            satisfied = True
            for pred in self.G.predecessors(succ):
                edge = (pred, succ)
                if self.G.edges[edge]["count"] > self.G.edges[edge]["frequency"]:
                    raise RuntimeError(
                        "Bad input sequence, provided too many inputs before receiving outputs"
                    )
                if self.G.edges[edge]["count"] < self.G.edges[edge]["frequency"]:
                    satisfied = False

            if satisfied:
                # recurse
                self._recurse_node(succ)

                # reset, but not if output
                # outputs are cleared with sim_recv_outputs
                if succ not in self.outputs:
                    for pred in self.G.predecessors(succ):
                        edge = (pred, succ)
                        self.G.edges[edge]["count"] = 0

    # sim_* calls comprise a degenerate Femtorunner
    # doesn't do any math, but knows what outputs follow
    # from which inputs

    def sim_reset(self):
        """reset execution model state
        sets the count attribute on each edge to 0
        """
        for edge in self.G.edges():
            self.G.edges[edge]["count"] = 0

    def sim_send_inputs(self, inputs: list[str]):
        """figure out which actions/outputs are triggered when these inputs are sent"""
        for inp in inputs:
            obj = self.var_to_node[inp]
            assert obj in self.G.nodes()  # must be a named node
            assert self.G.in_degree(obj) == 0  # must be an input node
            self._recurse_node(obj)

    def sim_recv_outputs(self) -> list[str]:
        """clear triggered outputs"""
        outputs = []

        for node in self.G.nodes():
            if node in self.outputs:
                # this is an output
                # there should be only one pred
                assert self.G.out_degree(node) == 0
                assert self.G.in_degree(node) == 1
                pred = next(iter(self.G.predecessors(node)))
                edge = (pred, node)
                if self.G.edges[edge]["count"] == self.G.edges[edge]["frequency"]:
                    # add to list and reset
                    outputs.append(self.node_to_var[node])
                    self.G.edges[edge]["count"] = 0

        return outputs

    ###############################
    # serialization

    def __repr__(self):
        class SpaceDumper(yaml.SafeDumper):
            # insert blank lines between top-level objects
            def write_line_break(self, data=None):
                super().write_line_break(data)
                if len(self.indents) == 1:
                    super().write_line_break()

        return yaml.dump(self.data, Dumper=SpaceDumper, sort_keys=False)

    def __str__(self):
        return self.__repr__()

    def write_spec_to_file(self, fname: str):
        """dump completed IO spec to file"""
        with open(fname, "w") as f:
            f.write(str(self))

    def serialize_to_string(self):
        return str(self)

    @classmethod
    def deserialize_from_string(cls, yamlstr):
        data = yaml.safe_load(yamlstr)
        return cls(data)

    ###############################
    # ML-user-facing APIs
    # same level as fmot

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

        self.check()

    def set_padded_length(self, name: str, padded_length: int):
        if name in self.inputs:
            self.inputs[name]["padded_length"] = padded_length
        elif name in self.outputs:
            self.outputs[name]["padded_length"] = padded_length
        else:
            raise KeyError(f"name: {name} not in inputs or outputs")

        self.check()

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

        self.check()

    def add_signature(
        self,
        inputs: list[str],
        latched_inputs: list[str],
        outputs: list[str],
        name: Optional[str] = None,
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

        if name is None:
            name = "sequence"

        def _seq_name(name):
            return f"{name}_{len(self.simple_sequences)}"

        self.simple_sequences[_seq_name(name)] = IOSpecSimpleSequence(
            type="simple_sequence",
            inputs=inputs,
            outputs=outputs,
            comments=comments,
        )

        for x in latched_inputs:
            self.simple_sequences[_seq_name(name)] = IOSpecSimpleSequence(
                type="simple_sequence", inputs=[x], outputs=[], comments=comments
            )

        self.check()

    def latched_input_names(self) -> list[str]:
        names = set(list(self.inputs.keys()))
        for signame, sig in self.simple_sequences.items():
            if len(sig["outputs"]) > 0:
                for x in sig["inputs"]:
                    if x in names:
                        names.remove(x)

        return list(names)


class IOSpecLegacyPadding:
    def __init__(self, input_padding, output_padding):
        """Just used in interim period while we are moving to IOSpec-initialization
        returns None for recv_outputs,
        derived runners should not check names actually received against None
        """
        self.input_padding = self._shapeify(input_padding)
        self.output_padding = self._shapeify(output_padding)
        self.is_simple = True

    @staticmethod
    def _shapeify(padding):
        """some runners pass {k : (int, int)} for 1d instead of {k : ((int,), (int,))}"""
        if padding is None:
            return None

        to_shape = {}
        for k, (true_shape, padded_shape) in padding.items():
            if isinstance(true_shape, int):
                to_shape[k] = ((true_shape,), (padded_shape,))
            else:
                to_shape[k] = (true_shape, padded_shape)
        return to_shape

    def sim_send_inputs(self, *args, **kwargs):
        pass

    def sim_recv_outputs(self, *args, **kwargs):
        return None

    def sim_reset(self, *args, **kwargs):
        pass
