param(
    [string]$EnvName = "astock-alpha"
)

conda env create -f environment.yml
conda activate $EnvName
pip install -r requirements.txt

