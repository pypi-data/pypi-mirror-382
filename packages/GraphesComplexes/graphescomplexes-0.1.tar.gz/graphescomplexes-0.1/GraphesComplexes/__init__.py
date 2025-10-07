# __init__.py

from .Fonction import Fonction
from .Graphe import Graphe
from .outils import *
from .fonctions import *

__all__ = [
    # classes et outils
    "Fonction", "Graphe", "eps", "nan2num", "clip", "ln", "hm_ln", "hm_sqrt",
    # fonctions élémentaires
    "id", "inv", "sin", "cos", "exp", "Log",
    # transformations
    "D2H", "H2D",
    # générateurs
    "z_p", "bijD", "bijH",
    "serieDirichlet", "serieDirichletn2",
    # fonctions de test
    "fonctions_test",
    # homeomorphismes
    "homeomorphismes_R",
    # marqueurs
    "marqueIsomod", "marqueIsomodLog", "marqueH", "marqueD", "marqueA",
    "fonctions_marques",
    # conversion couleurs
    "hsl2rgb"
]
