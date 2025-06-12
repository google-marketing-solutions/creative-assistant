# How to use text-categorizer as a library

1. Install `text-categorizer` with `pip install text-categorization` command.

2. Import package modules

```
from text_categorization import categorizer, llms, vectorstore
```

3. Initialize `text_categorizer`:

```
text_categorizer = categorizer.TextCategorizer(
  llm=llm, vect_store=vector_store
)
```

* Use helpers from `text_categorization` package to initialize `vector_store`
  and `llm`:

    ```
    llm = llms.create_categorizer_llm('gemini', {'model': 'gemini-1.5-flash'})
    vector_store = vectorstore.get_vector_store()
    ```

4. (Optional) Add examples to help with the categorization:

```
examples = ['one - digit', 'dog - pet']
text_categorizer.add_examples(examples, load_to_vectorstore=True)
```

5. Perform text categorization:

```
texts = ['seven', 'six', 'cat']
result = text_categorizer.categorize(texts)
```

* Convert results of categorization to pandas dataframe.

    ```
    categorization_df = result.to_pandas()
    ```
