from audioop import mul
from msilib.schema import Directory
import glfw
import sys
from OpenGL.GL import *
import numpy as np
import grafica.lighting_shaders as ls
import grafica.easy_shaders as es
from modelo import *
from controller import Controller
from curves import *

if __name__ == '__main__':

    t0 = 0

    # Initialize glfw2
    if not glfw.init():
        sys.exit()

    window = width, height = 1000, 1000

    window = glfw.create_window(*window, 'Simulador de Bote', None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    controller = Controller()

    glfw.set_key_callback(window, controller.on_key)

    # Creando el pipeline 
    multiplePhongPipeline = ls.MultipleLightPhongShaderProgram()
    axisPipeline = es.SimpleModelViewProjectionShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # Our shapes here are always fully painted
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Leer las coordenadas de la curva
    F = sys.argv[1]
    file1 = open(F, "r")
    Lines = file1.readlines()

    c = np.loadtxt(F, comments="#", delimiter=",", unpack=False)

    # Ejemplo
    """ c = np.array([
                [-0.9, -0.9],
                [-0.7, 0.2],
                [-0.1, 0.6],
                [0.4, 0.8],
                [0.9, 0.9],
                [0.6, 0],
                [0.4, -0.5]
                ]) """

    l = len(c)
    b = np.zeros((l,1))
    c = np.append(c, b, axis=1)

    N = 250
    # Hacer las curvas

    # Curva base para tener poder ir agregandose
    m = catmullromMatrix(np.array([c[-1]]).T, np.array([c[0]]).T, np.array([c[1]]).T, np.array([c[2]]).T)
    C = evalCurve(m,N)
    # Iteracion de todas las curvas excepto entre P0 y P1
    for i in range(1,l):
        m = catmullromMatrix(np.array([c[(i-1)%l]]).T, np.array([c[i%l]]).T, np.array([c[(i+1)%l]]).T, np.array([c[(i+2)%l]]).T)
        t = evalCurve(m,N)
        C = np.concatenate((C,t), axis=0)


    # Setting up the projection
    projection = controller.projection

    # HACEMOS LOS OBJETOS
    axis = Axis(axisPipeline)
    agua = Agua(multiplePhongPipeline)
    naufrago = Naufrago(multiplePhongPipeline)
    mountain = Mountain(multiplePhongPipeline)
    trayectoria = Trayectoria(C, 1, 0, 0, axisPipeline)
    luces = Lights()

    # Transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    step = 0

    while not glfw.window_should_close(window):  # Dibujando --> 1. obtener el input
        
        # Calculamos el dt
        ti = glfw.get_time()
        dt = ti - t0
        t0 = ti

        # Using GLFW to check for input events
        glfw.poll_events()  # OBTIENE EL INPUT --> controller --> MODELOS

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Setup view
        view = controller.setView()
        luces.setPlot(axisPipeline, multiplePhongPipeline, projection)
        # Reconocer la logica
        if not controller.stop:
            if step >= N * l:
                step = 0
            elif step < N * l:
                angle = np.arctan2(C[(step + 1) % (N * l), 0] - C[step, 0], C[(step + 1) % (N * l), 1] - C[step, 1])
            else:
                angle = np.arctan2(C[0, 0] - C[step, 0], C[0, 1] - C[step, 1])

            boatNode = sg.findNode(naufrago.model, "system")
            boatNode.transform = tr.matmul([tr.translate(C[step, 0], C[step, 1], C[step, 2]), tr.rotationZ(np.pi/2-angle)])

            step = step + 1

        # Mostrar la trayectoria
        glLineWidth(5)
        if controller.trayectoria:
            trayectoria.draw(axisPipeline, projection, view)
            

        # DIBUJAR LOS MODELOS
        glLineWidth(1)
        if controller.showAxis:
            axis.draw(axisPipeline,projection, view)
           
        if controller.agua:
            agua.draw(multiplePhongPipeline,projection, view[0])

        naufrago.draw(multiplePhongPipeline, projection, view)
        mountain.draw(multiplePhongPipeline, projection, view)

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    glfw.terminate()