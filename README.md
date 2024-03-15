# 🎧 lupid: LayoUt oPtImized Double array


# Commands

- `cargo run --bin build_matrix -- --input "$inputFile" --output "$matrixFile"`
  - `inputFile`: reads a text file with keywords separated by new lines
  - `matrixFile`: input for `./dasolver/dasolver.py`
- `cargo run --bin build_da -- --input "$inputFile" --output "$doubleFile"`: computes a double array trie greedily
  - `inputFile`: reads a text file with keywords separated by new lines
  - `doubleFile`: double array trie built greedily and represented in JSON format
- `pipenv run ./dasolver/dasolver.py --mat "$matrixFile" --output "$optDoubleArray" --minimize --n_arr "$size"`: computes an optimal double array trie
  - `matrixFile`: input from `build_matrix`
  - `optDoubleArray`: optimal double array trie represented in JSON format
  - `size`: upper bound on the length of the base/check array of the double array
- `pipenv run ./dasolver/da_subopt.py --input "$inputFile" --timeout "${timeout}s" --n_proc "$procs" --output "$optDoubleArray"`: binary searches to minimize the double array length
  - `inputFile`: reads a text file with keywords separated by new lines
  - `timeout`: timeout in secends for each call of `dasolver.py`
  - `n_proc`: number of processors (default: 1)
  - `output`: up-so-far computed double array trie represented in JSON format
- `./benchmark.sh` : creates folder `eval` and runs exhaustive benchmarks on the dataset `words_5000` [1].

[1]: https://github.com/legalforce-research/stringmatch-bench
