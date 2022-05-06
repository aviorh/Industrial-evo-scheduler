

## [ 06.05.2022, 15:28 ]

### Fixed
- fixed issue with site data parser
- fixed issues with engine.run()


## [ 05.05.2022, 19:45 ]

### Added
- SiteData deletion endpoint addition
- redundant logic from api.py removed

## [ 05.05.2022, 19:15 ]

### Added
- problem deletion endpoint completed
- collections at SiteManager were transformed to dict from list
- SiteData class properties case changed to snake case

## [ 05.05.2022 ]

### Added
- SiteData creation endpoint completed

## [ 5.5.2022 ]

### Added
- endpoints:
  - add_problem
  - add_mutation_method
  - edit_crossover_method
  - edit_selection_method
  - edit_ea_population_size
  - edit_num_ea_generation
  - get_problem_by_id
  - get_problems
- parallel mutation methods are currently not supported


## [ 30.4.2022 ]

### Added
- AppManager class
- Basic support for flask server
- Added constraints and engine
- POC
- Created json file for site data
