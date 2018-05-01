# Item Catalog

This item catalog allows users to create, edit, and delete information about items. This particular implementation is a musical instrument catalog.

## Setting Up

#### What you'll need:
- Python 3
- PostgreSQL
- Python packages:
    * Flask
    * SQLalchemy
    * oauth2client
    * requests

#### What to do:
1. Install PostgreSQL. Set up a user account with a password and create a database. In the file `database_setup.py`, modify the variable `database_info` to reflect these changes. In particular, you may need to change the username, password, and/or database.
2. With python 3, run the `database_setup.py`. This will define the database tables needed for the catalog and create the SQLalchemy object relations for the database.
3. With python 3, run `database_init.py`. This will insert the categories needed for the musical instrument catalog. You can change these categories according to your liking.
4. Run the application with `python3 catalog_project.py`. To test the application locally, connect to `https://localhost:5000` with a browser. It is **imperative** that you use https to connect to the application in order for Google's and Facebook's OAuth to work. Furthermore, you **must** use `localhost` as the domain name, since the application is currently registered under that domain with Google and Facebook.
5. To clear the database and delete all current tables, run `python3 database_clean.py`. This will give you a clean slate; you can then go from step 2 for a fresh start.

#### User Notes:

- You must be logged in to create, update, or delete items within the catalog.
- Items can only be edited or deleted by the user who created the item.
- A category cannot have two instruments with the same name.
- Downloading the catalog in JSON format:
    * Use the `/catalog.json` path to download the entire catalog.
    * `/catalog/<category_name>.json` to download the given category.
    * `/catalog/<category_name>/<instrument_name>.json` to download a specific instrument.

## Project Overview

This project implements a catalog that can keep track of a variety of items within specific categories. Users can carry out CRUD (create, read, update, delete) operations within the catalog. Users can also download the catalog using JSON endpoints.

The data is stored in a PostgreSQL database. Flask is the framework used in the backend, which is written in Python. SQLalchemy is used to communicate with the database from within the Flask backend.

User authentication and authorization is carried out through third-party OAuth providers, Google and Facebook. The application does restrict CRUD operations based on a user's authorization status. The website also implements measures to protect against CSRF attacks.
