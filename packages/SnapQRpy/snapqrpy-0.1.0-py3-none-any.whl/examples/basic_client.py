from snapqrpy import SnapQRClient

client = SnapQRClient()
url = client.scan_qr()
client.connect(url)
client.request_permission()
