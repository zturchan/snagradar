# Use ocr.space to process images
import ocrspace
import os
import math
from constants import OCRSPACE_API_KEY
from PIL import Image

OCRSPACE_FILESIZE_LIMIT_KB = 1024

def compress_image_for_ocr(filename, factor_bigger):
  img = Image.open(filename)

  # Source for resizing algorithm: http://math.stackexchange.com/questions/3983228/how-to-resize-a-rectangle-to-a-specific-area-while-maintaining-the-aspect-ratio
  width, height = img.size
  original_area = width * height
  new_area = round(original_area / factor_bigger)
  new_height = int(math.sqrt(new_area * height / width))
  new_width = int(math.sqrt(new_area * width / height))
  resized = img.resize((new_width, new_height))
  resized_filename = os.path.join(os.path.dirname(filename), os.path.splitext(os.path.basename(filename))[0] + '-resized.jpg')
  resized.save(resized_filename)
  return resized_filename

def run_ocr(filename):
  print('Running OCR')
  # Need to use OCR2, version 1 won't work well enough for our purposes
  api = ocrspace.API(api_key=OCRSPACE_API_KEY, OCREngine=2)

  filesize_in_bytes = os.path.getsize(filename)
  filesize_in_kb = filesize_in_bytes / 1000

  if (filesize_in_kb > OCRSPACE_FILESIZE_LIMIT_KB):
    # Downscale the image to fit the size requirements. 
    factor_bigger = filesize_in_kb / OCRSPACE_FILESIZE_LIMIT_KB 
    print("Image uploaded was " + str(filesize_in_kb) + "KB, resizing.")
    filename = compress_image_for_ocr(filename, factor_bigger)
    print("Resized File at " + str(filename))
    result = api.ocr_file(filename)
    print('OCR result is ' + str(result))
    return result