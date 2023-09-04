# HQC Components Estimator
HQC Components Estimator is a software that estimates High-Quality CPR (HQC) components from a CPR video that lasts more than 30 seconds. 

![image](https://github.com/seongjiko/CPR-estimator/assets/46768743/827fbb60-0839-4bf1-8320-ec0023d69a03)

real-time estimator demo

https://github.com/seongjiko/CPR-estimator/assets/105999203/602b4f1c-747a-40ce-8e14-6f44c984b91d

## Getting Started

Here's how to get this software up and running on your local machine.

### Prerequisites

The software runs on Python version 3.7 and above, but below version 3.11.

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
pip install -r requirements.txt
```

## Usage

After successful installation of all dependencies, run the software by navigating to the project directory and executing the main Python script.

```bash
python main.py
```

Upload your 30-second CPR video by either dragging and dropping the file onto the interface or clicking the 'Select File' button. *Videos can be recorded with any camera, including smartphones, but please ensure the camera remains stationary during recording.* After uploading the video, click on the 'Start Analysis' button to initiate the estimation process. The results will be displayed upon completion.

run real-time estimate

```bash
python main_real_time.py
```


## Acknowledgments

This project is a joint medical initiative by Dongtan Sacred Heart Hospital and the Department of Software at Hallym University, supported by a grant from the Ministry of Science and ICT of South Korea.

