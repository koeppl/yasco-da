use std::{
    fs::File,
    io::{self, BufRead},
    path::Path,
};

pub type CharType = u8;
pub const CHAR_SIZE: usize = 256;

pub fn read_lines(path: &Path) -> Vec<Vec<u8>> {
    let mut res = vec![];
    let file = File::open(path).unwrap();
    for line in io::BufReader::new(file).lines() {
        let line = line.unwrap().as_bytes().to_vec();
        // let x = str_u32vec(&line);
        res.push(line);
    }
    res
}

pub fn read_json(path: &Path) -> Vec<Vec<u8>> {
    let mut res = vec![];
    let file = File::open(path).unwrap();
    for line in io::BufReader::new(file).lines() {
        let line = line.unwrap().as_bytes().to_vec();
        // let x = str_u32vec(&line);
        res.push(line);
    }
    res
}
