from src.database.database import db


class SiteData(db.Model):
    __tablename__ = 'sites_data'

    id = db.Column(db.Integer, primary_key=True)
    json_data = db.Column(db.JSON)
    total_working_hours = db.Column(db.Integer)
    num_products = db.Column(db.Integer)
    num_production_lines = db.Column(db.Integer)
    individual_length = db.Column(db.Integer)

class Problem(db.Model):
    __tablename__ = 'problems'

    id = db.Column(db.Integer, primary_key=True)
    site_data_id = db.Column(db.Integer, db.ForeignKey('sites_data.id'), nullable=False)

    site_data = db.relationship('SiteData')
    engine_data = db.Column(db.JSON)


class Solution(db.Model):
    __tablename__ = 'solutions'

    id = db.Column(db.Integer, primary_key=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable=False)
    problem = db.relationship('Problem')

    best_solution = db.Column(db.JSON)
    min_fitness = db.Column(db.JSON)
    average_fitness = db.Column(db.JSON)
