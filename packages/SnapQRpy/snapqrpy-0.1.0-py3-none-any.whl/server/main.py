from snapqrpy.core.server import SnapQRServer

def run_server(port: int = 8000):
    server = SnapQRServer(port=port)
    qr_code = server.generate_qr()
    qr_code.show()
    server.start()

if __name__ == '__main__':
    run_server()
