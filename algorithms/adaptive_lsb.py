import cv2
import numpy as np


def bytes_to_binary(data):
    """Convert bytes into a binary string."""
    return ''.join(format(byte, '08b') for byte in data)


def binary_to_bytes(binary):
    """Convert a binary string into bytes."""
    return bytes(
        int(binary[i:i + 8], 2)
        for i in range(0, len(binary), 8)
    )


def get_bits_per_pixel(region):
    """
    Decide the number of bits to embed based on texture.

    Smooth       -> 1 bit
    Moderate     -> 2 bits
    Strong Edge  -> 3 bits
    """
    if region == 0:
        return 1
    elif region == 1:
        return 2
    else:
        return 3


def embed_message(image, data, texture_map):
    """
    Embed binary data adaptively into the blue channel.

    data:
        Secret data as bytes.

    texture_map:
        Sobel-based texture classification map.
    """

    stego_image = image.copy()

    # Convert data to binary
    binary_message = bytes_to_binary(data)

    # Store message length in the first 32 bits
    length_header = format(len(data), '032b')

    binary_message = length_header + binary_message

    message_index = 0

    height, width, channels = stego_image.shape

    for row in range(height):
        for col in range(width):

            if message_index >= len(binary_message):
                return stego_image

            # Get texture region
            region = texture_map[row, col]

            # Determine embedding capacity
            bits_to_embed = get_bits_per_pixel(region)

            remaining_bits = len(binary_message) - message_index

            bits_to_use = min(
                bits_to_embed,
                remaining_bits
            )

            bits = binary_message[
                message_index:
                message_index + bits_to_use
            ]

            # Pad if required
            bits = bits.ljust(bits_to_embed, '0')

            value = int(bits, 2)

            # Create LSB mask
            mask = (1 << bits_to_embed) - 1

            # Read blue channel
            pixel = int(stego_image[row, col, 0])

            # Replace LSBs
            pixel = (pixel & ~mask) | value

            stego_image[row, col, 0] = np.clip(
                pixel,
                0,
                255
            )

            message_index += bits_to_use

    if message_index < len(binary_message):
        raise ValueError(
            "Message is too large for this image."
        )

    return stego_image


def extract_message(stego_image, texture_map):
    """
    Extract the hidden binary data from the stego image.

    Returns:
        Extracted data as bytes.
    """

    binary_data = ''

    height, width, channels = stego_image.shape

    # First extract the 32-bit message length header
    for row in range(height):
        for col in range(width):

            region = texture_map[row, col]
            bits_to_extract = get_bits_per_pixel(region)

            pixel = int(stego_image[row, col, 0])

            mask = (1 << bits_to_extract) - 1

            value = pixel & mask

            binary_data += format(
                value,
                f'0{bits_to_extract}b'
            )

            if len(binary_data) >= 32:
                break

        if len(binary_data) >= 32:
            break

    # Read message length
    message_length = int(binary_data[:32], 2)

    required_bits = 32 + (message_length * 8)

    # Continue extraction
    binary_data = ''

    for row in range(height):
        for col in range(width):

            region = texture_map[row, col]
            bits_to_extract = get_bits_per_pixel(region)

            pixel = int(stego_image[row, col, 0])

            mask = (1 << bits_to_extract) - 1

            value = pixel & mask

            binary_data += format(
                value,
                f'0{bits_to_extract}b'
            )

            if len(binary_data) >= required_bits:
                message_binary = binary_data[
                    32:required_bits
                ]

                return binary_to_bytes(message_binary)

    raise ValueError(
        "Unable to extract the complete message."
    )


def save_stego_image(stego_image, output_path):
    """Save the stego image."""
    cv2.imwrite(output_path, stego_image)


if __name__ == "__main__":

    image_path = "images/cover/test.jpg"
    output_path = "images/stego_test.png"

    secret_message = "StegoSecure 2026! @Test#123"

    # Read cover image in color
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(
            "Unable to read the image."
        )

    # Get texture map from Sobel
    from sobel import apply_sobel

    _, edge_image, texture_map = apply_sobel(
        image_path
    )

    # Convert text to bytes
    secret_data = secret_message.encode("utf-8")

    # Embed message
    stego_image = embed_message(
        image,
        secret_data,
        texture_map
    )

    # Save stego image
    save_stego_image(
        stego_image,
        output_path
    )

    print("Adaptive LSB embedding completed successfully!")
    print("Secret message:", secret_message)
    print("Stego image saved at:", output_path)

    # Read generated stego image
    stego_image = cv2.imread(output_path)

    # Extract message
    extracted_data = extract_message(
        stego_image,
        texture_map
    )

    extracted_message = extracted_data.decode(
        "utf-8"
    )

    print("Extracted message:", extracted_message)

    if extracted_message == secret_message:
        print("Embedding and extraction test: PASSED")
    else:
        print("Embedding and extraction test: FAILED")