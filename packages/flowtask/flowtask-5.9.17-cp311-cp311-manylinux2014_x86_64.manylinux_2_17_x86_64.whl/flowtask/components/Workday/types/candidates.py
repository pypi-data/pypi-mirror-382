from typing import Dict, Any, List
import asyncio
import math
import pandas as pd

from ..models.candidate import Candidate
from ..parsers.candidate_parsers import (
    parse_candidate_reference,
    parse_candidate_personal_data,
    parse_candidate_contact_data,
    parse_candidate_recruitment_data,
    parse_candidate_status_data,
    parse_candidate_prospect_data,
    parse_candidate_education_data,
    parse_candidate_experience_data,
    parse_candidate_skills_data,
    parse_candidate_language_data,
    parse_candidate_document_data
)
from ..utils import safe_serialize
from .base import WorkdayTypeBase


class CandidateType(WorkdayTypeBase):
    """
    Handler for the Workday Get_Candidates operation from Recruiting API.
    
    Based on Workday Recruiting API v45.0:
    https://community.workday.com/sites/default/files/file-hosting/productionapi/Recruiting/v45.0/Get_Candidates.html
    
    Returns information for candidates in the recruiting pipeline.
    """
    
    def _get_default_payload(self) -> Dict[str, Any]:
        """
        Default payload for Get_Candidates operation.
        
        Get_Candidates returns all candidates by default.
        According to WSDL, Response_Group only accepts:
        - Include_Reference: xsd:boolean
        - Exclude_All_Attachments: xsd:boolean
        """
        return {
            "Response_Filter": {},
            "Response_Group": {
                "Include_Reference": True,
                "Exclude_All_Attachments": False,  # Include attachments by default
            },
        }
    
    async def execute(self, **kwargs) -> pd.DataFrame:
        """
        Execute the Get_Candidates operation and return a pandas DataFrame.
        
        Args:
            candidate_id: Optional specific candidate ID to fetch
            job_requisition_id: Optional filter by job requisition
            applied_from_date: Optional filter by application date from
            applied_to_date: Optional filter by application date to
            created_from_date: Optional filter by creation date from
            created_to_date: Optional filter by creation date to
        """
        # Extract parameters from kwargs
        candidate_id = kwargs.pop("candidate_id", None)
        job_requisition_id = kwargs.pop("job_requisition_id", None)
        applied_from_date = kwargs.pop("applied_from_date", None)
        applied_to_date = kwargs.pop("applied_to_date", None)
        created_from_date = kwargs.pop("created_from_date", None)
        created_to_date = kwargs.pop("created_to_date", None)
        pdf_directory = kwargs.pop("pdf_directory", None)
        
        # Log PDF directory if configured
        if pdf_directory:
            self._logger.info(f"📁 PDFs will be saved to: {pdf_directory}")
        
        payload = {**self.request_payload}
        
        # Build request based on provided parameters
        if candidate_id:
            # Use Request_References for specific candidate ID
            payload["Request_References"] = {
                "Candidate_Reference": [
                    {
                        "ID": [
                            {
                                "_value_1": candidate_id,
                                "type": "Candidate_ID"
                            }
                        ]
                    }
                ]
            }
            self._logger.info(f"Fetching specific candidate: {candidate_id}")
        else:
            # Use Request_Criteria for filtering
            criteria = {}
            
            # Job Requisition filter
            if job_requisition_id:
                criteria["Job_Requisition_Reference"] = [
                    {
                        "ID": [
                            {
                                "_value_1": job_requisition_id,
                                "type": "Job_Requisition_ID"
                            }
                        ]
                    }
                ]
            
            # Application date range
            if applied_from_date:
                criteria["Applied_From_Date"] = applied_from_date
            if applied_to_date:
                criteria["Applied_Through_Date"] = applied_to_date
            
            # Created date range
            if created_from_date:
                criteria["Created_From_Date"] = created_from_date
            if created_to_date:
                criteria["Created_Through_Date"] = created_to_date
            
            if criteria:
                payload["Request_Criteria"] = criteria
            
            self._logger.info("Fetching all candidates")
        
        # Execute the operation with pagination (similar to workers.py and applicants.py)
        try:
            # 1) Fetch page 1 to get total_pages
            if candidate_id:
                # For specific candidate, no pagination needed
                self._logger.info(f"Executing Get_Candidates for specific candidate: {candidate_id}")
                
                # Use retry for single candidate request
                response = None
                for attempt in range(1, self.max_retries + 1):
                    try:
                        self._logger.info(f"📡 Fetching candidate {candidate_id} (attempt {attempt}/{self.max_retries})...")
                        response = await self.component.run(
                            operation="Get_Candidates",
                            **payload
                        )
                        self._logger.info(f"✅ Successfully fetched candidate {candidate_id}")
                        break
                    except Exception as exc:
                        self._logger.warning(
                            f"[Get_Candidates] Error fetching candidate {candidate_id} "
                            f"(attempt {attempt}/{self.max_retries}): {exc}"
                        )
                        if attempt == self.max_retries:
                            self._logger.error(
                                f"[Get_Candidates] Failed to fetch candidate {candidate_id} after "
                                f"{self.max_retries} attempts."
                            )
                            raise
                        delay = min(self.retry_delay * (2 ** (attempt - 1)), 8.0)
                        self._logger.info(f"⏳ Waiting {delay:.1f}s before retry...")
                        await asyncio.sleep(delay)
                
                serialized = self.component.serialize_object(response)
                response_data = serialized.get("Response_Data", {})
                
                # Extract Candidate elements
                if "Candidate" in response_data:
                    candidate_data = response_data["Candidate"]
                    candidates_raw = [candidate_data] if isinstance(candidate_data, dict) else candidate_data
                else:
                    candidates_raw = []
                
                self._logger.info(f"Retrieved {len(candidates_raw)} candidate(s)")
                
            else:
                # For all candidates, use pagination
                self._logger.info("🔍 Fetching first page to determine total candidates and pages...")
                
                # Build first page payload
                first_payload = {
                    **payload,
                    "Response_Filter": {
                        **payload.get("Response_Filter", {}),
                        "Page": 1,
                        "Count": 100
                    }
                }
                
                # Fetch first page with retry logic
                raw1 = None
                for attempt in range(1, self.max_retries + 1):
                    try:
                        self._logger.info(f"📡 Attempting to fetch first page (attempt {attempt}/{self.max_retries})...")
                        raw1 = await self.component.run(operation="Get_Candidates", **first_payload)
                        self._logger.info("✅ Successfully fetched first page")
                        break
                    except Exception as exc:
                        self._logger.warning(
                            f"[Get_Candidates] Error on first page "
                            f"(attempt {attempt}/{self.max_retries}): {exc}"
                        )
                        if attempt == self.max_retries:
                            self._logger.error(
                                f"[Get_Candidates] Failed first page after "
                                f"{self.max_retries} attempts."
                            )
                            raise
                        # Use exponential backoff: 0.2s, 0.4s, 0.8s, 1.6s, 3.2s
                        delay = min(self.retry_delay * (2 ** (attempt - 1)), 8.0)
                        self._logger.info(f"⏳ Waiting {delay:.1f}s before retry...")
                        await asyncio.sleep(delay)
                
                data1 = self.component.serialize_object(raw1)
                
                # Extract candidates from first page
                page1 = data1.get("Response_Data", {}).get("Candidate", [])
                if isinstance(page1, dict):
                    page1 = [page1]
                
                # Extract pagination info from Response_Results
                response_results = data1.get("Response_Results", {})
                total_pages = int(float(response_results.get("Total_Pages", 1)))
                total_results = int(float(response_results.get("Total_Results", 0)))
                page_results = int(float(response_results.get("Page_Results", 0)))
                
                # Log pagination summary
                self._logger.info(
                    f"📊 Workday Pagination Info: Total Candidates={total_results}, "
                    f"Total Pages={total_pages}, Candidates per Page={page_results}"
                )
                self._logger.info(f"📄 Page 1/{total_pages} fetched: {len(page1)} candidates")
                
                all_candidates: List[dict] = list(page1)
                
                # 2) If more pages, batch them (max 10 parallel requests)
                max_parallel = 10
                if total_pages > 1:
                    pages = list(range(2, total_pages + 1))
                    num_batches = math.ceil(len(pages) / max_parallel)
                    batches = self.component.split_parts(pages, num_parts=num_batches)
                    
                    for batch in batches:
                        self._logger.info(f"🔄 Processing batch of {len(batch)} pages: {batch}")
                        tasks = [self._fetch_candidate_page(p, payload) for p in batch]
                        results = await asyncio.gather(*tasks, return_exceptions=True)
                        for res in results:
                            if isinstance(res, Exception):
                                self._logger.error(f"❌ Error fetching page: {res}")
                            else:
                                all_candidates.extend(res)
                        
                        # Log progress after each batch
                        self._logger.info(
                            f"✅ Progress: {len(all_candidates)}/{total_results} candidates fetched "
                            f"({len(all_candidates)/total_results*100:.1f}%)"
                        )
                
                candidates_raw = all_candidates
                
                # Final summary log
                self._logger.info(
                    f"✨ Completed fetching all pages: {len(candidates_raw)} candidates retrieved "
                    f"(Expected: {total_results})"
                )
                
                # Add metrics
                self.component.add_metric("EXPECTED_CANDIDATES", total_results)
                self.component.add_metric("TOTAL_PAGES", total_pages)
                if len(candidates_raw) != total_results:
                    self._logger.warning(
                        f"⚠️  Mismatch: Expected {total_results} candidates but got {len(candidates_raw)}"
                    )
            
        except Exception as e:
            self._logger.error(f"Error fetching candidates: {e}")
            import traceback
            self._logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        
        # Parse into Pydantic models
        parsed: List[Candidate] = []
        for candidate_raw in candidates_raw:
            try:
                # Extract candidate data from response
                candidate_data = candidate_raw.get("Candidate_Data", {}) if isinstance(candidate_raw, dict) else {}
                
                # Parse reference first to get candidate_id for PDF storage
                reference_data = parse_candidate_reference(candidate_raw)
                current_candidate_id = reference_data.get("candidate_id")
                
                # Parse only data sections that exist in Get_Candidates response
                # NOTE: Get_Candidates returns LESS data than Get_Applicants
                record = {
                    **reference_data,
                    **parse_candidate_personal_data(candidate_data),
                    **parse_candidate_contact_data(candidate_data),
                    **parse_candidate_recruitment_data(candidate_data),
                    **parse_candidate_status_data(candidate_data),
                    **parse_candidate_prospect_data(candidate_data),
                    **parse_candidate_education_data(candidate_data),
                    **parse_candidate_experience_data(candidate_data),
                    **parse_candidate_skills_data(candidate_data),
                    **parse_candidate_language_data(candidate_data),
                    **parse_candidate_document_data(candidate_data, current_candidate_id, pdf_directory),
                }
                
                parsed.append(Candidate(**record))
                
            except Exception as e:
                self._logger.warning(f"Error parsing candidate: {e}")
                import traceback
                self._logger.warning(f"Traceback: {traceback.format_exc()}")
                continue
        
        # Build DataFrame
        if parsed:
            df = pd.DataFrame([c.dict() for c in parsed])
            
            # Serialize complex columns
            complex_cols = [
                "emails", "phones", "schools", "degrees", "previous_employers", 
                "work_experience", "skills", "competencies", "languages",
                "references", "documents", "interviews", "assessments",
                "custom_fields", "candidate_tags"
            ]
            for col in complex_cols:
                if col in df.columns:
                    df[col] = df[col].apply(safe_serialize)
            
            # Add metrics
            self.component.add_metric("NUM_CANDIDATES", len(parsed))
            
            self._logger.info(f"Successfully parsed {len(parsed)} candidates")
            
            return df
        else:
            self._logger.warning("No candidates found or processed successfully")
            # Return empty DataFrame with expected columns
            return pd.DataFrame(columns=[
                'candidate_id', 'candidate_wid', 'first_name', 'last_name', 
                'email', 'candidate_status', 'job_requisition_id'
            ])
    
    async def _fetch_candidate_page(self, page_num: int, base_payload: dict) -> List[dict]:
        """
        Fetch a single page of Get_Candidates. Returns list of candidate dicts.
        Similar to workers.py _fetch_page method.
        """
        self._logger.debug(f"📄 Starting fetch for page {page_num}")
        
        # Build payload for this page
        payload = {
            **base_payload,
            "Response_Filter": {
                **base_payload.get("Response_Filter", {}),
                "Page": page_num,
                "Count": 100
            }
        }
        
        # Use retry mechanism with exponential backoff
        raw = None
        for attempt in range(1, self.max_retries + 1):
            try:
                raw = await self.component.run(operation="Get_Candidates", **payload)
                break
            except Exception as exc:
                self._logger.warning(
                    f"[Get_Candidates] Error on page {page_num} "
                    f"(attempt {attempt}/{self.max_retries}): {exc}"
                )
                if attempt == self.max_retries:
                    self._logger.error(
                        f"[Get_Candidates] Failed page {page_num} after "
                        f"{self.max_retries} attempts."
                    )
                    raise
                # Use exponential backoff: 0.2s, 0.4s, 0.8s, 1.6s, 3.2s
                delay = min(self.retry_delay * (2 ** (attempt - 1)), 8.0)
                await asyncio.sleep(delay)
        
        data = self.component.serialize_object(raw)
        items = data.get("Response_Data", {}).get("Candidate", [])
        if isinstance(items, dict):
            items = [items]
        
        candidates_count = len(items) if items else 0
        self._logger.debug(f"✅ Page {page_num} completed: {candidates_count} candidates fetched")
        
        return items or [] 