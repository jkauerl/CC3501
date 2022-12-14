"""
Este archivo generaría todos los modelos que tiene la aplicación. En programas más complicados
tendríamos una cosa así:

src/models/actor/chansey.py
src/models/actor/egg.py
src/models/factory/eggcreator.py

...
Y este archivo sería algo como
src/models/model.py --> sólo importaría los objetos que usa el resto de la aplicación, sin tocar el detalle mismo

from src.models.actor.chansey import Chansey
from src.models.actor.factory import EggCreator
...

Pero aquí, como nuestra app es sencilla, definimos todas las clases aquí mismo.
1. Chansey
2. Los huevos
"""
from asyncio.windows_utils import pipe
from contextlib import ContextDecorator
from re import X
from venv import create
import glfw
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.scene_graph as sg
import grafica.easy_shaders as es
from grafica.assets_path import getAssetPath
from OpenGL.GL import *

from OpenGL.GL import glClearColor, GL_STATIC_DRAW
import random
from typing import List

import numpy as np
import grafica.text_renderer as tx

def create_gpu(shape, texture, map, fill, pipeline):
    gpu = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpu)
    gpu.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    gpu.texture = es.textureSimpleSetup(
        getAssetPath(texture), fill, fill, map, map )
    return gpu


class Score(object): # Clase que se encarga de mostrar el Score en la pantalla

    global score
    def __init__(self, textPipeline,gpuText3DTexture):

        
        self.textPipeline = textPipeline
        self.shapeScore = tx.textToShape(str(score),0.125,0.25)

        self.gpuScore = es.GPUShape().initBuffers()
        self.textPipeline.setupVAO(self.gpuScore)
        self.gpuScore.fillBuffers(self.shapeScore.vertices, self.shapeScore.indices, GL_STATIC_DRAW)
        self.gpuScore.texture = gpuText3DTexture
        
    def draw(self, textPipeline):
        glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "fontColor"), 0,0,0,1)
        glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "backColor"), 0, 0, 0, 0)
        glUniformMatrix4fv(glGetUniformLocation(textPipeline.shaderProgram, "transform"), 1, GL_TRUE,
                        tr.translate(0, -1, 0))
        self.textPipeline.drawCall(self.gpuScore)    


class Background(object):
    def __init__(self,pipeline):

        self.pipeline = pipeline
        self.gpuBackground = create_gpu(bs.createTextureQuad(1,1), "background.jpg", GL_NEAREST, GL_CLAMP_TO_EDGE, pipeline)

        self.pos_x = 0

    def draw(self, pipeline):

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, np.matmul(
            tr.translate(self.pos_x, 1/6, 0),
            tr.scale(2, 5/3, 0)
        ))
        pipeline.drawCall(self.gpuBackground)



class Floor(object): 
    def __init__(self,pipeline,x):

        self.pipeline = pipeline
        self.gpuFloor = create_gpu(bs.createTextureQuad(1, 1),"suelo.jpg" , GL_NEAREST, GL_CLAMP_TO_EDGE, self.pipeline)

        self.pos_x = x

    def draw(self,pipeline):
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, np.matmul(
            tr.translate(self.pos_x, -5/6, 0), 
            tr.scale(2, 1/3, 0)
        ))
        self.pipeline.drawCall(self.gpuFloor)

    def update(self,dt):
        self.pos_x = self.pos_x - dt

class Floors(object): # Clase que contiene dos texturas en un lista
    floors: List["Floor"]

    def __init__(self):
        self.floors = []
        self.on = True

    def create_floor(self, pipeline):
        for i in range(0,2):
            self.floors.append(Floor(pipeline, 0 +i*2))

    def draw(self, pipeline):
        for k in self.floors:
            k.draw(pipeline)

    def update(self, pipeline):
        if self.on == True:
            for k in self.floors:
                k.update(pipeline)

    def swap(self,pipeline): # Funcion que borra el suelo en cierta posicion y lo agrega a la derecha de la pantalla
        
        if self.on == True:
            for k in self.floors:  
                if k.pos_x <= -2:  
                    self.floors.pop(0)
                    self.floors.append(Floor(pipeline,2))


class Die_Or_Win(object): # Clase que interpreta crea las textura para luego ser dibujado si gana o pierde

    def __init__(self, pipeline): 

        self.pipeline = pipeline
        self.gpu_w = create_gpu(bs.createTextureQuad(1,1),'win.png', GL_NEAREST, GL_CLAMP_TO_EDGE, self.pipeline)
        self.gpu_l =  create_gpu(bs.createTextureQuad(1,1), 'wasted.png', GL_NEAREST, GL_CLAMP_TO_EDGE, self.pipeline)

    def draw_w(self,pipeline, pajarito: 'Pajarito'):
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, 
                tr.translate(1/2,0,0),
                tr.scale(1, 1, 0)
            )
            self.pipeline.drawCall(self.gpu_w)
            pajarito.gravity = 0
            pajarito.vy = 0

            
    def draw_l(self,pipeline, pajarito: 'Pajarito'):     
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, 
                tr.translate(0,1/2,0),
                tr.scale(1, 1, 0)
            )
            self.pipeline.drawCall(self.gpu_l)
            pajarito.gravity = 0
            pajarito.vy = 0



class Pajarito(object):

    def __init__(self, pipeline,pos_x,pos_y,vy, gravity):
        # Figuras básicas
        self.pipeline = pipeline
        self.gpuPajarito = create_gpu(bs.createTextureQuad(1, 1), "pajarito.png",GL_NEAREST, GL_CLAMP_TO_EDGE,  self.pipeline)

        self.alive = True
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.vy = vy
        self.gravity = gravity

    def draw(self, pipeline):
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, np.matmul(
            tr.translate(self.pos_x, self.pos_y  , 0), 
            tr.scale(1/6, 1/6, 0)
        ))
        self.pipeline.drawCall(self.gpuPajarito)

    def updatePosition(self, dt): # Funcion de dinamica
        self.vy = self.vy + dt * self.gravity
        self.pos_y = self.pos_y + self.vy * dt

    def move_up(self): # Funcion que hace que se mueva para arriba
        if not self.alive or (self.gravity == 0 and self.vy == 0):
            return
        self.vy =  3/4

    def collide(self, tubos: 'Tubos', floors: "Floors"): # Funcion que detecta colisiones
        if not tubos.on:  
            return

        if self.pos_y <= -15/24: # Detecta si toco el suelo
            self.pos_y = -15/24
            self.vy = 0
            self.gravity = 0
            tubos.on = False
            self.alive = False
            floors.on = False

        for e in tubos.tubos:
            if e.pos_x - 3/16 <= self.pos_x <= e.pos_x + 3/16 and not e.pos_y - 0.156 <= self.pos_y <= e.pos_y + 0.156: # Detecta si toca algun tubo
                
                self.gravity = 0
                self.vy = 0
                tubos.on = False
                self.alive = False
                floors.on = False


class Tubo(object):

    def __init__(self, x, y, pipeline):

        self.pipeline = pipeline
        
        self.gpu_tubo = create_gpu(bs.createTextureQuad(1,3), "tubo.png",  GL_NEAREST, GL_CLAMP_TO_EDGE, self.pipeline)

        self.pos_y = y
        self.pos_x = x
        self.count = 0

    def draw(self,pipeline):

        # Dibujo tubo arriba
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, np.matmul(
            tr.translate(self.pos_x, self.pos_y + 1.7, 0), 
            tr.scale(1/2, -3, 0)
        ))
        self.pipeline.drawCall(self.gpu_tubo)
        # Dibujo tubo abajo
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, np.matmul(
            tr.translate(self.pos_x, self.pos_y - 1.7  , 0), 
            tr.scale(1/2, 3, 0)
        ))
        self.pipeline.drawCall(self.gpu_tubo)

    def counted(self):
        if self.pos_x <= -3/8 and self.count == 0:
            global score
            self.count = 1
            score = score + 1
    
    def update(self, dt):
        self.pos_x = self.pos_x - dt 

class Tubos(object):
    tubos: List['Tubo']

    global score
    score = 0
    def __init__(self):
        self.tubos = []
        self.on = True

    def create_tubo(self, pipeline,N):
        if len(self.tubos) >= N or not self.on:  # No puede haber un máximo de 10 huevos en pantalla
            return
        else:
            for i in range(0,N):
                self.tubos.append(Tubo(1+ 1/4 + i,random.uniform(-1/12,5/12),pipeline))

    def draw(self, pipeline):
        for k in self.tubos: 
            k.draw(pipeline)

    def counting(self): # Funcion que cuenta si un tubo k se contara o no
        if self.on:
            for k in self.tubos:
                k.counted()

    def update(self, dt, tubos: "Tubos"): 
        if self.tubos[-1].pos_x <= -3/8:
            self.on = False
            tubos.on = False
        
        if self.on == True:
            for k in self.tubos:
                k.update(dt)