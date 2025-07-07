import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.tools import Tool

from .backend import Bugzilla, CheckKcs, DocumentParse, Upstream

load_dotenv()
BUGZILLA_URL = os.getenv("BUGZILLA_URL")
BUGZILLA_API_KEY = os.getenv("BUGZILLA_API_KEY")
DOCUMENTATION = os.getenv("DOCUMENTATION", "data/ceph_documentation.txt")


document_parse = DocumentParse(
    DOCUMENTATION,
    folder_path=Path(DOCUMENTATION).parent,
    index_name="ceph_documentation_index",
)
document_parse.load_faiss_index()

kcs = CheckKcs()
bugzilla = Bugzilla(BUGZILLA_URL, BUGZILLA_API_KEY)
upstream = Upstream()


# Tool Functions
def search_document(query):
    result = document_parse.answer_query(query)
    return result


def check_kcs(query):
    result = kcs.get_results_from_kcs(query)
    return result


def search_bugzilla(query):
    result = bugzilla.search_or_get_bug(query)
    return result


def search_support_pages(label):
    result = upstream.fetch_ceph_issues(label)
    return result


# Use these tools except search_bugzilla
tools = [
    Tool(
        name="Check the documentation",
        func=search_document,
        description="Searches the document for a given query and returns the best possible result",
        return_direct=True,  # Ensures the response is directly sent to the user
    ),
    Tool(
        name="Check support pages",
        func=check_kcs,
        description="Searches the support pages and returns the best possible results ",
        return_direct=True,  # Ensures the response is directly sent to the user
    ),
    Tool(
        name="Check bugzilla records",
        func=search_bugzilla,
        description="Search bugzilla for a bug or fetch details of a specific bug by ID, summary or keywords",
        return_direct=True,  # Ensures the response is directly sent to the user
    ),
    Tool(
        name="Check upstream issues",
        func=search_support_pages,
        description="Search issues in upstream for a given label",
        return_direct=True,  # Ensures the response is directly sent to the user
    ),
]
