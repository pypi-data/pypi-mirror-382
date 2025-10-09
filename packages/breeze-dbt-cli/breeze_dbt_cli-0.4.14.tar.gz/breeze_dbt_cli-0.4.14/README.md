# Breeze CLI Tool Documentation

## Introduction

**Breeze** is a command-line interface (CLI) tool designed to streamline the development of dbt (Data Build Tool) projects. It automates the creation and management of dbt models, sources, semantic models, tests, and their associated YAML files. Additionally, it provides utilities to add tests to models and sources efficiently.

## Table of Contents

1. [Installation](#installation)
2. [Command Overview](#command-overview)
3. [Build Commands](#build-commands)
   - [`breeze build model`](#breeze-build-model)
   - [`breeze build yml`](#breeze-build-yml)
   - [`breeze build source`](#breeze-build-source)
   - [`breeze build semantic`](#breeze-build-semantic)
   - [`breeze build test`](#breeze-build-test)
4. [Add Commands](#add-commands)
   - [`breeze add test`](#breeze-add-test)
   - [`breeze add description`](#breeze-add-description)
5. [Templates](#templates)
   - [Template Placeholders](#template-placeholders)
   - [Example Templates](#example-templates)
6. [AI-Powered Description Generation](#ai-powered-description-generation)
   - [Configuration](#configuration)
   - [Usage](#usage)
7. [Examples](#examples)
8. [Best Practices](#best-practices)
9. [Support and Contributions](#support-and-contributions)
10.[Conclusion](#conclusion)

## Installation

Run `pip install breeze-dbt-cli` in your dbt project's virtual environment.

## Command Overview

Breeze organizes its functionality into several command groups:

- **build**: Commands to generate models, YAML files, sources, semantic models, and tests.
- **add**: Commands to add tests to models or sources.

Use `breeze --help` to display the help message and list of available commands.

## Build Commands

Commands under the `build` group help in creating models, YAML files, sources, semantic models, and tests.

### breeze build model

Generate `.sql` files with a boilerplate `SELECT` statement for each model under `models/folder_name/model_name/model_name.sql`.

#### Usage

```bash
breeze build model [OPTIONS] PATH MODEL_NAMES...
```

#### Arguments

- **PATH** *(required)*: The folder path where the models' .sql files will be created.
- **MODEL_NAMES** *(required)*: One or more model names for which to generate `.sql` files.

#### Options

- **--force, -f**: Overwrite existing `.sql` files if they exist.
- **--template, -t**: Path to a custom SQL template file.
- **--no-subfolder, -n**: If specified, the `.sql` file will be created directly in the provided path instead of a subfolder named after the model.

#### Examples

- Generate `.sql` files for `model1` and `model2` in `models/stg/model1/` and `models/stg/model2/` respectively:

```bash
breeze build model stg model1 model2
```

- Generate `.sql` files for `model1` and `model2` in `models/stg/` without creating separate subfolders for each model:

```bash
breeze build model stg model1 model2 --no-subfolder
```

- Generate `.sql` file for `model1` in `models/stg/model1/` using a custom template located in `templates/model1_template.sql` and overwrite existing file:

```bash
breeze build model stg model1 --template templates/model1_template.sql --force
```

### breeze build yml

Generate YAML files for one or more model, snapshot, or seed. The YAML file will be created in the same directory as the corresponding `.sql` file for the model.

#### Usage

```bash
breeze build yml [OPTIONS] MODEL_NAMES...
```

#### Arguments

- **MODEL_NAMES** *(required)*: One or more model name for which to generate YAML files.

#### Options

- **--force, -f**: Overwrite existing files if they exist.
- **--template, -t**: Path to a custom YAML template file.
- **--describe, -d**: Use ChatGPT to generate descriptions. See [AI-Powered Description Generation](#ai-powered-description-generation)

#### Examples

- Generate YAML files for `model1` and `model2`:

```bash
breeze build yml model1 model2
```

- Generate `.yml` file for `model1` using a custom template located in `templates/model1_template.yml` and overwrite existing file:

```bash
breeze build yml model1 --template templates/model1_template.yml --force
```

### breeze build source

Generate YAML files for one or more source. By default, the YAML file is created under `models/schema_name/source_name.yml`. However, you can specify a custom path using the `--path` flag.

#### Usage

```bash
breeze build source [OPTIONS] SCHEMA_NAME SOURCE_NAMES...
```

#### Arguments

- **SCHEMA_NAME** *(required)*: The schema name of the sources.
- **SOURCE_NAMES** *(optional)*: One or more source names for which to generate YAML files.

#### Options

- **--all, -a**: Build YAML files for all sources in the schema.
- **--force, -f**: Overwrite existing files if they exist.
- **--template, -t**: Path to a custom YAML template file.
- **--describe, -d**: Use ChatGPT to generate descriptions. See [AI-Powered Description Generation](#ai-powered-description-generation)
- **--path, -p**: Specify a custom directory where the source YAML file will be saved. If the path does not exist, it will be created.

#### Examples

- Generate source YAML files for `source1` and `source2` under `models/schema_name/`:

```bash
breeze build source my_schema source1 source2
```

- Generate source YAML file for `source1` using a custom template located in `templates/source_template.yml` and save it in `models/sources/postgres/`:

```bash
breeze build source my_schema source1 --template templates/source_template.yml --path sources/postgres
```

- Force overwrite existing YAML for all sources in the `raw` schema:

```bash
breeze build source raw --all --force
```

### breeze build semantic

Generate YAML boilerplate for the semantic model of dbt model. The YAML file will be created in the same directory as the corresponding `.sql` file for the model, or in a custom path specified with the `--path` flag.

#### Usage

```bash
breeze build semantic [OPTIONS] MODEL_NAMES...
```

#### Arguments

- **MODEL_NAMES** *(required)*: One or more dbt model names for which to generate semantic YAML files.

#### Options

- **--force, -f**: Overwrite existing files if they exist.
- **--template, -t**: Path to a custom semantic model template file.
- **--path, -p**: Specify a custom output path for the semantic YAML files.

#### Examples

- Generate semantic model YAML files for `model1` and `model2`:

```bash
breeze build semantic model1 model2
```

- Generate semantic model YAML for `model1` using a custom template and overwrite existing file:

```bash
breeze build semantic model1 --template templates/semantic_template.yml --force
```

- Save semantic YAML for `model1` in a custom directory `models/semantic/`:

```bash
breeze build semantic model1 --path models/semantic
```

### breeze build test

Generate boilerplate `.sql` files for custom dbt tests. The `.sql` file is created in the first `test-path` defined in the `dbt_project.yml`, or in a custom directory specified with the `--path` flag.

#### Usage

```bash
breeze build test [OPTIONS] TEST_NAMES...
```

#### Arguments

- **TEST_NAMES** *(required)*: One or more custom test names for which to generate SQL files.

#### Options

- **--force, -f**: Overwrite existing files if they exist.

#### Examples

- Generate generic test SQL files for `test1` and `test2`:

```bash
breeze build test test1 test2
```

## Add Commands

Commands under the `add` group assist in adding tests to models or sources.

### breeze add test

Add one or more tests to a model, seed, snapshot, or source. If columns are specified, the tests are added to those columns. If no columns are specified, the tests are added at the model, seed, snapshot, or source level.

#### Usage

```bash
breeze add test [OPTIONS] TEST_NAMES...
```

#### Arguments

- **TEST_NAMES** *(required)*: One or more test names to add (e.g., `not_null`, `unique`).

#### Options

- **--model, -m**: The model name to add the test(s) to.
- **--seed, -e**: The seed name to add the test(s) to.
- **--snapshot, -n**: The snapshot name to add the test(s) to.
- **--source, -s**: The source name to add the test(s) to.
- **--columns, -c**: Comma-separated column names to add the test(s) to.

#### Examples

- Add multiple tests to specific columns in a model:

```bash
breeze add test not_null unique --model customers --columns "customer_id, email"
```

- Add a test at the model level:

```bash
breeze add test unique --model orders
```

- Add multiple tests to specific columns in a source:

```bash
breeze add test not_null accepted_values --source status --columns status_code
```

### breeze add description

Add AI-generated descriptions to an existing YML of a model, seed, source, or snapshot. If no columns are specified, only the entity-level description is generated. If columns are specified, only the columns passed will be generated. If the flag `--all` is passed, all descriptions in the YML will be generated.

#### Usage

```bash
breeze add description [OPTIONS]
```

#### Options

- **--model, -m**: The model name to add the descriptions to.
- **--seed, -e**: The seed name to add the descriptions to.
- **--snapshot, -n**: The snapshot name to add the descriptions to.
- **--source, -s**: The source name to add the descriptions to.
- **--columns, -c**: Comma-separated column names to add the descriptions to.
- **--all, -a**: Update all descriptions for a specified entity. 

#### Examples

- Add a description to the model, but not its columns:

```bash
breeze add description --model customers
```

- Add a description to some columns of a model but not the model itself:

```bash
breeze add description --model customers --columns "customer_id, status"
```

- Add descriptions to the model and all of its columns:

```bash
breeze add description --model customers --all
```

## Templates

Breeze allows you to use custom templates for generating `.sql` and `.yml` files. You can specify a custom template using the `--template` option with the `build` commands.

### Template Placeholders

You can include the following placeholders in your templates:

- **{{ resource_tyoe }}**: Type of resource (e.g source, seed, snapshot, or model).
- **{{ model_name }}**: Name of the model.
- **{{ model_description }}**: Name of the model.
- **{{ source_name }}**: Name of the source table.
- **{{ source_description }}**: Name of the source table.
- **{{ schema_name }}**: Name of the schema.
- **{{ database }}**: Name of the database.
- **{{ columns }}**: List of columns (used in loops).

Within loops, each column has:

- **{{ column.name }}**: Column name.
- **{{ column.data_type }}**: Data type of the column.
- **{{ column.description }}**: Data type of the column.

### Example Templates

#### Model YAML Template

```yaml
version: 2

{{ resource_type }}:
  - name: {{ model_name }}
    description: {{ model_description }}
    tags: []
    columns:
    {% for column in columns %}
      - name: {{ column.name }}
        data_type: {{ column.data_type }}
        description: {{ column.description }}
        tests:
         - not_null
    {% endfor %}
```

#### Source YAML Template

```yaml
version: 2

sources:
  - name: {{ schema_name }}
    description: ''
    database: {{ database }}
    schema: {{ schema_name }}
    tables:
    - name: {{ source_name }}
      description: {{ source_description }}
      tags: []
      columns:
      {% for column in columns %}
        - name: {{ column.name }}
          data_type: {{ column.data_type }}
          description: {{ column.description }}
          tests:
            - not_null
      {% endfor %}
```

## AI-Powered Description Generation

Breeze allows you to use ChatGPT in order to generate descriptions for models, sources, seeds, snapshots, and their corresponding columns.

### Configuration

To enable AI-assisted description generation, add an `ai_token` field to your `profiles.yml` file:

```yaml
dbt_project:
  target: dev
  outputs:
    dev:
      type: type
      host: host
      user: user
      password: pwd
      port: 1234
      dbname: database
      schema: schema
      ai_token: "your_openai_api_key_here"
```

### Usage

To generate descriptions using AI, use the `--describe` or `-d` flag with the `breeze build yml`, `breeze build source` commands.

## Best Practices

- **Run `dbt compile` or `dbt build` before generating YAML files**: This ensures that the `manifest.json` is up-to-date, which Breeze uses to gather model information.
  
- **Use the `--force` flag cautiously**: Overwriting existing files can lead to loss of manual changes. Ensure you have backups or use version control.

- **Validate Generated Files**: After generating or modifying files, validate the YAML syntax and dbt configurations.

- **Enclose Columns with Spaces in Quotes**: When specifying columns with spaces in their names or spaces after commas, enclose the columns in quotes.

## Support and Contributions

If you encounter issues or have suggestions for new features, please consider contributing to the project or opening an issue on the project's repository.

## Conclusion

Breeze simplifies dbt project development by automating repetitive tasks and enforcing consistency across models and sources. By leveraging custom templates and automated test additions, you can focus on developing robust data transformations.
