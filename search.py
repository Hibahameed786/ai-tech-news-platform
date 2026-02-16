import pandas as pd

def find_answer(question):
    df = pd.read_csv("tech_news.csv")

    question = question.lower()
    results = []

    for _, row in df.iterrows():
        text = (row["title"] + " " + row["summary"]).lower()

        if any(word in text for word in question.split()):
            results.append(row["title"])

    if results:
        return "\n".join(results[:5])
    else:
        return "No matching news found."
