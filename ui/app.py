import tkinter as tk
from game.dungeon import rotation_case
from game.engine import tour_aventurier
from game.display import afficher_donjon  # facultatif
from data.levels import level1, dragons_level1, aventurier_start

CELL_SIZE = 100

class WallIsYouApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🧱 Wall Is You")

        # Données de jeu
        self.donjon = [row[:] for row in level1]
        self.aventurier = aventurier_start
        self.dragons = dragons_level1[:]
        self.intention = [(0, 0), (0, 1), (1, 1)]

        # Canvas
        self.canvas = tk.Canvas(root, width=400, height=400, bg="white")
        self.canvas.pack()

        # Bind actions
        self.canvas.bind("<Button-1>", self.on_click)
        self.root.bind("<space>", self.on_space)

        # Premier affichage
        self.draw_dungeon()

    # -------------------------------
    # DESSIN DU DONJON
    # -------------------------------
    def draw_dungeon(self):
        self.canvas.delete("all")
        for i, ligne in enumerate(self.donjon):
            for j, salle in enumerate(ligne):
                x, y = j * CELL_SIZE, i * CELL_SIZE
                self.canvas.create_rectangle(x, y, x + CELL_SIZE, y + CELL_SIZE, outline="black")

                # Murs / portes
                haut, droite, bas, gauche = salle
                if not haut:
                    self.canvas.create_line(x, y, x + CELL_SIZE, y, width=3)
                if not droite:
                    self.canvas.create_line(x + CELL_SIZE, y, x + CELL_SIZE, y + CELL_SIZE, width=3)
                if not bas:
                    self.canvas.create_line(x, y + CELL_SIZE, x + CELL_SIZE, y + CELL_SIZE, width=3)
                if not gauche:
                    self.canvas.create_line(x, y, x, y + CELL_SIZE, width=3)

        # Aventurier
        i, j = self.aventurier[0]
        x, y = j * CELL_SIZE + 50, i * CELL_SIZE + 50
        self.canvas.create_oval(x - 15, y - 15, x + 15, y + 15, fill="blue")
        self.canvas.create_text(x, y, text=str(self.aventurier[1]), fill="white")

        # Dragons
        for pos, level in self.dragons:
            i, j = pos
            x, y = j * CELL_SIZE + 50, i * CELL_SIZE + 50
            self.canvas.create_oval(x - 15, y - 15, x + 15, y + 15, fill="red")
            self.canvas.create_text(x, y, text=str(level), fill="white")

    # -------------------------------
    # INTERACTIONS
    # -------------------------------
    def on_click(self, event):
        """Rotation de la salle cliquée"""
        j = event.x // CELL_SIZE
        i = event.y // CELL_SIZE
        if 0 <= i < len(self.donjon) and 0 <= j < len(self.donjon[0]):
            rotation_case(self.donjon, i, j)
            self.draw_dungeon()

    def on_space(self, event):
        """Tour de l’aventurier"""
        self.aventurier, self.dragons, result = tour_aventurier(
            self.donjon, self.aventurier, self.dragons, self.intention
        )
        self.draw_dungeon()
        self.root.title(result)


# Lancement
if __name__ == "__main__":
    root = tk.Tk()
    app = WallIsYouApp(root)
    root.mainloop()
