import logging
import os
import zipfile
import shutil
from pprint import pprint
from typing import List, Dict

import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from .prompts import prompt_text_sql

logger = logging.getLogger(__name__)


class GeminiFlashModel:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash-lite"):
        if not api_key:
            raise ValueError("API key is required.")
        self.api_key = api_key
        self.model_name = model_name
        self.endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model_name}:generateContent"
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.exceptions.RequestException,)),
    )
    def evaluate(self, combined_content: str) -> Dict[str, any]:
        logger.info("Starting evaluation of SQL question-answer content")

        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [
                {"parts": [{"text": prompt_text_sql(combined_content)}]}
            ]
        }

        response = requests.post(
            f"{self.endpoint}?key={self.api_key}",
            headers=headers,
            json=data,
        )

        if response.status_code != 200:
            raise Exception(
                f"API call failed: {response.status_code} - {response.text}"
            )

        response_data = response.json()
        if not response_data.get("candidates"):
            raise ValueError("No candidates in API response")

        generated_text = response_data["candidates"][0]["content"]["parts"][0][
            "text"
        ]
        return self._parse_response(generated_text)

    def _parse_response(self, text: str) -> Dict[str, any]:
        result = {
            "score": 0,
            "feedback": "Evaluation not returned by API.",
            "issues": [],
            "recommendations": [],
        }
        try:
            lines = text.split("\n")
            score_found = False
            feedback_lines = []

            for line in lines:
                line = line.strip()
                if not score_found and line.startswith("OVERALL SCORE:") and "/100" in line:
                    try:
                        result["score"] = int(
                            line.split(":")[1].split("/")[0].strip()
                        )
                        score_found = True
                    except ValueError:
                        result["issues"].append("Failed to parse score from API response")
                        continue
                elif score_found:
                    feedback_lines.append(line)

            if feedback_lines:
                result["feedback"] = "\n".join(feedback_lines).strip()

            return result
        except Exception as e:
            result["issues"].append(str(e))
            return result


class SQLAnswerParser:
    @staticmethod
    def parse_single_file(content: str) -> List[str]:
        answers = [a.strip() for a in content.strip().split("\n\n") if a.strip()]
        if not answers:
            logger.warning("No valid answers found in single file")
        return answers

    @staticmethod
    def parse_zip_file(zip_path: str, temp_dir: str) -> List[str]:
        """
        Parse SQL files from a ZIP file, extracting to the specified temp_dir.

        Args:
            zip_path: Path to the ZIP file
            temp_dir: Directory to extract ZIP contents

        Returns:
            List of answer strings extracted from SQL files
        """
        combined_content = []

        try:
            # Create temporary extraction directory
            os.makedirs(temp_dir, exist_ok=True)
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            sql_files = sorted(
                [f for f in os.listdir(temp_dir) if f.endswith(".sql")]
            )

            if not sql_files:
                logger.warning(f"No SQL files found in ZIP: {zip_path}")
                return []

            for sql_file in sql_files:
                with open(
                        os.path.join(temp_dir, sql_file),
                        "r",
                        encoding="utf-8",
                ) as f:
                    content = f.read().strip()
                    if content:
                        combined_content.append(content)

            if not combined_content:
                logger.warning(f"No valid content found in SQL files in ZIP: {zip_path}")
                return []

            combined_text = "\n\n".join(combined_content)
            return [a.strip() for a in combined_text.split("\n\n") if a.strip()]
        except zipfile.BadZipFile:
            logger.error(f"Invalid ZIP file: {zip_path}")
            return []
        except Exception as e:
            logger.error(f"Error processing ZIP file {zip_path}: {str(e)}")
            return []
        finally:
            # Clean up temporary directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
                logger.info(f"Cleaned up temporary directory: {temp_dir}")


class SQLEvaluator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = GeminiFlashModel(api_key)

    def evaluate(self, questions: List[str], answer_path: str, temp_dir: str = None) -> Dict[str, any]:
        """
        Evaluate an SQL submission.

        Args:
            questions: List of questions to evaluate against
            answer_path: Path to the answer file (ZIP or single file)
            temp_dir: Optional directory for temporary ZIP extraction

        Returns:
            Dictionary containing score, feedback, issues, and recommendations
        """
        try:
            if answer_path.endswith(".zip"):
                # Use provided temp_dir or generate a default one
                temp_dir = temp_dir or f"temp_sql_extract_{os.getpid()}"
                answers = SQLAnswerParser.parse_zip_file(answer_path, temp_dir)
            else:
                with open(answer_path, "r", encoding="utf-8") as file:
                    content = file.read()
                answers = SQLAnswerParser.parse_single_file(content)

            logger.info(
                f"Processing {len(questions)} questions and {len(answers)} answers"
            )
            pprint(f"Processing {len(questions)} questions and {len(answers)} answers")

            combined_questions = "\n".join([q.strip() for q in questions if q.strip()])
            combined_answers = "\n".join([a.strip() for a in answers if a.strip()])
            combined_raw_content = (
                f"Questions:\n{combined_questions}\n\nAnswers:\n{combined_answers}"
            )

            return self.model.evaluate(combined_raw_content)
        except Exception as e:
            logger.error(f"Failed to process answers from {answer_path}: {str(e)}")
            return {
                "score": 0,
                "feedback": f"Error processing answers: {str(e)}",
                "issues": [str(e)],
                "recommendations": []
            }