import cv2
import pywt
import numpy as np
import matplotlib.pyplot as plt


# ---------------------------------------------------------
# DWT Decomposition
# ---------------------------------------------------------

def apply_dwt(image_path):
    """Read image and perform one-level Haar DWT."""

    image = cv2.imread(
        image_path,
        cv2.IMREAD_GRAYSCALE
    )

    if image is None:
        raise ValueError(
            "Unable to read the image."
        )

    LL, (LH, HL, HH) = pywt.dwt2(
        image,
        "haar"
    )

    return image, LL, LH, HL, HH


# ---------------------------------------------------------
# Convert data to binary
# ---------------------------------------------------------

def bytes_to_binary(data):
    """Convert bytes into binary string."""

    return ''.join(
        format(byte, '08b')
        for byte in data
    )


def binary_to_bytes(binary):
    """Convert binary string into bytes."""

    return bytes(
        int(binary[i:i + 8], 2)
        for i in range(0, len(binary), 8)
    )


# ---------------------------------------------------------
# DWT Embedding
# ---------------------------------------------------------

def embed_dwt(image, data):
    """
    Embed secret data using Haar DWT.

    The HH sub-band is used for embedding.
    """

    image = np.float32(image)

    # Perform DWT
    LL, (LH, HL, HH) = pywt.dwt2(
        image,
        "haar"
    )

    # Convert message to binary
    binary_message = bytes_to_binary(data)

    # Add 32-bit message length
    length_header = format(
        len(data),
        '032b'
    )

    binary_message = (
        length_header +
        binary_message
    )

    message_index = 0

    # Embedding strength
    alpha = 5.0

    # Embed into HH coefficients
    for row in range(HH.shape[0]):

        for col in range(HH.shape[1]):

            if message_index >= len(
                binary_message
            ):
                break

            bit = binary_message[
                message_index
            ]

            coefficient = HH[row, col]

            # Encode bit using coefficient sign
            if bit == '1':

                if coefficient < alpha:
                    HH[row, col] = alpha

            else:

                if coefficient >= 0:
                    HH[row, col] = -alpha
                else:
                    HH[row, col] = -abs(coefficient)

            message_index += 1

        if message_index >= len(
            binary_message
        ):
            break

    # Check capacity
    if message_index < len(
        binary_message
    ):
        raise ValueError(
            "Message is too large for this image."
        )

    # Reconstruct image using inverse DWT
    stego_image = pywt.idwt2(
        (LL, (LH, HL, HH)),
        "haar"
    )

    return np.clip(
        stego_image,
        0,
        255
    ).astype(np.uint8)


# ---------------------------------------------------------
# DWT Extraction
# ---------------------------------------------------------

def extract_dwt(stego_image):
    """
    Extract secret data from DWT stego image.
    """

    stego_image = np.float32(
        stego_image
    )

    # Perform DWT
    LL, (LH, HL, HH) = pywt.dwt2(
        stego_image,
        "haar"
    )

    binary_data = ""

    # First extract 32-bit message length
    for row in range(HH.shape[0]):

        for col in range(HH.shape[1]):

            coefficient = HH[row, col]

            if coefficient >= 0:
                bit = '1'
            else:
                bit = '0'

            binary_data += bit

            if len(binary_data) == 32:
                break

        if len(binary_data) == 32:
            break

    if len(binary_data) < 32:
        raise ValueError(
            "Unable to read message length."
        )

    # Get message length
    message_length = int(
        binary_data[:32],
        2
    )

    required_bits = (
        32 +
        message_length * 8
    )

    # Extract complete message
    binary_data = ""

    for row in range(HH.shape[0]):

        for col in range(HH.shape[1]):

            coefficient = HH[row, col]

            if coefficient >= 0:
                bit = '1'
            else:
                bit = '0'

            binary_data += bit

            if len(binary_data) >= required_bits:

                message_binary = binary_data[
                    32:required_bits
                ]

                return binary_to_bytes(
                    message_binary
                )

    raise ValueError(
        "Unable to extract the complete message."
    )


# ---------------------------------------------------------
# Display DWT
# ---------------------------------------------------------

def display_dwt(
    image,
    LL,
    LH,
    HL,
    HH
):
    """Display original image and DWT sub-bands."""

    plt.figure(figsize=(10, 8))

    plt.subplot(2, 3, 1)
    plt.imshow(
        image,
        cmap="gray"
    )
    plt.title("Original Image")
    plt.axis("off")

    plt.subplot(2, 3, 2)
    plt.imshow(
        LL,
        cmap="gray"
    )
    plt.title("LL - Approximation")
    plt.axis("off")

    plt.subplot(2, 3, 3)
    plt.imshow(
        LH,
        cmap="gray"
    )
    plt.title("LH - Horizontal Detail")
    plt.axis("off")

    plt.subplot(2, 3, 4)
    plt.imshow(
        HL,
        cmap="gray"
    )
    plt.title("HL - Vertical Detail")
    plt.axis("off")

    plt.subplot(2, 3, 5)
    plt.imshow(
        HH,
        cmap="gray"
    )
    plt.title("HH - Diagonal Detail")
    plt.axis("off")

    plt.tight_layout()
    plt.show()


# ---------------------------------------------------------
# Save stego image
# ---------------------------------------------------------

def save_dwt_image(
    image,
    output_path
):
    """Save DWT stego image."""

    cv2.imwrite(
        output_path,
        image
    )


# ---------------------------------------------------------
# Main Testing
# ---------------------------------------------------------

if __name__ == "__main__":

    image_path = (
        "images/cover/test.jpg"
    )

    # PNG for lossless testing
    output_path = (
        "images/dwt_stego_test.png"
    )

    secret_message = (
        "StegoSecure 2026! @Test#123"
    )

    # Apply DWT
    image, LL, LH, HL, HH = (
        apply_dwt(image_path)
    )

    print(
        "DWT decomposition completed successfully!"
    )

    print(
        "Original image shape:",
        image.shape
    )

    print(
        "LL shape:",
        LL.shape
    )

    print(
        "LH shape:",
        LH.shape
    )

    print(
        "HL shape:",
        HL.shape
    )

    print(
        "HH shape:",
        HH.shape
    )

    # Convert message to bytes
    secret_data = (
        secret_message.encode("utf-8")
    )

    # DWT embedding
    stego_image = embed_dwt(
        image,
        secret_data
    )

    # Save stego image
    save_dwt_image(
        stego_image,
        output_path
    )

    print(
        "DWT embedding completed successfully!"
    )

    print(
        "Secret message:",
        secret_message
    )

    print(
        "DWT stego image saved at:",
        output_path
    )

    # Read generated stego image
    stego_image = cv2.imread(
        output_path,
        cv2.IMREAD_GRAYSCALE
    )

    if stego_image is None:
        raise ValueError(
            "Unable to read stego image."
        )

    # Extract message
    extracted_data = extract_dwt(
        stego_image
    )

    extracted_message = (
        extracted_data.decode("utf-8")
    )

    print(
        "Extracted message:",
        extracted_message
    )

    # Verify
    if extracted_message == secret_message:

        print(
            "Embedding and extraction test: PASSED"
        )

    else:

        print(
            "Embedding and extraction test: FAILED"
        )

    # Display DWT sub-bands
    display_dwt(
        image,
        LL,
        LH,
        HL,
        HH
    )