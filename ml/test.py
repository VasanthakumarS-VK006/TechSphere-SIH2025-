import torch
from torchvision import models, transforms
from PIL import Image
import torch.nn as nn

# --- 1. CONFIGURATION ---
MODEL_PATH = 'pothole_severity_optimized_model.pth'
IMAGE_TO_TEST = 'image.jpg' # IMPORTANT: Change this to your image's filename
NUM_CLASSES = 3

# --- 2. LOAD THE TRAINED MODEL ---
# First, define the model architecture (must be the same as during training)
model = models.resnet50() # We don't need pre-trained weights here, as we'll load our own
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, NUM_CLASSES)

# Get the device
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# Load the saved model weights
# The map_location argument is important if you trained on a GPU but are predicting on a CPU
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))

# Move the model to the appropriate device
model.to(device)

# Set the model to evaluation mode
# This is crucial as it disables training-specific layers like dropout
model.eval()
print("Model loaded successfully and set to evaluation mode.")

# --- 3. PREPARE THE IMAGE ---
# Create the same transformation pipeline as used for the validation set
# It's critical that the input image is transformed in the exact same way
inference_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# --- 4. PREDICTION FUNCTION ---
def predict_severity(image_path):
    try:
        # Open the image file
        image = Image.open(image_path).convert("RGB")
    except FileNotFoundError:
        print(f"Error: The file '{image_path}' was not found.")
        return None

    # Apply the transformations and add a "batch" dimension
    image_tensor = inference_transform(image).unsqueeze(0)
    
    # Move the tensor to the same device as the model
    image_tensor = image_tensor.to(device)

    # Make the prediction
    with torch.no_grad(): # Disable gradient calculation for inference
        outputs = model(image_tensor)
        # Get the index of the highest score, which corresponds to the predicted class
        _, predicted_idx = torch.max(outputs, 1)

    return predicted_idx.item()

# --- 5. RUN PREDICTION ---
if __name__ == '__main__':
    # The class names must match the order from your training data (0, 1, 2)
    class_names = ['Minor Pothole', 'Medium Pothole', 'Major Pothole']
    
    # Get the prediction
    predicted_class_index = predict_severity(IMAGE_TO_TEST)

    # Print the result
    if predicted_class_index is not None:
        predicted_class_name = class_names[predicted_class_index]
        print(f"\nImage: '{IMAGE_TO_TEST}'")
        print(f"Predicted Severity: '{predicted_class_name}' (Class {predicted_class_index})")