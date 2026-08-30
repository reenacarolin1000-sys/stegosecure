import cv2
import numpy as np


# ---------------------------------------------------------
# Convert bytes to binary
# ---------------------------------------------------------

def bytes_to_binary(data):
    """Convert bytes into a binary string."""
    return ''.join(format(byte, '08b') for byte in data)


def binary_to_bytes(binary):
    """Convert binary string into bytes."""
    return bytes(
        int(binary[i:i + 8], 2)
        for i in range(0, len(binary), 8)
    )


# ---------------------------------------------------------
# DCT Embedding
# ---------------------------------------------------------

def embed_dct(image, data):
    """
    Embed secret data using DCT.

    Two middle-frequency coefficients are used
    to represent each secret bit.
    """

    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    gray = np.float32(gray)

    # Convert secret data to binary
    binary_message = bytes_to_binary(data)

    # Add 32-bit message length header
    length_header = format(len(data), '032b')

    binary_message = length_header + binary_message

    message_index = 0

    height, width = gray.shape

    # Middle-frequency coefficients
    pos1 = (3, 2)
    pos2 = (2, 3)

    # Minimum difference between coefficients
    alpha = 20.0

    # Process 8x8 blocks
    for row in range(0, height - 7, 8):

        for col in range(0, width - 7, 8):

            if message_index >= len(binary_message):
                return np.clip(
                    gray,
                    0,
                    255
                ).astype(np.uint8)

            # Extract block
            block = gray[
                row:row + 8,
                col:col + 8
            ]

            # Apply DCT
            dct_block = cv2.dct(block)

            r1, c1 = pos1
            r2, c2 = pos2

            coeff1 = dct_block[r1, c1]
            coeff2 = dct_block[r2, c2]

            bit = binary_message[message_index]

            # Embed 1
            if bit == '1':

                if coeff1 <= coeff2 + alpha:
                    dct_block[r1, c1] = coeff2 + alpha

            # Embed 0
            else:

                if coeff2 <= coeff1 + alpha:
                    dct_block[r2, c2] = coeff1 + alpha

            # Apply inverse DCT
            modified_block = cv2.idct(dct_block)

            # Store modified block
            gray[
                row:row + 8,
                col:col + 8
            ] = modified_block

            message_index += 1

    # Check capacity
    if message_index < len(binary_message):
        raise ValueError(
            "Message is too large for this image."
        )

    return np.clip(
        gray,
        0,
        255
    ).astype(np.uint8)


# ---------------------------------------------------------
# DCT Extraction
# ---------------------------------------------------------

def extract_dct(stego_image):
    """
    Extract secret data from a DCT stego image.
    """

    # Convert to grayscale if required
    if len(stego_image.shape) == 3:
        gray = cv2.cvtColor(
            stego_image,
            cv2.COLOR_BGR2GRAY
        )
    else:
        gray = stego_image

    gray = np.float32(gray)

    height, width = gray.shape

    pos1 = (3, 2)
    pos2 = (2, 3)

    binary_data = ''

    # First extract 32-bit message length
    for row in range(0, height - 7, 8):

        for col in range(0, width - 7, 8):

            block = gray[
                row:row + 8,
                col:col + 8
            ]

            dct_block = cv2.dct(block)

            coeff1 = dct_block[
                pos1[0],
                pos1[1]
            ]

            coeff2 = dct_block[
                pos2[0],
                pos2[1]
            ]

            # Compare coefficient strengths
            if coeff1 > coeff2:
                bit = '1'
            else:
                bit = '0'

            binary_data += bit

            if len(binary_data) == 32:
                break

        if len(binary_data) == 32:
            break

    # Check header
    if len(binary_data) < 32:
        raise ValueError(
            "Unable to read message length."
        )

    # Get message length
    message_length = int(
        binary_data[:32],
        2
    )

    required_bits = 32 + (
        message_length * 8
    )

    # Extract complete message
    binary_data = ''

    for row in range(0, height - 7, 8):

        for col in range(0, width - 7, 8):

            block = gray[
                row:row + 8,
                col:col + 8
            ]

            dct_block = cv2.dct(block)

            coeff1 = dct_block[
                pos1[0],
                pos1[1]
            ]

            coeff2 = dct_block[
                pos2[0],
                pos2[1]
            ]

            if coeff1 > coeff2:
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
# Save image
# ---------------------------------------------------------

def save_dct_image(image, output_path):
    """Save the DCT stego image."""
    cv2.imwrite(
        output_path,
        image
    )


# ---------------------------------------------------------
# Test DCT embedding and extraction
# ---------------------------------------------------------

if __name__ == "__main__":

    image_path = "images/cover/test.jpg"

    # PNG is used for lossless testing
    output_path = "images/dct_stego_test.png"

    secret_message = "StegoSecure 2026! @Test#123"

    # Read cover image
    image = cv2.imread(
        image_path
    )

    if image is None:
        raise ValueError(
            "Unable to read the image."
        )

    # Convert message to bytes
    secret_data = secret_message.encode(
        "utf-8"
    )

    # Embed message
    stego_image = embed_dct(
        image,
        secret_data
    )

    # Save stego image
    save_dct_image(
        stego_image,
        output_path
    )

    print(
        "DCT embedding completed successfully!"
    )

    print(
        "Secret message:",
        secret_message
    )

    print(
        "DCT stego image saved at:",
        output_path
    )

    # Read generated stego image
    stego_image = cv2.imread(
        output_path,
        cv2.IMREAD_GRAYSCALE
    )

    # Extract message
    extracted_data = extract_dct(
        stego_image
    )

    extracted_message = extracted_data.decode(
        "utf-8"
    )

    print(
        "Extracted message:",
        extracted_message
    )

    # Verify result
    if extracted_message == secret_message:

        print(
            "Embedding and extraction test: PASSED"
        )

    else:

        print(
            "Embedding and extraction test: FAILED"
        )