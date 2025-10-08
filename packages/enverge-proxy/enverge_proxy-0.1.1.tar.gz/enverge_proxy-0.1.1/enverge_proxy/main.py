import logging
import select
import socket
import ssl
import sys
import threading
import time
from dataclasses import dataclass
from urllib.parse import urlparse

import click

logger = logging.getLogger(__name__)


@dataclass
class Config:
    DEFAULT_REMOTE_HOST: str = "colab.enverge.ai"
    DEFAULT_REMOTE_PORT: int = 443
    DEFAULT_LOCAL_HOST: str = "localhost"
    DEFAULT_LOCAL_PORT: int = 8123


class Proxy:
    def __init__(
        self,
        local_host=Config.DEFAULT_LOCAL_HOST,
        local_port=Config.DEFAULT_LOCAL_PORT,
        remote_host=Config.DEFAULT_REMOTE_HOST,
        remote_port=Config.DEFAULT_REMOTE_PORT,
    ):
        self.local_host = local_host
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = True
        self.client_threads = []
        logger.debug(
            f"Proxy initialized with local={local_host}:{local_port}, remote={remote_host}:{remote_port}"
        )

    def start(self):
        try:
            self.server_socket.bind((self.local_host, self.local_port))
            self.server_socket.listen(5)
            logger.debug(f"Proxy server started on {self.local_host}:{self.local_port}")

            while self.running:
                client_socket, addr = self.server_socket.accept()
                logger.info(f"New connection accepted from {addr}")
                client_thread = threading.Thread(
                    target=self.handle_client, args=(client_socket,)
                )
                self.client_threads.append(client_thread)
                client_thread.daemon = True
                client_thread.start()
                logger.debug(f"Started new thread for client {addr}")
        except KeyboardInterrupt:
            logger.debug("Shutting down proxy server...")
            self.running = False
            self.server_socket.close()
            sys.exit(0)
        except Exception as e:
            logger.error(f"Failed to start proxy server: {e}", exc_info=True)
            raise

    def handle_client(self, client_socket):
        client_addr = client_socket.getpeername()
        logger.debug(f"Handling new client connection from {client_addr}")
        try:
            logger.debug("Attempting to receive initial request...")
            request = self.receive_full_request(client_socket)
            if not request:
                logger.warning(f"Empty request received from {client_addr}")
                return

            logger.debug(f"Request received, length: {len(request)} bytes")
            headers = request.split(b"\r\n\r\n")[0].decode("utf-8", "ignore")
            is_websocket = any(
                line.lower().startswith("upgrade: websocket")
                for line in headers.split("\r\n")
            )
            logger.debug(
                f"Request type determined: {'WebSocket' if is_websocket else 'HTTP'}"
            )

            logger.debug(
                f"Attempting connection to remote server {self.remote_host}:{self.remote_port}"
            )

            use_ssl = self.should_use_ssl(request)

            if use_ssl:
                remote_socket = self.create_ssl_connection()
                logger.debug(f"Using SSL connection to {self.remote_host}:443")
            else:
                remote_socket = socket.create_connection(
                    (self.remote_host, self.remote_port)
                )
                logger.debug(
                    f"Using plain connection to {self.remote_host}:{self.remote_port}"
                )

            with remote_socket:
                logger.debug("Remote connection established")
                remote_socket.sendall(request)
                logger.debug(
                    f"Request forwarded to remote server ({len(request)} bytes)"
                )

                if is_websocket:
                    logger.debug("Handling WebSocket upgrade response")
                    upgrade_response = self.receive_full_request(remote_socket)
                    if upgrade_response:
                        client_socket.sendall(upgrade_response)
                        logger.debug("WebSocket connection upgraded successfully")
                        self.forward_data(
                            client_socket, remote_socket, is_websocket=True
                        )
                else:
                    logger.debug("Starting regular HTTP communication")
                    self.forward_data(client_socket, remote_socket, is_websocket=False)

        except Exception as e:
            logger.error(f"Error handling client {client_addr}: {e}", exc_info=True)
        finally:
            client_socket.close()
            logger.debug(f"Closed connection from {client_addr}")

    def should_use_ssl(self, request):
        try:
            request_str = request.decode("utf-8", "ignore").lower()
            return (
                "https://" in request_str
                or self.remote_port == 443
                or "connect" in request_str
            )
        except:
            return self.remote_port == 443

    def create_ssl_connection(self):
        try:
            context = ssl.create_default_context()
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED

            conn = socket.create_connection((self.remote_host, 443))
            ssl_socket = context.wrap_socket(conn, server_hostname=self.remote_host)
            logger.debug(f"SSL connection established to {self.remote_host}:443")
            return ssl_socket
        except Exception as e:
            logger.error(f"Failed to create SSL connection: {e}")
            raise

    def receive_full_request(self, client_socket):
        request = b""
        while True:
            logger.debug("Receiving full request")
            try:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                request += chunk
                if b"\r\n\r\n" in request:
                    headers = request.split(b"\r\n\r\n")[0].decode("utf-8", "ignore")
                    content_length = self.get_content_length(headers)
                    if content_length:
                        body = request.split(b"\r\n\r\n")[1]
                        while len(body) < content_length:
                            chunk = client_socket.recv(4096)
                            if not chunk:
                                break
                            request += chunk
                            body = request.split(b"\r\n\r\n")[1]
                    break
            except socket.error:
                break
        return request

    def get_content_length(self, headers):
        for line in headers.split("\r\n"):
            if line.lower().startswith("content-length:"):
                return int(line.split(":")[1].strip())
        return None

    def forward_data(self, client_socket, remote_socket, is_websocket=False):
        sockets = [client_socket, remote_socket]
        timeout = None if is_websocket else 30

        while True:
            try:
                readable, _, _ = select.select(sockets, [], [], timeout)
                if not readable:
                    if not is_websocket:
                        return
                    continue

                for sock in readable:
                    try:
                        data = sock.recv(4096)
                        if not data:
                            return

                        other_socket = (
                            remote_socket if sock is client_socket else client_socket
                        )
                        other_socket.sendall(data)
                    except (ssl.SSLWantReadError, ssl.SSLWantWriteError):
                        continue
            except (socket.error, ssl.SSLError):
                return


@click.command()
@click.option(
    "--remote-host",
    default=Config.DEFAULT_REMOTE_HOST,
    help=f"Remote host to connect to (default: {Config.DEFAULT_REMOTE_HOST})",
)
@click.option(
    "--local-host",
    default=Config.DEFAULT_LOCAL_HOST,
    help=f"Local host to bind to (default: {Config.DEFAULT_LOCAL_HOST})",
)
@click.option(
    "--local-port",
    default=Config.DEFAULT_LOCAL_PORT,
    type=int,
    help=f"Local port to bind to (default: {Config.DEFAULT_LOCAL_PORT})",
)
@click.option(
    "--remote-port",
    default=Config.DEFAULT_REMOTE_PORT,
    type=int,
    help=f"Remote port to connect to (default: {Config.DEFAULT_REMOTE_PORT})",
)
@click.option("--token", required=True, help="Authentication token for the workspace")
def main(remote_host, local_host, local_port, remote_port, token):
    click.echo("creating Enverge instance", nl=False)
    for _ in range(3):
        click.echo(".", nl=False)
        time.sleep(1)
    click.echo("\ndone ✅")
    time.sleep(1)

    workspace_url = click.style(
        f"http://{local_host}:{local_port}/lab?token={token}", fg="blue", underline=True
    )
    click.echo(f"your local proxy is: {workspace_url}")
    time.sleep(1)

    docs_url = click.style(
        "https://enverge.ai/docs/colab-runtime", fg="blue", underline=True
    )
    click.echo(
        f"follow these instructions: {docs_url} to start using Google Colab with an Enverge Runtime."
    )
    time.sleep(1)

    click.echo(
        click.style("All steps completed successfully! Enjoy your session!", fg="green")
    )

    proxy = Proxy(
        local_host=local_host,
        local_port=local_port,
        remote_host=remote_host,
        remote_port=remote_port,
    )
    try:
        proxy.start()
    except KeyboardInterrupt:
        click.echo("\nShutting down proxy server...")


if __name__ == "__main__":
    main()
