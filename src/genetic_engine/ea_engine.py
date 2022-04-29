import logging
import random
from typing import Tuple, Union, Any

import numpy as np
from deap import tools, algorithms, creator, base

from src.genetic_engine.constraints_manager import ConstraintsManager
from src.genetic_engine.ea_conf import RANDOM_SEED, HALL_OF_FAME_SIZE, INVALID_SCHEDULING_PENALTY, \
    HARD_CONSTRAINT_PENALTY, SOFT_CONSTRAINT_PENALTY
from src.genetic_engine.site_manager import SiteManager
from src.genetic_engine.tools.crossover import cxTwoPoint
from src.genetic_engine.tools.mutation import mutFlipBit

logger = logging.getLogger()


class EAEngine:
    def __init__(self, site_manager: SiteManager):
        """order of initialization matters"""
        np.random.seed(RANDOM_SEED)

        self.site_manager = site_manager

        self.logbook = tools.Logbook()

        self.hall_of_fame = tools.HallOfFame(HALL_OF_FAME_SIZE, similar=np.array_equal)

        self.toolbox = base.Toolbox()

        self.stats = self._prepare_statistics_object()

        # define a single objective, maximizing fitness strategy:
        # fixme: maybe need fitness max instead min.
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))

        # prepare fitness evaluation function
        self.toolbox.register("evaluate", self._calculate_fitness)

        self._prepare_individual_creator()

        self._prepare_population_creator()

        self._prepare_genetic_operators()

        self.constraints_manager = ConstraintsManager(site_manager=self.site_manager,
                                                      invalid_scheduling_penalty=INVALID_SCHEDULING_PENALTY,  # INVALID_SCHEDULING_PENALTY,
                                                      hard_constraints_penalty=HARD_CONSTRAINT_PENALTY,
                                                      soft_constraints_penalty=SOFT_CONSTRAINT_PENALTY)

    def _prepare_population_creator(self):
        # create the population operator to generate a list of individuals:
        self.toolbox.register("population_creator", tools.initRepeat, list, self.toolbox.individual_creator)

    def _prepare_individual_creator(self):
        # create the Individual class based on list:
        creator.create("Individual", np.ndarray, fitness=creator.FitnessMin)
        # create the individual operator to fill up an Individual instance:
        self.toolbox.register("individual_creator", self._create_individual)

    def _prepare_genetic_operators(self):
        self.toolbox.register("select", tools.selTournament, tournsize=2)
        self.toolbox.register("mate", cxTwoPoint)
        self.toolbox.register("mutate", mutFlipBit, indpb=1.0 / self.site_manager.get_individual_length())

    def _calculate_fitness(self, individual) -> Tuple[Union[int, Any]]:
        logger.info("in fitness calc")
        production_line_halb_compliance = self.constraints_manager.production_line_halb_compliance(schedule=individual)
        forecast_compliance = self.constraints_manager.overall_forecast_compliance_violations(schedule=individual)
        # sufficient_packaging_material = self.constraints_manager.sufficient_packaging_material(schedule=individual)
        sufficient_packaging_material = 0
        ensure_minimal_transition_time = self.constraints_manager.ensure_minimal_transition_time(schedule=individual)
        regular_hours_exceeded_violations = self.constraints_manager.count_regular_hours_exceeded_violations(schedule=individual)

        invalid_scheduling_violations = production_line_halb_compliance  # sum all invalid violations
        hard_constraints_violations = enforce_products_priority + forecast_compliance + ensure_minimal_transition_time  # sum all hard rules
        soft_constraints_violations = sufficient_packaging_material  # sum all soft rules

        return self.constraints_manager.invalid_scheduling_penalty * invalid_scheduling_violations + \
               self.constraints_manager.hard_constraints_penalty * hard_constraints_violations + \
               self.constraints_manager.soft_constraints_penalty * soft_constraints_violations,

    @staticmethod
    def _prepare_statistics_object():
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("min", np.min)
        stats.register("avg", np.mean)

        return stats

    def _create_individual(self) -> np.ndarray:
        """
        this method creates a valid individual,
        by ensuring there are no multiple products manufactured on a certain line on the same time
        used this thread https://stackoverflow.com/questions/65395919/merging-2d-numpy-arrays-of-different-shapes-to-3d-array
        to merge the results
        """

        # return creator.Individual(np.random.randint(2, size=self.site_manager.get_individual_dimensions()))
        num_product_lines, num_products, num_hours = self.site_manager.get_individual_dimensions()
        production_line_sched_dims = (num_product_lines, num_hours)

        # create 2D manufacturing schedule
        product_line_schedule = np.random.randint(2, size=production_line_sched_dims)
        total_production_schedule = np.zeros(shape=production_line_sched_dims[1], dtype=int)
        for line in product_line_schedule:
            total_production_schedule = total_production_schedule | line

        # create random sequence of product ids to fill the schedule and shuffle their order
        prod_ids = [prod.id for prod in self.site_manager.products]
        random.shuffle(prod_ids)

        # create the 3rd dimension of schedule
        total_ones = total_production_schedule.sum()
        prods_schedule = []

        for prod_id in prod_ids:
            prod_sched = np.zeros(shape=(num_hours,), dtype=int)

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

        individual = np.concatenate([stacked_prods_schedule, product_line_schedule], axis=-1)  # concat together into a 3D array
        individual = np.moveaxis(individual, 0, 1)
        individual = np.moveaxis(individual, 1, 2)  # align dimensions to expected

        individual = individual[:, :-1, :]  # remove last extra layer that was used for concat only
        return creator.Individual(individual)

    def run(self, population_size, num_generations, crossover_probability, mutation_probability, verbose=__debug__):
        """This algorithm is similar to DEAP eaSimple() algorithm, with the modification that
        hall_of_fame is used to implement an elitism mechanism. The individuals contained in the
        hall_of_fame are directly injected into the next generation and are not subject to the
        genetic operators of selection, crossover and mutation.
        """

        population = self.toolbox.population_creator(n=population_size)

        self.logbook.header = ['gen', 'nevals'] + (self.stats.fields if self.stats else [])

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
        self.logbook.record(gen=0, nevals=len(invalid_ind), **record)
        if verbose:
            print(self.logbook.stream)

        # Begin the generational process
        for gen in range(1, num_generations + 1):

            # Select the next generation individuals
            offspring = self.toolbox.select(population, len(population) - hof_size)

            # Vary the pool of individuals
            offspring = algorithms.varAnd(offspring, self.toolbox, crossover_probability, mutation_probability)

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
            self.logbook.record(gen=gen, nevals=len(invalid_ind), **record)
            if verbose:
                print(self.logbook.stream)

        return population

