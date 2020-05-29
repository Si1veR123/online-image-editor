from django.test import TestCase
from image_editor_app import image_edits
from . file_test_environment import TestFileEnvironment
from PIL import Image
import numpy as np
import os


class ImageEditHSLTest(TestCase):
    """Checks the make_edit function that should alter hue, sat or lum by the given amount. Hue wraps around to 0 at 255."""
    def setUp(self):
        """Array of pixels to apply edits to"""
        self.colours = np.array([[[0, 10, 0], [115, 100, 100], [255, 240, 225]]], dtype=np.uint16)

    def test_hue(self):
        new = image_edits.make_edit(self.colours, 100, 0, 0)
        self.assertTrue((new == np.array([[[100, 10, 0], [215, 100, 100], [100, 240, 225]]], dtype=np.uint16)).all())

    def test_negative_hue(self):
        new = image_edits.make_edit(self.colours, -100, 0, 0)
        self.assertTrue((new == np.array([[[155, 10, 0], [15, 100, 100], [155, 240, 225]]], dtype=np.uint16)).all())

    def test_sat(self):
        new = image_edits.make_edit(self.colours, 0, 100, 0)
        self.assertTrue((new == np.array([[[0, 110, 0], [115, 200, 100], [255, 255, 225]]], dtype=np.uint16)).all())

    def test_negative_sat(self):
        new = image_edits.make_edit(self.colours, 0, -100, 0)
        self.assertTrue((new == np.array([[[0, 0, 0], [115, 0, 100], [255, 140, 225]]], dtype=np.uint16)).all())

    def test_lum(self):
        new = image_edits.make_edit(self.colours, 0, 0, 100)
        self.assertTrue((new == np.array([[[0, 10, 100], [115, 100, 200], [255, 240, 255]]], dtype=np.uint16)).all())

    def test_negative_lum(self):
        new = image_edits.make_edit(self.colours, 0, 0, -100)
        self.assertTrue((new == list(np.array([[[0, 10, 0], [115, 100, 0], [255, 240, 125]]], dtype=np.uint16))).all())

    def test_hsl(self):
        new = image_edits.make_edit(self.colours, 50, 250, -100)
        self.assertTrue((new == np.array([[[50, 255, 0], [165, 255, 0], [50, 255, 125]]], dtype=np.uint16)).all())


class ImageEditTransformTest(TestFileEnvironment):
    def setUp(self):
        # starting image
        self.colours = np.array([
            [[255, 255, 255], [0, 0, 0], [127, 127, 127]],
            [[10, 10, 10], [20, 20, 20], [30, 30, 30]],
        ], dtype=np.uint16)
        super().setUp()

    def test_rotate(self):
        # create Image object
        im = Image.fromarray(self.colours, mode="RGB")
        # save to current image
        im.save(os.path.join(self.session_key_root, "current" + self.r.session["type"]))

        # rotate image
        rotate_data = {"data": "1"}
        image_edits.rotate(self.r, rotate_data)

        # check image is rotated
        rotated = Image.open(os.path.join(self.session_key_root, "current" + self.r.session["type"]))
        self.assertTrue(np.array(rotated).shape == (3, 2, 3))

    def test_rotate_anti(self):
        # create Image object
        im = Image.fromarray(self.colours, mode="RGB")
        im.save(os.path.join(self.session_key_root, "current" + self.r.session["type"]))

        # rotate image
        rotate_data = {"data": "0"}
        image_edits.rotate(self.r, rotate_data)

        # check image is rotated
        rotated = Image.open(os.path.join(self.session_key_root, "current" + self.r.session["type"]))
        self.assertTrue(np.array(rotated).shape == (3, 2, 3))

    def test_crop(self):
        # create Image object
        im = Image.fromarray(self.colours, mode="RGB")
        im.save(os.path.join(self.session_key_root, "current" + self.r.session["type"]))

        # crop image
        crop_data = {"data": [1, 0, 2, 2]}
        image_edits.crop(self.r, crop_data)

        # check image is cropped
        cropped = Image.open(os.path.join(self.session_key_root, "current" + self.r.session["type"]))
        self.assertTrue(np.array(cropped).shape == (2, 2, 3))
