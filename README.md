Production version of passive capture.

## Installation
Skip the first two steps if you aren't using anaconda virtual envs

```
conda create -n "myenv" python=3.10
cd <myenv>
git clone git@github.com:AssistIQ/passive-capture-surface-recognition.git
pip install --upgrade pip
cd passive-capture-surface-prototype
pip install --no-deps -r requirements.txt
```

## Run each component in a separate terminal

#### Image segmentation and feature matching for inference images located in folder ./video_frame_to_be_processed
If you don't want to run the second component that captures images for processing, you can manually copy your own images directly into ```video_frame_to_be_processed``` for processing.

```python segment_and_feature_match.py```
   
#### Monitor surface for packages being added and removed
```python prep_area_monitor.py```

## S3 Uploader
The code for S3 uploading is located in `s3_upload/` folder.
To run the main script use:
`python s3_upload/main_s3_upload.py`

## Tests
Tests are located in `tests/` folder and are built using the [pytest library](https://docs.pytest.org/en/8.0.x/).

To execute tests run `python -m pytest`.
