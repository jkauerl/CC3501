"""
Clase controlador, obtiene el input, lo procesa, y manda los mensajes
a los modelos.
"""

from modelo import Pajarito, Tubos
import glfw
from typing import Union


class Controller(object):
    model: Union['Pajarito', None]
    tubos: Union['Tubos', None]
    
    def __init__(self):
        self.model = None
        self.tubos = None

    def set_model(self, m):
        self.model = m

    def on_key(self, window, key, scancode, action, mods):
        if not (action == glfw.PRESS or action == glfw.RELEASE):
            return

        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)

        # Controlador modifica al modelo
        if key == glfw.KEY_UP:
            # print('Move up')
            self.model.move_up()

        # Raton toca la pantalla....
        else:
            print('Unknown key')