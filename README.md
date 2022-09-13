**Disclaimer:** :warning: This is in alpha stage. Breaking changes could occur any time.

# qenerate

`qenerate` is a code generator for GraphQL Query Data Classes. 
`qenerate` is not a GQL client. A GQL client normally returns data in the form
of nested untyped dictionaries. `qenerate` solely focuses on generating code
for transforming those untyped dictionaries into concrete types.

## Usage

### Introspection

In a first step we must obtain your GQL schema in the form of an introspection query:

```sh
qenerate introspection http://my-gql-instance:4000/graphql > introspection.json
```

The `introspection.json` is used in a next step to map concrete types to your queries.

### Code Generation

```sh
qenerate code -i introspection.json dir/to/gql/files
```

An `introspection.json` and a directory holding `*.gql` files are given.
`qenerate` then generates data classes for every `*.gql` file it encounters
while traversing the given directory.

`qenerate` expects that a `.gql` file contains exactly one `query` operation.

## Plugins

`qenerate` follows a plugin based approach. I.e., multiple code generators are supported.
Choosing a code generator is done inside the query file, e.g., the following example will
generate data classes using the `pydantic_v1` plugin:

```graphql
# qenerate: plugin=pydantic_v1
query {
    ...
}
```

By choosing a plugin based approach, `qenerate` can extent its feature set creating new plugins
while at the same time keeping old plugins stable and fully backwards compatible.

Currently available plugins are:

- [pydantic_v1](docs/plugins/pydantic_v1.md) for generating Pydantic data classes

## Feature Flags

`qenerate` leverages feature flags to configure the behavior of the generator. Feature flags are passed to
the generator via comments in your .gql definition file.

### Plugin

```graphql
# qenerate: plugin=<plugin-id>
```

This feature flag tells `qenerate` which plugin it should use to generate the code for the given definition.

### Naming Collision Strategy

```graphql
# qenerate: naming_collision_strategy=[PARENT_CONTEXT | ENUMERATE]
```

This feature flag tells `qenerate` how to deal with naming collisions in classes.
In GraphQL it is easy to query the same object in a nested fashion, which results
in re-definitions of the type. We call this naming collision. A naming collision
strategy defines how to adjust recurring names to make them unique.

**PARENT_CONTEXT**

This is the default strategy if nothing else is specified. It uses the name of the
parent node in the query as a prefix.

**ENUMERATE**

This strategy adds the number of occurrences of this name as a suffix.

## Development

### Build and Dependency Management

`qenerate` uses [poetry](https://python-poetry.org/docs/) as build and dependency management system.

### Formatting

`qenerate` uses [black](https://github.com/psf/black) for formatting.

### Generating setup.py

```sh
pip install poetry2setup
poetry2setup .
```