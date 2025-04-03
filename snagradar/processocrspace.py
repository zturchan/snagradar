# Use ocr.space to process images
import ocrspace
import sys 
from constants import OCRSPACE_API_KEY

def run_ocr(filename):
  print('run ocr')
  # Need to use OCR2, version 1 won't work well enough for our purposes
  api = ocrspace.API(api_key=OCRSPACE_API_KEY, OCREngine=2)
  result = api.ocr_file(filename)
  print('result is ' + str(result))
  return result

def run_ocr_stream(stream):
  print('run ocr stream')
  # Need to use OCR2, version 1 won't work well enough for our purposes
  api = ocrspace.API(api_key=OCRSPACE_API_KEY, OCREngine=2)
  result = api.ocr_file(open(stream, 'rb'))
  print('result is ' + str(result))
  return result