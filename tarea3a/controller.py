from modelo import *
import glfw


class Controller(object):
    
    def __init__(self):

        self.showAxis = False
        self.distance = 3
        self.camera_theta = np.pi/4
        self.camX = -np.cos(self.camera_theta)
        self.camY = -np.sin(self.camera_theta)
        self.viewPos = np.array([self.distance*self.camX,self.distance*self.camY, self.distance])
        self.camAt = np.array([0,0,0])
        self.camUp = np.array([0, 0, 1])
        self.edificio = 0
        self.projection = tr.perspective(45, float(1000) / float(1000), 0.1, 100)
        self.trayectoria = True
        self.model = None
        self.stop = False
        self.agua = True

    def set_model(self, m):
        self.model = m

    def setView(self):
        view = tr.lookAt(
            self.viewPos,
            self.camAt,
            self.camUp
        )
        return view

    def on_key(self, window, key, scancode, action, mods):
        if action != glfw.PRESS:
            return

        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)

        # Controlador modifica al modelo
        elif key == glfw.KEY_1:
            # Camara Frontal
            self.camX = 0
            self.camY = -1
            self.distance = 3
            self.viewPos = np.array([self.distance*self.camX, self.distance*self.camY, 0.5])  # Vista frontal
            self.camAt = np.array([0, 0, 0.5])
            self.camUp = np.array([0, 0, 1])
            print('Camara Frontal')

        elif key == glfw.KEY_2:
            # Camara elevada-lateral Derecha
            self.camera_theta = 5*np.pi/4
            self.camX = np.cos(self.camera_theta)
            self.camY = np.sin(self.camera_theta)
            self.distance = 3
            self.viewPos = np.array([self.distance*self.camX, -self.distance*self.camY, self.distance])  # Vista diagonal 1
            self.camAt = np.array([0,0,0])
            self.camUp = np.array([0, 0, 1])
            print('Camara Descendiente-Lateral Derecha')

        elif key == glfw.KEY_3:
            # Camara descendiente-diagonal Izquierda
            self.camera_theta = np.pi/4
            self.camX = np.cos(self.camera_theta)
            self.camY = np.sin(self.camera_theta)
            self.distance = 3
            self.viewPos = np.array([self.distance*self.camX, self.distance*self.camY, self.distance])  # Vista diagonal 1
            self.camAt = np.array([0,0,0])
            self.camUp = np.array([0, 0, 1])
            print('Camara Lateral-Diagonal Izquierda')

        elif key == glfw.KEY_4:
            # Camara Superior
            self.camera_theta = 2*np.pi
            self.camX = -2 * np.cos(self.camera_theta)
            self.camY = -2 * np.sin(self.camera_theta)
            self.distance = 3
            self.viewPos = np.array([0, 0, self.distance])  # Vista superior
            self.camAt = np.array([0,0,0])
            self.camUp = np.array([0, 1, 0])
            print('Camara Superior')            

        elif key == glfw.KEY_X:
            if self.showAxis:
                self.showAxis = False
            else:
                self.showAxis = True

        elif key == glfw.KEY_SPACE:
            if self.trayectoria:
                self.trayectoria = False
            else:
                self.trayectoria = True

        elif key == glfw.KEY_S:
            if self.stop:
                self.stop = False
            else:
                self.stop = True

        elif key == glfw.KEY_A:
            if self.agua:
                self.agua = False
            else:
                self.agua = True

        # Cualquier otra cosa
        else:
            print('Unknown key')