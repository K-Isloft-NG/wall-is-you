# Représentation simple des personnages.
# Un personnage = [(ligne, colonne), niveau]
# L'aventurier commence toujours au niveau 1 (selon le sujet).
# Dragons : liste de personnages.

def creer_personnage(ligne, colonne):
    "Retourne un personnage initialisé à la position (ligne, colonne) et au niveau 1."
    return [(ligne, colonne), 1]

def creer_dragon(ligne, colonne, niveau):
    "Retourne un dragon initialisé à la position (ligne, colonne) et au niveau donné."
    return [(ligne, colonne), niveau]

def trouver_dragon_a_position(dragons, positions):
    """
    Retourne le dragon à la position donnée (ligne, colonne) dans la liste des dragons.
    Si aucun dragon n'est trouvé à cette position, retourne None.
    """
    for dragon in dragons:
        if dragon[0] == positions:
            return dragon
    return None

def tuer_dragon(dragons, indice):
    """
    Supprime le dragon donné de la liste des dragons.
    Modifie la liste en place.
    """
    dragons.pop(indice)


if __name__ == "__main__":
    import doctest
    # doctest.testmod()
    
    p = creer_personnage(0,1)
    d = [creer_dragon(1,0,2), creer_dragon(1,1,3)]
    print(p, d)
    print(trouver_dragon_a_position(d, (1,1)))