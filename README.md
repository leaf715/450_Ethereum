# 450_Ethereum
## Folders
- Contract DB: Workspace for Modules for Graph Library
- Final Deliverables: Finalized Codebase and Evaluation Data
- Parser: Workspace for Parser and visualizer
- Similarity: Old Similarity Algorithm from Midterm

## Codebase
#### Module -1: trace_generator.py
Creates fake traces that simulate traces expected from data collector
To run:
- gen_traces(start, stop, trace_dir)
  - *start: starting block number*
  - *stop: ending block number*
  - *trace_dir: folder name for traces*
  - Generates fake traces for a range of blocks in folder *trace_dir*
  - **Example Results in trace_eval/**
#### Module 0: parser.py
Parses trace into objects
to run:
- parse_file(file_name)
  - *file_name: trace file to parse*
  - Returns a list of TransactionLevelTrace objects which contain CallLevelTrace, Output, Taint, and Dependency Objects
- (another version of parser is available parser_1.py which is strictly as per the graph analysis library)
#### Module 1: DB_builder.py
Builds state database for contracts called in the traces
To run:
- DB_Builder(log_dir, level_size)
  - *log_dir: folder for creating database in*
  - *level_size: number of bytes to hash each level by within database*
  - Initializes DB_Builder object
- DB_Builder.build_DB(trace_dir, start, end, restart)
  - *trace_dir: folder containting traces*
  - *start: starting block number*
  - *end: ending block number*
  - *restart: Clear database and restart if true. Else continue from last logged trace. False if left blank*
  - Generates contract state database folder _log_dir_ by scanning traces in a range of blocks in folder *trace_dir*
  - **Example Results in DB_eval/**
#### Module 2: Cross_Linker.py
Links transactions based on contract storage reads and writes
To run:
- Cross_Linker(log_dir, trace_dir, level_size)
  - *log_dir: folder where contract database is*
  - *trace_dir: folder where traces are*
  - *level_size: number of bytes to hash each level by within database*
  - Initializes Cross_Linker object
- Cross_Linker.link(trace, tx_id, direction)
  - *trace: block number*
  - *tx_id: transaction id*
  - *direction: forward or backward linking. Input must be "forward" or "backward"*
  - *restart: Clear database and restart if true. Else continue from last logged trace. False if left blank*
  - Returns dictionary with the linked external taint
    - Backward: dictionary key is the SLOAD taint id and the value is the block trxn and taint of the external taint
    - Forward: outer dictionary key is contract that was written to and inner dictionary key is taint that wrote to storage and value is list of external taints that read the storage
  - **Example Results in test_cl.json**
#### Module 3: Transformer.py
Transforms trace into grey box representation
To run:
- Transformer(trace_dir, trace)
  - *trace_dir: folder where traces are*
  - *trace: the block of the trace*
  - Initializes Transformer object
- Transformer.greybox_call(tx_id, call_id)
  - *tx_id: transaction id*
  - *call_id: call id"*
  - Returns a CallLevelTrace object where call.taints has been replaced with only the grey taints and the grey dependencies
  - **Example Results Visualized in test_trans/**
 - Transformer.greybox_trxn(tx_id)
  - *tx_id: transaction id*
  - Returns a TransactionLevelTrace object where the only call left is the root call with transaction level grey box taints
  - **Example Results Visualized in test_trans/**
#### Module 5: Visualizer.py
Creates a human readable graph illustration of the trace
To run:
- Graph(tx_ct)
  - *tx_ct: list of a transaction's call level traces*
  - Initializes Graph object
- Graph.render(output_filename):
  - *output_filename: name of pdf file to be produced*
  - Creates a visual graph of the transaction
 (test_cross_vis is the visualiser for backward linking , taking the trace and the output of cross_linker as input)
  - **Example Visualizations in test_trans/**
