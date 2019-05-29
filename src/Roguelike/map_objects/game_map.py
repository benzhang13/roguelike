from map_objects.tile import Tile
from map_objects.rectangle import Rect
from random import randint

class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]

        return tiles

    def make_map(self, max_rooms, room_max_size, room_min_size, map_width, map_height, player):

        rooms = []
        num_rooms = 0

        for r in range(max_rooms):
            # generates random room size
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)

            # generates random room location in the map and not overlapping
            x = randint(0, map_width - w - 1)
            y = randint(0, map_height - h - 1)

            new_room = Rect(x, y, w, h)

            # checks for room intersections
            for other_room in rooms:
                if new_room.intersect(other_room):
                    break
            else:
                # if no intersections
                self.create_room(new_room)
                (new_x, new_y) = new_room.center()

                if num_rooms == 0:
                    # the first room contains the player in its center
                    player.x = new_x
                    player.y = new_y
                else:
                    # finds center of previous room
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()

                    # flips a coin to find order of tunnel generation
                    if randint(0,1) == 0:
                        # moves horizontally then vertically
                        self.create_horizontal_tunnel(prev_x, new_x, prev_y)
                        self.create_vertical_tunnel(prev_y, new_y, new_x)
                    else:
                        # moves vertically then horizontally
                        self.create_horizontal_tunnel(prev_x, new_x, new_y)
                        self.create_vertical_tunnel(prev_y, new_y, prev_x)
                rooms.append(new_room)
                num_rooms += 1

    def create_room(self, room):
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_horizontal_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].block_sight = False
            self.tiles[x][y].blocked = False

    def create_vertical_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].block_sight = False
            self.tiles[x][y].blocked = False

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True
        else:
            return False