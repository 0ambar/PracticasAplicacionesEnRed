import socket

HOST = "localhost"
PORT = 65432
buffer_size = 1024

def mostrar_estado(comando_serv, tablero):
    if comando_serv == "S-5":
        print("Juego iniciado en PRINCIPIANTE")
        print("Listo para recibir tiros. Ingresa coordenadas en formato LetraNúmero, por ejemplo: A1")
    elif comando_serv == "S-6":
        print("Juego iniciado en AVANZADO")
        print("Listo para recibir tiros. Ingresa coordenadas en formato LetraNúmero, por ejemplo: A1")
    elif comando_serv == "S-7":
        print("Mina pisada")
        minas_str = TCPClientSocket.recv(buffer_size).decode()
        minas = minas_str.split(',')
        for mina in minas:
            fila = int(mina[1:]) - 1
            columna = ord(mina[0].upper()) - ord('A')
            tablero[fila][columna] = "*"
        imprimir_tablero(tablero)
        print("HAS PERIDO!!!")
    elif comando_serv == "S-8":
        print("Casilla ya liberada")
    elif comando_serv == "S-9":
        print("Casilla liberada")
    elif comando_serv == "S-10":
        print("Has ganado el juego!")
    elif comando_serv == "S-11":
        print("Coordenadas fuera del rango, intenta de nuevo")
    else:
        print(f"Mensaje desconocido: {comando_serv}")

def imprimir_tablero(tablero):
    size = len(tablero)
    # Imprimir encabezado de columnas
    encabezado_columnas = "   " + " ".join(chr(65 + i) for i in range(size))
    print(encabezado_columnas)
    
    # Imprimir filas con encabezado de filas
    for i in range(size):
        print(f"{i+1:2} " + " ".join(tablero[i]))

#Función para elegir la dificultad del juego
def generar_tablero(dificultad):
    size = 0
    if dificultad == "1":
        size = 9
    elif dificultad == "2":
        size = 16
    else:
        print("Digite una opción válida")
        return None
    
    tablero = [["-" for _ in range(size)] for _ in range(size)]

    return tablero


try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPClientSocket:
        TCPClientSocket.connect((HOST, PORT))
        print("Conectado al servidor")
        print("Selecciona la dificultad:")
        print("C-1: Principiante (9x9, 10 minas) \nC-2: Avanzado (16x16, 40 minas)")
        dificultad = input("> ")
        TCPClientSocket.sendall(dificultad.encode())
        comando_serv = TCPClientSocket.recv(buffer_size).decode()
        tablero = generar_tablero(dificultad[-1])
        mostrar_estado(comando_serv, tablero)
        imprimir_tablero(tablero)

        while True:
            # realizar_tiro(talero, TCPClientSocket)
            comando_coord = input("Ingresa una coordenada (Ej: A1): ")
            columna = ord(comando_coord[0].upper()) - ord('A') + 1
            fila = int(comando_coord[1])

            TCPClientSocket.sendall(comando_coord.encode())
            comando_serv = TCPClientSocket.recv(buffer_size).decode()
            mostrar_estado(comando_serv, tablero)
            
            if comando_serv == "S-7":
                print("PERDISTE EL JUEGO")
                break
            if comando_serv == "S-10":
                imprimir_tablero(tablero)
                print("GANASTE EL JUEGO!!")
                break
            
            tablero[fila-1][columna-1] = "o"
            imprimir_tablero(tablero)


except ConnectionError as e:
    print(f"Error de conexión: {e}")
except Exception as e:
    print(f"Ocurrió un error: {e}")