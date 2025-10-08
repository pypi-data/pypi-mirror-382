from vllm import LLM, SamplingParams
from vllm.sampling_params import StructuredOutputsParams


def main():
    output_schema = {
        "type": "object",
        "properties": {"sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]}},
        "required": ["sentiment"],
    }
    pipe = LLM(model="Qwen/Qwen2.5-0.5B-Instruct", max_model_len=1024)

    tokenizer = pipe.get_tokenizer()

    prompt = tokenizer.apply_chat_template(
        [{"role": "user", "content": "Is this text positive or negative? Text: I love this movie!"}],
        tokenize=False,
        add_generation_template=True,
    )

    structured_outputs = StructuredOutputsParams(json=output_schema, whitespace_pattern=r" ?")
    sampling_params = SamplingParams(structured_outputs=structured_outputs)
    responses = pipe.generate(prompt, sampling_params=sampling_params)
    print(bytes(responses[0].outputs[0].text.encode("utf-8")))
    # b'{\n\n\n  "sentiment":\n\n   "positive"\n}'


if __name__ == "__main__":
    main()
