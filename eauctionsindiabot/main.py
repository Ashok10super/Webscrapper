from eauctionsindiabot.bot import start_scrapping
from eauctionsindiabot.database.db_config import get_eauctionindiadb_connection,get_script_log_connection
from eauctionsindiabot.custom_exceptions.exceptions import DatabaseError, StartScrapperError, GeminiApiError, TesseractOCRError,SingleScrapperError
from datetime import datetime
from eauctionsindiabot.config import log_check_list,Status



if __name__ == "__main__":
    try:
        print("Cron job started!")
        eauction_conn = get_eauctionindiadb_connection()
        script_log_conn = get_script_log_connection()
        log_check_list["database"]["status"] = Status.SUCCESS  # <-- EXPLICITLY LOG SUCCESS
        print("Database connection successful.")
        state_list = ['tamil-nadu', 'Puducherry','Karnataka']
        today_date = datetime.today().date().isoformat()
        total_fetched_properties = 0
        for state in state_list:
            fetched_properties_count = start_scrapping(state=state, date=today_date, conn=eauction_conn)
            total_fetched_properties += fetched_properties_count
        log_check_list['total_properties_fetched'] = total_fetched_properties
        print("All states processed successfully.")
        script_log_conn.insert_one(log_check_list)
        print("All states processed successfully.")
    except DatabaseError as e:
        print("database connection failed: ", e)
        log_check_list["database"]["error_message"] = str(e)
        log_check_list["database"]["status"] = Status.FAILED
    except StartScrapperError as e:
        print("start scrapper failed: ", e)
        log_check_list["start_scrapper_info"]["error_message"] = str(e)
        log_check_list["start_scrapper_info"]["status"] = Status.FAILED
        script_log_conn.insert_one(log_check_list)
    except SingleScrapperError as e:
        print("single scrapper failed: ", e)
        log_check_list["single_scrapper_info"]["error_message"] = str(e)
        log_check_list["single_scrapper_info"]["status"] = Status.FAILED
        script_log_conn.insert_one(log_check_list)
    except GeminiApiError as e:
        print("Gemini API error: ", e)
        log_check_list["gemini_api_info"]["error_message"] = str(e)
        log_check_list["gemini_api_info"]["status"] = Status.FAILED
        script_log_conn.insert_one(log_check_list)
    except TesseractOCRError as e:
        print("Tesseract OCR error: ", e)
        log_check_list["tesseract_ocr_info"]["error_message"] = str(e)
        log_check_list["tesseract_ocr_info"]["status"] = Status.FAILED
        script_log_conn.insert_one(log_check_list)









