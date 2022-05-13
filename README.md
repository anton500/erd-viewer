# ERD viewer

Python web app for vizualisation relationships in a database using Graphviz graphs.

## Installation

Clone the git repository and build the docker image:  
`docker build -t erd-viewer:latest github.com/anton500/erd-viewer`

## Quickstart

1. Extract into json file db structure and relationships between tables.  
Sample json and sql script (mssql) provided in the folders `data` and `sql`.

2. Run docker container with specified `path to json file`:  
`docker run -d --name erd-viewer -v /path/to/json/file:/usr/erd-viewer/data/db_schema.json -p 4444:80 erd-viewer:latest`

3. Go to `http://localhost:4444`

## Features

### Related tables

Here you can see all tables related to the choosen table at specified depth.

### Find a route **(Not implemented yet)**

In this mode you can find how two choosen tables can be related thought other tables.

### Schema **(Not implemented yet)**

Shows all the tables and relations between them in the choosen schema.

### Database **(Not implemented yet)**

Shows all available infromation from json file - all schemas, tables and relations.
