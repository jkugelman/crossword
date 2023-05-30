#![allow(clippy::uninlined_format_args)]

mod direction;
mod grid;
mod location;
mod search;
mod slot;
mod square;
mod wordlist;

pub use direction::Direction;
pub use grid::Grid;
pub use location::Location;
pub use search::Search;
pub use slot::Slot;
pub use square::Square;
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
    let pattern = args.next().expect("missing pattern");
    let thickness = args
        .next()
        .expect("missing thickness")
        .parse::<usize>()
        .expect("bad thickness");

    let word_list = WordList::load(word_list)?;
    let mut grid = Grid::blank(size);

    let slots = match pattern.as_str() {
        "ring" => ring(size, thickness),
        "figure_eight" => figure_eight(size, thickness),
        "window_pane" => window_pane(size, thickness),
        "cross" => cross(size, thickness),
        "custom" => custom(size, thickness),
        _ => panic!("bad pattern, expected ring|figure_eight|window_pane|cross|custom"),
    };
    Search::search(&word_list, &mut grid, &slots);

    Ok(())
}

fn ring(size: usize, thickness: usize) -> Vec<Slot> {
    assert!(thickness <= size / 2);

    let t = 0;
    let l = 0;
    let r = size - 1;
    let b = size - 1;

    #[rustfmt::skip]
    let slots = (0..thickness)
        .flat_map(|i| {
            [
                Slot { loc: Location { row: t + i, col: l }, dir: Direction::East, len: size },
                Slot { loc: Location { row: t, col: r - i }, dir: Direction::South, len: size },
                Slot { loc: Location { row: b - i, col: l }, dir: Direction::East, len: size },
                Slot { loc: Location { row: t, col: l + i }, dir: Direction::South, len: size },
            ]
        })
        .collect();
    slots
}

fn figure_eight(size: usize, thickness: usize) -> Vec<Slot> {
    assert!(thickness <= size / 2);

    let mut slots = ring(size, thickness);
    for i in 0..thickness {
        slots.push(Slot {
            loc: Location {
                row: size / 2 - thickness / 2 + i,
                col: 0,
            },
            dir: Direction::East,
            len: size,
        });
    }
    slots
}

fn window_pane(size: usize, thickness: usize) -> Vec<Slot> {
    assert!(thickness <= size / 2);

    let mut slots = figure_eight(size, thickness);
    for i in 0..thickness {
        slots.push(Slot {
            loc: Location {
                row: 0,
                col: size / 2 - thickness / 2 + i,
            },
            dir: Direction::South,
            len: size,
        });
    }
    slots
}

fn cross(size: usize, thickness: usize) -> Vec<Slot> {
    assert!(thickness <= size / 2);

    let row = size / 2;
    let col = size / 2;

    let slots = (0..isize::try_from(thickness).unwrap())
        .flat_map(|i| {
            let offset = match i % 2 {
                0 if i == 0 => 0,
                1 => (i + 1) / 2,
                0 => -i / 2,
                _ => unreachable!(),
            };

            [
                Slot {
                    loc: Location {
                        row: row.saturating_add_signed(offset),
                        col: 0,
                    },
                    dir: Direction::East,
                    len: size,
                },
                Slot {
                    loc: Location {
                        row: 0,
                        col: col.saturating_add_signed(offset),
                    },
                    dir: Direction::South,
                    len: size,
                },
            ]
        })
        .collect();
    slots
}

fn custom(_size: usize, _thickness: usize) -> Vec<Slot> {
    vec![
        // Slot { loc: Location { row: 2, col: 0 }, dir: Direction::East, len: 15 },
        Slot {
            loc: Location { row: 0, col: 2 },
            dir: Direction::South,
            len: 15,
        },
        // Slot { loc: Location { row: 12, col: 0 }, dir: Direction::East, len: 15 },
        Slot {
            loc: Location { row: 0, col: 12 },
            dir: Direction::South,
            len: 15,
        },
    ]
}
