def translate_text(
    text,
    tokenizer,
    translator_model,
    source_lang="hin_Deva",
    target_lang="eng_Latn"
):
    # 1. Explicitly set the source language on the tokenizer
    tokenizer.src_lang = source_lang

    inputs = tokenizer(
        text,
        return_tensors="pt"
    )

    translated_tokens = translator_model.generate(
        **inputs,
        forced_bos_token_id=
        tokenizer.convert_tokens_to_ids(
            target_lang
        ),
        max_length=50  # 2. Prevents the model from generating infinitely long, looping outputs
    )

    translated_text = tokenizer.batch_decode(
        translated_tokens,
        skip_special_tokens=True
    )

    return translated_text[0]