from snapqrpy.core.client import SnapQRClient

def run_client():
    client = SnapQRClient()
    url = client.scan_qr()
    client.connect(url)
    client.request_permission()

if __name__ == '__main__':
    run_client()
