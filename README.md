# Iris - A Neural Network Based Steganalysis tool

## Overview
Iris is an open-source **AI Steganalysis Tool** that uses **Machine Learning** to detect **LSB and BPCS** steganography in PNGs. It is designed to catch steganographic communication by being able to analyse images and guess embed rates with up to +-0.8% accuracy for LSB and +-0.14% accuracy for BPCS.

---

## Features

- **Machine Learning Based Detection**  
  Machine learning based detection means that the tool is able to adjust to unfamiliar images seamlessly to maximise efficency

- **Support for LSB and BPCS steganography**  
  The tool supports detection for both LSB and BPCS, allowing for maximum ability to detect stegos

- **Multi-channel support**  
    Each channel can be analysed individually to detect single-channel or dual-channel embedding

- **Lightweight UI**  
The UI is built in Python with PyQt, making it much more lightweight and less resource-intensive than other frameworks such as Electron

- **Customisable Pathing**  
Model paths are highly customisable within the app, allowing for easy swapping out of different models

- **Settings Saving**  
Settings are saved between uses to allow for the best user experience
---

## Architecture Overview

- **Python** is used to form the backend of the project and to house the Neural Networks
    - **SQL** was used to store training data for loss functions
    - **Numpy** was used to create the arrays that the networks take as input
    - **Tensorflow and Keras** were used to train the AIs, using MAE and Huber Loss to converge at optimal minima
- **C++** was used to generate the stegos used for training for maximum speed
- **PyQt** is used to render the frontend for the project allowing for a lightweight UI

- Models can be found at https://drive.google.com/drive/folders/1EuD-09CzrcAYcQI3dBajPbkV1JIihQX2?usp=sharing
    - Rod is the name of the LSB model, Cone is the name of the BPCS model

---

## Learning Results

- I learnt how to use **Tensorflow and Keras** to train Neural Networks

- I learnt about how Neural Networks work, including **Loss Functions** and **Regressional vs CNN** networks

- I learnt how to use **PyQt** to render a frontend in Python

- I learnt how to manipulate images in **C++** with OpenCV in order to generate the needed stegos

- I learnt how to work with **large datasets** and how to manage them during training
--- 

## Future Improvements

- Support for other steganongraphy methods, such as **adversarial embedding** and **whitespace encoding**

- Training the AIs to reach **lower accuracy** through an architecture change to achieve even better minima

- Support for other image sizes outisde of **256 x 256**

---

## Images Showcase
![App Screenshot](Display%20Images/Display%20Image%201.png)

![App Screenshot](Display%20Images/Display%20Image%202.png)

![App Screenshot](Display%20Images/Display%20Image%203.png)