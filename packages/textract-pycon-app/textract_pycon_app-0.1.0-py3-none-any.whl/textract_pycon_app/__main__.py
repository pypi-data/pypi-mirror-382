import sys

import boto3  # type: ignore
from textract_pycon import get_unique_words


def main() -> None:
    bucket_name = sys.argv[1]
    document_name = sys.argv[2]

    client = boto3.client("textract")
    response = client.detect_document_text(
        Document={"S3Object": {"Bucket": bucket_name, "Name": document_name}}
    )

    print(get_unique_words(response))


if __name__ == "__main__":
    main()
