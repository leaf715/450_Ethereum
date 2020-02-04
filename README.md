# Parsing & Visualization Tool for EVM Traces

There are 2 modules:
- `trace_parser.py`: parse a trace file into a list of `Transaction` objects.
- `dfg_builder.py`: extract a `Graph` object out of a `Transaction` object. The extracted graph can be turned into a PDF file via its `.render` function. The `Graph` object is well traversable via the `.predecessors_of` and `.successors_of` functions.

I also wrote some helper functions in `struct_dump.py` to serialize an object of some arbitrary class. I believe it is a useful feature for debugging. **But please notice that the classes cannot contain loop references, otherwise the serialization would fail from infinite recursion.**

Please see the `test()` function of each Python file to get a better idea of how to use these modules.

*Also note: compared to my original visualizer, the arrow direction of edges are **flipped** in this version. I think that the arrow direction now is more conventional for a Data Flow Graph.*