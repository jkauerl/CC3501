from tkinter.tix import Tree

from numpy import dtype
from modelo import *
import glfw
from typing import Union
import grafica.lighting_shaders as ls


class Controller(object):
    
    def __init__(self):

        self.showAxis = False
        self.distance = 2
        self.camera_theta = np.pi/4
        self.camX = -np.cos(self.camera_theta)
        self.camY = -np.sin(self.camera_theta)
        self.viewPos = np.array([self.distance*self.camX,self.distance*self.camY, self.distance])
        self.camAt = np.array([0,0,0])
        self.camUp = np.array([0, 0, 1])
        self.edificio = 0
        self.type = True
        self.camera5 = False
        self.iluminacion = False
        self.buildingPipeline = ls.SimpleGouraudShaderProgram()
        self.floorPipeline= ls.SimpleTextureGouraudShaderProgram()
        
    def setProjection(self):
        if self.type:
            self.projection = tr.perspective(45, float(1000) / float(1000), 0.1, 100)
        if not self.type:
            self.projection = tr.ortho(-1, 1, -1, 1, 0.1, 100)
        return self.projection

    def set_model(self, m):
        self.model = m

    def setView(self):
        view = tr.lookAt(
            self.viewPos,
            self.camAt,
            self.camUp
        )
        return view

    def interpolacion(self, floorPipeline, buildingPipeline,night):
        glUseProgram(floorPipeline.shaderProgram)
        glUniform1f(glGetUniformLocation(floorPipeline.shaderProgram, "Ka"), night[0])
        glUniform1f(glGetUniformLocation(floorPipeline.shaderProgram, "Kd"), night[1])
        glUniform1f(glGetUniformLocation(floorPipeline.shaderProgram, "Ks"), night[2])

        glUseProgram(buildingPipeline.shaderProgram)
        glUniform1f(glGetUniformLocation(buildingPipeline.shaderProgram, "Ka"), night[0][0])
        glUniform1f(glGetUniformLocation(buildingPipeline.shaderProgram, "Kd"), night[1][1])
        glUniform1f(glGetUniformLocation(buildingPipeline.shaderProgram, "Ks"), night[2][2])

    def on_key(self, window, key, scancode, action, mods):
        if action != glfw.PRESS:
            return

        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)

        # Controlador modifica al modelo
        elif key == glfw.KEY_1:
            # Camara Frontal
            self.camera5 = False
            self.type = False
            self.camX = 0
            self.camY = -3
            self.distance = 3
            self.viewPos = np.array([self.distance*self.camX,self.distance*self.camY, self.distance])  # Vista frontal
            self.camAt = np.array([0,1,0])
            self.camUp = np.array([0, 0, 10])
            print('Camara Frontal')

        elif key == glfw.KEY_2:
            # Camara elevada-lateral Derecha
            self.camera5 = False
            self.type = True
            self.camera_theta = 5*np.pi/4
            self.camX = np.cos(self.camera_theta)
            self.camY = np.sin(self.camera_theta)
            self.distance = 3
            self.viewPos = np.array([self.distance*self.camX,-self.distance*self.camY, self.distance])  # Vista diagonal 1
            self.camAt = np.array([0,0,0])
            self.camUp = np.array([0, 0, 1])
            print('Camara Descendiente-Lateral Derecha')

        elif key == glfw.KEY_3:
            # Camara descendiente-diagonal Izquierda
            self.camera5 = False
            self.type = True
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
            self.camera5 = False
            self.type = False
            self.camera_theta = np.pi/4+np.pi
            self.camX = -2 * np.cos(self.camera_theta)
            self.camY = -2 * np.sin(self.camera_theta)
            self.distance = 3
            self.viewPos = np.array([0, 0, self.distance])  # Vista superior
            self.camAt = np.array([0,0,0])
            self.camUp = np.array([0, 1, 0])
            print('Camara Superior')

        elif key == glfw.KEY_5:
            # Camara Movil
            self.camera_theta = 2*np.pi
            self.camera5 = True
            self.type = False
            self.distance = 8
            self.camX = -4*np.cos(self.camera_theta)
            self.camY = -4*np.sin(self.camera_theta)
            self.viewPos= np.array([self.camX,self.camY,self.distance])
            self.camAt = np.array([0,0,0])
            self.camUp = np.array([0, 0, 1])
            print('Camara Movil')
            

        elif key == glfw.KEY_E:
            # Edificio Empire State
            self.edificio = 0
            print('Edificio Empire State')

        elif key == glfw.KEY_W:
            # Edifico Willis Tower
            self.edificio = 1
            print('Edificio Willis Tower')

        elif key == glfw.KEY_B:
            # Edicio Burj Al Arab
            self.edificio = 2
            print('Edificio Burj Al Arab')

        elif key == glfw.KEY_L:
            # Interpolacion Luz Lunar
            self.iluminacion = True
            print('Interpolacion Luz Lunar')

        elif key == glfw.KEY_A:
            if self.showAxis:
                self.showAxis = False
            else:
                self.showAxis = True

        # Cualquier otra cosa
        else:
            print('Unknown key')