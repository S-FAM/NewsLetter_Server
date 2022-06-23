from socket import *


class Server:

    response_method_not_allowed = (
        lambda version: f"{version} 405 Method Not Allowed\n\nYou must use GET method"
    )
    response_ok = (
        lambda version, sentence: f"{version} 200 OK\nContent-Type: application/json; charset=utf-8\nConnection: close\n\n{sentence}"
    )

    def __init__(self):
        host = "localhost"
        port = 9999
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen(1)
        print(f"Listening on {host}:{port}")

    def __connect(self):
        """
        클라이언트와 3-way-handshake를 수행하여 연결합니다.

        Return
        ------
        conn : socket
            연결된 클라이언트의 소켓

        addr: str
            연결된 클라이언트의 주소
        """
        return self.sock.accept()

    def __get_news_list(self, data: str):
        """
        저장된 뉴스 리스트를 json으로 반환하는 함수
        """
        # TODO: 저장된 뉴스 리스트를 json으로 반환하는 함수를 작성해야합니다.
        return "{암튼 json 형식임}"

    def __access_check(self, data: str) -> bool:
        data = data.split()
        if data[0] != "GET":
            return False

        return True

    def run(self, verbose=False):
        """
        서버를 실행하는 함수        
        """
        if verbose:
            print("Server Run")
        while True:
            conn, addr = self.__connect()

            if verbose:
                print(f"Connected by {addr}")

            recv_data = conn.recv(1024).decode("utf-8")
            splited_data = recv_data.split()

            # access failed
            if not self.__access_check(splited_data[0]):
                conn.send(Server.response_method_not_allowed(splited_data[2]).encode())
            # access success
            else:
                if verbose:
                    print(f"===Received===\n{recv_data}")
                    print(splited_data)

                sentence = self.__get_news_list(splited_data[1])
                results = Server.response_ok(splited_data[2], sentence).encode()
                print(f"===Sending===\n{results.decode()}")
                conn.send(results)

            conn.close()
            print(f"Disconnected by {addr}")

    def close(self):
        self.sock.close()


if __name__ == "__main__":
    Server().run(verbose=True)

