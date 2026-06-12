from game.dungeon import rotation_case, sont_connectees
from game.engine import tour_aventurier
from game.display import afficher_donjon
from data.levels import level1, dragons_level1, aventurier_start

if __name__ == "__main__":
    donjon = [row[:] for row in level1]
    aventurier = aventurier_start
    dragons = dragons_level1[:]

    afficher_donjon(donjon, aventurier, dragons)

    # Tour d'exemple
    rotation_case(donjon, 0, 0)
    afficher_donjon(donjon, aventurier, dragons)

    intention = [(0, 0), (0, 1), (1, 1)]
    aventurier, dragons, result = tour_aventurier(donjon, aventurier, dragons, intention)
    print(result)
