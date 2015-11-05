# TolkienRing
Chat de até quatro máquinas sobre uma rede Token Ring: Trabalho 2 de Redes 1

## Rodando
`chat -p [communicationPort] -s [serverPort] -c`

* -p: porta de comunicação do anel
* -s: porta do servidor de configuração do anel
* -c: Inicia em modo servidor de configuração do anel

## Funcionamento
O TolkienRing é um chat de até 4 máquinas sobre uma rede Token Ring.

A primeira máquina (ou alguma delas, mas só uma) inicia executando em modo de
configuração de rede. Esta máquina é conhecida como servidora (de configuração) do anel. 
Este modo funciona da seguinte maneira:

1. Uma primeira máquina (A) manda um *handshake* (um tipo especial de mensagem) para
a servidora.
    * A servidora responde com o IP e porta do nodo com quem ela se conecta
    * A máquina (A) responde um OK e se conecta
    * Como esta é a primeira máquina, ela se conecta com a servidora
    * A servidora define que esta máquina (A) é o próximo nodo da rede
    * A rede é: [servidora] -> [A] -> [servidora]
* Uma segunda máquina (B) manda o *handshake*
    * A servidora responde com o IP e porta da última máquina que se conectou (A)
    * A máquina (B) responde um OK e se conecta
    * A servidora se conecta com a máquina (B)
    * A rede é: [servidora] -> [B] -> [A] -> [servidora]
* Uma terceira e última máquina (C) manda o *handshake*
    * A servidora responde com o IP e porta da última máquina que se conectou (B)
    * A máquina (C) responde um OK e se conecta
    * A servidora se conecta com a máquina (C)
    * A rede é: [servidora] -> [C] -> [B] -> [A]
* A servidora então cria o bastão da rede e envia para a próxima máquina
* O bastão passa por todas as máquinas e retorna para a servidora
* Vendo que a rede está correta, a servidora envia a primeira mensagem em modo de
broadcast: o nome de todas as máquinas na rede
* As outras máquinas armazenam essa informação para que os usuários possam escolher
para quem querem enviar algo.
* A partir de então, a máquina servidora vira a última máquina da rede (D) e pode
enviar normalmente as mensagens

O modo de configuração da rede pode ser fechado por um comando do usuário com
menos do que 4 máquinas na rede. Caso isso ocorra e uma máquina queira entrar no chat
ela deve enviar o *handhsake* para a porta de configuração (note que existe uma porta
para a configuração da rede e uma para a comunicação do anel) de qualquer máquina.
Ao fazer isso, a máquina entra em modo de configuração e passa o bastão (quando sob sua posse)
pelo anel indicando o modo de configuração. Esta máquina então segue os passos normais
do servidor de configuração.

## Mensagem
A mensagem é definida assim

|Indicador de início|Controle|Origem|Destino|Tamanho|Dados|Paridade|Resposta|
|-------------------|--------|------|-------|-------|-----|---|--------|
|1 Byte|1 Byte|6 Bytes|6 Bytes|1 Byte|<= 1004 Bytes|4 Bytes|1 Byte|

**Controle**

|Token|Monitor|Configuração|Reservado|
|-----|-------|------------|---------|
|1 bit|1 bit|1 bit|5 bits|

## Especificação do trabalho
Implementar um chat entre 4 máquinas montadas como um anel com passagem de bastão temporizado.

Anel deve ser criado logicamente entre 4 servidores do Dinf usando Socket Datagram.

As 4 máquinas **devem** ter acesso de usuário.

Usuário deve digitar primeiro um número (máquina a qual a mensagem é destinada) depois ':' e depois a mensagem.

Exemplo: `1:teste`. Caso especial: `5:mensagem` -> mensagem para todo mundo.

Protocolo: definido pelos membros do trabalho.
* Respostas de carona são obrigatórias
* Protocolo deve especifcar enquadramento (sequencialização/detecção de erros/mensagens)
* Timeout de mensagens que não voltam p/ origem não precisa ser implementado
* Implementar timeout de bastão

Entregar:
* Relatório com o protocolo detalhado e as escolhas de implementação feitas pela equipe
* Nota: 1,0
* Código: por e-mail depois da apresentação
* Em duplas
* Linguagem: qualquer uma
