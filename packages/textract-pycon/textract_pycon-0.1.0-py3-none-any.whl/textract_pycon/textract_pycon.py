from collections.abc import Generator


def _yield_all_word_blocks(textract_response: dict) -> Generator[dict]:
    return (
        block for block in textract_response["Blocks"] if block["BlockType"] == "WORD"
    )


def get_unique_words(textract_response: dict) -> set[str]:
    """Get all unique texts from WORD blocks in a Textract API response.

    Parameters
    ----------
    textract_response : dict
        Textract API response for detecting text in a document.

    Returns
    -------
    set[str]
        unique text entries from WORD block in a Textract API response.
    """
    return {block["Text"] for block in _yield_all_word_blocks(textract_response)}
