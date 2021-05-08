# -*- coding: utf-8 -*-
"""
@author: Andre L. Chimpliganond (190010321@aluno.unb.br) 06/04/2021
@author: Rafael Henrique N. de Lima (190036966@aluno.unb.br) 06/04/2021


@description: PyDash Project

First implementation of a ABR algorithm
"""


import time

from player.parser import *
from r2a.ir2a import IR2A


qualidade = 0 # comecar com QI menor?
start = 0
end = 0
size = 0
taxa_atual = 0
taxa_anterior = 0
variacao_taxa = 1
flag_buffer = 0


class ABRv1(IR2A): # define a qualidade do segmento de video

    def __init__(self, id):
        IR2A.__init__(self, id)
        self.parsed_mpd = ''
        self.qi = []

    def handle_xml_request(self, msg):
        self.send_down(msg)

    def handle_xml_response(self, msg):
        # getting qi list
        self.parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = self.parsed_mpd.get_qi()

        # passa mensagem adiante para o Player
        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        status = self.whiteboard.get_playback_history()
        buffer = self.whiteboard.get_playback_buffer_size()

        global start
        t = (end - start)
        #print("tempo = " + str(t))

        global taxa_atual
        if(t > 0):
            taxa_atual = size/t
            #print("taxa_atual = " + str(taxa_atual))

        # variacao de taxa de transmissao
        global taxa_anterior
        global variacao_taxa
        if(taxa_anterior > 0):
            variacao_taxa = taxa_atual/taxa_anterior # > 1 bom, < 1 ruim
        taxa_anterior = taxa_atual
        #print("var = " + str(variacao_taxa))

        start = time.time()
        # print("start = " + str(start))

        global qualidade
        global flag_buffer
        if(status): 
            if(buffer[-1][1] >= 50): # buffer cheio, QI++
                if(qualidade < 9):
                    qualidade = 9
                else:
                    qualidade = int(qualidade*1.25) # crescer nao tao rapido para nao demorar muito o envio esvaziando o buffer
                    if(qualidade > 19): # garante que nao sai dos limites (maior que 19)
                        qualidade = 19
            if(buffer[-1][1] <= 20 and qualidade > 0): # buffer vazio, QI--
                flag_buffer = 1
                qualidade = int(qualidade/1.5) # tinha: if(qualidade > 3):
            if(buffer[-1][1] > 20 and buffer[-1][1] <= 30): # buffer meio vazio
                if(variacao_taxa < 1 and qualidade > 0 and flag_buffer == 0): # flag garante que nao vai diminuir o QI quando estiver voltando a crescer (enchendo o buffer)
                    qualidade -= 1
            if(buffer[-1][1] > 30 and buffer[-1][1] < 50): # buffer meio cheio
                flag_buffer = 0
                if(variacao_taxa > 1 and qualidade < 19):   
                    qualidade += 1

        msg.add_quality_id(self.qi[qualidade])

        # passa mensagem adiante para o ConnectionHandler
        self.send_down(msg) 

    def handle_segment_size_response(self, msg):
        global size
        size = msg.get_bit_length()
        #print("size = " + str(size))

        global end
        end = time.time()
        #print("end = " + str(end))

        # passa mensagem adiante para o Player
        self.send_up(msg) 

    def initialize(self):
        pass

    def finalization(self):
        pass