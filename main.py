import json
import logging
from pathlib import Path
from google.generativeai import configure, GenerativeModel

# Suppress irrelevant logging messages (Google library warnings)
logging.getLogger('google').setLevel(logging.CRITICAL)

# Configure your Gemini API key
configure(api_key="YOUR-API-KEY")  # Replace with your API key

# Function to load text from a file
def load_text(file_path):
    try:
        logging.info(f"🔍 Loading file: {file_path}")
        content = Path(file_path).read_text(encoding="utf-8")
        return content
    except FileNotFoundError:
        logging.error(f"⚠️ File not found: {file_path}")
        return ""
    except Exception as e:
        logging.error(f"⚠️ Error reading file {file_path}: {e}")
        return ""

# Function to build the prompt to send to Gemini
def build_prompt(jd_text, cv_text):
    return f"Job Description:\n{jd_text}\n\nCandidate CV:\n{cv_text}"

# Function to evaluate CV using Gemini model
def evaluate_cv(jd_file, cv_file, cv_id):
    logging.info(f"🔍 Evaluating CV{cv_id}...")

    # Load job description and CV text
    jd_text = load_text(jd_file)
    cv_text = load_text(cv_file)

    if not jd_text or not cv_text:
        logging.warning(f"⚠️ Skipping CV{cv_id} due to missing text data.")
        return

    # Build the prompt to send to Gemini
    prompt = build_prompt(jd_text, cv_text)

    # Initialize Gemini model
    try:
        model = GenerativeModel("models/gemini-2.5-flash")  # Replace with the correct model version
    except Exception as e:
        logging.error(f"⚠️ Error initializing Gemini model: {e}")
        return

    try:
        # Call Gemini API to generate content (evaluation of CV)
        logging.info(f"🔍 Calling Gemini API for CV{cv_id}...")
        response = model.generate_content(prompt, generation_config={"temperature": 0.3})
        
        # Check if the response is valid
        if not response or not response.text:
            logging.error(f"⚠️ No response received for CV{cv_id}")
            return

        # Clean up response text by removing markdown formatting (backticks)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")

        # Try to parse the response as JSON
        try:
            result = json.loads(cleaned_response)
        except json.JSONDecodeError:
            logging.error(f"⚠️ Error parsing JSON response for CV{cv_id}: {cleaned_response}")
            return

        # Calculate match score based on evaluation data
        match_score = calculate_match_score(result)
        verdict = determine_verdict(match_score)

        # Prepare the final evaluation result (JSON structure)
        formatted_result = {
            "match_score": match_score,
            "summary": result.get("summary", "No summary available."),
            "strengths": result.get("strengths", []),
            "missing_requirements": result.get("missing_requirements", []),
            "verdict": verdict
        }

        # Print the result to console for feedback
        print_evaluation(formatted_result, cv_id)

        # Create the output directory if it doesn't exist
        output_dir = Path("outputs")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save the result as JSON
        output_json_path = output_dir / f"cv{cv_id}_evaluation.json"
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(formatted_result, f, indent=4)
        
        logging.info(f"✅ Evaluation saved to: {output_json_path}")

        # Generate and save the markdown report
        generate_report(formatted_result, cv_id, output_dir)

    except Exception as e:
        logging.error(f"⚠️ Error processing CV{cv_id}: {e}")

# Function to print evaluation result to the console
def print_evaluation(formatted_result, cv_id):
    print(f"\n--- Evaluation Results for CV{cv_id} ---")
    print(f"Match Score: {formatted_result['match_score']}")
    print(f"Summary: {formatted_result['summary']}")
    print("Strengths:")
    for strength in formatted_result['strengths']:
        print(f"  - {strength}")
    print("Missing Requirements:")
    for req in formatted_result['missing_requirements']:
        print(f"  - {req}")
    print(f"Verdict: {formatted_result['verdict']}")
    print("\n--- End of Evaluation ---\n")

# Function to generate a markdown report from the JSON result
def generate_report(result, cv_id, output_dir):
    try:
        match_score = result.get("match_score", "N/A")
        summary = result.get("summary", "N/A")
        strengths = "\n".join(result.get("strengths", []))
        missing_requirements = "\n".join(result.get("missing_requirements", []))
        verdict = result.get("verdict", "N/A")

        report_content = f"""
# CV{cv_id} Evaluation Report

## Match Score: {match_score}

### Summary:
{summary}

### Strengths:
{strengths}

### Missing Requirements:
{missing_requirements}

### Verdict:
{verdict}
"""

        # Save the report to a markdown file
        report_path = output_dir / f"cv{cv_id}_evaluation_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        logging.info(f"✅ Report saved: {report_path}")

    except Exception as e:
        logging.error(f"⚠️ Error generating report for CV{cv_id}: {e}")

# Simple function to calculate match score (can be modified for better accuracy)
def calculate_match_score(result):
    # Placeholder: Adjust the logic as per your needs
    if "strong" in result.get("summary", "").lower():
        return 85
    elif "possible" in result.get("summary", "").lower():
        return 60
    else:
        return 30

# Determine verdict based on match score
def determine_verdict(match_score):
    if match_score >= 80:
        return "strong match"
    elif 50 <= match_score < 80:
        return "possible match"
    else:
        return "not a match"

# Main function to loop over CV files and evaluate them
def main():
    # File paths for job description and CVs (update paths if needed)
    jd_path = "sample_inputs/jd.txt"  # Replace with correct path
    cv_files = [
        "sample_inputs/cv1.txt",
        "sample_inputs/cv2.txt",
        "sample_inputs/cv3.txt",
    ]

    # Check if the job description file exists
    if not Path(jd_path).exists():
        logging.error(f"⚠️ Job description file '{jd_path}' not found.")
        return

    # Check if CV files exist
    for cv_file in cv_files:
        if not Path(cv_file).exists():
            logging.error(f"⚠️ CV file '{cv_file}' not found.")
            return

    # Evaluate each CV
    for i, cv_file in enumerate(cv_files, 1):
        logging.info(f"🔍 Evaluating CV{i}...")
        evaluate_cv(jd_path, cv_file, i)

# Run the main function
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)  # Set logging level to INFO for more visibility
    main()
