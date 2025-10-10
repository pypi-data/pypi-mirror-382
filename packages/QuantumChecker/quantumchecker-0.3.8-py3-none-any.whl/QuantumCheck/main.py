import logging
import os
import zipfile
from datetime import datetime
from typing import List, Dict
from .python_evaluator import PythonEvaluator
from .sql_evaluator import SQLEvaluator
from .powerbi_evaluator import PowerBIEvaluator
from .ssis_evaluator import SSISEvaluator
import asyncio

_logger_cache = {}

class HomeworkEvaluator:
    EVALUATOR_REGISTRY = {
        "python": PythonEvaluator,
        "sql": SQLEvaluator,
        "powerbi": PowerBIEvaluator,
        "ssis": SSISEvaluator
    }

    EXTENSION_TO_TYPE = {
        ".py": "python",
        ".sql": "sql",
        ".pbit": "powerbi",
        ".pdf": "powerbi",
        ".dtsx": "ssis",
        ".DTSX": "ssis",
        ".txt": "text",
        ".md": "text"
    }

    def __init__(self, log_level: int = logging.INFO):
        self.log_level = log_level
        self._lock = asyncio.Lock()
        self._last_request_time = None

    def _get_logger(self, log_type: str) -> logging.Logger:
        log_name = f"{log_type}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        if log_name not in _logger_cache:
            logger = logging.getLogger(log_name)
            logger.setLevel(self.log_level)
            if not logger.handlers:
                handler = logging.StreamHandler()
                handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
                logger.addHandler(handler)
            _logger_cache[log_name] = logger
        return _logger_cache[log_name]

    def parse_questions(self, content: str) -> List[str]:
        logger = self._get_logger("QuantumCheck.main")
        questions = [q.strip() for q in content.split("\n\n") if q.strip()]
        if not questions:
            raise ValueError("No valid questions found in content")
        return questions

    def _detect_zip_content_type(self, zip_path: str, logger: logging.Logger) -> str:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            extensions = {os.path.splitext(name)[1].lower() for name in zip_ref.namelist()}
            file_types = [self.EXTENSION_TO_TYPE.get(ext, "text") for ext in extensions if ext]
            if "python" in file_types:
                return "python"
            elif "sql" in file_types:
                return "sql"
            elif "powerbi" in file_types:
                return "powerbi"
            elif "ssis" in file_types:
                return "ssis"
            else:
                return "text"

    async def evaluate_from_content(
        self,
        question_content: str,
        answer_path: str,
        api_key: str,
        question_type: str
    ) -> Dict[str, any]:
        async with self._lock:
            now = datetime.now()
            if self._last_request_time:
                elapsed = (now - self._last_request_time).total_seconds()
                if elapsed < 5:
                    await asyncio.sleep(5 - elapsed)
            self._last_request_time = datetime.now()

            logger = self._get_logger("QuantumCheck.main")

            try:
                questions = self.parse_questions(question_content)
            except ValueError as e:
                return {
                    "score": 0,
                    "feedback": f"Error parsing question content: {str(e)}",
                    "issues": [str(e)],
                    "recommendations": []
                }

            answer_path = answer_path.strip()
            _, ext = os.path.splitext(answer_path)
            ext = ext.lower()

            if ext == ".zip":
                logger = self._get_logger("zip")
                file_type = self._detect_zip_content_type(answer_path, logger)
            else:
                file_type = self.EXTENSION_TO_TYPE.get(ext, "text")
                logger = self._get_logger(file_type)

            eval_type = question_type if question_type in self.EVALUATOR_REGISTRY else file_type

            if not os.path.exists(answer_path):
                return {
                    "score": 0,
                    "feedback": f"Answer file not found: {answer_path}",
                    "issues": [f"Answer file not found: {answer_path}"],
                    "recommendations": []
                }

            evaluator_class = self.EVALUATOR_REGISTRY.get(eval_type, PythonEvaluator)
            evaluator = evaluator_class(api_key)

            try:
                evaluation = evaluator.evaluate(questions, answer_path, temp_dir=f"temp_extract_{os.getpid()}")
                return {
                    "score": evaluation.get("score", 0),
                    "feedback": evaluation.get("feedback", "No feedback provided"),
                    "issues": evaluation.get("issues", []),
                    "recommendations": evaluation.get("recommendations", [])
                }

            except Exception as e:
                return {
                    "score": 0,
                    "feedback": f"Evaluation failed: {str(e)}",
                    "issues": [str(e)],
                    "recommendations": []
                }
