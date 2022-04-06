from pyswip import Prolog

# Map layouts
# ====================================================================================================
# '#': Wall
# 'W': Wumpus
# 'O': Confundus Portal
# '*': Coin
# '^', '<', '>', 'v': Agent facing North, West, East, South directions
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
        # '^','<','>','v' for Agent facing North, West, East, South directions
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

    def set_stench(self):
        self.indicators['Stench'] = 'on'
        self.symbols['2'] = '='
        self.update_square()

    def set_tingle(self):
        self.indicators['Tingle'] = 'on'
        self.symbols['3'] = 'T'
        self.update_square()

    def set_inhabited(self):
        self.symbols['4'] = self.symbols['6'] = '-'
        self.update_square()

    def set_empty(self):
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

    def set_west(self):
        self.symbols['5'] = '<'
        self.update_square()

    def set_east(self):
        self.symbols['5'] = '>'
        self.update_square()

    def set_south(self):
        self.symbols['5'] = 'v'
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

    def set_bump(self):
        self.indicators['Bump'] = 'on'
        self.symbols['8'] = 'B'
        self.update_square()
    
    def set_scream(self):
        self.indicators['Scream'] = 'on'
        self.symbols['9'] = '@'
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
        self.has_arrow = True
        self.wumpus_alive = False    # Wumpus is dead until spawned 
        self.coin_count = 0          # Increment when spawned, decrement when picked up
        # Initialize grid with default MapCells first
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
                elif layout[i][j] == '<':
                    self.spawn_agent(i, j, 'west')
                elif layout[i][j] == '>':
                    self.spawn_agent(i, j, 'east')
                elif layout[i][j] == 'v':
                    self.spawn_agent(i, j, 'south')
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

    def spawn_wumpus(self, row, col):
        self.grid[row][col].set_wumpus()
        self.grid[row][col].set_inhabited()
        if row-1 != 0:
            self.grid[row-1][col].set_stench()
        if row+1 != self.height-1:
            self.grid[row+1][col].set_stench()
        if col-1 != 0:
            self.grid[row][col-1].set_stench()
        if col+1 != self.width-1:
            self.grid[row][col+1].set_stench()
        self.wumpus_alive = True

    def despawn_wumpus(self, x, y):
        pass

    def spawn_portal(self, row, col):
        self.grid[row][col].set_portal()
        self.grid[row][col].set_inhabited()
        if row-1 != 0:
            self.grid[row-1][col].set_tingle()
        if row+1 != self.height-1:
            self.grid[row+1][col].set_tingle()
        if col-1 != 0:
            self.grid[row][col-1].set_tingle()
        if col+1 != self.width-1:
            self.grid[row][col+1].set_tingle()

    def spawn_coin(self, row, col):
        self.grid[row][col].set_glitter()
        self.grid[row][col].set_inhabited()
        self.grid[row][col].set_unvisited_and_safe()
        self.coin_count += 1

    def despawn_coin(self, x, y):
        pass

    def spawn_agent(self, row, col, direction):
        if direction == 'north':
            self.grid[row][col].set_north()
        if direction == 'west':
            self.grid[row][col].set_west()
        if direction == 'east':
            self.grid[row][col].set_east()
        if direction == 'south':
            self.grid[row][col].set_south()
        self.grid[row][col].set_inhabited()
        # Confounded is On at the start of the game
        self.grid[row][col].set_confounded()

    def move_agent(self):
        pass

    def teleport_agent(self):
        pass

    def pickup_coin(self):
        pass

    def shoot_arrow(self):
        pass


if __name__ == '__main__':
    wumpus_world = AbsoluteWorld(layout1)
    wumpus_world.print_map()
