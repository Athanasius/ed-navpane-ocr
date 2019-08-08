#!/usr/bin/env python2

import os
from wand.image import Image
from PIL import Image as PImage
from PIL import ImageFilter
import sys

import pyocr
import pyocr.builders

if len(sys.argv) != 2:
  print("Must supply an input file name");
  sys.exit(-1)

navpane_boxes = [322, 100, 531, 35]

tools = pyocr.get_available_tools()
if len(tools) == 0:
    print("No OCR tool found")
    sys.exit(1)
# The tools are returned in the recommended order of usage
tool = tools[0]
print("Will use tool '%s'" % (tool.get_name()))
# Ex: Will use tool 'libtesseract'
#os.environ['TESSDATA_PREFIX'] = '/home/users/athan/games/elite-dangerous/tools/ed-navpane-ocr/tessdata'
os.environ['TESSDATA_PREFIX'] = '/home/users/athan/games/elite-dangerous/tools/ed-navpane-ocr/docs/dubliner-0.0.4-training/training/numbers_eurocaps/tessdata'

langs = tool.get_available_languages()
print("Available languages: %s" % ", ".join(langs))
lang = langs[0]
print("Will use lang '%s'" % (lang))
# Ex: Will use lang 'fra'
# Note that languages are NOT sorted in any way. Please refer
# to the system locale settings for the default language
# to use.
#ocrLang = 'elitedangerous-systemname'
ocrLang = 'eng1'

def selectEDOrange(p):
  #print p
  #print type(p)
  if p > 0xf0:
    return p
  return (0,0,0,0)

res_multi = 1.0 # 1 is for 1920x1080
with Image(filename=sys.argv[1]) as img:
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
  img.save(filename="navpane-normalised.png")
  img.crop(int(6*res_multi), int(95*res_multi), int(6*res_multi + 258*res_multi), int(95*res_multi + 58*res_multi))
  img.save(filename="system-name.png")

  # Location System name:  6,95 258x58
  ocrImage = PImage.open("navpane-normalised.png")

  # Try to filter down to just the ED orange pixels
  # 0xfa621c
  pixels = ocrImage.load()
  width, height = ocrImage.size
  for x in range(width):
    for y in range(height):
      p = pixels[x,y]
      r = p[0]
      g = p[1]
      b = p[2]
      if r > 150 and r <= 255 and g > 40 and g < 150 and b >= 0 and b < 45:
        pixels[x,y] = (255,255,255,255)
      else:
        pixels[x,y] = (0,0,0,255)

  ocrImage.save("navpane-normalised-monochrome.png", "PNG")
  #sys.exit(0)

  # Grab the system name from the top-left 'location' area.
  ocrSystemNameImage = ocrImage.crop(box=(6*res_multi, 95*res_multi, 6*res_multi + 258*res_multi, 95*res_multi + 58*res_multi))
  txt = tool.image_to_string(
    ocrSystemNameImage,
    lang=ocrLang,
    builder=pyocr.builders.TextBuilder()
  )
  print("Location is: %s" % txt)

  # Step through the rows in the navpane listing of local stars/planets/etc
  # The co-ordinate, plus width and height in navpane_boxes[] is the origin
  # for this.  We then add 41 to the y co-ordinate for each row.
  # The name boxes have width as per the array.
  # The distance boxes are an additional 480 pixels to the right.
  # The distance boxes have width 165.
  for b in range(0, 12):
    # Grab just the name
    ocrBox = ocrImage.crop(box=(navpane_boxes[0]*res_multi, (navpane_boxes[1] + 41 * b)*res_multi, navpane_boxes[0]*res_multi + navpane_boxes[2]*res_multi, (navpane_boxes[1] + 41 * b)*res_multi + navpane_boxes[3]*res_multi))
    ocrBox.save("navpane-normalised-box-" + str(b) + "-name.png", "PNG")
    txt = tool.image_to_string(
      ocrBox,
      lang=ocrLang,
      builder=pyocr.builders.TextBuilder()
    )
    print("Nav system name[" + str(b) + "]: %s" % txt)

    continue
    # Now the distance text
    ocrBox = ocrImage.crop(box=((navpane_boxes[0] + 480)*res_multi, (navpane_boxes[1] + 41 * b)*res_multi, (navpane_boxes[0] + 480)*res_multi + 165*res_multi, (navpane_boxes[1] + 41 * b)*res_multi + navpane_boxes[3]*res_multi))
    ocrBox.save("navpane-normalised-box-" + str(b) + "-distance.png", "PNG")
    txt = tool.image_to_string(
      ocrBox,
      lang=ocrLang,
      builder=pyocr.builders.TextBuilder()
    )
    print("       distance[" + str(b) + "]: %s" % txt)
