import socket
import struct
import pickle
import base64
import threading
import time
import queue
from gui_windows import logger

queues = {'received': queue.Queue()}

# Networking state
connection_socket = None  # for 1:1 client connection (legacy 2P client)
server_socket = None  # listening socket on host

# Server/client role & player info
is_server = False
total_players = 2
my_player_id = None  # 0 for host, >=1 for clients after assignment

# On server, track connected clients and their IDs
_server_clients: dict[int, socket.socket] = {}
_server_client_threads: list[threading.Thread] = []

# Simple server-side game coordination
current_turn = 0  # player id whose turn it is
_server_ready: set[int] = set()

threads = [threading.Thread() for _ in range(2)]  # legacy threads list
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
def create_lobby_server(players: int = 2):
    """Start a lobby server. Supports 2 or 4 players.

    Returns a short lobby code that encodes ip:port.
    """
    assert players in (2, 4), "Only 2 or 4 players supported"
    global threads, server_socket, is_server, total_players, my_player_id
    is_server = True
    total_players = players
    my_player_id = 0

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((socket.gethostbyname(socket.gethostname()), 0))
    s.listen()
    server_socket = s
    print(s.getsockname())
    lobby_code = encode_ip(s.getsockname())

    threads[0] = threading.Thread(target=_server_accept_loop, args=(s,), daemon=True)
    threads[0].start()

    return lobby_code


def _server_accept_loop(s: socket.socket):
    """Accept up to total_players-1 clients, assign IDs, and start reader threads."""
    global _server_clients, _server_client_threads
    next_id = 1  # host is 0
    try:
        while True:
            con, addr = s.accept()
            if len(_server_clients) >= (total_players - 1):
                # Too many clients; close connection politely
                try:
                    con.close()
                except Exception:
                    pass
                continue

            pid = next_id
            next_id += 1
            _server_clients[pid] = con

            # Assign ID to client
            try:
                payload = {'type': 'assign', 'player_id': pid, 'total_players': total_players}
                con.sendall(pickle.dumps(payload))
            except Exception:
                logger.exception("Failed to send assign message to client")

            # Notify local queue that a client joined (for UI updates)
            queues['received'].put({'type': 'client_joined', 'player_id': pid, 'connected': len(_server_clients)})

            # Start a reader thread for this client
            t = threading.Thread(target=_server_client_reader, args=(pid, con), daemon=True)
            _server_client_threads.append(t)
            t.start()
    except Exception:
        logger.exception("Server accept loop encountered an error")


def _server_client_reader(pid: int, con: socket.socket):
    """Read messages from a client and broadcast to everyone (including host)."""
    global _server_clients
    with con:
        while True:
            try:
                data = con.recv(4096)
                if not data:
                    break
                obj = pickle.loads(data)
                # Stamp sender id if missing
                if isinstance(obj, dict) and 'from' not in obj:
                    obj['from'] = pid

                # Unified move/result packet handling
                if isinstance(obj, dict):
                    # Ready signal
                    if obj.get('status') == 'ready':
                        _server_on_ready(pid)
                        continue

                    # Unified move/result packet
                    if 'move' in obj and 'to' in obj and 'from' in obj:
                        # Always broadcast to all (including host)
                        _server_broadcast(obj, include_host=True)
                        # If this is a result and it's a miss, advance turn
                        if obj.get('result') == 'miss':
                            _server_advance_turn()
                        continue

                # Default behavior: deliver to host queue and broadcast
                queues['received'].put(obj)
                _server_broadcast(obj, exclude_pid=pid, include_host=False)
            except (ConnectionResetError, EOFError, ConnectionAbortedError):
                logger.error(f"Connection with client {pid} closed.")
                break
            except Exception:
                logger.exception("Error reading from client")
                break
    # Cleanup
    try:
        del _server_clients[pid]
        logger.error(f"Client {pid} disconnected and removed.")
    except KeyError:
        pass
    queues['received'].put({'type': 'client_left', 'player_id': pid, 'connected': len(_server_clients)})


def _server_broadcast(obj: dict, exclude_pid: int | None = None, include_host: bool = True):
    """Broadcast a message to all connected clients. Optionally deliver to host queue too."""
    # Ensure obj has a 'from'
    if isinstance(obj, dict) and 'from' not in obj:
        obj['from'] = my_player_id if my_player_id is not None else 0
    # Send to clients
    for pid, con in list(_server_clients.items()):
        if exclude_pid is not None and pid == exclude_pid:
            continue
        try:
            con.sendall(pickle.dumps(obj))
        except Exception as e:
            logger.error(f"Failed to send to client {pid}, {e=}")
    # Optionally also deliver to host (local queue)
    if include_host:
        queues['received'].put(obj)


def _server_send_to(pid: int, obj: dict):
    # Ensure 'from' exists
    if 'from' not in obj:
        obj['from'] = my_player_id if my_player_id is not None else 0
    con = _server_clients.get(pid)
    if con:
        try:
            con.sendall(pickle.dumps(obj))
        except Exception as e:
            logger.error(f"Failed to send direct message to client {pid}, {e=}")


def _server_on_ready(pid: int):
    _server_ready.add(pid)
    # Host ready is tracked via special call below
    expected_ready = total_players - 1  # all clients
    if len(_server_ready) >= expected_ready and _host_ready_flag:
        # Start game: player 0 begins
        _server_broadcast({'type': 'start', 'turn': current_turn}, include_host=True)


_host_ready_flag = False


def _server_on_host_ready():
    global _host_ready_flag
    _host_ready_flag = True
    expected_ready = total_players - 1
    if len(_server_ready) >= expected_ready:
        _server_broadcast({'type': 'start', 'turn': current_turn}, include_host=True)


def _server_advance_turn():
    global current_turn
    if total_players <= 0:
        return
    current_turn = (current_turn + 1) % total_players
    _server_broadcast({'type': 'turn', 'turn': current_turn}, include_host=True)


# client side function to join a game lobby
def join_lobby_player(address: tuple[str, int]):
    """Join a lobby. Receives an assigned player_id and total_players from server."""
    global threads, is_server, my_player_id, total_players
    is_server = False

    def connect_thread():
        global connection_socket, my_player_id, total_players
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(address)
            connection_socket = s
            print(f"Connected to lobby at {address}")
            while True:
                try:
                    data = s.recv(4096)
                    if not data:
                        break
                    obj = pickle.loads(data)
                    if isinstance(obj, dict) and obj.get('type') == 'assign':
                        my_player_id = obj.get('player_id')
                        total_players = obj.get('total_players', 2)
                    else:
                        queues['received'].put(obj)
                except (ConnectionResetError, EOFError, ConnectionAbortedError):
                    logger.error(f"Connection with server closed.")
                    break
        except ConnectionRefusedError:
            print(f"Could not connect to server at {address}. Is the server running?")
        except Exception as e:
            print(f"An error occurred: {e}")

    threads[1] = threading.Thread(target=connect_thread, daemon=True)
    threads[1].start()


def send_data(data: dict):
    """Send a message into the session.

    - If client: send to server.
    - If server/host: broadcast to all clients and deliver to self.
    """
    global connection_socket
    if not isinstance(data, dict):
        data = {'payload': data}

    # Stamp sender id
    if 'from' not in data:
        data['from'] = my_player_id if my_player_id is not None else 0

    # Unified move/result packet: always broadcast if server, send to server if client
    if is_server:
        if data.get('status') == 'ready':
            _server_on_host_ready()
            return
        # For move/result packets, always broadcast
        if 'move' in data and 'to' in data and 'from' in data:
            _server_broadcast(data, include_host=True)
            if data.get('result') == 'miss':
                _server_advance_turn()
            return
        # Fallback: broadcast
        _server_broadcast(data, include_host=True)
    else:
        if connection_socket:
            try:
                connection_socket.sendall(pickle.dumps(data))
            except (ConnectionResetError, BrokenPipeError):
                logger.error("Failed to send data. Connection lost.")


# --- Small helpers for GUI ---
def get_total_players() -> int:
    return total_players


def get_is_server() -> bool:
    return is_server


def get_my_player_id() -> int | None:
    return my_player_id


def get_connected_clients_count() -> int:
    # For server, number of connected remote clients
    return len(_server_clients)


if __name__ == "__main__":
    # testing usage
    time.sleep(1)
    x = input("Enter 's' to start server or 'j' to join as player: ")
    if x == "s":
        create_lobby_server(players=2)
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