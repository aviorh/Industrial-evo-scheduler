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

    mutation_id = body['id']
    mutation_params = body['mutation_parameters']

    am = AppManager()
    problem = am.get_problem_by_id(problem_id)

    problem.engine.add_mutation(mutation_id, mutation_params)
    return problem.to_json()


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

    return app_manager.create_problem(site_data_id=site_data_id)


def add_stopping_condition(problem_id, body=None):
    """add new stopping condition
    :param problem_id: Numeric ID to get problem
    :type problem_id: int
    :param body: 
    :type body: dict | bytes

    :rtype: object
    """
    if connexion.request.is_json:
        body = connexion.request.get_json()
    return 'do some magic!'


def create_site_data(file=None):
    """uploading a json file with site data
    :param file:
    :type file: str

    :rtype: object
    """

    app_manager = AppManager()
    return app_manager.create_site_data(file)


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
    crossover_id = body['id']
    crossover_params = body['crossover_parameters']

    am = AppManager()
    problem = am.get_problem_by_id(problem_id)

    problem.engine.set_crossover_method(crossover_id, crossover_params)

    return problem.to_json()


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
    problem = am.get_problem_by_id(problem_id)
    problem.engine.set_population_size(population_size)

    return problem.to_json()


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


def edit_num_ea_generation(body, problem_id):
    """set num of generation for EA to run
    :param body: num generations
    :type body: dict | bytes
    :param problem_id: Numeric ID to get problem
    :type problem_id: int

    :rtype: object
    """
    if connexion.request.is_json:
        body = connexion.request.get_json()

    max_generations = body['generations']

    am = AppManager()
    problem = am.get_problem_by_id(problem_id)
    problem.engine.set_num_generations(max_generations)

    return problem.to_json()


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
    selection_id = body['id']
    selection_params = body['selection_parameters']

    am = AppManager()
    problem = am.get_problem_by_id(problem_id)

    problem.engine.set_selection_method(selection_id, selection_params)

    return problem.to_json()


def edit_stopping_condition(body, problem_id, cond_id):
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
    return 'do some magic!'


def get_ea_best_solution(problem_id):
    """get current best solution

   

    :param problem_id: Numeric ID to get problem
    :type problem_id: int

    :rtype: object
    """
    return 'do some magic!'


def get_ea_progress(problem_id):
    """get progress according to stopping-conditions for this problem

   

    :param problem_id: Numeric ID to get problem
    :type problem_id: int

    :rtype: object
    """
    return 'do some magic!'


def get_problem_by_id(problem_id):
    """get problem by id
    :param problem_id: Numeric ID to get problem
    :type problem_id: int

    :rtype: object
    """
    app_manager = AppManager()
    problem = app_manager.get_problem_by_id(problem_id)

    return problem.to_json()


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
    return 'do some magic!'


def pause_ea(problem_id):
    """pause ea for this problem

   

    :param problem_id: Numeric ID to get problem
    :type problem_id: int

    :rtype: object
    """
    return 'do some magic!'


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
    return 'do some magic!'


def stop_ea(problem_id):
    """stop ea for this problem

   

    :param problem_id: Numeric ID to get problem
    :type problem_id: int

    :rtype: object
    """
    return 'do some magic!'


def update_current_ea_solution(problem_id):
    """manually update solution

   

    :param problem_id: Numeric ID to get problem
    :type problem_id: int

    :rtype: object
    """
    return 'do some magic!'
