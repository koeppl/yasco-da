# yasco-DA: yet another space-compress-optimization for the double array

The double-array is a trie implementation that has been well-used in practice for 
indexing a set of strings for prefix search or membership queries - a fundamental task with many applications such as information retrieval or database systems.
Due to the fundamental nature of this problem, it has sparked much interest, leading to a variety of trie implementations with different characteristics.
While a traversal takes constant time per node visit, the needed space consumption in computer words can be as large as the product of the number of nodes and the alphabet size.
We here propose an approximation based on a SAT encoding.

## Implementation Details
We implemented the SAT formulation using the PySAT library.
We proceed as follows for a user-defined timeout parameter.

- compute greedily a double array by reading each string from the input set of strings. 
If this double array has length $\lambda_2$ and $\lambda_1$ nodes, then our search interval for the optimal value is $\lambda \in [\lambda_1..\lambda_2]$.
- try to find a double array with length of at most $\lambda$, where $\lambda$ is given by performing a binary search on the initial range $[\lambda_1..\lambda_2]$;
- abort the search when it exceeds the timeout.

By doing so, we try to approximate the smallest double array size until a computation instance is exceeding our timeout.
Additionally, our approach can apply parallelization via parallel binary search.


## Commands

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
  - `timeout`: timeout in seconds for each call of `dasolver.py`
  - `n_proc`: number of processors (default: 1)
  - `output`: up-so-far computed double array trie represented in JSON format
- `./benchmark.sh` : creates folder `eval` and runs exhaustive benchmarks on the dataset `words_5000` [1].

[1]: https://github.com/legalforce-research/stringmatch-bench
