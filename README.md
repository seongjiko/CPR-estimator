# Harnessing Optical Flow in Deep Learning Framework for Cardiopulmonary Resuscitation Training
> Elsevier, Expert System with Application journal

# Overview

<center> 
  <img width="876" alt="image" src="https://github.com/seongjiko/CPR-estimator/assets/46768743/7979d7ac-6f67-4866-85d9-9f2b89db91cb"> 
</center>



> The global rise in out-of-hospital cardiac arrests underscores the importance of cardiopulmonary resuscitation (CPR) training. However, the high cost of feedback-equipped manikins limits widespread CPR education. To address this, we propose a deep learning solution that transforms smartphone-captured chest compression videos into images for feedback. This model assesses four key CPR quality indicators: compression count, depth, complete release, and hand positioning. By using composite-image evaluation, we simplify video processing and achieve effective performance. This cost-effective approach not only broadens CPR educational opportunities but also aims to enhance survival rates for cardiac arrest patients.

# HQC Components Estimator
HQC Components Estimator is a software that estimates High-Quality CPR (HQC) components from a CPR video that lasts more than 30 seconds. 
![image](https://github.com/seongjiko/CPR-estimator/assets/105999203/49196c14-d13f-4568-8cec-5f0260fb84c2)

<!-- ## real-time estimator demo -->

<!-- https://github.com/seongjiko/CPR-estimator/assets/105999203/602b4f1c-747a-40ce-8e14-6f44c984b91d -->

## Getting Started

Here's how to get this software up and running on your local machine.

### Prerequisites

The software runs on Python version 3.8

CUDA must be installed for GPU environment support. You can confirm this by running the following Python code:

```python
import torch
print(torch.cuda.is_available())
```

This should return True.





### Installation

1. Clone the repository to your local machine.

```bash
git clone https://github.com/seongjiko/CPR-estimator.git
```

2. Navigate into the project directory and install the dependencies using pip.

```bash
conda env create -f requirements.yaml
```

## Usage

After successful installation of all dependencies, run the software by navigating to the project directory and executing the main Python script.

```bash
python main.py
```

Upload your 30-second CPR video by either dragging and dropping the file onto the interface or clicking the 'Select File' button. *Videos can be recorded with any camera, including smartphones, but please ensure the camera remains stationary during recording.* After uploading the video, click on the 'Start Analysis' button to initiate the estimation process. The results will be displayed upon completion.

## run real-time estimate

```bash
python main_real_time.py
```


## Acknowledgments

This work was supported by the National Research Foundation of Korea(NRF) grant funded by the Korea government(MSIT) (No. 2021R1F1A1060211) and in part by the National Research Foundation of Korea (NRF) funded by the Korean Government (MSIT) under Grant NRF-2022R1A4A1033600. 

