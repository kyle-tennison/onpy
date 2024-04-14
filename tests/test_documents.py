"""Tests document management"""

from pyshape import Client

import uuid

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
