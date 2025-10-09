
"""
@file core.py
@brief Contient la classe principale pour appliquer des regles sur des bounding boxes.
"""

import json
from agoralib.rules import RULE_CLASSES
from agoralib.rules.utils import flatten_bboxes, rebuild_hierarchy

class BoundingBoxProcessor:
    """
    @class BoundingBoxProcessor
    @brief Gere le chargement, l'application des regles et la sauvegarde des bounding boxes.
    """
    def __init__(self):
        self.bboxes = []
        self.rules = []

    def load_bboxes(self, filename):
        """
        @brief Charge une liste de bounding boxes depuis un fichier JSON.
        @param filename Chemin du fichier JSON.
        """
        with open(filename, 'r') as f:
            self.bboxes = json.load(f)
    
    def display_bboxes(self):

        flat_list = flatten_bboxes(self.bboxes)
        print("=== List of Bounding boxes (flatten) ===")        
        for b in flat_list:
            print(f"id={b['id']}, x={b['x']}, y={b['y']}, w={b['width']}, h={b['height']}, label={b['label']}, parent={b['parent']}")

        print("=== === === === === ===")        


    def load_rules(self, filename):
        """
        @brief Charge les règles de filtrage à partir d’un fichier JSON.
        @param filename Chemin du fichier JSON contenant les règles.
        """    
        with open(filename, 'r') as f:
            rules_json = json.load(f)['rules']
        self.rules = [RULE_CLASSES[rule['rule_type']](rule) for rule in rules_json]

    def apply_rules(self):
        """
        @brief Applique toutes les règles sur la liste de bounding boxes.
        """
        flat = flatten_bboxes(self.bboxes)        
        box = flat[0]
        if box['label']=="page":
            page_w = box['width']
            page_h = box['height']            
        else:
            page_w = 1000
            page_h = 2000
            print("WARNING: Page size missing in the BB list")

        for rule in self.rules:
            print(f" -Try {rule.__class__.__name__} : ")            
            flat = rule.apply(flat,page_w,page_h)  
                
        self.bboxes = rebuild_hierarchy(flat)

    def display_rules(self):
        """
        @brief affiche la liste de regles.
        """ 
        print("=== Current Scenario ===")               
        for rule in self.rules:            
            print(f" - {rule.__class__.__name__} avec params = {rule.params}")
        print("=== === === === === ===")               

    def save_bboxes(self, filename):
        """
        @brief Sauvegarde la liste des bounding boxes après filtrage dans un fichier JSON.
        @param filename Chemin du fichier de sortie.
        """
        with open(filename, 'w') as f:
            json.dump(self.bboxes, f, indent=2)
