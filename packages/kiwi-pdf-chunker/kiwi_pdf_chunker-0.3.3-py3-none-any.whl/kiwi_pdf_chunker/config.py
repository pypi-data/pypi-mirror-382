"""
Configuration settings for the PDF parser.

This module loads configuration from environment variables or default values.
"""

import os
import logging
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = os.getenv("MODEL_DIR", os.path.join(BASE_DIR, "models"))
OUTPUT_DIR = os.getenv("OUTPUT_DIR", os.path.join(BASE_DIR, "output"))
DEBUG_DIR = os.getenv("DEBUG_DIR", os.path.join(OUTPUT_DIR, "debug"))
TEMP_DIR = os.getenv("TEMP_DIR", os.path.join(BASE_DIR, "temp"))

# Ensure directories exist
os.makedirs(MODEL_DIR, exist_ok = True)
os.makedirs(OUTPUT_DIR, exist_ok = True)
os.makedirs(TEMP_DIR, exist_ok = True)

# Model paths
YOLO_MODEL_PATH = os.path.join(MODEL_DIR, "doclayout_yolo_docstructbench_imgsz1024.pt")

# Image Processing Settings
ZOOM_FACTOR = float(os.getenv("ZOOM_FACTOR", "2.0"))
IOU_THRESHOLD = float(os.getenv("IOU_THRESHOLD", "0.45"))
CONTAINMENT_THRESHOLD = float(os.getenv("CONTAINMENT_THRESHOLD", "0.90"))

# Box Processing Settings
AUTOMATIC_ROW_DETECTION = os.getenv("AUTOMATIC_ROW_DETECTION", "True").lower() in ("true", "1", "yes")
ROW_SIMILARITY_THRESHOLD = int(os.getenv("ROW_SIMILARITY_THRESHOLD", "10"))
CONTAINER_THRESHOLD = int(os.getenv("CONTAINER_THRESHOLD", "2"))

# Memory Management Settings
MEMORY_EFFICIENT = os.getenv("MEMORY_EFFICIENT", "True").lower() in ("true", "1", "yes")
PAGE_BATCH_SIZE = int(os.getenv("PAGE_BATCH_SIZE", "1"))
ENABLE_GC = os.getenv("ENABLE_GC", "True").lower() in ("true", "1", "yes")
CLEAR_CUDA_CACHE = os.getenv("CLEAR_CUDA_CACHE", "True").lower() in ("true", "1", "yes")

# Text label categories (elements that should be preserved during processing)
TEXT_LABELS = ["title", "plain_text"] #"table_caption", "table_footnote", "formula_caption"]

# Embedding Settings
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"

# Debug mode settings
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in ("true", "1", "yes")
if DEBUG_MODE:
    logging.basicConfig(level = logging.DEBUG)

else:
    logging.basicConfig(level = logging.INFO)

# System prompt for table classification
TABLE_CLASSIFICATION_SYSTEM_PROMPT = """
You are a PDF-table classifier.  
Your entire reply **MUST be a single, valid JSON object** that uses the exact keys and formats shown below.

[INPUT]
  [TABLE_TEXT] - the content of the table in a structured format  
  [CATEGORIES] - a JSON/dict mapping each category name to its natural-language description.
                 e.g. {"change_table": "If the table represents a change or amendment to existing products, goods, or services", "contact_information": "If the table contains contact information for a person or company", ...}

[TASK]
  For **each** category in [CATEGORIES] decide whether the table satisfies the description (**true**) or not (**false**).

[OUTPUT]
  Return **ONLY** minified JSON with the same keys that appear in [CATEGORIES], 
  e.g.: {"change_table": true, "contact_information": false, ...}

[RULES]
  - Use **only** the category names provided in [CATEGORIES] as JSON keys.  
  - Values **must** be lowercase JSON booleans: `true` or `false`.  
  - **Never** add keys, comments, or extra text.  
  - If uncertain, output `false`.  
  - Think step-by-step **internally**, but output **only** the JSON object.  
  - The result **must parse** with a standard JSON parser.
"""

TABLE_SUMMARY_SYSTEM_PROMPT = """
You are an expert table summarizer.  
Your task is to produce a **brief summary (less than 50 words)** of the table content in a fixed format.

[INPUT]  
  [TABLE_TEXT] - the content of the table in a structured format 

[TASK]  
  - Write a concise summary of what the table contains.  
  - The summary must be less than 50 words.  
  - Always follow this format exactly:  
    Table containing {CONTENT SUMMARY}. Columns: \n {COLUMNS}  

    - {CONTENT SUMMARY}: a short description of the content of the table.  
    - {COLUMNS}: a comma-separated list of the column headers in the order they appear.  

[OUTPUT]  
  Output only the summary string in the specified format.  

[RULES]  
  - Do not exceed 50 words for {CONTENT SUMMARY}.  
  - Do not add extra commentary or text outside the required format.  
  - If columns are unclear, include them exactly as extracted.  
  - Be strictly faithful to the content in [TABLE_TEXT]; never invent details.
"""

TABLE_ID_COLUMN_SYSTEM_PROMPT = """
You are an expert table analyzer.  
Your task is to detect which columns in the table are **identifier columns**.  
Identifier columns are those that contain values such as IDs, codes, numbers, or other unique keys that could later be used to look up entities like user IDs, product IDs, quote IDs, circuit IDs, etc.

[INPUT]  
  [TABLE_TEXT] - the content of the table in a structured format  

[TASK]  
  - Identify all columns whose contents represent identifiers or unique keys.  
  - Typical identifier columns include:  
    - Alphanumeric codes (e.g., PROD001, USER1234, QUOTE-9876).  
    - Numeric-only unique values (e.g., 19142213, 5_000115003).  
    - Circuit IDs, invoice numbers, order numbers, etc.  
  - Ignore columns with descriptive names or free text that don't act as identifiers (e.g., Product Description, Action).  

[OUTPUT]
  Return a Python list in the following format:  
  ["<column_name_1>", "<column_name_2>", ...]  

  Example: ["Product Code", "Serial #"]

[RULES]  
  - Only include columns that function as identifiers.  
  - Use the column headers exactly as they appear in the table.  
  - If no identifier column is found, return [].  
  - Do not add commentary, explanations, or extra text outside the list.  
  - The result must be a valid Python list.
"""

TABLE_CATEGORIES = {
  "address_information": "If the table contains address information like shipping address, billing address, vendor address, or customer address",
  "billing_information": "If the table contains billing instructions such as payment instructions, payment frequency, or billed to instructions",
  "change_table": "If the table represents a change or amendment to existing products, goods, or services",
  "contact_information": "If the table contains contact information for a person or company",
  "date_information": "If the table contains commitment period information such as start and end dates, contract term, or auto-renewal information. Do not include dates related to signatures or individual products, goods, or services",
  "discount_information": "If the table content explicit information about discounts. Only answer True if there is content explicitly stating discounts. If a product, good, or service has no cost information return False unless the lack of cost information is labeled as a discount in the table",
  "overview_information": "If the table is primarily an overview, description, or summary of the document or section",
  "product_table": "If the table an image of products, goods, or services from a purchase order",
  "signature_information": "If the content is a signature table",
  "terms_information": "If the content is primarily a list of terms such as legal terms, definitions, or price increase terms",
  "totals": "If the content represents billing or cost totals",
  "charges_recurring": "Tables that list ongoing/periodic charges (e.g., 'Monthly Recurring Services', lines with an MRC column or recurring rate). Do not use for one-time fees.",
  "charges_one_time": "Tables that list setup/installation or other non-recurring items (NRC or 'One-Time Items').",
  "line_item_pricing": "General line-item price tables showing Qty/UoM, unit rate, and extended price (often with both MRC and NRC columns). Use when the table is not explicitly scoped to recurring-only or one-time-only.",
  "taxes_and_fees": "Tables that explicitly enumerate regulatory or compliance surcharges, taxes, or fees (e.g., e911, administrative recovery).",
  "payment_information": "If the table primarily contains how/when to PAY: payment terms or remittance instructions.",
  "currency_information": "If the table explicitly specifies the currency for amounts.",
  "schedule_information": "If the table presents a project/work schedule (common in SOWs): tasks/activities, milestones, deliverables, owners, durations, start/due dates, or dependencies.",
  "definitions_information": "If the table contains legal definitions, e.g., two columns like 'Term' and 'Definition', or rows of the form '“X” means …'."
}