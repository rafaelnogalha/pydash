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


# globai de controle
qualidade = 0 # comecar com QI menor?
inicio = 0
fim = 0
tamanho = 0
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

        # tempo transcorrido entre o pedido do sgmento e seu recebimento
        global inicio
        tempo = (fim - inicio)

        # taxa de transmissao do pedido anterior
        global taxa_atual
        if(tempo > 0):
            taxa_atual = tamanho/tempo

        # variacao de taxa de transmissao
        global taxa_anterior # taxa de transmissao de dois pedidos atras
        global variacao_taxa
        if(taxa_anterior > 0):
            variacao_taxa = taxa_atual/taxa_anterior # > 1 bom, < 1 ruim
        taxa_anterior = taxa_atual

        # codigo principal
        global qualidade
        global flag_buffer
        if(status): 
            # buffer vazio
            if(buffer[-1][1] <= 20 and qualidade > 0):
                flag_buffer = 1
                qualidade = int(qualidade/1.5)
            # buffer meio vazio
            if(buffer[-1][1] > 20 and buffer[-1][1] <= 30):
                if(variacao_taxa < 1 and qualidade > 0 and flag_buffer == 0):
                    qualidade -= 1
            # buffer meio cheio
            if(buffer[-1][1] > 30 and buffer[-1][1] < 50):
                flag_buffer = 0
                if(variacao_taxa > 1 and qualidade < 19):   
                    qualidade += 1
            # buffer cheio
            if(buffer[-1][1] >= 50):
                if(qualidade < 9):
                    qualidade = 9
                else:
                    qualidade = int(qualidade*1.25)
                    if(qualidade > 19):
                        qualidade = 19
            
        msg.add_quality_id(self.qi[qualidade])

        # inicio da contagem de tempo da requisicao de segmento
        inicio = time.time()

        # passa mensagem adiante para o ConnectionHandler
        self.send_down(msg) 

    def handle_segment_size_response(self, msg):
        # tamanho do segmento recebido
        global tamanho
        tamanho = msg.get_bit_length()

        # fim da contagem de tempo da requisicao de segmento
        global fim
        fim = time.time()

        # passa mensagem adiante para o Player
        self.send_up(msg) 

    def initialize(self):
        pass

    def finalization(self):
        pass