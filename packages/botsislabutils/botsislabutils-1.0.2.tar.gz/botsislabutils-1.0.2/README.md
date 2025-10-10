The Botsis Lab Utilities package provides a set of commonly used tools within projects developed at the Botsis Lab at Johns Hopkins University.

## Installation

The package can be installed using pip:

pip install botsislabutils

## Available Modules

### MySQL Interface

The `mysql_interface` module provides a set of functions for commonly used MySQL operations.

Dependencies:

- A set of environment variables for MySQL connection:
  - `DATABASE_USER`: MySQL username
  - `DATABASE_PASS`: MySQL password
  - `DATABASE_HOST`: MySQL host (default: localhost)
  - `DATABASE_PORT`: MySQL port (default: 3306)
  - `DATABASE_SCHEMA_NAME`: MySQL database name

### Configuration

The `config_manager` module provides functions for reading and writing configuration to and from a MySQL database.

Dependencies:

- MySQL database connection (using the `mysql_interface` module).
- Table `configuration` in the database, which contains two columns: `key` and `value`.

### Authorization

The `authorization_manager` module contains functions for interacting with users.

Dependencies:

- MySQL database connection (using the `mysql_interface` module).
- Table `user_role` in the database, which maps usernames to roles.

### Authentication

The `authentication_manager` module provides functions for user authentication.

Dependencies:

- MySQL database connection (using the `mysql_interface` module).
- `config_manager` module for retrieving SSO configuration.
- Table `user` in the database, which contains a username column.
- Authorization module (to retrieve user roles).

### Logging

The `logger` module provides a simple logging interface which prepends log messages with a timestamp.

### Service Utility

The `service_utility` module provides functionality used by Flask services.

Dependencies:

- `authentication_manager` module for user authentication.
- `authorization_manager` module for user authorization.
