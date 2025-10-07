import gliner_cpp

MODEL = "gliner_small-v2.1"
MODEL_PATH = f"./models/{MODEL}/model.onnx"
TOKENIZER_PATH = f"./models/{MODEL}/tokenizer.json"
cfg = gliner_cpp.Config(12, 512)
model = gliner_cpp.Model(MODEL_PATH, TOKENIZER_PATH, cfg)
print("Imported GLiNER C++ library successfully")
test = "The capital of France is Paris. I visited last in September last year."
entities = ["LOCATION", "COUNTRY", "DATE"]
spans = model.inference([test], entities)

for span in spans:
    print(span)
