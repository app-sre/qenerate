# Qenerate Changelog

## 0.6.3

Bugfixes:

* revert `allow_population_by_field_name` Pydantic model config. This was causing troubles with mypy.
*
## 0.6.2

New Features:

* Set `allow_population_by_field_name` Pydantic [model config](https://docs.pydantic.dev/1.10/usage/model_config/#options)

## 0.6.1

BUGFIX:

* properly handle inline fragments inside fragment definitions ([#80](https://github.com/app-sre/qenerate/pull/80))

## 0.6.0

New Features:

* Allow custom type mapping of GQL scalars ([#76](https://github.com/app-sre/qenerate/pull/76))

## 0.5.2

ENHANCEMENTS:

* Reduce Boilerplate ([#75](https://github.com/app-sre/qenerate/pull/75))
