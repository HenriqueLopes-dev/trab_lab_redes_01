import socket
import threading
import json
import ast

HOST = "127.0.0.1"  # Use 127.0.0.1 para testar localmente
PORT = 55555

nickname = input("Digite seu nome de usuário: ")


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
round_active = False
round_letter = ""
categories = list()


def receive_messages():
    global round_active, round_letter, categories
    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            print(message)
            for line in message.splitlines():

                if "A letra dessa rodada é:" in line:
                    round_active = True
                    round_letter = line.split(":", 1)[1].strip()

                if "Categorias do jogo:" in line:
                    list_part = line.split(":", 1)[1].strip()
                    categories = ast.literal_eval(list_part)

        except:
            print("Ocorreu um erro! Desconectando do servidor.")
            client.close()
            break


receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

client.send(nickname.encode("utf-8"))


def send_messages():
    global round_active, round_letter, categories
    while True:
        if round_active:
            print("Digite suas respostas para os seguintes temas:\n")
            answers = []
            for category in categories:
                answer = input(f"-{category}: ")
                answers.append(answer)

            message = json.dumps(answers)
            client.send(message.encode("utf-8"))
            print("Resposta enviada ao Servidor!\n")
            print("Aguarde a próxima rodada\n")
            round_active = False


send_thread = threading.Thread(target=send_messages)
send_thread.start()
