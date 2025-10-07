#include <emscripten/bind.h>
#include <emscripten/val.h>

#include <memory>
#include <string>
#include <vector>

#include "GLiNER/gliner_config.hpp"
#include "GLiNER/gliner_structs.hpp"
#include "GLiNER/model.hpp"

namespace em = emscripten;

namespace
{
    std::vector<std::vector<gliner::Span>> run_inference(
        gliner::Model &model,
        const std::vector<std::string> &texts,
        const std::vector<std::string> &entities,
        bool flat_ner,
        float threshold,
        bool multi_label
    )
    {
        return model.inference(texts, entities, flat_ner, threshold, multi_label);
    }

    gliner::Config make_config(int max_width, int max_length, gliner::ModelType type)
    {
        return gliner::Config{max_width, max_length, type};
    }
}

EMSCRIPTEN_BINDINGS(gliner_bindings)
{
    em::enum_<gliner::ModelType>("ModelType")
        .value("TOKEN_LEVEL", gliner::ModelType::TOKEN_LEVEL)
        .value("SPAN_LEVEL", gliner::ModelType::SPAN_LEVEL);

    em::value_object<gliner::Config>("Config")
        .field("max_width", &gliner::Config::maxWidth)
        .field("max_length", &gliner::Config::maxLength)
        .field("model_type", &gliner::Config::modelType);

    em::function("createConfig", &make_config, em::allow_raw_pointers());

    em::value_object<gliner::Span>("Span")
        .field("start_idx", &gliner::Span::startIdx)
        .field("end_idx", &gliner::Span::endIdx)
        .field("text", &gliner::Span::text)
        .field("class_label", &gliner::Span::classLabel)
        .field("prob", &gliner::Span::prob);

    em::register_vector<std::string>("StringList");
    em::register_vector<gliner::Span>("SpanList");
    em::register_vector<std::vector<gliner::Span>>("SpanBatch");

    em::class_<gliner::Model>("Model")
        .constructor<const std::string &, const std::string &, const gliner::Config &>()
        .constructor<const std::string &, const std::string &, const gliner::Config &, int>()
        .function("inference", &run_inference, em::allow_raw_pointers());
}
