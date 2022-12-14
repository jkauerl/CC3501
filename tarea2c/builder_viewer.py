from msilib.schema import Directory
import glfw
import sys
from OpenGL.GL import *
import numpy as np
import pip
import grafica.basic_shapes as bs
import grafica.lighting_shaders as ls

from modelo import *
from controller import Controller
import grafica.text_renderer as tx
import grafica.lighting_shaders as ls

if __name__ == '__main__':

    t0 = 0

    # Initialize glfw2
    if not glfw.init():
        sys.exit()

    window = width, height = 1000, 1000

    window = glfw.create_window(*window, 'Visualizador de Edificio', None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    controller = Controller()

    glfw.set_key_callback(window, controller.on_key)

    # Creando el pipeline 
    simpleGouraudPipeline = ls.SimpleGouraudShaderProgram()
    textureGouraudPipeline = ls.SimpleTextureGouraudShaderProgram()
    axisPipeline = es.SimpleModelViewProjectionShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # Our shapes here are always fully painted
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # HACEMOS LOS OBJETOS
    gpuEmpireState = EmpireState(textureGouraudPipeline, simpleGouraudPipeline)
    gpuWillisTower = WillisTower(textureGouraudPipeline, simpleGouraudPipeline)
    gpuBurjAlArab = BurjAlArab(textureGouraudPipeline, simpleGouraudPipeline) 
    gpuAxis = createSimpleGPUShape(bs.createAxis(4), axisPipeline)

    # Transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    while not glfw.window_should_close(window):  # Dibujando --> 1. obtener el input
        
        # Calculamos el dt
        ti = glfw.get_time()
        dt = ti - t0
        t0 = ti

        projection = controller.setProjection()

        # Using GLFW to check for input events
        glfw.poll_events()  # OBTIENE EL INPUT --> controller --> MODELOS

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        view = controller.setView()

        # Reconocer la logica

        if controller.edificio == 0:
            gpuEdificio = gpuEmpireState
        elif controller.edificio == 1:
            gpuEdificio = gpuWillisTower
        elif controller.edificio == 2:
            gpuEdificio = gpuBurjAlArab
        else:
            raise Exception() 
    
        if (gpuEdificio.lightning[0] < 0 and gpuEdificio.lightning[1] < 0 and gpuEdificio.lightning[2] < 0):
            controller.iluminacion = False
            if controller.edificio == 0:
                gpuEdificio = gpuEmpireState
                gpuEdificio.lightning = np.array([0,3/4,1])
            elif controller.edificio == 1:
                gpuEdificio = gpuWillisTower
                gpuEdificio.lightning = np.array([1,3/4,0])
            elif controller.edificio == 2:
                gpuEdificio = gpuBurjAlArab
                gpuEdificio.lightning = np.array([1,1,0])
            else:
                raise Exception() 
        if controller.camera5:
            speed = dt*0.5
            controller.camera_theta = (controller.camera_theta - speed)
            controller.camX = -4*np.cos(controller.camera_theta)
            controller.camY = -4*np.sin(controller.camera_theta)
            if controller.distance > 0:
                controller.distance = controller.distance - speed
            elif controller.distance < 0:
                controller.camera5 = False    
            controller.viewPos = np.array([controller.camX,controller.camY,controller.distance])           

        # DIBUJAR LOS MODELOSe
        if controller.showAxis:
            glUseProgram(axisPipeline.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(axisPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
            glUniformMatrix4fv(glGetUniformLocation(axisPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
            glUniformMatrix4fv(glGetUniformLocation(axisPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
            axisPipeline.drawCall(gpuAxis, GL_LINES)
        
        # Dibujar el Edificio
        if controller.iluminacion:
            interpolation = dt*(1/2)
            gpuEdificio.lightning = gpuEdificio.lightning + interpolation
            print(gpuEdificio.lightning)
            gpuEdificio.lightnings(textureGouraudPipeline,simpleGouraudPipeline,view[0])
        elif not controller.iluminacion:
            gpuEdificio.lightnings(textureGouraudPipeline,simpleGouraudPipeline,view[0])
        gpuEdificio.draw(textureGouraudPipeline, simpleGouraudPipeline, projection, view[0])

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    glfw.terminate()