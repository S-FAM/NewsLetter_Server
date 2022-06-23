from urllib.parse import unquote
from socket import *
import pandas as pd


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

    def __data_to_dict(self, data) -> dict:
        """
        전달받은 데이터를 딕셔너리로 변환하는 함수
        """
        refined_dict = {}
        data = data.split("\n")
        refined_dict["method"] = data[0].split()[0]
        refined_dict["path"] = unquote(data[0].split()[1])[1:]
        refined_dict["version"] = data[0].split()[2]

        for line in data[1:]:
            line = line.rstrip()
            if not line:
                continue

            key, value = line.split(": ")
            refined_dict[key] = value

        return refined_dict

    def __get_news_list(self, path: str, start: int, count: int):
        """
        저장된 뉴스 리스트를 json으로 반환하는 함수
        """
        df = pd.read_csv(f"{path}.csv", delimiter="|", on_bad_lines="skip")
        return df.iloc[start : start + count].to_json(orient="records")

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

            if verbose:
                print(f"===Received===\n{recv_data}")

            refined_data = self.__data_to_dict(recv_data)

            # access failed
            if not self.__access_check(refined_data["method"]):
                conn.send(
                    Server.response_method_not_allowed(refined_data["version"]).encode()
                )

            # access success
            else:
                if verbose:
                    print(refined_data)

                sentence = self.__get_news_list(
                    refined_data["path"],
                    int(refined_data["startIndex"]),
                    int(refined_data["count"]),
                )
                results = Server.response_ok(refined_data["version"], sentence)

                if verbose:
                    print(f"===Sending===\n{results}")
                conn.send(results.encode())

            conn.close()
            print(f"Disconnected by {addr}")

    def close(self):
        self.sock.close()


if __name__ == "__main__":
    Server().run(verbose=True)

