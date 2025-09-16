import socket, random, threading, json, time

# Configurações do servidor
HOST = "0.0.0.0"
PORT = 55555
DEFAULT_PRINTER = "Placar Atual"
users = 0
clients = {}  # Dicionário: {'nickname': client_socket}

current_letter = None
game_on = False
categories = list()
current_points = 10
answers = {}
round_points = {}


def read_commands():
    global game_on, users
    while True:
        command = input("")
        if command == "start":
            print("Começando o jogo!")
            broadcast("Começando o jogo!\n".encode("utf-8"))
            game_on = True
            game_start()

        if command == "end":
            game_on = False

        if command == "scores":
            broadcast_scores(clients, DEFAULT_PRINTER)

        if command == "list":
            users_list = list(clients.keys())
            print(f"Atualmente {users} Jogadores ativos!")
            print(f"Usuários conectados: {users_list}")

        if command == "kick":
            nickname_to_kick = input("Digite o nickname do usuario a ser removido: ")
            if nickname_to_kick in clients:
                client_socket = clients[nickname_to_kick]["socket"]
                client_socket.send("Você foi desconectado do servidor.".encode("utf-8"))
                client_socket.close()
                del clients[nickname_to_kick]
                broadcast(f"{nickname_to_kick} foi desconectado.\n".encode("utf-8"))
            else:
                print(f"Usuário '{nickname_to_kick}' não encontrado.")


def broadcast_scores(dict, printer):
    score_list = []
    for nickname, client_info in dict.items():
        score_list.append({"nickname": nickname, "score": client_info["score"]})

    ranking = sorted(score_list, key=lambda x: x["score"], reverse=True)

    message_text = f"\n=== {printer} ===\n"
    for pos, item in enumerate(ranking, start=1):
        message_text += f"{pos}º lugar: {item['nickname']} com {item['score']} pontos\n"
    message_text += "====================\n\n"

    broadcast(message_text.encode("utf-8"))

    print(message_text)


def broadcast(message):
    for client_info in clients.values():
        client_info["socket"].send(message)


def handle_client(client_socket, nickname):
    global game_on, users, current_points, answers, round_points

    while True:
        try:

            message = client_socket.recv(1024)
            if not message:
                break
            msg_decoded = message.decode("utf-8").strip()

            answers[nickname] = msg_decoded
            print(f"Resposta de {nickname}: {msg_decoded}")
            user_answers = json.loads(msg_decoded)

            # valida todas as respostas do jogador
            answers_validation = all(
                len(ans) > 2 and ans[0].upper() == current_letter
                for ans in user_answers
            )

            if not answers_validation:
                client_socket.send(
                    "Sua resposta foi inválida, você não receberá pontos!\n".encode(
                        "utf-8"
                    )
                )
                round_points[nickname]["score"] = 0
            else:
                clients[nickname]["score"] += current_points

                if nickname not in round_points:
                    round_points[nickname] = {"score": 0}

                round_points[nickname]["score"] += current_points

                client_socket.send(
                    f"Resposta válida + {current_points} Pontos\n".encode("utf-8")
                )
                if current_points >= 3:
                    current_points -= 2
                else:
                    current_points = 0

            # se todos já responderam, fecha a rodada
            if len(answers) == len(clients):
                print("Todos responderam! Rodada encerrada.")

                broadcast_scores(round_points, "Placar da Rodada")
                for client_info in round_points.values():
                    client_info["score"] = 0

                broadcast_scores(clients, DEFAULT_PRINTER)
                current_points = 10
                answers.clear()

                if game_on:
                    game_start()
                else:
                    print("Jogo encerrado!")
                    broadcast("Jogo encerrado!\n".encode("utf-8"))
                    broadcast_scores(clients, DEFAULT_PRINTER)

                    for client_info in clients.values():
                        client_info["score"] = 0

        except:
            print(f"O usuário {nickname} se desconectou.")
            del clients[nickname]
            client_socket.close()
            broadcast(f"{nickname} saiu do chat!\n".encode("utf-8"))
            users -= 1
            break


def start_server():
    global users, categories

    category = input("Digite as categorias separadas por enter:")
    categories = list()

    while category != "":
        categories.append(category)
        category = input()

    print(f"Categorias do jogo: {categories}")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Servidor de Stop iniciado em {HOST}:{PORT}")

    command_thread = threading.Thread(target=read_commands)
    command_thread.daemon = True
    command_thread.start()

    while True:
        try:
            client_socket, addr = server.accept()
            print(f"Conexão aceita de {addr[0]}:{addr[1]}")
            users += 1
            print(f"Atualmente {users} Jogadores ativos!\n")
            client_socket.send(f"Categorias do jogo: {categories}\n".encode("utf-8"))

            # Pede o nickname e espera a resposta
            nickname = client_socket.recv(1024).decode("utf-8")

            # Armazena o cliente com o score inicial
            clients[nickname] = {"socket": client_socket, "score": 0}

            # Inicia a thread para o cliente
            thread = threading.Thread(
                target=handle_client, args=(client_socket, nickname)
            )
            thread.start()

            # Anuncia a entrada do novo usuário para todos os clientes
            broadcast(f"{nickname} entrou no servidor!\n".encode("utf-8"))
            client_socket.send(
                f"Aguarde todos entrarem e o Server Iniciar!\n".encode("utf-8")
            )
        except Exception as e:
            print(f"Erro ao aceitar nova conexão: {e}")
            print(users)


def game_start():
    global current_letter, categories
    current_letter = random.choice("abcdefghijklmnopqrstuvwxyz").upper()
    print(f"Letra da rodada: {current_letter}")
    broadcast(f"A letra dessa rodada é: {current_letter}\n".encode("utf-8"))
    broadcast(f"Categorias do jogo: {categories}\n".encode("utf-8"))


if __name__ == "__main__":
    start_server()
