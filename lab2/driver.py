from pyswip import Prolog

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


class AbsoluteWorld:
    width = 7   # No. of columns
    height = 6  # No. of rows

    def __init__(self):
        self.grid = [[None for j in range(AbsoluteWorld.width)] for i in range(AbsoluteWorld.height)]
        for i in range(AbsoluteWorld.height):
            for j in range(AbsoluteWorld.width):
                self.grid[i][j] = MapCell(j, AbsoluteWorld.height-1-i)  # MapCell(x, y)
                if i == 0 or i == AbsoluteWorld.height-1 or j == 0 or j == AbsoluteWorld.width-1:
                    self.grid[i][j].set_wall()
                else:
                    self.grid[i][j].set_unvisited_and_safe()
        self.has_arrow = True
        self.wumpus_dead = False
        # No. of coins in the world: increment when spawned, decrement when picked up
        self.coin_count = 0

    def print_map(self):
        print('ABSOLUTE MAP: ')
        for i in range(AbsoluteWorld.height):
            squares = [self.grid[i][j].square for j in range(AbsoluteWorld.width)]
            for k in range(3):
                rowlist = [squares[s][k] for s in range(len(squares))]
                for row in rowlist:
                    print(f'[{"|".join(row)}]', end=' ')
                print()
            print()

    def spawn_wumpus(self, x, y):
        i, j = AbsoluteWorld.height-1-y, x
        self.grid[i][j].set_wumpus()
        self.grid[i][j].set_inhabited()
        if i-1 != 0:
            self.grid[i-1][j].set_stench()
        if i+1 != AbsoluteWorld.height-1:
            self.grid[i+1][j].set_stench()
        if j-1 != 0:
            self.grid[i][j-1].set_stench()
        if j+1 != AbsoluteWorld.width-1:
            self.grid[i][j+1].set_stench()

    def despawn_wumpus(self, x, y):
        pass

    def spawn_portal(self, x, y):
        i, j = AbsoluteWorld.height-1-y, x
        self.grid[i][j].set_portal()
        self.grid[i][j].set_inhabited()
        if i-1 != 0:
            self.grid[i-1][j].set_tingle()
        if i+1 != AbsoluteWorld.height-1:
            self.grid[i+1][j].set_tingle()
        if j-1 != 0:
            self.grid[i][j-1].set_tingle()
        if j+1 != AbsoluteWorld.width-1:
            self.grid[i][j+1].set_tingle()

    def spawn_coin(self, x, y):
        i, j = AbsoluteWorld.height-1-y, x
        self.grid[i][j].set_glitter()
        self.grid[i][j].set_inhabited()
        self.coin_count += 1

    def despawn_coin(self, x, y):
        pass

    def spawn_agent(self, x, y, direction):
        i, j = AbsoluteWorld.height-1-y, x
        if direction == 'north':
            self.grid[i][j].set_north()
        if direction == 'west':
            self.grid[i][j].set_west()
        if direction == 'east':
            self.grid[i][j].set_east()
        if direction == 'south':
            self.grid[i][j].set_south()
        self.grid[i][j].set_inhabited()
        # Confounded is On at the start of the game
        self.grid[i][j].set_confounded()

    def move_agent(self):
        pass

    def teleport_agent(self):
        pass

    def pickup_coin(self):
        pass

    def shoot_arrow(self):
        pass


def populate_world(world):
    world.spawn_wumpus(1, 3)
    world.spawn_portal(3, 1)
    world.spawn_portal(3, 3)
    world.spawn_portal(4, 4)
    world.spawn_coin(2, 3)
    world.spawn_agent(1, 1, 'north')


if __name__ == '__main__':
    wumpus_world = AbsoluteWorld()
    populate_world(wumpus_world)
    wumpus_world.print_map()