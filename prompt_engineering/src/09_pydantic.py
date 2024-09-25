import json

from pydantic import BaseModel, ValidationError


class Person(BaseModel):
    name: str
    age: int


def parse_json(json_str: str) -> Person:
    try:
        # Convert JSON string to Python dictionary
        data = json.loads(json_str)

        # Parse the dictionary into a Person object
        person = Person(**data)
        return person
    except ValidationError as e:
        print("Validation error:", e.json())
        raise


if __name__ == "__main__":
    person_json = """
    {
    "name": "Max",
    "age": 30
    }
    """
    person = parse_json(person_json)
    print("Parsed Person:", person)

    # Manipulate JSON
    person.age += 1
    print(f"Updated Age: {person.age}")
    person.name = "Dilip"
    print(f"Updated Name: {person.name}")

    print("Updated Person:", person)
