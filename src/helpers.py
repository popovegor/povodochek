#!/usr/bin/python
# -*- coding: utf-8 -*-

from PIL import Image, ImageOps
import os
from pymongo import MongoClient
import gridfs
import sys
import StringIO


def num(value, default = None):
    if (isinstance(value, str) or  isinstance(value, unicode)) and value.isdigit():
        return int(value)
    elif isinstance(value, int):
        return value
    elif isinstance(value, float):
        return int(value)
    return default

def get_thumbnail_filename(filename):
    return os.path.basename(os.path.splitext(filename)[0] + "_preview.png")

def resize_image(filename):
    size =  (600, 400) #width, height
    baseheight = 400
    print(filename)
    # out_filename = os.path.splitext(filename)[0] + ".jpeg"
    (infile, img) = (None, None)
    try:
        img = Image.open(filename)
        hpercent = (baseheight / float(img.size[1]))
        wsize = int((float(img.size[0]) * float(hpercent)))
        img = img.resize((wsize, baseheight), Image.ANTIALIAS)
        # img.thumbnail(size, Image.ANTIALIAS)
        img.save(filename, "JPEG")
    except IOError as e:
        print("error: cannot resize image")

    del img
    

    return os.path.basename(filename)

def create_thumbnail(file, filename):
    size =  (150, 100) #width, height
    out_filename = os.path.splitext(filename)[0] + "_preview.png"
    im = None
    infile = None 
    try:
        im = StringIO.StringIO()
        im.write(file)
        im.seek(0)
        infile = Image.open(im)
        im = ImageOps.fit(infile, size, Image.ANTIALIAS)
        im.save(out_filename, "PNG")
    except IOError as e:
        print(e)
        print("cannot create thumbnail for", filename)
    except:
        print("error")

    del im, infile

    print("outfile", out_filename)

    return os.path.basename(out_filename) if out_filename else None


def gridfs_photos(mongo):
    return gridfs.GridFS(mongo, 'photos')

def save_photo(mongo, file):
    """
    return _id of gridfs file
    """
    try:
        fs = gridfs_photos(mongo)
        print("filename", file.name)
        return fs.put(file.read(), filename = os.path.basename(file.name))
    except e:
        print(e)
    


def get_photo(mongo, filename):
    """
    return file
    """
    try:
        filename = filename.lower()
        fs = gridfs_photos(mongo)
        name = os.path.basename(filename)
        print("get_photo", name)
        photo = mongo.photos.files.find_one({"filename" : filename}, fields= ['_id'])
        print(photo)
        with fs.get(photo.get('_id')) as gridfs_file:
            return (gridfs_file.name, gridfs_file.read()) 
    except:
        print(sys.exc_info())
    
    return (None, None)

if __name__ == "__main__":
    import glob
    for infile in glob.glob("/tmp/*.*"):
        create_thumbnail(infile)