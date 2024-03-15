use std::{fs, path::Path};

use lupid::{double_array::DoubleArray, util::read_lines};

use clap::Parser;

#[derive(Parser)]
#[clap(
    name = "build_da",
    author = "kg86",
    version = "v0.0.0",
    about = "builds double array"
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
    let keys = read_lines(path);
    let nokeys = keys.len();
    println!("# of keys = {}", keys.len());
    let da = DoubleArray::build(keys);
    println!("Size of double array is {}", da.base.len());
    println!(
        "{}/{}={:.5} is used",
        da.num_used(),
        da.len(),
        da.num_used() as f32 / da.base.len() as f32
    );
    println!(
        "RESULT method=greedy file={} keys={} baselength={} length={} filledentries={}",
        &args.input_path,
        nokeys,
        da.base.len(),
        da.len(),
        da.num_used()
    );

    let keys = read_lines(path);
    for mut key in keys {
        // println!("{:?}", key);
        assert!(da.contain(&key));
        key.extend_from_slice(br"hogehoge");
        // println!("{:?}", key);
        assert!(!da.contain(&key));
    }

    let json = da.to_json();
    fs::write(&args.output_path, json).unwrap();

    // for key in da.enum_keys() {
    //     println!("{}", std::str::from_utf8(&key).unwrap());
    // }
}
