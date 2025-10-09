
"""
@file utils.py
@brief Fonctions utilitaires pour mise en place des RULES et pour manipuler les structures arborescentes de bounding boxes.
"""

import copy

def flatten_bboxes(bboxes, parent_id=None, prefix=""):
    """
    Applatissement d'une liste (ou d'un unique bbox sous forme de dict) de bounding boxes
    en liste plate avec id et parent.
    """
    flat = []

    # Si on reçoit un dict unique (comme la racine), on le transforme en liste pour uniformiser
    if isinstance(bboxes, dict):
        bboxes = [bboxes]

    for i, bbox in enumerate(bboxes):
        bbox_copy = copy.deepcopy(bbox)
        bbox_copy['id'] = f"{prefix}{i}"
        bbox_copy['parent'] = parent_id
        # On enlève temporairement les enfants pour éviter duplication dans la liste plate
        children = bbox_copy.pop('children', None)
        flat.append(bbox_copy)
        if children:
            flat += flatten_bboxes(children, bbox_copy['id'], f"{prefix}{i}_")
        
    return flat


def rebuild_hierarchy(flat):
    """
    Reconstruit la hiérarchie des bounding boxes à partir de la liste plate
    """
    by_id = {box['id']: box for box in flat}
    root = []
    # On vide les listes children existantes pour repartir à zéro
    for box in flat:
        box['children'] = []

    for box in flat:
        if box['parent']:
            parent = by_id.get(box['parent'])
            if parent is not None:
                parent['children'].append(box)
        else:
            root.append(box)

    # remove id and parent
    for box in flat:
        box.pop('id', None)
        box.pop('parent', None)

    return root


def bbox_overlap_metrics(bb1, bb2):
    """
    Calcule les ratios de superposition horizontale et verticale,
    ainsi que les distances minimales entre les bords si pas de recouvrement.
    Args:
        bb1, bb2 (dict): Bounding boxes avec 'x', 'y', 'width', 'height'.
    Returns:
        dict: {
            'x_overlap_ratio': float,
            'y_overlap_ratio': float,
            'x_distance': float,
            'y_distance': float
        }
    """
    x1_min, x1_max = bb1["x"], bb1["x"] + bb1["width"]
    y1_min, y1_max = bb1["y"], bb1["y"] + bb1["height"]
    x2_min, x2_max = bb2["x"], bb2["x"] + bb2["width"]
    y2_min, y2_max = bb2["y"], bb2["y"] + bb2["height"]

    x_overlap = max(0, min(x1_max, x2_max) - max(x1_min, x2_min))
    y_overlap = max(0, min(y1_max, y2_max) - max(y1_min, y2_min))
    #x_union = max(x1_max, x2_max) - min(x1_min, x2_min)
    #y_union = max(y1_max, y2_max) - min(y1_min, y2_min)
    #x_overlap_ratio = x_overlap / x_union
    #y_overlap_ratio = y_overlap / y_union

    # Sur X
    x_length = x1_max - x1_min
    x_overlap_ratio = x_overlap / x_length if x_length > 0 else 0
    # Sur Y
    y_length = y1_max - y1_min
    y_overlap_ratio = y_overlap / y_length if y_length > 0 else 0

    x_distance = max(0, max(x1_min, x2_min) - min(x1_max, x2_max)) if x_overlap == 0 else 0
    y_distance = max(0, max(y1_min, y2_min) - min(y1_max, y2_max)) if y_overlap == 0 else 0

    return {
        "x_overlap_ratio": x_overlap_ratio,
        "y_overlap_ratio": y_overlap_ratio,
        "x_distance": x_distance,
        "y_distance": y_distance
        }



def merge_compatibilty(bb1, bb2, x_thresh, y_thresh, max_dist_x, max_dist_y):
    """
    return true if the 2 BB can be merged :
        => overlapping in x and in y > thresholds in x and y 
        => overlapping in x > x_thresh and dist_y < max_dist_y
        =>  overlapping in y > y_thresh and dist_x < max_dist_x
    """
    # Metrics computation
    m = bbox_overlap_metrics(bb1, bb2)    
 
    x_dist_norm = m["x_distance"] / bb1['width']
    y_dist_norm = m["y_distance"]  / bb1['height']

    # Decision computation
    return (m["x_overlap_ratio"] >= x_thresh and m["y_overlap_ratio"] >= y_thresh
    ) or (
        x_dist_norm < max_dist_x and m["y_overlap_ratio"] > y_thresh
    ) or (
        y_dist_norm < max_dist_y and m["x_overlap_ratio"] > x_thresh
    )
        



