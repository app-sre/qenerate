# Pydantic V1 Plugin

This plugin generates simple [pydantic](https://docs.pydantic.dev/) data classes for your queries and fragments.
Pydantic is capable of mapping nested dictionaries to nested types.
I.e., no data mapping functions need to be generated.

This plugin expects exactly one gql definition per `.gql` file.
Supported definitions are:

- `fragment`
- `query`
- `mutation` (only response data structures - input data structures are still a [TODO](https://github.com/app-sre/qenerate/issues/71))

## Opinionated Custom Scalars

The `pydantic_v1` plugin has an opinionated approach towards some very common custom scalars
defined in https://the-guild.dev/graphql/scalars/docs

Currently it maps the following: 

- `JSON` maps to `pydantic.Json`
- `DateTime` maps to `datetime.datetime` 

Any other custom scalar will be mapped to `str`.

## Examples

### Query with inline fragments

**hero.gql:**
```graphql
# qenerate: plugin=pydantic_v1
query HeroForEpisode {
  hero {
    name
    ... on Droid {
      primaryFunction
    }
    ... on Human {
      height
    }
  }
}
```

**hero.py:**
```python
class Hero(BaseModel):
  name: str = Field(..., alias="name")


class Droid(Hero):  # Note that Droid implements Hero
  primary_function: str = Field(..., alias="primaryFunction")


class Human(Hero):  # Note that Human implements Hero
  height: str = Field(..., alias="height")


class HeroForEpisodeData(BaseModel):
  hero: Optional[list[Union[Droid, Human, Hero]]] = Field(..., alias="hero")

  class Config:
    # This is set so pydantic can properly match the data to union, i.e., properly infer the correct type
    # https://pydantic-docs.helpmanual.io/usage/model_config/#smart-union
    # https://stackoverflow.com/a/69705356/4478420
    smart_union = True
    extra = Extra.forbid
```

### Query with Fragments

**hero.gql:**
```graphql
# qenerate: plugin=pydantic_v1
query HeroForEpisode {
  hero {
    ... HeroName
    ... HeroAge
    number
  }
}
```

**hero_name_fragment.gql:**
```graphql
# qenerate: plugin=pydantic_v1
fragment HeroName on Hero {
  name
}
```

**hero_age_fragment.gql:**
```graphql
# qenerate: plugin=pydantic_v1
fragment HeroAge on Hero {
  age
}
```

**hero_name_fragment.py:**
```python
class HeroName(BaseModel):
    name: str = Field(..., alias="name")
```

**hero_age_fragment.py:**
```python
class HeroAge(BaseModel):
    age: int = Field(..., alias="age")
```

**hero.py:**
```python
from hero_age_fragment import HeroAge
from hero_name_fragment import HeroName


# Note, that Hero implements the fragments
class Hero(HeroAge, HeroName):
  number: int = Field(..., alias="number")


class HeroForEpisodeData(BaseModel):
  hero: Optional[list[Hero]] = Field(..., alias="hero")
```

Note, that the python import path is relative to the directory
in which `qenerate` was executed.
