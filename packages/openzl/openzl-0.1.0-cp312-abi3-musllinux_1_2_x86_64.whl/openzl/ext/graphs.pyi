from collections.abc import Mapping, Sequence

import ext


class Graph:
    def __init__(self) -> None: ...

    def base_graph(self) -> ext.GraphID: ...

    def parameters(self) -> ext.GraphParameters | None: ...

    def set_destination(self, arg: ext.Edge, /) -> None: ...

    def set_multi_input_destination(self, arg: Sequence[ext.Edge], /) -> None: ...

    def parameterize(self, arg: ext.Compressor, /) -> ext.GraphID: ...

class Bitpack(Graph):
    """
    Bitpacks ints into the smallest number of bits possible

    Inputs:
    ints: TypeMask.Serial | TypeMask.Numeric
    """

    def __init__(self) -> None: ...

    def __call__(self, arg: ext.Compressor, /) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.GraphID: ...

    def set_destination(self, edge: ext.Edge) -> None: ...

    def set_multi_input_destination(self, edges: Sequence[ext.Edge]) -> None: ...

    @property
    def base_graph(self) -> ext.GraphID: ...

class Compress(Graph):
    """
    Compress the inputs using a generic compression backend

    Inputs:
    input: TypeMask.Any
    	...
    """

    def __init__(self) -> None: ...

    def __call__(self, arg: ext.Compressor, /) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.GraphID: ...

    def set_destination(self, edge: ext.Edge) -> None: ...

    def set_multi_input_destination(self, edges: Sequence[ext.Edge]) -> None: ...

    @property
    def base_graph(self) -> ext.GraphID: ...

class Constant(Graph):
    """
    Encode a constant input as a singleton value and size pair

    Inputs:
    constant data: TypeMask.Serial | TypeMask.Struct
    """

    def __init__(self) -> None: ...

    def __call__(self, arg: ext.Compressor, /) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.GraphID: ...

    def set_destination(self, edge: ext.Edge) -> None: ...

    def set_multi_input_destination(self, edges: Sequence[ext.Edge]) -> None: ...

    @property
    def base_graph(self) -> ext.GraphID: ...

class Entropy(Graph):
    """
    Compress the input using an order-0 entropy compressor

    Inputs:
    input: TypeMask.Serial | TypeMask.Struct | TypeMask.Numeric
    """

    def __init__(self) -> None: ...

    def __call__(self, arg: ext.Compressor, /) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.GraphID: ...

    def set_destination(self, edge: ext.Edge) -> None: ...

    def set_multi_input_destination(self, edges: Sequence[ext.Edge]) -> None: ...

    @property
    def base_graph(self) -> ext.GraphID: ...

class Huffman(Graph):
    """
    Compress the input using Huffman

    Inputs:
    input: TypeMask.Serial | TypeMask.Struct | TypeMask.Numeric
    """

    def __init__(self) -> None: ...

    def __call__(self, arg: ext.Compressor, /) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.GraphID: ...

    def set_destination(self, edge: ext.Edge) -> None: ...

    def set_multi_input_destination(self, edges: Sequence[ext.Edge]) -> None: ...

    @property
    def base_graph(self) -> ext.GraphID: ...

class Fse(Graph):
    """
    Compress the input using FSE

    Inputs:
    input: TypeMask.Serial
    """

    def __init__(self) -> None: ...

    def __call__(self, arg: ext.Compressor, /) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.GraphID: ...

    def set_destination(self, edge: ext.Edge) -> None: ...

    def set_multi_input_destination(self, edges: Sequence[ext.Edge]) -> None: ...

    @property
    def base_graph(self) -> ext.GraphID: ...

class FieldLz(Graph):
    """
    Compress the struct inputs using the FieldLZ codec with the default graphs

    Inputs:
    input: TypeMask.Struct | TypeMask.Numeric
    """

    def __init__(self, *, compression_level: int | None = None, literals_graph: ext.GraphID | None = None, tokens_graph: ext.GraphID | None = None, offsets_graph: ext.GraphID | None = None, extr_literal_lengths_graph: ext.GraphID | None = None, extra_match_lengths_graph: ext.GraphID | None = None) -> None: ...

    def __call__(self, arg: ext.Compressor, /) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.GraphID: ...

    def set_destination(self, edge: ext.Edge) -> None: ...

    def set_multi_input_destination(self, edges: Sequence[ext.Edge]) -> None: ...

    @property
    def base_graph(self) -> ext.GraphID: ...

class Flatpack(Graph):
    """
    Tokenize + bitpack

    Inputs:
    input: TypeMask.Serial
    """

    def __init__(self) -> None: ...

    def __call__(self, arg: ext.Compressor, /) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.GraphID: ...

    def set_destination(self, edge: ext.Edge) -> None: ...

    def set_multi_input_destination(self, edges: Sequence[ext.Edge]) -> None: ...

    @property
    def base_graph(self) -> ext.GraphID: ...

class SDDL(Graph):
    """
    Graph that runs the Simple Data Description Language over the input to decompose the input stream into a number of output streams. Must be given a description and successor. Refer to the SDDL documentation for usage instructions.

    Inputs:
    input: TypeMask.Serial
    """

    def __init__(self, *, description: str, successor: ext.GraphID) -> None: ...

    def __call__(self, arg: ext.Compressor, /) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.GraphID: ...

    def set_destination(self, edge: ext.Edge) -> None: ...

    def set_multi_input_destination(self, edges: Sequence[ext.Edge]) -> None: ...

    @property
    def base_graph(self) -> ext.GraphID: ...

class Store(Graph):
    """
    Store the input streams into the compressed frame

    Inputs:
    input: TypeMask.Any
    	...
    """

    def __init__(self) -> None: ...

    def __call__(self, arg: ext.Compressor, /) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.GraphID: ...

    def set_destination(self, edge: ext.Edge) -> None: ...

    def set_multi_input_destination(self, edges: Sequence[ext.Edge]) -> None: ...

    @property
    def base_graph(self) -> ext.GraphID: ...

class Zstd(Graph):
    """
    Zstd compress the input data

    Inputs:
    input: TypeMask.Serial
    """

    def __init__(self, *, compression_level: int | None = None, zstd_params: Mapping[int, int] | None = None) -> None: ...

    def __call__(self, arg: ext.Compressor, /) -> ext.GraphID: ...

    def parameterize(self, compressor: ext.Compressor) -> ext.GraphID: ...

    def set_destination(self, edge: ext.Edge) -> None: ...

    def set_multi_input_destination(self, edges: Sequence[ext.Edge]) -> None: ...

    @property
    def base_graph(self) -> ext.GraphID: ...
