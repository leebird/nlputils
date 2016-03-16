# Install

## Preparation
- Create a folder under /data/Applications/user_name/ (Disk I/O under this folder is much faster than home directory)
- `cd /data/Applications/user_name/` and follow the steps below

## Check out the repository
- `git clone https://github.com/leebird/nlputils/`

## Initialization
- First create a python virtual enviroment: `virtualenv --python=python2 env`. _Note that the virtual enviroment can be placed anywhere, not necessarily under nlputils. If you just want to use nlputils as a module, maybe you want to create the virtual environment in the parent folder of nlputils._
- Activate the virtual enviroment: `. env/bin/activate` for bash or `source env/bin/activate.csh` for tcsh
- `cd scripts`
- Set up environment path variables: `. export_path.sh` for bash or `source tcsh_export_path.sh` for tcsh
- Run the initialization script: `sh init.sh`
- Compile document.proto to generate python codes: `sh compile_document_proto.sh`

## Example
- Activate the virtual enviroment: `. env/bin/activate` for bash or `source env/bin/activate.csh` for tcsh
- `cd script` and set up environment path variables: `. export_path.sh` for bash or `source tcsh_export_path.sh` for tcsh. Note that these variables can be written into .bashrc so that they are set up when the terminal starts.
- Run `python test/example.py`, it should print a list of structured information.

## Note
- Tested under bash, but not tcsh.
