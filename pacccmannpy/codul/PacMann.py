import pygame
import random
import sys
from collections import deque
from tkinter import Tk, simpledialog

# Init la pygame
pygame.init()

# Constanteee
GRID_SIZE = 20
CELL_SIZE = 30
SCREEN_SIZE = GRID_SIZE * CELL_SIZE
FPS = 10
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

# Start la joc
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("Pac-Man Game")
clock = pygame.time.Clock()

# Definire imagini
ghost_image = pygame.image.load("poze si chestii/ghost.png")
ghost_image = pygame.transform.scale(ghost_image, (CELL_SIZE, CELL_SIZE))
ghost_image.set_colorkey(WHITE)  # delete la alb

pacman_image = pygame.image.load("poze si chestii/pacman.png")
pacman_image = pygame.transform.scale(pacman_image, (CELL_SIZE, CELL_SIZE))
pacman_image.set_colorkey(WHITE)  # delete la alb

# Mazeul
WALLS = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1],
    [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1],
    [1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1],
    [1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1],
    [1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# generare puncte pe harta
def generate_points():
    points = []
    for y in range(len(WALLS)):
        for x in range(len(WALLS[y])):
            if WALLS[y][x] == 0:  
                points.append((x, y))
    return points

all_points = generate_points()
points = []

# intrebarii
intrebari = [
    {"question": "Cat ai pula Arabe?", "answer": "7"},
    {"question": "Cat ai pula Iuliane?", "answer": "7"},
    {"question": "Sunteti roman din tata in fiu", "answer": "DA"},
    {"question": "Cat ai pula Vlade?", "answer": "7"},
    {"question": "Cat ai pula Craciun?", "answer": "7"},
]

class PacMan:
    def __init__(self, position):
        self.start_position = position
        self.position = position
        self.score = 0

    def move(self, direction):
        x, y = self.position
        moves = {
            "UP": (x, max(0, y - 1)),
            "DOWN": (x, min(GRID_SIZE - 1, y + 1)),
            "LEFT": (max(0, x - 1), y),
            "RIGHT": (min(GRID_SIZE - 1, x + 1), y),
        }
        new_position = moves.get(direction, self.position)
        if not is_wall(new_position):
            self.position = new_position

    def reset(self):
        self.position = self.start_position

class Ghost:
    def __init__(self, name, position, behavior="random"):
        self.name = name
        self.start_position = position
        self.position = position
        self.behavior = behavior
        self.move_counter = 0  #viteza pacman

    def move(self, pacman_position):
        self.move_counter += 1
        if self.move_counter % 4 == 0:  # Viteza per frame la fantome
            if self.behavior == "random":
                self.position = self.random_move()
            elif self.behavior == "chase":
                self.position = self.chase_pacman(pacman_position)

    def random_move(self):
        x, y = self.position
        moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(moves)
        for dx, dy in moves:
            new_position = (x + dx, y + dy)
            if not is_wall(new_position):
                return new_position
        return self.position

    def chase_pacman(self, pacman_position):
        # BFS pt hunt mode
        path = self.bfs(self.position, pacman_position)
        if len(path) > 1:
            return path[1]  # urmatoarea miscare
        return self.position

    def bfs(self, start, target):
        queue = deque([start])
        visited = set([start])
        parent = {start: None}

        while queue:
            current = queue.popleft()
            if current == target:
                break

            x, y = current
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = (x + dx, y + dy)
                if neighbor not in visited and not is_wall(neighbor):
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)

        # Redefinire path de cautare
        path = []
        while target and target in parent:
            path.append(target)
            target = parent[target]
        return path[::-1]  # Daca nu se gaseste inverseaza path ul si cauta iar

    def reset(self):
        self.position = self.start_position

def is_wall(position):
    x, y = position
    if y < 0 or y >= len(WALLS) or x < 0 or x >= len(WALLS[0]):
        return True  # in cazul in care se iese din labirint e lfl ca la perete
    return WALLS[y][x] == 1

def draw_grid():
    for y in range(len(WALLS)):
        for x in range(len(WALLS[y])):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if WALLS[y][x] == 1:
                pygame.draw.rect(screen, BLUE, rect)
            else:
                pygame.draw.rect(screen, WHITE, rect, 1)

def draw_entity(image, position):
    rect = pygame.Rect(
        position[0] * CELL_SIZE,
        position[1] * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE,
    )
    screen.blit(image, rect.topleft)

def handle_input(pacman):
    keys = pygame.key.get_pressed()
    directions = {
        pygame.K_UP: "UP",
        pygame.K_DOWN: "DOWN",
        pygame.K_LEFT: "LEFT",
        pygame.K_RIGHT: "RIGHT",
    }
    for key, direction in directions.items():
        if keys[key]:
            pacman.move(direction)

def check_collision(pacman, ghosts):
    for ghost in ghosts:
        if pacman.position == ghost.position:
            return ghost
    return None

def ask_question():
    root = Tk()
    root.withdraw()  # Pornire fereastra de intreabare

    # Se centreaza fereastra(Nu merge)
    root.geometry(f"300x200+{screen.get_width() // 2 - 150}+{screen.get_height() // 2 - 100}")

    # Random la intreabari
    question = random.choice(intrebari)
    answer = simpledialog.askstring("Math Question", question["question"])
    root.destroy()
    return answer, question["answer"]

def check_points(pacman):
    global points
    if pacman.position in points:
        points.remove(pacman.position)
        pacman.score += 1

def draw_points():
    for point in points:
        rect = pygame.Rect(
            point[0] * CELL_SIZE + CELL_SIZE // 3,
            point[1] * CELL_SIZE + CELL_SIZE // 3,
            CELL_SIZE // 3,
            CELL_SIZE // 3,
        )
        pygame.draw.ellipse(screen, YELLOW, rect)

def draw_score(score):
    font = pygame.font.Font(None, 36)
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (10, 10))

def spawn_points():
    if len(all_points) > 0 and len(points) < 10:  # Maximul de puncte pe mapa in fiecare secunda
        new_point = random.choice(all_points)
        all_points.remove(new_point)
        points.append(new_point)

def main():
    pacman = PacMan((1, 1))
    ghosts = [
        Ghost("Un negru", (18, 1), behavior="chase"),
        Ghost("Al doilea negru", (10, 10), behavior="random"), 
    ]

    running = True
    while running:
        screen.fill(BLACK)
        draw_grid()
        draw_points()
        draw_score(pacman.score)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        handle_input(pacman)
        check_points(pacman)
        spawn_points()

        for ghost in ghosts:
            ghost.move(pacman.position)

        collided_ghost = check_collision(pacman, ghosts)
        if collided_ghost:
            answer, correct_answer = ask_question()
            if answer == correct_answer:
                collided_ghost.reset()
            else:
                pacman.reset()
                for ghost in ghosts:
                    ghost.reset()

        draw_entity(pacman_image, pacman.position) 
        for ghost in ghosts:
            draw_entity(ghost_image, ghost.position) 

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
