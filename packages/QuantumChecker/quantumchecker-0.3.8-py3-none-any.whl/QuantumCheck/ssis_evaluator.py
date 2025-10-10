import logging
import os
import zipfile
import shutil
import xml.etree.ElementTree as ET
from typing import List, Dict
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pprint import pprint
import re

from .prompts import prompt_text_ssis

logger = logging.getLogger(__name__)


class GeminiFlashModel:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash-lite"):
        if not api_key:
            raise ValueError("API key is required.")
        self.api_key = api_key
        self.model_name = model_name
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.exceptions.RequestException,))
    )
    def evaluate(self, combined_content: str) -> Dict[str, any]:
        logger.info("Starting evaluation of SSIS question-answer content")
        headers = {"Content-Type": "application/json"}
        data = {"contents": [{"parts": [{"text": prompt_text_ssis(combined_content)}]}]}

        response = requests.post(f"{self.endpoint}?key={self.api_key}", headers=headers, json=data)
        if response.status_code != 200:
            raise Exception(f"API call failed: {response.status_code} - {response.text}")

        response_data = response.json()
        if not response_data.get("candidates"):
            raise ValueError("No candidates in API response")

        parts = response_data["candidates"][0].get("content", {}).get("parts", [])
        if not parts or not isinstance(parts, list) or not parts[0].get("text"):
            raise ValueError("Missing 'parts' or 'text' in API response content")

        generated_text = parts[0]["text"]
        return self._parse_response(generated_text)

    def _parse_response(self, text: str) -> Dict[str, any]:
        result = {"score": 0, "feedback": "Evaluation not returned by API.", "issues": [], "recommendations": []}
        try:
            lines = text.split("\n")
            score_found = False
            feedback_lines = []
            for line in lines:
                line = line.strip()
                if not score_found and line.startswith("OVERALL SCORE:") and "/100" in line:
                    try:
                        result["score"] = int(line.split(":")[1].split("/")[0].strip())
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
            logger.error("Error parsing API response: %s", str(e))
            result["issues"].append(str(e))
            return result


class SSISAnswerParser:
    @staticmethod
    def parse_single_file(content: str) -> Dict[str, any]:
        try:
            root = ET.fromstring(content)
            namespace = {'DTS': 'www.microsoft.com/SqlServer/Dts'}
            summary = []
            structured_data = {
                "package_info": {},
                "connections": [],
                "variables": [],
                "data_flow_components": [],
                "data_flow_paths": [],
                "issues": []
            }


            package_info = {
                "Package Name": root.attrib.get("{www.microsoft.com/SqlServer/Dts}ObjectName", "Unknown"),
                "Creation Date": root.attrib.get("{www.microsoft.com/SqlServer/Dts}CreationDate", "Unknown"),
                "Creator": root.attrib.get("{www.microsoft.com/SqlServer/Dts}CreatorName", "Unknown"),
                "Computer": root.attrib.get("{www.microsoft.com/SqlServer/Dts}CreatorComputerName", "Unknown"),
                "Version": root.attrib.get("{www.microsoft.com/SqlServer/Dts}VersionGUID", "Unknown")
            }
            structured_data["package_info"] = package_info
            summary.append(f"Package: {package_info['Package Name']} (Created: {package_info['Creation Date']})")


            package_description = "No description found"
            comment_pattern = re.compile(r'<!--\s*Package Description:\s*(.*?)\s*-->', re.DOTALL)
            match = comment_pattern.search(content)
            if match:
                package_description = match.group(1).strip()
                summary.append(f"Description: {package_description}")


            for conn in root.findall(".//DTS:ConnectionManager", namespace):
                try:
                    conn_name = conn.attrib.get("{www.microsoft.com/SqlServer/Dts}ObjectName", "Unnamed Connection")
                    conn_type = conn.attrib.get("{www.microsoft.com/SqlServer/Dts}CreationName", "Unknown")
                    conn_details = {"Name": conn_name, "Type": conn_type, "ConnectionString": "N/A"}
                    conn_obj_data = conn.find(".//DTS:ObjectData/DTS:ConnectionManager", namespace)
                    if conn_obj_data is not None:
                        conn_string = conn_obj_data.attrib.get("{www.microsoft.com/SqlServer/Dts}ConnectionString",
                                                               "N/A")
                        conn_details["ConnectionString"] = conn_string
                        if conn_type == "FLATFILE":
                            columns = []
                            for col in conn_obj_data.findall(".//DTS:Column", namespace):
                                col_name = col.attrib.get("{www.microsoft.com/SqlServer/Dts}Name", None)
                                if col_name:
                                    columns.append(col_name)
                                else:
                                    structured_data["issues"].append(
                                        f"Column in connection {conn_name} missing Name attribute")
                            conn_details["Columns"] = columns
                    summary.append(
                        f"Connection: {conn_name} ({conn_type}, ConnectionString: {conn_details['ConnectionString']})")
                    structured_data["connections"].append(conn_details)

                    if conn_type == "OLEDB" and "Initial Catalog" not in conn_details["ConnectionString"]:
                        structured_data["issues"].append(f"OLEDB Connection {conn_name} missing database specification")
                except AttributeError as e:
                    structured_data["issues"].append(f"Error parsing connection {conn_name}: {str(e)}")
                    logger.error("Error parsing connection %s: %s", conn_name, str(e))


            for var in root.findall(".//DTS:Variable", namespace):
                try:
                    var_name = var.attrib.get("{www.microsoft.com/SqlServer/Dts}ObjectName", "Unnamed Variable")
                    var_value_elem = var.find("DTS:VariableValue", namespace)
                    var_value = var_value_elem.text if var_value_elem is not None and hasattr(var_value_elem,
                                                                                              'text') else "N/A"
                    summary.append(f"Variable: {var_name} = {var_value}")
                    structured_data["variables"].append({"Name": var_name, "Value": var_value})
                    if var_value == "N/A":
                        structured_data["issues"].append(f"Variable {var_name} has no value")
                except AttributeError as e:
                    structured_data["issues"].append(f"Error parsing variable {var_name}: {str(e)}")
                    logger.error("Error parsing variable %s: %s", var_name, str(e))


            component_ids = set()
            for component in root.findall(".//DTS:Executables//component", namespace):
                try:
                    comp_name = component.attrib.get("name", "Unnamed Component")
                    comp_ref_id = component.attrib.get("refId", "Unknown")
                    component_ids.add(comp_ref_id)
                    summary.append(f"Component: {comp_name}")
                    structured_data["data_flow_components"].append({"Name": comp_name, "RefId": comp_ref_id})
                except AttributeError as e:
                    structured_data["issues"].append(f"Error parsing component {comp_name}: {str(e)}")
                    logger.error("Error parsing component %s: %s", comp_name, str(e))


            for path in root.findall(".//DTS:Executables//path", namespace):
                try:
                    start_id = path.attrib.get("startId", "Unknown Start")
                    end_id = path.attrib.get("endId", "Unknown End")
                    path_name = path.attrib.get("name", "Unnamed Path")
                    summary.append(f"Data Flow Path: {path_name} ({start_id} -> {end_id})")
                    structured_data["data_flow_paths"].append({"Path Name": path_name, "From": start_id, "To": end_id})
                    if start_id not in component_ids or end_id not in component_ids:
                        structured_data["issues"].append(
                            f"Path {path_name} references non-existent components: {start_id} -> {end_id}")
                except AttributeError as e:
                    structured_data["issues"].append(f"Error parsing path {path_name}: {str(e)}")
                    logger.error("Error parsing path %s: %s", path_name, str(e))


            if not structured_data["connections"]:
                structured_data["issues"].append("No connections configured in the package")
            if not structured_data["data_flow_paths"]:
                structured_data["issues"].append("No data flow paths configured in the package")

            combined_summary = "\n".join(summary)[:2000] or "No components found in SSIS package"

            answers = []
            sections = ["Package", "Description", "Connection", "Variable", "Component", "Data Flow Path"]
            current_section = []
            for line in summary:
                if any(line.startswith(s) for s in sections) and current_section:
                    answers.append("\n".join(current_section))
                    current_section = [line]
                else:
                    current_section.append(line)
            if current_section:
                answers.append("\n".join(current_section))

            if not answers:
                logger.warning("No valid answers found in single SSIS file")
                answers = [combined_summary]

            return {
                "text_answers": answers,
                "structured_data": structured_data
            }

        except ET.ParseError as e:
            logger.error("Invalid SSIS package file: %s", str(e))
            return {"text_answers": ["Invalid SSIS package file"], "structured_data": {"issues": [str(e)]}}
        except Exception as e:
            logger.error("Unexpected error parsing .dtsx file: %s", str(e))
            with open("debug_dtsx_content.txt", "w", encoding="utf-8") as f:
                f.write(content)
            logger.info("Saved raw .dtsx content to 'debug_dtsx_content.txt' for debugging")
            return {"text_answers": ["Error parsing SSIS package"], "structured_data": {"issues": [str(e)]}}

    @staticmethod
    def parse_zip_file(zip_path: str, temp_dir: str) -> Dict[str, any]:
        """
        Parse SSIS files from a ZIP file, extracting to the specified temp_dir.

        Args:
            zip_path: Path to the ZIP file
            temp_dir: Directory to extract ZIP contents

        Returns:
            Dictionary containing text_answers and structured_data
        """
        combined_answers = []
        combined_structured_data = {
            "package_info": {},
            "connections": [],
            "variables": [],
            "data_flow_components": [],
            "data_flow_paths": [],
            "issues": []
        }

        try:
            # Create temporary extraction directory
            os.makedirs(temp_dir, exist_ok=True)
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            dtsx_files = sorted(
                [f for f in os.listdir(temp_dir) if f.lower().endswith(".dtsx")]
            )

            if not dtsx_files:
                logger.warning(f"No .dtsx files found in ZIP: {zip_path}")
                return {
                    "text_answers": ["No SSIS files found in ZIP"],
                    "structured_data": {"issues": ["No .dtsx files found"]}
                }

            for dtsx_file in dtsx_files:
                file_path = os.path.join(temp_dir, dtsx_file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        parsed_data = SSISAnswerParser.parse_single_file(content)
                        combined_answers.extend(parsed_data.get("text_answers", []))
                        # Merge structured data
                        structured_data = parsed_data.get("structured_data", {})
                        combined_structured_data["connections"].extend(structured_data.get("connections", []))
                        combined_structured_data["variables"].extend(structured_data.get("variables", []))
                        combined_structured_data["data_flow_components"].extend(
                            structured_data.get("data_flow_components", []))
                        combined_structured_data["data_flow_paths"].extend(structured_data.get("data_flow_paths", []))
                        combined_structured_data["issues"].extend(structured_data.get("issues", []))
                        # Update package_info with the last file's info (if needed)
                        if structured_data.get("package_info"):
                            combined_structured_data["package_info"] = structured_data["package_info"]

            if not combined_answers:
                logger.warning(f"No valid content found in .dtsx files in ZIP: {zip_path}")
                return {
                    "text_answers": ["No valid SSIS content found in ZIP"],
                    "structured_data": combined_structured_data
                }

            return {
                "text_answers": combined_answers,
                "structured_data": combined_structured_data
            }
        except zipfile.BadZipFile:
            logger.error(f"Invalid ZIP file: {zip_path}")
            return {
                "text_answers": ["Invalid ZIP file"],
                "structured_data": {"issues": ["Invalid ZIP file"]}
            }
        except Exception as e:
            logger.error(f"Error processing ZIP file {zip_path}: {str(e)}")
            return {
                "text_answers": ["Error processing SSIS ZIP file"],
                "structured_data": {"issues": [str(e)]}
            }
        finally:
            # Clean up temporary directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
                logger.info(f"Cleaned up temporary directory: {temp_dir}")


class SSISEvaluator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = GeminiFlashModel(api_key)

    def evaluate(self, questions: List[str], answer_path: str, temp_dir: str = None) -> Dict[str, any]:
        """
        Evaluate an SSIS submission.

        Args:
            questions: List of questions to evaluate against
            answer_path: Path to the answer file (ZIP or .dtsx file)
            temp_dir: Optional directory for temporary ZIP extraction

        Returns:
            Dictionary containing score, feedback, issues, and recommendations
        """
        try:
            if answer_path.lower().endswith(".zip"):

                temp_dir = temp_dir or f"temp_ssis_extract_{os.getpid()}"
                parsed_data = SSISAnswerParser.parse_zip_file(answer_path, temp_dir)
            elif answer_path.lower().endswith('.dtsx'):
                with open(answer_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                parsed_data = SSISAnswerParser.parse_single_file(content)
            else:
                raise ValueError("File must be a .dtsx file or a ZIP containing .dtsx files")

            if not isinstance(parsed_data, dict):
                raise TypeError(f"Expected dict from parse, got {type(parsed_data)}")

            answers = parsed_data.get("text_answers", [])
            structured_data = parsed_data.get("structured_data", {"issues": []})

            if not isinstance(answers, list):
                raise TypeError(f"Expected list for text_answers, got {type(answers)}")
            if not isinstance(structured_data, dict):
                raise TypeError(f"Expected dict for structured_data, got {type(structured_data)}")

            logger.info("Processing %d questions and %d answers", len(questions), len(answers))
            pprint(f"Processing {len(questions)} questions and {len(answers)} answers")


            if not answers:
                logger.warning("No answers parsed from SSIS file")
                answers = ["No valid SSIS components found"] * len(questions)
            elif len(answers) < len(questions):

                answers = [answers[i % len(answers)] for i in range(len(questions))]
                logger.debug("Expanded %d answers to %d for %d questions", len(parsed_data["text_answers"]),
                             len(answers), len(questions))
            elif len(answers) > len(questions):

                answers = answers[:len(questions)]
                logger.debug("Truncated %d answers to %d for %d questions", len(parsed_data["text_answers"]),
                             len(answers), len(questions))

            combined_questions = "\n".join([q.strip() for q in questions if q.strip()])
            combined_answers = "\n".join([a.strip() for a in answers if a.strip()])
            issues = structured_data.get("issues", [])
            combined_raw_content = (
                f"Questions:\n{combined_questions}\n\n"
                f"Answers:\n{combined_answers}\n\n"
                f"Issues:\n{', '.join(issues) if issues else 'None'}"
            )


            result = self.model.evaluate(combined_raw_content)
            result["issues"] = result.get("issues", []) + issues
            return result

        except Exception as e:
            logger.error("Evaluation failed: %s", str(e))
            return {"score": 0, "feedback": f"Evaluation failed: {str(e)}", "issues": [str(e)], "recommendations": []}