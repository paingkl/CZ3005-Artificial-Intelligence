import random
import sys

from pyswip import Prolog
prolog = Prolog()
prolog.consult('JP-Agent.pl')


# Map layout
# ====================================================================================================
# '#': Wall
# 'W': Wumpus
# 'O': Confundus Portal
# '*': Coin
# '^', '>', 'v', '<': Agent facing North, East, South, West directions
# ' ': Empty (safe)
# Assume Agent will not spawn in the same cell as Coin
layout1 = [
    ['#', '#', '#', '#', '#', '#', '#'], 
    ['#', ' ', ' ', ' ', 'O', ' ', '#'], 
    ['#', 'W', '*', 'O', ' ', ' ', '#'], 
    ['#', ' ', ' ', ' ', ' ', ' ', '#'], 
    ['#', '>', ' ', 'O', ' ', ' ', '#'], 
    ['#', '#', '#', '#', '#', '#', '#']
]


# Class representing each grid map cell of the world
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
        # Sensory indicators of absolute starting position
        self.start_indicators = self.get_start_indicators()

    # Convert absolute x, y to absolute row, column indices
    def xy_to_rowcol(self, x, y):
        return self.height-1-y, x

    def get_start_indicators(self):
        row, col = self.xy_to_rowcol(self.start_x, self.start_y)
        return list(self.grid[row][col].indicators.values())

    def print_map(self):
        for i in range(self.height):
            squares = [self.grid[i][j].square for j in range(self.width)]
            for k in range(3):
                rows = [squares[s][k] for s in range(len(squares))]
                for row in rows:
                    print(f'{" ".join(row)} ', end=' ')
                print()
            print()

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
        # Confounded is On at the start of the game
        self.grid[row][col].set_confounded()

    def teleport_agent(self):
        # Both unvisited and visited cells are considered safe
        safe_xy_positions = []
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j].symbols['5'] == 's' or self.grid[i][j].symbols['5'] == 'S':
                    safe_xy_positions.append((j, self.height-1-i))
        # Randomly choose a safe absolute (x, y) and direction
        x, y = random.choice(safe_xy_positions)
        direction = random.choice(['north', 'east', 'south', 'west'])
        # Move Agent to the chosen position
        row, col = self.xy_to_rowcol(x, y)
        self.spawn_agent(row, col, direction)
        return x, y, direction


# Class representing the world built by Agent using relative knowledge
# ====================================================================================================
class RelativeWorld:
    def __init__(self):
        self.width = 3
        self.height = 3
        self.origin_x = 0
        self.origin_y = 0
        self.origin_direction = 'rnorth'
        # Initialize relative map with default MapCells first
        self.grid = [[MapCell(j-(self.width//2), (self.height//2)-i) for j in range(self.width)] for i in range(self.height)]  # MapCell(x, y)
        self.init_agent()

    # Convert relative row, column indices to relative x, y
    def rowcol_to_xy(self, row, col):
        # Row, column indices of center cell
        row_c = self.height // 2
        col_c = self.width // 2
        return col-col_c, row_c-row

    # Convert relative x, y to relative row, column indices
    def xy_to_rowcol(self, x, y):
        # Row, column indices of center cell
        row_c = self.height // 2
        col_c = self.width // 2
        return row_c-y, col_c+x

    def reset_grid(self):
        self.grid = [[MapCell(j-(self.width//2), (self.height//2)-i) for j in range(self.width)] for i in range(self.height)]  # MapCell(x, y)

    def print_map(self):
        for i in range(self.height):
            squares = [self.grid[i][j].square for j in range(self.width)]
            for k in range(3):
                rows = [squares[s][k] for s in range(len(squares))]
                for row in rows:
                    print(f'{" ".join(row)} ', end=' ')
                print()
            print()

    # Initialize Agent due to reposition(L)
    def init_agent(self):
        # Confirm Agent's ability to reposition via current(X,Y,D)
        # Agent should always return (0, 0) and relative north
        x, y, direction = self.get_agent_position()
        row, col = self.xy_to_rowcol(x, y)
        if direction == 'rnorth':
            self.grid[row][col].set_north()
        if direction == 'reast':
            self.grid[row][col].set_east()
        if direction == 'rsouth':
            self.grid[row][col].set_south()
        if direction == 'rwest':
            self.grid[row][col].set_west()
        self.grid[row][col].set_inhabited()
        # Confounded is On automatically
        self.grid[row][col].set_confounded()
        # Stench, Tingle, Glitter should be queried
        if bool(list(prolog.query(f'stench({x},{y})'))):
            self.grid[row][col].set_stench()
        if bool(list(prolog.query(f'tingle({x},{y})'))):
            self.grid[row][col].set_tingle()
        if bool(list(prolog.query(f'glitter({x},{y})'))):
            self.grid[row][col].set_glitter()

    # Get Agent's current relative position and direction via current(X,Y,D)
    def get_agent_position(self):
        result = list(prolog.query('current(X,Y,D)'))
        if result:
            x = result[0].get('X')
            y = result[0].get('Y')
            direction = result[0].get('D')
            return x, y, direction

    def place_agent(self, row, col, direction):
        if direction == 'rnorth':
            self.grid[row][col].set_north()
        if direction == 'reast':
            self.grid[row][col].set_east()
        if direction == 'rsouth':
            self.grid[row][col].set_south()
        if direction == 'rwest':
            self.grid[row][col].set_west()
        self.grid[row][col].set_inhabited()


# Class to simulate Agent's actions and their consequences in absolute world to generate percepts
# and also to update relative map by querying Agent using localisation and mapping terms
# ====================================================================================================
class Simulator:
    def __init__(self, layout):
        # Initial absolute map layout
        self.abs_layout = layout
        # Flag whether to return sensory indicators
        self.return_indicators = True

        # Absolute world
        self.abs_world = AbsoluteWorld(layout)
        self.abs_x = self.abs_world.start_x                         # Agent's absolute x
        self.abs_y = self.abs_world.start_y                         # Agent's absolute y
        self.abs_direction = self.abs_world.start_direction         # Agent's absolute direction
        self.has_arrow = True
        self.coins_collected = 0

        # Relative world
        self.relative_reposition(self.abs_world.start_indicators)   # Call reposition(L) first
        self.rel_world = RelativeWorld()
        self.rel_x = self.rel_world.origin_x                        # Agent's relative x
        self.rel_y = self.rel_world.origin_y                        # Agent's relative y
        self.rel_direction = self.rel_world.origin_direction        # Agent's relative direction
        self.rel_temp_indicators = None                             # Agent's relative temporary indicators

    # Absolute world related
    # ================================================================================================
    def reset_absolute_world(self):
        self.abs_world = AbsoluteWorld(self.abs_layout)
        self.abs_x = self.abs_world.start_x
        self.abs_y = self.abs_world.start_y
        self.abs_direction = self.abs_world.start_direction
        self.has_arrow = True
        self.coins_collected = 0

    def move_forward(self):
        self.return_indicators = True  # Reset flag
        # Save Agent's absolute x, y and row, column indices before the move
        abs_x_s, abs_y_s = self.abs_x, self.abs_y
        row_s, col_s = self.abs_world.xy_to_rowcol(abs_x_s, abs_y_s)
        # Turn Confounded, Bump and Scream Off if they were On previously
        if self.abs_world.grid[row_s][col_s].symbols['1'] == '%':
            self.abs_world.grid[row_s][col_s].unset_confounded()
        if self.abs_world.grid[row_s][col_s].symbols['8'] == 'B':
            self.abs_world.grid[row_s][col_s].unset_bump()
        if self.abs_world.grid[row_s][col_s].symbols['9'] == '@':
            self.abs_world.grid[row_s][col_s].unset_scream()

        # Update Agent's absolute x, y based on direction
        if self.abs_direction == 'north':
            # Get absolute row, column indices of one cell ahead
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

        row, col = self.abs_world.xy_to_rowcol(self.abs_x, self.abs_y)
        indicators = list(self.abs_world.grid[row][col].indicators.values())
        self.update_rel_temp_indicators(indicators)
        print(onoff_to_name(indicators))

        # Return sensory indicators of cell that Agent is in after the action
        # e.g., [on,off,off,off,off,off] which will be passed as L for move(A,L)
        # However, if reposition(L) was called inside safe_moveforward due to Wumpus/Confundus Portal
        # then return None to differentiate between whether need to call move(A,L) or not
        if self.return_indicators:
            return indicators

    def safe_moveforward(self, row_s, col_s, row_d, col_d):
        # A moveforward is safe only if Agent can move one cell ahead successfully
        # row_s, col_s: Absolute row, column indices of cell Agent is currently in
        # row_d, col_d: Absolute row, column indices of one cell ahead

        # If next cell is a wall, Agent remains in same cell but Bump is On
        if self.abs_world.grid[row_d][col_d].symbols['5'] == '#':
            self.abs_world.grid[row_s][col_s].set_bump()

        # If next cell is Confundus Portal, teleport Agent
        elif self.abs_world.grid[row_d][col_d].symbols['5'] == 'O':
            self.abs_world.grid[row_s][col_s].set_visited_and_safe()
            # To account for when Agent did not pick up Coin in previous cell
            if self.abs_world.grid[row_s][col_s].symbols['7'] == '.':
                self.abs_world.grid[row_s][col_s].unset_inhabited()
            # Update Agent's absolute position and direction after teleporting
            self.abs_x, self.abs_y, self.abs_direction = self.abs_world.teleport_agent()
            # Reset Agent's relative position and direction via reposition(L)
            row, col = self.abs_world.xy_to_rowcol(self.abs_x, self.abs_y)
            indicators_after_teleport = list(self.abs_world.grid[row][col].indicators.values())
            self.reset_relative_world(indicators_after_teleport) # reposition(L) is called here
            # reposition(L) was called so no need to return L for move(A,L)
            self.return_indicators = False
        
        # If next cell is Wumpus, reset the game
        elif self.abs_world.grid[row_d][col_d].symbols['5'] == 'W':
            self.reset_absolute_world()
            self.relative_reborn()  # reborn is called here
            self.reset_relative_world(self.abs_world.start_indicators)  # reposition(L) is called here
            # reposition(L) was called so no need to return L for move(A,L)
            self.return_indicators = False

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
        row, col = self.abs_world.xy_to_rowcol(self.abs_x, self.abs_y)
        # Turn Confounded, Bump and Scream Off if they were On previously
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

        indicators = list(self.abs_world.grid[row][col].indicators.values())
        self.update_rel_temp_indicators(indicators)
        print(onoff_to_name(indicators))

        return indicators

    def turn_right(self):
        row, col = self.abs_world.xy_to_rowcol(self.abs_x, self.abs_y)
        # Turn Confounded, Bump and Scream Off if they were On previously
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

        indicators = list(self.abs_world.grid[row][col].indicators.values())
        self.update_rel_temp_indicators(indicators)
        print(onoff_to_name(indicators))

        return indicators

    def pickup_coin(self):
        row, col = self.abs_world.xy_to_rowcol(self.abs_x, self.abs_y)
        # Turn Confounded, Bump and Scream Off if they were On previously
        if self.abs_world.grid[row][col].symbols['1'] == '%':
            self.abs_world.grid[row][col].unset_confounded()
        if self.abs_world.grid[row][col].symbols['8'] == 'B':
            self.abs_world.grid[row][col].unset_bump()
        if self.abs_world.grid[row][col].symbols['9'] == '@':
            self.abs_world.grid[row][col].unset_scream()
        
        if self.abs_world.despawn_coin(row, col):
            self.coins_collected += 1

        indicators = list(self.abs_world.grid[row][col].indicators.values())
        self.update_rel_temp_indicators(indicators)
        print(onoff_to_name(indicators))
        
        return indicators

    def shoot_arrow(self):
        row, col = self.abs_world.xy_to_rowcol(self.abs_x, self.abs_y)
        # Turn Confounded, Bump and Scream Off if they were On previously
        if self.abs_world.grid[row][col].symbols['1'] == '%':
            self.abs_world.grid[row][col].unset_confounded()
        if self.abs_world.grid[row][col].symbols['8'] == 'B':
            self.abs_world.grid[row][col].unset_bump()
        if self.abs_world.grid[row][col].symbols['9'] == '@':
            self.abs_world.grid[row][col].unset_scream()

        # Let the arrow "fly" only if Agent has it in both absolute and relative world
        # Confirm in relative world by querying hasarrow
        if self.has_arrow and bool(list(prolog.query('hasarrow'))):
            self.has_arrow = False
            wumpus_hit = False
            # Check if Wumpus is present in the arrow's direction
            if self.abs_direction == 'north':
                for i in range(row-1, 0, -1):
                    if self.abs_world.grid[i][col].symbols['5'] == 'W':
                        wumpus_hit = True
                        row_w, col_w = i, col  # Save Wumpus's absolute position
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

        indicators = list(self.abs_world.grid[row][col].indicators.values())
        self.update_rel_temp_indicators(indicators)
        print(onoff_to_name(indicators))
        
        return indicators

    # Decide next action sequence for Agent when it reasons to stay at same cell
    # due to adjacent cells being unsafe during explore(L)
    def get_next_action_sequence(self):
        row, col = self.abs_world.xy_to_rowcol(self.abs_x, self.abs_y)
        # Find a safe adjacent cell for Agent to move to using absolute map knowledge
        # Priority order in checking will be forward, leftward, rightward, backward
        if self.abs_direction == 'north':
            if self.abs_world.grid[row-1][col].symbols['5'] == 's' or self.abs_world.grid[row-1][col].symbols['5'] == 'S':
                return ['moveforward']
            elif self.abs_world.grid[row][col-1].symbols['5'] == 's' or self.abs_world.grid[row][col-1].symbols['5'] == 'S':
                return ['turnleft', 'moveforward']
            elif self.abs_world.grid[row][col+1].symbols['5'] == 's' or self.abs_world.grid[row][col+1].symbols['5'] == 'S':
                return ['turnright', 'moveforward']
            elif self.abs_world.grid[row+1][col].symbols['5'] == 's' or self.abs_world.grid[row+1][col].symbols['5'] == 'S':
                return ['turnleft', 'turnleft', 'moveforward']
        
        if self.abs_direction == 'east':
            if self.abs_world.grid[row][col+1].symbols['5'] == 's' or self.abs_world.grid[row][col+1].symbols['5'] == 'S':
                return ['moveforward']
            elif self.abs_world.grid[row-1][col].symbols['5'] == 's' or self.abs_world.grid[row-1][col].symbols['5'] == 'S':
                return ['turnleft', 'moveforward']
            elif self.abs_world.grid[row+1][col].symbols['5'] == 's' or self.abs_world.grid[row+1][col].symbols['5'] == 'S':
                return ['turnright', 'moveforward']
            elif self.abs_world.grid[row][col-1].symbols['5'] == 's' or self.abs_world.grid[row][col-1].symbols['5'] == 'S':
                return ['turnleft', 'turnleft', 'moveforward']

        if self.abs_direction == 'south':
            if self.abs_world.grid[row+1][col].symbols['5'] == 's' or self.abs_world.grid[row+1][col].symbols['5'] == 'S':
                return ['moveforward']
            elif self.abs_world.grid[row][col+1].symbols['5'] == 's' or self.abs_world.grid[row][col+1].symbols['5'] == 'S':
                return ['turnleft', 'moveforward']
            elif self.abs_world.grid[row][col-1].symbols['5'] == 's' or self.abs_world.grid[row][col-1].symbols['5'] == 'S':
                return ['turnright', 'moveforward']
            elif self.abs_world.grid[row-1][col].symbols['5'] == 's' or self.abs_world.grid[row-1][col].symbols['5'] == 'S':
                return ['turnleft', 'turnleft', 'moveforward']

        if self.abs_direction == 'west':
            if self.abs_world.grid[row][col-1].symbols['5'] == 's' or self.abs_world.grid[row][col-1].symbols['5'] == 'S':
                return ['moveforward']
            elif self.abs_world.grid[row+1][col].symbols['5'] == 's' or self.abs_world.grid[row+1][col].symbols['5'] == 'S':
                return ['turnleft', 'moveforward']
            elif self.abs_world.grid[row-1][col].symbols['5'] == 's' or self.abs_world.grid[row-1][col].symbols['5'] == 'S':
                return ['turnright', 'moveforward']
            elif self.abs_world.grid[row][col+1].symbols['5'] == 's' or self.abs_world.grid[row][col+1].symbols['5'] == 'S':
                return ['turnleft', 'turnleft', 'moveforward']

    # Relative world related
    # ================================================================================================
    def reset_relative_world(self, indicators):
        self.relative_reposition(indicators)
        self.rel_world = RelativeWorld()
        self.rel_x = self.rel_world.origin_x
        self.rel_y = self.rel_world.origin_y
        self.rel_direction = self.rel_world.origin_direction
        self.rel_temp_indicators = None

    def relative_reborn(self):
        list(prolog.query('reborn'))

    def relative_reposition(self, indicators):
        list(prolog.query(f'reposition({indicators})'))

    def update_rel_temp_indicators(self, indicators):
        # [Confounded, Bump, Scream]
        self.rel_temp_indicators = [indicators[i] for i in (0, 4, 5)]

    def update_relative_map(self):
        # Save Agent's relative position and direction (just in case) before the action
        old_rel_x, old_rel_y, old_rel_direction = self.rel_x, self.rel_y, self.rel_direction
        # Update Agent's relative position and direction via current(X,Y,D)
        self.rel_x, self.rel_y, self.rel_direction = self.rel_world.get_agent_position()

        # Consider expanding relative map only if Agent moved by one cell
        if (self.rel_x, self.rel_y) != (old_rel_x, old_rel_y):
            # If one cell ahead of Agent's cell is out of bounds in relative map
            # then it should expand accordingly based on Agent's relative direction
            if self.rel_direction == 'rnorth':
                row, col = self.rel_world.xy_to_rowcol(self.rel_x, self.rel_y+1)
                if row < 0:
                    self.rel_world.height += 2
            if self.rel_direction == 'rsouth':
                row, col = self.rel_world.xy_to_rowcol(self.rel_x, self.rel_y-1)
                if row > self.rel_world.height-1:
                    self.rel_world.height += 2
            if self.rel_direction == 'reast':
                row, col = self.rel_world.xy_to_rowcol(self.rel_x+1, self.rel_y)
                if col > self.rel_world.width-1:
                    self.rel_world.width += 2
            if self.rel_direction == 'rwest':
                row, col = self.rel_world.xy_to_rowcol(self.rel_x-1, self.rel_y)
                if col < 0:
                    self.rel_world.width += 2

        # Reset relative map grid to start from a clean state
        self.rel_world.reset_grid()

        # Update map cells by querying Agent using localisation and mapping terms
        # Using big X and Y, each term will return all relevant relative x, y positions
        # which are then used to update the symbols of each map cell accordingly
        # safe(X,Y)
        # print('safe(X,Y):', end=' ')
        results = sorted(list(prolog.query('safe(X,Y)')), key=lambda d: d['X'])
        for result in results:
            # print(result, end=', ')
            x, y = result.get('X'), result.get('Y')
            row, col = self.rel_world.xy_to_rowcol(x, y)
            self.rel_world.grid[row][col].set_unvisited_and_safe()
        # print()

        # visited(X,Y)
        # print('visited(X,Y):', end=' ')
        results = sorted(list(prolog.query('visited(X,Y)')), key=lambda d: d['X'])
        for result in results:
            # print(result, end=', ')
            x, y = result.get('X'), result.get('Y')
            row, col = self.rel_world.xy_to_rowcol(x, y)
            self.rel_world.grid[row][col].set_visited_and_safe()
        # print()

        # wumpus(X,Y)
        # print('wumpus(X,Y):', end=' ')
        results = sorted(list(prolog.query('wumpus(X,Y)')), key=lambda d: d['X'])
        for result in results:
            # print(result, end=', ')
            x, y = result.get('X'), result.get('Y')
            row, col = self.rel_world.xy_to_rowcol(x, y)
            self.rel_world.grid[row][col].set_wumpus()
            self.rel_world.grid[row][col].set_inhabited()
        # print()

        # confundus(X,Y)
        # print('confundus(X,Y):', end=' ')
        results = sorted(list(prolog.query('confundus(X,Y)')), key=lambda d: d['X'])
        for result in results:
            # print(result, end=', ')
            x, y = result.get('X'), result.get('Y')
            row, col = self.rel_world.xy_to_rowcol(x, y)
            # Check if cell possibly contains Wumpus also
            if self.rel_world.grid[row][col].symbols['5'] == 'W':
                self.rel_world.grid[row][col].set_wumpus_or_portal()
            else:
                self.rel_world.grid[row][col].set_portal()
            self.rel_world.grid[row][col].set_inhabited()
        # print()

        # stench(X,Y)
        # print('stench(X,Y):', end=' ')
        results = sorted(list(prolog.query('stench(X,Y)')), key=lambda d: d['X'])
        for result in results:
            # print(result, end=', ')
            x, y = result.get('X'), result.get('Y')
            row, col = self.rel_world.xy_to_rowcol(x, y)
            self.rel_world.grid[row][col].set_stench()
        # print()

        # tingle(X,Y)
        # print('tingle(X,Y):', end=' ')
        results = sorted(list(prolog.query('tingle(X,Y)')), key=lambda d: d['X'])
        for result in results:
            # print(result, end=', ')
            x, y = result.get('X'), result.get('Y')
            row, col = self.rel_world.xy_to_rowcol(x, y)
            self.rel_world.grid[row][col].set_tingle()
        # print()

        # glitter(X,Y)
        # print('glitter(X,Y):', end=' ')
        results = sorted(list(prolog.query('glitter(X,Y)')), key=lambda d: d['X'])
        for result in results:
            # print(result, end=', ')
            x, y = result.get('X'), result.get('Y')
            row, col = self.rel_world.xy_to_rowcol(x, y)
            self.rel_world.grid[row][col].set_glitter()
            self.rel_world.grid[row][col].set_inhabited()
        # print()

        # wall(X,Y)
        # print('wall(X,Y):', end=' ')
        results = sorted(list(prolog.query('wall(X,Y)')), key=lambda d: d['X'])
        for result in results:
            # print(result, end=', ')
            x, y = result.get('X'), result.get('Y')
            row, col = self.rel_world.xy_to_rowcol(x, y)
            self.rel_world.grid[row][col].set_wall()
        # print()
        # print()

        # Finally, place Agent on relative map
        row, col = self.rel_world.xy_to_rowcol(self.rel_x, self.rel_y)
        self.rel_world.place_agent(row, col, self.rel_direction)
        if self.rel_temp_indicators:
            if self.rel_temp_indicators[0] == 'on':
                self.rel_world.grid[row][col].set_confounded()
            if self.rel_temp_indicators[1] == 'on':
                self.rel_world.grid[row][col].set_bump()
            if self.rel_temp_indicators[2] == 'on':
                self.rel_world.grid[row][col].set_scream()
        else:
            self.rel_world.grid[row][col].set_confounded()


# Class to test correctness of Agent capabilities
# ====================================================================================================
class TestAgent:
    def __init__(self, simulator: Simulator):
        self.simulator = simulator

    # Reset before next correctness test
    def reset(self):
        self.simulator.reset_absolute_world()
        self.simulator.relative_reborn()  # reborn is called here
        self.simulator.reset_relative_world(self.simulator.abs_world.start_indicators)  # reposition(L) is called here

    # Simulate action in absolute world to generate percepts 
    # which are then passed as L in move(A,L) calls to Agent
    def execute_action(self, action):
        print(action)
        if action == 'moveforward':
            indicators = self.simulator.move_forward()
            # If indicators is None means reposition(L) was called inside move_forward()
            # due to Wumpus/Confundus Portal so no need to call move(A,L)
            if indicators:
                list(prolog.query(f'move(moveforward,{indicators})'))
        if action == 'turnleft':
            indicators = self.simulator.turn_left()
            list(prolog.query(f'move(turnleft,{indicators})'))
        if action == 'turnright':
            indicators = self.simulator.turn_right()
            list(prolog.query(f'move(turnright,{indicators})'))
        if action == 'pickup':
            indicators = self.simulator.pickup_coin()
            list(prolog.query(f'move(pickup,{indicators})'))
        if action == 'shoot':
            indicators = self.simulator.shoot_arrow()
            list(prolog.query(f'move(shoot,{indicators})'))
    
    # Test if Agent can correctly represent its relative position on relative map
    def test_localisation_and_mapping(self):
        self.reset()
        print('[Test correctness of Agent\'s localisation and mapping abilities]')
        print('=== ABSOLUTE WORLD ===')
        self.simulator.abs_world.print_map()

        action_sequence = ['moveforward', 'turnleft', 'turnleft', 'moveforward', 
            'turnright', 'moveforward', 'turnright', 'turnright', 'moveforward']
        print(', '.join([str(action) for action in action_sequence]))

        print('=== RELATIVE WORLD ===')
        # Initial relative map
        self.simulator.update_relative_map()
        self.simulator.rel_world.print_map()
        # Subsequent relative maps
        for action in action_sequence:
            self.execute_action(action)
            self.simulator.update_relative_map()
            self.simulator.rel_world.print_map()

    # Test if Agent can correctly absorb and interpret sensory input passed by Driver
    def test_sensory_inference(self):
        self.reset()
        print('[Test correctness of Agent\'s sensory inference]')
        print('=== ABSOLUTE WORLD ===')
        self.simulator.abs_world.print_map()

        action_sequence = ['moveforward', 'turnleft', 'moveforward', 'moveforward', 'pickup', 
            'moveforward', 'turnleft', 'moveforward', 'moveforward', 'turnleft', 'shoot']
        print(', '.join([str(action) for action in action_sequence]))

        print('=== RELATIVE WORLD ===')
        # Initial relative map
        self.simulator.update_relative_map()
        self.simulator.rel_world.print_map()
        # Subsequent relative maps
        for action in action_sequence:
            self.execute_action(action)
            self.simulator.update_relative_map()
            self.simulator.rel_world.print_map()

    # Test if Agent can reset its knowledge base after stepping through Confundus Portal
    def test_confundus_portal(self):
        self.reset()
        print('[Test correctness of Agent\'s memory management after stepping through a Confundus Portal]')
        print('=== ABSOLUTE WORLD ===')
        self.simulator.abs_world.print_map()

        action_sequence = ['moveforward', 'moveforward']
        print(', '.join([str(action) for action in action_sequence]))

        print('=== RELATIVE WORLD ===')
        # Initial relative map
        self.simulator.update_relative_map()
        self.simulator.rel_world.print_map()
        # Subsequent relative maps
        for action in action_sequence:
            self.execute_action(action)
            self.simulator.update_relative_map()
            self.simulator.rel_world.print_map()

        # Print absolute map again after teleport for verification
        print('=== ABSOLUTE WORLD (after teleport) ===')
        self.simulator.abs_world.print_map()

    # Test if Agent can reset its knowledge base for a new game after walking into Wumpus
    def test_end_game_reset(self):
        self.reset()
        print('[Test correctness of Agent\'s end-game reset]')
        print('=== ABSOLUTE WORLD ===')
        self.simulator.abs_world.print_map()

        action_sequence = ['turnleft', 'moveforward', 'moveforward']
        print(', '.join([str(action) for action in action_sequence]))

        print('=== RELATIVE WORLD ===')
        # Initial relative map
        self.simulator.update_relative_map()
        self.simulator.rel_world.print_map()
        # Subsequent relative maps
        for action in action_sequence:
            self.execute_action(action)
            self.simulator.update_relative_map()
            self.simulator.rel_world.print_map()

    # Test correctness of Agent's exploration capabilities
    def test_explore(self):
        self.reset()
        print('[Test correctness of Agent\'s exploration capabilities]')
        print('=== ABSOLUTE WORLD ===')
        self.simulator.abs_world.print_map()

        print('=== RELATIVE WORLD ===')
        # Initial relative map
        self.simulator.update_relative_map()
        self.simulator.rel_world.print_map()

        # Keep calling explore(L) until all coins are collected
        while self.simulator.coins_collected < self.simulator.abs_world.coins_at_start:
            result = list(prolog.query('explore(L)'))
            # print(result)
            suggested_actions = result[0].get('L')
            if suggested_actions:
                for action in suggested_actions:
                    self.execute_action(action)
                    self.simulator.update_relative_map()
                    self.simulator.rel_world.print_map()
            else:
                # If no suggested actions from Agent (i.e., L = [])
                # Driver will force an action sequence (mainly to not let Agent get stuck when surrounded by unsafe cells)
                forced_actions = self.simulator.get_next_action_sequence()
                for action in forced_actions:
                    self.execute_action(action)
                    self.simulator.update_relative_map()
                    self.simulator.rel_world.print_map()

            # Order Agent to pickup if current cell contains a Coin
            if bool(list(prolog.query(f'glitter({self.simulator.rel_x},{self.simulator.rel_y})'))):
                self.execute_action('pickup')
                self.simulator.update_relative_map()
                self.simulator.rel_world.print_map()
        
        # Coin collected, so keep calling explore(L) until Agent returns to Origin
        while (self.simulator.rel_x, self.simulator.rel_y) != (self.simulator.rel_world.origin_x, self.simulator.rel_world.origin_y):
            result = list(prolog.query('explore(L)'))
            suggested_actions = result[0].get('L')
            if suggested_actions:
                for action in suggested_actions:
                    self.execute_action(action)
                    self.simulator.update_relative_map()
                    self.simulator.rel_world.print_map()

            
# Convert the list of on/offs to a string of indicator names
# E.g., [on,off,off,off,off,off] to Confounded-S-T-G-B-S
def onoff_to_name(onoffs):
    names = [('Confounded', 'C'), ('Stench', 'S'), ('Tingle', 'T'), ('Glitter', 'G'), ('Bump', 'B'), ('Scream', 'S')]
    return '-'.join(name[0] if onoff == 'on' else name[1] for name, onoff in zip(names, onoffs))     


if __name__ == '__main__':
    # Filename of Driver printout
    # <team name>-testPrintout-<agent source>-<driver source>.txt
    # Source is either "Self" or "Friend"
    filename = 'JP-testPrintout-Self-Self.txt'  # Change accordingly

    simulator = Simulator(layout1)
    agenttest = TestAgent(simulator)

    temp = sys.stdout
    sys.stdout = open(filename, 'w')
    # Run correctness tests
    agenttest.test_localisation_and_mapping()
    agenttest.test_sensory_inference()
    agenttest.test_confundus_portal()
    agenttest.test_end_game_reset()
    agenttest.test_explore()
    sys.stdout.close()
    sys.stdout = temp
