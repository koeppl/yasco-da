use std::fs::{self};

use clap::Parser;
use lupid::double_array::DoubleArray;

#[derive(Parser)]
#[clap(
    name = "build_matrix",
    author = "kg86",
    version = "v0.0.0",
    about = "builds matrix of trie"
)]
struct AppArg {
    #[clap(long = "input1")]
    input_path1: String,

    #[clap(long = "input2")]
    input_path2: String,
}

fn main() {
    let args: AppArg = AppArg::parse();
    let json1 = fs::read_to_string(&args.input_path1).unwrap();
    let da1 = DoubleArray::from_json(&json1);
    let keys1 = da1.enum_keys();
    let json2 = fs::read_to_string(&args.input_path2).unwrap();
    let da2 = DoubleArray::from_json(&json2);
    let keys2 = da2.enum_keys();

    println!("|da1|={}, |da2|={}", da1.len(), da2.len());
    println!("|keys1|={}, |keys2|={}", keys1.len(), keys2.len());
    assert_eq!(keys1.len(), keys2.len());
    assert_eq!(keys1, keys2);

}
