use std::fmt::{self, Display, Formatter};
use std::ops::{Deref, DerefMut};

use array2d::Array2D;

use crate::{Direction, Location, Square, Target};

/// The crossword grid. Keeps track of the letters in each square and how many overlapping words
/// there are in each location.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Grid(Array2D<Option<Square>>);

impl Grid {
    /// Returns a blank grid of the requested size, for example `21` for a 21x21 grid.
    pub fn blank(size: usize) -> Self {
        Self(Array2D::filled_with(None, size, size))
    }

    /// The grid size. For simplicity, grids are always square.
    pub fn size(&self) -> usize {
        assert_eq!(self.0.num_rows(), self.0.num_columns());
        self.0.num_rows()
    }

    /// Returns an iterator over the letters of a word and the squares they correspond with starting
    /// from the target location.
    pub fn squares(&self, target: Target) -> impl Iterator<Item = &Option<Square>> {
        target
            .locations()
            .take_while(|&loc| self.is_in_bounds(loc))
            .map(|loc| &self[loc])
    }

    /// Returns an iterator over the letters of a word and the squares they correspond with starting
    /// from the target location.
    pub fn letter_squares<'grid, 'word: 'grid>(
        &'grid self,
        word: &'word str,
        target: Target,
    ) -> impl Iterator<Item = (char, &'grid Option<Square>)> + 'grid {
        target
            .letter_locations(word)
            .map(|(letter, loc)| (letter, &self[loc]))
    }

    /// Adds a word to the grid. Fails if there's a conflict with any crossing words.
    #[allow(clippy::result_unit_err)]
    pub fn enter(&mut self, word: &str, target: Target) -> Result<(), ()> {
        // Check if the word fits up front to avoid having partially-entered words.
        self.check_with(word, target, |(letter, square)| {
            if let Some(square) = square {
                square.letter == letter
            } else {
                true
            }
        })?;

        for (letter, loc) in target.letter_locations(word) {
            let square = &mut self[loc];
            let square = square.get_or_insert_with(|| Square::new(letter));

            assert_eq!(square.letter, letter);
            square.crossings += 1;
        }
        Ok(())
    }

    /// Removes an existing word from the grid without disturbing crossing words.
    #[allow(clippy::result_unit_err)]
    pub fn erase(&mut self, word: &str, target: Target) -> Result<(), ()> {
        // Check that the word is present up front to avoid having partially-removed words.
        self.check_with(word, target, |(letter, square)| {
            square
                .as_ref()
                .map_or(false, |square| square.letter == letter)
        })?;

        for (_letter, loc) in target.letter_locations(word) {
            let square = &mut self[loc];
            let crossings = &mut square.as_mut().unwrap().crossings;
            *crossings -= 1;
            if *crossings == 0 {
                *square = None;
            }
        }
        Ok(())
    }

    /// Checks that a word at the target location matches the given predicate.
    #[allow(clippy::result_unit_err)]
    pub fn check_with(
        &self,
        word: &str,
        target: Target,
        pred: impl FnMut((char, &Option<Square>)) -> bool,
    ) -> Result<(), ()> {
        if self.letter_squares(word, target).all(pred) {
            Ok(())
        } else {
            Err(())
        }
    }

    /// Checks if `loc` is in the bounds of this grid.
    pub fn is_in_bounds(&self, loc: Location) -> bool {
        loc.row < self.num_rows() && loc.col < self.num_columns()
    }

    /// Generates a list of targets in a series of concentric rings moving inwards.
    pub fn ring_targets(&self) -> Vec<Vec<Target>> {
        let t = 0;
        let l = 0;
        let r = self.size() - 1;
        let b = self.size() - 1;

        let mut txs = Vec::new();

        for ring in 0..self.size() / 2 {
            #[rustfmt::skip]
            txs.push(vec![
                Target { loc: Location { row: t + ring, col: l }, dir: Direction::East},
                Target { loc: Location { row: t, col: r - ring }, dir: Direction::South},
                Target { loc: Location { row: b - ring, col: l }, dir: Direction::East},
                Target { loc: Location { row: t, col: l + ring }, dir: Direction::South},
            ]);
        }

        if self.size() % 2 != 0 {
            txs.push(vec![
                Target {
                    loc: Location {
                        row: t + self.size() / 2,
                        col: l,
                    },
                    dir: Direction::East,
                },
                Target {
                    loc: Location {
                        row: t,
                        col: l + self.size() / 2,
                    },
                    dir: Direction::South,
                },
            ]);
        }

        txs
    }
}

impl Deref for Grid {
    type Target = Array2D<Option<Square>>;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl DerefMut for Grid {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.0
    }
}

impl Display for Grid {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        for row in self.rows_iter() {
            let line = row
                .map(|square| square.as_ref().map(|s| s.letter).unwrap_or(' '))
                .collect::<String>();
            writeln!(f, "{}", line)?;
        }
        Ok(())
    }
}
