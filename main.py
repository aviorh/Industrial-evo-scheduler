import matplotlib.pyplot as plt
import seaborn as sns

from src.genetic_engine.ea_conf import POPULATION_SIZE, MAX_GENERATIONS, P_CROSSOVER, P_MUTATION
from src.site_data_parser.data_classes import SiteData
from src.genetic_engine.ea_engine import EAEngine
from src.site_data_parser.data_classes import ProductionLine, Product, BulkProduct


def simulate_site_args():
    production_lines = [
        ProductionLine(id=0, productIds={0: 300, 1: 400, 2: 500, 3: 250}, manpower=10, setupTime=1.5, ffo=4),
        ProductionLine(id=1, productIds={0: 800, 1: 250, 3: 450}, manpower=12, setupTime=0.5, ffo=3),
        ProductionLine(id=2, productIds={2: 350}, manpower=6, setupTime=1.0, ffo=5)
    ]
    products = [
        Product(id=0, bulk_id=0, name='Bissli 100g', priority=1, weight=100,
                stock=50, forecast=100, unit_package_id=0, retailer_package_id=0),
        Product(id=1, bulk_id=0, name='Bissli 150g', priority=1, weight=150,
                stock=0, forecast=80, unit_package_id=1, retailer_package_id=1),
        Product(id=2, bulk_id=1, name='Bamba 50g', priority=2, weight=50,
                stock=50, forecast=300, unit_package_id=2, retailer_package_id=2),
        Product(id=3, bulk_id=2, name='Apropo 50g', priority=3, weight=50,
                stock=10, forecast=100, unit_package_id=3, retailer_package_id=3)
    ]
    bulk_products = [
        BulkProduct(id=0, recipeId=0, transitionTime=0.5, productionLineIds=[0, 1]),
        BulkProduct(id=1, recipeId=1, transitionTime=1, productionLineIds=[0, 2]),
        BulkProduct(id=2, recipeId=2, transitionTime=0.5, productionLineIds=[0, 1])
    ]
    total_working_hours = 18 * 5
    num_shifts = 3
    shift_duration = 6
    manpower_per_production_line = {0: 10, 1: 12, 2: 6}
    recipes = {0: {'sugar': 150, 'peanuts': 40}, 1: {'peanuts': 5}, 2: {'muju muju': 53}}
    product_packaging_unit = {0: 230, 1: 130, 2: 100, 3: 100}
    retailer_packaging_unit = {0: (10000, 100), 1: (24000, 50), 2: (2000, 100), 3: (8000, 0)}

    return production_lines, products, bulk_products, total_working_hours, num_shifts, shift_duration, \
           manpower_per_production_line, recipes, product_packaging_unit, retailer_packaging_unit


def prepare_site_manager() -> SiteData:
    production_lines, products, bulk_products, total_working_hours, num_shifts, shift_duration, \
    manpower_per_production_line, recipes, product_packaging_unit, retailer_packaging_unit = simulate_site_args()

    site_data = SiteData(productionLines=production_lines, products=products, bulkProducts=bulk_products,
                    totalWorkingHours=total_working_hours, numShifts=num_shifts, usualStartHour=6,
                    usualEndHour=17, shiftDuration=shift_duration,
                    manpowerPerProductionLine=manpower_per_production_line,
                    recipes=recipes, productPackagingUnit=product_packaging_unit,
                    retailerPackagingUnit=retailer_packaging_unit)

    json_data = site_data.to_dict()
    with open('/Users/avior/Desktop/final-project/Industrial-evo-scheduler/tests/files/site_data.json', 'w', encoding='utf-8') as f:
        ujson.dump(json_data, f, ensure_ascii=False, indent=4)
    return site_data


if __name__ == '__main__':
    site_manager = prepare_site_manager()

    engine = EAEngine(site_manager)

    # show random solution
    random_schedule = engine.toolbox.individual_creator()
    print("-- Random Schedule = ")
    site_manager.print_schedule(random_schedule)

    # run algorithm
    final_population = engine.run()

    # print best solution found:
    best = engine.hall_of_fame.items[0]
    print("-- Best Individual = ", best)
    print("-- Best Fitness = ", best.fitness.values[0])
    print()
    print("-- Schedule = ")
    site_manager.print_schedule(best)
    violation_score = engine.constraints_manager.count_overlaying_manufacturing(schedule=best)
    print(f"-- Violation score = {violation_score}")

    # extract statistics:
    minFitnessValues, meanFitnessValues = engine.logbook.select("min", "avg")

    # plot statistics:
    sns.set_style("whitegrid")
    plt.plot(minFitnessValues, color='red')
    plt.plot(meanFitnessValues, color='green')
    plt.xlabel('Generation')
    plt.ylabel('Min / Average Fitness')
    plt.title('Min and Average fitness over Generations')
    plt.show()
