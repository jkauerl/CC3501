from asyncio.windows_utils import pipe
from contextlib import ContextDecorator
from re import X
from venv import create
import glfw
from matplotlib.pyplot import text
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.scene_graph as sg
import grafica.easy_shaders as es
from grafica.assets_path import getAssetPath
from OpenGL.GL import *

import random
from typing import List

import numpy as np


def createSimpleGPUShape(shape, pipeline):
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape

def createTextureGPUShape(shape, texture, pipeline):
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    gpuShape.texture = es.textureSimpleSetup(
        getAssetPath(texture), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
    return gpuShape

class EmpireState(object):

    def __init__(self, floorPipeline, buildingPipeline):

        gpuFloor = createTextureGPUShape(bs.createTextureNormalsCube(),"piso Empire State.png", floorPipeline)
        gpuBlocks = createSimpleGPUShape(bs.createColorNormalsCube(1,1,1), buildingPipeline)

        # Creation of 1 Block
        blocks = sg.SceneGraphNode('blocks')
        blocks.childs += [gpuBlocks]

        #    
        #
        #    4 5 4 4 4 4 5 4 
        #   2 3 2 2 4 2 2 3 2
        #  1 1 1 1 1 1 1 1 1 1 1
        # Creation of the differnt
        block1 = sg.SceneGraphNode('block1')
        block1.transform = tr.matmul([tr.scale(0.5,0.2,0.13), tr.translate(0, 0, 0.5)])
        block1.childs += [blocks]

        # Base
        block2 = sg.SceneGraphNode('block2')
        block2.transform = tr.matmul([tr.scale(0.25,0.1,0.2), tr.translate(0, 0, 0.7)])
        block2.childs += [blocks]

        # Square Base
        block3 = sg.SceneGraphNode('block3')
        block3.transform = tr.matmul([tr.scale(0.38,0.16,0.25), tr.translate(0, 0, 1)])
        block3.childs += [blocks]

        # 4 Pilars Base
        block4 = sg.SceneGraphNode('block4')
        block4.transform = tr.matmul([tr.scale(0.07,0.07,0.3), tr.translate(-1.7, -0.8, 0.9)])
        block4.childs += [blocks]

        block5 = sg.SceneGraphNode('block5')
        block5.transform = tr.matmul([tr.scale(0.07,0.07,0.3), tr.translate(-1.7, 0.8, 0.9)])
        block5.childs += [blocks]

        block6 = sg.SceneGraphNode('block6')
        block6.transform = tr.matmul([tr.scale(0.07,0.07,0.3), tr.translate(1.7, -0.8, 0.9)])
        block6.childs += [blocks]

        block7 = sg.SceneGraphNode('block7')
        block7.transform = tr.matmul([tr.scale(0.07,0.07,0.3), tr.translate(1.7, 0.8, 0.9)])
        block7.childs += [blocks]

        # Mid-Section Balcony
        block8 = sg.SceneGraphNode('block8')
        block8.transform = tr.matmul([tr.scale(0.28,0.1,0.07), tr.translate(0, 0, 5.8)])
        block8.childs += [blocks]

        block9 = sg.SceneGraphNode('block9')
        block9.transform = tr.matmul([tr.scale(0.04,0.16,0.07), tr.translate(0, 0, 5.8)])
        block9.childs += [blocks] 

        # 3 Main Buildings
        block10 = sg.SceneGraphNode('block10')
        block10.transform = tr.matmul([tr.scale(0.1,0.16,0.7), tr.translate(-0.7, 0, 0.8)])
        block10.childs += [blocks]

        block11 = sg.SceneGraphNode('block11')
        block11.transform = tr.matmul([tr.scale(0.1,0.16,0.7), tr.translate(0.7, 0, 0.8)])
        block11.childs += [blocks]

        block12 = sg.SceneGraphNode('block12')
        block12.transform = tr.matmul([tr.scale(0.1,0.1,0.7), tr.translate(0, 0, 0.8)])
        block12.childs += [blocks]

        # Thin 3 Main Buildings
        block13 = sg.SceneGraphNode('block13')
        block13.transform = tr.matmul([tr.scale(0.09,0.14,0.2), tr.translate(-0.7, 0, 4.5)])
        block13.childs += [blocks]

        block14 = sg.SceneGraphNode('block14')
        block14.transform = tr.matmul([tr.scale(0.09,0.14,0.2), tr.translate(0.7, 0, 4.5)])
        block14.childs += [blocks]

        block15 = sg.SceneGraphNode('block15')
        block15.transform = tr.matmul([tr.scale(0.1,0.1,0.2), tr.translate(0, 0, 4.59)])
        block15.childs += [blocks]

        # Thinner 3 Main Buildings
        block16 = sg.SceneGraphNode('block16')
        block16.transform = tr.matmul([tr.scale(0.08,0.12,0.2), tr.translate(-0.7, 0, 4.6)])
        block16.childs += [blocks]

        block17 = sg.SceneGraphNode('block17')
        block17.transform = tr.matmul([tr.scale(0.08,0.12,0.2), tr.translate(0.7, 0, 4.6)])
        block17.childs += [blocks]

        # Union of the blocks of the Building
        building = sg.SceneGraphNode('building')
        building.childs += [ block1, block2, block3, block4, block5, block6, block7, block8, block9, 
                            block10, block11, block12, block13, block14, block15, block16, block17]

        # Floor
        floor = sg.SceneGraphNode('floor')
        floor.transform = tr.scale(1, 1, 0)
        floor.childs += [gpuFloor]

        # Union of all elemnts
        whole = sg.SceneGraphNode('whole')
        whole.childs += [floor, building ]

        self.model = whole
        self.lightning = np.array([0,3/4,1])

    def lightnings(self, floorPipeline,buildingPipeline, view):
        glUseProgram(floorPipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(floorPipeline.shaderProgram, "La"),self.lightning[0],self.lightning[1],self.lightning[2])
        glUniform3f(glGetUniformLocation(floorPipeline.shaderProgram, "Ld"),self.lightning[0],self.lightning[1],self.lightning[2])
        glUniform3f(glGetUniformLocation(floorPipeline.shaderProgram, "Ls"),self.lightning[0],self.lightning[1],self.lightning[2])

        glUniform3f(glGetUniformLocation(floorPipeline.shaderProgram, "lightPosition"), 10, 10, 105)
        glUniform3f(glGetUniformLocation(floorPipeline.shaderProgram, "viewPosition"), view[0], view[1],
                    view[2])
        glUniform1ui(glGetUniformLocation(floorPipeline.shaderProgram, "shininess"), 100)

        glUniform1f(glGetUniformLocation(floorPipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(floorPipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(floorPipeline.shaderProgram, "quadraticAttenuation"), 0.01)

        glUseProgram(buildingPipeline.shaderProgram)
        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(floorPipeline.shaderProgram, "La"),self.lightning[0],self.lightning[1],self.lightning[2])
        glUniform3f(glGetUniformLocation(floorPipeline.shaderProgram, "Ld"),self.lightning[0],self.lightning[1],self.lightning[2])
        glUniform3f(glGetUniformLocation(floorPipeline.shaderProgram, "Ls"),self.lightning[0],self.lightning[1],self.lightning[2])

        glUniform3f(glGetUniformLocation(buildingPipeline.shaderProgram, "lightPosition"), 10, 10, 105)
        glUniform3f(glGetUniformLocation(buildingPipeline.shaderProgram, "viewPosition"), view[0], view[1],
                    view[2])
        glUniform1ui(glGetUniformLocation(buildingPipeline.shaderProgram, "shininess"), 100)

        glUniform1f(glGetUniformLocation(buildingPipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(buildingPipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(buildingPipeline.shaderProgram, "quadraticAttenuation"), 0.01)

    def draw(self, floorPipeline, buildingPipeline, projection, view):

        glUseProgram(floorPipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(floorPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(floorPipeline.shaderProgram, "Kd"), 0.9, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(floorPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        glUniformMatrix4fv(glGetUniformLocation(floorPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(floorPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        sg.drawSceneGraphNode(sg.findNode(self.model, 'floor'), floorPipeline, 'model')

        glUseProgram(buildingPipeline.shaderProgram)       
        glUniform3f(glGetUniformLocation(buildingPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(buildingPipeline.shaderProgram, "Kd"), 0.9, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(buildingPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        glUniformMatrix4fv(glGetUniformLocation(buildingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(buildingPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        sg.drawSceneGraphNode(sg.findNode(self.model, 'building'), buildingPipeline, 'model' )

class WillisTower(object):

    def __init__(self, floorPipeline, buildingPipeline):

        gpuFloor = createTextureGPUShape(bs.createTextureNormalsCube(),"piso Willis Tower.png", floorPipeline)
        gpuBlocks = createSimpleGPUShape(bs.createColorNormalsCube(1/2,1/2,1/2), buildingPipeline)

        # Block
        # 1 2 3
        # 4 5 6
        # 7 8 9
        blocks = sg.SceneGraphNode('block')
        blocks.transform = tr.scale(1/7,1/7,0.8)
        blocks.childs += [gpuBlocks]

        # Different Blocks
        block1 = sg.SceneGraphNode('block1')
        block1.transform = tr.matmul([ tr.translate(-1/7,1/7,0.4),tr.scale(1,1,1)])
        block1.childs += [blocks]
        
        block2 = sg.SceneGraphNode('block2') # Se mueveu en +y
        block2.transform = tr.matmul([ tr.translate(0,1/7,0.56), tr.scale(1,1,1.4)])
        block2.childs += [blocks]

        block3 = sg.SceneGraphNode('block3')
        block3.transform = tr.matmul([tr.translate(1/7,1/7,0.48),tr.scale(1,1,1.2)])
        block3.childs += [blocks]

        block4 = sg.SceneGraphNode('block4') # Se mueve en -x
        block4.transform = tr.matmul([tr.translate(-1/7,0,0.56), tr.scale(1,1,1.4)])
        block4.childs += [blocks]

        block5 = sg.SceneGraphNode('block5') # No se hace translacion
        block5.transform = tr.matmul([ tr.translate(0,0,0.72), tr.scale(1,1,1.8)])
        block5.childs += [blocks]

        block6 = sg.SceneGraphNode('6') # Se mueve en +x
        block6.transform = tr.matmul([tr.translate(1/7,0,0.72), tr.scale(1,1,1.8)])
        block6.childs += [blocks]

        block7 = sg.SceneGraphNode('block7')
        block7.transform = tr.matmul([tr.translate(-1/7,-1/7,0.48), tr.scale(1,1,1.2)])
        block7.childs += [blocks]

        block8 = sg.SceneGraphNode('block8') # Se mueve en -y
        block8.transform = tr.matmul([tr.translate(0,-1/7,0.56), tr.scale(1,1,1.4)])
        block8.childs += [blocks]

        block9 = sg.SceneGraphNode('block9')
        block9.transform = tr.matmul([tr.translate(1/7,-1/7,0.4), tr.scale(1,1,1)])
        block9.childs += [blocks]

        # Union of the blocks of the Building
        building = sg.SceneGraphNode('building')
        building.childs += [ block1, block2, block3, block4, block5, block6, block7, block8, block9]

        # Floor
        floor = sg.SceneGraphNode('floor')
        floor.transform = tr.scale(1, 1, 0)
        floor.childs += [gpuFloor]

        # Union of all elemnts
        whole = sg.SceneGraphNode('whole')
        whole.childs += [floor, building ]

        self.model = whole
        self.lightning = np.array([1,3/4,0])

    def lightnings(self, floorPipeline, buildingPipeline,view):
        glUseProgram(floorPipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(floorPipeline.shaderProgram, "La"), self.lightning[0],self.lightning[1],self.lightning[2])
        glUniform3f(glGetUniformLocation(floorPipeline.shaderProgram, "Ld"), self.lightning[0],self.lightning[1],self.lightning[2])
        glUniform3f(glGetUniformLocation(floorPipeline.shaderProgram, "Ls"), self.lightning[0],self.lightning[1],self.lightning[2])

        glUniform3f(glGetUniformLocation(floorPipeline.shaderProgram, "lightPosition"), 5, 5, 5)
        glUniform3f(glGetUniformLocation(floorPipeline.shaderProgram, "viewPosition"), view[0], view[1],
                    view[2])
        glUniform1ui(glGetUniformLocation(floorPipeline.shaderProgram, "shininess"), 100)

        glUniform1f(glGetUniformLocation(floorPipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(floorPipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(floorPipeline.shaderProgram, "quadraticAttenuation"), 0.01)

        glUseProgram(buildingPipeline.shaderProgram)
        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(buildingPipeline.shaderProgram, "La"), self.lightning[0],self.lightning[1],self.lightning[2])
        glUniform3f(glGetUniformLocation(buildingPipeline.shaderProgram, "Ld"), self.lightning[0],self.lightning[1],self.lightning[2])
        glUniform3f(glGetUniformLocation(buildingPipeline.shaderProgram, "Ls"), self.lightning[0],self.lightning[1],self.lightning[2])

        glUniform3f(glGetUniformLocation(buildingPipeline.shaderProgram, "lightPosition"), 5, 5, 5)
        glUniform3f(glGetUniformLocation(buildingPipeline.shaderProgram, "viewPosition"), view[0], view[1],
                    view[2])
        glUniform1ui(glGetUniformLocation(buildingPipeline.shaderProgram, "shininess"), 100)

        glUniform1f(glGetUniformLocation(buildingPipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(buildingPipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(buildingPipeline.shaderProgram, "quadraticAttenuation"), 0.01)

    def draw(self, floorPipeline, buildingPipeline, projection, view):
        
        glUseProgram(floorPipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(floorPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(floorPipeline.shaderProgram, "Kd"), 0.9, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(floorPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        glUniformMatrix4fv(glGetUniformLocation(floorPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(floorPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        sg.drawSceneGraphNode(sg.findNode(self.model, 'floor'), floorPipeline, 'model')

        glUseProgram(buildingPipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(buildingPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(buildingPipeline.shaderProgram, "Kd"), 0.9, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(buildingPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        glUniformMatrix4fv(glGetUniformLocation(buildingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(buildingPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        sg.drawSceneGraphNode(sg.findNode(self.model, 'building'), buildingPipeline, 'model' )

class BurjAlArab(object):
        
    def __init__(self, floorPipeline, buildingPipeline):
        
        gpuFloor = createTextureGPUShape( bs.createTextureNormalsCube(), "piso Burj Al Arab.png", floorPipeline)
        gpuBlocks = createSimpleGPUShape(bs.createColorNormalsCube(3/5,3/5,3/5), buildingPipeline)
        
        blocks = sg.SceneGraphNode("blockcs")
        blocks.transform = tr.scale(1/2,1/2,1)
        blocks.childs = [gpuBlocks]

        block1 = sg.SceneGraphNode("block1")
        block1.transform = tr.matmul([tr.translate(0,0,1/2), tr.scale(1/2,1/2,1)])
        block1.childs = [blocks]

        block2 = sg.SceneGraphNode("block2")
        block2.transform = tr.matmul([tr.scale(1/4,1/4,1/2),tr.translate(0,0,2)])
        block2.childs = [blocks]

        # Union of the blocks of the Building
        building = sg.SceneGraphNode('building')
        building.childs += [block1, block2]

        # Floor
        floor = sg.SceneGraphNode('floor')
        floor.transform = tr.scale(1, 1, 0)
        floor.childs += [gpuFloor]

        # Union of all elemnts
        whole = sg.SceneGraphNode('whole')
        whole.childs += [floor, building ]

        self.model = whole
        self.lightning = np.array([1,1,0])

    def lightnings(self, floorPipeline, buildingPipeline, view):

        glUseProgram(floorPipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(floorPipeline.shaderProgram, "La"), self.lightning[0],self.lightning[1],self.lightning[2])
        glUniform3f(glGetUniformLocation(floorPipeline.shaderProgram, "Ld"), self.lightning[0],self.lightning[1],self.lightning[2])
        glUniform3f(glGetUniformLocation(floorPipeline.shaderProgram, "Ls"), self.lightning[0],self.lightning[1],self.lightning[2])

        glUniform3f(glGetUniformLocation(floorPipeline.shaderProgram, "lightPosition"), 5, 5, 5)
        glUniform3f(glGetUniformLocation(floorPipeline.shaderProgram, "viewPosition"), view[0], view[1],
                    view[2])
        glUniform1ui(glGetUniformLocation(floorPipeline.shaderProgram, "shininess"), 100)

        glUniform1f(glGetUniformLocation(floorPipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(floorPipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(floorPipeline.shaderProgram, "quadraticAttenuation"), 0.01)

        glUseProgram(buildingPipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(buildingPipeline.shaderProgram, "La"), self.lightning[0],self.lightning[1],self.lightning[2])
        glUniform3f(glGetUniformLocation(buildingPipeline.shaderProgram, "Ld"), self.lightning[0],self.lightning[1],self.lightning[2])
        glUniform3f(glGetUniformLocation(buildingPipeline.shaderProgram, "Ls"), self.lightning[0],self.lightning[1],self.lightning[2])

        glUniform3f(glGetUniformLocation(buildingPipeline.shaderProgram, "lightPosition"), 5, 5, 5)
        glUniform3f(glGetUniformLocation(buildingPipeline.shaderProgram, "viewPosition"), view[0], view[1],
                    view[2])
        glUniform1ui(glGetUniformLocation(buildingPipeline.shaderProgram, "shininess"), 100)

        glUniform1f(glGetUniformLocation(buildingPipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(buildingPipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(buildingPipeline.shaderProgram, "quadraticAttenuation"), 0.01)



    def draw(self, floorPipeline, buildingPipeline, projection, view):
        glUseProgram(floorPipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(floorPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(floorPipeline.shaderProgram, "Kd"), 0.9, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(floorPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        glUniformMatrix4fv(glGetUniformLocation(floorPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(floorPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        sg.drawSceneGraphNode(sg.findNode(self.model, 'floor'), floorPipeline, 'model')
        
        glUseProgram(buildingPipeline.shaderProgram)


        glUniform3f(glGetUniformLocation(buildingPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(buildingPipeline.shaderProgram, "Kd"), 0.9, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(buildingPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        glUniformMatrix4fv(glGetUniformLocation(buildingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(buildingPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        sg.drawSceneGraphNode(sg.findNode(self.model, 'building'), buildingPipeline, 'model')