#!/usr/bin/env zsh
function die {
	echo "$1" >&2
	exit 1
}

evalPath="eval"
mkdir -p "$evalPath"

rawInputFile="$evalPath/words_5000.txt"

[[ ! -r "$rawInputFile" ]] && curl -o "$rawInputFile"  "https://raw.githubusercontent.com/legalforce-research/stringmatch-bench/main/data/words_5000.txt"
[[ -r "$rawInputFile" ]] || die "$rawInputFile not readable"
pipenv sync
cargo build


for noPhrases in $(seq 1 5000); do
	inputFile="$evalPath/words.${noPhrases}.txt"
	matrixFile="$evalPath/words.${noPhrases}.mat"
	rustDoubleArray="$evalPath/words.${noPhrases}.rust.json"


	./truncateLines.py --input "$rawInputFile" --output "$inputFile" --length "$noPhrases"
	[[ -r "$inputFile" ]] || die "$inputFile not readable"

	# set -x
	# set -e
	cargo run --bin build_matrix -- --input "$inputFile" --output "$matrixFile"
	timestart=$(date +%s)
	out=$(cargo run --bin build_da -- --input "$inputFile" --output "$rustDoubleArray")
	timeend=$(date +%s)
	echo "RESULT method=time algo=greedy file=${inputFile} seconds=$(($timeend-$timestart))"
	echo "$out"
	sizePattern="^RESULT.* length=\([0-9]\+\) .*"
	size=$(echo "$out" | grep "$sizePattern" | sed "s@$sizePattern@\1@")

	# pipenv run ./dasolver/dasolver.py --mat "$matrixFile" --output "$optDoubleArray" --minimize --n_arr "$size"

	# for procs in $(seq 1 $(nproc)); do
	for procs in $(seq 2 2); do
		for timeout in $(seq 10 10 120); do
			optDoubleArray="$evalPath/words.${noPhrases}.subopt.${timeout}s.${procs}p.json"
			timestart=$(date +%s)
			pipenv run ./dasolver/da_subopt.py --input "$inputFile" --timeout "${timeout}s" --n_proc "$procs" --output "$optDoubleArray"
			timeend=$(date +%s)
			echo "RESULT method=time algo=subopt seconds=$(($timeend-$timestart)) file=${inputFile} procs=${procs} timeout=${timeout}"
			cargo run --bin identify_da -- --input1 "$rustDoubleArray" --input2 "$optDoubleArray"
		done
	done
done | tee "$evalPath"/log.txt

