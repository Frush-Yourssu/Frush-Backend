from skimage.metrics import structural_similarity as ssim 
import numpy as np
import cv2
from fastapi import HTTPException, UploadFile

from enums.fruit import Fruit, FruitPart


# Function to convert an image to RGB
def to_rgb(image):
    if image.shape[2] == 4:  # If the image has 4 channels (RGBA)
        return cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    elif image.shape[2] == 1:  # If the image has 1 channel (grayscale)
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return image  # If the image already has 3 channels (RGB)

# Function for MSE
def mean_squared_error(image1, image2):
    error = np.sum((image1.astype('float') - image2.astype('float'))**2)
    error = error/float(image1.shape[0] * image2.shape[1])
    return error

# Function to determine the maximum pixel value based on dtype
def get_max_pixel_value(dtype):
    if np.issubdtype(dtype, np.uint8):
        return 255.0
    elif np.issubdtype(dtype, np.uint16):
        return 65535.0
    elif np.issubdtype(dtype, np.float32) or np.issubdtype(dtype, np.float64):
        return 1.0  # Assuming normalized floating-point images
    else:
        raise ValueError("Unsupported image dtype")

# Function to normalize MSE
def normalize_mse(mse, image):
    max_pixel_value = get_max_pixel_value(image.dtype)

    max_mse = max_pixel_value ** 2
    
    # Normalize MSE to [0, 1]
    normalized_mse = mse / max_mse
    return normalized_mse

# Function for image compare
def image_comparison(image1, image2):
    # input image must have the same dimension for comparison
    image1 = to_rgb(image1)
    image2 = to_rgb(image2)

    image2 = cv2.resize(image2,(image1.shape[1::-1]),interpolation=cv2.INTER_AREA)

    mse = mean_squared_error(image1, image2)

    # Normalize MSE
    normalized_mse = normalize_mse(mse, image1)

    s = ssim(image1, image2, channel_axis = 2)
    
    # Combine MSE and SSIM into a final similarity score
    # Adjust alpha and beta to control the impact of MSE and SSIM
    alpha = 0.7  # Weight for normalized MSE
    beta = 0.3   # Weight for SSIM
    
    # Final score calculation
    final_score = (1 - normalized_mse) * alpha + s * beta
    
    # Scale score to 0-100
    final_score = final_score * 100
    
    print("Mean Squared Error is {:.2f}".format(mse))
    print("Normalized Mean Squared Error is {:.4f}".format(normalized_mse))
    print("Structural Similarity Measure index is: {:.2f}".format(s))
    print("Final Similarity Score (0-100): {:.2f}".format(final_score))

    return round(final_score, 2)


def compare_fruit(fruit, fruit_part, comparison_image):
    # Dictionary for fruit and fruit part image paths
    # /Users/ggona/Documents/GitHub/학교/Frush-Backend/data/watermelon/watermelon-stripes.png
    image_paths = {
        ("WATER_MELON", "WATER_MELON_STRIPES"): "/app/data/watermelon/watermelon-stripes.png",
        ("WATER_MELON", "WATER_MELON_STEM"): "/app/data/watermelon/watermelon-stem.png",
        ("WATER_MELON", "WATER_MELON_NAVEL"): "/app/data/watermelon/watermelon-navel.png"
    }
    
    # Get the correct image path based on fruit and fruit part
    path = image_paths.get((fruit, fruit_part))
    
    if not path:
        raise HTTPException(status_code=400, detail="Invalid fruit or fruit part")
    
    original_image = cv2.imread(path)
        
    similarity = image_comparison(original_image, comparison_image)

    return similarity