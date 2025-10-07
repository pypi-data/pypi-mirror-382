
# GLiNER.cpp: Generalist and Lightweight Named Entity Recognition for C++ with Python bindings

Forked from: https://github.com/Knowledgator/GLiNER.cpp --> see there for the original repo


GLiNER.cpp is a C++-based inference engine for running GLiNER (Generalist and Lightweight Named Entity Recognition) models. GLiNER can identify any entity type using a bidirectional transformer encoder, offering a practical alternative to traditional NER models and large language models.

## TlDr;

```bash
# clone the repo 
cd GLiNER.cpp && python -m pip install .
```

## Example 

ONNX model example

```python
import gliner_cpp
import time

cfg = gliner_cpp.Config(12, 512)
MODEL_PATH = "./models/model.onnx"
TOKENIZER_PATH = "./models/tokenizer.json"
start = time.time()
model = gliner_cpp.Model(MODEL_PATH, TOKENIZER_PATH, cfg)
end = time.time()
print(f"Loading model took: {end - start} seconds")


test = "The capital of France is Paris. I visited last in September last year."
entities = ["LOCATION", "COUNTRY", "DATE"]
start = time.time()
spans = model.inference([test], entities)
for span in spans:
    print(span)
end = time.time()
print(f"Inference took: {end - start} seconds")

```