import tiktoken
import constants


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


if __name__ == "__main__":
    print(num_tokens_from_string("Hello world, let's test tiktoken.", constants.MODEL))
