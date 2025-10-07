import gliner_cpp
import time

cfg = gliner_cpp.Config(12, 512)
MODEL = "gliner_small-v2.1"
MODEL_PATH = f"./models/{MODEL}/model.onnx"
TOKENIZER_PATH = f"./models/{MODEL}/tokenizer.json"
start = time.time()
model = gliner_cpp.Model(MODEL_PATH, TOKENIZER_PATH, cfg)
end = time.time()
print(f"Loading model took: {end - start} seconds")


test = "The capital of France is Paris. I visited last in September last year."
entities = ["LOCATION", "COUNTRY", "DATE"]
start = time.time()
N = 100
for _ in range(N):
    spans = model.inference([test], entities)
end = time.time()
print(f"Inference took: {end - start} seconds for {N} iterations")
print(f"Average inference time per iteration: {(end - start) / N} seconds")
for span in spans:
    print(span)
