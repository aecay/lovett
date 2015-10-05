# Before sending to Anton

- API documentation for all functions
- reasonably complete coverage of intended domains
- at least a skeleton of narrative docs – focus on aims/goals/target
  audience; secondary focus on showing how it’s used
- ipython integration (rudimentary, to show things off in notebook format)
- infrastructure:
  - test coverage reporting
  - use hypothesis for generative testing? (save for later?)
  - continuous integration
  - read the docs
  - versioneye
- speed benchmarks
  - figure out the sql indexing story
- review all todos in code


# Before sending to Joel, Caitlin, other technical users (= “private” beta)

- fully worked examples of:
  - searching
  - corpus revision
  - (optional) coding queries
- mostly-complete documentation


# Before sending to Tony, Beatrice, et al. (= public beta)

- a fully worked “pretty” ipython example (graphs, interactivity, ...)
- ...?

# Before releasing

- ???

# Annotald integration

- use this as the backend in the annotald python program
- split out the annotald js
- define a transfer representation for trees (json?), make annotald
  accept this, emit it from lovett
- annotald based on react
