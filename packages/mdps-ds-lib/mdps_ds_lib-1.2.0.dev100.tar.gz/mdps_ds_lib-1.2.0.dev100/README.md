# Mission Data System - MDPS (Unity) Data Service Core library
#### PyPI Location
- https://pypi.org/project/mdps-ds-lib/

#### How to build it
- `conda create -n uds_lib_39 python=3.9`
- `conda activate uds_lib_39`
- `python -m poetry build`
- `python3 -m twine upload --repository pypi dist/*`