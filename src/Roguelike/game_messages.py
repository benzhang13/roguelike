import tcod as libtcod

import textwrap

class Message:
    def __init__(self, text, colour=libtcod.white):
        self.text = text
        self.colour = colour

class MessageLog:
    def __init__(self, x, width, height):
        self.messages = []
        self.x = x
        self.width = width
        self.height = height

    def add_message(self, message):
        # Splits text into multiple lines if necessary
        new_msg_line = textwrap.wrap(message.text, self.width)

        for line in new_msg_line:
            # Deletes top message if message log is full
            if len(self.messages) == self.height:
                del self.messages[0]

            # Adds new line as a message object
            self.messages.append(message)


