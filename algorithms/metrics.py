import cv2
import numpy as np


def calculate_mse(original, stego):
    """Calculate Mean Squared Error."""

    original = original.astype(np.float64)
    stego = stego.astype(np.float64)

    return np.mean((original - stego) ** 2)


def calculate_psnr(original, stego):
    """Calculate Peak Signal-to-Noise Ratio."""

    mse = calculate_mse(original, stego)

    if mse == 0:
        return float("inf")

    return 10 * np.log10((255.0 ** 2) / mse)


def evaluate_image(original_path, stego_path, grayscale=False):

    if grayscale:
        original = cv2.imread(
            original_path,
            cv2.IMREAD_GRAYSCALE
        )
        stego = cv2.imread(
            stego_path,
            cv2.IMREAD_GRAYSCALE
        )
    else:
        original = cv2.imread(original_path)
        stego = cv2.imread(stego_path)

    if original is None:
        raise ValueError(
            "Unable to read original image."
        )

    if stego is None:
        raise ValueError(
            f"Unable to read stego image: {stego_path}"
        )

    if original.shape != stego.shape:
        raise ValueError(
            f"Image dimensions do not match: "
            f"{original.shape} vs {stego.shape}"
        )

    mse = calculate_mse(original, stego)
    psnr = calculate_psnr(original, stego)

    return mse, psnr


if __name__ == "__main__":

    original_path = "images/cover/test.jpg"

    # Adaptive LSB - color image
    lsb_mse, lsb_psnr = evaluate_image(
        original_path,
        "images/stego_test.png"
    )

    # DCT - grayscale image
    dct_mse, dct_psnr = evaluate_image(
        original_path,
        "images/dct_stego_test.png",
        grayscale=True
    )

    # DWT - grayscale image
    dwt_mse, dwt_psnr = evaluate_image(
        original_path,
        "images/dwt_stego_test.png",
        grayscale=True
    )

    print("Image Quality Evaluation")
    print("-------------------------")

    print("\nAdaptive LSB:")
    print(f"MSE  : {lsb_mse:.6f}")
    print(f"PSNR : {lsb_psnr:.2f} dB")

    print("\nDCT:")
    print(f"MSE  : {dct_mse:.6f}")
    print(f"PSNR : {dct_psnr:.2f} dB")

    print("\nDWT:")
    print(f"MSE  : {dwt_mse:.6f}")
    print(f"PSNR : {dwt_psnr:.2f} dB")