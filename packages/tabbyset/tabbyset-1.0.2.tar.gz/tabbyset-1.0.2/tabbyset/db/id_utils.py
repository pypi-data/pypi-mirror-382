from uuid import uuid4, uuid5, UUID
from tabbyset.entities.test_case import TestCase

NAMESPACE_TEST_CASE = UUID('c5b52f89-d85e-48cc-b749-dd911b1e7526')

def new_id() -> str:
    """
    Generates a new ID.
    """
    return str(uuid4())

def get_id_from_steps(test_case: TestCase) -> str:
    """
    Generates ID based on the steps of the test case.

    Running this function multiple times with the same test case will always return the same ID.
    """
    return str(uuid5(namespace=NAMESPACE_TEST_CASE,
                     name=str(hash(test_case.steps))))

def is_valid_id(id_string: str) -> bool:
    """
    Checks if the given string is a valid UUID.
    """
    if isinstance(id_string, UUID):
        return True
    if not isinstance(id_string, str):
        return False
    try:
        UUID(id_string)
        return True
    except ValueError:
        return False