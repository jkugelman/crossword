use std::cell::RefCell;
use std::collections::HashSet;
use std::io::{stdout, Write};
use std::iter::{empty, repeat};

use crate::{Grid, Target, WordList};

#[derive(Debug, Clone)]
pub struct Search<'wl> {
    word_list: &'wl WordList,
    grid: RefCell<Grid>,
    used: RefCell<HashSet<&'wl str>>,
}

impl<'wl> Search<'wl> {
    pub fn load(word_list: &'wl WordList, grid: Grid) -> Self {
        Self {
            word_list,
            grid: RefCell::new(grid),
            used: RefCell::new(HashSet::new()),
        }
    }

    pub fn search_for(&self, targets: &[Target]) {
        match targets.split_first() {
            // Out of targets. Print the solution.
            None => {
                println!();
                println!("{}", self.grid.borrow());
            }

            Some((&target, later_targets)) => {
                let fits = self.word_list.find_fits(&self.grid.borrow(), target);
                for word in fits {
                    if !self.used.borrow_mut().insert(word) {
                        return;
                    }
                    self.grid.borrow_mut().enter(word, target).unwrap();
                    self.print_progress(later_targets.len());

                    self.search_for(later_targets);

                    self.grid.borrow_mut().erase(word, target).unwrap();
                    self.used.borrow_mut().remove(word);
                    self.print_progress(later_targets.len() + 1);
                }
            }
        }
    }

    fn print_progress(&self, remaining: usize) {
        let mut stdout = stdout().lock();

        let progress = self.used.borrow().len();
        let string = empty()
            .chain(repeat('|').take(progress))
            .chain(repeat(' ').take(remaining))
            .collect::<String>();
        let _ = write!(stdout, "\r[{}]", string);
        let _ = stdout.flush();
    }
}
