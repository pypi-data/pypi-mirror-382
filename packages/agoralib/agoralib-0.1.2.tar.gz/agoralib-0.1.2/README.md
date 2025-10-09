/**
 * @mainpage agoralib
 *
 * @section description 
 * Cette bibliothèque permet d'appliquer des règles de filtrage sur des bounding boxes arborescentes
 * (issues d'images 2D). Les règles sont définies dans un fichier JSON et permettent de modifier,
 * fusionner, supprimer ou reclasser des régions selon leur position, forme, ou proximité.
 * Les BB doivent etre les enfant/children d'une BBox "page" à ne jamais supprimer. 
 * Cette BB fournit les infos sur l'image de la page a traiter.
 * Les parameètres des regles sont exprimés en % des tailles de la page (pas en pixels)
 *
 * @section usage
 * @code
 * # see main_agoralib.py
 * from agoralib.core import BoundingBoxProcessor
 * processor = BoundingBoxProcessor()
 * processor.load_rules("./samples/FINAL_MODEL_rules2.json")
 * processor.display_rules()
 * processor.load_bboxes("./samples/FINAL_MODEL_bbs.json")
 * processor.display_bboxes()
 * processor.apply_rules()
 * processor.display_bboxes()
 * processor.save_bboxes("./samples/output.json")
 * @endcode
 *
 * @section requirement
 * - detection.py : pseudo-regle qui necessite "pip install opencv-python numpy requests". 
 *   (cette regle crée de nouvelles BB qui remplacent les BB existantes par extraction de composantes connexes)
 *
 *
 * @section structure 
 * - core.py : logique principale de traitement
 * - utils.py : fonctions utilitaires pour gérer les structures
 * - rules/ : contient les implémentations de chaque type de règle
 *
 *
 * @section documentation
 * - detection.py : threshold = seuil de binarisation [1-254] - 0 = Otsu  / areamin = taille mini d'une BB en % surface de la page
 * - info.py : donne info sur le scenario - ne fait rien sur les bB
 * - delete.py : supprime BB selon label (pb si enfant ?)
 * - position.py : position de du centre de la BB avec xmin, xmax en % de largeur de la page - ymin, ymax en % de hauteur de page - si xmax ou ymax = 0.0 => dimension ignorée
 * - shape.py : taille de la BB avec xmin, xmax en % de largeur de la page - ymin, ymax en % de hauteur de page - si xmax ou ymax = 0.0 => dimens
 *              ratio Largeur / Hauteur entre rmin et rmax - ignoré si rmax = 0.0 
 * - proximlity.py : distance bord à bord des BB avec xmin (left) , xmax (right) en % de largeur de la page - ymin (top), ymax (bottom) en % de hauteur de page - avec ratio de superposition > 25% dans l'autre dimension
 *                   (dxleft <= self.params['xmin'] or dxright <= self.params['xmax']) and m["x_overlap_ratio"] >= 0.25 ) or ( (dytop <= self.params['ymin'] or dybottom <= self.params['ymax']) and m["y_overlap_ratio"] >= 0.25 ) :
 * - merge.py : fusion comme enfants d'une nouvelle BB si distance bord à bord des BB avec xmin (left) , xmax (right) en % de largeur de la page - ymin (top), ymax (bottom) en % de hauteur de page - avec ratio de superposition > 25% dans l'autre dimension
 *                   (dxleft <= self.params['xmin'] or dxright <= self.params['xmax']) and m["x_overlap_ratio"] >= 0.25 ) or ( (dytop <= self.params['ymin'] or dybottom <= self.params['ymax']) and m["y_overlap_ratio"] >= 0.25 ) :
 */
