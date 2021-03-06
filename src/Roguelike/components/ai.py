import tcod as libtcod
from random import randint

from game_messages import Message

class BasicMonster():
    def take_turn(self, target, fov_map, game_map, entities):
        monster = self.owner
        results = []
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            if monster.distance_to(target) >= 2:
                monster.move_astar(target, entities, game_map)
            elif target.fighter.hp > 0:
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)

                return results


class ConfusedMonster():
    def __init__(self, previous_ai, number_of_turns=10):
        self.previous_ai = previous_ai
        self.number_of_turns = number_of_turns

    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        if libtcod.map_is_in_fov(fov_map, self.owner.x, self.owner.y):
            if self.number_of_turns > 0:
                random_x = self.owner.x + randint(0, 2) - 1
                random_y = self.owner.y + randint(0, 2) - 1

                if random_x == target.x and random_y == target.y:
                    attack_results = self.owner.fighter.attack(target)
                    results.extend(attack_results)

                    return results
                elif random_x != self.owner.x and random_y != self.owner.y:
                    self.owner.move_towards(random_x, random_y, game_map, entities)

                self.number_of_turns -= 1
            else:
                self.owner.ai = self.previous_ai
                results.append({"message": Message("The {0} is no longer confused!".format(self.owner.name), libtcod.red)})

        return results


class BetrayingMonster():
    def __init__(self, previous_ai, number_of_moves):
        self.previous_ai = previous_ai
        self.number_of_moves = number_of_moves

    def take_turn(self, player, fov_map, game_map, entities):
        results = []

        if self.number_of_moves > 0:
            closest_distance = 30
            target = None
            for entity in entities:
                if libtcod.map_is_in_fov(fov_map, entity.x, entity.y) and entity.fighter and entity != self.owner and entity != player:
                    if entity.fighter.hp > 0:
                        distance = self.owner.distance_to(entity)
                        if distance < closest_distance:
                            target = entity
                            closest_distance = distance

            if target:
                if self.owner.distance_to(target) >= 2:
                    self.owner.move_astar(target, entities, game_map)
                else:
                    attack_results = self.owner.fighter.attack(target)
                    results.extend(attack_results)
            elif self.owner.distance_to(player) > 2:
                self.owner.move_astar(player, entities, game_map)
            elif self.owner.distance_to(player) < 2:
                self.owner.move_away_from(player, game_map, entities)

            self.number_of_moves -= 1
        else:
            self.owner.ai = self.previous_ai
            results.append({"message": Message("The {0} is no longer betraying its brethren!".format(self.owner.name), libtcod.red)})
        return results


