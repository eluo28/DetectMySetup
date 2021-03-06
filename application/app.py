import streamlit as st
import numpy as np
import json
import random
import cv2
import torch
from PIL import Image

# Detectron2 imports
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog
from detectron2.engine import DefaultPredictor

subset = ["Computer keyboard","Computer monitor","Computer mouse","Lamp","Laptop","Microphone"]

subset.sort()

# Set up default variables
CONFIG_FILE = "model/config.yaml"
MODEL_FILE = "model/model_final.pth"

# TODO Way to load model with @st.cache so it doesn't take a long time each time
@st.cache(allow_output_mutation=True)
def create_predictor(model_config, model_weights, threshold):
    """
    Loads a Detectron2 model based on model_config, model_weights and creates a default
    Detectron2 predictor.

    Returns Detectron2 default predictor and model config.
    """
    cfg = get_cfg()
    cfg.merge_from_file(model_config)
    cfg.MODEL.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    #st.write(f"Making prediction using: {cfg.MODEL.DEVICE}")
    cfg.MODEL.WEIGHTS = model_weights
    cfg.MODEL.SCORE_THRESH_TEST = threshold

    predictor = DefaultPredictor(cfg)

    return cfg, predictor


def make_inference(image, model_config, model_weights, threshold=0.5, n=5, save=False):
  """
  Makes inference on image (single image) using model_config, model_weights and threshold.

  Returns image with n instance predictions drawn on.

  Params:
  -------
  image (str) : file path to target image
  model_config (str) : file path to model config in .yaml format
  model_weights (str) : file path to model weights 
  threshold (float) : confidence threshold for model prediction, default 0.5
  n (int) : number of prediction instances to draw on, default 5
    Note: some images may not have 5 instances to draw on depending on threshold,
    n=5 means the top 5 instances above the threshold will be drawn on.
  save (bool) : if True will save image with predicted instances to file, default False
  """
  # Create predictor and model config
  cfg, predictor = create_predictor(model_config, model_weights, threshold)

  # Convert PIL image to array
  image = np.asarray(image)
  
  # Create visualizer instance
  visualizer = Visualizer(img_rgb=image,
                          # TODO: maybe this metadata variable could be improved?.. yes it can
                          metadata=MetadataCatalog.get(cfg.DATASETS.TEST[0]).set(thing_classes=subset),
                          #metadata=MetadataCatalog.get(cfg.DATASETS.TEST[0]),
                          scale=0.3)
  outputs = predictor(image) # Outputs: https://detectron2.readthedocs.io/modules/structures.html#detectron2.structures.Instances
  
  # Get instance predictions from outputs
  instances = outputs["instances"]

  # Draw on predictions to image
  vis = visualizer.draw_instance_predictions(instances[:n].to("cpu"))

  return vis.get_image(), instances[:n]

def main():
    st.title("Detect My Setup")
    st.write("This application uses a machine learning learning model to outline and classify common objects in a computer setup.")
    st.write("## How does it work?")
    st.write("Add an image of a setup and the model will detect items like the example below:")
    st.image(Image.open("images/set.png"), 
             caption="Example of model being run.", 
             use_column_width=True)
    st.write("## Upload your own image")
    uploaded_image = st.file_uploader("Choose a png or jpg image", 
                                      type=["jpg", "png", "jpeg"])

    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image.", use_column_width=True)
        
        n_boxes_to_draw = st.slider(label="Number of objects to detect (boxes to draw)",
                                    min_value=1, 
                                    max_value=10, 
                                    value=1)

        image = image.convert("RGB")
      
    if st.button("Make a prediction"):
          # TODO: Add progress/spinning wheel here
          "Making a prediction and drawing", n_boxes_to_draw, "object bedboxes on your image..."
          with st.spinner("Analyzing the image..."):
            custom_pred, preds = make_inference(
                image=image,
                model_config=CONFIG_FILE,
                model_weights=MODEL_FILE,
                n=n_boxes_to_draw
            )
            st.image(custom_pred, caption="Objects detected.", use_column_width=True)
          classes = np.array(preds.pred_classes)
          st.write("Objects detected:")
          st.write([subset[i] for i in classes])

if __name__ == "__main__":
    main()