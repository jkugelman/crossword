#![allow(clippy::uninlined_format_args)]

mod direction;
mod grid;
mod location;
mod search;
mod square;
mod target;
mod wordlist;

pub use direction::Direction;
pub use grid::Grid;
pub use location::Location;
pub use search::Search;
pub use square::Square;
pub use target::Target;
pub use wordlist::WordList;

use std::{env, io};

fn main() -> io::Result<()> {
    let mut args = env::args().skip(1);
    let word_list = args.next().expect("missing word list");
    let size = args
        .next()
        .expect("missing size")
        .parse::<usize>()
        .expect("bad size");
    let thickness = args
        .next()
        .expect("missing thickness")
        .parse::<usize>()
        .expect("bad thickness");

    let word_list = WordList::load(word_list)?;
    let grid = Grid::blank(size);

    let mut search = Search::load(&word_list, grid);
    let targets = eight(size, thickness);
    search.search_for(&targets);

    Ok(())
}

/// Generates a list of targets in a series of concentric rings moving inwards.
#[rustfmt::skip]
pub fn rings(size: usize, ring_count: usize) -> Vec<Target> {
    assert!(ring_count <= size / 2);

    let t = 0;
    let l = 0;
    let r = size - 1;
    let b = size - 1;

    (0..ring_count)
        .flat_map(|ring| {
            [
                Target { loc: Location { row: t + ring, col: l }, dir: Direction::East, len: size },
                Target { loc: Location { row: t, col: r - ring }, dir: Direction::South, len: size },
                Target { loc: Location { row: b - ring, col: l }, dir: Direction::East, len: size },
                Target { loc: Location { row: t, col: l + ring }, dir: Direction::South, len: size },
            ]
        })
        .collect()
}

/// Generates a list of targets in a series of concentric rings moving inwards.
pub fn eight(size: usize, thickness: usize) -> Vec<Target> {
    assert!(thickness <= size / 2);

    let mut rings = rings(size, thickness);

    for i in 0..thickness {
        rings.push(Target {
            loc: Location {
                row: size / 2 - thickness / 2 + i,
                col: 0,
            },
            dir: Direction::East,
            len: size,
        });
    }

    rings
}
