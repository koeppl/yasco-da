use crate::util::CharType;

use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub struct TrieMatrix {
    mat: Vec<Vec<(CharType, usize)>>,
}

impl TrieMatrix {
    pub fn build(mut keys: Vec<Vec<CharType>>) -> Self {
        keys.sort_unstable();
        let mut tm = Self { mat: vec![vec![]] };
        tm.build_mat(&keys, 0, 0, keys.len(), 0);
        tm
    }

    pub fn contain(&self, key: &[CharType]) -> bool {
        let mut cur = 0;
        for &c in key {
            if let Some(child_id) = self.next(cur, c) {
                cur = child_id;
            } else {
                return false;
            }
        }
        true
    }

    fn next(&self, nid: usize, c: CharType) -> Option<usize> {
        self.mat[nid]
            .iter()
            .find(|&(d, _)| c == *d)
            .map(|&(_, child_id)| child_id)
    }

    fn build_mat(
        &mut self,
        keys: &[Vec<CharType>],
        nid: usize,
        key_beg: usize,
        key_end: usize,
        char_idx: usize,
    ) {
        assert!(self.mat[nid].is_empty());
        let mut key_beg = (key_beg..key_end)
            .into_iter()
            .find(|&i| keys[i].len() > char_idx)
            .unwrap_or(key_end);

        let mut children = vec![];
        while key_beg < key_end {
            let key_e = *(key_beg..key_end)
                .into_iter()
                .find(|&i| keys[key_beg][char_idx] != keys[i][char_idx])
                .get_or_insert(key_end);
            let c = keys[key_e - 1][char_idx];
            let child_id = self.mat.len();
            children.push((c, child_id, key_beg, key_e));
            self.mat.push(vec![]);
            key_beg = key_e;
        }
        children
            .into_iter()
            .for_each(|(c, child_id, key_beg, key_end)| {
                self.mat[nid].push((c, child_id));
                self.build_mat(keys, child_id, key_beg, key_end, char_idx + 1);
            });
    }
}
