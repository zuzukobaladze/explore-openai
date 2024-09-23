import os

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

load_dotenv()

client = OpenAI()
LLM = os.environ.get("OPEN_AI_MODEL")


def ask_openai(
    prompt: str,
) -> ChatCompletion:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    return response


def multi_step_instruction():
    text = """
    Peter is a software engineer living in France with his wife, two daughters, and their beloved dog.
    He deeply values family time, often enjoying weekends filled with laughter and activities with his loved ones.
    In addition to being a devoted family man, Pierre has a passion for soccer and plays regularly in his free time. 
    Balancing work and play, he cherishes every moment spent both on the field and at home, where his heart truly belongs.
    """

    prompt = f"""
    Perform the following actions on the text delimited by triple backticks:

    1. Summarize the text in one sentence.
    2. Translate the summary into French.
    3. List the key people mentioned in the text.
    4. Output a JSON object with the structure:
    {{
        "summary": "<your summary>",
        "translation": "<translated summary>",
        "people": ["<person1>", "<person2>", ...]
    }}

    ```{text}```
    """
    response = ask_openai(prompt=prompt)
    # Print the Type and Response
    print(f"response  : {response.choices[0].message.content}")


def analyze_person_profile():
    text = """
    ```
    John is a 34-year-old architect living in London. He has been working in the field for over 10 years and specializes in sustainable building designs.
    John is married to Sarah, and they have a son named Liam. In his free time, he enjoys hiking, reading books about history, and volunteering at a local community center.
    John is passionate about making a positive impact on the environment through his work.
    ```
    """

    prompt = f"""
    Perform the following actions on the text delimited by triple backticks:

    1. **Summarize** the text in 2 sentences.
    2. **Identify** the profession and hobbies of the person in the text.
    3. **Provide advice** for someone who shares the same profession on how to balance work and personal life.
    4. **Output** a JSON object with the following structure:

        {{
            "summary": "<your summary>",
            "profession": "<profession>",
            "hobbies": ["<hobby1>", "<hobby2>", ...],
            "advice": "<your advice>"
        }}

Please ensure your answers are separated by line breaks.

    Text to process:
    ```{text}```
    """
    response = ask_openai(prompt=prompt)
    # Print the Type and Response
    print(f"response  : {response.choices[0].message.content}")


def analyze_personal_journey():
    text = """
    ```
    Emily is an aspiring author who has been working on her first novel for three years. 
    She often struggles with self-doubt and feels that her work may never be good enough. 
    Despite this, she remains dedicated to improving her craft, writing every day, and learning from her mistakes.
    In addition to writing, Emily enjoys painting and taking long walks in nature, which help her clear her mind and find inspiration.
    ```
    """

    prompt = f"""
        Perform the following actions on the text delimited by triple backticks:

        1. **Summarize** the person's journey in 1-2 sentences.
        2. **Identify** the key emotional states (e.g., frustration, joy, fear) mentioned in the text.
        3. **Analyze** the main themes in the person's journey (e.g., perseverance, creativity).
        4. **Provide motivational advice** to help the person overcome their self-doubt.
        5. **Output** a JSON object with the following structure:

            {{
                "summary": "<your summary>",
                "emotional_states": ["<emotion1>", "<emotion2>", ...],
                "themes": ["<theme1>", "<theme2>", ...],
                "advice": "<your motivational advice>"
            }}

    Please ensure your answers are separated by line breaks.

        Text to process:
        ```{text}```
    """
    response = ask_openai(prompt=prompt)
    # Print the Type and Response
    print(f"response  : {response.choices[0].message.content}")


if __name__ == "__main__":
    multi_step_instruction()
    # analyze_person_profile()
    # analyze_personal_journey()
