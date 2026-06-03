def translate_text(
    text,
    tokenizer,
    translator_model,
    source_lang="hin_Deva",
    target_lang="eng_Latn"
):

    inputs = tokenizer(
        text,
        return_tensors="pt",
        src_lang=source_lang
    )

    translated_tokens = translator_model.generate(
        **inputs,
        forced_bos_token_id=
        tokenizer.convert_tokens_to_ids(
            target_lang
        )
    )

    translated_text = tokenizer.batch_decode(
        translated_tokens,
        skip_special_tokens=True
    )

    return translated_text[0]