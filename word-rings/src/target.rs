use crate::{Location, Direction};

/// A target location for entering a word, for example "a 5-letter word at square (0,2) pointing
/// south".
#[derive(Clone, Copy, Debug, Eq, PartialEq, Hash)]
pub struct Target {
    pub loc: Location,
    pub dir: Direction,
    pub len: usize,
}

impl Target {
    /// Returns an iterator over the grid locations represented by this target.
    pub fn locations(&self) -> impl Iterator<Item = Location> {
        let Target { dir, loc, len } = *self;
        (0..len).map(move |squares| loc.project(dir, squares))
    }

    /// Given a word, returns an iterator over the letters and their locations starting from this
    /// target.
    pub fn letter_locations<'word>(
        &self,
        word: &'word str,
    ) -> impl Iterator<Item = (char, Location)> + 'word {
        assert_eq!(word.chars().count(), self.len);
        word.chars().zip(self.locations())
    }
}
