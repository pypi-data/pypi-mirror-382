# RAISE Synthetic Data Generator
A Python package to generate shareable versions of tabular datasets ready to upload to the [**RAISE platform**](https://portal.raise-science.eu).
The package can also be used beyond the scope of the RAISE project as a lightweight synthetic data generator.

## Features
The package currently provides a single main function: **`generate_synthetic_data`**.

### Main capabilities
- **Input flexibility**
  Accepts either:
  - A CSV file path, or
  - A `pandas.DataFrame`.

- **Automatic or manual model selection**
  - `"auto-select"` (default) automatically chooses the best synthetic data generation model based on simulations carried out on the input data.
  - You can also specify a model explicitly (for the moment one of `CTGAN`, `TVAE` or `Copulas`).

- **Synthetic data generation**
  - Generates a synthetic dataset with the same properties as the input data.
  - Number of synthetic samples to generate can be specified via `n_samples` (defaults to the size of the input data).

- **Results storage**
  - Saves the generated synthetic dataset as `synthetic_data.csv`.
  - Stores model information (`info.txt`) inside the chosen output folder.
  - Creates a run-specific folder under the desired output path.

- **Evaluation report (optional)**
  - If `evaluation_report=True` (default), runs a quality assessment comparing original vs synthetic data.
  - Produces an evaluation report (`evaluation_report.pdf`) with figures and summary statistics.

- **Logging and error handling**
  - Provides informative log messages for each step (dataset loading, model selection, data generation, report creation).
  - Exceptions are logged with full traceback and re-raised for debugging.


## Installation
You can install `raise-synthetic-data-generator` directly from PyPI using pip:

```bash
pip install raise-synthetic-data-generator
```

## Usage
```python
from raise_synthetic_data_generator import generate_synthetic_data
import pandas as pd

# Example input dataframe
df = pd.DataFrame(
    {"age": [23, 35, 44, 29, 31], "country": ["ES", "FR", "DE", "IT", "ES"]}
)

# Generate synthetic data (in memory + saved to disk)
generate_synthetic_data(
    dataset=df,  # if desired the CSV filename can also be given
    selected_model="auto-select",  # or explicitly: "CTGAN", "TVAE" or "Copulas
    n_samples=10,  # number of synthetic samples to generate
    evaluation_report=True,  # if true (evaluation PDF report is generated)
    output_dir="results",  # base output directory (if none, results path will be created)
    run_name="demo-run",  # optional run name (this will be the subfolder where generated objects will be stored, if none a subfolder will be created)
)
```

This will save in specified output folder:
- The generated synthetic (`synthetic_data.csv`)
- A text file with the applied model information (`info.txt`)
- (If selected) A folder with resulted evaluation figures (`evaluation_figures`).
- (If selected) A PDF report with synthetic data quality evaluation results (`evaluation_report.pdf`).

## Usage Examples
Code examples demonstrating how to use the `raise-synthetic-data-generator` package are provided in the `examples` folder of the repository. You can explore these examples to understand how to utilize the functionality of the package.

To get started, check the `examples` folder for various scripts and notebooks, such as:
- **`generate_synthetic_data.ipynb`**: A Jupyter Notebook with step-by-step instructions for generating synthetic data of your dataset.


## License
This project is licensed under the European Union Public License (EUPL) version 1.2. See the LICENSE file for more details.

## Contributing
We welcome contributions! If you'd like to contribute, please fork the repository, make changes, and submit a pull request. Contributions are subject to the terms of the EUPL license.

## Contact
For any inquiries, feel free to reach out via the following email: info@raise-science.eu.
More about the project: https://raise-science.eu
