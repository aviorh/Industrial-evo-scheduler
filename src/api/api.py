import connexion

from src.app_manager.app_manager import AppManager


def add_mutation_method(body, problem_id):
    """add new mutation for specific problem
    :param body: mutation configuration
    :type body: dict | bytes
    :param problem_id: Numeric ID to get problem
    :type problem_id: int

    :rtype: object
    """
    if connexion.request.is_json:
        body = connexion.request.get_json()

    mutation_id = body['mutation_id']
    mutation_params = body.get('mutation_parameters', dict())

    am = AppManager()
    problem = am.add_mutation(problem_id, mutation_id, mutation_params)
    return problem.to_dict_format()


def add_problem(body):
    """create a new problem from a given site data (id)
    :param body: related site data id
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = connexion.request.get_json()
    
    app_manager = AppManager()
    site_data_id = body['site_data_id']

    new_problem = app_manager.create_problem(site_data_id=site_data_id)
    return new_problem.to_dict_format()


def delete_stopping_condition(problem_id, cond_id):
    """delete stopping condition

    :param problem_id: Numeric ID to get problem
    :param cond_id: int
    :return:
    """

    am = AppManager()
    am.delete_stopping_condition(problem_id, cond_id)
    return 'do some magic!'


def create_site_data(file=None, body=None):
    """uploading a json file with site data
    :param file:
    :type file: str
    :param body:
    :type body: str

    :rtype: object
    """

    title = body.get('title', "")
    app_manager = AppManager()
    return app_manager.create_site_data(file, title)


def delete_problem(problem_id):
    """remove problem

    :param problem_id: Numeric ID to get problem
    :type problem_id: int

    :rtype: None
    """
    app_manager = AppManager()
    return app_manager.delete_problem(problem_id)


def delete_site_data(site_data_id):
    """remove site data
    :param site_data_id: Numeric ID to get site-data
    :type site_data_id: int

    :rtype: None
    """
    app_manager = AppManager()
    return app_manager.delete_site_data(site_data_id=site_data_id)


def edit_crossover_method(body, problem_id):
    """change crossover method for specific problem
    :param body: crossover configuration
    :type body: dict | bytes
    :param problem_id: Numeric ID to get problem
    :type problem_id: int

    :rtype: object
    """
    if connexion.request.is_json:
        body = connexion.request.get_json()
    crossover_id = body['crossover_id']
    crossover_params = body.get('crossover_parameters', dict())

    am = AppManager()
    problem = am.set_crossover_method(problem_id, crossover_id, crossover_params)

    return problem.to_dict_format()


def edit_ea_population_size(body, problem_id):
    """set population size for EA to run
    :param body: size of population
    :type body: dict | bytes
    :param problem_id: Numeric ID to get problem
    :type problem_id: int

    :rtype: object
    """
    if connexion.request.is_json:
        body = connexion.request.get_json()

    population_size = body['population_size']

    am = AppManager()
    problem = am.set_population_size(problem_id, population_size)
    return problem.to_dict_format()


def edit_mutation_method(body, problem_id, mutation_id):
    """change mutation for specific problem

   

    :param body: mutation configuration
    :type body: dict | bytes
    :param problem_id: 
    :type problem_id: int
    :param mutation_id: Numeric ID to get problem
    :type mutation_id: int

    :rtype: object
    """

    raise NotImplementedError("For now supporting only single mutation")


def edit_selection_method(body, problem_id):
    """change selection method for specific problem
    :param body: selection configuration
    :type body: dict | bytes
    :param problem_id: Numeric ID to get problem
    :type problem_id: int

    :rtype: object
    """
    if connexion.request.is_json:
        body = connexion.request.get_json()
    selection_id = body['selection_id']
    selection_params = body.get('selection_parameters', dict())

    am = AppManager()
    problem = am.set_selection_method(problem_id, selection_id, selection_params)

    return problem.to_dict_format()


def set_stopping_condition(body, problem_id, cond_id):
    """set stopping-condition size for EA to run
    :param body: stopping-condition configuration
    :type body: dict | bytes
    :param problem_id: Numeric ID to get problem
    :type problem_id: int
    :param cond_id: Numeric ID to get stopping-condition
    :type cond_id: int

    :rtype: object
    """
    if connexion.request.is_json:
        body = connexion.request.get_json()

    am = AppManager()
    stop_cond = am.set_stopping_condition(problem_id, cond_id, body['bound'])
    return {"stopping_condition": stop_cond}


def get_ea_best_solution(problem_id):
    """get current best solution
    :param problem_id: Numeric ID to get problem
    :type problem_id: int
    :rtype: object
    """
    app_manager = AppManager()
    problem = app_manager.get_problem_by_id(problem_id)
    return problem.get_current_best_solution()


def get_ea_progress(problem_id):
    """get progress according to stopping-conditions for this problem

   

    :param problem_id: Numeric ID to get problem
    :type problem_id: int

    :rtype: object
    """

    app_manager = AppManager()
    return app_manager.get_progress(problem_id)


def get_problem_by_id(problem_id):
    """get problem by id
    :param problem_id: Numeric ID to get problem
    :type problem_id: int

    :rtype: object
    """
    app_manager = AppManager()
    problem = app_manager.get_problem_by_id(problem_id)

    return problem.to_dict_format()


def get_problems():
    """get all problems
    :rtype: object
    """
    app_manager = AppManager()
    return app_manager.problems


def get_site_data_by_id(site_data_id):
    """get site-data of specific id

   

    :param site_data_id: Numeric ID to get site-data
    :type site_data_id: int

    :rtype: object
    """
    return 'do some magic!'


def get_sites_data():
    """get all site-datas



    :rtype: object
    """

    app_manager = AppManager()
    return app_manager.get_site_data()


def remove_mutation(problem_id, mutation_id):
    """remove mutation

   

    :param problem_id: 
    :type problem_id: int
    :param mutation_id: Numeric ID to get mutation
    :type mutation_id: int

    :rtype: None
    """
    raise NotImplementedError("For now supporting only single mutation")


def start_ea(problem_id):
    """start ea for this problem
    :param problem_id: Numeric ID to get problem
    :type problem_id: int

    :rtype: object
    """

    am = AppManager()
    am.start_running(problem_id)
    return "Started"


def stop_ea(problem_id):
    """stop ea for this problem, and clean all results accumulated so far.
    :param problem_id: Numeric ID to get problem
    :type problem_id: int

    :rtype: object
    """
    am = AppManager()
    am.cleanup_problem(problem_id)
    return "Calculation Stopped, data cleansed"


def pause_ea(problem_id):
    """pause ea for this problem
    :param problem_id: Numeric ID to get problem
    :type problem_id: int
    :rtype: object
    """
    am = AppManager()
    am.pause_problem(problem_id)
    return 'Problem calculation paused'


def resume_ea(problem_id):
    """resume ea for this problem
    :param problem_id: Numeric ID to get problem
    :type problem_id: int
    :rtype: object
    """
    am = AppManager()
    am.resume_problem(problem_id)
    return 'Problem calculation resumed'


def update_current_ea_solution(problem_id):
    """manually update solution
    :param problem_id: Numeric ID to get problem
    :type problem_id: int

    :rtype: object
    """
    return 'do some magic!'


def get_fitness_logbook(problem_id):
    """resume ea for this problem
    :param problem_id: Numeric ID to get problem
    :type problem_id: int
    :rtype: object
    """

    am = AppManager()
    problem = am.get_problem_by_id(problem_id)

    return problem.get_fitness_logbook()


def get_fitness_graph(problem_id):
    """resume ea for this problem
    :param problem_id: Numeric ID to get problem
    :type problem_id: int
    :rtype: object
    """

    am = AppManager()
    problem = am.get_problem_by_id(problem_id)
    return problem.get_fitness_graph_as_img()
