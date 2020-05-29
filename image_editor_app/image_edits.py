import shutil
import os
import numpy as np
from django.conf import settings
from PIL import Image


def check_limit(r):
    """checks if undo/redo limit is reached, and if so, removes oldest"""
    # get all from undo directory
    undo_dir = os.listdir(os.path.join(settings.UPLOADED_IMAGES_ROOT, r.session.session_key, "undo"))
    # if limit (5) reached
    if len(undo_dir) > 5:
        # get lowest number (oldest)
        lowest = min([int(file.split(".")[0]) for file in undo_dir])
        # remove it
        os.remove(os.path.join(settings.UPLOADED_IMAGES_ROOT, r.session.session_key, "undo", str(lowest) + r.session["type"]))

    # get all from redo directory
    redo_dir = os.listdir(os.path.join(settings.UPLOADED_IMAGES_ROOT, r.session.session_key, "redo"))
    # if limit (5) reached
    if len(redo_dir) > 5:
        # get lowest number (oldest)
        lowest = min([int(file.split(".")[0]) for file in redo_dir])
        # remove it
        os.remove(os.path.join(settings.UPLOADED_IMAGES_ROOT, r.session.session_key, "redo", str(lowest) + r.session["type"]))


def update_current(r, im: Image.Image):
    """Moves current image to the undo folder and saves the PIL.Image to current"""
    # get all files in undo folder of session id folder
    dirs = os.listdir(os.path.join(settings.UPLOADED_IMAGES_ROOT, r.session.session_key, "undo"))
    # split to file name and extension
    dirs = [file.split(".") for file in dirs]

    try:
        # new name = largest of previous numbers + 1 + extension
        new_name = str(max([int(file[0]) for file in dirs]) + 1) + r.session["type"]
    except ValueError:
        # if empty, new name is 0
        new_name = "0" + r.session["type"]

    # session id folder path
    path = os.path.join(settings.UPLOADED_IMAGES_ROOT, r.session.session_key)

    # rename current image to new_name and move to undo folder
    os.rename(os.path.join(path, "current" + r.session["type"]), os.path.join(path, new_name))
    shutil.move(os.path.join(path, new_name), os.path.join(path, "undo"))

    # save image as new current
    im.save(os.path.join(settings.UPLOADED_IMAGES_ROOT, r.session.session_key, "current" + r.session["type"]))

    check_limit(r)


def undo(r, _):
    """Gets most recent image from undo folder replaces with current, and moves old current to redo"""
    # get all from undo directory
    undo_dirs = os.listdir(os.path.join(settings.UPLOADED_IMAGES_ROOT, r.session.session_key, "undo"))
    # get integer filenames from undo_dirs
    undo_dirs = [int(file.split(".")[0]) for file in undo_dirs]

    # if there are no undos, return
    if len(undo_dirs) == 0:
        return

    # get new name for undo file, later renamed to current
    try:
        new_undo_name = str(max(undo_dirs)) + r.session["type"]
    except ValueError:
        new_undo_name = "0" + r.session["type"]

    # get redo files and get integer names
    redo_dirs = os.listdir(os.path.join(settings.UPLOADED_IMAGES_ROOT, r.session.session_key, "redo"))
    redo_dirs = [int(file.split(".")[0]) for file in redo_dirs]

    # get new redo name (max of prev + 1)
    try:
        new_redo_name = str(max(redo_dirs) + 1) + r.session["type"]
    except ValueError:
        new_redo_name = "0" + r.session["type"]

    # path of sessionid folder
    path = os.path.join(settings.UPLOADED_IMAGES_ROOT, r.session.session_key)
    # rename old current to new_redo_n ame
    os.rename(os.path.join(path, "current" + r.session["type"]), os.path.join(path, new_redo_name))
    # move old current to redo folder
    shutil.move(os.path.join(path, new_redo_name), os.path.join(path, "redo"))

    # rename new_undo_name to current
    os.rename(os.path.join(path, "undo", new_undo_name), os.path.join(path, "current" + r.session["type"]))


def redo(r, _):
    # get all from redo directory
    redo_dirs = os.listdir(os.path.join(settings.UPLOADED_IMAGES_ROOT, r.session.session_key, "redo"))
    redo_dirs = [int(file.split(".")[0]) for file in redo_dirs]

    # if there are no redos, return
    if len(redo_dirs) == 0:
        return

    # get new_redo_name
    try:
        new_redo_name = str(max(redo_dirs)) + r.session["type"]
    except ValueError:
        new_redo_name = "0" + r.session["type"]

    # get all from undo_dirs
    undo_dirs = os.listdir(os.path.join(settings.UPLOADED_IMAGES_ROOT, r.session.session_key, "undo"))
    undo_dirs = [int(file.split(".")[0]) for file in undo_dirs]

    # get new_undo_name
    try:
        new_undo_name = str(max(undo_dirs) + 1) + r.session["type"]
    except ValueError:
        new_undo_name = "0" + r.session["type"]

    # get sessionid folder path
    path = os.path.join(settings.UPLOADED_IMAGES_ROOT, r.session.session_key)
    # rename old current to new_undo_name
    os.rename(os.path.join(path, "current" + r.session["type"]), os.path.join(path, new_undo_name))
    # move old current to undo folder
    shutil.move(os.path.join(path, new_undo_name), os.path.join(path, "undo"))

    # rename new_redo_name to current
    os.rename(os.path.join(path, "redo", new_redo_name), os.path.join(path, "current" + r.session["type"]))


def crop(r, data):
    # use PIL to crop image from given data

    # get crop data
    crop_data = data["data"]
    im = Image.open(os.path.join(settings.UPLOADED_IMAGES_ROOT, r.session.session_key, "current" + r.session["type"]))

    # perform crop (right, top, right + width, top + height)
    im = im.crop((crop_data[0], crop_data[1], crop_data[0] + crop_data[2], crop_data[1] + crop_data[3]))

    update_current(r, im)


def rotate(r, data):
    # use PIL to rotate
    im = Image.open(os.path.join(settings.UPLOADED_IMAGES_ROOT, r.session.session_key, "current" + r.session["type"]))

    if data["data"] == "1":
        # rotate anti clockwise
        im = im.rotate(-90, expand=True, resample=Image.BILINEAR)
    else:
        # rotate clockwise
        im = im.rotate(90, expand=True, resample=Image.BILINEAR)
    update_current(r, im)


# highest HSL value
MAX_VAL = 255


def make_edit(pixels, hue, sat, lum):
    # new image array
    new = np.zeros(pixels.shape)

    # add hue to first val in each pixel
    new[:, :, 0] = pixels[:, :, 0] + hue
    # any pixels with negative hues, add MAX_VAL to loop round (hue is circular)
    new[:, :, 0][new[:, :, 0] < 0] += MAX_VAL
    # loop round the other way (-MAX_VAL)
    new[:, :, 0][new[:, :, 0] > MAX_VAL] -= MAX_VAL

    # add sat to second val in each pixel
    new[:, :, 1] = pixels[:, :, 1] + sat

    # add lum to third val in each pixel
    new[:, :, 2] = pixels[:, :, 2] + lum

    return np.clip(new, 0, 255).astype(np.uint8)


def adjust(r, data):
    # get HSL values and scale e.g. data is between -50 and 50, scale to -MAX_VAL and MAX_VAL
    h_amount = data["data"]["h"] * MAX_VAL / 100
    s_amount = data["data"]["s"] * MAX_VAL / 100
    l_amount = data["data"]["l"] * MAX_VAL / 100

    # open image
    im = Image.open(os.path.join(settings.UPLOADED_IMAGES_ROOT, r.session.session_key, "current" + r.session["type"]))

    # convert to HSV/HSL
    im = im.convert("HSV")
    # get numpy array of pixels for processing
    pixels = np.asarray(im).astype(np.uint16)
    # process and change HSL vals
    pixels = make_edit(pixels, h_amount, s_amount, l_amount)

    # create image from new numpy array, with mode=HSV
    im = Image.fromarray(pixels, mode="HSV")

    im = im.convert("RGB")

    update_current(r, im)
