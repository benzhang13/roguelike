import tcod as libtcod

from map_objects.tile import Tile
from map_objects.rectangle import Rect
from random import randint
from entity import Entity
from components.fighter import Fighter
from components.ai import BasicMonster
from render_functions import RenderOrder
from components.item import Item
from item_functions import *
from game_messages import Message
from components.stairs import Stairs
from random_utils import random_choice_from_dict, from_dungeon_level
from components.equipment import Equipment, EquipmentSlots
from components.equippable import Equippable

class GameMap:
    def __init__(self, width, height, dungeon_level=1):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.dungeon_level = dungeon_level

    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]

        return tiles

    def make_map(self, max_rooms, room_max_size, room_min_size, map_width, map_height, player, entities):

        rooms = []
        num_rooms = 0

        center_of_last_room_x = 0
        center_of_last_room_y = 0

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

                    center_of_last_room_x = new_x
                    center_of_last_room_y = new_y

                    # flips a coin to find order of tunnel generation
                    if randint(0, 1) == 0:
                        # moves horizontally then vertically
                        self.create_horizontal_tunnel(prev_x, new_x, prev_y)
                        self.create_vertical_tunnel(prev_y, new_y, new_x)
                    else:
                        # moves vertically then horizontally
                        self.create_horizontal_tunnel(prev_x, new_x, new_y)
                        self.create_vertical_tunnel(prev_y, new_y, prev_x)

                self.place_entities(new_room, entities)
                rooms.append(new_room)
                num_rooms += 1

        stairs_component = Stairs(self.dungeon_level + 1)
        down_stairs = Entity(center_of_last_room_x, center_of_last_room_y, ">", libtcod.white, "Stairs", False,
                             render_order=RenderOrder.STAIRS, stairs=stairs_component)
        entities.append(down_stairs)

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

    def place_entities(self, room, entities):

        max_monsters_per_room = from_dungeon_level([[2, 1], [3, 4], [5, 6]], self.dungeon_level)
        max_items_per_room = from_dungeon_level([[1, 1], [2, 4]], self.dungeon_level)

        # gets random number of monsters
        number_of_monsters = randint(0, max_monsters_per_room)
        number_of_items = randint(0, max_items_per_room)

        monster_chances = {"orc": 80,
                           "troll": from_dungeon_level([[15, 3], [30, 5], [60, 7]], self.dungeon_level),
                           "dragon": from_dungeon_level([[10, 7], [20, 10], [30, 14]], self.dungeon_level)}
        item_chances = {"health_potion": 35,
                        "lightning_scroll": from_dungeon_level([[25, 4]], self.dungeon_level),
                        "fireball_scroll": from_dungeon_level([[25, 6]], self.dungeon_level),
                        "confusion_scroll": from_dungeon_level([[10, 2]], self.dungeon_level),
                        "betrayal_scroll": from_dungeon_level([[10, 5]], self.dungeon_level),
                        "iron_sword": from_dungeon_level([[5, 4]], self.dungeon_level),
                        "wooden_shield": from_dungeon_level([[15, 8]], self.dungeon_level)}

        for i in range(number_of_monsters):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                monster_choice = random_choice_from_dict(monster_chances)

                if monster_choice == "orc":
                    fighter_component = Fighter(hp=20, defense=0, power=4, xp=35)
                    ai_component = BasicMonster()
                    monster = Entity(x, y, "o", libtcod.desaturated_green, "Orc", blocks=True,
                                     render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
                elif monster_choice == "troll":
                    fighter_component = Fighter(hp=30, defense=2, power=8, xp=100)
                    ai_component = BasicMonster()
                    monster = Entity(x, y, "T", libtcod.darker_green, "Troll", blocks=True,
                                     render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
                elif monster_choice == "dragon":
                    fighter_component = Fighter(hp=40, defense=2, power=12, xp=500)
                    ai_component = BasicMonster()
                    monster = Entity(x, y, "D", libtcod.dark_red, "Dragon", blocks=True,
                                     render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)

                entities.append(monster)

        for i in range(number_of_items):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                item_choice = random_choice_from_dict(item_chances)

                if item_choice == "health_potion":
                    item_component = Item(use_function=heal, amount=40)
                    item = Entity(x, y, "!", libtcod.violet, "Health Potion", False, render_order=RenderOrder.ITEM,
                                  item=item_component)
                elif item_choice == "fireball_scroll":
                    item_component = Item(use_function=cast_fireball, targeting=True,
                                          targeting_message=Message(
                                              "Left-click a tile to target, or right-click to cancel.",
                                              libtcod.light_cyan),
                                          damage=25, radius=3)
                    item = Entity(x, y, "#", libtcod.red, "Fireball Scroll", False, render_order=RenderOrder.ITEM,
                                  item=item_component)

                elif item_choice == "confusion_scroll":
                    item_component = Item(use_function=cast_confuse, targeting=True,
                                          targeting_message=Message(
                                              "Left-click a tile to target, or right-click to cancel",
                                              libtcod.light_cyan))
                    item = Entity(x, y, "#", libtcod.light_pink, "Confusion Scroll", False,
                                  render_order=RenderOrder.ITEM, item=item_component)

                elif item_choice == "betrayal_scroll":
                    item_component = Item(use_function=cast_betrayal, targeting=True,
                                          targeting_message=Message(
                                              "Left-click a tile to target, or right-click to cancel",
                                              libtcod.light_cyan))
                    item = Entity(x, y, '#', libtcod.black, "Betrayal Scroll", False, render_order=RenderOrder.ITEM,
                                  item=item_component)
                elif item_choice == "lightning_scroll":
                    item_component = Item(use_function=cast_lightning, damage=40, maximum_range=5)
                    item = Entity(x, y, "#", libtcod.yellow, "Lightning Scroll", False, render_order=RenderOrder.ITEM,
                                  item=item_component)
                elif item_choice == "iron_sword":
                    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=3)
                    item = Entity(x, y, "/", libtcod.silver, "Iron Sword", False, render_order=RenderOrder.ITEM,
                                  equippable=equippable_component)
                elif item_choice == "wooden_shield":
                    equippable_component = Equippable(EquipmentSlots.OFF_HAND, defense_bonus=1)
                    item = Entity(x, y, "[", libtcod.darker_orange, "Wooden Shield", False, render_order=RenderOrder.ITEM,
                                  equippable=equippable_component)
                entities.append(item)

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True
        else:
            return False

    def next_floor(self, player, message_log, constants):
        self.dungeon_level += 1
        entities = [player]

        self.tiles = self.initialize_tiles()
        self.make_map(constants["max_rooms"], constants["room_max_size"], constants["room_min_size"],
                      constants["map_width"], constants["map_height"], player, entities)
        player.fighter.heal(player.fighter.max_hp // 2)

        message_log.add_message(Message("You take a moment to rest, and recover your strength.", libtcod.light_violet))

        return entities

