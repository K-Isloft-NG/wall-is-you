"""
Script de démonstration de base. Montre la représentation, une rotation, une vérification
de chemin et l'application d'un déplacement.
"""

from donjon import creer_donjon_vide, rotation_case
from personnages import creer_personnage, creer_dragon
from moteur import sont_connectees, chemin_valide, appliquer_deplacements, definir_intention

def exemple():
    # Création d'un donjon 2x2 simple
    # On construit manuellement des salles connectées en ligne droite (ex: (haut, droite, bas, gauche))
    d = [
        [(False, True, True, False), (False, False, True, True)],
        [(True, True, False, False), (True, False, False, True)]
    ]

    # Aventurier en (0,0), dragon en (1,1) niveau 1
    aventurier = [(0,0), 1]
    dragons = [[(1,1), 1]]

    print("Sont (0,0) et (0,1) connectées ?", sont_connectees(d, (0,0), (0,1)))

    # Définir l’intention “manuellement” :
    intention = definir_intention([(0,0), (0,1), (1,1)])
    print("Intention :", intention)

    # Vérifier et appliquer l'intention
    if chemin_valide(d, intention):
        etat, msg = appliquer_deplacements(aventurier, d, intention, dragons)
        print("Résultat du tour :", etat, "-", msg)
    else:
        print("Intention invalide (chemin non connecté)")

    # Définir un chemin du joueur (doit être valide)
    print("Aventurier final :", aventurier)
    print("Dragons restants :", dragons)
    

if __name__ == "__main__":
    exemple()