# Fonctions centrales du moteur : connexions entre salles, vérification de chemins
# et application simple d'un pas de déplacement le long d'un chemin.

from donjon import rotation_salle

def sont_connectees(donjon, pos1, pos2):
    """
    Renvoie True si pos1 et pos2 sont adjacentes ET reliées (passages ouverts).
    pos = (i, j)
    """
    i1, j1 = pos1
    i2, j2 = pos2
    # Vérifier indices hors bornes -> pas connectées
    lignes = len(donjon)
    colonnes = len(donjon[0]) if lignes > 0 else 0
    if not (0 <= i1 < lignes and 0 <= j1 < colonnes and 0 <= i2 < lignes and 0 <= j2 < colonnes):
        return False

    salle1 = donjon[i1][j1]
    salle2 = donjon[i2][j2]

    # pos2 est à droite
    if i1 == i2 and j2 == j1 + 1:
        return salle1[1] and salle2[3]
    # pos2 est à gauche
    if i1 == i2 and j2 == j1 - 1:
        return salle1[3] and salle2[1]
    # pos2 est en dessous
    if j1 == j2 and i2 == i1 + 1:
        return salle1[2] and salle2[0]
    # pos2 est au-dessus
    if j1 == j2 and i2 == i1 - 1:
        return salle1[0] and salle2[2]

    return False

def chemin_valide(donjon, chemin):
    """
    Vérifie qu'une liste de positions représente un chemin valide (salles adjacentes et connectées).
    chemin : [(i0,j0), (i1,j1), ...]
    Retourne True si la chaîne entière est valide.
    """
    if not chemin:
        return False
    for i in range(len(chemin) - 1):
        a = chemin[i]
        b = chemin[i + 1]
        if not sont_connectees(donjon, a, b):
            return False
    return True

def appliquer_deplacements(aventurier, donjon, chemin, dragons):
    """
    Applique les déplacements de l'aventurier le long du 'chemin' jusqu'au premier
    dragon rencontré ou jusqu'à la fin du chemin.
    - aventurier : [(i,j), niveau] (muté)
    - donjon : pour vérifier connexions
    - chemin : liste de positions (incluant la position de départ de l'aventurier en première pos)
    - dragons : liste mutable de dragons ; si un dragon est tué, on l'enlève et on augmente le niveau
    Retourne un tuple (etat, message) où etat est 'en_cours', 'victoire', ou 'defaite'
    """
    # Vérifier validité du chemin
    if not chemin_valide(donjon, chemin):
        return ('erreur', "Chemin invalide ou discontinuité détectée.")

    # On suppose chemin[0] est la position actuelle de l'aventurier.
    for i in range(1, len(chemin)):  # on avance case par case
        pos = chemin[i]
        aventurier[0] = pos  # déplacer aventurier
        # vérifier s'il y a un dragon ici
        indice = None
        for k, d in enumerate(dragons):
            if d[0] == pos:
                indice = k
                break
        if indice is not None:
            niveau_av = aventurier[1]
            niveau_dr = dragons[indice][1]
            if niveau_av >= niveau_dr:
                # tue le dragon et gagne un niveau
                dragons.pop(indice)
                aventurier[1] += 1
                # le tour de l'aventurier s'arrête après avoir tué un dragon
                if not dragons:
                    return ('victoire', "Tous les dragons sont tués.")
                return ('en_cours', f"Dragon de niveau {niveau_dr} tué. Aventurier niveau {aventurier[1]}.")
            else:
                return ('defaite', f"Aventurier tué par un dragon de niveau {niveau_dr}.")
    return ('en_cours', "Chemin parcouru sans rencontrer de dragon.")

def definir_intention(chemin):
    """
    Définit l'intention de l'aventurier sous forme de liste de positions.
    Exemple :
    >>> definir_intention([(0,0), (0,1), (1,1)])
    [(0,0), (0,1), (1,1)]
    """
    return chemin