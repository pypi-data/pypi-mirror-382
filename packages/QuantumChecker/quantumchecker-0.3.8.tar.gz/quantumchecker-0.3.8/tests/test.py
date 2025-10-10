import asyncio
from pprint import pprint
from QuantumCheck import HomeworkEvaluator

API_KEY = "AIzaSyDw76DEINpfBVgwIEZLShhy97tvWg7BmzY"

question_sets = {
    "python": "Write a Python function to calculate factorial.\nWrite a Python script to reverse a string.",
    "powerbi": "Create a Power BI report\nExplain DAX measures for sales analysis.",
    "sql": "Write a SQL query to join two tables.\nWrite a SQL query for aggregate functions.",
    "ssis": "Design an SSIS package for data import.\nExplain SSIS control flow tasks."
}

answer_paths = {
    "python": ["../tests/answers/second_highest_salary.py"],
    "powerbi": ["../tests/answers/random_diagrams.pdf"],
    "sql": ["../tests/answers/second_highest_salary.sql"],
    "ssis": ["../tests/answers/Package.dtsx"]
}

async def main():
    evaluator = HomeworkEvaluator()

    for qtype, question in question_sets.items():
        for ans in answer_paths[qtype]:
            evaluation = await evaluator.evaluate_from_content(
                question_content=question,
                answer_path=ans,
                api_key=API_KEY,
                question_type=qtype
            )

            print(f"{qtype} | {ans}")
            print(f"✅ Evaluation result: {pprint(evaluation)}")
            print("-" * 40)

if __name__ == "__main__":
    asyncio.run(main())
