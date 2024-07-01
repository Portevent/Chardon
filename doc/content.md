# Content

## Content Attributes
Content can have attributes. Some of them are mandatory, and some of them are optionnal. For instance, ContentType.TEXT have a mandatory 'text' attribute, and an optional 'class' attribute'

```python
# You can access attributes like this :

# Mandatory attributes
my_content.attributes['text']
my_content.attributes.get('text')

# Optional attributes
if 'class' in my_content.attributes:
    my_content.attributes['class']
my_content.attributes.get('class', 'no-classes')
```

You can find a list of all attributes in [content.attributes.json](content.attributes.json)