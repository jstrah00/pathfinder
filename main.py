from os import close
import sys, pygame, math
from operator import attrgetter

COLORS = {'clear': (73, 67, 104), 'painted': (206, 236, 151), 'solved': (50, 50, 255)}
BORDER_COLOR = (122, 40, 203)
BORDERS = {'small': 1, 'big': 3}
TEXT_COLOR = (255,255,255)
START_COLOR = (255,0,0)
END_COLOR = (0,255,0)

class Tile():
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.status = 'clear'
        self.f = 0
        self.h = 0
        self.g = 0
        self.prev_x = 0
        self.prev_y = 0

class PathFinder():
    def __init__(self):
        print("---- Bienvenido -----")
        print("Configure la pantalla")
        self.width_blocks = int(input(" - Bloques de ancho: "))
        self.height_blocks = int(input(" - Bloques de alto: "))
        self.border_type = self.get_border_type()
        self.mouse_darg = False
        pygame.font.init()
        self.text_size = 30
        self.font = pygame.font.SysFont(None, int(self.text_size))
        self.text = "Dibuje los obstaculos. Cuando finalice presione espacio."
        self.mode = 'obstacles'
        self.start_point = None
        self.end_point = None
        self.Matrix = [[Tile(x,y) for x in range(self.width_blocks)] for y in range(self.height_blocks)] 
        pygame.init()
        self.block_size, self.display_size = self.calculate_size()
        self.screen = pygame.display.set_mode(self.display_size)
        self.screen.fill((0, 0, 0))
        self.last_x, self.last_y = 0, 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and self.mode != 'run':
                if event.button == 1:
                    self.mouse_darg = True
                    mouse_x, mouse_y = event.pos
                    if self.mode == 'set_start':
                        self.set_point(mouse_x, mouse_y, 'start')
                    elif self.mode == 'set_end':
                        self.set_point(mouse_x, mouse_y, 'end')
                    self.update_clicked_box(mouse_x, mouse_y)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_darg = False
            elif event.type == pygame.MOUSEMOTION and self.mode != 'run':
                if self.mouse_darg:
                    mouse_x, mouse_y = event.pos
                    self.update_clicked_box(mouse_x, mouse_y)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.mode == 'obstacles':
                        self.mode = 'set_start'
                        self.text = "Seleccione el inicio. Luego presione espacio."
                    elif self.mode == 'set_start':
                        self.mode = 'set_end'
                        self.text = "Seleccione el final. Luego presione espacio."
                    elif self.mode == 'set_end':
                        self.mode = 'run'
                        self.text = "Hayando solucion..."
                        self.solve_path()
                        self.text = "Solucionado. Presione espacio para salir"
                        self.mode = 'exit'
                    elif self.mode == 'exit':
                        sys.exit()

    def calculate_size(self):
        infoObject = pygame.display.Info()
        if self.width_blocks > self.height_blocks:
            limited_size = infoObject.current_w / 4 * 3
            block_limit = self.width_blocks
        else: 
            limited_size = infoObject.current_h / 4 * 3
            block_limit = self.height_blocks
        block_size = int((limited_size) / block_limit)
        display_size = block_size * self.width_blocks, block_size * self.height_blocks + self.text_size
        return block_size, display_size

    def get_border_type(self):
        maxi = self.width_blocks if self.width_blocks >= self.height_blocks else self.height_blocks
        return 'big' if maxi <= 30 else 'small'

    def set_point(self, x, y, point_type):
        x = math.floor(x / self.block_size)
        y = math.floor(y / self.block_size)
        if point_type == 'start':
            self.start_point = (x,y)
        elif point_type == 'end':
            self.end_point = (x,y)

    def draw_grid(self):
        for y in range(len(self.Matrix)):
            for x in range(len(self.Matrix[y])):
                rect = pygame.Rect(x * self.block_size, y * self.block_size, self.block_size, self.block_size)
                if (x,y) == self.start_point:
                    color = START_COLOR
                elif (x,y) == self.end_point:
                    color = END_COLOR
                else:
                    color = COLORS[self.Matrix[y][x].status]
                pygame.draw.rect(self.screen, color, rect) #Relleno
                pygame.draw.rect(self.screen, BORDER_COLOR, rect, BORDERS[self.border_type]) #Borde

    def update_text(self):
        self.screen.fill((0, 0, 0))
        display_text = self.font.render(self.text, False, TEXT_COLOR)
        self.screen.blit(display_text, (10, int(self.display_size[1] - (self.text_size / 1.2))))

    def update_clicked_box(self, x, y):
        x = math.floor(x / self.block_size)
        y = math.floor(y / self.block_size)
        if not(self.last_x == x and self.last_y == y):
            if self.Matrix[y][x].status == 'clear':
                self.Matrix[y][x].status = 'painted'
            elif self.Matrix[y][x].status == 'painted':
                self.Matrix[y][x].status= 'clear'
            self.last_x, self.last_y = x,y

    def solve_path(self):
        open_set = []
        closed_set = []
        x,y = self.start_point
        closed_set.append(self.Matrix[y][x])
        self.Matrix[y][x].prev_x = None
        self.Matrix[y][x].prev_y = None
        final_tile = self.Matrix[self.end_point[1]][self.end_point[0]]
        print("FINAL TILE: "+str(final_tile.x) + ","+ str(final_tile.y)+ " : "+str(final_tile))
        final_tile.status = 'end'

        while True:
            if x+1 < self.width_blocks and self.Matrix[y][x+1].status != 'painted' and self.Matrix[y][x+1] not in open_set and self.Matrix[y][x+1] not in closed_set:
                open_set.append(self.Matrix[y][x+1])
            if x-1 >= 0 and self.Matrix[y][x-1].status != 'painted' and self.Matrix[y][x-1] not in open_set and self.Matrix[y][x-1] not in closed_set:
                open_set.append(self.Matrix[y][x-1])
            if y+1 < self.height_blocks and self.Matrix[y+1][x].status != 'painted' and self.Matrix[y+1][x] not in open_set and self.Matrix[y+1][x] not in closed_set:
                open_set.append(self.Matrix[y+1][x])
            if y-1 >= 0 and self.Matrix[y-1][x].status != 'painted' and self.Matrix[y-1][x] not in open_set and self.Matrix[y-1][x] not in closed_set:
                open_set.append(self.Matrix[y-1][x])

            print(open_set)
            if final_tile in open_set:
                closed_set.append(final_tile)
                open_set.remove(final_tile)
                final_tile.prev_x = x
                final_tile.prev_y = y
                break

            for tile in open_set:
                if (x == tile.x and (y == tile.y + 1 or y == tile.y - 1)) or  (y == tile.y and (x == tile.x + 1 or x == tile.x - 1)):
                    tile.g = self.Matrix[y][x].g + 1
                    tile.h = abs(tile.x - self.end_point[0]) + abs(tile.y - self.end_point[1])
                    f = tile.g + tile.h
                    if tile.f == 0:
                        tile.f = f
                    elif f < tile.f:
                        tile.f = f
                    tile.prev_x = x
                    tile.prev_y = y
            
            tile_minor_f = min(open_set, key=attrgetter('f'))
            closed_set.append(tile_minor_f)
            open_set.remove(tile_minor_f)
            x = tile_minor_f.x
            y = tile_minor_f.y

        x,y = self.end_point
        while True:
            try:
                x_to_paint = self.Matrix[y][x].prev_x
                y_to_paint = self.Matrix[y][x].prev_y
                self.Matrix[y_to_paint][x_to_paint].status = 'solved'
                x = self.Matrix[y_to_paint][x_to_paint].x
                y = self.Matrix[y_to_paint][x_to_paint].y
            except TypeError:
                break

def main():
    game = PathFinder()
    while 1:
        game.handle_events()
        game.update_text()
        game.draw_grid()
        pygame.display.flip()

if __name__=='__main__':
    main()