use std::ops::{Index, IndexMut};

use array2d::Array2D;

use crate::Direction;

/// A row and column in the grid.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Hash)]
pub struct Location {
    pub row: usize,
    pub col: usize,
}

impl<T> Index<Location> for Array2D<T>
where
    T: Clone,
{
    type Output = T;

    fn index(&self, loc: Location) -> &Self::Output {
        &self[(loc.row, loc.col)]
    }
}

impl<T> IndexMut<Location> for Array2D<T>
where
    T: Clone,
{
    fn index_mut(&mut self, loc: Location) -> &mut Self::Output {
        &mut self[(loc.row, loc.col)]
    }
}

impl Location {
    /// Returns the location `count` squares in the given direction.
    #[rustfmt::skip]
    pub fn project(&self, dir: Direction, count: usize) -> Location {
        match dir {
            Direction::East => Location { col: self.col + count, ..*self },
            Direction::South => Location { row: self.row + count, ..*self },
            Direction::West => Location { col: self.col - count, ..*self },
            Direction::North => Location { row: self.row - count, ..*self },
        }
    }
}
