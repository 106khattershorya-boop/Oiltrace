import cv2
import numpy as np


def load_image(image_path):
    """
    Load an image from the given path.
    """

    image = cv2.imread(image_path)

    if image is None:
        raise FileNotFoundError(
            f"Could not load image: {image_path}"
        )

    return image


def resize_image(image, width=512, height=512):
    """
    Resize image to a fixed size.
    """

    return cv2.resize(
        image,
        (width, height)
    )


def convert_to_grayscale(image):
    """
    Convert BGR image to grayscale.
    """

    return cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )


def remove_noise(image):
    """
    Reduce image noise using Gaussian blur.
    """

    return cv2.GaussianBlur(
        image,
        (5, 5),
        0
    )


def normalize_image(image):
    """
    Normalize pixel values to 0-255.
    """

    return cv2.normalize(
        image,
        None,
        0,
        255,
        cv2.NORM_MINMAX
    )


def preprocess(image_path):

    image = load_image(image_path)

    image = resize_image(image)

    gray = convert_to_grayscale(image)

    gray = remove_noise(gray)

    gray = normalize_image(gray)

    return image, gray