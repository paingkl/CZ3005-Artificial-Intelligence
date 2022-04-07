from pyswip import Prolog

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
        # 'W' if cell contains Wumpus
        # 'O' if cell contains Confundus Portal
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
        self.symbols['5'] = 's'
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
        self.coins_left = 0          # Increment when spawned, decrement when picked up
        # Initialize grid map with default MapCells first
        self.grid = [[MapCell(j, self.height-1-i) for j in range(self.width)] for i in range(self.height)]  # MapCell(x, y)
        # Update MapCells based on layout
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

    # Utility function to convert x, y position to row, column index of grid map
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
        self.coins_left += 1

    def despawn_coin(self, row, col):
        # If Confounded and/or Bump indicators were On previously, need to turn them off
        if self.grid[row][col].symbols['1'] == '%':
            self.grid[row][col].unset_confounded()
        if self.grid[row][col].symbols['8'] == 'B':
            self.grid[row][col].unset_bump()

        # Check if coin exists in cell first
        if self.grid[row][col].symbols['7'] == '*':
            self.grid[row][col].unset_glitter()
            self.coins_left -= 1
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

    def move_agent(self):
        pass

    def turn_agent(self, row, col, new_direction):
        # If Confounded and/or Bump indicators were On previously, need to turn them off
        if self.grid[row][col].symbols['1'] == '%':
            self.grid[row][col].unset_confounded()
        if self.grid[row][col].symbols['8'] == 'B':
            self.grid[row][col].unset_bump()

        if new_direction == 'north':
            self.grid[row][col].set_north()
        if new_direction == 'east':
            self.grid[row][col].set_east()
        if new_direction == 'south':
            self.grid[row][col].set_south()
        if new_direction == 'west':
            self.grid[row][col].set_west()

    def teleport_agent(self):
        pass

    def agent_shoots(self, row, col, direction):
        # If Confounded and/or Bump indicators were On previously, need to turn them off
        if self.grid[row][col].symbols['1'] == '%':
            self.grid[row][col].unset_confounded()
        if self.grid[row][col].symbols['8'] == 'B':
            self.grid[row][col].unset_bump()

        wumpus_hit = False
        if direction == 'north':
            for i in range(row-1, 0, -1):
                if self.grid[i][col].symbols['5'] == 'W':
                    wumpus_hit = True
                    row_w, col_w = i, col
        if direction == 'south':
            for i in range(row+1, self.height-1):
                if self.grid[i][col].symbols['5'] == 'W':
                    wumpus_hit = True
                    row_w, col_w = i, col
        if direction == 'east':
            for j in range(col+1, self.width-1):
                if self.grid[row][j].symbols['5'] == 'W':
                    wumpus_hit = True
                    row_w, col_w = row, j
        if direction == 'west':
            for j in range(col-1, 0, -1):
                if self.grid[row][j].symbols['5'] == 'W':
                    wumpus_hit = True
                    row_w, col_w = row, j

        if wumpus_hit:
            self.despawn_wumpus(row_w, col_w)
            self.grid[row][col].set_scream()  # Not sure if at Agent's or Wumpus's position


# Class to simulate Agent's actions and consequences in the world
# ====================================================================================================
class Simulator:
    def __init__(self, abs_world: AbsoluteWorld):
        self.abs_world = abs_world
        self.abs_x = abs_world.start_x                  # Agent's absolute x position
        self.abs_y = abs_world.start_y                  # Agent's absolute y position
        self.abs_direction = abs_world.start_direction  # Agent's absolute direction
        self.has_arrow = True
        self.coins_collected = 0

    def move_forward(self):
        # Save old x and y positions first
        old_abs_x = self.abs_x
        old_abs_y = self.abs_y

        if self.abs_direction == 'north':
            pass
        if self.abs_direction == 'east':
            pass
        if self.abs_direction == 'south':
            pass
        if self.abs_direction == 'west':
            pass

    def turn_left(self):
        if self.abs_direction == 'north':
            self.abs_direction = 'west'
        if self.abs_direction == 'east':
            self.abs_direction = 'north'
        if self.abs_direction == 'south':
            self.abs_direction = 'east'
        if self.abs_direction == 'west':
            self.abs_direction = 'south'
        row, col = self.abs_world.xy_to_rowcol(self.abs_x, self.abs_y)
        self.abs_world.turn_agent(row, col, self.abs_direction)
        return list(self.abs_world.grid[row][col].indicators.values())

    def turn_right(self):
        if self.abs_direction == 'north':
            self.abs_direction = 'east'
        if self.abs_direction == 'east':
            self.abs_direction = 'south'
        if self.abs_direction == 'south':
            self.abs_direction = 'west'
        if self.abs_direction == 'west':
            self.abs_direction = 'north'
        row, col = self.abs_world.xy_to_rowcol(self.abs_x, self.abs_y)
        self.abs_world.turn_agent(row, col, self.abs_direction)
        return list(self.abs_world.grid[row][col].indicators.values())

    def pickup_coin(self):
        row, col = self.abs_world.xy_to_rowcol(self.abs_x, self.abs_y)
        if self.abs_world.despawn_coin(row, col):
            self.coins_collected += 1
        return list(self.abs_world.grid[row][col].indicators.values())

    def shoot_arrow(self):
        row, col = self.abs_world.xy_to_rowcol(self.abs_x, self.abs_y)
        if self.has_arrow:
            self.abs_world.agent_shoots(row, col, self.abs_direction)
            self.has_arrow = False
        return list(self.abs_world.grid[row][col].indicators.values())


if __name__ == '__main__':
    wumpus_world = AbsoluteWorld(layout1)
    wumpus_world.print_map()
