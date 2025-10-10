`qcop` enables standardized operation of dozens of Quantum Chemistry programs including `TeraChem`, `Psi4`, `rdkit`, `ORCA`, `MolPro`, `geomeTRIC`, `CREST`, `xtb`, `CFOUR`, `QCore`, `GAMESS`, `MRChem`, `NWChem`, `Q-Chem`, `Turbomole`, `MOPAC` and more using [qcio](https://qcio.coltonhicks.com) standardized data structures and a common pattern for running programs. `qcop` uses `Adapters` to operate QC programs in a standardized way. Program `Adapters` are listed to the left.

`qcop` does not standardize keywords across programs, so for detailed instructions on program options and keywords please consult the documentation for each individual program. `qcop` will pass these options/keywords through to the respective program.

This section contains details about how `qcop's` adapters for each program work and any details that might influence how you use a given program. Supported programs not listed on the left are supported via `QCEngine` which provides an adapter for numerous additional programs.

Special keywords that control the program for a particular program will be listed in the `compute_results()` method for each adapter.
