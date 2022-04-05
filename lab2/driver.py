class MapCell:
    def __init__(self, x, y):
        self.xpos = x
        self.ypos = y
        self.confounded = '.'   # '%' for On, '.' for Off
        self.stench = '.'       # '=' for On, '.' for Off
        self.tingle = '.'       # 'T' for On, '.' for Off
        self.symbol4 = ' '      # '-' if cell contains Agent or NPC else ' '

        # 'W' if cell contains Wumpus
        # 'O' if cell contains Confundus Portal
        # '^','<','>','v' for Agent facing North, West, East, South directions
        # 's' for non-visited safe cell (no Agent)
        # 'S' for visited safe cell (no Agent)
        # '?' if none of the above
        self.symbol5 = '?'

        self.symbol6 = ' '      # '-' if cell contains Agent or NPC else ' '
        self.glitter = '.'      # '*' for On, '.' for Off
        self.bump = '.'         # 'B' for On, '.' for Off
        self.scream = '.'       # '@' for On, '.' for Off

        # Symbols square
        # [1, 2, 3]
        # [4, 5, 6]
        # [7, 8, 9]
        self.square = [
            [self.confounded, self.stench, self.tingle], 
            [self.symbol4, self.symbol5, self.symbol6], 
            [self.glitter, self.bump, self.scream]
        ]

    def update_square(self):
        self.square = [
            [self.confounded, self.stench, self.tingle], 
            [self.symbol4, self.symbol5, self.symbol6], 
            [self.glitter, self.bump, self.scream]
        ]

    def set_confounded(self):
        self.confounded = '%'
        self.update_square()

    def set_stench(self):
        self.stench = '='
        self.update_square()

    def set_tingle(self):
        self.tingle = 'T'
        self.update_square()

    def set_inhabited(self):
        self.symbol4 = '-'
        self.symbol6 = '-'
        self.update_square()

    def set_wumpus(self):
        self.symbol5 = 'W'
        self.update_square()

    def set_portal(self):
        self.symbol5 = 'O'
        self.update_square()

    def set_north(self):
        self.symbol5 = '^'
        self.update_square()

    def set_west(self):
        self.symbol5 = '<'
        self.update_square()

    def set_east(self):
        self.symbol5 = '>'
        self.update_square()

    def set_south(self):
        self.symbol5 = 'v'
        self.update_square()

    def set_unvisited(self):
        self.symbol5 = 's'
        self.update_square()

    def set_visited(self):
        self.symbol5 = 'S'
        self.update_square()

    def set_glitter(self):
        self.glitter = '*'
        self.update_square()

    def set_bump(self):
        self.bump = 'B'
        self.update_square()
    
    def set_scream(self):
        self.scream = '@'
        self.update_square()

    def set_wall(self):
        self.confounded = self.stench = self.tingle = self.symbol4 = self.symbol5 = self.symbol6 = self.glitter = self.bump = self.scream = '#'
        self.update_square()


class AbsoluteMap:
    width = 7   # No. of columns
    height = 6  # No. of rows

    def __init__(self):
        self.grid = [[None for j in range(AbsoluteMap.width)] for i in range(AbsoluteMap.height)]
        for i in range(AbsoluteMap.height):
            for j in range(AbsoluteMap.width):
                self.grid[i][j] = MapCell(j, AbsoluteMap.height-1-i)  # MapCell(x, y)
                if i == 0 or i == AbsoluteMap.height-1 or j == 0 or j == AbsoluteMap.width-1:
                    self.grid[i][j].set_wall()

    def place_wumpus(self, x, y):
        i, j = AbsoluteMap.height-1-y, x
        self.grid[i][j].set_wumpus()
        self.grid[i][j].set_inhabited()
        if i-1 != 0:
            self.grid[i-1][j].set_stench()
        if i+1 != AbsoluteMap.height-1:
            self.grid[i+1][j].set_stench()
        if j-1 != 0:
            self.grid[i][j-1].set_stench()
        if j+1 != AbsoluteMap.width-1:
            self.grid[i][j+1].set_stench()

    def place_portal(self, x, y):
        i, j = AbsoluteMap.height-1-y, x
        self.grid[i][j].set_portal()
        self.grid[i][j].set_inhabited()
        if i-1 != 0:
            self.grid[i-1][j].set_tingle()
        if i+1 != AbsoluteMap.height-1:
            self.grid[i+1][j].set_tingle()
        if j-1 != 0:
            self.grid[i][j-1].set_tingle()
        if j+1 != AbsoluteMap.width-1:
            self.grid[i][j+1].set_tingle()

    def place_coin(self, x, y):
        i, j = AbsoluteMap.height-1-y, x
        self.grid[i][j].set_glitter()
        self.grid[i][j].set_inhabited()

    def print_map(self):
        print('ABSOLUTE MAP: ')
        for i in range(AbsoluteMap.height):
            squares = [self.grid[i][j].square for j in range(AbsoluteMap.width)]
            for k in range(3):
                rowlist = [squares[s][k] for s in range(len(squares))]
                for row in rowlist:
                    print(f'|{"|".join(row)}|', end=' ')
                print()
            print()


def populate_world(world):
    world.place_wumpus(1, 3)
    world.place_portal(3, 1)
    world.place_portal(3, 3)
    world.place_portal(4, 4)
    world.place_coin(2, 3)


if __name__ == '__main__':
    world = AbsoluteMap()
    populate_world(world)
    world.print_map()
