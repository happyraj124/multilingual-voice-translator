from datetime import datetime


class HistoryManager:

    def __init__(self):

        self.history = []

    def add_record(
        self,
        source_language,
        target_language,
        source_text,
        translated_text
    ):

        self.history.append(
            {
                "timestamp":
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),

                "source_language":
                    source_language,

                "target_language":
                    target_language,

                "source_text":
                    source_text,

                "translated_text":
                    translated_text
            }
        )

    def get_history(self):

        return self.history

    def clear_history(self):

        self.history.clear()