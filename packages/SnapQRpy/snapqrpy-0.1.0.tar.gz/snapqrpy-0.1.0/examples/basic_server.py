from snapqrpy import SnapQRServer

server = SnapQRServer(port=8000)
qr = server.generate_qr()
qr.show()
server.start()
