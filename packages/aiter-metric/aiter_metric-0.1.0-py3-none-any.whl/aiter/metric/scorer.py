from ..metric.reformulation import create_reformulations
from ..metric.ter_computation import compute_scores

from ..config import MODELS_CONFIG

cols = {"1": ["corrected_hypothesis", "score"], 
        "2": ["filtered_hypothesis", "corrected_hypothesis", "cor_score", "ot_score", "score"]}

class Scorer:
    def __init__(self, df, model, version="3"):
        self.version = version
        self.model = MODELS_CONFIG[model]
        self.df = df
            
    def reformulation(self):
        self.df = create_reformulations(self.df, self.model["name"], self.version)
        return
    
    def scoring(self):
        self.df = compute_scores(self.df, self.version)
        return