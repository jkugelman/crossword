use std::cell::{Cell, RefCell};
use std::collections::HashSet;
use std::io::{stderr, Write};
use std::iter::{empty, repeat};
use std::process::exit;

use crossterm::ExecutableCommand;
use crossterm::cursor::{Hide, Show};

use crate::{Grid, Target, WordList};

#[derive(Debug, Clone)]
pub struct Search<'wl> {
    word_list: &'wl WordList,
    grid: RefCell<Grid>,

    target_count: usize,
    used: RefCell<HashSet<&'wl str>>,
    percent_complete: Cell<f64>,
}

impl<'wl> Search<'wl> {
    pub fn load(word_list: &'wl WordList, grid: Grid) -> Self {
        Self {
            word_list,
            grid: RefCell::new(grid),

            target_count: 0,
            used: RefCell::new(HashSet::new()),
            percent_complete: Cell::default(),
        }
    }

    pub fn search_for(&mut self, targets: &[Target]) {
        let _hidden = hide_cursor();

        self.target_count = targets.len();
        self.search(targets, 0);
        println!();
    }

    fn search(&self, targets: &[Target], depth: usize) {
        match targets.split_first() {
            // Out of targets. Print the solution.
            None => {
                println!();
                println!("{}", self.grid.borrow());
            }

            Some((&target, later_targets)) => {
                let fits = self.word_list.find_fits(&self.grid.borrow(), target);
                for (i, word) in fits.iter().enumerate() {
                    if depth == 0 {
                        self.percent_complete.set(i as f64 / fits.len() as f64);
                    }

                    if !self.used.borrow_mut().insert(word) {
                        return;
                    }
                    self.grid.borrow_mut().enter(word, target).unwrap();
                    self.print_progress();

                    self.search(later_targets, depth + 1);

                    self.grid.borrow_mut().erase(word, target).unwrap();
                    self.used.borrow_mut().remove(word);
                    self.print_progress();
                }
            }
        }
    }

    fn print_progress(&self) {
        let mut stderr = stderr().lock();

        let progress = self.used.borrow().len();
        let remaining = self.target_count - progress;
        let string = empty()
            .chain(repeat('|').take(progress))
            .chain(repeat(' ').take(remaining))
            .collect::<String>();
        let percent = self.percent_complete.get() * 100.0;

        let _ = write!(stderr, "\r[{}] {:.0}%", string, percent);
        let _ = stderr.flush();
    }
}

struct HiddenCursor;

fn hide_cursor() -> HiddenCursor {
    let _ = ctrlc::set_handler(|| {
        let _ = stderr().lock().execute(Show);
        exit(1);
    });

    let _ = stderr().lock().execute(Hide);
    HiddenCursor
}

impl Drop for HiddenCursor {
    fn drop(&mut self) {
        let _ = stderr().lock().execute(Show);
    }
}
