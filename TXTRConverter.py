import mmap

from PIL import Image

class TXTRConverter():

    @staticmethod
    def I4_bytes_to_RGBA(bytes):
        bits = "{0:08b}".format(int.from_bytes(bytes, byteorder='big'))
        first = int(bits[:4], 2)
        second = int(bits[4:], 2)
        return [
            tuple([first*17] * 3 + [255 if first != 0 else 0]), 
            tuple([second*17] * 3 + [255 if second != 0 else 0])
        ]

    def __init__(self, filename):

        self.filename = filename
        with open(filename, 'r+b') as fil:
            self.file = mmap.mmap(fil.fileno(), 0)

        self.header = {
            'id': int.from_bytes(self.file.read(4), byteorder='big'),
            'width': int.from_bytes(self.file.read(2), byteorder='big'),
            'height': int.from_bytes(self.file.read(2), byteorder='big'),
            'mipmap': int.from_bytes(self.file.read(4), byteorder='big')
        }

        self.img = Image.new('RGBA', (self.header['width'], self.header['height']), (0,0,0,0))

        file_types = {
            0: {'bits': 4, 'bytes': 1, 'width': 8, 'height': 8, 'converter': self.I4_bytes_to_RGBA},
            1: {'bits': 8, 'bytes': 1, 'width': 8, 'height': 4, 'converter': self.I4_bytes_to_RGBA},
            2: {'bits': 8, 'bytes': 1, 'width': 8, 'height': 4, 'converter': self.I4_bytes_to_RGBA},
            3: {'bits': 16, 'bytes': 2, 'width': 4, 'height': 4, 'converter': self.I4_bytes_to_RGBA},
            4: {'bits': 4, 'bytes': 1, 'width': 8, 'height': 8, 'converter': self.I4_bytes_to_RGBA},
            5: {'bits': 8, 'bytes': 1, 'width': 8, 'height': 4, 'converter': self.I4_bytes_to_RGBA},
            6: {'bits': 16, 'bytes': 2, 'width': 4, 'height': 4, 'converter': self.I4_bytes_to_RGBA},
            7: {'bits': 16, 'bytes': 2, 'width': 4, 'height': 4, 'converter': self.I4_bytes_to_RGBA},
            8: {'bits': 16, 'bytes': 2, 'width': 4, 'height': 4, 'converter': self.I4_bytes_to_RGBA},
            9: {'bits': 32, 'bytes': 4, 'width': 4, 'height': 4, 'converter': self.I4_bytes_to_RGBA},
            10: {'bits': 4, 'bytes': 1, 'width': 8, 'height': 8, 'converter': self.I4_bytes_to_RGBA},
        }

        self.file_type = file_types.get(self.header['id'])

        if self.header['id'] in [4, 5]:
            self.palette_data = {
                'format': int.from_bytes(self.file.read(4), byteorder='big'),
                'width': int.from_bytes(self.file.read(2), byteorder='big'),
                'height': int.from_bytes(self.file.read(2), byteorder='big'),
            }

            if self.header['id'] == 4:
                self.palette_data.update({
                    'colors': [self.file.read(2) for i in range(16)]
                })
            elif self.header['id'] == 5:
                self.palette_data.update({
                    'colors': [self.file.read(2) for i in range(256)]
                })

        self.data_start = self.file.tell()

    def generate_pixels(self):
        self.pixels = list()
        self.file.seek(self.data_start)
        while True:
            buff = self.file.read(self.file_type['bytes'])
            if not buff:
                break
            self.pixels += self.file_type['converter'](buff)
    
            
    def save_as_png(self):
        self.generate_pixels()
        pos = 0

        for y in range(0, self.header['height'], self.file_type['height']):
            for x in range(0, self.header['width'], self.file_type['width']):
                for h in range(self.file_type['height']):
                    for w in range(self.file_type['width']):
                        self.img.putpixel((w+x, h+y), self.pixels[pos])
                        pos += 1

        self.img.save(self.filename.split('.')[0] + '.png')