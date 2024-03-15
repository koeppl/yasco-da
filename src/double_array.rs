use serde::{Deserialize, Serialize};

use crate::util::{CharType, CHAR_SIZE};

#[derive(Serialize, Deserialize)]
pub struct DoubleArray {
    pub base: Vec<Option<usize>>,
    pub check: Vec<Option<usize>>,
}

const ROOT: usize = 0;

impl DoubleArray {
    /// Builds a double array of given keys.
    pub fn build(mut keys: Vec<Vec<CharType>>) -> Self {
        keys.sort_unstable();
        let mut da = Self {
            base: vec![],
            check: vec![],
        };
        da.expand();
        da.expand();
        da.add(ROOT, 0, keys.len(), 0, &keys);
        da.trim();
        da
    }

    pub fn len(&self) -> usize {
        self.check.len()
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    pub fn contain(&self, key: &[CharType]) -> bool {
        let mut cur = ROOT;
        for &c in key {
            if let Some(next) = self.next(cur, c) {
                cur = next;
            } else {
                return false;
            }
        }
        true
    }

    fn next(&self, parent: usize, c: CharType) -> Option<usize> {
        if let Some(base) = self.base[parent] {
            if let Some(check) = self.check[base + c as usize] {
                if check == parent {
                    return Some(base + c as usize);
                }
            }
        }
        None
    }

    /// Expands the base and check arrays.
    fn expand(&mut self) -> usize {
        for _ in 0..CHAR_SIZE {
            self.base.push(None);
            self.check.push(None);
        }
        self.base.len() - CHAR_SIZE
    }

    /// Trims the unused elements of tails of base and check arrays.
    fn trim(&mut self) {
        let mut num_used = 0;
        for i in (0..self.check.len()).rev() {
            if self.check[i].is_some() {
                num_used = i + 1;
                break;
            }
        }
        self.base.resize(num_used, None);
        self.check.resize(num_used, None);
    }

    pub fn num_used(&self) -> usize {
        self.check.iter().filter(|x| x.is_some()).count()
    }

    /// Finds a base that given characters can be inserted.
    /// Returns None if such base does not exist.
    fn find_base(&self, chars: &[CharType]) -> Option<usize> {
        if self.base.len() < CHAR_SIZE {
            return None;
        }
        for i in 1..self.base.len() - CHAR_SIZE {
            let pos_some = chars
                .iter()
                .find(|&&c| self.check[i + c as usize].is_some());
            if pos_some.is_none() {
                return Some(i);
            }
        }
        None
    }

    /// Set a base value and check for the node `parent`.
    fn set_base_check(&mut self, parent: usize, base: usize, chars: &[u8]) {
        // println!("base[{}]={}", parent, base);
        self.base[parent] = Some(base);
        for &c in chars {
            self.check[base + c as usize] = Some(parent);
        }
    }

    /// Adds a subtree.
    /// keys[key_beg][..char_idx] corresponds a string from to the node.
    /// All keys of keys[key_beg..key_end] have keys[key_beg][..char_idx] as prefix.
    /// `parent` indicates the index of the double array of the node, that is,
    /// `check[base[parent]+c]=parent`, where `c` is the child labels of the node.
    fn add(
        &mut self,
        parent: usize,
        key_beg: usize,
        key_end: usize,
        char_idx: usize,
        keys: &[Vec<u8>],
    ) {
        // dbg!((parent, key_beg, key_end, char_idx));
        assert!(key_beg <= key_end && key_end <= keys.len() && !keys.is_empty());
        if key_beg >= key_end || keys[key_end - 1].len() <= char_idx {
            return;
        }
        // sub range of children.
        let mut children: Vec<(usize, usize)> = vec![];
        // child labels
        let mut chars: Vec<u8> = vec![];
        let mut key_beg = (key_beg..key_end)
            .into_iter()
            .find(|&i| keys[i].len() > char_idx)
            .unwrap();

        while key_beg < key_end {
            let key_e = *(key_beg..key_end)
                .into_iter()
                .find(|&i| keys[key_beg][char_idx] != keys[i][char_idx])
                .get_or_insert(key_end);
            children.push((key_beg, key_e));
            chars.push(keys[key_e - 1][char_idx]);
            key_beg = key_e;
        }

        let base = self
            .find_base(&chars)
            .map_or_else(|| self.expand(), |pos| pos);
        self.set_base_check(parent, base, &chars);
        for i in 0..children.len() {
            let child = self.base[parent].unwrap() + chars[i] as usize;
            let (key_beg, key_end) = children[i];
            self.add(child, key_beg, key_end, char_idx + 1, keys);
        }
    }

    fn enum_keys_rec(&self, keys: &mut Vec<Vec<CharType>>, pref: Vec<CharType>, cur: usize) {
        // find children
        if self.base[cur].is_none() {
            keys.push(pref);
            return;
        }
        assert!(self.base[cur].is_some());
        let base = self.base[cur].unwrap();
        let mut children = vec![];
        for i in 0..CHAR_SIZE {
            let next = base + i;
            if next >= self.check.len() {
                break;
            }
            if self.check[next] == Some(cur) {
                children.push(i);
            }
        }
        assert!(!children.is_empty());
        for c in children {
            let mut pref_next = pref.clone();
            pref_next.push(c as CharType);
            self.enum_keys_rec(keys, pref_next, base + c);
        }
    }

    pub fn enum_keys(&self) -> Vec<Vec<CharType>> {
        let mut keys = vec![];
        self.enum_keys_rec(&mut keys, vec![], 0);
        keys
    }

    pub fn to_json(&self) -> String {
        serde_json::to_string(&self).unwrap()
    }

    pub fn from_json(json: &str) -> Self {
        serde_json::from_str(json).unwrap()
    }
}
