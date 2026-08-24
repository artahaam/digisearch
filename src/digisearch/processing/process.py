import json
from digisearch.paths import PROCESSED_DIR, PROJECT_ROOT


def extract_questions_data(file_path: str):
    with open(file_path, "r", encoding='utf-8') as file:
        f = file.read()
        questions = []
        try:
            loads = json.loads(f)[:5]
            for l in loads:
                _questions = l.get("questions")
                for _question in _questions:

                    question = _question.get("text")
                    answers = []

                    for ans in _question["answers"]:
                        answers.append(ans["text"])

                    questions.append({'question': question,
                                      'answers': answers})
        except:
            pass

    return json.dumps(questions, indent=4,  ensure_ascii=False)



def extract_details_data(file_path: str):

    return ""

def extract_comments_data(file_path: str):

    return ""


with open(PROCESSED_DIR / "product_list.json", "r") as file:

    f = file.read()

    for p in json.loads(f)[:100]:

        product_id = p['product'].get('id')
        questions_path = p['product'].get('questions_path')
        details_path = p['product'].get('details_path')
        comments_path = p['product'].get('comments_path')
        category = p['product'].get('category')


        questions = extract_questions_data(questions_path)


