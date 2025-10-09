"""
@file info.py
@brief Rule (not real one) to provide info about the scenario.
"""

from .base import BaseRule


class InfoRule(BaseRule):
    """
    @class InfoRule
    @brief Not really a rule, just return info about the scenario
    """     
    def apply(self, bboxes, page_width, page_height):
        #return info about the scenario
        
        scenario_data = {
            "scenario_name": self.params["label"],
            "author": self.params["author"],
            "description": self.params["description"],
            "date": self.params["date"],
        }
        print(f"==> success => {self.params['label']} - {self.params['author']}  {self.params['date']}.")
        print(f"==> {self.params['description']} ")
        return bboxes
