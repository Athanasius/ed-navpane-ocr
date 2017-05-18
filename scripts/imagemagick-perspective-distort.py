#!/usr/bin/env python3

from wand.image import Image

with Image(filename="Screenshot_1032.bmp") as img:
  img.virtual_pixel = 'transparent'
  img.distort('perspective',
    (
      458,285   , 458,285,
      1344,272  , 1340,285,
      492,832   , 458,835,
      1358,744  , 1341,835
    )
  )

  img.save(filename="Screenshot_1032-py-squared.bmp")
