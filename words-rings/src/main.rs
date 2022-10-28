#![allow(clippy::uninlined_format_args)]

mod direction;
mod grid;
mod location;
mod square;
mod target;
mod wordlist;

pub use direction::Direction;
pub use grid::Grid;
pub use location::Location;
pub use square::Square;
pub use target::Target;
pub use wordlist::WordList;

use std::cell::RefCell;
use std::{io, env};
use std::path::Path;

#[derive(Debug, Clone)]
struct RingSearch {
    word_list: WordList,
    grid: RefCell<Grid>,
    min_depth: usize,
}

impl RingSearch {
    pub fn load(path: impl AsRef<Path>, size: usize, min_depth: usize) -> io::Result<Self> {
        let word_list = WordList::load_filtered(path, |(word, _)| word.chars().count() == size)?;
        let grid = Grid::blank(size);
        Ok(Self {
            word_list,
            grid: RefCell::new(grid),
            min_depth,
        })
    }

    pub fn go(&self) {
        let rings = self.grid.borrow().ring_targets();
        self.do_rings(&rings, 1);
    }

    fn do_rings(&self, rings: &[Vec<Target>], depth: usize) {
        let Some((ring, inner_rings)) = rings.split_first() else {
            return;
        };
        let Some((&target, later_targets)) = ring.split_first() else {
            return;
        };

        self.do_target(target, later_targets, inner_rings, depth);
    }

    fn do_target(
        &self,
        target: Target,
        later_targets: &[Target],
        inner_rings: &[Vec<Target>],
        depth: usize,
    ) {
        let fits = self.word_list.find_fits(&self.grid.borrow(), target);
        for word in fits {
            self.do_word(word, target, later_targets, inner_rings, depth);
        }
    }

    fn do_word(
        &self,
        word: &str,
        target: Target,
        later_targets: &[Target],
        inner_rings: &[Vec<Target>],
        depth: usize,
    ) {
        self.grid.borrow_mut().enter(word, target).unwrap();

        if let Some((&next_target, later_targets)) = later_targets.split_first() {
            self.do_target(next_target, later_targets, inner_rings, depth);
        } else {
            if depth >= self.min_depth {
                if depth > self.min_depth {
                    println!("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                }
                print!("{}", self.grid.borrow());
                if depth > self.min_depth {
                    println!("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                }
                println!();
            }
            self.do_rings(inner_rings, depth + 1);
        }

        self.grid.borrow_mut().erase(word, target).unwrap();
    }
}

fn main() -> io::Result<()> {
    let args = env::args().collect::<Vec<String>>();
    let size = args[1].parse::<usize>().expect("bad size");
    let min_depth = args[2].parse::<usize>().expect("bad rings");

    let ring_search = RingSearch::load("XwiJeffChenList.txt", size, min_depth)?;
    ring_search.go();
    Ok(())
}
