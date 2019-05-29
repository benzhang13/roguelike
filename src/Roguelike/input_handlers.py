import tcod as libtcod

def handle_keys(key):

    key_char = chr(key.c)
    # Movement keys
    if key.vk == libtcod.KEY_UP:
        return {"move" : (0, -1)}
    elif key.vk == libtcod.KEY_DOWN:
        return {"move" : (0, 1)}
    elif key.vk == libtcod.KEY_LEFT:
        return {"move" : (-1, 0)}
    elif key.vk == libtcod.KEY_RIGHT:
        return {"move" : (1, 0)}
    elif key_char == 'y':
        return {"move" : (-1, -1)}
    elif key_char == 'u':
        return {"move" : (1, -1)}
    elif key_char == 'b':
        return {"move" : (-1, 1)}
    elif key_char == 'n':
        return {"move" : (1, 1)}

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # alt + enter toggles fullscreen
        return {'fullscreen' : True}
    elif key.vk == libtcod.KEY_ESCAPE:
        # esc quits game
        return {'exit' : True}

    # no key presses
    return {}