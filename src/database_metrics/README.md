# Capturing Database Metrics
This module contains methods for collecting metrics on the database server under different conditions.

## Usage
1. Using the [Docker tutorials](https://github.com/cmu-delphi/delphi-epidata/blob/main/docs/epidata_development.md),
install Docker and clone all the relevant repositories to a working directory. Do not build the images yet.
2. Obtain the test data you will be running. Place it into a `common_full/`folder in the same working directory, with 
sub folders corresponding to the production ingestion structure: `common_full/covidcast/receiving/<data_source>/filename`
3. Before building the images, you will need to make two edits. These can be achieved by navigating to the 
`repos/delphi/operations/src/database_metrics/` directory and running `setup.sh` (you may have to chmod u+x) the file:  
    a. Edit `repos/delphi/operations/src/secrets.py` by setting `db.host = 'delphi_database_epidata'` and 
    `set db.epi = ('user', 'pass')`, which will match the testing docker image.  
    b. Add `COPY common_full common_full` to `repos/delphi/operations/dev/docker/python/Dockerfile` after copying source files.
4. Continue with the tutorial to complete the following steps:
    a. Build the `delphi_web`, `delphi_web_epidata`, `delphi_database`, and `delphi_python` images. 
    b. Create the `delphi-net` network.  
    c. Run the database and web server.  
5. TODO #35. TBD based on exact user-facing implementation