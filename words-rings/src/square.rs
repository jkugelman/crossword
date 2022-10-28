/// A filled-in square in the grid. Keeps track of the count of overlapping words so words can be
/// removed without destroying crossing words.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Square {
    pub letter: char,
    pub crossings: usize,
}

impl Square {
    pub fn new(letter: char) -> Self {
        Self {
            letter,
            crossings: 0,
        }
    }
}
