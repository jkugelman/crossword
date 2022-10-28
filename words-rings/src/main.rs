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
    let mut grid = Grid::blank(size);

    let targets = window_pane(size, thickness);
    Search::search(&word_list, &mut grid, &targets);

    Ok(())
}

#[rustfmt::skip]
pub fn rings(size: usize, thickness: usize) -> Vec<Target> {
    assert!(thickness <= size / 2);

    let t = 0;
    let l = 0;
    let r = size - 1;
    let b = size - 1;

    (0..thickness)
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

pub fn eight(size: usize, thickness: usize) -> Vec<Target> {
    assert!(thickness <= size / 2);

    let mut targets = rings(size, thickness);

    for i in 0..thickness {
        targets.push(Target {
            loc: Location {
                row: size / 2 - thickness / 2 + i,
                col: 0,
            },
            dir: Direction::East,
            len: size,
        });
    }

    targets
}

pub fn window_pane(size: usize, thickness: usize) -> Vec<Target> {
    assert!(thickness <= size / 2);

    let mut targets = eight(size, thickness);

    for i in 0..thickness {
        targets.push(Target {
            loc: Location {
                row: 0,
                col: size / 2 - thickness / 2 + i,
            },
            dir: Direction::South,
            len: size,
        });
    }

    targets
}
