use crate::{Direction, Location};

/// A word slot, for example "a 5-letter word at square (0,2) pointing south".
#[derive(Clone, Copy, Debug, Eq, PartialEq, Hash)]
pub struct Slot {
    pub loc: Location,
    pub dir: Direction,
    pub len: usize,
}

impl Slot {
    /// Returns an iterator over the grid locations represented by this slot.
    pub fn locations(&self) -> impl Iterator<Item = Location> {
        let Slot { dir, loc, len } = *self;
        (0..len).map(move |squares| loc.project(dir, squares))
    }

    /// Given a word, returns an iterator over the letters and their locations starting from this
    /// slot.
    pub fn letter_locations<'word>(
        &self,
        word: &'word str,
    ) -> impl Iterator<Item = (char, Location)> + 'word {
        assert_eq!(word.chars().count(), self.len);
        word.chars().zip(self.locations())
    }
}
