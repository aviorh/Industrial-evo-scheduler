## [7.08.2022, 14:00]
- integrated problems and sites-data to sqlite local db
- automatically load data from db on application startup
- db for solutions still not implemented (progress, raw solution).
- added status for each problem in db: `running`/`paused`/`idle`. if application reset, 
  all problems status is lazy updated to `idle`.
- added `GET` endpoints for all sites-data and problems
- updated postman collection


## [ 14.07.2022, 17:00]

### Added
- stop engine and cleanup endpoint


## [ 21.05.2022, 21:54]

### Added
- get progress endpoint

### Fixed
- algorithm loop condition

### removed
- editing number of generations endpoint  


## [ 21.05.2022, 19:27]

### Added
- endpoints:
  - get fitness logbook
  - get fitness graph


## [ 21.05.2022, 17:46 ]
### Fixed
- fix thread pausing mechanism
- api now receives string ids for stopping conditions instead of numbers
- time bound conversion from minutes to seconds


## [ 21.05.2022, 16:27]

### Added
- endpoints:
  - get the current best solution (3D numpy array converted to json 3D array)

## [ 06.05.2022, 15:28 ]

### Fixed
- fix serialize for `Problem` class


## [ 06.05.2022, 15:28 ]

### Added
- engine is now a Thread subclass, where run() is the function to execute the ea algorithm
- endpoints:
  - engine start, pause, resume

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
