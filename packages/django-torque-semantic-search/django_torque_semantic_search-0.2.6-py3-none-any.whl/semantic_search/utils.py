from luqum.parser import parser
from langchain_text_splitters import MarkdownHeaderTextSplitter

from semantic_search.transformers import (
    FilterQueryTransformer,
    WithoutNegationsTransformer,
)

headers_to_split_on = [
    ("#", "Header 1"),
]

token_splitter = MarkdownHeaderTextSplitter(headers_to_split_on, strip_headers=False)


def filter_queries(qs, keep_negations=True):
    """
    Filters a list of queries to keep only phrases, e.g. "term", and
    negations, and some operators,
    e.g. `title:water water in india -"is a resource" -goats "test"`
    becomes `-"is a resource" -goats "test"`.
    Or just removes negations.
    """

    Transformer = (
        FilterQueryTransformer if keep_negations else WithoutNegationsTransformer
    )

    return [str(Transformer().visit(parser.parse(q))).strip() for q in qs]


def dict_to_markdown(data, level=1):
    markdown = ""
    for key, value in data.items():
        if value:
            markdown += f"{'#' * level} {key}\n\n"
            if isinstance(value, dict):
                markdown += dict_to_markdown(value, level + 1)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        markdown += dict_to_markdown(item, level + 1)
                    else:
                        markdown += f"* {item}\n"
            else:
                markdown += f"{value}\n"
            markdown += "\n"
    return markdown


async def batch_queryset(qs, batch_size):
    batch = []
    async for obj in qs:
        batch.append(obj)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def build_semantic_summaries(document_dict):
    text = dict_to_markdown(document_dict)
    summaries = [
        doc.page_content
        for doc in token_splitter.split_text(text)
        if doc.page_content.strip()
    ]
    return summaries
