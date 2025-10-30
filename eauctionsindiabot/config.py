from datetime import datetime
from enum import StrEnum


class Status(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"

log_check_list = {
        "script_execution_time": datetime.today().date().isoformat(),
        "database": {
            "status": Status.PENDING,
            "error_message": None
        }, "start_scrapper_info": {
            "status": Status.PENDING,
            "error_message": None
        },"single_scrapper_info": {
            "status": Status.PENDING,
            "error_message": None
        },
        "gemini_api_info": {
            "status": Status.PENDING,
            "error_message": None
        },
        "tesseract_ocr_info": {
            "status": Status.PENDING,
            "error_message": None},
        "total_properties_fetched":0}