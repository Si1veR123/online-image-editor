from image_editor_app import image_edits
from . file_test_environment import TestFileEnvironment
from PIL import Image
import numpy as np
import os


class ImageEditFileTest(TestFileEnvironment):
    """Tests the file writing and moving when editing an image"""
    def test_update_current(self):
        # create the test file to be moved to undo
        with open(os.path.join(self.session_key_root, f"current{self.r.session['type']}"), "w") as f:
            f.write("test")

        # image to be saved as current
        array = np.array([[[0, 10, 0], [115, 100, 100], [255, 240, 225]]], dtype=np.uint16)
        im = Image.fromarray(array, mode="RGB")

        # update current
        image_edits.update_current(self.r, im)

        # check the test file has been moved to undo
        undo_dir_names = [int(file.split(".")[0]) for file in os.listdir(os.path.join(self.session_key_root, "undo"))]
        self.assertTrue(0 in undo_dir_names)

        # check new 'current' image has same shape as the image given to save
        current_im = Image.open(os.path.join(self.session_key_root, f"current{self.r.session['type']}"))
        self.assertTrue(np.array(current_im).shape == array.shape)

    def test_max_undo(self):
        """
        Tests that oldest undo is cleared if max (5) is reached
        """
        # write 6 test files
        for i in range(6):
            with open(os.path.join(self.session_key_root, "undo", f"{str(i)}{self.r.session['type']}"), "w") as f:
                f.write("test")

        # check limit
        image_edits.check_limit(self.r)

        # get filenames (list of numbers) and check 0 isn't there (should be removed)
        filenames = [int(file.split(".")[0]) for file in os.listdir(os.path.join(self.session_key_root, "undo"))]
        self.assertFalse(0 in filenames)

    def test_max_redo(self):
        """
        Tests that oldest redo is cleared if max (5) is reached
        """
        # write 6 test files
        for i in range(6):
            with open(os.path.join(self.session_key_root, "redo", f"{str(i)}{self.r.session['type']}"), "w") as f:
                f.write("test")

        # check limit
        image_edits.check_limit(self.r)

        # get filenames (list of numbers) and check 0 isn't there (should be removed)
        filenames = [int(file.split(".")[0]) for file in os.listdir(os.path.join(self.session_key_root, "redo"))]
        self.assertFalse(0 in filenames)

    def test_undo(self):
        """Test that undo works"""
        # pixel data for file to put in undo folder
        undo_file = np.array([[[200, 100, 255], [50, 60, 45], [10, 67, 89]]], dtype=np.uint16)
        # path to undo folder
        undo_file_path = os.path.join(self.session_key_root, "undo", "0" + self.r.session["type"])
        # get Image object from pixel values
        undo_im = Image.fromarray(undo_file, mode="RGB")
        # save Image to undo file path
        undo_im.save(undo_file_path)

        # pixel data for current file
        current_file = np.array([[[200, 100, 255], [50, 60, 45], [10, 67, 89], [70, 65, 128]]], dtype=np.uint16)
        # path to current file
        current_file_path = os.path.join(self.session_key_root, "current" + self.r.session["type"])
        # get Image object from pixel values
        current_im = Image.fromarray(current_file, mode="RGB")
        # save Image to current image path
        current_im.save(current_file_path)

        # run test function, undo image should now be current, and old current image should be in the redo folder
        image_edits.undo(self.r, None)

        # open new current image and new redo image as Image objects
        new_current_im = Image.open(os.path.join(self.session_key_root, "current" + self.r.session["type"]))
        new_redo_im = Image.open(os.path.join(self.session_key_root, "redo", "0" + self.r.session["type"]))

        # comparing shape is enough as the image that started in current has different shape to image that started in undo
        # compare image that started in undo folder and current image (compares shape)
        self.assertTrue(np.array(new_current_im).shape == undo_file.shape)
        # compare image that started as current and ended in redo folder (compares shape)
        self.assertTrue(np.array(new_redo_im).shape == current_file.shape)

    def test_redo(self):
        """Test that redo works"""
        # pixel data for file to put in redo folder
        redo_file = np.array([[[200, 100, 255], [50, 60, 45], [10, 67, 89]]], dtype=np.uint16)
        # path to redo folder
        redo_file_path = os.path.join(self.session_key_root, "redo", "0" + self.r.session["type"])
        # get Image object from pixel values
        redo_im = Image.fromarray(redo_file, mode="RGB")
        # save Image to redo file path
        redo_im.save(redo_file_path)

        # pixel data for current file
        current_file = np.array([[[200, 100, 255], [50, 60, 45], [10, 67, 89], [70, 65, 128]]], dtype=np.uint16)
        # path to current file
        current_file_path = os.path.join(self.session_key_root, "current" + self.r.session["type"])
        # get Image object from pixel values
        current_im = Image.fromarray(current_file, mode="RGB")
        # save Image to current image path
        current_im.save(current_file_path)

        # run test function, redo image should now be current, and old current image should be in the undo folder
        image_edits.redo(self.r, None)

        # open new current image and new undo image as Image objects
        new_current_im = Image.open(os.path.join(self.session_key_root, "current" + self.r.session["type"]))
        new_undo_im = Image.open(os.path.join(self.session_key_root, "undo", "0" + self.r.session["type"]))

        # comparing shape is enough as the image that started in current has different shape to image that started in redo
        # compare image that started in redo folder and current image (compares shape)
        self.assertTrue(np.array(new_current_im).shape == redo_file.shape)
        # compare image that started as current and ended in redo folder (compares shape)
        self.assertTrue(np.array(new_undo_im).shape == current_file.shape)
