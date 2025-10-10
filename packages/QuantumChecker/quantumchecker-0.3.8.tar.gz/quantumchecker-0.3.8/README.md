Sample usage: 
```
import asyncio
from your_evaluator_module import HomeworkEvaluator

async def main():
    evaluator = HomeworkEvaluator()
    question_content = """
Q1: What is a Python list? Explain with an example.

Q2: Write an SQL query to select all records from a table named 'students'.
"""
    answer_path = "sample_submissions/student1_answer.py"
    question_type = "python"

    result = await evaluator.evaluate_from_content(
        question_content=question_content,
        answer_path=answer_path,
        api_key="your_api_key",
        question_type=question_type
    )
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```