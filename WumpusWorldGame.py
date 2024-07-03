import pygame
import random

GRID_SIZE = 4
CELL_SIZE = 100
WINDOW_SIZE = GRID_SIZE * CELL_SIZE
FPS = 30

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
BLUE = (0, 0, 255)
GRAY = (169, 169, 169)

pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Wumpus World")
clock = pygame.time.Clock()

class Agent:
    def __init__(self):
        self.position = [0, 0]
        self.direction = 'E'
        self.has_gold = False
        self.alive = True
        self.score = 0
        self.arrows = 1
    
    def move_forward(self):
        if self.direction == 'N' and self.position[1] > 0:
            self.position[1] -= 1
        elif self.direction == 'S' and self.position[1] < GRID_SIZE - 1:
            self.position[1] += 1
        elif self.direction == 'E' and self.position[0] < GRID_SIZE - 1:
            self.position[0] += 1
        elif self.direction == 'W' and self.position[0] > 0:
            self.position[0] -= 1
        else:
            self.score -= 1  
        self.score -= 1
    
    def turn_left(self):
        directions = ['N', 'W', 'S', 'E']
        self.direction = directions[(directions.index(self.direction) + 1) % 4]
        self.score -= 1
    
    def turn_right(self):
        directions = ['N', 'E', 'S', 'W']
        self.direction = directions[(directions.index(self.direction) + 1) % 4]
        self.score -= 1
    
    def shoot_arrow(self, world):
        if self.arrows > 0:
            self.arrows -= 1
            self.score -= 10
            # Check if Wumpus is in the direction of the arrow
            w_x, w_y = world.wumpus_position
            a_x, a_y = self.position
            if (self.direction == 'N' and w_x == a_x and w_y < a_y) or \
               (self.direction == 'S' and w_x == a_x and w_y > a_y) or \
               (self.direction == 'E' and w_y == a_y and w_x > a_x) or \
               (self.direction == 'W' and w_y == a_y and w_x < a_x):
                world.wumpus_position = None  # Wumpus is killed
                self.score += 500
                return "Scream"
            return "Missed"
        return "No Arrows Left"
    
    def grab_gold(self, world):
        if world.has_gold(self.position):
            self.has_gold = True
            world.remove_gold()
            self.score += 1000
    
    def is_dead(self):
        return not self.alive

class World:
    def __init__(self):
        self.agent = Agent()
        self.wumpus_position = self.random_position(exclude=[self.agent.position])
        self.gold_position = self.random_position(exclude=[self.agent.position, self.wumpus_position])
        self.pit_positions = [self.random_position(exclude=[self.agent.position, self.wumpus_position, self.gold_position]) for _ in range(3)]
    
    def random_position(self, exclude):
        pos = [random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)]
        while pos in exclude:
            pos = [random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)]
        return pos
    
    def has_gold(self, position):
        return position == self.gold_position
    
    def remove_gold(self):
        self.gold_position = None
    
    def check_pit(self, position):
        return position in self.pit_positions
    
    def check_wumpus(self, position):
        return position == self.wumpus_position
    
    def breeze(self, position):
        return any([abs(position[0] - pit[0]) + abs(position[1] - pit[1]) == 1 for pit in self.pit_positions])
    
    def stench(self, position):
        return abs(position[0] - self.wumpus_position[0]) + abs(position[1] - self.wumpus_position[1]) == 1 if self.wumpus_position else False
    
    def glitter(self, position):
        return position == self.gold_position
    
    def update_agent_state(self):
        if self.check_pit(self.agent.position):
            self.agent.alive = False
            self.agent.score -= 1000
        if self.check_wumpus(self.agent.position):
            self.agent.alive = False
            self.agent.score -= 1000
    
    def game_over(self):
        return not self.agent.alive or (self.agent.has_gold and not self.wumpus_position)

def draw_grid():
    for x in range(0, WINDOW_SIZE, CELL_SIZE):
        for y in range(0, WINDOW_SIZE, CELL_SIZE):
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, (255, 255, 255), rect, 1)

def draw_agent(agent):
    x, y = agent.position
    cx, cy = x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2
    pygame.draw.circle(screen, (0, 0, 255), (cx, cy), CELL_SIZE // 4)
    # Draw direction arrow
    if agent.direction == 'N':
        pygame.draw.line(screen, BLUE, (cx, cy), (cx, cy - CELL_SIZE // 2), 3)
    elif agent.direction == 'S':
        pygame.draw.line(screen, BLUE, (cx, cy), (cx, cy + CELL_SIZE // 2), 3)
    elif agent.direction == 'E':
        pygame.draw.line(screen, BLUE, (cx, cy), (cx + CELL_SIZE // 2, cy), 3)
    elif agent.direction == 'W':
        pygame.draw.line(screen, BLUE, (cx, cy), (cx - CELL_SIZE // 2, cy), 3)

def draw_wumpus(position):
    if position:
        x, y = position
        cx, cy = x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, (0, 0, 0), (cx, cy), CELL_SIZE // 4)

def draw_gold(position, agent_position):
    if position is None:
        return  # Exit early if position is None

    if position == agent_position:
        x, y = position
        cx, cy = x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, (255, 215, 0), (cx, cy), CELL_SIZE // 4)  # Gold color with glitter
    else:
        x, y = position
        cx, cy = x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.rect(screen, BLACK, (cx - CELL_SIZE // 4, cy - CELL_SIZE // 4, CELL_SIZE // 2, CELL_SIZE // 2))

def draw_pits(positions):
    for pos in positions:
        x, y = pos
        cx, cy = x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, (0, 0, 0), (cx, cy), CELL_SIZE // 4)

def display_score(score):
    font = pygame.font.Font(None, 36)
    text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

def display_feedback(feedback):
    font = pygame.font.Font(None, 36)
    text = font.render(feedback, True, (255, 255, 255))
    screen.blit(text, (10, 50))

def display_sensors(world, position):
    font = pygame.font.Font(None, 36)
    messages = []
    if world.breeze(position):
        messages.append("Breeze")
    if world.stench(position):
        messages.append("Stench")
    if world.glitter(position):
        messages.append("Glitter")
    for i, message in enumerate(messages):
        text = font.render(message, True, (255, 255, 255))
        screen.blit(text, (10, 90 + i * 40))

def main():
    level = 1
    while True:
        world = World()
        feedback = ""
        running = True
        while running and not world.game_over():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        world.agent.move_forward()
                        feedback = "Moved Forward"
                    elif event.key == pygame.K_LEFT:
                        world.agent.turn_left()
                        feedback = "Turned Left"
                    elif event.key == pygame.K_RIGHT:
                        world.agent.turn_right()
                        feedback = "Turned Right"
                    elif event.key == pygame.K_SPACE:
                        feedback = world.agent.shoot_arrow(world)
                    elif event.key == pygame.K_g:
                        world.agent.grab_gold(world)
                        feedback = "Grabbed Gold"
        
            world.update_agent_state()
        
            # Drawing
            screen.fill(BLACK)
            draw_grid()
            draw_agent(world.agent)
            draw_wumpus(world.wumpus_position)
            draw_gold(world.gold_position, world.agent.position)
            draw_pits(world.pit_positions)
            display_score(world.agent.score)
            display_feedback(feedback)
            display_sensors(world, world.agent.position)
            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    main()