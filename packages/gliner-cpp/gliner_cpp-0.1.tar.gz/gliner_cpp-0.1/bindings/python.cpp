#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "GLiNER/model.hpp"
#include "GLiNER/gliner_structs.hpp"
#include "GLiNER/gliner_config.hpp"

namespace py = pybind11;

namespace
{
    py::dict span_to_dict(const gliner::Span &span)
    {
        py::dict span_dict;
        span_dict["start_idx"] = span.startIdx;
        span_dict["end_idx"] = span.endIdx;
        span_dict["text"] = span.text;
        span_dict["class_label"] = span.classLabel;
        span_dict["prob"] = span.prob;
        return span_dict;
    }
}

PYBIND11_MODULE(gliner_cpp, m)
{
    m.doc() = "Pybind11 bindings exposing the GLiNER C++ inference API.";

    py::enum_<gliner::ModelType>(m, "ModelType")
        .value("TOKEN_LEVEL", gliner::ModelType::TOKEN_LEVEL)
        .value("SPAN_LEVEL", gliner::ModelType::SPAN_LEVEL)
        .export_values();

    py::class_<gliner::Config>(m, "Config", "Configuration parameters controlling GLiNER inference.")
        .def(py::init([](int max_width, int max_length, gliner::ModelType model_type)
                      { return gliner::Config{max_width, max_length, model_type}; }),
             py::arg("max_width"), py::arg("max_length"), py::arg("model_type") = gliner::ModelType::SPAN_LEVEL,
             "Create a configuration object for GLiNER models.")
        .def_readwrite("max_width", &gliner::Config::maxWidth)
        .def_readwrite("max_length", &gliner::Config::maxLength)
        .def_readwrite("model_type", &gliner::Config::modelType);

    py::class_<gliner::Model>(m, "Model", R"doc(High-level wrapper around the GLiNER ONNX inference engine.)doc")
        .def(py::init<const std::string &, const std::string &, const gliner::Config &>(),
             py::arg("model_path"), py::arg("tokenizer_path"), py::arg("config"),
             "Instantiate a GLiNER model for CPU or auto-selected execution.")
        .def(py::init<const std::string &, const std::string &, const gliner::Config &, int>(),
             py::arg("model_path"), py::arg("tokenizer_path"), py::arg("config"), py::arg("device_id"),
             "Instantiate a GLiNER model on an explicit device.")
        .def("inference", [](gliner::Model &self, const std::vector<std::string> &texts, const std::vector<std::string> &entities, bool flat_ner, float threshold, bool multi_label)
             {
                 py::gil_scoped_release release;
                 auto inference_result = self.inference(texts, entities, flat_ner, threshold, multi_label);
                 py::gil_scoped_acquire acquire;

                 py::list batch_results;
                 for (const auto &text_spans : inference_result) {
                     py::list spans_for_text;
                     for (const auto &span : text_spans) {
                         spans_for_text.append(span_to_dict(span));
                     }
                     batch_results.append(spans_for_text);
                 }
                 return batch_results; }, py::arg("texts"), py::arg("entities"), py::arg("flat_ner") = true, py::arg("threshold") = 0.5f, py::arg("multi_label") = false, "Run span prediction for a batch of texts.");
}
