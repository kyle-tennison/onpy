"""Tests document management"""

from onpy import Client

import pytest
import uuid

from onpy.util.exceptions import PyshapeParameterError

client = Client()


def test_lifecycle():
    """Tests document creation, retrieval, and deletion"""

    document_name = f"test_document_{uuid.uuid4()}"

    document = client.create_document(document_name)

    doc_copy1 = client.get_document(name=document_name)
    assert doc_copy1 == document

    doc_copy2 = client.get_document(id=document.id)
    assert doc_copy2 == document

    new_document = client.create_document(document_name + "_modified")
    assert new_document != document

    new_document.delete()
    document.delete()


def test_exceptions():
    """Tests exertions relating to documents"""

    with pytest.raises(PyshapeParameterError) as _:
        client.get_document(id="not a id")

    with pytest.raises(PyshapeParameterError) as _:
        client.get_document()

    with pytest.raises(PyshapeParameterError) as _:
        client.get_document(id="123", name="123")


def test_elements():
    """Tests element fetching"""

    document = client.create_document("test_documents::test_elements")

    try:
        main_ps = document.get_partstudio(name="Part Studio 1")

        assert main_ps == document.get_partstudio(id=main_ps.id)
        assert main_ps in document.elements
    finally:
        document.delete()
