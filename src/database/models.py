from sqlalchemy.ext.mutable import MutableDict

from src.database.database import db


class SiteData(db.Model):
    __tablename__ = 'sites_data'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    json_data = db.Column(db.JSON)
    total_working_hours = db.Column(db.Integer)
    num_products = db.Column(db.Integer)
    num_production_lines = db.Column(db.Integer)
    individual_length = db.Column(db.Integer)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Problem(db.Model):
    __tablename__ = 'problems'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    site_data_id = db.Column(db.Integer, db.ForeignKey('sites_data.id'), nullable=False)

    site_data = db.relationship('SiteData')
    engine_data = db.Column(MutableDict.as_mutable(db.JSON))

    status = db.Column(db.Text, default='idle')
    """
    engine json:
    {
        "site_data_id": int,
        "population_size": int,
        "stopping_conditions_configuration": {
            "TIME_STOPPING_CONDITION": {"applied": False, "bound": 0},
            "FITNESS_STOPPING_CONDITION": {"applied": False, "bound": 0},
            "GENERATIONS_STOPPING_CONDITION": {"applied": True, "bound": DEFAULT_GENERATIONS}
        },
        "selection_method": {"method_id": 1, "params": {"a": "a", "b": "b"}},
        "crossover_method": {"method_id": 1, "params": {"a": "a", "b": "b"}},
        "mutations": [{"mutation_id": 0, "params": {"a": "a", "b": "b"}},
                      {"mutation_id": 1, "params": {"c": "a"}}]
    }
    """


class Solution(db.Model):
    __tablename__ = 'solutions'

    id = db.Column(db.Integer, primary_key=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable=False)
    problem = db.relationship('Problem')

    best_solution = db.Column(db.JSON)
    min_fitness = db.Column(db.JSON)
    average_fitness = db.Column(db.JSON)
