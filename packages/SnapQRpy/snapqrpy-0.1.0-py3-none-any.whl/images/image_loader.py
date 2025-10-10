from PIL import Image

class ImageLoader:
    def load(self, path):
        return Image.open(path)
