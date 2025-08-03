import socket
import struct
import pickle
import base64
import threading
import time
import queue
import logging

logger = logging.getLogger(__name__)

queues = {'received': queue.Queue()}
connection_socket = None
threads = [threading.Thread() for _ in range(2)]  # list to hold threads
# encode_ip function for full IP

# encode ip to short form (server)
# works with full IPv4 addresses and ports
def encode_ip(address: tuple[str, int]) -> str:
    ip, port = address
    packed_ip = socket.inet_aton(ip)
    packed_port = struct.pack("!H", port)
    combined = packed_ip + packed_port
    return base64.urlsafe_b64encode(combined).decode().rstrip("=") # remove padding


# decode short form to ip
# works with full IPv4 addresses and ports
def decode_ip(encoded: str) -> tuple[str, int]:
    padded = encoded + "=" * (-len(encoded) % 4)  # add padding back
    combined = base64.urlsafe_b64decode(padded)
    ip = socket.inet_ntoa(combined[:4])
    port = struct.unpack("!H", combined[4:])[0]
    return ip, port


# server side function to create a game lobby
def create_lobby_server():
    global threads
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((socket.gethostbyname(socket.gethostname()), 0))
    print(s.getsockname())
    lobby_code = encode_ip(s.getsockname())
    threads[0] = threading.Thread(target=listen_for_connections, args=(s,), daemon=True)
    threads[0].start()

    return lobby_code


def listen_for_connections(s: socket.socket):
    global connection_socket
    with s:
        s.listen()
        con, addr = s.accept()
        connection_socket = con
        with con:
            while True:
                try:
                    data = con.recv(4096)
                    if not data:
                        break
                    queues['received'].put(pickle.loads(data))
                except (ConnectionResetError, EOFError, ConnectionAbortedError):
                    logger.error(f"Connection with {addr} closed.")
                    break


# client side function to join a game lobby
def join_lobby_player(address: tuple[str, int]):
    global threads

    def connect_thread():
        global connection_socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect(address)
                connection_socket = s
                print(f"Connected to lobby at {address}")
                while True:
                    try:
                        data = s.recv(4096)
                        if not data:
                            break
                        queues['received'].put(pickle.loads(data))
                    except (ConnectionResetError, EOFError, ConnectionAbortedError):
                        logger.error(f"Connection with server closed.")
                        break
            except ConnectionRefusedError:
                print(f"Could not connect to server at {address}. Is the server running?")
            except Exception as e:
                print(f"An error occurred: {e}")

    threads[1] = threading.Thread(target=connect_thread, daemon=True)
    threads[1].start()


def send_data(data):
    global connection_socket
    if connection_socket:
        try:
            # noinspection PyUnresolvedReferences
            connection_socket.sendall(pickle.dumps(data))
        except (ConnectionResetError, BrokenPipeError):
            logger.error("Failed to send data. Connection lost.")


if __name__ == "__main__":
    # testing usage
    time.sleep(1)
    x = input("Enter 's' to start server or 'j' to join as player: ")
    if x == "s":
        create_lobby_server()
    elif x == "j":
        code = input("Enter a secret code: ")
        server_address = decode_ip(code)
        join_lobby_player(server_address)





# old code

'''def turn(game_data, current_player: int):
    player = game_data.players[current_player]
    print(f"{player.name}'s turn")

    while True:
        try:
            x = int(input("Enter x coordinate to shoot: "))
            y = int(input("Enter y coordinate to shoot: "))
            if 0 <= x < game_data.size and 0 <= y < game_data.size:
                break
            else:
                print(f"Coordinates must be between 0 and {game_data.size-1}.")
        except ValueError:
            print("Invalid input. Please enter integers for coordinates.")

    result = player.player_board.shoot_cell(x, y)
    if result == 1:
        print("Hit!")
    elif result == 0:
        print("Miss!")
    else:
        print("Already shot at this cell.")
'''