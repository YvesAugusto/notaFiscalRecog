import time
from classes import *
from config import *
import numpy as np
from pdf2image import convert_from_path
from extractors import DefaultExtractorNF



pdf = 'notafiscal-16765-000066661.pdf'

print(image.shape)
start = time.time()
notas['Fortaleza'].recogOCR(image, extractor)
print("Time elapsed: {}".format(time.time() - start))