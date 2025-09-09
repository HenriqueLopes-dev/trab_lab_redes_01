import socket
import threading
import json
import random

# Configurações do servidor
HOST = '0.0.0.0'
PORT = 55555

clients = {} # Dicionário: {'nickname': client_socket}

def read_commands():
    while(True):
        command = input("")
        if(command == "start"):
            print("Comecando o jogo!")
            letra_rodada = random.choice("abcdefghijklmnopqrstuvwxyz").upper()
            print(letra_rodada)
            broadcast("Começando o Jogo!".encode('utf-8'))
            broadcast(f"A letra dessa rodada é: {letra_rodada}".encode('utf-8'))
        if(command == 'scores'):
            broadcast_scores()
        if(command == "list"):
            users_list = list(clients.keys())
            print(f"Usuários conectados: {users_list}")
        if(command == "kick"):
            nickname_to_kick = input("Digite o nickname do usuario a ser removido: ")
            if nickname_to_kick in clients:
                client_socket = clients[nickname_to_kick]
                client_socket.send("Você foi desconectado do servidor.".encode('utf-8'))
                client_socket.close()
                del clients[nickname_to_kick]
                broadcast(f"{nickname_to_kick} foi desconectado.".encode('utf-8'))
            else:
                print(f"Usuário '{nickname_to_kick}' não encontrado.")
                
def broadcast_scores():
    score_list = []
    for nickname, client_info in clients.items():
        score_list.append({'nickname': nickname, 'score': client_info['score']})

    # Serializa a lista de dicionários em uma string JSON
    json_string = json.dumps(score_list)

    # Adiciona um marcador para o cliente identificar o tipo de mensagem
    message = f"SCORES:{json_string}".encode('utf-8')

    # Envia a mensagem para todos os clientes
    broadcast(message)

def broadcast(message):
    # A nova iteração percorre os valores do dicionário clients
    for client_info in clients.values():
        client_info['socket'].send(message)

def handle_client(client_socket, nickname):
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break
            # Se desejar adicionar pontuação, este é o local
            # Exemplo: Se o usuário digitar 'ganhei', aumente o score
            if message.decode('utf-8').strip().lower() == 'ganhei':
                clients[nickname]['score'] += 10
                # Você pode chamar o broadcast de scores aqui, ou no final do roteiro.
                broadcast_scores()

            broadcast(f"{nickname}: ".encode('utf-8') + message)
        except:
            print(f"O usuário {nickname} se desconectou.")
            del clients[nickname]
            client_socket.close()
            broadcast(f"{nickname} saiu do chat!".encode('utf-8'))
            break

def start_server():

    categoria = input("Digite as categorias separadas por enter:")
    categorias = list()

    while(categoria != ""):
        categorias.append(categoria)
        categoria = input()

    print(f"Categorias do jogo: {categorias}")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Servidor de chat iniciado em {HOST}:{PORT}")

    command_thread = threading.Thread(target=read_commands)
    command_thread.daemon = True
    command_thread.start()

    while True:
        try:
            client_socket, addr = server.accept()
            print(f"Conexão aceita de {addr[0]}:{addr[1]}")
            client_socket.send(f"Categorias do jogo: {categorias}".encode('utf-8'))

            # Pede o nickname e espera a resposta
            nickname = client_socket.recv(1024).decode('utf-8')

            # Armazena o cliente com o score inicial
            clients[nickname] = {'socket': client_socket, 'score': 0}

            # Inicia a thread para o cliente
            thread = threading.Thread(target=handle_client, args=(client_socket, nickname))
            thread.start()

            # Anuncia a entrada do novo usuário para todos os clientes
            broadcast(f"{nickname} entrou no chat!".encode('utf-8'))
        except Exception as e:
            print(f"Erro ao aceitar nova conexão: {e}")

if __name__ == "__main__":
    start_server()
