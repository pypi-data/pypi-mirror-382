import click
from snapqrpy.core.server import SnapQRServer
from snapqrpy.core.client import SnapQRClient

@click.group()
def main():
    pass

@main.command()
@click.option('--port', default=8000, help='Server port')
def server(port):
    srv = SnapQRServer(port=port)
    qr = srv.generate_qr()
    qr.show()
    srv.start()

@main.command()
def client():
    cli = SnapQRClient()
    url = cli.scan_qr()
    cli.connect(url)
    cli.request_permission()

if __name__ == '__main__':
    main()
