# Pydantic V1 Plugin

This plugin generates simple pydantic data classes for your queries.
Pydantic is capable of mapping nested dictionaries to nested types.
I.e., no custom mapping functions are required.

This plugin expects exactly one `query` operation or fragment definition
per `.gql` file.

## Examples

### Hero

**fragments.gql:**
```graphql
# qenerate: plugin=pydantic_v1
fragment Hobby on HeroHobby {
  name
  interval
}
```

**hero.gql:**
```graphql
# qenerate: plugin=pydantic_v1
query HeroForEpisode {
  hero {
    name
    heroHobby {
      ... Hobby
    }
    ... on Droid {
      primaryFunction
    }
    ... on Human {
      height
    }
  }
}
```

**fragments.py:**
```python
class Hobby(BaseModel):
  name: str = Field(..., alias="name")
  interval: str = Field(..., alias="interval")
```

**hero.py:**
```python
from fragments import Hobby


class Hero(BaseModel):
  name: str = Field(..., alias="name")
  hero_hobby: Hobby = Field(..., alias="heroHobby")


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

## Missing Features / TODOs

- support for nested fragments

```graphql
fragment Identity on Identity_v1 {
  key
}

fragment Jumphost on Jumphost_v1 {
  host
  identity {
    ... Identity
  }
}
```
Currently, a fragment cannot use another fragment within its definition

- support enums
