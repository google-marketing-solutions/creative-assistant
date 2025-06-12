# How to use text-categorizer as a HTTP endpoint

`text-categorizer` can be exposed as HTTP endpoint.

1. Install `text-categorizer` with `pip install text-categorization` command.

2. Clone `text-categorization` repository and run:

```
fastapi run entrypoints/server.py
```

3. POST to `http://localhost:8000/`
(check example using [`httpie`](https://httpie.io/docs/cli) below):

```
http POST localhost:8000 \
  data[texts][]=one \
  data[texts][]=two \
  data[texts][]=ferret
```

4. Results of categorization will be shown as a JSON output.
