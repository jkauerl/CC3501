"""
Esta sería la clase vista. Contiene el ciclo de la aplicación y ensambla
las llamadas para obtener el dibujo de la escena.
"""

from msilib.schema import Directory
import glfw
import sys
from OpenGL.GL import *
import numpy as np

from modelo import *
from controlador import Controller
import sys 
import grafica.text_renderer as tx

if __name__ == '__main__':

    t0 = 0

    # Recibe un valor cuando se llama la funcion
    N = sys.argv[1]

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    window = width, height = 600, 800

    window = glfw.create_window(*window, 'FLAPPY BIRD!!!!', None, None)


    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    controlador = Controller()

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, controlador.on_key)

    # Assembling the shader program (pipeline) with both shaders
    pipeline = es.SimpleTextureTransformShaderProgram()
    textPipeline = tx.TextureTextRendererShaderProgram()

    # Funcion para el Texto
    gpuText3DTexture = tx.toOpenGLTexture(tx.generateTextBitsTexture())
    

    # Our shapes here are always fully painted
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    # HACEMOS LOS OBJETOS
    background = Background(pipeline)
    floors = Floors()
    floors.create_floor(pipeline)
    pajarito = Pajarito(pipeline,0,1/2,1, -3/2)
    tubos = Tubos()
    die_or_win = Die_Or_Win(pipeline)
    
    # Hacemos que el modeelo se setee
    controlador.set_model(pajarito)

    # Transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    


    while not glfw.window_should_close(window):  # Dibujando --> 1. obtener el input
        
        # Calculamos el dt
        ti = glfw.get_time()
        dt = ti - t0
        t0 = ti

        # Using GLFW to check for input events
        glfw.poll_events()  # OBTIENE EL INPUT --> CONTROLADOR --> MODELOS

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Reconocer la logica
        text_score = Score(textPipeline, gpuText3DTexture)
        floors.update(0.43*dt) # Velocidad movimiento del suelo
        floors.swap(pipeline)
        tubos.create_tubo(pipeline, N) 
        tubos.update(0.43*dt, floors)  # Velocidad movimiento de los tubos        
        tubos.counting()
        pajarito.updatePosition(dt)
        pajarito.collide(tubos, floors)

        # DIBUJAR LOS MODELOS
        glUseProgram(pipeline.shaderProgram)
        background.draw(pipeline)
        tubos.draw(pipeline)
        floors.draw(pipeline)
        pajarito.draw(pipeline)
        if tubos.on == False and pajarito.alive == True:
            die_or_win.draw_w(pipeline, pajarito)
        elif tubos.on == False and pajarito.alive == False:
            die_or_win.draw_l(pipeline, pajarito)

        # Dibuja el score
        glUseProgram(textPipeline.shaderProgram)
        text_score.draw(textPipeline)
        

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    glfw.terminate()
