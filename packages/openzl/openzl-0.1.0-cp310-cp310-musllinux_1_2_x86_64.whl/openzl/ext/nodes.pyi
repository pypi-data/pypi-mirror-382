from collections.abc import Sequence

import ext
import ext.graphs


class Node:
    def __init__(self) -> None: ...

    def base_node(self) -> ext.NodeID: ...

    def parameters(self) -> ext.NodeParameters | None: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

class Bitunpack(Node):
    """
    Unpack integers of a fixed bit-width

    Inputs:
    bitpacked: Type.Serial


    Singleton Outputs:
    unpacked ints: Type.Numeric
    """

    def __init__(self, num_bits: int) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class ConcatSerial(Node):
    """
    Concatenate all inputs into a single output

    Inputs:
    input: Type.Serial
    	...

    Singleton Outputs:
    input lengths: Type.Numeric
    concatenated: Type.Serial
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, lengths: ext.GraphID | ext.graphs.Graph, concatenated: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class ConcatStruct(Node):
    """
    Concatenate all inputs into a single output

    Inputs:
    input: Type.Struct
    	...

    Singleton Outputs:
    input lengths: Type.Numeric
    concatenated: Type.Struct
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, lengths: ext.GraphID | ext.graphs.Graph, concatenated: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class ConcatNumeric(Node):
    """
    Concatenate all inputs into a single output

    Inputs:
    input: Type.Numeric
    	...

    Singleton Outputs:
    input lengths: Type.Numeric
    concatenated: Type.Numeric
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, lengths: ext.GraphID | ext.graphs.Graph, concatenated: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class ConcatString(Node):
    """
    Concatenate all inputs into a single output

    Inputs:
    input: Type.String
    	...

    Singleton Outputs:
    input lengths: Type.Numeric
    concatenated: Type.String
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, lengths: ext.GraphID | ext.graphs.Graph, concatenated: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class Concat(Node):
    def __init__(self, type: ext.Type) -> None: ...

    def __call__(self, compressor: ext.Compressor, lengths: ext.GraphID | ext.graphs.Graph, concatenated: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class ConvertStructToSerial(Node):
    """
    Convert struct to serial

    Inputs:
    input: Type.Struct


    Singleton Outputs:
    converted: Type.Serial
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class ConvertSerialToStruct(Node):
    """
    Convert a serial input to a struct output with the given struct size

    Inputs:
    input: Type.Serial


    Singleton Outputs:
    converted: Type.Struct
    """

    def __init__(self, struct_size_bytes: int) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class ConvertNumToSerialLE(Node):
    """
    Convert numeric to serial in little-endian format

    Inputs:
    input: Type.Numeric


    Singleton Outputs:
    converted: Type.Serial
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class ConvertSerialToNum8(Node):
    """
    Convert serial input of 8-bit data to numeric output

    Inputs:
    input: Type.Serial


    Singleton Outputs:
    converted: Type.Numeric
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class ConvertSerialToNumLE16(Node):
    """
    Convert serial input of little-endian 16-bit data to numeric output

    Inputs:
    input: Type.Serial


    Singleton Outputs:
    converted: Type.Numeric
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class ConvertSerialToNumLE32(Node):
    """
    Convert serial input of little-endian 32-bit data to numeric output

    Inputs:
    input: Type.Serial


    Singleton Outputs:
    converted: Type.Numeric
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class ConvertSerialToNumLE64(Node):
    """
    Convert serial input of little-endian 64-bit data to numeric output

    Inputs:
    input: Type.Serial


    Singleton Outputs:
    converted: Type.Numeric
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class ConvertSerialToNumBE16(Node):
    """
    Convert serial input of big-endian 16-bit data to numeric output

    Inputs:
    input: Type.Serial


    Singleton Outputs:
    converted: Type.Numeric
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class ConvertSerialToNumBE32(Node):
    """
    Convert serial input of big-endian 32-bit data to numeric output

    Inputs:
    input: Type.Serial


    Singleton Outputs:
    converted: Type.Numeric
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class ConvertSerialToNumBE64(Node):
    """
    Convert serial input of big-endian 64-bit data to numeric output

    Inputs:
    input: Type.Serial


    Singleton Outputs:
    converted: Type.Numeric
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class ConvertSerialToNumLE(Node):
    def __init__(self, int_size_bytes: int) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class ConvertSerialToNumBE(Node):
    def __init__(self, int_size_bytes: int) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class ConvertNumToStructLE(Node):
    """
    Convert numeric input to a little-endian fixed-size struct output

    Inputs:
    input: Type.Numeric


    Singleton Outputs:
    converted: Type.Struct
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class ConvertStructToNumLE(Node):
    """
    Convert little-endian fixed-size struct input to numeric output

    Inputs:
    input: Type.Struct


    Singleton Outputs:
    converted: Type.Numeric
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class ConvertStructToNumBE(Node):
    """
    Convert big-endian fixed-size struct input to numeric output

    Inputs:
    input: Type.Struct


    Singleton Outputs:
    converted: Type.Numeric
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class ConvertSerialToString(Node):
    """
    Convert a serial input to a string output by telling OpenZL the string lengths

    Inputs:
    input: Type.Serial


    Singleton Outputs:
    converted: Type.String
    """

    def __init__(self, string_lens: Sequence[int]) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class SeparateStringComponents(Node):
    """
    Separate a string input into its content and lengths streams

    Inputs:
    strings: Type.String


    Singleton Outputs:
    string content: Type.Serial
    32-bit string lengths: Type.Numeric
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, content: ext.GraphID | ext.graphs.Graph, lengths: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class DedupNumeric(Node):
    """
    Takes N numeric inputs containing exactly the same data & outputs a single copy

    Inputs:
    duplicated: Type.Numeric
    	...

    Singleton Outputs:
    deduped: Type.Numeric
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class DeltaInt(Node):
    """
    Output the deltas between each int in the input. The first value is written into the header.

    Inputs:
    input: Type.Numeric


    Singleton Outputs:
    deltas: Type.Numeric
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class DispatchSerial(Node):
    """
    Dispatch serial data into one of the `dispatched` variable outputs according to the `Instructions`.

    Inputs:
    input: Type.Serial


    Singleton Outputs:
    tags: Type.Numeric
    sizes: Type.Numeric


    Variable Outputs:
    dispatched: Type.Serial
    """

    def __init__(self, *, segment_tags: Sequence[int], segment_sizes: Sequence[int], num_tags: int) -> None: ...

    def __call__(self, compressor: ext.Compressor, tags: ext.GraphID | ext.graphs.Graph, sizes: ext.GraphID | ext.graphs.Graph, dispatched: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class DispatchString(Node):
    """
    Dispatch serial data into one of the `dispatched` variable outputs according to the `tags`

    Inputs:
    input: Type.String


    Singleton Outputs:
    tags: Type.Numeric


    Variable Outputs:
    dispatched: Type.String
    """

    def __init__(self, *, tags: Sequence[int], num_tags: int) -> None: ...

    def __call__(self, compressor: ext.Compressor, tags: ext.GraphID | ext.graphs.Graph, dispatched: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class DivideBy(Node):
    """
    Divide the input by the given divisor or the GCD if none is provided

    Inputs:
    input: Type.Numeric


    Singleton Outputs:
    output: Type.Numeric
    """

    def __init__(self, *, divisor: int | None = None) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class FieldLz(Node):
    """
    Run an LZ compression that matches whole structs

    Inputs:
    input: Type.Struct


    Singleton Outputs:
    literals: Type.Struct
    tokens (2-bytes): Type.Struct
    offsets: Type.Numeric
    extra literal lengths: Type.Numeric
    extra match lengths: Type.Numeric
    """

    def __init__(self, compression_level: int | None = None) -> None: ...

    def __call__(self, compressor: ext.Compressor, literals: ext.GraphID | ext.graphs.Graph, tokens: ext.GraphID | ext.graphs.Graph, offsets: ext.GraphID | ext.graphs.Graph, extra_literal_lengths: ext.GraphID | ext.graphs.Graph, extra_match_lengths: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class Float32Deconstruct(Node):
    """
    Separate float exponents from sign+fraction

    Inputs:
    floats: Type.Numeric


    Singleton Outputs:
    sign+fraction bits (24-bits): Type.Struct
    exponent bits (8-bits): Type.Serial
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, sign_frac: ext.GraphID | ext.graphs.Graph, exponent: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class BFloat16Deconstruct(Node):
    """
    Separate float exponents from sign+fraction

    Inputs:
    floats: Type.Numeric


    Singleton Outputs:
    sign+fraction bits (8-bits): Type.Struct
    exponent bits (8-bits): Type.Serial
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, sign_frac: ext.GraphID | ext.graphs.Graph, exponent: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class Float16Deconstruct(Node):
    """
    Separate float exponents from sign+fraction

    Inputs:
    floats: Type.Numeric


    Singleton Outputs:
    sign+fraction bits (11-bits): Type.Struct
    exponent bits (5-bits): Type.Serial
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, sign_frac: ext.GraphID | ext.graphs.Graph, exponent: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class MergeSorted(Node):
    """
    Merge <= 64 sorted u32 runs into a bitset telling whether the i'th run has the next value, and the sorted list of unique u32 values

    Inputs:
    sorted u32 runs: Type.Numeric


    Singleton Outputs:
    bitset: Type.Numeric
    strictly increasing u32s: Type.Numeric
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, bitset: ext.GraphID | ext.graphs.Graph, sorted: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class ParseInt(Node):
    """
    Parse ASCII integers into int64_t

    Inputs:
    ascii int64s: Type.String


    Singleton Outputs:
    int64s: Type.Numeric
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class Prefix(Node):
    """
    Remove shared prefixes between consecutive elements

    Inputs:
    strings: Type.String


    Singleton Outputs:
    suffixes: Type.String
    prefix lengths: Type.Numeric
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class QuantizeOffsets(Node):
    """
    Quantize uint32_t values != 0 using a power-of-2 scheme

    Inputs:
    input: Type.Numeric


    Singleton Outputs:
    codes: Type.Numeric
    extra_bits: Type.Serial
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, codes: ext.GraphID | ext.graphs.Graph, extra_bits: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class QuantizeLengths(Node):
    """
    Quantize uint32_t values giving small values a unique code and large values a code based on their log2

    Inputs:
    input: Type.Numeric


    Singleton Outputs:
    codes: Type.Numeric
    extra_bits: Type.Serial
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, codes: ext.GraphID | ext.graphs.Graph, extra_bits: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class RangePack(Node):
    """
    Subtract the minimum value and pack into the smallest possible integer width

    Inputs:
    input: Type.Numeric


    Singleton Outputs:
    output: Type.Numeric
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class SplitSerial(Node):
    """
    Split the input into N segments according to the given `segmentSizes`

    Inputs:
    input: Type.Serial


    Variable Outputs:
    segments: Type.Serial
    """

    def __init__(self, *, segment_sizes: Sequence[int]) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class SplitStruct(Node):
    """
    Split the input into N segments according to the given `segmentSizes`

    Inputs:
    input: Type.Struct


    Variable Outputs:
    segments: Type.Struct
    """

    def __init__(self, *, segment_sizes: Sequence[int]) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class SplitNumeric(Node):
    """
    Split the input into N segments according to the given `segmentSizes`

    Inputs:
    input: Type.Numeric


    Variable Outputs:
    segments: Type.Numeric
    """

    def __init__(self, *, segment_sizes: Sequence[int]) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class SplitString(Node):
    """
    Split the input into N segments according to the given `segmentSizes`

    Inputs:
    input: Type.String


    Variable Outputs:
    segments: Type.String
    """

    def __init__(self, *, segment_sizes: Sequence[int]) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class Split(Node):
    def __init__(self, *, segment_sizes: Sequence[int]) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class TokenizeStruct(Node):
    """
    Tokenize the input struct into an alphabet of unique values and indices into that alphabet

    Inputs:
    input: Type.Struct


    Singleton Outputs:
    alphabet: Type.Struct
    indices: Type.Numeric
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, alphabet: ext.GraphID | ext.graphs.Graph, indices: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class TokenizeNumeric(Node):
    """
    Tokenize the input struct into an alphabet of unique values and indices into that alphabet

    Inputs:
    input: Type.Numeric


    Singleton Outputs:
    alphabet: Type.Numeric
    indices: Type.Numeric
    """

    def __init__(self, *, sort: bool = False) -> None: ...

    def __call__(self, compressor: ext.Compressor, alphabet: ext.GraphID | ext.graphs.Graph, indices: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class TokenizeString(Node):
    """
    Tokenize the input struct into an alphabet of unique values and indices into that alphabet

    Inputs:
    input: Type.String


    Singleton Outputs:
    alphabet: Type.String
    indices: Type.Numeric
    """

    def __init__(self, *, sort: bool = False) -> None: ...

    def __call__(self, compressor: ext.Compressor, alphabet: ext.GraphID | ext.graphs.Graph, indices: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class Tokenize(Node):
    def __init__(self, *, type: ext.Type, sort: bool = False) -> None: ...

    def __call__(self, compressor: ext.Compressor, alphabet: ext.GraphID | ext.graphs.Graph, indices: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class TransposeSplit(Node):
    """
    Transpose the input structs into their lanes, and produce one output per lane

    Inputs:
    input: Type.Struct


    Variable Outputs:
    lanes: Type.Serial
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...

class Zigzag(Node):
    """
    Zigzag encode the input values

    Inputs:
    input: Type.Numeric


    Singleton Outputs:
    output: Type.Numeric
    """

    def __init__(self) -> None: ...

    def __call__(self, compressor: ext.Compressor, successor: ext.GraphID | ext.graphs.Graph) -> ext.GraphID: ...

    def run(self, edge: ext.Edge) -> list[ext.Edge]: ...

    def run_multi_input(self, edges: Sequence[ext.Edge]) -> list[ext.Edge]: ...

    def build_graph(self, compressor: ext.Compressor, successors: Sequence[ext.GraphID]) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.NodeID: ...

    @property
    def base_node(self) -> ext.NodeID: ...
