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


qualidade = 9

class ABRv1(IR2A): # define a qualidade do segmento de video


    def __init__(self, id):
        IR2A.__init__(self, id)
        self.parsed_mpd = ''
        self.qi = []

    def handle_xml_request(self, msg):
        # Recebe mendagem da camada superior Player no formato base.Message e
        # encaminha a camada de inferior ConnectionHandler
        # Aqui podemos executar alguma operacao relacionada com a requisicao
        # do arquivo descritor mpd.


        # passa mensagem adiante para o ConnectionHandler
        self.send_down(msg)

    def handle_xml_response(self, msg):
        # Recebe uma mensagem do tipo base.Message da camada inferior ConnectionHandler que eh a 
        # resposta a requisicao ao arquivo mpd. O playload dessa mensagem eh o conteudo xml do arquivo
        # mpd recuperado pelo servidor HTTP. Seu conteudo pode ser acessado pelo metodo
        # msg.get_playload().
        # Aqui podemos realiazar operacoes com a mensagem recebida, como verificar
        # a lista de qualidades possiveis do arquivo mpd.
        # Por fim devemos enviar a mensagem para a camada superior Player.


        # getting qi list
        self.parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = self.parsed_mpd.get_qi()

        # passa mensagem adiante para o Player
        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        # Recebe uma mensagem do tipo base.SSMessage, que representa a requisicao
        # de um segmento de video (o proximo segmento de video), da camada seperior Player.
        # A qualidade deve ser defeinida nessa funcao, por meio do metodo msg.add quality id(...).
        # Por fim, eviar a mensagem gerada na camada superior Player para a
        # camada inferior ConnectionHandler.


        # Tupla. Primeiro o momento em que o dado foi coletado e
        # o segundo se foi possivel (1) ou nao (0) reproduzir o video.
        # Se nao foi, diminuimos  a qualidade.
        status = self.whiteboard.get_playback_history()

        # Tupla. Primeiro o momento em que o dado foi coletado e
        # o segundo o tamanho do buffer observado durante a reproducao do video.
        # Se o buffer for muito pequeno (o quao pequeno?) aumentamos a qualidade
        # para enviar os novos segmentos mais devagar. ????
        buffer = self.whiteboard.get_playback_buffer_size()

        # Precisamos calcular o tempo entre a requisicao (handle_segment_size_request)
        # e a resposta (handle_xml_response) para, juntamento com o "tamanho"
        # calcular a taxa de transferencia

        #int taxa = tamanho/tempo 

        # definindo o pedido como de menor qualidade

        # acrescentar a taxa depois
        # como acessar os elementos da tupla status e buffer?



        #TAMNHO MAXIMO DO BUFFER 60 (se buffer = 60, buffer cheio)

        global qualidade

        # ABR 1
        #msg.add_quality_id(self.qi[0])
        # ABR 2
        #msg.add_quality_id(self.qi[19])

        # ABR 3
        if(status):
            print("status = " + str(status[-1][1]))
            if(qualidade < 19):
                if(status[-1][1] == 1 and buffer[-1][1] < 30):
                    qualidade += 1
                else:
                    qualidade = (int)(qualidade/2)
            if(status[-1][1] == 0 or buffer[-1][1] >= 30):
                qualidade = (int)(qualidade/2)

        msg.add_quality_id(self.qi[qualidade])

        #if(status == 0):
        #    msg.add_quality_id(self.qi[5]) 
        #if(status == 1):
        #    msg.add_quality_id(self.qi[10]) 



        #if((end - start)%2 == 0):
        #    msg.add_quality_id(self.qi[10])
        #else:
        #    msg.add_quality_id(self.qi[9])  



        #if( (size/(end - start)) > 1 ):
        #     msg.add_quality_id(self.qi[10])
        #else:
        #    msg.add_quality_id(self.qi[10])

        #if((size/(end - start)) > 1 and status == 1)

        #msg.add_quality_id(self.qi[10])


        # passa mensagem adiante para o ConnectionHandler
        self.send_down(msg) 

    def handle_segment_size_response(self, msg):
        # Recebe uma mensagem do tipo base.SSMessage, que representa a resposta
        # da requisicao, da camada inferior ConnectionHandler. Nessa mensagem se encontam
        # todas as informacoes necessarias para a representacao do segmento de video requisitado.
        # Por fim, a mensagem eh enviada para a camada superior Player.



        # Tamanho do segmento recebido
        size = msg.get_bit_length()


        #print("TEMPO DE RESPOSTA: " + str(end - start))

        # passa mensagem adiante para o Player
        self.send_up(msg) 

    def initialize(self):
        # Primeiro metodo a ser executado pela plataforma pyDash.
        # Eh possivel utilizar essa funcao para inicializar os atributo que serao utilizados pelo ABR.
        # Contudo, todos os atributos devem estar declarados no construtor da classe.


        pass

    def finalization(self):
        # Ultimo metodo a ser executado pela plataforma pyDash.
        # Pode ser utiliado para gerar estatisticas finais computadas pelo protocolo ABR.
        
        
        pass
