use std::collections::{HashMap, HashSet};
use std::fs::File;
use std::io::{self, BufRead, BufReader, Read};
use std::path::Path;

use crate::{Grid, Slot};

/// Word score like 30 or 50.
pub type Score = u16;

/// A crossword word list with clever indexes for speedy lookups.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct WordList {
    /// A raw list of all the words. The indexes below store positional indices into this vector.
    words: Vec<String>,
    /// Word scores, stored in the same order as `words`.
    scores: Vec<Score>,
    /// Index of words by length.
    index_by_len: HashMap<usize, HashSet<usize>>,
    /// Index of words by length, letter position, and letter.
    index_by_len_pos_letter: HashMap<(usize, usize, char), HashSet<usize>>,
}

impl WordList {
    /// Creates a word list from a list of words and their scores.
    ///
    /// # Panics
    ///
    /// Panics if `words` and `scores` have different lengths.
    pub fn new(words: Vec<String>, scores: Vec<Score>) -> Self {
        assert_eq!(words.len(), scores.len());

        let mut index_by_len: HashMap<_, HashSet<usize>> = HashMap::new();
        let mut index_by_len_pos_letter: HashMap<_, HashSet<usize>> = HashMap::new();

        for (i, word) in words.iter().enumerate() {
            let len = word.chars().count();

            index_by_len.entry(len).or_default().insert(i);

            for (pos, letter) in word.chars().enumerate() {
                index_by_len_pos_letter
                    .entry((len, pos, letter))
                    .or_default()
                    .insert(i);
            }
        }

        Self {
            words,
            scores,
            index_by_len,
            index_by_len_pos_letter,
        }
    }

    /// Creates a word list with scores calculated by a custom function.
    pub fn new_with(words: Vec<String>, score_fn: impl Fn(&str) -> Score) -> Self {
        let scores = words.iter().map(|word| score_fn(word)).collect::<Vec<_>>();
        Self::new(words, scores)
    }

    /// Creates a word list where every entry has the same default score.
    pub fn new_with_default_score(words: Vec<String>, default_score: Score) -> Self {
        Self::new_with(words, |_| default_score)
    }

    /// Loads a word list where each line is in the format `word;score;optional clue`.
    pub fn load(path: impl AsRef<Path>) -> io::Result<Self> {
        let path = path.as_ref();
        let file = File::open(path)?;
        Self::load_reader(file, &path.to_string_lossy())
    }

    /// Loads a word list from a generic reader where each line is in the format
    /// `word;score;optional clue`.
    pub fn load_reader(reader: impl Read, name: &str) -> io::Result<Self> {
        fn inner(reader: &mut dyn BufRead, name: &str) -> io::Result<WordList> {
            let mut words = Vec::new();
            let mut scores = Vec::new();

            for (i, line) in reader.lines().enumerate() {
                let line = line?;

                let parts = line.split(';').take(2).collect::<Vec<_>>();
                let &[word, score] = &parts[..]
                else {
                    eprintln!("{}:{}: bad entry: {}", name, i + 1, line);
                    continue;
                };

                let word = word.to_uppercase();
                let score = score
                    .parse::<Score>()
                    .map_err(|e| io::Error::new(io::ErrorKind::InvalidData, e))?;

                words.push(word);
                scores.push(score);
            }

            Ok(WordList::new(words, scores))
        }

        let mut reader = BufReader::new(reader);
        inner(&mut reader, name)
    }

    /// Returns the score of a particular word.
    pub fn score(&self, word: &str) -> Option<Score> {
        let index = self.words.iter().position(|w| w == word)?;
        let score = self.scores[index];
        Some(score)
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

    /// Returns words that would fit in a grid slot.
    pub fn find_fits(&self, grid: &Grid, slot: Slot) -> HashSet<&str> {
        let mut fits: Option<HashSet<&str>> = None;

        for (pos, square) in grid.squares(slot).enumerate() {
            let Some(square) = square else {
                continue;
            };

            match &mut fits {
                None => {
                    fits = Some(self.words_with_len_pos_letter(slot.len, pos, square.letter));
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
        fits.unwrap_or_else(|| self.words_with_len(slot.len))
    }
}
