# 📦 alidaparse

`alidaparse` is a Python package for generating CLI arguments required by ALIDA's services.
Instead of creating each time an `arguments.py`, a simple import of `alidaparse` will do the trick!

---

## 🚀 Features

- Automatically generate dataset/model argument for a service
- Multiple arguments are supported

---

## 📥 Installation

Install via pip:

```bash
pip install alidaparse
```

Or install from source:

```bash
git https://github.com/JosephMartinelli/alidaparse.git
cd alidaparse
pip install .
```

---

## 🧪 Usage
Usually a service of the ALIDA's platform needs to declare an `arguments.py` file in which it defines
a series of an arguments it needs in input to work. This file looks something like this:
```python
# contents of arguments.py
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--input-dataset", dest="input_dataset", type=str, required=True)
parser.add_argument(
    "--input-dataset.minio_bucket", dest="input_minio_bucket", type=str, required=True
)
...
```
Those arguments need to be repeated for each input/ouput dataset and model that the service needs to use.

With `alidaparse.py` you simply import a factory class that will automatically 
generate those arguments for you:
```python
# contents of main.py
from alidaparse.input import InDatasetFactory

dataset = InDatasetFactory.from_cli()
```  
And running `main.py` will have this effect:
```python
python.exe main.py

usage: main.py [-h] --input-dataset INPUT_DATASET
                    --input-dataset.minio_bucket INPUT_MINIO_BUCKET
                    --input-dataset.minIO_URL INPUT_MINIO_URL
                    --input-dataset.minIO_ACCESS_KEY INPUT_ACCESS_KEY
                    --input-dataset.minIO_SECRET_KEY INPUT_SECRET_KEY
main.py: error: the following arguments are required: --input-dataset, --input-dataset.minio_bucket, --input-dataset.minIO_URL, --input-dataset.minIO_ACCESS_KEY, --input-dataset.minIO_SECRET_KEY
```  
---
You can also declare multiple arguments by passing an integer to `from_cli(n)`
```python
# contents of main.py
from alidaparse.input import InDatasetFactory

dataset = InDatasetFactory.from_cli(n=2)
```  
```python
usage: main.py [-h] --input-dataset-1 INPUT_DATASET_1
--input-dataset-1.minio_bucket INPUT_DATASET_1_MINIO_BUCKET
--input-dataset-1.minIO_URL INPUT_DATASET_1_MINIO_URL
--input-dataset-1.minIO_ACCESS_KEY INPUT_DATASET_1_ACCESS_KEY
--input-dataset-1.minIO_SECRET_KEY INPUT_DATASET_1_SECRET_KEY
--input-dataset-2 INPUT_DATASET_2
--input-dataset-2.minio_bucket INPUT_DATASET_2_MINIO_BUCKET
--input-dataset-2.minIO_URL INPUT_DATASET_2_MINIO_URL
--input-dataset-2.minIO_ACCESS_KEY INPUT_DATASET_2_ACCESS_KEY
--input-dataset-2.minIO_SECRET_KEY INPUT_DATASET_2_SECRET_KEY
main.py: error: the following arguments are required: --input-dataset-1, --input-dataset-1.minio_bucket, 
--input-dataset-1.minIO_URL, --input-dataset-1.minIO_ACCESS_KEY, --input-dataset-1.minIO_SECRET_KEY, 
--input-dataset-2, --input-dataset-2.minio_bucket, --input-dataset-2.minIO_URL, --input-dataset-2.minIO_ACCESS_KEY, 
--input-dataset-2.minIO_SECRET_KEY
```
`alidaparse.py` has classes for dealing with input/output datasets, models and custom params. Simply
import `from alidaparse.input import InDataset,InModel,InParam`
## 📁 Project Structure

```
alidaparse/
├── input/
│   ├── __init__.py
│   └── InDataset.py
│   └── InModel.py
│   └── InParam.py
├── output/
│   ├── __init__.py
│   └── OutDataset.py
│   └── OutModel.py
├── __init__.py
├── setup.py
├── pyproject.toml
└── README.md
```

[//]: # (├── test/)

[//]: # (│   ├── conftest.py # Needed for pytest)

[//]: # (│   ├── test_input.py)

[//]: # (│   └── test_output.py)

---

## 🛠 Development

To install dependencies:

```bash
pip install -r requirements.txt
```  

[//]: # (To run tests with arguments to pass to the services, you can invoke pytest)

[//]: # (by passing a `--vars` value that will be passed to the argument of the test)

[//]: # (functions:)

[//]: # (```bash)

[//]: # (cd alidaparse/test)

[//]: # (pytest --vars custom-param1=custom-value1,custom-param2=custom-value2 ...)

[//]: # (# or)

[//]: # (pytest --vars custom-param=custom-value --vars custom-param2=custom-value2)

[//]: # (```  )

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
