# DuckDB Kernel for Jupyter

This is a simple DuckDB wrapper kernel which accepts SQL as input, executes it
using a previously loaded DuckDB instance and formats the output as a table.
There are some magic commands that make teaching easier with this kernel.

## Table of Contents

- [Setup](#setup)
    - [Using pip](#using-pip)
    - [Using Docker](#using-docker)
- [Usage](#usage)
    - [A Note on Magic Commands](#a-note-on-magic-commands)
    - [Load a Database](#load-a-database)
    - [Schema Diagrams](#schema-diagrams)
    - [Number of Rows](#number-of-rows)
    - [Ship Tests With Your Notebook](#ship-tests-with-your-notebooks)
    - [Relational Algebra](#relational-algebra)
    - [Domain Calculus](#domain-calculus)

## Setup

### Using pip

Run `pip` to install the corresponding package from
[pypi](https://pypi.org/project/jupyter-duckdb/)
**after** Jupyter is already installed.

```bash
pip install jupyter-duckdb
```

Register the kernel.

```bash
jupyter kernelspec install <path to the site-packages directory>/duckdb_kernel
```

Now start Jupyter the usual way and the kernel should be available.

If DuckDB cannot be installed on your system, you can use SQLite as a backend
instead. To do this, set the environment variable `SQLITE` when running pip:

```bash
SQLITE=1 pip install jupyter-duckdb
```

### Using Docker

Execute the following command to pull and run a prepared image.

```bash
docker run -p 8888:8888 troebs/jupyter-duckdb
```

There is also a second image. It contains an additional instance of PostgreSQL:

```bash
docker run -p 8888:8888 troebs/jupyter-duckdb:postgresql
```

This image can also be used with JupyterHub and the
[DockerSpawner / SwarmSpawner](https://github.com/jupyterhub/dockerspawner)
and probably with the
[kubespawner](https://github.com/jupyterhub/kubespawner). You can also build
your own image using the [Dockerfile](Dockerfile) in the repository.

## Usage

A detailed example can be found [in the repository](examples/). The rest of this
section describes the magic commands.

### A Note on Magic Commands

Many Jupyter kernels make a difference between magic commands for a single line
starting with one percent sign and others for a whole cell starting with two
percent signs. The upcoming magic commands always apply to a whole cell.
Therefore, it does not matter whether you use a single or two percent signs.
However, the magic commands must always be used at the beginning of a cell.

It is also possible to use more than one magic command per cell.

### Load a Database

To load the database two magic commands are available.

`CREATE` creates a new database and therefore overwrites files with the same
name without prompting. Using the optional parameter `OF` you can either provide
another DuckDB file or a file with SQL statements. In the first case the
included tables will be copied to the new database, while in the second case the
SQL statements are just executed. We find this feature very useful to work in a
temporary copy of the data and therefore be able to restart at any time. The
optional parameter `NAME` may be used to name a connection and reference it
later by using the magic command `USE`.

```
%CREATE data.duckdb OF my_statements.sql
```

`LOAD` on the other hand loads an existing database and returns an error if it
does not exist. (That is why `OF` cannot be used with `LOAD`! `NAME` on the
other hand is available also with this magic command.)

```
%LOAD data.duckdb
```

Multiple databases can be open at any time. If a new database with the same
name is created or loaded, the current one is closed first and saved to disk
if necessary.

Please note that `:memory:` is also a valid file path for DuckDB. The data is
then stored exclusively in the main memory. In combination with `CREATE`
and `OF` this makes it possible to work on a temporary copy in memory.

Although the name suggests otherwise, the kernel can also be used with other
databases:
- **SQLite** is automatically used as a fallback if the DuckDB dependency is
  missing.
- To connect to a **PostgreSQL** instance, you need to specify a database URI
  starting with `(postgresql|postgres|pgsql|psql|pg)://`.

### Schema Diagrams

The magic command `SCHEMA` can be used to create a simple schema diagram of the
loaded database, showing all created tables, their columns and data types, but
without any views. Primary keys are printed in bold and unique keys are
underlined. Foreign keys are also highlighted and the dependencies between the
tables are shown by arrows.

The optional flag `TD` can be set to force a vertical layout. This
representation requires more space, but can improve readability.

```
%SCHEMA TD
```

The optional argument `ONLY`, followed by one or more table names separated by a
comma, can be used to display only the named tables and all those connected with
a foreign key.

Graphviz (`dot` in PATH) is required to render schema diagrams.

### Number of Rows

By default, only 20 rows are shown. All further lines are replaced by three
dots. When hovering over the three dots using the cursor, the number of omitted
lines is displayed. Of course, the number of lines displayed can be changed.

The magic command `ALL_ROWS` and its short form `ALL` can be used to display *
*all** rows of the query in the same cell. **Caution**: With large result sets
this can lead to a frozen Jupyter instance.

```sql
%ALL_ROWS
SELECT *
FROM foo
-- all rows
```

The magic command `QUERY_MAX_ROWS` followed by an integer can be used to change
the number of displayed rows for the current cell.

```sql
%QUERY_MAX_ROWS 50
SELECT *
FROM foo
-- 50 rows
```

The magic command `MAX_ROWS` followed by an integer can be used to change the
number of displayed rows for all future queries including the current cell.

```sql
%MAX_ROWS 30
SELECT *
FROM foo
-- 30 rows
```

```sql
SELECT *
FROM bar
-- 30 rows
```

### Ship Tests With Your Notebooks

Simple tests can be loaded from json files with the help of magic command
`LOAD_TESTS`. These tests are stored as a JSON file. Each test is assigned a
unique name, a result set and whether the test should check the order of the
result. A very simple test file looks like the following JSON object:

```json
{
  "task1": {
    "ordered": false,
    "equals": [
      [
        1,
        "Name 1"
      ],
      [
        2,
        "Name 2"
      ]
    ]
  }
}
```

To bind a test to a cell, use the magic command `TEST` in combination with a
name. After the cell is executed, the result is evaluated and then displayed
below the query result.

```sql
%TEST task1
SELECT 2, 'Name 2'
UNION
SELECT 1, 'Name 1'
```

By default, failed tests will display an explanation, but the notebook will
continue to run. Set the `DUCKDB_TESTS_RAISE_EXCEPTION` environment variable to
`true` to raise an exception when a test fails. This can be useful for automated
testing in CI environments.

Disclaimer: The integrated testing is work-in-progress and thus subject to
potentially incompatible changes and enhancements.

### Relational Algebra

An interpreter for relational algebra queries is integrated in this kernel. The
magic command `RA` activates the relational algebra mode for a single cell:

```
%RA
π [a, b] (σ [c = 1] (R))
```

The supported operations are:

- Projection `π`
- Selection `σ`
- Rename `β`
- Union `∪`
- Intersection `∩`
- Difference `\`
- Natural Join `⋈`
- Cross Product `×`
- Division `÷`

The optional flag `ANALYZE` can be used to add an execution diagram to the
output.

The Dockerfile also installs the Jupyter Lab plugin
[jupyter-ra-extension](https://pypi.org/project/jupyter-ra-extension/). It adds
the symbols mentioned above and some other supported symbols to the toolbar for
insertion on click.

### Domain Calculus

An interpreter for domain calculus queries is integrated in this kernel. The
magic command `DC` activates the domain calculus mode for a single cell:

```
%DC
{ a, b | R(a, b, c) ∧ c = 1 }
```

### Automated Parser Selection

`%ALL_RA` or `%ALL_DC` enables the corresponding parser for all subsequently
executed cells.

If the magic command `%AUTO_PARSER` is added to a cell, a parser is
automatically selected. If `%GUESS_PARSER` is executed, the parser is
automatically selected for all subsequent cells.

