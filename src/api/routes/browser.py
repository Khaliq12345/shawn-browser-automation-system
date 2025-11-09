import time
from datetime import datetime

from fastapi import APIRouter, HTTPException

from src.api.dependencies import databaseDepends
from src.models.model import Prompt
from src.utils import celery_app

router = APIRouter(prefix="/browser")


@router.post("/start")
def start_browser(
    database: databaseDepends,
    brand_report_id: str,
    languague: str,
    country: str,
    prompts: list[Prompt],
    domain: str,
    brand: str,
    timeout: int = 60,
):
    try:
        timestamp = int(time.time())
        # save the report
        database.add_report(
            brand_report_id, languague, country, brand, domain, datetime.now()
        )

        processes = []

        # modify the prompt to always have domain with the name
        for prompt_data in prompts:
            prompt = prompt_data["prompt"]
            prompt_id = prompt_data["prompt_id"]
            clean_prompt = prompt.replace(brand, f"{brand}[{domain}]")
            database.update_schedule(brand_report_id, prompt_id, clean_prompt)
            prompt_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for name in ["chatgpt", "google", "perplexity"]:
                process_id = f"{name}-{brand_report_id}-{prompt_id}-{timestamp}"
                celery_app.run_browser.apply_async(
                    args=(
                        name,
                        clean_prompt,
                        process_id,
                        timeout,
                        country,
                        brand_report_id,
                        prompt_id,
                        languague,
                        brand,
                        prompt_date,
                    )
                )
                processes.append(process_id)

        output = {
            "message": "Browser started",
            "processes": processes,
        }
        return {"details": output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {e}")


@router.get("/status/{process_id}")
def check_status(database: databaseDepends, process_id: str):
    try:
        # Get the process status
        status = database.get_process_status(process_id)
        if status:
            output = {"process_id": process_id, "status": status}
            return {"details": output}
        else:
            raise HTTPException(
                status_code=404, detail=f"Process ({process_id}) not found"
            )
    except HTTPException as _:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {e}")


@router.get("/processes/{platform}")
def get_processes(database: databaseDepends, platform: str):
    try:
        outputs = database.get_all_platform_processes(platform)
        return {"details": outputs}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Server Error - Unable to retrieve processes for the platform: {e}",
        )
