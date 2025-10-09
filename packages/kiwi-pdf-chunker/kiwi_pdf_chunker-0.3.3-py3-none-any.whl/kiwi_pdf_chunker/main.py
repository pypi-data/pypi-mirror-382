"""
Main processing module for PDF parsing.
This module integrates all the components to process PDF documents,
extract text and structure, and save the results.
"""

import os
import gc
import io
import re
import sys
import json
import fitz
import torch
import base64
import logging
import requests
import tempfile 
import subprocess
import pdfplumber
import collections
import pytesseract
import numpy as np
from PIL import Image
from pathlib import Path
from .pdf import pdf_to_images
from collections import defaultdict
from openai import OpenAI, AzureOpenAI
from .models import initialize_yolo_model
from typing import Optional, Union, List, Dict, Any
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ServiceRequestError
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter
from docling.datamodel.pipeline_options import PdfPipelineOptions
from azure.ai.documentintelligence import DocumentIntelligenceClient
from docling.document_converter import DocumentConverter, PdfFormatOption

from .box_processing import (nms_merge_boxes, 
                             remove_inner_boxes, 
                             remove_container_boxes, 
                             sort_bounding_boxes, 
                             deduplicate_boxes, 
                             recover_missed_boxes,
                             get_box_class, 
                             remove_contained_bounding_boxes)

from .image_processing import annotate_image, save_annotated_image

from .config import OUTPUT_DIR, IOU_THRESHOLD, TEXT_LABELS, CONTAINER_THRESHOLD, DEFAULT_EMBEDDING_MODEL, TABLE_CLASSIFICATION_SYSTEM_PROMPT, TABLE_SUMMARY_SYSTEM_PROMPT, TABLE_ID_COLUMN_SYSTEM_PROMPT, TABLE_CATEGORIES

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_openai_client(api_key: Optional[str] = None,
                      azure_api_key: Optional[str] = None,
                      api_version: Optional[str] = None,
                      azure_endpoint: Optional[str] = None,
                      azure_endpoint_embedding: Optional[str] = None) -> Union[OpenAI, AzureOpenAI]: 
    """
    Initializes and returns an appropriate OpenAI client (standard or Azure).
    """
    if azure_api_key and api_version and azure_endpoint and azure_endpoint_embedding: 

        logger.info("Initializing AzureOpenAI client for embeddings and table classification.")
        return AzureOpenAI(api_key = azure_api_key, api_version = api_version, azure_endpoint = azure_endpoint, azure_endpoint_embedding = azure_endpoint_embedding)

    elif api_key:
    
        logger.info("Initializing OpenAI client for text embeddings.")
        return OpenAI(api_key=api_key)
    
    else:
    
        raise ValueError("Insufficient credentials provided for OpenAI client.")

class PDFParser: 
    """
    Main class for parsing PDF documents. Optionally performs OCR on extracted elements.
    """

    def __init__(self, 
                 yolo_model_path: Optional[str] = None, 
                 debug_mode: Optional[bool] = False, 
                 container_threshold: Optional[int] = None, 
                 ocr: Optional[bool] = False, 
                 azure_ocr_endpoint: Optional[str] = None, 
                 azure_ocr_key: Optional[str] = None, 
                 hierarchy: Optional[bool] = True,
                 embed: Optional[bool] = False,
                 classify_tables: Optional[bool] = False,
                 table_categories: Optional[dict] = None,
                 table_classification_system_prompt: Optional[str] = None,
                 table_summary_system_prompt: Optional[str] = None,
                 table_id_column_system_prompt: Optional[str] = None,
                 embedding_model: Optional[str] = None,
                 hf_token: Optional[str] = None,
                 hf_endpoint: Optional[str] = None,
                 openai_api_key: Optional[str] = None,
                 azure_openai_api_key: Optional[str] = None,
                 azure_openai_api_version: Optional[str] = None,
                 azure_openai_endpoint: Optional[str] = None,
                 azure_openai_endpoint_embedding: Optional[str] = None): 
        """
        Initialize the PDF Parser.
        
        Args:
            yolo_model_path (str, optional): Path to the YOLO model file.
                If None, uses the default path from config.
            debug_mode (bool, optional): Enable debug mode with additional logging and outputs.
                Defaults to False.
            container_threshold (int, optional): Minimum number of contained boxes required
                to remove a container box. If None, uses the default from config.
            ocr (bool, optional): Enable OCR processing using Azure Document Intelligence.
                Defaults to False. Requires Azure credentials.
            hierarchy (bool, optional): Enable hierarchy generation.
                Defaults to True.
            azure_ocr_endpoint (str, optional): Azure Document Intelligence endpoint URL.
                Required if ocr is True. Defaults to env var AZURE_DOC_INTEL_ENDPOINT.
            azure_ocr_key (str, optional): Azure Document Intelligence API key.
                Required if ocr is True. Defaults to env var AZURE_DOC_INTEL_KEY.
            embed (bool, optional): If True, generate embeddings for extracted text.
                Defaults to False.
            classify_tables (bool, optional): If True, classify tables in the document.
                Defaults to False.
            table_categories (dict, optional): Dictionary of table categories and their descriptions to classify.
                Defaults to TABLE_CATEGORIES.
            table_classification_system_prompt (str, optional): System prompt for table classification.
            table_summary_system_prompt (str, optional): System prompt for table summary generation.
            table_id_column_system_prompt (str, optional): System prompt for table ID column identification.
            embedding_model (str, optional): Name of the OpenAI model for embeddings.
                Defaults to the value in config.
            hf_token (str, optional): Hugging Face API token for embeddings.
                Defaults to env var HF_TOKEN.
            hf_endpoint (str, optional): Hugging Face endpoint URL for embeddings.
                Defaults to env var HF_ENDPOINT.
            openai_api_key (str, optional): API key for standard OpenAI service.
            azure_openai_api_key (str, optional): API key for Azure OpenAI service (for embeddings and table classification).
            azure_openai_api_version (str, optional): API version for Azure OpenAI service.
            azure_openai_endpoint (str, optional): Endpoint URL for Azure OpenAI service for table classification.
            azure_openai_endpoint_embedding (str, optional): Endpoint URL for Azure OpenAI service for text embeddings.
        """

        self.yolo_model = initialize_yolo_model(yolo_model_path)
        self.debug_mode = debug_mode
        self.container_threshold = container_threshold or CONTAINER_THRESHOLD
        self.ocr = ocr
        self.hierarchy = hierarchy
        self.azure_ocr_endpoint = None
        self.azure_ocr_key = None
        self.document_client = None
    
        # --- Embedding settings ---
        self.embed = embed
        self.embedding_model = embedding_model or DEFAULT_EMBEDDING_MODEL

        # --- Hugging Face settings ---
        self.hf_token = hf_token or os.getenv("HF_TOKEN")
        self.hf_endpoint = hf_endpoint or os.getenv("HF_ENDPOINT")

        # --- OpenAI settings ---
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.azure_openai_api_key = azure_openai_api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_openai_api_version = azure_openai_api_version or os.getenv("AZURE_OPENAI_API_VERSION")
        self.azure_openai_endpoint = azure_openai_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_openai_endpoint_embedding = azure_openai_endpoint_embedding or os.getenv("AZURE_OPENAI_ENDPOINT_EMBEDDING")
        self.openai_client = None

        # --- Table classification settings ---
        self.classify_tables = classify_tables
        self.table_categories = table_categories or TABLE_CATEGORIES
        self.table_classification_system_prompt = table_classification_system_prompt or TABLE_CLASSIFICATION_SYSTEM_PROMPT
        self.table_summary_system_prompt = table_summary_system_prompt or TABLE_SUMMARY_SYSTEM_PROMPT
        self.table_id_column_system_prompt = table_id_column_system_prompt or TABLE_ID_COLUMN_SYSTEM_PROMPT

        self.docling_converter = self._initialize_docling_converter()
        
        if debug_mode:
            logging.getLogger().setLevel(logging.DEBUG)
            
        if self.ocr:

            self.azure_ocr_endpoint = azure_ocr_endpoint or os.getenv("AZURE_DOC_INTEL_ENDPOINT")
            self.azure_ocr_key = azure_ocr_key or os.getenv("AZURE_DOC_INTEL_KEY")

            if not self.azure_ocr_endpoint or not self.azure_ocr_key:

                raise ValueError("Azure endpoint and key are required for OCR. "
                                 "Provide them as arguments or set environment variables "
                                 "AZURE_DOC_INTEL_ENDPOINT and AZURE_DOC_INTEL_KEY.")

            try:
            
                self.document_client = DocumentIntelligenceClient(endpoint=self.azure_ocr_endpoint, credential=AzureKeyCredential(self.azure_ocr_key))
                logger.info("Azure Document Intelligence client initialized for OCR.")
            
            except Exception as e:
            
                logger.error(f"Failed to initialize Azure Document Intelligence client: {e}")
                raise ValueError(f"Failed to initialize Azure Document Intelligence client: {e}")
        
        # Validate embedding configuration if enabled
        if self.embed:
            if not self.ocr:
                logger.warning("Embedding is enabled, but OCR is disabled. No text will be available to embed.")
            
            # Check for valid credentials - prioritize Hugging Face
            is_hf_configured = (self.hf_token and self.hf_endpoint)
            is_azure_configured = (self.azure_openai_api_key and self.azure_openai_api_version and self.azure_openai_endpoint_embedding)
            is_openai_configured = bool(self.openai_api_key)
            
            if not is_hf_configured and not is_azure_configured and not is_openai_configured:
                raise ValueError(
                    "Embedding is enabled, but no valid API credentials were provided. "
                    "Please provide either Hugging Face credentials (hf_token, hf_endpoint), "
                    "OpenAI credentials (openai_api_key), or Azure credentials."
                )

        # Prepare for memory-efficient processing if GPU is available 
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    def parse_document(self, pdf_path, output_dir=None, generate_annotations=True, table_categories=None, iou_threshold=None, save_bounding_boxes=True, use_tesseract = False):
        """
        Parse a PDF document, optionally performing OCR.
        
        Args:
            pdf_path (str): Path to the PDF file.
            
            output_dir (str, optional): Directory to save output files.
                If None, uses the default from config.
            
            generate_annotations (bool, optional): Whether to generate annotated images.
                Defaults to True.
                        
            iou_threshold (float, optional): Threshold for merging bounding boxes.
                If None, uses the default from config.
            
            save_bounding_boxes (bool, optional): Whether to save individual bounding box images.
                Required for OCR. Defaults to True.

        Returns:
            dict: Dictionary containing the parsed document data.
        """
        def _normalize_page_rotation(src_path: str):
            """
            Create a new PDF where every page is rotated to 0°.
            """

            def _detect_page_rotation(page: pdfplumber.page.Page) -> int:
                """
                Return 0/90/180/270 that would make the page upright.
                Strategy:
                1) Honor the page's /Rotate flag if set.
                2) If 0, fall back to a chars-based heuristic.
                """
                rotation = (page.rotation or 0) % 360
                if rotation in (90, 180, 270):
                    return rotation    
                
                chars = page.chars or []
                if not chars:
                    return 0
            
                upright_flags = [bool(c.get("upright", True)) for c in page.chars]
                upright_ratio = sum(upright_flags) / len(upright_flags)

                if upright_ratio < 0.3:
                    return 90

                return 0
            
            # Rotations per page
            rotations = []
            with pdfplumber.open(src_path) as pdf:
                for page in pdf.pages:
                    rotations.append(_detect_page_rotation(page))

            if not any(rotations):
                return src_path  # Nothing to change
                
            # Create a temporary file path for the corrected PDF
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_f:
                fixed_pdf_path = temp_f.name
            
            src = fitz.open(src_path)
            dst = fitz.open()
            try:
                for i, need in enumerate(rotations):
                    src_page = src[i]
                    src_rect = src_page.rect
                    
                    w, h = (src_rect.height, src_rect.width) if need in (90, 270) else (src_rect.width, src_rect.height)

                    dst_page = dst.new_page(width=w, height=h)
                    dst_page.show_pdf_page(dst_page.rect, src, i, rotate=need)

                dst.save(fixed_pdf_path, garbage=4, deflate=True)
            finally:
                src.close()
                dst.close()
            
            return fixed_pdf_path

        temp_pdf_path = None

        try:
            original_pdf_path = pdf_path
            pdf_path = _normalize_page_rotation(pdf_path)

            if pdf_path != original_pdf_path:
                temp_pdf_path = pdf_path
                logger.info(f"Rotation detected. Processing temporary file: {temp_pdf_path}")
            else:
                logger.info("No rotation detected.")

            if self.ocr and not save_bounding_boxes: 
                
                logger.warning("OCR requires saving bounding boxes. Setting save_bounding_boxes=True.")
                save_bounding_boxes = True

            # Set defaults from config if not provided
            output_dir = output_dir or OUTPUT_DIR
            iou_threshold = iou_threshold or IOU_THRESHOLD

            if table_categories is None: 
                table_categories = self.table_categories

            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Extract filename without extension for output naming
            file_basename = Path(pdf_path).stem

            # Call docling via subprocess
            docling_results = self._run_docling_parser(pdf_path)
            docling_tables = docling_results.get('tables', []) if docling_results else []
            if not docling_results:
                logger.error("Docling pre-parsing failed. 'Good' tables will not be processed.")

            # Include document structure information
            structure_info = {}
            # Include parsed tables information (docling only)
            parsed_tables = {}

            try:

                logger.info(f"Converting PDF to images for layout analysis: {pdf_path}")
                pages, scale_factors = pdf_to_images(pdf_path)

                logger.info("Detecting layout elements with YOLO model...")
                processed_pages = self._process_pages_improved(pages, iou_threshold)
                
                # Table Parsing Step
                with pdfplumber.open(pdf_path) as pdf:                
                    
                    # --- Save screenshots and process tables found by docling ---
                    if docling_tables:
                        self._save_table_screenshots(docling_tables, pages, pdf, scale_factors, output_dir)
                        logger.info(f"Processing {len(docling_tables)} tables found by docling...")
                        
                        page_table_counts = defaultdict(int) 

                        for docling_table in docling_tables:
                            prov = docling_table.get('prov', [{}])[0]
                            page_num = prov.get('page_no') - 1      # Docling provides a 1-indexed page number
                            bbox_dict = prov.get('bbox')

                            if not all([page_num is not None, bbox_dict]):
                                logger.warning(f"Skipping a docling table due to missing 'page_no' or 'bbox' in its provenance data.")
                                continue

                            if not (0 <= page_num < len(pdf.pages)):
                                logger.warning(
                                    f"Skipping a docling table because its page number ({page_num}) is outside the range "
                                    f"of pages found by pdfplumber (1-{len(pdf.pages)})."
                                )
                                continue
                            
                            # Use a page-specific counter for a correct table_id
                            table_index_on_page = page_table_counts[page_num]
                            table_id = f"{page_num}_table_{table_index_on_page}"
                            page_table_counts[page_num] += 1

                            pdf_page = pdf.pages[page_num]
                            scale_factor = scale_factors.get(page_num, 1.0)

                            # Classify the table structure
                            plumber_bbox = self._get_plumber_bbox_from_docling(bbox_dict, pdf_page)

                            structure_type = self._classify_table_structure(plumber_bbox, pdf_page)
                            logger.info(f"Docling table on page {page_num} classified as '{structure_type}'.")

                            if structure_type == 'good':

                                try:

                                    logger.info(f"Processing 'good' table {table_id} with docling hierarchical parser.")

                                    grid = self._construct_table_grid(docling_table)
                                    tree = self._build_table_tree(grid, pdf_page)
                                    
                                    # Convert docling coordinates to YOLO format
                                    plumber_bbox = self._get_plumber_bbox_from_docling(bbox_dict, pdf_page)
                                    if plumber_bbox:
                                        # Convert PDF points to pixels and to YOLO format [x, y, w, h]
                                        x1, y1, x2, y2 = plumber_bbox
                                        pixel_x1 = x1 * scale_factor
                                        pixel_y1 = y1 * scale_factor
                                        pixel_x2 = x2 * scale_factor
                                        pixel_y2 = y2 * scale_factor
                                        pixel_w = pixel_x2 - pixel_x1
                                        pixel_h = pixel_y2 - pixel_y1
                                        yolo_coordinates = [int(pixel_x1), int(pixel_y1), int(pixel_w), int(pixel_h)]
                                    else:
                                        yolo_coordinates = [0, 0, 0, 0]  # Fallback
                                    
                                    parsed_tables[table_id] = {
                                        "parsed_data": tree, 
                                        "coordinates": yolo_coordinates
                                    }

                                except Exception as e:
                                    logger.error(f"Failed to process 'good' table {table_id} with hierarchical parser: {e}", exc_info=self.debug_mode)
                                    # Add a placeholder with the error message so the table isn't lost
                                    parsed_tables[table_id] = {"parsed_data": f"Error: Failed to build tree - {e}", "coordinates": bbox_dict}

                            else: # 'bad'

                                logger.info(f"Processing 'bad' table {table_id} with vision pipeline.")

                                if plumber_bbox:

                                    pixel_bbox = (
                                        plumber_bbox[0] * scale_factor,
                                        plumber_bbox[1] * scale_factor,
                                        plumber_bbox[2] * scale_factor,
                                        plumber_bbox[3] * scale_factor
                                    )

                                    table_image = pages[page_num].crop(pixel_bbox)
                                    parsed_string = self._parse_bad_table_with_llm(table_image)
                                    
                                    # Convert to YOLO format [x, y, w, h]
                                    pixel_x1, pixel_y1, pixel_x2, pixel_y2 = pixel_bbox
                                    pixel_w = pixel_x2 - pixel_x1
                                    pixel_h = pixel_y2 - pixel_y1
                                    yolo_coordinates = [int(pixel_x1), int(pixel_y1), int(pixel_w), int(pixel_h)]
                                    
                                    parsed_tables[table_id] = {
                                        "parsed_data": parsed_string, 
                                        "coordinates": yolo_coordinates
                                    }

                                else:
                                    parsed_tables[table_id] = {"parsed_data": "Error: Could not process bbox.", "coordinates": bbox_dict}

                    # Generate annotations if requested
                    if generate_annotations: 
                        
                        logger.info("Generating annotated images...")
                        annotations_dir = os.path.join(output_dir, "annotations")
                        self._generate_annotations(pages, processed_pages, annotations_dir)
                        
                    # Save individual bounding boxes if requested
                    if save_bounding_boxes: 
                        
                        logger.info("Saving individual bounding box images...")
                        boxes_dir = os.path.join(output_dir, "boxes")
                        self._save_bounding_boxes(processed_pages, boxes_dir)
            
                    # --- Structure Classification Step ---
                    logger.info("Building structure and classifying tables...")
                    for page_num, page_content in processed_pages.items(): 

                        if page_num >= len(pdf.pages):
                            logger.warning(f"Skipping page {page_num} as it is out of bounds for the PDF.")
                            continue

                        page_structure = {}
                        pdf_page = pdf.pages[page_num] # pdfplumber page object
                        scale_factor = scale_factors.get(page_num, 1.0) # Get the correct scale factor
                        
                        for label, element in page_content.items():

                            element_data = {
                                'coordinates': element['coordinates'],
                                'class': get_box_class(label),
                                'confidence': element['confidence']
                            }

                            # If the element is a table, classify its structure
                            if element_data['class'] == 'table':
                                element_data['structure_type'] = 'undetermined_by_yolo'

                            page_structure[label] = element_data
                            
                        structure_info[str(page_num)] = page_structure

            except Exception as e:
                logger.error(f"Failed during main parsing and classification phase: {e}", exc_info=self.debug_mode)
                return None # Exit if initial parsing fails
                    
            # Save results to file
            result_path = os.path.join(output_dir, "boxes.json")
            with open(result_path, 'w', encoding='utf-8') as f: 
                json.dump(structure_info, f, ensure_ascii = False, indent = 2)
            logger.info(f"Base structure with table classifications saved to {result_path}")

            # Save parsed table data, which will be augmented later
            tables_path = os.path.join(output_dir, "tables.json")
            with open(tables_path, 'w', encoding='utf-8') as f:
                json.dump(parsed_tables, f, indent=4)
            logger.info(f"Parsed table data saved to {tables_path}")
            
            # --- Hierarchy Step ---
            if self.hierarchy: 

                unclustered_content = {page:{k:None for k, v in boxes.items()} for page, boxes in structure_info.items()}

                # Flatten content, adding page notation to tag name 
                flattened_doc_texts = {}
                for page, page_content in unclustered_content.items(): 
                    
                    for tag, content in page_content.items(): 
                            
                            if (not content) or (content.strip() != ''):
                                
                                flattened_doc_texts[f"{page}_{tag}"] = content

                # Establish hierarchy by assigning heading to each chunk 
                heading = None
                chunks = {}
                order = 0
                for tag, text in flattened_doc_texts.items(): 

                    page = tag.split('_')[0]

                    if 'title' in tag: 

                        chunks[tag] = {'heading':heading, 'page':page, 'order':order}
                        heading = tag

                    else: 

                        chunks[tag] = {'heading':heading, 'page':page, 'order':order}
                    
                    order += 1

                # Save hierarchy to file
                hierarchy_path = os.path.join(output_dir, "hierarchy.json")
                with open(hierarchy_path, 'w', encoding='utf-8') as f:
                    json.dump(chunks, f)
                
                logger.info(f"Hierarchy saved to {hierarchy_path}")
            
            # --- OCR Step ---
            sorted_doc_texts = None
            if self.ocr: 

                logger.info(f"Starting OCR process using {'Tesseract' if use_tesseract else 'Azure'}...")
                
                try:
                    
                    sorted_doc_texts = self._run_ocr(output_dir, result_path, use_tesseract)
                    ocr_path = os.path.join(output_dir, "text.json")
                    with open(ocr_path, 'w', encoding = 'utf-8') as f: 
                        json.dump(sorted_doc_texts, f, ensure_ascii = False, indent = 2)
                            
                    logger.info("OCR processing finished successfully.")
                
                except Exception as e: 

                    logger.error(f"OCR processing failed: {e}", exc_info=self.debug_mode)

            # --- Embedding Step ---
            embeddings_results = None
            if self.embed and sorted_doc_texts:
                logger.info("Starting embedding generation...")
                try:
                    embeddings_results = self._generate_embeddings(sorted_doc_texts)
                    embedding_path = os.path.join(output_dir, "embeddings.json")
                    with open(embedding_path, 'w', encoding='utf-8') as f:
                        json.dump(embeddings_results, f, ensure_ascii=False, indent=2)
                    logger.info(f"Embedding generation successful. Saved to {embedding_path}")
                except Exception as e:
                    logger.error(f"Embedding generation failed: {e}", exc_info=self.debug_mode)
            elif self.embed:
                logger.warning("Embedding was enabled, but no text was extracted. Skipping embedding step.")
                
            # --- Table Classification Step ---
            if self.classify_tables and parsed_tables:
                logger.info("Starting table classification and summarization...")
                try:

                    content_classifications, failed_count, table_summaries, failed_summaries, table_id_columns, failed_id_columns = self._classify_and_summarize_table_content(parsed_tables, table_categories)

                    # Augment the parsed_tables dictionary with content classifications
                    for table_id, classification in content_classifications.items():
                        
                        if table_id in parsed_tables:
                            parsed_tables[table_id]['content_classification'] = classification
                        else:
                            logger.warning(f"Content classification found for {table_id}, but it was not in the initially parsed tables.")

                    # Augment the parsed_tables dictionary with table summaries
                    for table_id, summary in table_summaries.items():
                        if table_id in parsed_tables:
                            parsed_tables[table_id]['summary'] = summary
                        else:
                            logger.warning(f"Table summary found for {table_id}, but it was not in the initially parsed tables.")

                    # Augment the parsed_tables dictionary with table id columns
                    for table_id, id_columns in table_id_columns.items():
                        if table_id in parsed_tables:
                            parsed_tables[table_id]['identifier_columns'] = id_columns
                        else:
                            logger.warning(f"Table id columns found for {table_id}, but it was not in the initially parsed tables.")

                    # Re-save the augmented tables.json
                    with open(tables_path, 'w', encoding='utf-8') as f:
                        json.dump(parsed_tables, f, indent=4)

                    if failed_count > 0:
                        logger.warning(f"Table content classification partially successful. Results saved to {tables_path}")
                    else:
                        logger.info(f"Table content classification successful. Results augmented in {tables_path}")

                    if failed_summaries > 0:
                        logger.warning(f"Table summary generation partially successful. Results saved to {tables_path}")
                    else:
                        logger.info(f"Table summary generation successful. Results augmented in {tables_path}")

                    if failed_id_columns > 0:
                        logger.warning(f"Table id column identification partially successful. Results saved to {tables_path}")
                    else:
                        logger.info(f"Table id column identification successful. Results augmented in {tables_path}")

                except Exception as e:
                    logger.error(f"Table classification failed with an unexpected error: {e}", exc_info=self.debug_mode)

            elif self.classify_tables:
                logger.warning("Table classification was enabled, but no tables were found to classify. Skipping classification step.")

            # Clean up to free memory
            self._cleanup_images(pages)
            self._cleanup_images(processed_pages)

            gc.collect()
            if torch.cuda.is_available(): 

                torch.cuda.empty_cache()
        
            result = {
                'structure': structure_info,
                'text': sorted_doc_texts,
                'hierarchy': chunks if self.hierarchy else None,
                'embeddings': embeddings_results,
                'tables': parsed_tables
            }

            if temp_pdf_path and os.path.exists(temp_pdf_path):
                try:
                    os.unlink(temp_pdf_path)
                    logger.info(f"Cleaned up temporary rotated PDF file: {temp_pdf_path}")
                except Exception as e:
                    logger.warning(f"Could not remove temporary file {temp_pdf_path}: {e}")

            return result
        
        finally:

            if temp_pdf_path and os.path.exists(temp_pdf_path):
                try:
                    os.unlink(temp_pdf_path)
                    logger.info(f"Cleaned up temporary rotated PDF file: {temp_pdf_path}")
                except Exception as e:
                    logger.warning(f"Could not remove temporary file {temp_pdf_path}: {e}")

    def _initialize_docling_converter(self):
        """
        Initialize the Docling document converter with OCR disabled and robust error handling.
        """
        try:
            artifacts = os.environ.get("DOCLING_ARTIFACTS_PATH")
            if not artifacts:
                raise RuntimeError("DOCLING_ARTIFACTS_PATH is not set (env_config should have set it).")

            opts = PdfPipelineOptions(
                do_ocr=False,
                do_table_structure=True,
                do_picture_description=False,
                do_picture_classification=False,
                do_code_formula=False,
                artifacts_path=artifacts
            )

            converter = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)})

            logger.info("Docling converter initialized successfully with OCR disabled. Artifacts: %s", artifacts)
            return converter

        except Exception as e:
            logger.error(f"Failed to initialize Docling converter: {e}", exc_info=getattr(self, "debug_mode", False))
            return None

    def _run_docling_parser(self, pdf_path: str) -> Optional[dict]:
        """
        Runs docling parsing directly (no subprocess needed).
        """
        if not self.docling_converter:
            logger.error("Docling converter not initialized.")
            return None

        try:
            logger.info(f"Running docling parser on {pdf_path}...")
            
            # Convert PDF using docling
            docling_doc = self.docling_converter.convert(pdf_path).document
            
            # Convert to dictionary
            doc_dict = docling_doc.model_dump()
            
            logger.info(f"Docling parsing completed successfully. Found {len(doc_dict.get('tables', []))} tables.")
            return doc_dict
            
        except Exception as e:
            logger.error(f"Docling parsing failed: {e}", exc_info=self.debug_mode)
            return None

    def _get_plumber_bbox_from_docling(self, docling_bbox: dict, pdf_page):
        """
        Converts a docling bbox (bottom-left origin) to a pdfplumber bbox (top-left origin).
        """
        coord_origin = str(docling_bbox.get('coord_origin', '')).upper()
        page_height = pdf_page.height
        
        if 'BOTTOMLEFT' in coord_origin:
            return (
                docling_bbox['l'], 
                page_height - docling_bbox['t'], 
                docling_bbox['r'], 
                page_height - docling_bbox['b']
            )
        elif 'TOPLEFT' in coord_origin:
             return (docling_bbox['l'], docling_bbox['t'], docling_bbox['r'], docling_bbox['b'])
        else:
            logger.warning(f"Unknown coord_origin '{docling_bbox.get('coord_origin')}' for docling table.")
            return None
            
    def _save_table_screenshots(self, docling_tables, page_images, pdfplumber_pdf, scale_factors, output_dir):
        """
        Saves screenshots of tables found by docling.
        """
        screenshots_dir = Path(output_dir) / "table_screenshots"
        screenshots_dir.mkdir(exist_ok=True)
        logger.info(f"Saving table screenshots to: {screenshots_dir}")

        page_table_counts = defaultdict(int)
        
        for table in docling_tables:
            prov = table.get('prov', [{}])[0]
            page_num = prov.get('page_no') - 1
            bbox_dict = prov.get('bbox')

            if not all([page_num is not None, bbox_dict]):
                continue
            
            if page_num not in page_images:
                continue

            # Use a page-specific counter for a correct table_id
            table_index_on_page = page_table_counts[page_num]
            table_id = f"{page_num}_table_{table_index_on_page}"
            page_table_counts[page_num] += 1

            pdf_page = pdfplumber_pdf.pages[page_num]
            page_image = page_images[page_num]
            scale_factor = scale_factors.get(page_num, 1.0)

            plumber_bbox = self._get_plumber_bbox_from_docling(bbox_dict, pdf_page)
            if not plumber_bbox:
                continue

            # Scale the PDF point coordinates to image pixel coordinates for cropping
            pixel_bbox = (
                plumber_bbox[0] * scale_factor,
                plumber_bbox[1] * scale_factor,
                plumber_bbox[2] * scale_factor,
                plumber_bbox[3] * scale_factor
            )

            try:
                table_screenshot = page_image.crop(pixel_bbox)
                screenshot_path = screenshots_dir / f"{table_id}.png"
                table_screenshot.save(screenshot_path)
                logger.debug(f"Saved screenshot for table {table_id} on page {page_num} to {screenshot_path}")
            except Exception as e:
                logger.error(f"Failed to save screenshot for table {table_id} on page {page_num}: {e}", exc_info=self.debug_mode)

    def _classify_and_summarize_table_content(self, parsed_tables, table_categories):
        """
        Classifies tables using their parsed data. For 'good' tables, it uses the
        JSON tree structure. For 'bad' tables, it uses the string from the vision model.
        """
        if not self.azure_openai_endpoint or not self.azure_openai_api_key:
            raise ValueError("The 'azure_openai_endpoint' and 'azure_openai_api_key' must be provided for table classification.")

        if not self.table_classification_system_prompt or not self.table_summary_system_prompt or not self.table_id_column_system_prompt:
            raise ValueError("The 'table_classification_system_prompt', 'table_summary_system_prompt', and 'table_id_column_system_prompt' must be provided for table classification.")

        headers = {"Content-Type": "application/json", "api-key": self.azure_openai_api_key}
        
        table_classifications = {}
        found_tables = bool(parsed_tables)
        failed_classifications = 0

        table_summaries = {}
        failed_summaries = 0

        table_id_columns = {}
        failed_id_columns = 0
        
        # Iterate directly over the parsed_tables dictionary
        for table_id, table_data in parsed_tables.items():
            try:
                parsed_data = table_data.get('parsed_data')
                
                text_to_classify = ""
                # Check the type of parsed_data to decide how to format it
                if isinstance(parsed_data, dict):
                    # For 'good' tables, convert the JSON tree to a string
                    text_to_classify = json.dumps(parsed_data, indent=2)
                elif isinstance(parsed_data, str):
                    # For 'bad' tables or error messages, use the string directly
                    text_to_classify = parsed_data
                
                if not text_to_classify or not text_to_classify.strip():
                    logger.warning(f"No content to classify for table {table_id}. Skipping content classification.")
                    failed_classifications += 1
                    continue
                
                # Table Classification
                TABLE_CLASSIFICATION_USER_PROMPT = f"""[TABLE_TEXT]\n{text_to_classify}\n\n[CATEGORIES]\n{table_categories}"""
                payload_1 = {
                    "messages": [{"role": "system", "content": [{"type": "text", "text": self.table_classification_system_prompt}]}, {"role": "user", "content": [{"type": "text", "text": TABLE_CLASSIFICATION_USER_PROMPT}]}],
                    "temperature": 0.7
                }
                
                response_1 = requests.post(self.azure_openai_endpoint, headers = headers, json = payload_1)
                response_1.raise_for_status()
                response_json_1 = response_1.json()
                output_classification = response_json_1['choices'][0]['message']['content'].strip()

                try:
                    output_json = json.loads(output_classification)
                    table_classifications[table_id] = output_json
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse API JSON response for table {table_id}. Response: {output_classification}", exc_info=self.debug_mode)
                    failed_classifications += 1

                # Table Summary Generation
                TABLE_SUMMARY_USER_PROMPT = f"""[TABLE_TEXT]\n{text_to_classify}"""
                payload_2 = {
                    "messages": [{"role": "system", "content": [{"type": "text", "text": self.table_summary_system_prompt}]}, {"role": "user", "content": [{"type": "text", "text": TABLE_SUMMARY_USER_PROMPT}]}],
                    "temperature": 1.0
                }
                
                response_2 = requests.post(self.azure_openai_endpoint, headers = headers, json = payload_2)
                response_2.raise_for_status()
                response_json_2 = response_2.json()
                output_summary = response_json_2['choices'][0]['message']['content'].strip()
                
                table_summaries[table_id] = output_summary

                # Table ID Column Identification
                TABLE_ID_COLUMN_USER_PROMPT = f"""[TABLE_TEXT]\n{text_to_classify}"""
                payload_3 = {
                    "messages": [{"role": "system", "content": [{"type": "text", "text": self.table_id_column_system_prompt}]}, {"role": "user", "content": [{"type": "text", "text": TABLE_ID_COLUMN_USER_PROMPT}]}],
                    "temperature": 0.7
                }

                response_3 = requests.post(self.azure_openai_endpoint, headers = headers, json = payload_3)
                response_3.raise_for_status()
                response_json_3 = response_3.json()
                output_id_columns = response_json_3['choices'][0]['message']['content'].strip()
                
                try:
                    output_list = json.loads(output_id_columns)
                    table_id_columns[table_id] = output_list
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse API JSON response for table {table_id}. Response: {output_id_columns}", exc_info=self.debug_mode)
                    failed_id_columns += 1

            except requests.exceptions.RequestException as e:
                failed_classifications += 1
                failed_summaries += 1
                failed_id_columns += 1
                error_content = ""
                if e.response is not None:
                    error_content = f" Status Code: {e.response.status_code}, Response: {e.response.text}"
                logger.error(f"HTTP request failed for table {table_id}: {e}{error_content}", exc_info=self.debug_mode)
            except Exception as e:
                logger.error(f"Failed to classify and summarize content for table {table_id}: {e}", exc_info=self.debug_mode)
                failed_classifications += 1
                failed_summaries += 1
                failed_id_columns += 1

        if not found_tables:
            logger.warning("No tables were identified in the document, so no classification was performed.")

        return table_classifications, failed_classifications, table_summaries, failed_summaries, table_id_columns, failed_id_columns

    def _classify_table_structure(self, pdfplumber_bbox, pdf_page):
        """
        Classifies a table's structure as 'good' or 'bad' based on parseability.
        Primary rule: Tables with multiple text lines in a single cell are bad.
        This implementation is very conservative and only flags obvious multi-line content.
        """
        try:
            # Ensure the bounding box is valid before cropping
            if not all(isinstance(c, (int, float)) for c in pdfplumber_bbox) or len(pdfplumber_bbox) != 4:
                logger.warning(f"Invalid bounding box received for structure classification: {pdfplumber_bbox}")
                return "bad"
            
            table_crop = pdf_page.crop(pdfplumber_bbox)

            # --- Basic Text Presence Check ---
            if not table_crop.chars or len(table_crop.chars) < 10:
                return "bad"

            # --- Try to extract table structure using pdfplumber's table detection ---
            try:
                # Extract tables using pdfplumber's built-in table detection
                tables = table_crop.extract_tables()
                
                if tables and len(tables) > 0:

                    if len(tables) > 1:
                        logger.warning(f"Found multiple tables in one bounding box: {tables}")

                    # Check each table for multi-line cells
                    for table in tables:

                        num_rows = len(table)

                        if num_rows == 2:
                            logger.info(f"Classified as BAD - number of rows is 2: {table[:100]}...")
                            return "bad"

                        num_cells = 0
                        average_lines_per_cell = 0
                        total_lines = 0

                        num_single_line_cells = 0
                        num_multi_line_cells = 0
                        
                        for row in table:
                            for cell in row:
                                if cell and isinstance(cell, str):
                                    num_cells += 1

                                    cell_lines = cell.strip().split('\n')
                                    if len(cell_lines) > 10:
                                        logger.info(f"Classified as BAD - cell has more than 10 lines: {cell[:100]}...")
                                        return "bad"

                                    if len(cell_lines) > 1:
                                        num_multi_line_cells += 1
                                    elif len(cell_lines) == 1:
                                        num_single_line_cells += 1

                                    total_lines += len(cell_lines)

                        average_lines_per_cell = total_lines / num_cells

                        logger.debug(f"Table stats: num_rows={num_rows}, num_non_empty_cells={num_cells}, num_single_line_cells={num_single_line_cells}, num_multi_line_cells={num_multi_line_cells}, average_lines_per_cell={average_lines_per_cell}")

                        if average_lines_per_cell > 2:
                            logger.info(f"Classified as BAD - average lines per cell is greater than 2: {table[:100]}...")
                            return "bad"

                        if average_lines_per_cell > num_rows:
                            logger.info(f"Classified as BAD - average lines per cell is greater than number of rows: {table[:100]}...")
                            return "bad"
                            
                        if num_single_line_cells < num_multi_line_cells:
                            logger.info(f"Classified as BAD - number of single line cells is smaller than number of multi-line cells: {table[:100]}...")
                            return "bad"

                    # If we successfully extracted tables and no multi-line cells found, it's good
                    logger.info(f"Classified as GOOD - No multi-line cells found in extracted table structure")
                    return "good"
                    
                else:
                    logger.info(f"Classified as BAD - no tables extracted")
                    return "bad"

            except Exception as e:
                logger.info(f"Table extraction failed: {e}")
                return "bad"

        except Exception as e:
            logger.error(f"ERROR: An error occurred during table structure classification: {e}", exc_info=self.debug_mode)
            return "bad"
            
    def _construct_table_grid(self, table: dict) -> list[list[dict]]:
        """
        Build a dense table grid from a Docling table object, preserving empty cells.
        - Works whether Docling nested cells under table['data'] or at the top level.
        - Handles both *_idx and *_offset_idx field names.
        - Fills row/col spans with placeholders that point back to the anchor cell.
        - Normalizes bbox values so downstream code won't crash.
        Schema guarantees: every grid[r][c] is a dict.
        """
        def _normalize_docling_grid(grid):
            if not grid:
                return []
            out = []
            for row in grid:
                new_row = []
                for cell in (row or []):
                    if isinstance(cell, dict):
                        c = dict(cell)
                    elif cell is None:
                        c = {"text": "", "is_placeholder": True}
                    else:
                        c = {"text": str(cell), "is_placeholder": False}
                    c.setdefault("text", "")
                    c.setdefault("is_placeholder", c.get("text", "") == "")
                    if "bbox" in c and not isinstance(c["bbox"], dict):
                        c.pop("bbox", None)
                    new_row.append(c)
                out.append(new_row)
            return out

        grid = table.get("data", {}).get("grid")
        if grid:
            return _normalize_docling_grid(grid)

    def _build_table_tree(self, docling_table_grid, pdfplumber_page, indent_tolerance=2, cols_to_check=2):
        """
        Builds a tree structure from a reconstructed table grid. This version
        correctly identifies hierarchy based on column-level indentation.
        """
        def _cell_is_header(cell):
            return isinstance(cell, dict) and bool(cell.get("column_header", False))

        def _cell_is_highlighted(pdfplumber_page, cell):
            """
            Checks if a cell is highlighted in a pdfplumber page.
            """
            # cell_bbox: (x0, top, x1, bottom) in pdfplumber coords
            bbox = (cell or {}).get("bbox")
            if not isinstance(bbox, dict):
                return False

            # Accept common key sets; bail safely if missing
            try:
                cx0 = bbox.get("x0"); cx1 = bbox.get("x1")
                ctop = bbox.get("top"); cbottom = bbox.get("bottom")
                if None in (cx0, ctop, cx1, cbottom):
                    return False
            except Exception:
                return False

            def overlap_area(a, b):
                ax0, atop, ax1, abot = a
                bx0, btop, bx1, bbot = b
                ox0, ox1 = max(ax0, bx0), min(ax1, bx1)
                otop, obot = max(atop, btop), min(abot, bbot)
                w, h = max(0, ox1 - ox0), max(0, obot - otop)
                return w * h

            cell_area = max(0.0, (cx1 - cx0) * (cbottom - ctop))

            if cell_area <= 0:
                return False

            for rect in pdfplumber_page.rects:

                if rect.get("non_stroking_color") is None:      # Not filled
                    continue

                rx0, rtop, rx1, rbot = rect["x0"], rect["top"], rect["x1"], rect["bottom"]
                rw, rh = (rx1 - rx0), (rbot - rtop)

                if min(rw, rh) < 1:      # Likely a border
                    continue

                overlap = overlap_area((cx0, ctop, cx1, cbottom), (rx0, rtop, rx1, rbot))
                if overlap / cell_area >= 0.7:
                    return True

            return False

        if not docling_table_grid:
            return []

        pdfplumber_words = pdfplumber_page.extract_words(extra_attrs=["fontname"])

        # Separate header and body rows
        header_rows = []
        body_rows = []
        for row in docling_table_grid:
            
            if not row:
                continue
            non_placeholders = [c for c in row if isinstance(c, dict) and not c.get("is_placeholder")]
            if non_placeholders and all(_cell_is_header(c) for c in non_placeholders):
                header_rows.append([c.get("text","") for c in row if isinstance(c, dict)])
            else:
                body_rows.append(row)
        
        def get_row_features(row, pdfplumber_words, pdfplumber_page):
            """
            Extracts features from a row, including a list of bbox_l values
            for each cell to allow for column-level comparisons.
            """
            summary_keywords = ["total", "subtotal", "summary", "amount due"]

            if not row:
                return {"text": [], "cell_indents": []}

            row_text = []
            cell_indents = []
            cell_is_bold = []
            cell_is_highlighted = []
            cell_is_all_caps = []
            cell_is_summary = []

            for cell in row:
                cell_text = cell.get('text', '')

                if cell.get("is_placeholder", False) or not cell_text.strip():
                    row_text.append(cell_text)  # Preserve original whitespace
                    bbox = cell.get("bbox")
                    indent_l = bbox.get("l", 0) if isinstance(bbox, dict) else 0
                    cell_indents.append(indent_l)
                    cell_is_bold.append(False)
                    cell_is_highlighted.append(False)
                    cell_is_all_caps.append(False)
                    cell_is_summary.append(False)
                    continue
                
                bbox = cell.get("bbox")
                if not isinstance(bbox, dict):
                    # Can't align without bbox; keep row shape and move on
                    row_text.append(cell_text)
                    cell_indents.append(0)
                    cell_is_bold.append(False)
                    cell_is_highlighted.append(False)
                    cell_is_all_caps.append(False)
                    cell_is_summary.append(False)
                    continue

                cell_bbox_l = bbox.get("l", 0)
                cell_bbox_r = bbox.get("r", 0)
                cell_bbox_t = bbox.get("t", 0)
                cell_bbox_b = bbox.get("b", 0)


                pdfplumber_word_matches = []
                docling_center_x = (cell_bbox_l + cell_bbox_r) / 2
                docling_center_y = (cell_bbox_t + cell_bbox_b) / 2

                for word in pdfplumber_words:
                    if word['x0'] <= docling_center_x <= word['x1'] and word['top'] <= docling_center_y <= word['bottom']:
                        pdfplumber_word_matches.append(word)
                
                row_text.append(cell_text)
                cell_indents.append(cell_bbox_l)
                
                if pdfplumber_word_matches:
                    is_b = "bold" in pdfplumber_word_matches[0]['fontname'].lower()
                    cell_is_bold.append(is_b)
                else:
                    cell_is_bold.append(False)

                cell_is_highlighted.append(_cell_is_highlighted(pdfplumber_page, cell))
                cell_is_all_caps.append(cell_text.isupper())
                cell_is_summary.append(any(summary_keyword in cell_text.lower() for summary_keyword in summary_keywords))

            row_is_highlighted = any(cell_is_highlighted)
            row_is_bold = any(cell_is_bold)
            row_is_all_caps = all(cell_is_all_caps)
            row_is_summary = any(cell_is_summary)
            
            return {
                "text": row_text,
                "cell_indents": cell_indents,
                "highlighted": row_is_highlighted,
                "bold": row_is_bold,
                "caps": row_is_all_caps,
                "is_summary": row_is_summary
            }
        
        def is_center_aligned_column(docling_table_grid: List[List[Dict[str, Any]]], col_idx: int, indent_tolerance=2) -> bool:
            """
            Returns True if *all usable body rows* in the given column are center-aligned,
            and the normalized text lengths are not all identical.
            """
            def _cell_is_merged(cell: Dict[str, Any]) -> bool:

                sc = cell.get("start_col_offset_idx", None)
                ec = cell.get("end_col_offset_idx", None)
                sr = cell.get("start_row_offset_idx", None)
                er = cell.get("end_row_offset_idx", None)
                try:
                    col_span = (ec - sc) if (sc and ec) else 1
                    row_span = (er - sr) if (sr and er) else 1
                except Exception:
                    col_span, row_span = 1, 1

                return (col_span and col_span > 1) or (row_span and row_span > 1)

            centers: List[float] = []
            widths: List[float] = []
            lengths: List[int] = []

            for row in docling_table_grid:

                if col_idx < 0 or col_idx >= len(row):
                    return False
                
                cell = row[col_idx]
                if not isinstance(cell, dict):
                    return False
                if cell.get("is_placeholder"):
                    continue

                # Only proceed if bbox exists
                bbox = cell.get("bbox")
                if not isinstance(bbox, dict):
                    continue

                if _cell_is_header(cell) or _cell_is_merged(cell):
                    continue

                text = cell.get("text", "")
                
                l, r = bbox.get("l"), bbox.get("r")

                if l is None or r is None:
                    # cannot assess without horizontal bbox
                    return False

                cx = (float(l) + float(r)) / 2
                w = float(r - l)

                centers.append(cx)
                widths.append(w)
                lengths.append(text)

            # If no usable body cells, don't call it center-aligned.
            if not centers:
                return False

            # All rows must agree: we interpret that as all *usable* rows agreeing.
            ref_center = np.median(centers)

            # Every usable row must fall within tolerance
            all_within = all(abs(c - ref_center) <= indent_tolerance for c in centers)
            if not all_within:
                return False

            # Text lengths must NOT all be the same
            all_same_length = (len(set(lengths)) == 1)
            if all_same_length:
                return False

            return True

        def create_node(features):
            """Creates a tree node from extracted row features."""
            return {
                "row_data": features["text"],
                "children": []
            }

        tree_roots = []
        parent_stack = []

        for row in body_rows:
            if not row:
                continue
                
            current_features = get_row_features(row, pdfplumber_words, pdfplumber_page)

            new_node = create_node(current_features)

            while parent_stack:
                parent_features = parent_stack[-1]['features']
                is_child = False
                
                # --- Start: Hierarchy Decision Logic ---
                p_is_highlighted = parent_features['highlighted']
                c_is_highlighted = current_features['highlighted']
                p_is_bold = parent_features['bold']
                c_is_bold = current_features['bold']
                p_is_caps = parent_features['caps']
                c_is_caps = current_features['caps']

                c_is_summary = current_features['is_summary']
                if c_is_summary:
                    is_child = False
                else:
                    # 1. Veto Rule: Style Promotion
                    # A more styled row (e.g., bold) cannot be a child of a less styled one (e.g., plain)
                    is_promoted = (c_is_highlighted and not p_is_highlighted) or (c_is_bold and not p_is_bold and not c_is_highlighted)

                    if is_promoted:
                        is_child = False
                    else:
                        # 2. Primary Check: Indentation
                        indent_decision = "ambiguous"
                        min_len = min(len(current_features["cell_indents"]), len(parent_features["cell_indents"]), cols_to_check)
                        
                        for col_idx in range(min_len):
                            if is_center_aligned_column(docling_table_grid, col_idx):
                                continue

                            parent_indent = parent_features["cell_indents"][col_idx]
                            current_indent = current_features["cell_indents"][col_idx]
                            
                            if current_indent > parent_indent + indent_tolerance:
                                indent_decision = "child"
                                break
                            if current_indent < parent_indent - indent_tolerance:
                                indent_decision = "not_child"
                                break
                        
                        if indent_decision == "child":
                            is_child = True
                        elif indent_decision == "not_child":
                            is_child = False
                        else:
                            # 3. Tie-breaker: Style Demotion
                            # Check for style demotion in order of importance
                            if p_is_highlighted and not c_is_highlighted:
                                is_child = True
                            elif p_is_highlighted == c_is_highlighted:
                                if p_is_bold and not c_is_bold:
                                    is_child = True
                                elif p_is_bold == c_is_bold:
                                    if p_is_caps and not c_is_caps:
                                        is_child = True

                # --- End: Hierarchy Decision Logic ---

                if is_child:
                    break
                else:
                    parent_stack.pop()

            if not parent_stack:
                tree_roots.append(new_node)
            else:
                # Access the 'node' dictionary to append the child
                parent_stack[-1]['node']["children"].append(new_node)
            
            parent_stack.append({"features": current_features, "node": new_node})
        
        return {"headers": header_rows, "body": tree_roots}

    def _parse_bad_table_with_llm(self, table_image: Image.Image) -> Optional[str]:
        """
        Parses a 'bad' table by sending its image to a vision model.
        """
        if not self.azure_openai_endpoint or not self.azure_openai_api_key:
            logger.error("Azure OpenAI credentials for vision model are not configured.")
            return "Error: Vision model credentials not configured."

        try:
            buffered = io.BytesIO()
            table_image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

            headers = {"Content-Type": "application/json", "api-key": self.azure_openai_api_key}
            
            # This is the detailed system prompt from your notebook
            system_prompt = """
            You are a table parsing engine.
            Your task is to convert a table image into a structured string representation while preserving, as faithfully as possible, the original formatting and hierarchy cues of the table.

            [INPUT]  
              [TABLE_IMAGE] - a screenshot image of the table  

            [TASK]  
              • Reconstruct the table as text, row by row and column by column.  
              • Preserve formatting cues that indicate hierarchy, such as:  
                - Indentation (use leading spaces or tabs exactly as they appear).  
                - Bold text (wrap words in **double asterisks**).  
                - ALL CAPS text.  
                - Underlines, dashes, or separators.  
              • Do **not** infer or add any content that is not visible in the image.  
              • Keep the column structure intact using spacing, pipes (`|`), or another consistent delimiter.  
              • The goal is to produce a **faithful textual replica** of the table that preserves the hierarchy-defining features.  

            [OUTPUT]  
              Output only the reconstructed table text.  
              Do not include explanations, comments, or metadata.  

            [RULES]  
              - Never invent text, numbers, or formatting.  
              - Never summarize or interpret — only transcribe and preserve formatting.  
              - If indentation exists, preserve the same relative spacing.  
              - If bold or styled text exists, reproduce it with the agreed markers.  
              - Every visible element in the table must appear in the output, even if it looks redundant.  
              - Output must be plain text only.
            """

            payload = {
                "messages": [
                    {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Here is the image of the table:"},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                        ]
                    }
                ],
                "temperature": 0.7, # Lower temperature for more deterministic output
                "max_tokens": 4000
            }

            response = requests.post(self.azure_openai_endpoint, headers=headers, json=payload)

            if response.status_code != 200:
                logger.error(f"Azure vision API call failed with status code {response.status_code}.")
                logger.error(f"Response Body: {response.text}")
                response.raise_for_status() # Raise the exception after logging

            response_json = response.json()

            if 'choices' not in response_json or not response_json['choices']:
                logger.error(f"Invalid response from Azure vision API: 'choices' key is missing or empty. Response: {response_json}")
                return "Error: Invalid API response."
            
            return response_json['choices'][0]['message']['content'].strip()

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request to Azure vision model failed: {e}", exc_info=self.debug_mode)
            return f"Error: API call failed - {e}"
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse response from Azure vision model: {e}", exc_info=self.debug_mode)
            return f"Error: Invalid API response - {e}"
        except Exception as e:
            logger.error(f"An unexpected error occurred during bad table parsing: {e}", exc_info=self.debug_mode)
            return f"Error: An unexpected error occurred - {e}"

    def _generate_embeddings(self, sorted_doc_texts): 
        """
        Generate embeddings for the given text blocks using a batch approach.
        Prioritize Hugging Face, falls back to OpenAI/Azure if needed.
        """
        
        texts_to_embed = []
        text_keys = []
        for page_num, page_content in sorted_doc_texts.items(): 

            for element_id, text in page_content.items(): 

                if text and not text.isspace(): 

                    texts_to_embed.append(text.replace("\n", " "))
                    text_keys.append((page_num, element_id))
        
        embedding_vectors = []
        if texts_to_embed: 
            logger.info(f"Generating embeddings for {len(texts_to_embed)} text block(s).")
            
            # Try Hugging Face first
            if self.hf_token and self.hf_endpoint:
                try:
                    embedding_vectors = self._generate_hf_embeddings(texts_to_embed)
                    logger.info("Successfully generated embeddings using Hugging Face.")
                except Exception as e:
                    logger.error(f"Hugging Face embedding generation failed: {e}", exc_info=self.debug_mode)
                    # Fall back to OpenAI/Azure
                    embedding_vectors = self._generate_openai_embeddings(texts_to_embed)
            else:
                # Use OpenAI/Azure directly
                embedding_vectors = self._generate_openai_embeddings(texts_to_embed)

        embeddings_map = {key: vec for key, vec in zip(text_keys, embedding_vectors)}

        # Reconstruct the results dictionary, preserving the original structure
        final_embeddings = {}
        for page_num, page_content in sorted_doc_texts.items(): 

            final_embeddings[page_num] = {}
            for element_id, text in page_content.items(): 
            
                key = (page_num, element_id)
                final_embeddings[page_num][element_id] = embeddings_map.get(key)
        
        return final_embeddings

    def _generate_hf_embeddings(self, texts_to_embed):
        """
        Generate embeddings using Hugging Face API with batching to handle size limits.
        
        Args:
            texts_to_embed (list): List of text strings to embed.
            
        Returns:
            list: List of embedding vectors.
        """
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json"
        }
        
        # Batch size limit for Hugging Face endpoint
        batch_size = 32
        all_embeddings = []
        
        # Process texts in batches
        for i in range(0, len(texts_to_embed), batch_size):
            batch_texts = texts_to_embed[i:i + batch_size]
            
            # Prepare payload for this batch
            payload = {
                "inputs": batch_texts,
                "options": {
                    "wait_for_model": True
                }
            }
            
            try:
                response = requests.post(
                    self.hf_endpoint,
                    headers=headers,
                    json=payload,
                    timeout=120   # Timeout for large requests
                )

                response.raise_for_status()
                
                result = response.json()
                
                # Handle different response formats from Hugging Face
                if isinstance(result, list):
                    # Direct list of embeddings
                    batch_embeddings = result
                elif isinstance(result, dict) and "embeddings" in result:
                    # Response with embeddings key
                    batch_embeddings = result["embeddings"]
                elif isinstance(result, dict) and "data" in result:
                    # Response with data key (similar to OpenAI format)
                    batch_embeddings = [item["embedding"] for item in result["data"]]
                else:
                    raise ValueError(f"Unexpected response format from Hugging Face API: {result}")
                
                all_embeddings.extend(batch_embeddings)
                logger.debug(f"Processed batch {i//batch_size + 1}/{(len(texts_to_embed) + batch_size - 1)//batch_size} with {len(batch_embeddings)} embeddings")
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Hugging Face API request failed for batch {i//batch_size + 1}: {e}", exc_info=self.debug_mode)
                raise
            except (KeyError, IndexError, ValueError) as e:
                logger.error(f"Failed to parse Hugging Face API response for batch {i//batch_size + 1}: {e}", exc_info=self.debug_mode)
                raise
            except Exception as e:
                logger.error(f"Unexpected error during Hugging Face embedding generation for batch {i//batch_size + 1}: {e}", exc_info=self.debug_mode)
                raise
        
        logger.info(f"Successfully generated {len(all_embeddings)} embeddings using Hugging Face in {(len(texts_to_embed) + batch_size - 1)//batch_size} batches.")
        return all_embeddings

    def _generate_openai_embeddings(self, texts_to_embed):
        """
        Generate embeddings using OpenAI/Azure API (fallback method).
        
        Args:
            texts_to_embed (list): List of text strings to embed.
            
        Returns:
            list: List of embedding vectors.
        """
        if not self.openai_client: 
            self.openai_client = get_openai_client(
                api_key=self.openai_api_key,
                azure_api_key=self.azure_openai_api_key,
                api_version=self.azure_openai_api_version,
                azure_endpoint=self.azure_openai_endpoint_embedding
            )

        try: 
            response = self.openai_client.embeddings.create(input=texts_to_embed, model=self.embedding_model)
            embedding_vectors = [item.embedding for item in response.data]
            logger.info(f"Successfully generated {len(embedding_vectors)} embeddings using OpenAI/Azure.")
            return embedding_vectors

        except Exception as e:
            logger.error(f"OpenAI/Azure API call for embeddings failed: {e}", exc_info=self.debug_mode)
            raise
    
    def _get_pdf_page_count(self, pdf_path):
        """Get the number of pages in a PDF file."""
                
        doc = fitz.open(pdf_path)
        page_count = len(doc)
        doc.close()
        
        return page_count
    
    def _process_single_page(self, pages, page_num, iou_threshold): 
        """
        Process a single page of the document.
        
        Args:
            pages (dict): Dictionary containing a single page image.
            page_num (int): Page number being processed.
            iou_threshold (float): Threshold for merging bounding boxes.
            
        Returns:
            dict: Dictionary of processed page elements.
        """
        # Parse document structure with YOLO
        parsed_page = self._parse_document_structure(pages)
        
        # Process parsed page with improved algorithm
        if page_num in parsed_page:
            processed_page = self._process_page_improved(pages, parsed_page[page_num], page_num, iou_threshold)
            return processed_page
        
        return {}
    
    def _cleanup_images(self, data):
        """
        Remove image data from the processed results to free memory.
        
        Args:
            data: Data structure containing images to clean up.
            
        Returns:
            The same data structure with images removed.
        """

        if isinstance(data, dict):

            for key, value in list(data.items()):

                if key == 'image' and isinstance(value, Image.Image):
                    data[key] = None  # Remove the image

                elif isinstance(value, dict):
                    self._cleanup_images(value)

                elif isinstance(value, list):

                    for item in value:

                        if isinstance(item, dict):

                            self._cleanup_images(item)
        return data
    
    def _save_bounding_boxes_for_page(self, page_content, page_dir):
        """
        Save individual bounding box images for a single page.
        
        Args:
            page_content (dict): Dictionary of page elements.
            page_dir (str): Directory to save bounding box images.
        """

        for label, element in page_content.items():

            if 'image' in element:

                # Create a safe filename from the label
                safe_label = label.replace('/', '_').replace('\\', '_')
                image_path = os.path.join(page_dir, f"{safe_label}.png")
                
                # Save the bounding box image
                element['image'].save(image_path)
                
                # Save coordinates as JSON
                coords_path = os.path.join(page_dir, f"{safe_label}_coords.json")
                with open(coords_path, 'w') as f:
                    json.dump({
                        'label': label,
                        'class': get_box_class(label),
                        'coordinates': element['coordinates']
                    }, f, indent=2)
    
    def _parse_document_structure(self, pages): 
        """
        Parse document structure using YOLO.
        
        Args:
            pages (dict): Dictionary of page images.
            
        Returns:
            dict: Dictionary of parsed page elements.
        """

        all_detections = {}
        
        for page_num, page in pages.items():
            
            # Clear PyTorch cache before processing each page
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                
            # Save page temporarily
            page.save('temp_page.jpg')
            
            # Run detection
            det_res = self.yolo_model.predict('temp_page.jpg',
                                               imgsz=1024, 
                                               conf=0.01,  # Using lower confidence threshold
                                               device="cuda:0" if torch.cuda.is_available() else "cpu")
            
            # Remove temporary file
            os.remove('temp_page.jpg')
            
            # Process detection results
            page_detections = {}
            for result in det_res: 

                # Convert the original image array to a PIL Image
                orig_img_array = result.orig_img
                orig_img = Image.fromarray(orig_img_array)
                
                # Get class names
                names = result.names  # Dictionary mapping class indices to class names
                
                # Get the boxes object
                boxes = result.boxes  # Boxes object
                
                # Access bounding box data
                boxes_data = boxes.xyxy  # Torch tensor with shape [num_boxes, 4]

                # Convert boxes data to a NumPy array
                # if isinstance(boxes_data, torch.Tensor):
                boxes_array = boxes_data.cpu().numpy()
                
                # Iterate over each detected box
                num_boxes = boxes_array.shape[0]
                for i in range(num_boxes):

                    box = boxes_array[i]
                    x1, y1, x2, y2 = box[:4]

                    # Get boxes.conf and boxes.cls
                    confidence = float(boxes.conf[i]) 
                    cls = int(boxes.cls[i])
                    
                    # Get class name
                    class_name = names.get(cls, 'Unknown') if cls is not None else 'Unknown'
                    
                    # Format coordinates 
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    w = x2 - x1
                    h = y2 - y1
                    
                    # Crop the image using the bounding box coordinates
                    cropped_img = orig_img.crop((x1, y1, x2, y2))
                    
                    numbered_class_name = f'{class_name.replace(" ", "_")}_{i}'
                    
                    # Append the detection details to the dictionary
                    page_detections[numbered_class_name] = {'coordinates': [x1, y1, w, h], 
                                                            'image': cropped_img,
                                                            'confidence': confidence}
            
            # Sort detections by vertical position
            sorted_page_detections = dict(sorted((item for item in page_detections.items()), key = lambda item: item[1]['coordinates'][1]))
            
            all_detections[page_num] = sorted_page_detections
            
            # Clear PyTorch cache after processing
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        
        return all_detections
    
    def _process_page_improved(self, pages, page_content, page_num, iou_threshold): 
        """
        Process a single page using the improved algorithm.
        
        Args:
            pages (dict): Dictionary of page images.
            page_content (dict): Dictionary of page elements.
            page_num (int): Page number being processed.
            iou_threshold (float): Threshold for merging bounding boxes.
            
        Returns:
            dict: Dictionary of processed page elements.
        """

        logger.info(f"Processing page {page_num} with {len(page_content)} elements")
        
        # STEP 1: Perform class-specific NMS to merge overlapping boxes of the same class
        logger.info("Step 1: Performing class-specific NMS")
        merged_boxes = nms_merge_boxes(page_content, iou_threshold, class_specific = True)
        
        # STEP 2: Remove container boxes that contain multiple other boxes
        logger.info(f"Step 2: Removing container boxes (threshold: {self.container_threshold})")
        no_container_boxes = remove_container_boxes(merged_boxes, min_contained_boxes=self.container_threshold)
        
        # STEP 3: Remove boxes that are completely inside other boxes, with improved handling
        logger.info("Step 3: Removing inner boxes with improved handling")
        filtered_boxes = remove_inner_boxes(no_container_boxes, containment_threshold=0.95, safe_classes=TEXT_LABELS)
        
        # STEP 4: Attempt to recover boxes that might have been incorrectly removed
        logger.info("Step 4: Recovering potentially missed boxes")
        recovered_boxes = recover_missed_boxes(merged_boxes, filtered_boxes, pages[page_num])
        
        # STEP 5: Sort boxes by position
        logger.info("Step 5: Sorting boxes by position")
        sorted_boxes = sort_bounding_boxes(recovered_boxes)

        # STEP 6: Deduplicate boxes
        logger.info("Step 6: Deduplicating boxes")
        deduplicated_boxes = deduplicate_boxes(sorted_boxes)

        # STEP 7: Remove contained boxes
        logger.info("Step 7: Removing contained boxes")
        final_boxes = remove_contained_bounding_boxes(deduplicated_boxes)
        
        logger.info(f"Finished processing page {page_num}: {len(final_boxes)} elements")
        
        # Garbage collection
        gc.collect()
        
        return final_boxes
    
    def _process_pages_improved(self, pages, iou_threshold) : 
        """
        Process all pages using the improved algorithm.
        
        Args:
            pages (dict): Dictionary of page images.
            iou_threshold (float): Threshold for merging bounding boxes.
            
        Returns:
            dict: Dictionary of processed page elements.
        """
        
        processed_pages = {}
        for page_num, page_content in self._parse_document_structure(pages).items():
            
            processed_pages[page_num] = self._process_page_improved(pages, page_content, page_num, iou_threshold)
            
            # Clean up after each page to save memory
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        
        return processed_pages
    
    def _save_debug_image(self, original_image, boxes, output_path): 
        """
        Save a debug image with bounding boxes for troubleshooting.
        
        Args:
            original_image (PIL.Image): The original image.
            boxes (dict): Dictionary of bounding boxes.
            output_path (str): Path to save the debug image.
        """
        annotated = annotate_image(boxes, original_image)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        annotated.save(output_path)
        logger.debug(f"Saved debug image to {output_path}")
    
    def _generate_annotations(self, pages, processed_pages, output_dir): 
        """
        Generate annotated images showing detected elements.
        
        Args:
            pages (dict): Dictionary of page images.
            processed_pages (dict): Dictionary of processed page elements.
            output_dir (str): Directory to save annotated images.
        """

        os.makedirs(output_dir, exist_ok=True)
        
        for page_num, page_content in processed_pages.items():
            if page_num in pages:
                annotated_image = annotate_image(page_content, pages[page_num])
                save_annotated_image(annotated_image, output_dir, page_num)
                
                # Clean up to free memory
                annotated_image = None
                gc.collect()
                
    def _save_bounding_boxes(self, processed_pages, output_dir): 
        """
        Save individual bounding box images.
        
        Args:
            processed_pages (dict): Dictionary of processed page elements.
            output_dir (str): Directory to save bounding box images.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        for page_num, page_content in processed_pages.items():
            page_dir = os.path.join(output_dir, f"page_{page_num}")
            os.makedirs(page_dir, exist_ok=True)
            
            self._save_bounding_boxes_for_page(page_content, page_dir)
            
            # Garbage collection after each page
            gc.collect()

    def _ocr_with_azure(self, image_path): 
        """
        Process a single bounding box image using Azure Document Intelligence,
        handling potential small image sizes by padding.

        Args:
            image_path (str): Path to the local image file (e.g., PNG).

        Returns:
            str: Extracted text content, or an empty string if OCR fails.
        """
        
        if not self.document_client:
            logger.error("OCR client not initialized. Cannot process image.")
            return ""

        temp_path = None
        process_path = image_path
        text = ""

        try:
            # Check image dimensions and pad if necessary
            with Image.open(image_path) as img:
                
                width, height = img.size
                needs_padding = width < 50 or height < 50

                if needs_padding:
                    
                    new_width = max(width, 50)
                    new_height = max(height, 50)
                    padded_img = Image.new('RGB', (new_width, new_height), color='white')
                   
                    # Convert to RGB if necessary before pasting
                    if img.mode != 'RGB':
                   
                        img = img.convert('RGB')
                  
                    padded_img.paste(img, (0, 0))

                    # Use NamedTemporaryFile to handle cleanup automatically
                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                     
                        temp_path = temp_file.name
                        padded_img.save(temp_path, format='JPEG')
                   
                    process_path = temp_path
                    if self.debug_mode:
                    
                         logger.debug(f"Padded image {os.path.basename(image_path)} to {new_width}x{new_height}, saved to temp file: {temp_path}")

            # Process the image (original or padded)
            try:
                with open(process_path, "rb") as image_file:
                  
                    # Use the 'prebuilt-read' model for OCR
                    poller = self.document_client.begin_analyze_document("prebuilt-read", image_file.read())
                    result = poller.result() # Wait for the result

                    # Safely access content, default to empty string if not found
                    text = result.content if result and hasattr(result, 'content') else ""

                    if self.debug_mode and not text:
                        logger.debug(f"OCR returned no content for image: {os.path.basename(image_path)}")
                  
                    elif self.debug_mode:
                         logger.debug(f"OCR successful for: {os.path.basename(image_path)}")


            except ServiceRequestError as e:
                logger.error(f"Azure service error during OCR for {os.path.basename(image_path)}: {e}")
         
            except Exception as e:
                 logger.error(f"Error during OCR processing for {os.path.basename(image_path)}: {e}", exc_info=self.debug_mode)


        except FileNotFoundError:
             logger.error(f"Image file not found for OCR: {image_path}")
    
        except Exception as e:
            logger.error(f"Error opening or padding image {image_path}: {e}", exc_info=self.debug_mode)
    
        finally:
    
            # Clean up temporary file if created
            if temp_path and os.path.exists(temp_path):
        
                try:
        
                    os.unlink(temp_path)
                    if self.debug_mode:
                        logger.debug(f"Cleaned up temporary OCR file: {temp_path}")
        
                except Exception as e:
                     logger.warning(f"Could not remove temporary OCR file {temp_path}: {e}")

        return text

    def _ocr_with_tesseract(self, image_path):
        """
        Process a single bounding box image using Tesseract.

        Args:
            image_path (str): Path to the local image file.

        Returns:
            str: Extracted text content, or an empty string if OCR fails.
        """

        text = ""

        try:

            # Load the image using Pillow
            img = Image.open(image_path)
            
            # Perform OCR
            text = pytesseract.image_to_string(img, lang='eng') # Specify language if needed
            text = text.strip()

            if self.debug_mode:
                logger.debug(f"Tesseract OCR successful for: {os.path.basename(image_path)}")

        except FileNotFoundError:
             
             logger.error(f"Image file not found for Tesseract OCR: {image_path}")
        except pytesseract.TesseractNotFoundError:
            
            logger.error(
                "Tesseract is not installed or not in your PATH. "
                "Please install Tesseract OCR engine"
            )
            # Re-raise or return empty string depending on desired behavior
            
            raise # Or return ""
       
        except Exception as e:
            logger.error(f"Error during Tesseract OCR for {os.path.basename(image_path)}: {e}", exc_info=self.debug_mode)
       

        return text

    def _run_ocr(self, output_dir, structure_json_path, use_tesseract = False): 

        """
        Run OCR on all saved bounding box images for the document,
        sort the text based on the structure JSON, and save the results.

        Args:
            output_dir (str): The main output directory for the document.
            structure_json_path (str): Path to the _parsed.json file containing structure info.
            use_tesseract (bool): If True, use Tesseract; otherwise use Azure.
        """

        output_doc_boxes_dir = os.path.join(output_dir, "boxes")
        if not os.path.isdir(output_doc_boxes_dir):
            
            logger.error(f"Bounding box directory not found for OCR: {output_doc_boxes_dir}")
            return

        doc_texts = {} # Structure: {page_num_str: {box_id: text}}

        # Iterate through page directories (e.g., page_0, page_1)
        page_dirs = sorted([d for d in os.listdir(output_doc_boxes_dir) if os.path.isdir(os.path.join(output_doc_boxes_dir, d)) and d.startswith("page_")],
                           key=lambda x: int(x.split('_')[-1])) # Sort numerically

        for page_dir_name in page_dirs:
            
            page_num_str = page_dir_name.split('_')[-1]
            page_path = os.path.join(output_doc_boxes_dir, page_dir_name)
            logger.info(f"Processing OCR for page {page_num_str}...")

            texts = {} # Structure: {box_id: text}
            box_files = [f for f in os.listdir(page_path) if f.lower().endswith(".png")] # Assume boxes are PNG

            for box_file in box_files:
           
                image_path = os.path.join(page_path, box_file)
           
                # Box ID is the filename without extension
                box_id = os.path.splitext(box_file)[0]
                try:
                                        
                    if use_tesseract:
                        text = self._ocr_with_tesseract(image_path)
                    
                    else:
                        text = self._ocr_with_azure(image_path)
                    
                    texts[box_id] = text
           
                except Exception as e:

                    logger.error(f"Failed OCR for box {box_id} on page {page_num_str}: {e}", exc_info=self.debug_mode)
                    texts[box_id] = "" # Store empty string on error

            doc_texts[page_num_str] = texts
            logger.info(f"Finished OCR for page {page_num_str}.")

        # Load the structure JSON to get the correct order
        try:

            with open(structure_json_path, "r", encoding='utf-8') as f: 
                
                structure = json.load(f)
           
        except FileNotFoundError: 

            logger.error(f"Structure JSON file not found: {structure_json_path}")
            return
      
        except json.JSONDecodeError: 
            
             logger.error(f"Error decoding structure JSON file: {structure_json_path}")
             return
       
        except Exception as e: 
            
             logger.error(f"Error loading structure JSON {structure_json_path}: {e}", exc_info=self.debug_mode)
             return

        # Create the sorted text dictionary based on structure order
        sorted_doc_texts = {} # {page_num_str: {box_id: text}}
        for page_num_str, page_content in structure.items(): 
      
            if page_num_str in doc_texts: 
     
                sorted_page_texts = {}
                for box_id in page_content.keys(): # Iterate in the order defined by structure JSON
      
                    if box_id in doc_texts[page_num_str]: 
                        sorted_page_texts[box_id] = doc_texts[page_num_str][box_id]
      
                    else: 

                        # Box ID exists in structure but not in OCR results (maybe OCR failed?)
                        logger.warning(f"Box ID '{box_id}' from structure JSON not found in OCR results for page {page_num_str}. Storing empty text.")
                        sorted_page_texts[box_id] = ""
         
                sorted_doc_texts[page_num_str] = sorted_page_texts
        
            else: 
                 
                 # Page exists in structure but not in OCR results (maybe no boxes saved?)
                 logger.warning(f"Page {page_num_str} from structure JSON not found in OCR results. Skipping.")

        return sorted_doc_texts

    # --- End OCR Methods ---