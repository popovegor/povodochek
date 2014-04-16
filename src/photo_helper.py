#!/usr/bin/python
# -*- coding: utf-8 -*-
from PIL import Image, ImageOps
import os
import sys
import StringIO
import db


thumbnail_size =  (300, 200) #width, height
thumbnail_quality = 60

def get_thumbnail_filename(filename):
    return "{0}_{1[0]}_{1[1]}_{2}_preview.jpg".\
    format(os.path.splitext(os.path.basename(filename))[0], \
    	thumbnail_size, thumbnail_quality)

def calc_image_size(img, height = None, width = None):
    if height:
        hpercent = (height / float(img.size[1]))
        wsize = int((float(img.size[0]) * float(hpercent)))
        return (wsize, height)
    elif width:
        wpercent = (width / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        return (width, hsize)


def resize_image(filename, height = None, width = None):
    print(filename)
    # out_filename = os.path.splitext(filename)[0] + ".jpeg"
    (infile, img) = (None, None)
    try:
        img = Image.open(filename)
        if img.mode != "RGB":
            img = img.convert("RGB")
        (w,h) = calc_image_size(img, height, width)
        img = img.resize((w, h), Image.ANTIALIAS)
        img.save(filename, "JPEG")
    except IOError as e:
        print("error: cannot resize image")

    del img
    
    return os.path.basename(filename)

def create_thumbnail(file, filename, photo_path):
    out_filename = get_thumbnail_filename(filename)
    print("================", out_filename, "================")
    im = None
    infile = None 
    try:
        im = StringIO.StringIO()
        im.write(file)
        im.seek(0)
        infile = Image.open(im)
        im = ImageOps.fit(infile, thumbnail_size, Image.ANTIALIAS)
        print(im.mode)
        if im.mode != "RGB":
            im = im.convert("RGB")
        im.save(os.path.join(photo_path, out_filename), "JPEG", quality=thumbnail_quality, optimize=True, progressive=True)
    except IOError as e:
        print(e)
        print("cannot create thumbnail for", filename)
    except:
        print("error")

    del im, infile

    print("outfile", out_filename)

    return os.path.basename(out_filename) if out_filename else None


def get_photo_size(filename, height = None, width = None):
    (buf, file, im) = None, None, None
    try:
        (name, file)  = db.get_photo(filename)
        buf = StringIO.StringIO()
        buf.write(file)
        buf.seek(0)
        im = Image.open(buf)
        (w,h) = calc_image_size(im, height, width)
        return {'w': w, 'h':h}
    except Exception, e:
        print(e)
        raise e
    finally:
        del im
        del file
        del buf