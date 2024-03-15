use std::{fs::File, io::Write, path::Path};

use clap::Parser;
use lupid::{trie_matrix::TrieMatrix, util::read_lines};

#[derive(Parser)]
#[clap(
    name = "build_matrix",
    author = "kg86",
    version = "v0.0.0",
    about = "builds matrix of trie"
)]
struct AppArg {
    #[clap(short = 'i', long = "input")]
    input_path: String,
    #[clap(short = 'o', long = "output")]
    output_path: String,
}

fn main() {
    let args: AppArg = AppArg::parse();
    let path = Path::new(&args.input_path);
    // let file = File::open(path).unwrap();
    // let reader = BufReader::new(file);
    // let da1: DoubleArray = serde_json::from_reader::<DoubleArray>(reader).unwrap();
    // let da1: DoubleArray = serde_json::from_reader(reader).unwrap();
    let keys = read_lines(path);
    let tm = TrieMatrix::build(keys);

    let json = serde_json::to_string(&tm).unwrap();
    let file = File::create(&args.output_path).unwrap();
    write!(&file, "{}", json).unwrap();

    let keys = read_lines(path);
    for mut key in keys {
        // println!("{:?}", &key);
        assert!(tm.contain(&key));
        key.extend_from_slice(br"hogehoge");
        // println!("{:?}", key);
        assert!(!tm.contain(&key));
    }
    // use to_le_bytes()
}
