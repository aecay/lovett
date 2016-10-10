# Before sending to Anton

- [ ] API documentation for all functions
- [ ] reasonably complete coverage of intended domains
- [ ] at least a skeleton of narrative docs – focus on aims/goals/target
  audience; secondary focus on showing how it’s used
- [x] ipython integration (rudimentary, to show things off in notebook format)
- infrastructure:
  - [x] test coverage reporting
  - [ ] use hypothesis for generative testing? (save for later?)
  - [x] continuous integration
  - [ ] read the docs
  - [ ] versioneye
- [ ] speed benchmarks
  - figure out the sql indexing story
- [ ] review all todos in code
- [ ] doc coverage calculation; remove undoc-members from makefile


# Before sending to Joel, Caitlin, other technical users (= “private” beta)

- fully worked examples of:
  - [ ] searching
  - [ ] corpus revision
  - [ ] (optional) coding queries
- [ ] mostly-complete documentation


# Before sending to Tony, Beatrice, et al. (= public beta)

- [ ] a fully worked “pretty” ipython example (graphs, interactivity, ...)
- ...?

# Before releasing

- ???

# Annotald integration

- [ ] use this as the backend in the annotald python program
- [ ] split out the annotald js
- [ ] define a transfer representation for trees (json?), make annotald
  accept this, emit it from lovett
- [ ] annotald based on react (cljs)

# Next steps (as of 12/9/15)

- [ ] Parallel corpus db backend
  - wraps N CorpusDb objects, proxies calls to add_tree(s) and splits
    between them

- [ ] Test how much the `__slots__` optimization on Trees actually matters –
  the marking code would be much simpler if we could just add attributes
  to the dict of Tree objects freely.
  - It looks like it’s ~10% of time and ~25-50% of the memory.  Not
    huge, but probably still important

- [x] Implement saving corpus dbs to file
