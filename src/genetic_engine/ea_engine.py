import logging
import random
import threading
import time
from dataclasses import asdict
from typing import Tuple, Union, Any, Dict

import numpy as np
from deap import tools, algorithms, creator, base

from src.app_manager.engine_facade import EAEngineFacade
from src.database.exceptions import ItemNotFoundInDB
from src.exceptions.engine_exceptions import EngineCleanupFailed
from src.genetic_engine.constraints_manager import ConstraintsManager
from src.genetic_engine.ea_conf import RANDOM_SEED, HALL_OF_FAME_SIZE, INVALID_SCHEDULING_PENALTY, \
    HARD_CONSTRAINT_PENALTY, SOFT_CONSTRAINT_PENALTY, POPULATION_SIZE, DEFAULT_GENERATIONS, P_CROSSOVER, P_MUTATION
from src.genetic_engine.stopping_condition import StoppingCondition
from src.database.models import SiteData
from src.genetic_engine.tools.crossover import cxTwoPoint
from src.genetic_engine.tools.mutation import mutFlipBit

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


class EAEngine(threading.Thread):
    SELECTION_METHODS = {
        0: tools.selTournament,
        tools.selTournament.__name__: 0
    }
    CROSSOVER_METHODS = {
        0: cxTwoPoint,
        cxTwoPoint.__name__: 0
    }

    MUTATIONS = {
        0: mutFlipBit,
        mutFlipBit.__name__: 0
    }
    DEFAULT_SELECTION_METHOD_INDEX = 0
    DEFAULT_CROSSOVER_METHOD_INDEX = 0
    DEFAULT_MUTATION_INDEX = 0

    def __init__(self, site_data: SiteData):
        threading.Thread.__init__(self)
        # ~~~~~~ threading related members
        self.terminate_run = False
        self.paused = False
        self.pause_cond = threading.Condition(threading.Lock())

        # ~~~~~~ EA related members (order of initialization matters)
        np.random.seed(RANDOM_SEED)

        self.site_data = site_data

        self.logbook = tools.Logbook()

        self.hall_of_fame = tools.HallOfFame(HALL_OF_FAME_SIZE, similar=np.array_equal)

        self.toolbox = base.Toolbox()

        self.stats = self._prepare_statistics_object()

        # define a single objective, maximizing fitness strategy:
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))

        # prepare fitness evaluation function
        self.toolbox.register("evaluate", self._calculate_fitness)

        self._prepare_individual_creator()

        self._prepare_population_creator()

        self._prepare_genetic_operators()

        self.constraints_manager = ConstraintsManager(db_site_data=site_data,
                                                      invalid_scheduling_penalty=INVALID_SCHEDULING_PENALTY,
                                                      # INVALID_SCHEDULING_PENALTY,
                                                      hard_constraints_penalty=HARD_CONSTRAINT_PENALTY,
                                                      soft_constraints_penalty=SOFT_CONSTRAINT_PENALTY)

        self.set_population_size(size=POPULATION_SIZE)

        self.final_population = None

        self.stopping_conditions_configuration = {
            "TIME_STOPPING_CONDITION": StoppingCondition(applied=False, bound=0),
            "FITNESS_STOPPING_CONDITION": StoppingCondition(applied=False, bound=0),
            "GENERATIONS_STOPPING_CONDITION": StoppingCondition(applied=True, bound=DEFAULT_GENERATIONS)
        }

    def to_dict(self):
        return EAEngineFacade(
            site_data_id=self.site_data.id,
            population_size=self.population_size,
            stopping_conditions_configuration={k: asdict(v) for k, v in self.stopping_conditions_configuration.items()},
            selection_method={"method_id": self.SELECTION_METHODS[self.toolbox.select.func.__name__],
                              "params": self.toolbox.select.keywords},
            crossover_method={"method_id": self.CROSSOVER_METHODS[self.toolbox.mate.func.__name__],
                              "params": self.toolbox.mate.keywords},
            mutations=[{"mutation_id": self.MUTATIONS[self.toolbox.mutate.func.__name__],
                        "params": self.toolbox.mutate.keywords}]
        ).to_dict()

    @staticmethod
    def from_json(json_data):
        site_data_id = json_data['site_data_id']
        site_data: SiteData = SiteData.query.filter_by(id=site_data_id).first()
        if site_data is None:
            raise ItemNotFoundInDB(f"item site_data with id {site_data_id} was not found in DB")

        engine = EAEngine(site_data=site_data)
        engine.set_population_size(json_data['population_size'])
        for cond_id, params in json_data['stopping_conditions_configuration'].items():
            engine.set_stopping_condition(cond_id, bound=params["bound"], force_apply_state=params["applied"])

        engine.set_selection_method(method_id=json_data['selection_method']['method_id'],
                                    params=json_data['selection_method']['params'])
        engine.set_crossover_method(method_id=json_data['crossover_method']['method_id'],
                                    params=json_data['crossover_method']['params'])
        for mutation in json_data['mutations']:
            engine.add_mutation(mutation_id=mutation['mutation_id'],
                                params=mutation['params'])

        return engine

    def set_population_size(self, size):
        self.population_size = size

    def _prepare_population_creator(self):
        # create the population operator to generate a list of individuals:
        self.toolbox.register("population_creator", tools.initRepeat, list, self.toolbox.individual_creator)

    def _prepare_individual_creator(self):
        # create the Individual class based on list:
        creator.create("Individual", np.ndarray, fitness=creator.FitnessMin)
        # create the individual operator to fill up an Individual instance:
        self.toolbox.register("individual_creator", self._create_individual)

    def _prepare_genetic_operators(self):
        self.set_selection_method(self.DEFAULT_SELECTION_METHOD_INDEX, params={'tournsize': 2})
        self.set_crossover_method(self.DEFAULT_CROSSOVER_METHOD_INDEX, params={})
        self.add_mutation(self.DEFAULT_MUTATION_INDEX, params={'indpb': 1.0 / self.site_data.individual_length})

    def _calculate_fitness(self, individual) -> Tuple[Union[int, Any]]:
        production_line_halb_compliance = self.constraints_manager.production_line_halb_compliance(schedule=individual)
        forecast_compliance = self.constraints_manager.overall_forecast_compliance_violations(schedule=individual)
        # sufficient_packaging_material = self.constraints_manager.sufficient_packaging_material(schedule=individual)
        sufficient_packaging_material = 0
        # ensure_minimal_transition_time = self.constraints_manager.ensure_minimal_transition_time(schedule=individual)
        ensure_minimal_transition_time = 0
        regular_hours_exceeded_violations = self.constraints_manager.count_regular_hours_exceeded_violations(
            schedule=individual)

        invalid_scheduling_violations = production_line_halb_compliance  # sum all invalid violations
        hard_constraints_violations = forecast_compliance + ensure_minimal_transition_time  # sum all hard rules
        soft_constraints_violations = sufficient_packaging_material  # sum all soft rules

        return self.constraints_manager.invalid_scheduling_penalty * invalid_scheduling_violations + \
               self.constraints_manager.hard_constraints_penalty * hard_constraints_violations + \
               self.constraints_manager.soft_constraints_penalty * soft_constraints_violations,

    @staticmethod
    def _prepare_statistics_object():
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("min_fitness", np.min)
        stats.register("avg_fitness", np.mean)

        return stats

    def _create_individual(self) -> np.ndarray:
        """
        this method creates a valid individual,
        by ensuring there are no multiple products manufactured on a certain line on the same time
        used this thread https://stackoverflow.com/questions/65395919/merging-2d-numpy-arrays-of-different-shapes-to-3d-array
        to merge the results
        """

        # return creator.Individual(np.random.randint(2, size=self.site_data_list.get_individual_dimensions()))
        production_line_sched_dims = (self.site_data.num_production_lines, self.site_data.total_working_hours)

        # create 2D manufacturing schedule
        product_line_schedule = np.random.randint(2, size=production_line_sched_dims)
        total_production_schedule = np.zeros(shape=production_line_sched_dims[1], dtype=int)
        for line in product_line_schedule:
            total_production_schedule = total_production_schedule | line

        # create random sequence of product ids to fill the schedule and shuffle their order
        prod_ids = [prod["id"] for prod in self.site_data.json_data["products"]]
        random.shuffle(prod_ids)

        # create the 3rd dimension of schedule
        total_ones = total_production_schedule.sum()
        prods_schedule = []

        for prod_id in prod_ids:
            prod_sched = np.zeros(shape=(self.site_data.total_working_hours,), dtype=int)

            if total_ones > 0:  # there are available slots in total schedule
                # randomly choose how many slots this product will take in production
                num_indices_to_take = random.randint(0, total_ones)

                # get all available slots in production
                available_indices = np.where(total_production_schedule == 1)[0]

                # if this is the last product, grant the entire remaining free slots
                if prod_id == prod_ids[-1] and total_ones > 0:
                    indices_to_take = available_indices
                else:
                    # choose random available slots
                    selected = np.random.choice(available_indices.shape[0], num_indices_to_take, replace=False)
                    indices_to_take = available_indices[selected]

                # fill in available slots in schedule for this product
                prod_sched[indices_to_take] = 1

                # remove available slots from total schedule
                total_production_schedule[indices_to_take] = 0
                total_ones -= len(indices_to_take)

            # create a list of product schedules, shuffled
            prods_schedule.append((prod_id, prod_sched))

            # sort the products schedule back in ascending order
            prods_schedule.sort(key=lambda t: t[0])

        for prod_sched in prods_schedule:
            if prod_sched[0] == 0:  # first element
                stacked_prods_schedule = prod_sched[1]
            else:  # stack element with existing stack
                stacked_prods_schedule = np.vstack((stacked_prods_schedule, prod_sched[1]))

        # bring the 2 2D arrays together into a 3D array of shape (num_prod_lines, num_prods, working_hours)
        stacked_prods_schedule = np.moveaxis(stacked_prods_schedule, 0, -1)
        product_line_schedule = np.moveaxis(product_line_schedule, 0, -1)

        stacked_prods_schedule = stacked_prods_schedule[:, None, :]  # expand 1 axis
        product_line_schedule = product_line_schedule[:, :, None]  # expand 1 axis
        stacked_prods_schedule = np.broadcast_to(stacked_prods_schedule,
                                                 (stacked_prods_schedule.shape[0],
                                                  product_line_schedule.shape[1],
                                                  stacked_prods_schedule.shape[2]))

        individual = np.concatenate([stacked_prods_schedule, product_line_schedule],
                                    axis=-1)  # concat together into a 3D array
        individual = np.moveaxis(individual, 0, 1)
        individual = np.moveaxis(individual, 1, 2)  # align dimensions to expected

        individual = individual[:, :-1, :]  # remove last extra layer that was used for concat only
        return creator.Individual(individual)

    def set_selection_method(self, method_id, params: Dict):
        self.toolbox.register("select", self.SELECTION_METHODS[method_id], **params)
        logger.info(f"Selection method changed to {self.SELECTION_METHODS[method_id].__name__}")

    def set_crossover_method(self, method_id, params: Dict):
        # probability is required for the algorithm and not for a specific method
        probability = params.get("probability", None)
        self.crossover_probability = P_CROSSOVER if probability is None else probability
        self.toolbox.register("mate", self.CROSSOVER_METHODS[method_id], **params)
        logger.info(f"Crossover method changed to {self.CROSSOVER_METHODS[method_id].__name__}")

    def add_mutation(self, mutation_id, params: Dict):
        # probability is required for the algorithm and not for a specific method
        probability = params.pop("probability", None)
        self.mutation_probability = P_MUTATION if probability is None else probability
        self.toolbox.register("mutate", self.MUTATIONS[mutation_id], **params)
        logger.info(f"Mutation Added {self.MUTATIONS[mutation_id].__name__}")

    def _perform_single_generation(self, population, gen, hof_size, verbose):
        """Begin single generational process"""
        # Select the next generation individuals
        offspring = self.toolbox.select(population, len(population) - hof_size)

        # Vary the pool of individuals
        offspring = algorithms.varAnd(offspring, self.toolbox, self.crossover_probability, self.mutation_probability)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = self.toolbox.map(self.toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # add the best back to population:
        offspring.extend(self.hall_of_fame.items)

        # Update the hall of fame with the generated individuals
        self.hall_of_fame.update(offspring)

        # Replace the current population by the offspring
        population[:] = offspring

        # Append the current generation statistics to the logbook
        record = self.stats.compile(population) if self.stats else {}
        self.logbook.record(generation=gen, nevals=len(invalid_ind), **record)
        if verbose:
            logger.info(self.logbook.stream)

    def run(self):
        """This algorithm is similar to DEAP eaSimple() algorithm, with the modification that
        hall_of_fame is used to implement an elitism mechanism. The individuals contained in the
        hall_of_fame are directly injected into the next generation and are not subject to the
        genetic operators of selection, crossover and mutation.
        """
        verbose = __debug__
        logger.info("=== RUN STARTED ===")
        logger.info(f"thread {self.ident} started")
        population = self.toolbox.population_creator(n=self.population_size)

        self.logbook.header = ['generation', 'nevals'] + (self.stats.fields if self.stats else [])

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in population if not ind.fitness.valid]
        fitnesses = self.toolbox.map(self.toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        if self.hall_of_fame is None:
            raise ValueError("hall_of_fame parameter must not be empty!")

        self.hall_of_fame.update(population)
        hof_size = len(self.hall_of_fame.items) if self.hall_of_fame.items else 0

        record = self.stats.compile(population) if self.stats else {}
        self.logbook.record(generation=0, nevals=len(invalid_ind), **record)
        if verbose:
            logger.info(self.logbook.stream)

        paused_total_time = 0
        start_time = time.time()
        generation = 1
        cur_fitness = -1
        while not self.should_finish(generation, cur_fitness, time.time() - start_time - paused_total_time):
            cur_fitness = self.hall_of_fame.items[0].fitness.values[0]
            while self.paused:
                paused_time = time.time()
                self.pause_cond.wait()
                self.pause_cond.release()
                if self.terminate_run:
                    logger.info(f"running thread {self.ident} terminated by USER.")
                    exit(0)
                paused_total_time += (time.time() - paused_time)
                logger.info(f'paused total time: {paused_total_time}')

            self._perform_single_generation(population, generation, hof_size, verbose)
            generation += 1

        logger.info("=== RUN FINISHED ===")
        return self.hall_of_fame.items

    def pause(self):
        logger.info(f"thread {self.ident} paused")
        self.pause_cond.acquire()
        # If in sleep, we acquire immediately, otherwise we wait for thread
        # to release condition. In race, worker will still see self.paused
        # and begin waiting until it's set back to False
        self.paused = True

    def resume(self):
        logger.info(f"thread {self.ident} resumed")
        self.pause_cond.acquire()
        self.paused = False
        # Notify so thread will wake after lock released
        self.pause_cond.notify()
        # Now release the lock
        self.pause_cond.release()

    def set_stopping_condition(self, cond_id: str, bound, force_apply_state=None):
        applied = True if force_apply_state is None else force_apply_state
        logger.info(f"Set stopping condition to {cond_id}, bound {bound}")
        self.stopping_conditions_configuration[cond_id] = StoppingCondition(applied=applied, bound=bound)

    def delete_stopping_condition(self, cond_id: str):
        logger.info(f"delete stopping condition {cond_id}")
        self.stopping_conditions_configuration[cond_id] = StoppingCondition(applied=False, bound=0)

    def should_finish(self, generation, fitness, time):
        should_stop = False
        time_cond = self.stopping_conditions_configuration.get("TIME_STOPPING_CONDITION")
        fitness_cond = self.stopping_conditions_configuration.get("FITNESS_STOPPING_CONDITION")
        generations_cond = self.stopping_conditions_configuration.get("GENERATIONS_STOPPING_CONDITION")

        should_stop = should_stop or (
                        time_cond.bound < time and time_cond.applied) or (
                        fitness_cond.bound > fitness and fitness_cond.applied) or (
                        generations_cond.bound < generation and generations_cond.applied)

        self.update_progress(time, fitness, generation)

        return should_stop

    def update_progress(self, time, fitness, generation):
        time_cond = self.stopping_conditions_configuration.get("TIME_STOPPING_CONDITION")
        fitness_cond = self.stopping_conditions_configuration.get("FITNESS_STOPPING_CONDITION")
        generations_cond = self.stopping_conditions_configuration.get("GENERATIONS_STOPPING_CONDITION")

        time_cond.progress = time_cond.bound if time_cond.bound == 0 else round((time / time_cond.bound) * 100, 0)
        generations_cond.progress = generations_cond.bound if generations_cond.bound == 0 \
            else round((generation / generations_cond.bound) * 100, 0)
        fitness_cond.progress = fitness_cond.bound if fitness_cond.bound == 0 else \
            round((1 - (float(fitness) - fitness_cond.bound) / float(fitness)) * 100, 0)

    def notify_run_termination(self):
        self.terminate_run = True
        self.resume()

    def new_engine_from_existing(self):
        new_engine = EAEngine(self.site_data)

        new_engine.set_population_size(self.population_size)
        new_engine.stopping_conditions_configuration = self.stopping_conditions_configuration
        self._reset_run_progression(new_engine.stopping_conditions_configuration)

        new_engine.toolbox = self.toolbox  # all EA parameters are maintained

        return new_engine

    def _reset_run_progression(self, stopping_conditions_configuration):
        for stopping_cond in stopping_conditions_configuration.values():
            stopping_cond.progress = 0