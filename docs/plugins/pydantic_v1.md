# Pydantic V1 Plugin

This plugin generates simple pydantic data classes for your queries.
Pydantic is capable of mapping nested dictionaries to nested types.
I.e., no custom mapping functions are required.

## Examples

### Hero

**hero.gql:**
```gql
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
