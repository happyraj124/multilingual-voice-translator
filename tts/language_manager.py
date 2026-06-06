# tts/language_manager.py

NLLB_TO_MMS = {

    "eng_Latn": "eng",
    "hin_Deva": "hin",
    "urd_Arab": "urd",
    "spa_Latn": "spa",
    "fra_Latn": "fra"

}


def get_mms_language(nllb_code):

    if nllb_code not in NLLB_TO_MMS:
        raise ValueError(
            f"No MMS mapping found for {nllb_code}"
        )

    return NLLB_TO_MMS[nllb_code]