def translate_text(
    text,
    tokenizer,
    translator_model,
    source_lang,
    target_lang
):

    if not text.strip():
        return ""

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
        max_length=50
    )

    translated_text = tokenizer.batch_decode(
        translated_tokens,
        skip_special_tokens=True
    )

    return translated_text[0]