use std::borrow::Cow;
use std::collections::{hash_set, HashMap, HashSet};
use std::fs::File;
use std::io::{self, BufRead, BufReader, Read};
use std::iter;
use std::path::Path;

use itertools::{Either, Itertools};

use crate::{Grid, Slot};

/// Word score like 30 or 50.
pub type Score = u16;

/// A crossword word list with clever indexes for speedy lookups.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct WordList {
    /// A raw list of all the words stored in alphabetical order.
    /// The indexes below store positional indices into this vector.
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

        // Sort both `words` and `scores` at the same time.
        let (mut words, mut scores) = (words, scores);
        let mut permutation = permutation::sort(&words);
        permutation.apply_slice_in_place(&mut words);
        permutation.apply_slice_in_place(&mut scores);

        // Build the indexes.
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

                let word = word.to_string();
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
}

impl WordList {
    /// Returns an iterator over words of length `len`.
    pub fn words_with_len(&self, len: usize) -> WordsWithLen<'_> {
        WordsWithLen {
            word_list: self,
            iter: self.index_by_len.get(&len).map(HashSet::iter),
        }
    }
}

#[derive(Clone, Debug)]
struct WordsWithLen<'wl> {
    word_list: &'wl WordList,
    iter: Option<hash_set::Iter<'wl, usize>>,
}

impl<'wl> Iterator for WordsWithLen<'wl> {
    type Item = &'wl str;

    fn next(&mut self) -> Option<Self::Item> {
        self.iter
            .as_mut()?
            .next()
            .map(|&idx| self.word_list.words[idx].as_str())
    }
}

impl ExactSizeIterator for WordsWithLen<'_> {
    fn len(&self) -> usize {
        self.iter.as_ref().map_or(0, |iter| iter.len())
    }
}

impl WordList {
    /// Returns an iterator over words of length `len` that have `letter` at position `pos`. For
    /// example, all 21-letter words whose 3rd letter is "C".
    pub fn words_with_len_pos_letter(
        &self,
        len: usize,
        pos: usize,
        letter: char,
    ) -> WordsWithLenPosLetter<'_> {
        WordsWithLenPosLetter {
            word_list: self,
            iter: self
                .index_by_len_pos_letter
                .get(&(len, pos, letter))
                .map(HashSet::iter),
        }
    }
}

#[derive(Clone, Debug)]
struct WordsWithLenPosLetter<'wl> {
    word_list: &'wl WordList,
    iter: Option<hash_set::Iter<'wl, usize>>,
}

impl<'wl> Iterator for WordsWithLenPosLetter<'wl> {
    type Item = &'wl str;

    fn next(&mut self) -> Option<Self::Item> {
        self.iter
            .as_mut()?
            .next()
            .map(|&idx| self.word_list.words[idx].as_str())
    }
}

impl ExactSizeIterator for WordsWithLenPosLetter<'_> {
    fn len(&self) -> usize {
        self.iter.as_ref().map_or(0, |iter| iter.len())
    }
}

impl WordList {
    /// Returns words that would fit in a grid slot.
    pub fn find_fits(&self, grid: &Grid, slot: Slot) -> FindFits<'_> {
        let mut fits: Option<HashSet<&str>> = None;

        let filled_squares = grid
            .squares(slot)
            .enumerate()
            .flat_map(|(pos, square)| square.map(|square| (pos, square)))
            .collect_vec();

        match filled_squares[..] {
            // If all squares are filled then return the word whether or not it's in the word list.
            _ if filled_squares.len() == slot.len => {
                let word = filled_squares
                    .iter()
                    .map(|(_, square)| square.letter)
                    .collect::<String>();
                FindFits::AllFilled(Some(word))
            }

            // If all squares are blank then return the full word list.
            [] => FindFits::AllBlank(self.words_with_len(slot.len)),

            // If only one square is filled then return words that fit that square.
            [(pos, square)] => {
                FindFits::OneFilled(self.words_with_len_pos_letter(slot.len, pos, square.letter))
            }

            // If multiple squares are filled then return words that fit all squares.
            [..] => {
                // Get the word sets for each filled square, sorted by length.
                let word_sets = filled_squares
                    .iter()
                    .map(|(pos, square)| {
                        self.index_by_len_pos_letter
                            .get(&(slot.len, *pos, square.letter))
                    })
                    .sorted_by_key(|set| set.map_or(0, HashSet::len))
                    .collect_vec();
                assert!(word_sets.len() >= 2);

                // Get the intersection of all word sets.
                let mut word_sets = word_sets.into_iter();
                let mut fits = word_sets.next().unwrap().cloned().unwrap_or_default();

                for word_set in word_sets {
                    let Some(word_set) = word_set else { break; };
                    fits.retain(|idx| word_set.contains(idx));
                    if fits.capacity() >= fits.len() * 2 {
                        fits.shrink_to_fit();
                    }
                }

                FindFits::MultipleFilled(self, fits.into_iter().collect_vec())
            }
        }
    }
}

#[derive(Clone, Debug)]
enum FindFits<'wl> {
    AllFilled(Option<String>),
    AllBlank(WordsWithLen<'wl>),
    OneFilled(WordsWithLenPosLetter<'wl>),
    MultipleFilled(&'wl WordList, Vec<usize>),
}

impl<'wl> Iterator for FindFits<'wl> {
    type Item = Cow<'wl, str>;

    fn next(&mut self) -> Option<Self::Item> {
        match self {
            FindFits::AllFilled(word) => word.take().map(Cow::Owned),
            FindFits::AllBlank(iter) => iter.next().map(Cow::Borrowed),
            FindFits::OneFilled(iter) => iter.next().map(Cow::Borrowed),
            FindFits::MultipleFilled(word_list, indexes) => indexes
                .pop()
                .map(|idx| Cow::Borrowed(word_list.words[idx].as_str())),
        }
    }
}

impl<'wl> ExactSizeIterator for FindFits<'wl> {
    fn len(&self) -> usize {
        match self {
            FindFits::AllFilled(word) => {
                if word.is_some() {
                    1
                } else {
                    0
                }
            }
            FindFits::AllBlank(iter) => iter.len(),
            FindFits::OneFilled(iter) => iter.len(),
            FindFits::MultipleFilled(_, iter) => iter.len(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_load_reader() {
        let wordlist = load_test_wordlist();

        assert_eq!(wordlist.words, vec!["foo", "bar", "baz", "quux"]);
        assert_eq!(wordlist.scores, vec![30, 50, 30, 40]);
        assert_eq!(
            wordlist.index_by_len,
            HashMap::from([(3, HashSet::from([0, 1, 2])), (4, HashSet::from([3])),])
        );
        assert_eq!(
            wordlist.index_by_len_pos_letter,
            HashMap::from([
                ((3, 0, 'f'), HashSet::from([0])),
                ((3, 1, 'o'), HashSet::from([0])),
                ((3, 2, 'o'), HashSet::from([0])),
                ((3, 0, 'b'), HashSet::from([1, 2])),
                ((3, 1, 'a'), HashSet::from([1, 2])),
                ((3, 2, 'r'), HashSet::from([1])),
                ((3, 2, 'z'), HashSet::from([2])),
                ((4, 0, 'q'), HashSet::from([3])),
                ((4, 1, 'u'), HashSet::from([3])),
                ((4, 2, 'u'), HashSet::from([3])),
                ((4, 3, 'x'), HashSet::from([3])),
            ])
        );
    }

    #[test]
    fn test_score() {
        let wordlist = load_test_wordlist();

        assert_eq!(wordlist.score("foo"), Some(30));
        assert_eq!(wordlist.score("bar"), Some(50));
        assert_eq!(wordlist.score("baz"), Some(30));
        assert_eq!(wordlist.score("quux"), Some(40));
        assert_eq!(wordlist.score("quuux"), None);
    }

    #[test]
    fn test_words_with_len() {
        let wordlist = load_test_wordlist();

        assert_eq!(
            wordlist.words_with_len(3).collect::<HashSet<_>>(),
            HashSet::from(["foo", "bar", "baz"])
        );
        assert_eq!(
            wordlist.words_with_len(4).collect::<HashSet<_>>(),
            HashSet::from(["quux"])
        );
        assert_eq!(
            wordlist.words_with_len(5).collect::<HashSet<_>>(),
            HashSet::new()
        );
    }

    #[test]
    fn test_words_with_len_pos_letter() {
        let wordlist = load_test_wordlist();

        assert_eq!(
            wordlist
                .words_with_len_pos_letter(3, 0, 'f')
                .collect::<HashSet<_>>(),
            HashSet::from(["foo"])
        );
        assert_eq!(
            wordlist
                .words_with_len_pos_letter(3, 1, 'o')
                .collect::<HashSet<_>>(),
            HashSet::from(["foo"])
        );
        assert_eq!(
            wordlist
                .words_with_len_pos_letter(3, 2, 'o')
                .collect::<HashSet<_>>(),
            HashSet::from(["foo"])
        );
        assert_eq!(
            wordlist
                .words_with_len_pos_letter(3, 0, 'b')
                .collect::<HashSet<_>>(),
            HashSet::from(["bar", "baz"])
        );
        assert_eq!(
            wordlist
                .words_with_len_pos_letter(3, 1, 'a')
                .collect::<HashSet<_>>(),
            HashSet::from(["bar", "baz"])
        );
        assert_eq!(
            wordlist
                .words_with_len_pos_letter(3, 2, 'r')
                .collect::<HashSet<_>>(),
            HashSet::from(["bar"])
        );
        assert_eq!(
            wordlist
                .words_with_len_pos_letter(3, 2, 'z')
                .collect::<HashSet<_>>(),
            HashSet::from(["baz"])
        );
        assert_eq!(
            wordlist
                .words_with_len_pos_letter(3, 0, 'q')
                .collect::<HashSet<_>>(),
            HashSet::new()
        );
        assert_eq!(
            wordlist
                .words_with_len_pos_letter(3, 1, 'u')
                .collect::<HashSet<_>>(),
            HashSet::new()
        );
        assert_eq!(
            wordlist
                .words_with_len_pos_letter(3, 2, 'u')
                .collect::<HashSet<_>>(),
            HashSet::new()
        );
        assert_eq!(
            wordlist
                .words_with_len_pos_letter(3, 3, 'x')
                .collect::<HashSet<_>>(),
            HashSet::new()
        );
    }

    fn load_test_wordlist() -> WordList {
        let words = ["foo;30", "bar;50", "baz;30", "quux;40"];
        let words = words.join("\n");
        WordList::load_reader(words.as_bytes(), "test").unwrap()
    }
}
