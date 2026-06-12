# Représentation du donjon et fonctions de manipulation simples.
# Une salle est un tuple (haut, droite, bas, gauche) de booléens.
# Le donjon est une liste de listes : donjon[i][j] est la salle en ligne i, colonne j.

def rotation_salle(salle):
    """Retourne la salle tournée de 90 degrés dans le sens des aiguilles d'une montre.
    Exemple :
    >>> rotation_salle((True, False, True, False))
    (False, True, False, True)
    """
    haut, droite, bas, gauche = salle
    return (gauche, haut, droite, bas)

def rotation_case(donjon, i, j):
    """
    Tourne la salle en position (i, j) du donjon de 90 degrés dans le sens des aiguilles d'une montre.
    """
    donjon[i][j] = rotation_salle(donjon[i][j])

def creer_donjon_vide(lignes, colonnes, valeur=False):
    """
    Crée un donjon vide de dimensions lignes x colonnes.
    Chaque salle est initialisée avec la valeur donnée (par défaut False).
    """
    salle_vide = (valeur, valeur, valeur, valeur)
    return [[salle_vide for _ in range(colonnes)] for _ in range(lignes)]


if __name__ == "__main__":
    import doctest
    # doctest.testmod()

    donjon = creer_donjon_vide(2, 2)
    donjon[0][0] = (True, False, True, False)
    print("Avant rotation :", donjon[0][0])
    rotation_case(donjon, 0, 0)
    print("Après rotation :", donjon[0][0])