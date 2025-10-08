from tabbyset.entities.test_case import TestCase

def tc_to_dict(tc: TestCase) -> dict:
    return {
        "name": tc.name,
        "description": tc.description,
        "id": tc.id,
        "steps": list(tc.steps),
    }

def dict_to_tc(tc_dict: dict) -> TestCase:
    return TestCase(
        name=tc_dict["name"],
        steps=tc_dict["steps"],
        description=tc_dict.get("description", ""),
        id=tc_dict.get("id", None)
    )