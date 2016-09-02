# NLP utils based on protobuf and grpc

## Preparation
- Create a folder under /data/Applications/user_name/ (Disk I/O under this folder is much faster than home directory)
- `cd /data/Applications/user_name/` and follow the steps below

## Check out the repository
- `git clone https://github.com/leebird/nlputils/`

## Initialization
- Only bash is supported. If you default shell is not bash, run `bash` before running the following steps.
- First create a python virtual enviroment: `virtualenv --python=python2 env`. _Note that the virtual enviroment can be placed anywhere, not necessarily under nlputils. If you just want to use nlputils as a module, maybe you want to create the virtual environment in the parent folder of nlputils._
- Activate the virtual enviroment: `. env/bin/activate`
- `bash ./scripts/clear_init.sh`
- Set up environment path variables: `. ./scripts/export_path.sh`
- Run the initialization script: `bash ./scripts/init.sh`
- Compile document.proto to generate python codes: `bash ./scripts/compile_document_proto.sh`

## Example
- Only bash is supported. If you default shell is not bash, run `bash` before running the following steps.
- Activate the virtual enviroment: `. env/bin/activate`
- Set up environment path variables: `. ./scripts/export_path.sh`. Note that these variables can be written into .bashrc so that they are set up when the terminal starts.
- Run `python test/example.py`, it should print a list of structured information.

## Note
- Tested under bash, but not tcsh.
