import cv2
import numpy as np
import matplotlib.pyplot as plt


def apply_sobel(image_path):
    # Read the image in grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if image is None:
        raise ValueError("Unable to read the image.")

    # Apply Sobel operator in X direction
    sobel_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)

    # Apply Sobel operator in Y direction
    sobel_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)

    # Calculate edge strength
    edge_strength = np.sqrt(sobel_x ** 2 + sobel_y ** 2)

    # Normalize edge strength to 0-255
    edge_image = cv2.normalize(
        edge_strength,
        None,
        0,
        255,
        cv2.NORM_MINMAX
    ).astype(np.uint8)

    # Create texture classification map
    texture_map = classify_texture(edge_image)

    return image, edge_image, texture_map


def classify_texture(edge_image):
    """
    Classify image regions into:
    0 = Smooth
    1 = Moderate
    2 = Strong Edge
    """

    texture_map = np.zeros_like(edge_image, dtype=np.uint8)

    # Thresholds for classification
    smooth_threshold = 50
    strong_threshold = 150

    # Moderate regions
    texture_map[
        (edge_image >= smooth_threshold) &
        (edge_image < strong_threshold)
    ] = 1

    # Strong-edge regions
    texture_map[edge_image >= strong_threshold] = 2

    return texture_map


def display_sobel(image, edge_image, texture_map):

    plt.figure(figsize=(12, 4))

    # Original image
    plt.subplot(1, 3, 1)
    plt.imshow(image, cmap="gray")
    plt.title("Original Image")
    plt.axis("off")

    # Sobel edge image
    plt.subplot(1, 3, 2)
    plt.imshow(edge_image, cmap="gray")
    plt.title("Sobel Edge Map")
    plt.axis("off")

    # Texture classification
    plt.subplot(1, 3, 3)
    plt.imshow(texture_map, cmap="gray")
    plt.title("Texture Map")
    plt.axis("off")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":

    image_path = "images/cover/test.jpg"

    image, edge_image, texture_map = apply_sobel(image_path)

    print("Sobel edge detection completed successfully!")

    print("Image shape:", image.shape)
    print("Edge map shape:", edge_image.shape)
    print("Texture map shape:", texture_map.shape)

    print("\nTexture classification:")
    print("0 = Smooth")
    print("1 = Moderate")
    print("2 = Strong Edge")

    print("\nNumber of pixels:")
    print("Smooth:",
          np.sum(texture_map == 0))

    print("Moderate:",
          np.sum(texture_map == 1))

    print("Strong Edge:",
          np.sum(texture_map == 2))

    display_sobel(image, edge_image, texture_map)