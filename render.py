import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import json
import os
import cv2
import numpy as np
from PIL import Image

# Parâmetros do tabuleiro
tamanho = 8
escala = 0.5
metade = tamanho // 2

# Cores
branco = (1, 1, 1)
cinza = (0.2, 0.2, 0.2)
cores = [
    (0.6, 0.3, 0.1),
    (0.9, 0.8, 0.6),
    (0.5, 0.3, 0.2),
    (0.8, 0.7, 0.5),
    (0.5, 0.25, 0.1),
    (0.87, 0.72, 0.53),
    (0.7, 0.5, 0.2),
    (1.0, 0.89, 0.71)
]

# Direção da luz normalizada
light_dir = [0.5, 1.0, 0.7]
length = math.sqrt(sum(l**2 for l in light_dir))
light_dir = [l / length for l in light_dir]

def calcular_normal(v1, v2, v3):
    u = [v2[i] - v1[i] for i in range(3)]
    v = [v3[i] - v1[i] for i in range(3)]
    normal = [
        u[1]*v[2] - u[2]*v[1],
        u[2]*v[0] - u[0]*v[2],
        u[0]*v[1] - u[1]*v[0]
    ]
    length = math.sqrt(sum(n**2 for n in normal))
    return [n / length for n in normal]

def carregar_objeto(path):
    vertices, faces = [], []
    with open(path, 'r') as f:
        for linha in f:
            if linha.startswith('v '):
                vertices.append([float(v) for v in linha.strip().split()[1:]])
            elif linha.startswith('f '):
                face = [int(p.split('/')[0]) - 1 for p in linha.strip().split()[1:]]
                faces.append(face)
    return vertices, faces

def desenhar_objeto_com_iluminacao(vertices, faces, cor):
    glBegin(GL_TRIANGLES)
    for face in faces:
        if len(face) >= 3:
            v1, v2, v3 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
            normal = calcular_normal(v1, v2, v3)
            intensidade = max(0.1, sum(normal[i] * light_dir[i] for i in range(3)))
            cor_iluminada = [min(1.0, c * intensidade) for c in cor]
            glColor3f(*cor_iluminada)
            for idx in face:
                glVertex3fv(vertices[idx])
    glEnd()

def desenhar_quadrado(x, z, cor):
    glColor3f(*cor)
    y = 0
    glBegin(GL_QUADS)
    glVertex3f(x, y, z)
    glVertex3f(x + escala, y, z)
    glVertex3f(x + escala, y, z + escala)
    glVertex3f(x, y, z + escala)
    glEnd()

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    gluPerspective(45, display[0] / display[1], 0.1, 50.0)
    glTranslatef(0.0, -0.5, -6)
    glRotatef(30, 1, 0, 0)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)

    vertices_rainha, faces_rainha = carregar_objeto('rainha.obj')

    with open('historico_execucao.json', 'r') as f:
        historico = json.load(f)

    os.makedirs("frames", exist_ok=True)
    frame_paths = []

    for frame_count, passo in enumerate(historico):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Tabuleiro
        for x in range(tamanho):
            for z in range(tamanho):
                px = (x - metade) * escala
                pz = (z - metade) * escala
                cor = branco if (x + z) % 2 == 0 else cinza
                desenhar_quadrado(px, pz, cor)

        # Rainhas
        for i in range(tamanho):
            glPushMatrix()
            px = (i - metade + 0.5) * escala
            pz = (passo["posicoes"][i] - metade + 0.5) * escala
            glTranslatef(px, 0.001, pz)
            glScalef(0.1, 0.1, 0.1)

            if i == passo["linha"] and passo["coluna"] == passo["posicoes"][i]:
                cor = (1.0, 0.2, 0.2)
            else:
                cor = cores[i]

            desenhar_objeto_com_iluminacao(vertices_rainha, faces_rainha, cor)
            glPopMatrix()

        pygame.display.flip()

        # Captura do framebuffer OpenGL
        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        data = glReadPixels(0, 0, display[0], display[1], GL_RGB, GL_UNSIGNED_BYTE)
        image = np.frombuffer(data, dtype=np.uint8).reshape(display[1], display[0], 3)
        image = np.flipud(image)

        frame_path = os.path.join("frames", f"frame_{frame_count:03d}.png")
        Image.fromarray(image).save(frame_path)
        frame_paths.append(frame_path)

        pygame.time.wait(300)

    pygame.quit()

    # Geração do vídeo
    if frame_paths:
        print("Renderizando vídeo...")

        frame_exemplo = cv2.imread(frame_paths[0])
        altura, largura, _ = frame_exemplo.shape

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter("tentativas_rainhas.mp4", fourcc, 30, (largura, altura))

        for frame_path in frame_paths:
            frame = cv2.imread(frame_path)
            for _ in range(30):
                video.write(frame)

        video.release()
        print("Vídeo salvo como 'tentativas_rainhas.mp4'")

main()
