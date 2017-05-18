#!/usr/bin/env python2

from wand.image import Image
from PIL import Image as PImage
import sys

import pyocr
import pyocr.builders

tools = pyocr.get_available_tools()
if len(tools) == 0:
    print("No OCR tool found")
    sys.exit(1)
# The tools are returned in the recommended order of usage
tool = tools[0]
print("Will use tool '%s'" % (tool.get_name()))
# Ex: Will use tool 'libtesseract'

langs = tool.get_available_languages()
print("Available languages: %s" % ", ".join(langs))
lang = langs[0]
print("Will use lang '%s'" % (lang))
# Ex: Will use lang 'fra'
# Note that languages are NOT sorted in any way. Please refer
# to the system locale settings for the default language
# to use.

res_multi = 1.0 # 1 is for 1920x1080
with Image(filename="Screenshot_1042.bmp") as img:
  # Get image size so as to set res_multi properly
  res_multi = img.width / 1920
  # XXX This will only handle 16:9 aspect ratio, need to treat height/width
  #     separately and see if there's a sane transform.

  img.virtual_pixel = 'transparent'
  img.distort('perspective',
    (
      300*res_multi,278*res_multi   , 300*res_multi,278*res_multi,
      1279*res_multi,264*res_multi  , 1279*res_multi,278*res_multi,
      346*res_multi,874*res_multi   , 300*res_multi,874*res_multi,
      1293*res_multi,771*res_multi  , 1279*res_multi,874*res_multi
    )
  )
  # Actual nav pane now: 457,281 891x550
  img.crop(int(300*res_multi), int(276*res_multi), int(300*res_multi + 986*res_multi), int(276*res_multi + 595*res_multi))
  img.save(filename="temp-ocr.png")
  img.crop(int(6*res_multi), int(95*res_multi), int(6*res_multi + 258*res_multi), int(95*res_multi + 58*res_multi))
  img.save(filename="system-name.png")

  # Location System name:  6,95 258x58
  ocrImage = PImage.open("temp-ocr.png")
  ocrSystemNameImage = ocrImage.crop(box=(6*res_multi, 95*res_multi, 6*res_multi + 258*res_multi, 95*res_multi + 58*res_multi))
  txt = tool.image_to_string(
    ocrSystemNameImage,
    lang="eng",
    builder=pyocr.builders.TextBuilder()
  )
  print("Text is '%s'\n" % txt)
