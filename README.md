# Install

## Preparation
- Create a folder under /data/Applications/user_name/ (Disk I/O under this folder is much faster than home directory)
- `cd /data/Applications/user_name/` and follow the steps below

## Check out the repository
- `git clone https://github.com/leebird/nlputils/`

## Initialization
- First create a python virtual enviroment: `virtualenv --python=python2 env`
- Activate the virtual enviroment: `. env/bin/activate`
- Set up environment path variables: `. export_path.sh` for bash or `source tcsh_export_path.sh` for tcsh
- Run the initialization script: `sh init_client.sh`
- Compile document.proto to generate python codes: `sh compile_document_proto.sh`

## Example
- Activate the virtual enviroment: `. env/bin/activate`
- Set up environment path variables: `. export_path.sh` for bash or `source tcsh_export_path.sh` for tcsh
- Run `python example.py`, it should print a list of structured information.

## Note
- Tested under bash, but not tcsh.
