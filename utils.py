
def compose_stream(dict_generator, first_message=None):
    """
    Compose a generator object by extracting the `text` field from the input
    generator values.
    """
    for item in dict_generator:
        yield item["text"]