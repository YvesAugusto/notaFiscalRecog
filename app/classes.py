import pytesseract as pt

class Box:

    def __init__(self, x1, y1, x2, y2, tag, OPTIONS):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.tag = tag
        self.OPTIONS = OPTIONS

    @property
    def getTag(self):
        return self.tag

    def crop(self, image):
        cp = image.copy()
        x1, y1, x2, y2 = self.x1, self.y1, self.x2, self.y2
        if self.y1 > self.y2:
            y1 = self.y2
            y2 = self.y1
        if self.x1 > self.x2:
            x1 = self.x2
            x2 = self.x1
        return cp[
            y1: y2, x1: x2
        ]

class NotaFiscal:

    def __init__(self, campos):
        self.municipio = False
        self.campos = []
        self.errorMessage = {}
        for key, value in campos.items():
            coordinates = value['coordinates']
            OPTIONS = value['OPTIONS']
            box = Box(coordinates[0][0], coordinates[0][1],
                      coordinates[1][0], coordinates[1][1],
                      key, OPTIONS)
            self.campos.append(box)

    def recogOCR(self, image, extractor):
        json = {
            key: None for key in extractor.methods.keys()
        }
        erros = 0
        camposFailed = ''
        for idc, campo in enumerate(self.campos):
            crop = campo.crop(image)
            if crop.shape[0] == 0 or crop.shape[1] == 0:
                erros += 1
                camposFailed += f'{campo.getTag}, '
                continue
            df = pt.image_to_data(crop, output_type=pt.Output.DATAFRAME, config=campo.OPTIONS)
            flag, value = extractor.methods[campo.getTag](df)
            if not flag:
                erros += 1
                camposFailed += f'{campo.getTag}, '
            json[campo.getTag] = value
        return json, camposFailed[:-2]

def makeNote(key, noteDict):
    notaFiscal = NotaFiscal(
        noteDict
    )
    notaFiscal.municipio = key
    return notaFiscal