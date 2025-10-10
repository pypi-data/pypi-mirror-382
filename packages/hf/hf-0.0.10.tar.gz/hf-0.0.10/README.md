# hf

Simple Mapping interface to HuggingFace

This package offers such a `Mapping`-based façade to all four types of Hugging Face resources—datasets, models, spaces, and papers—allowing you to browse, query, and access them as if they were simple Python dictionaries. The goal isn't to replace the original API, but to provide a thin, ergonomic layer for the most common operations — so you can spend less time remembering syntax, and more time working with data.

To install:	```pip install hf```

You'll also need a Hugginface token. See [more about this here](https://huggingface.co/docs/huggingface_hub/en/quick-start).


## Motivation

The Python packages [`datasets`](https://github.com/huggingface/datasets) and [`huggingface_hub`](https://github.com/huggingface/huggingface_hub) provide a remarkably clean, well-documented, and comprehensive API for accessing datasets, models, spaces, and papers hosted on [Hugging Face](https://huggingface.co).  
Yet, as elegant as these APIs are, they remain *their own language*. Every library—no matter how intuitive—inevitably carries its own conventions, abstractions, and domain-specific semantics. When working with one or two APIs, this diversity is harmless, even stimulating. But when juggling dozens or hundreds of them, the cognitive overhead accumulates.

Despite their differences, most APIs share a small set of universal primitives — *retrieve something by key, list what’s available, check existence, store, update, delete*.  
In Python, these operations are embodied by the `Mapping` interface, the conceptual model behind dictionaries. It’s a minimal, ubiquitous, and instantly recognizable abstraction.  

This package offers such a `Mapping`-based façade to Hugging Face datasets and models, allowing you to browse, query, and access them as if they were simple Python dictionaries. The goal isn’t to replace the original API, but to provide a thin, ergonomic layer for the most common operations — so you can spend less time remembering syntax, and more time working with data.

## Examples

This package provides four ready-to-use singleton instances, each offering a dictionary-like interface to different types of HuggingFace resources:

```python
from hf import datasets, models, spaces, papers
```

### Working with Datasets

The `datasets` singleton provides a `Mapping` (i.e. read-only-dictionary-like) interface to HuggingFace datasets:

#### List Local Datasets

As with dictionaries, `datasets` is an iterable. An iterable of keys. 
The keys are repository ids for those datasets you've downloaded. 
See what datasets you already have cached locally like this:

```python
list(datasets)  # Lists locally cached datasets
# ['stingning/ultrachat', 'allenai/WildChat-1M', 'google-research-datasets/go_emotions']
```

#### Access Local Datasets

The values of `hf.datasets` are the `DatasetDict` 
(from Huggingface's `datasets` package) instances that give you access to the dataset.
If you already have the dataset downloaded locally, it will load it from there, 
if not it will download it, then give it to you (and it will be cached locally 
for the next time you access it). 

```python
data = datasets['stingning/ultrachat']  # Loads the dataset
print(data)  # Shows dataset information and structure
```

#### Search for Remote Datasets

`hf.datasets` also offers a search functionality, so you can search "remote" 
repositories:

```python
# Search for music-related datasets
search_results = datasets.search('music', gated=False)
print(f"search_results is a {type(search_results).__name__}")  # It's a generator

# Get the first result (it will be a `DatasetInfo` instance contain information on the dataset)
result = next(search_results)
print(f"Dataset ID: {result.id}")
print(f"Description: {result.description[:80]}...")

# Download and use it directly
data = datasets[result]  # You can pass the DatasetInfo object directly
```

Note that the `gated=False` was to make sure you get models that you have access to. 
For more search options, see the [HuggingFace Hub documentation](https://huggingface.co/docs/huggingface_hub/package_reference/hf_api#huggingface_hub.HfApi.list_datasets).

#### A useful recipe: Get a table of result infos

You can use this to get a dataframe of the first/next `n` results of the results iterable:

```py
def table_of_results(results, n=10):
    import itertools, operator, pandas as pd

    results_table = pd.DataFrame(  # make a table with
        map(
            operator.attrgetter('__dict__'),  # the attributes dicts
            itertools.islice(results, n),  # ... of the first 10 search results
        )
    )
    return results_table
```

Example:

```py
results_table = table_of_results(search_results)
results_table
```

                              id            author                                       sha ...
    0   Genius-Society/hoyoMusic    Genius-Society  4f7e5120c0e8e26213d4bb3b52bcce76e69dfce4 ...
    1      Genius-Society/emo163    Genius-Society  6b8c3526b66940ddaedf15602d01083d24eb370c ...
    2  ccmusic-database/acapella  ccmusic-database  4cb8a4d4cb58cc55f30cb8c7a180fee1b5576dc5 ...
    3    ccmusic-database/pianos  ccmusic-database  db2b3f74c4c989b4fbda4b309e6bc925bfd8f5d1 ...
    ...


### Working with Models

The `models` singleton provides the same dictionary-like interface for models:

```python
from hf import models
```

#### Search for Models

Find models by keywords:

```python
model_search_results = models.search('embeddings', gated=False)
model_result = next(model_search_results)
print(f"Model: {model_result.id}")
```

#### Download Models

Get the local path to a model (downloads if not cached):

```python
model_path = models[model_result]
print(f"Model downloaded to: {model_path}")
```

#### List Local Models

See what models you have cached:

```python
list(models)  # Lists all locally cached models
```

### Working with Spaces

The `spaces` singleton provides access to HuggingFace Spaces (interactive ML demos and applications):

```python
from hf import spaces
```

#### Search for Spaces

Find interesting Spaces by keywords:

```python
space_search_results = spaces.search('gradio', limit=5)
space_result = next(space_search_results)
print(f"Space: {space_result.id}")
```

#### Access Space Information

Get detailed information about a Space:

```python
space_info = spaces[space_result]
print(f"Space info: {space_info}")
```

#### List Local Spaces

See what spaces you have cached locally:

```python
list(spaces)  # Lists all locally cached spaces
```

### Working with Papers

The `papers` singleton provides access to research papers hosted on HuggingFace:

```python
from hf import papers
```

#### Search for Papers

Find research papers by topic:

```python
paper_search_results = papers.search('transformer', limit=5)
paper_result = next(paper_search_results)
print(f"Paper: {paper_result.id}")
```

#### Access Paper Information

Get detailed information about a paper:

```python
paper_info = papers[paper_result]
print(f"Paper title: {paper_info.title}")
print(f"Abstract: {paper_info.summary[:100]}...")
```

Note: Papers are metadata objects only—they contain information about research papers but don't have downloadable files like datasets or models.

### Getting Repository Sizes

You can check the size of any repository before downloading using the `get_size` function. The `repo_type` parameter is required to avoid ambiguity when repositories exist as multiple types:

```python
from hf import get_size

# Get size of a dataset (specify repo_type explicitly)
dataset_size = get_size('ccmusic-database/music_genre', repo_type='dataset')
print(f"Dataset size: {dataset_size:.2f} GiB")

# Get size of a model 
model_size = get_size('ccmusic-database/music_genre', repo_type='model')
print(f"Model size: {model_size:.2f} GiB")

# Using RepoType enum for type safety
from hf.base import RepoType
size_with_enum = get_size('some-repo', repo_type=RepoType.DATASET)

# Get size in different units (e.g., bytes)
size_in_bytes = get_size('some-repo', repo_type='dataset', unit_bytes=1)
```

**Pro tip**: Use the singleton instances for automatic repo_type handling:
```python
# These automatically know their repo_type
dataset_size = datasets.get_size('ccmusic-database/music_genre')
model_size = models.get_size('ccmusic-database/music_genre')
```

### Unified Interface

The beauty of this approach is that whether you're working with datasets, models, spaces, or papers, the interface remains familiar and consistent—just like working with Python dictionaries. All four singleton instances support the same core operations:

- **Dictionary-style access**: `resource = datasets[key]`, `model_path = models[key]`
- **Local listing**: `list(datasets)`, `list(models)` 
- **Remote searching**: `datasets.search(query)`, `models.search(query)`
- **Existence checking**: `key in datasets`, `key in models`

This unified interface means you can switch between different types of HuggingFace resources without learning new APIs—it's all just dictionaries! And since they're singleton instances, they're always ready to use without any setup.


