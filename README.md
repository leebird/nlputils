# Install

## Check out the repository
- git clone https://github.com/leebird/nlputils/

## Initialization
- First create a python virtual enviroment: `virtualenv --python=python2 env`
- Activate the virtual enviroment: `. env/bin/activate`
- Set up environment path variables: `. export_path.sh`
- Run the initialization script: `sh init_client.sh`
- Compile document.proto to generate python codes: `sh compile_document_proto.sh`

## Example
- Activate the virtual enviroment: `. env/bin/activate`
- Set up environment path variables: `. export_path.sh`
- `python example.py`
