use crate::{Location, Direction};

/// A target location and direction for a word, for example "square (0,2) looking south".
#[derive(Clone, Copy, Debug, Eq, PartialEq, Hash)]
pub struct Target {
    pub loc: Location,
    pub dir: Direction,
}

impl Target {
    /// Returns an iterator over the locations reachable from the target.
    ///
    /// # Note
    ///
    /// This is an infinite iterator since the grid size is unknown here.
    pub fn locations(&self) -> impl Iterator<Item = Location> {
        let Target { dir, loc } = *self;
        (0..).map(move |squares| loc.project(dir, squares))
    }

    /// Given a word, returns an iterator over the letters and their locations starting from this
    /// target.
    pub fn letter_locations<'word>(
        &self,
        word: &'word str,
    ) -> impl Iterator<Item = (char, Location)> + 'word {
        word.chars().zip(self.locations())
    }
}
