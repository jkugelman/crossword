use std::collections::{HashMap, HashSet};
use std::fs::File;
use std::io::{self, BufRead, BufReader};
use std::path::Path;

use crate::{Grid, Target};

/// A crossword word list with clever indexes for speedy lookups.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct WordList {
    words: Vec<String>,
    index: HashMap<usize, HashMap<char, HashSet<usize>>>,
}

impl From<Vec<String>> for WordList {
    fn from(words: Vec<String>) -> Self {
        let mut index: HashMap<usize, HashMap<char, HashSet<usize>>> = HashMap::new();

        for (i, word) in words.iter().enumerate() {
            for (pos, letter) in word.chars().enumerate() {
                let index = index.entry(pos).or_default();
                let index = index.entry(letter).or_default();
                index.insert(i);
            }
        }

        Self { words, index }
    }
}

impl WordList {
    /// Loads a word list where each line is in the format `word;score`.
    pub fn load(path: impl AsRef<Path>) -> io::Result<Self> {
        Self::load_filtered(path, |_| true)
    }

    /// Loads a filtered word list where each line is in the format `word;score`. Only words that
    /// pass the filter are kept.
    pub fn load_filtered(
        path: impl AsRef<Path>,
        mut filter: impl FnMut((&str, u32)) -> bool,
    ) -> io::Result<Self> {
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
            let score = score
                .parse::<u32>()
                .map_err(|e| io::Error::new(io::ErrorKind::InvalidData, e))?;

            if filter((&word, score)) {
                words.push(word);
            }
        }

        Ok(Self::from(words))
    }

    /// Returns a list of words that have `letter` at position `pos`. For example, all words whose
    /// 3rd letter is "C".
    pub fn find_letter_at_pos(&self, pos: usize, letter: char) -> HashSet<&str> {
        let index = self.index.get(&pos);
        let index = index.and_then(|index| index.get(&letter));

        if let Some(index) = index {
            index.iter().map(|&pos| self.words[pos].as_str()).collect()
        } else {
            HashSet::new()
        }
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
                    fits = Some(self.find_letter_at_pos(pos, square.letter));
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
        fits.unwrap_or_else(|| self.words.iter().map(String::as_str).collect())
    }
}
