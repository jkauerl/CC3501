from asyncio.windows_utils import pipe
from venv import create
from matplotlib.pyplot import text
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.scene_graph as sg
import grafica.easy_shaders as es
from grafica.assets_path import getAssetPath
from OpenGL.GL import *
import numpy as np
from curves import *

def createSimpleGPUShape(shape, pipeline):
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape

class Axis(object):

    def __init__(self, axisPipeline):
        
        self.axisPipeline = axisPipeline
        self.gpuAxis = createSimpleGPUShape(bs.createAxis(4), axisPipeline)

    def draw(self, axisPipeline, projection, view):

        glUseProgram(axisPipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(axisPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(axisPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(axisPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        axisPipeline.drawCall(self.gpuAxis, GL_LINES)


class Agua(object):

    def __init__(self, pipeline):

        self.aguaPipeline = pipeline
        self.gpuAgua = createSimpleGPUShape(bs.createAguaNormalsCube(0, 0, 1), pipeline)
        self.lightning = np.array([1,1,1])


    def draw(self, aguaPipeline, projection, setView):

        glUseProgram(aguaPipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(aguaPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(aguaPipeline.shaderProgram, "Kd"), 0.9, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(aguaPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        glUniformMatrix4fv(glGetUniformLocation(aguaPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(aguaPipeline.shaderProgram, "view"), 1, GL_TRUE, setView)
        glUniformMatrix4fv(glGetUniformLocation(aguaPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.scale(2, 2, 0))
        aguaPipeline.drawCall(self.gpuAgua)

class Naufrago(object):

    def __init__(self, pipeline):

        gpuBlocks = createSimpleGPUShape(bs.createColorNormalsCube(58/255, 28/255, 0), pipeline)
        gpuSail = createSimpleGPUShape(bs.createColorNormalsCube(1,1,1), pipeline)



        blocks = sg.SceneGraphNode("blocks")
        blocks.transform = tr.matmul([tr.scale(1/32,1/4,1/16), tr.translate(0, 0, 1/2)])
        blocks.childs = [gpuBlocks]

        block1 = sg.SceneGraphNode("block1") 
        block1.transform = tr.translate(1/10,0,0) # bloque de adelante
        block1.childs = [blocks]

        block2 = sg.SceneGraphNode("block2") # bloque de atras
        block2.transform = tr.translate(-1/10, 0, 0)
        block2.childs = [blocks]

        block3 = sg.SceneGraphNode("block3") # bloque del centro
        block3.childs = [blocks]

        block4 = sg.SceneGraphNode("block4") # bloque de la derecha
        block4.transform = tr.matmul([ tr.scale(3/8, 1/32, 1/16), tr.translate(0, -2, 1/2)])
        block4.childs = [gpuBlocks]

        block5 = sg.SceneGraphNode("block5") # bloque de la izquierda
        block5.transform = tr.matmul([ tr.scale(3/8, 1/32, 1/16), tr.translate(0, 2, 1/2)])
        block5.childs = [gpuBlocks]

        block6 = sg.SceneGraphNode("block6") # mastil
        block6.transform = tr.matmul([tr.scale(1/64, 1/16, 1/4), tr.translate(0, 0, 1/2)])
        block6.childs = [gpuBlocks]

        block7 = sg.SceneGraphNode("block7")
        block7.transform = tr.matmul([tr.scale(1/64, 1/8, 1/32), tr.translate(0, 0, 14)])
        block7.childs = [gpuBlocks]

        floor = sg.SceneGraphNode("floor")
        floor.childs = [block1, block2, block3, block4, block5, block6, block7]

        sail = sg.SceneGraphNode("sail")
        sail.transform = tr.matmul([tr.scale(1/32,1/4,5/16), tr.translate(0, 0, 7/8)])
        sail.childs = [gpuSail]

        boat = sg.SceneGraphNode("boat")
        boat.childs = [floor, sail]

        system = sg.SceneGraphNode("system")
        system.childs = [boat]

        self.model = system
        self.lightning = np.array([1/2,1/2,0])


    def draw(self, naufragoPipeline, projection, setView):

        glUseProgram(naufragoPipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(naufragoPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(naufragoPipeline.shaderProgram, "Kd"), 0.9, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(naufragoPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        glUniformMatrix4fv(glGetUniformLocation(naufragoPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(naufragoPipeline.shaderProgram, "view"), 1, GL_TRUE, setView)
        sg.drawSceneGraphNode(self.model, naufragoPipeline, "model")


class Mountain(object):

    def __init__(self, mountainPipeline):

        self.pipeline = mountainPipeline
        gpuBlockG = createSimpleGPUShape(bs.createColorNormalsCube(0, 1, 0),mountainPipeline)
        gpuBlockB = createSimpleGPUShape(bs.createColorNormalsCube(1/2, 1/4, 0),mountainPipeline)
        gpuBlockW = createSimpleGPUShape(bs.createColorNormalsCube(1, 1, 1),mountainPipeline)
        
        test = createSimpleGPUShape(bs.createColorNormalsCube(0,0,0), mountainPipeline)

        blockG = sg.SceneGraphNode("Green")
        blockG.transform = tr.scale(1/2,1/2,1)
        blockG.childs = [gpuBlockG]

        blockB = sg.SceneGraphNode("Brown")
        blockB.transform = tr.scale(1/2,1/2,1)
        blockB.childs = [gpuBlockB]

        blockW = sg.SceneGraphNode("White")
        blockW.transform = tr.scale(1/2,1/2,1)
        blockW.childs = [gpuBlockW]

        testBlock = sg.SceneGraphNode("Test Block")
        testBlock.transform = tr.matmul([ tr.translate(0, 0, 0.5), tr.scale(1, 1, 0.008)])
        testBlock.childs = [test]

        # Iterate the shapes creating a mountain with the shapes defined above

        greenMountain = sg.SceneGraphNode("Green Mountain")

        for i in range(31):
            node = sg.SceneGraphNode('blockG'+str(i))
            node.transform = tr.matmul([tr.scale(1-(0.01*i), 1-(0.01*i), 1/32), tr.translate(0, 0, 1/2+1/2*i)])
            node.childs += [blockG]
            greenMountain.childs += [node]

        brownMountain = sg.SceneGraphNode("Brown Mountain")

        for i in range(21):
            node = sg.SceneGraphNode('blockB'+str(i))
            node.transform = tr.matmul([tr.scale(0.71-(0.01*i), 0.71-(0.01*i), 1/32), tr.translate(0, 0, 15+1/2*i)])
            node.childs += [blockB]
            brownMountain.childs += [node]

        whiteMountain = sg.SceneGraphNode("White Mountain")

        for i in range(14):
            node = sg.SceneGraphNode('blockW'+str(i))
            node.transform = tr.matmul([tr.scale(0.51-(0.01*i), 0.51-(0.01*i), 1/32), tr.translate(0, 0, 25+1/2*i)])
            node.childs += [blockW]
            whiteMountain.childs += [node]

        mountain = sg.SceneGraphNode("Mountain")
        mountain.childs = [greenMountain, brownMountain, whiteMountain]    #, testBlock]

        self.model = mountain

    def draw(self, mountainPipeline,projection, setView):

        glUseProgram(mountainPipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(mountainPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(mountainPipeline.shaderProgram, "Kd"), 0.9, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(mountainPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        glUniformMatrix4fv(glGetUniformLocation(mountainPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(mountainPipeline.shaderProgram, "view"), 1, GL_TRUE, setView)
        sg.drawSceneGraphNode(self.model, mountainPipeline, "model")

class Trayectoria(object):

    def __init__(self, C, r, g, b, pipeline):

        self.C = C
        self.pipeline = pipeline

        shape = bs.trayectoria(C, r, g, b)
        self.gpuC = createSimpleGPUShape(shape, pipeline)

    def draw(self, trayectoriaPipeline, projection, view):

        glUseProgram(trayectoriaPipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(trayectoriaPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(trayectoriaPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(trayectoriaPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        trayectoriaPipeline.drawCall(self.gpuC, GL_LINES)




class Spotlight:
    def __init__(self):
        self.ambient = np.array([0,0,0])
        self.diffuse = np.array([0,0,0])
        self.specular = np.array([0,0,0])
        self.constant = 0
        self.linear = 0
        self.quadratic = 0
        self.position = np.array([0,0,0])
        self.direction = np.array([0,0,0])
        self.cutOff = 0
        self.outerCutOff = 0


class Lights:

    def __init__(self):

        self.spotlightsPool = dict()

        #TAREA4: Primera luz spotlight
        self.spot1 = Spotlight()
        self.spot1.ambient = np.array([0.0, 0.0, 0.0])
        self.spot1.diffuse = np.array([1.0, 1.0, 1.0])
        self.spot1.specular = np.array([1.0, 1.0, 1.0])
        self.spot1.constant = 1.0
        self.spot1.linear = 0.09
        self.spot1.quadratic = 0.032
        self.spot1.position = np.array([-0.5, -0.5, 3]) #TAREA4: esta ubicada en esta posición
        self.spot1.direction = np.array([0, 0, -1]) #TAREA4: está apuntando perpendicularmente hacia el terreno (Y-, o sea hacia abajo)
        self.spot1.cutOff = np.cos(np.radians(12.5)) #TAREA4: corte del ángulo para la luz
        self.spot1.outerCutOff = np.cos(np.radians(45)) #TAREA4: la apertura permitida de la luz es de 45°
                                                    #mientras más alto es este ángulo, más se difumina su efecto
        
        self.spotlightsPool['spot1'] = self.spot1 #TAREA4: almacenamos la luz en el diccionario, con una clave única

        #TAREA4: Segunda luz spotlight
        self.spot2 = Spotlight()
        self.spot2.ambient = np.array([0.0, 0.0, 0.0])
        self.spot2.diffuse = np.array([1.0, 1.0, 1.0])
        self.spot2.specular = np.array([1.0, 1.0, 1.0])
        self.spot2.constant = 1.0
        self.spot2.linear = 0.09
        self.spot2.quadratic = 0.032
        self.spot2.position = np.array([-0.5, 0.5, 3]) #TAREA4: Está ubicada en esta posición
        self.spot2.direction = np.array([0, 0, -1]) #TAREA4: también apunta hacia abajo
        self.spot2.cutOff = np.cos(np.radians(12.5))
        self.spot2.outerCutOff = np.cos(np.radians(45)) #TAREA4: Esta luz tiene menos apertura, por eso es más focalizada
        self.spotlightsPool['spot2'] = self.spot2 #TAREA4: almacenamos la luz en el diccionario

        #TAREA5: Luces spotlights para los faros de los autos
        self.spot3 = Spotlight()
        self.spot3.ambient = np.array([0, 0, 0])
        self.spot3.diffuse = np.array([1.0, 1.0, 1.0])
        self.spot3.specular = np.array([1.0, 1.0, 1.0])
        self.spot3.constant = 1.0
        self.spot3.linear = 0.09
        self.spot3.quadratic = 0.032
        self.spot3.position = np.array([0.5, 0.5, 3]) # posición inicial
        self.spot3.direction = np.array([0, 0, -1]) # dirección inicial
        self.spot3.cutOff = np.cos(np.radians(12.5)) 
        self.spot3.outerCutOff = np.cos(np.radians(45)) 
        self.spotlightsPool['spot3'] = self.spot3 #TAREA4: almacenamos la luz en el diccionario

        self.spot4 = Spotlight()
        self.spot4.ambient = np.array([0, 0, 0])
        self.spot4.diffuse = np.array([1.0, 1.0, 1.0])
        self.spot4.specular = np.array([1.0, 1.0, 1.0])
        self.spot4.constant = 1.0
        self.spot4.linear = 0.09
        self.spot4.quadratic = 0.032
        self.spot4.position = np.array([0.5, -0.5, 3])
        self.spot4.direction = np.array([0, 0, -1])
        self.spot4.cutOff = np.cos(np.radians(12.5))
        self.spot4.outerCutOff = np.cos(np.radians(45)) 
        self.spotlightsPool['spot4'] = self.spot4 #TAREA4: almacenamos la luz en el diccionario


    def setPlot(self, axisPipeline, lightPipeline, projection):
        #projection = tr.perspective(60, float(1000)/float(1000), 0.1, 100) #el primer parametro se cambia a 60 para que se vea más escena

        glUseProgram(axisPipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(axisPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

        #TAREA4: Como tenemos 2 shaders con múltiples luces, tenemos que enviar toda esa información a cada shader
        #TAREA4: Primero al shader de color
        glUseProgram(lightPipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(lightPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        
        #TAREA4: Enviamos la información de la luz puntual y del material
        #TAREA4: La luz puntual está desactivada por defecto (ya que su componente ambiente es 0.0, 0.0, 0.0), pero pueden usarla
        # para añadir más realismo a la escena
        glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "pointLights[0].ambient"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "pointLights[0].diffuse"), 0.0, 0.0, 0.0)
        glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "pointLights[0].specular"), 0.0, 0.0, 0.0)
        glUniform1f(glGetUniformLocation(lightPipeline.shaderProgram, "pointLights[0].constant"), 0.1)
        glUniform1f(glGetUniformLocation(lightPipeline.shaderProgram, "pointLights[0].linear"), 0.1)
        glUniform1f(glGetUniformLocation(lightPipeline.shaderProgram, "pointLights[0].quadratic"), 0.01)
        glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "pointLights[0].position"), 5, 5, 5)

        glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "material.ambient"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "material.diffuse"), 0.9, 0.9, 0.9)
        glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "material.specular"), 1.0, 1.0, 1.0)
        glUniform1f(glGetUniformLocation(lightPipeline.shaderProgram, "material.shininess"), 32)

        #TAREA4: Aprovechamos que las luces spotlight están almacenadas en el diccionario para mandarlas al shader
        for i, (k,v) in enumerate(self.spotlightsPool.items()):
            baseString = "spotLights[" + str(i) + "]."
            glUniform3fv(glGetUniformLocation(lightPipeline.shaderProgram, baseString + "ambient"), 1, v.ambient)
            glUniform3fv(glGetUniformLocation(lightPipeline.shaderProgram, baseString + "diffuse"), 1, v.diffuse)
            glUniform3fv(glGetUniformLocation(lightPipeline.shaderProgram, baseString + "specular"), 1, v.specular)
            glUniform1f(glGetUniformLocation(lightPipeline.shaderProgram, baseString + "constant"), v.constant)
            glUniform1f(glGetUniformLocation(lightPipeline.shaderProgram, baseString + "linear"), 0.09)
            glUniform1f(glGetUniformLocation(lightPipeline.shaderProgram, baseString + "quadratic"), 0.032)
            glUniform3fv(glGetUniformLocation(lightPipeline.shaderProgram, baseString + "position"), 1, v.position)
            glUniform3fv(glGetUniformLocation(lightPipeline.shaderProgram, baseString + "direction"), 1, v.direction)
            glUniform1f(glGetUniformLocation(lightPipeline.shaderProgram, baseString + "cutOff"), v.cutOff)
            glUniform1f(glGetUniformLocation(lightPipeline.shaderProgram, baseString + "outerCutOff"), v.outerCutOff)

        