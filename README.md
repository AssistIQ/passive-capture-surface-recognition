Production version of passive capture.

#  Installation
Make sure to have the latest version of Python. An easy way to manage different Python version can be done using this tool https://github.com/pyenv/pyenv.

```
git clone git@github.com:AssistIQ/passive-capture-surface-recognition.git
cd passive-capture-surface-recognition
pip install --upgrade pip
pip install --no-deps -r requirements.txt
```

#  S3 Uploader
The code for S3 uploading is located in `s3_upload/` folder.

Navigate to `s3_upload/main_s3_upload.py` and fill in the information for these fields:
```
aws_access_key = 'YOUR_ACCESS_KEY'
aws_secret_key = 'YOUR_SECRET_KEY'
aws_bucket_name = 'NAME_OF_BUCKET_TO_UPLOAD_TO'
```

To run the main script use:
`python s3_upload/main_s3_upload.py`

#  Tests
Tests are located in `tests/` folder and are built using the [pytest library](https://docs.pytest.org/en/8.0.x/).
To execute tests run `python -m pytest`.