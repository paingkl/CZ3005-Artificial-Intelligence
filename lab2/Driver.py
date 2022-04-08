from pyswip import Prolog
import random

# Map layouts
# ====================================================================================================
# '#': Wall
# 'W': Wumpus
# 'O': Confundus Portal
# '*': Coin
# '^', '>', 'v', '<': Agent facing North, East, South, West directions
# ' ': Empty (safe)
layout1 = [
    ['#', '#', '#', '#', '#', '#', '#'], 
    ['#', ' ', ' ', ' ', 'O', ' ', '#'], 
    ['#', 'W', '*', 'O', ' ', ' ', '#'], 
    ['#', ' ', ' ', ' ', ' ', ' ', '#'], 
    ['#', '^', ' ', 'O', ' ', ' ', '#'], 
    ['#', '#', '#', '#', '#', '#', '#']
]


# Class representing each map cell of the world
# ====================================================================================================
class MapCell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # Sensory indicators
        self.indicators = {
            'Confounded': 'off', 
            'Stench': 'off', 
            'Tingle': 'off', 
            'Glitter': 'off', 
            'Bump': 'off', 
            'Scream': 'off'
        }
        # Symbol 1: Confounded ('%' for On, '.' for Off)
        # Symbol 2: Stench ('=' for On, '.' for Off)
        # Symbol 3: Tingle ('T' for On, '.' for Off)
        # Symbol 4: '-' if cell contains Agent or NPC else ' '
        # Symbol 5: 
        # 'W' if cell contains (or possibly contains) Wumpus
        # 'O' if cell contains (or possibly contains) Confundus Portal
        # 'U' if cell possibly contains either Wumpus or Confundus Portal
        # '^', '>', 'v', '<': Agent facing North, East, South, West directions
        # 's' for non-visited safe cell (no Agent)
        # 'S' for visited safe cell (no Agent)
        # '?' if none of the above
        # Symbol 6: '-' if cell contains Agent or NPC else ' '
        # Symbol 7: Glitter ('*' for On, '.' for Off)
        # Symbol 8: Bump ('B' for On, '.' for Off)
        # Symbol 9: Scream ('@' for On, '.' for Off)
        self.symbols = {
            '1': '.', 
            '2': '.', 
            '3': '.', 
            '4': ' ', 
            '5': '?', 
            '6': ' ', 
            '7': '.', 
            '8': '.', 
            '9': '.'
        }
        # 3x3 square of symbols
        self.square = [
            [self.symbols['1'], self.symbols['2'], self.symbols['3']], 
            [self.symbols['4'], self.symbols['5'], self.symbols['6']], 
            [self.symbols['7'], self.symbols['8'], self.symbols['9']]
        ]

    def update_square(self):
        self.square = [
            [self.symbols['1'], self.symbols['2'], self.symbols['3']], 
            [self.symbols['4'], self.symbols['5'], self.symbols['6']], 
            [self.symbols['7'], self.symbols['8'], self.symbols['9']]
        ]

    def set_confounded(self):
        self.indicators['Confounded'] = 'on'
        self.symbols['1'] = '%'
        self.update_square()

    def unset_confounded(self):
        self.indicators['Confounded'] = 'off'
        self.symbols['1'] = '.'
        self.update_square()

    def set_stench(self):
        self.indicators['Stench'] = 'on'
        self.symbols['2'] = '='
        self.update_square()

    def unset_stench(self):
        self.indicators['Stench'] = 'off'
        self.symbols['2'] = '.'
        self.update_square()

    def set_tingle(self):
        self.indicators['Tingle'] = 'on'
        self.symbols['3'] = 'T'
        self.update_square()

    def set_inhabited(self):
        self.symbols['4'] = self.symbols['6'] = '-'
        self.update_square()

    def unset_inhabited(self):
        self.symbols['4'] = self.symbols['6'] = ' '
        self.update_square()

    def set_wumpus(self):
        self.symbols['5'] = 'W'
        self.update_square()

    def set_portal(self):
        self.symbols['5'] = 'O'
        self.update_square()
    
    def set_wumpus_or_portal(self):  # For relative map
        self.symbols['5'] = 'U'
        self.update_square()

    def set_north(self):
        self.symbols['5'] = '^'
        self.update_square()

    def set_east(self):
        self.symbols['5'] = '>'
        self.update_square()

    def set_south(self):
        self.symbols['5'] = 'v'
        self.update_square()

    def set_west(self):
        self.symbols['5'] = '<'
        self.update_square()

    def set_unvisited_and_safe(self):
        self.symbols['5'] = 's'
        self.update_square()

    def set_visited_and_safe(self):
        self.symbols['5'] = 'S'
        self.update_square()

    def set_glitter(self):
        self.indicators['Glitter'] = 'on'
        self.symbols['7'] = '*'
        self.update_square()

    def unset_glitter(self):
        self.indicators['Glitter'] = 'off'
        self.symbols['7'] = '.'
        self.update_square()

    def set_bump(self):
        self.indicators['Bump'] = 'on'
        self.symbols['8'] = 'B'
        self.update_square()

    def unset_bump(self):
        self.indicators['Bump'] = 'off'
        self.symbols['8'] = '.'
        self.update_square()
    
    def set_scream(self):
        self.indicators['Scream'] = 'on'
        self.symbols['9'] = '@'
        self.update_square()

    def unset_scream(self):
        self.indicators['Scream'] = 'off'
        self.symbols['9'] = '.'
        self.update_square()

    def set_wall(self):
        for key in self.symbols.keys():
            self.symbols[key] = '#'
        self.update_square()


# Class representing the actual Wumpus World
# ====================================================================================================
class AbsoluteWorld:
    def __init__(self, layout):
        self.reset(layout)

    def reset(self, layout):
        self.width = len(layout[0])  # No. of columns
        self.height = len(layout)    # No. of rows
        self.start_x = None
        self.start_y = None
        self.start_direction = None
        self.wumpus_alive = False    # Wumpus is dead until spawned 
        self.coins_at_start = 0
        # Initialize absolute map with default MapCells first
        self.grid = [[MapCell(j, self.height-1-i) for j in range(self.width)] for i in range(self.height)]  # MapCell(x, y)
        # Update cells based on layout
        for i in range(self.height):
            for j in range(self.width):
                if layout[i][j] == '#':
                    self.grid[i][j].set_wall()
                elif layout[i][j] == 'W':
                    self.spawn_wumpus(i, j)
                elif layout[i][j] == 'O':
                    self.spawn_portal(i, j)
                elif layout[i][j] == '*':
                    self.spawn_coin(i, j)
                elif layout[i][j] == '^':
                    self.spawn_agent(i, j, 'north')
                    self.start_x = j
                    self.start_y = self.height-1-i
                    self.start_direction = 'north'
                elif layout[i][j] == '>':
                    self.spawn_agent(i, j, 'east')
                    self.start_x = j
                    self.start_y = self.height-1-i
                    self.start_direction = 'east'
                elif layout[i][j] == 'v':
                    self.spawn_agent(i, j, 'south')
                    self.start_x = j
                    self.start_y = self.height-1-i
                    self.start_direction = 'south'
                elif layout[i][j] == '<':
                    self.spawn_agent(i, j, 'west')
                    self.start_x = j
                    self.start_y = self.height-1-i
                    self.start_direction = 'west'
                else:
                    self.grid[i][j].set_unvisited_and_safe()

    def print_map(self):
        print('ABSOLUTE MAP: ')
        for i in range(self.height):
            squares = [self.grid[i][j].square for j in range(self.width)]
            for k in range(3):
                rows = [squares[s][k] for s in range(len(squares))]
                for row in rows:
                    print(f'[{"|".join(row)}]', end=' ')
                print()
            print()

    # Utility function to convert x, y positions to row, column indices of absolute map
    def xy_to_rowcol(self, x, y):
        return self.height-1-y, x

    def spawn_wumpus(self, row, col):
        self.grid[row][col].set_wumpus()
        self.grid[row][col].set_inhabited()
        if self.grid[row-1][col].symbols['5'] != '#':
            self.grid[row-1][col].set_stench()
        if self.grid[row+1][col].symbols['5'] != '#':
            self.grid[row+1][col].set_stench()
        if self.grid[row][col-1].symbols['5'] != '#':
            self.grid[row][col-1].set_stench()
        if self.grid[row][col+1].symbols['5'] != '#':
            self.grid[row][col+1].set_stench()
        self.wumpus_alive = True

    def despawn_wumpus(self, row, col):
        self.grid[row][col].unset_inhabited()
        self.grid[row][col].set_unvisited_and_safe()
        if self.grid[row-1][col].symbols['5'] != '#':
            self.grid[row-1][col].unset_stench()
        if self.grid[row+1][col].symbols['5'] != '#':
            self.grid[row+1][col].unset_stench()
        if self.grid[row][col-1].symbols['5'] != '#':
            self.grid[row][col-1].unset_stench()
        if self.grid[row][col+1].symbols['5'] != '#':
            self.grid[row][col+1].unset_stench()
        self.wumpus_alive = False

    def spawn_portal(self, row, col):
        self.grid[row][col].set_portal()
        self.grid[row][col].set_inhabited()
        if self.grid[row-1][col].symbols['5'] != '#':
            self.grid[row-1][col].set_tingle()
        if self.grid[row+1][col].symbols['5'] != '#':
            self.grid[row+1][col].set_tingle()
        if self.grid[row][col-1].symbols['5'] != '#':
            self.grid[row][col-1].set_tingle()
        if self.grid[row][col+1].symbols['5'] != '#':
            self.grid[row][col+1].set_tingle()

    def spawn_coin(self, row, col):
        self.grid[row][col].set_glitter()
        self.grid[row][col].set_inhabited()
        self.grid[row][col].set_unvisited_and_safe()
        self.coins_at_start += 1

    def despawn_coin(self, row, col):
        # Check if coin exists in cell first
        if self.grid[row][col].symbols['7'] == '*':
            self.grid[row][col].unset_glitter()
            return True
        return False

    def spawn_agent(self, row, col, direction):
        if direction == 'north':
            self.grid[row][col].set_north()
        if direction == 'east':
            self.grid[row][col].set_east()
        if direction == 'south':
            self.grid[row][col].set_south()
        if direction == 'west':
            self.grid[row][col].set_west()
        self.grid[row][col].set_inhabited()
        # Confounded indicator is On at the start of the game
        self.grid[row][col].set_confounded()

    def teleport_agent(self):
        safe_xy_positions = []
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j].symbols['5'] == 's' or self.grid[i][j].symbols['5'] == 'S':
                    safe_xy_positions.append((j, self.height-1-i))
        # Randomly choose a safe (x, y) position and a direction
        x, y = random.choice(safe_xy_positions)
        direction = random.choice(['north', 'east', 'south', 'west'])
        # Move Agent to the chosen position
        row, col = self.xy_to_rowcol(x, y)
        self.spawn_agent(row, col, direction)
        return x, y, direction


# Class to simulate Agent's actions and consequences in the world
# ====================================================================================================
class Simulator:
    def __init__(self, abs_world: AbsoluteWorld):
        self.reset(abs_world)

    def reset(self, abs_world: AbsoluteWorld):
        self.abs_world = abs_world
        self.abs_x = abs_world.start_x                  # Agent's absolute x position
        self.abs_y = abs_world.start_y                  # Agent's absolute y position
        self.abs_direction = abs_world.start_direction  # Agent's absolute direction
        self.has_arrow = True
        self.coins_collected = 0

    def move_forward(self):
        # Save Agent's x, y positions and row, column indices on absolute map before the move
        abs_x_s, abs_y_s = self.abs_x, self.abs_y
        row_s, col_s = self.abs_world.xy_to_rowcol(abs_x_s, abs_y_s)

        # Turn transitory indicators Off if they were On previously (i.e., Confounded, Bump, Scream)
        if self.abs_world.grid[row_s][col_s].symbols['1'] == '%':
            self.abs_world.grid[row_s][col_s].unset_confounded()
        if self.abs_world.grid[row_s][col_s].symbols['8'] == 'B':
            self.abs_world.grid[row_s][col_s].unset_bump()
        if self.abs_world.grid[row_s][col_s].symbols['9'] == '@':
            self.abs_world.grid[row_s][col_s].unset_scream()

        if self.abs_direction == 'north':
            # Get row and column indices of one cell ahead on absolute map
            row_d, col_d = self.abs_world.xy_to_rowcol(self.abs_x, self.abs_y+1)
            if self.safe_moveforward(row_s, col_s, row_d, col_d):
                self.abs_y += 1
        elif self.abs_direction == 'east':
            row_d, col_d = self.abs_world.xy_to_rowcol(self.abs_x+1, self.abs_y)
            if self.safe_moveforward(row_s, col_s, row_d, col_d):
                self.abs_x += 1
        elif self.abs_direction == 'south':
            row_d, col_d = self.abs_world.xy_to_rowcol(self.abs_x, self.abs_y-1)
            if self.safe_moveforward(row_s, col_s, row_d, col_d):
                self.abs_y -= 1
        elif self.abs_direction == 'west':
            row_d, col_d = self.abs_world.xy_to_rowcol(self.abs_x-1, self.abs_y)
            if self.safe_moveforward(row_s, col_s, row_d, col_d):
                self.abs_x -= 1

        # Return sensory indicators of cell that Agent is in after the action
        row, col = self.abs_world.xy_to_rowcol(self.abs_x, self.abs_y)
        return list(self.abs_world.grid[row][col].indicators.values())

    def safe_moveforward(self, row_s, col_s, row_d, col_d):
        # row_s, col_s: row and column indices of cell that Agent is currently in
        # row_d, col_d: row and column indices of one cell ahead

        # If next cell is a wall, Agent remains in same cell but Bump indicator is On
        if self.abs_world.grid[row_d][col_d].symbols['5'] == '#':
            self.abs_world.grid[row_s][col_s].set_bump()

        # If next cell is Confundus Portal, teleport Agent
        elif self.abs_world.grid[row_d][col_d].symbols['5'] == 'O':
            self.abs_world.grid[row_s][col_s].set_visited_and_safe()
            # To account for when Agent did not pick up Coin in previous cell
            if self.abs_world.grid[row_s][col_s].symbols['7'] == '.':
                self.abs_world.grid[row_s][col_s].unset_inhabited()
            # Update Agent's position and direction on absolute map after teleporting
            self.abs_x, self.abs_y, self.abs_direction = self.abs_world.teleport_agent()
        
        # If next cell is Wumpus, reset the game
        elif self.abs_world.grid[row_d][col_d].symbols['5'] == 'W':
            self.abs_world.reset(layout1)
            self.reset(wumpus_world)

        # If next cell is safe, Agent moves one cell ahead
        elif self.abs_world.grid[row_d][col_d].symbols['5'] == 's' or self.abs_world.grid[row_d][col_d].symbols['5'] == 'S':
            if self.abs_direction == 'north':
                self.abs_world.grid[row_d][col_d].set_north()
            if self.abs_direction == 'east':
                self.abs_world.grid[row_d][col_d].set_east()
            if self.abs_direction == 'south':
                self.abs_world.grid[row_d][col_d].set_south()
            if self.abs_direction == 'west':
                self.abs_world.grid[row_d][col_d].set_west()
            self.abs_world.grid[row_d][col_d].set_inhabited()
            self.abs_world.grid[row_s][col_s].set_visited_and_safe()
            # To account for when Agent did not pick up Coin in previous cell
            if self.abs_world.grid[row_s][col_s].symbols['7'] == '.':
                self.abs_world.grid[row_s][col_s].unset_inhabited()
            return True

        return False

    def turn_left(self):
        # Get Agent's position on absolute map in terms of row and column indices
        row, col = self.abs_world.xy_to_rowcol(self.abs_x, self.abs_y)

        # Turn transitory indicators Off if they were On previously (i.e., Confounded, Bump, Scream)
        if self.abs_world.grid[row][col].symbols['1'] == '%':
            self.abs_world.grid[row][col].unset_confounded()
        if self.abs_world.grid[row][col].symbols['8'] == 'B':
            self.abs_world.grid[row][col].unset_bump()
        if self.abs_world.grid[row][col].symbols['9'] == '@':
            self.abs_world.grid[row][col].unset_scream()

        if self.abs_direction == 'north':
            self.abs_direction = 'west'
            self.abs_world.grid[row][col].set_west()
        elif self.abs_direction == 'east':
            self.abs_direction = 'north'
            self.abs_world.grid[row][col].set_north()
        elif self.abs_direction == 'south':
            self.abs_direction = 'east'
            self.abs_world.grid[row][col].set_east()
        elif self.abs_direction == 'west':
            self.abs_direction = 'south'
            self.abs_world.grid[row][col].set_south()

        # Return sensory indicators of cell that Agent is in after the action
        return list(self.abs_world.grid[row][col].indicators.values())

    def turn_right(self):
        # Get Agent's position on absolute map in terms of row and column indices
        row, col = self.abs_world.xy_to_rowcol(self.abs_x, self.abs_y)

        # Turn transitory indicators Off if they were On previously (i.e., Confounded, Bump, Scream)
        if self.abs_world.grid[row][col].symbols['1'] == '%':
            self.abs_world.grid[row][col].unset_confounded()
        if self.abs_world.grid[row][col].symbols['8'] == 'B':
            self.abs_world.grid[row][col].unset_bump()
        if self.abs_world.grid[row][col].symbols['9'] == '@':
            self.abs_world.grid[row][col].unset_scream()

        if self.abs_direction == 'north':
            self.abs_direction = 'east'
            self.abs_world.grid[row][col].set_east()
        elif self.abs_direction == 'east':
            self.abs_direction = 'south'
            self.abs_world.grid[row][col].set_south()
        elif self.abs_direction == 'south':
            self.abs_direction = 'west'
            self.abs_world.grid[row][col].set_west()
        elif self.abs_direction == 'west':
            self.abs_direction = 'north'
            self.abs_world.grid[row][col].set_north()

        # Return sensory indicators of cell that Agent is in after the action
        return list(self.abs_world.grid[row][col].indicators.values())

    def pickup_coin(self):
        # Get Agent's position on absolute map in terms of row and column indices
        row, col = self.abs_world.xy_to_rowcol(self.abs_x, self.abs_y)

        # Turn transitory indicators Off if they were On previously (i.e., Confounded, Bump, Scream)
        if self.abs_world.grid[row][col].symbols['1'] == '%':
            self.abs_world.grid[row][col].unset_confounded()
        if self.abs_world.grid[row][col].symbols['8'] == 'B':
            self.abs_world.grid[row][col].unset_bump()
        if self.abs_world.grid[row][col].symbols['9'] == '@':
            self.abs_world.grid[row][col].unset_scream()
        
        if self.abs_world.despawn_coin(row, col):
            self.coins_collected += 1
        
        # Return sensory indicators of cell that Agent is in after the action
        return list(self.abs_world.grid[row][col].indicators.values())

    def shoot_arrow(self):
        # Get Agent's position on absolute map in terms of row and column indices
        row, col = self.abs_world.xy_to_rowcol(self.abs_x, self.abs_y)

        # Turn transitory indicators Off if they were On previously (i.e., Confounded, Bump, Scream)
        if self.abs_world.grid[row][col].symbols['1'] == '%':
            self.abs_world.grid[row][col].unset_confounded()
        if self.abs_world.grid[row][col].symbols['8'] == 'B':
            self.abs_world.grid[row][col].unset_bump()
        if self.abs_world.grid[row][col].symbols['9'] == '@':
            self.abs_world.grid[row][col].unset_scream()

        if self.has_arrow:
            self.has_arrow = False
            wumpus_hit = False
            if self.abs_direction == 'north':
                for i in range(row-1, 0, -1):
                    if self.abs_world.grid[i][col].symbols['5'] == 'W':
                        wumpus_hit = True
                        row_w, col_w = i, col  # Save Wumpus's position on absolute map
            if self.abs_direction == 'south':
                for i in range(row+1, self.abs_world.height-1):
                    if self.abs_world.grid[i][col].symbols['5'] == 'W':
                        wumpus_hit = True
                        row_w, col_w = i, col
            if self.abs_direction == 'east':
                for j in range(col+1, self.abs_world.width-1):
                    if self.abs_world.grid[row][j].symbols['5'] == 'W':
                        wumpus_hit = True
                        row_w, col_w = row, j
            if self.abs_direction == 'west':
                for j in range(col-1, 0, -1):
                    if self.abs_world.grid[row][j].symbols['5'] == 'W':
                        wumpus_hit = True
                        row_w, col_w = row, j
            if wumpus_hit:
                self.abs_world.despawn_wumpus(row_w, col_w)
                self.abs_world.grid[row][col].set_scream()

        # Return sensory indicators of cell that Agent is in after the action
        return list(self.abs_world.grid[row][col].indicators.values())


def onoff_to_name(onoffs):
    names = [('Confounded', 'C'), ('Stench', 'S'), ('Tingle', 'T'), ('Glitter', 'G'), ('Bump', 'B'), ('Scream', 'S')]
    return '-'.join(name[0] if onoff == 'on' else name[1] for name, onoff in zip(names, onoffs))     


# Function to test updates on absolute map
def simulate_absolute_world(world: AbsoluteWorld, sim: Simulator):
    world.print_map()
    menu = 'Next action: (1)moveforward (2)turnleft (3)turnright (4)pickup (5)shoot (6)exit '
    end = False
    while not end:
        print(menu)
        choice = int(input())
        if choice == 1:
            print('moveforward')
            onoffs = sim.move_forward()
            print(onoff_to_name(onoffs))
            print(f'({sim.abs_x},{sim.abs_y}), {sim.abs_direction}')
            world.print_map()
        elif choice == 2:
            print('turnleft')
            onoffs = sim.turn_left()
            print(onoff_to_name(onoffs))
            print(f'({sim.abs_x},{sim.abs_y}), {sim.abs_direction}')
            world.print_map()
        elif choice == 3:
            print('turnright')
            onoffs = sim.turn_right()
            print(onoff_to_name(onoffs))
            print(f'({sim.abs_x},{sim.abs_y}), {sim.abs_direction}')
            world.print_map()
        elif choice == 4:
            print('pickup')
            onoffs = sim.pickup_coin()
            print(onoff_to_name(onoffs))
            print(f'({sim.abs_x},{sim.abs_y}), {sim.abs_direction}')
            world.print_map()
        elif choice == 5:
            print('shoot')
            onoffs = sim.shoot_arrow()
            print(onoff_to_name(onoffs))
            print(f'({sim.abs_x},{sim.abs_y}), {sim.abs_direction}')
            world.print_map()
        elif choice == 6:
            end = True
        else:
            pass
    print(f'Coins spawned: {world.coins_at_start}')
    print(f'Coins collected: {sim.coins_collected}')
    print(f'Wumpus alive? {world.wumpus_alive}')
    print(f'Has arrow? {sim.has_arrow}')


if __name__ == '__main__':
    wumpus_world = AbsoluteWorld(layout1)
    # wumpus_world.print_map()
    simulator = Simulator(wumpus_world)
    simulate_absolute_world(wumpus_world, simulator)
