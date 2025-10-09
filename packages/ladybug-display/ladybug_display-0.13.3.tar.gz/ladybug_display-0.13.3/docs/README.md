
## Usage
For generating the documents locally use commands below from the root folder. 

```shell
# install dependencies
cd ladybug_display
pip install -r dev-requirements.txt

# generate rst files for modules
sphinx-apidoc -f -e -d 4 -o ./docs ./ladybug_display
# build the documentation under _build/docs folder
sphinx-build -b html ./docs ./docs/_build/docs
```
