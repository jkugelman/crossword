use std::collections::HashSet;
use std::io::{stderr, Write};
use std::iter::{empty, repeat};
use std::process::exit;

use crossterm::cursor::{Hide, Show};
use crossterm::ExecutableCommand;

use crate::{Grid, Target, WordList};

#[derive(Clone, Debug, Default)]
pub struct Search<'wl> {
    target_count: usize,
    peak_count: usize,
    used: HashSet<&'wl str>,
    percent_complete: f64,
}

impl<'wl> Search<'wl> {
    pub fn search(word_list: &'wl WordList, grid: &mut Grid, targets: &[Target]) {
        let mut search = Self {
            target_count: targets.len(),
            peak_count: 0,
            used: HashSet::new(),
            percent_complete: 0.0,
        };

        let _hidden = hide_cursor();
        search.search_r(word_list, grid, targets);
        println!();
    }

    fn search_r(&mut self, word_list: &'wl WordList, grid: &mut Grid, targets: &[Target]) {
        match targets.split_first() {
            // Out of targets. Print the solution.
            None => {
                println!();
                println!("{}", grid);
            }

            Some((&target, later_targets)) => {
                let fits = word_list.find_fits(grid, target);
                for (i, word) in fits.iter().enumerate() {
                    if self.used.is_empty() {
                        self.percent_complete = i as f64 / fits.len() as f64;
                    }

                    if !self.used.insert(word) {
                        return;
                    }
                    self.peak_count = self.peak_count.max(self.used.len());
                    grid.enter(word, target).unwrap();
                    self.print_progress();

                    self.search_r(word_list, grid, later_targets);

                    grid.erase(word, target).unwrap();
                    self.used.remove(word);
                    self.print_progress();
                }
            }
        }
    }

    fn print_progress(&self) {
        let mut stderr = stderr().lock();

        assert!(self.used.len() <= self.peak_count);
        assert!(self.peak_count <= self.target_count);

        let progress = self.used.len();
        let peak = self.peak_count - progress;
        let remaining = self.target_count - self.peak_count;
        let string = empty()
            .chain(repeat('█').take(progress))
            .chain(repeat('░').take(peak))
            .chain(repeat(' ').take(remaining))
            .collect::<String>();
        let percent = self.percent_complete * 100.0;

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
