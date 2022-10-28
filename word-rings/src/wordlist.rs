use std::collections::{HashMap, HashSet};
use std::fs::File;
use std::io::{self, BufRead, BufReader};
use std::path::Path;

use crate::{Grid, Target};

/// A crossword word list with clever indexes for speedy lookups.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct WordList {
    /// A raw list of all the words. The indexes below store positional indices into this vector.
    words: Vec<String>,
    /// Index of words by length.
    index_by_len: HashMap<usize, HashSet<usize>>,
    /// Index of words by length, letter position, and letter.
    index_by_len_pos_letter: HashMap<(usize, usize, char), HashSet<usize>>,
}

impl From<Vec<String>> for WordList {
    fn from(words: Vec<String>) -> Self {
        let mut index_by_len: HashMap<usize, HashSet<usize>> = HashMap::new();
        let mut index_by_len_pos_letter: HashMap<(usize, usize, char), HashSet<usize>> = HashMap::new();

        for (i, word) in words.iter().enumerate() {
            let len = word.chars().count();

            index_by_len.entry(len).or_default().insert(i);

            for (pos, letter) in word.chars().enumerate() {
                index_by_len_pos_letter.entry((len, pos, letter)).or_default().insert(i);
            }
        }

        Self {
            words,
            index_by_len,
            index_by_len_pos_letter,
        }
    }
}

impl WordList {
    /// Loads a word list where each line is in the format `word;score`.
    pub fn load(path: impl AsRef<Path>) -> io::Result<Self> {
        let path = path.as_ref();
        let file = File::open(path)?;
        let reader = BufReader::new(file);

        let mut words = Vec::new();

        for (i, line) in reader.lines().enumerate() {
            let line = line?;
            let Some((word, score)) = line.split_once(';') else {
                eprintln!("{}:{}: bad entry: {}", path.display(), i+1, line);
                continue;
            };

            let word = word.to_uppercase();
            let _score = score
                .parse::<u32>()
                .map_err(|e| io::Error::new(io::ErrorKind::InvalidData, e))?;

            words.push(word);
        }

        Ok(Self::from(words))
    }

    /// Returns a list of words of length `len`.
    pub fn words_with_len(&self, len: usize) -> HashSet<&str> {
        self.index_by_len
            .get(&len)
            .map(|indices| indices.iter().map(|&i| self.words[i].as_str()).collect())
            .unwrap_or_default()
    }

    /// Returns a list of words of length `len` that have `letter` at position `pos`. For example,
    /// all 21-letter words whose 3rd letter is "C".
    pub fn words_with_len_pos_letter(&self, len: usize, pos: usize, letter: char) -> HashSet<&str> {
        self.index_by_len_pos_letter
            .get(&(len, pos, letter))
            .map(|indices| indices.iter().map(|&i| self.words[i].as_str()).collect())
            .unwrap_or_default()
    }

    /// Returns words that would fit in the grid at the target location.
    pub fn find_fits(&self, grid: &Grid, target: Target) -> HashSet<&str> {
        let mut fits: Option<HashSet<&str>> = None;

        for (pos, square) in grid.squares(target).enumerate() {
            let Some(square) = square else {
                continue;
            };

            match &mut fits {
                None => {
                    fits = Some(self.words_with_len_pos_letter(target.len, pos, square.letter));
                }
                Some(fits) => {
                    fits.retain(|word| word.as_bytes()[pos] as char == square.letter);
                    if fits.is_empty() {
                        break;
                    }
                }
            }
        }

        // If all squares were blank then return the full word list.
        fits.unwrap_or_else(|| self.words_with_len(target.len))
    }
}
