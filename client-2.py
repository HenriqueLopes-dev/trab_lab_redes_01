import socket
import threading

# Configurações do cliente
HOST = '127.0.0.1' # Use 127.0.0.1 para testar localmente
PORT = 55555

# Pede um nome de usuário para o chat
nickname = input("Digite seu nome de usuário: ")

# Conecta ao servidor
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# Função para receber mensagens do servidor
def receive_messages():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            print(message)
        except:
            print("Ocorreu um erro! Desconectando do servidor.")
            client.close()
            break

# Inicia a thread de recebimento ANTES de enviar o nickname
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

# Espera o servidor pedir o nickname e envia
# Note: Este trecho deve ser executado APENAS UMA VEZ no início.
# O servidor envia 'NICK' e o cliente responde, depois inicia o loop de envio.
client.send(nickname.encode('utf-8'))

# Função para enviar mensagens para o servidor
def send_messages():
    while True:
        message = input("")
        full_message = f'{nickname}: {message}'
        client.send(message.encode('utf-8'))

# Inicia a thread para enviar mensagens após o nickname ser enviado
send_thread = threading.Thread(target=send_messages)
send_thread.start()
