import sys

sys.path.append("..")

from src.config.config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client, Client


def get_supabase_session() -> Client:
    return create_client(supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY)


def start_process(process_id: str, status: str = "running"):
    supabase = get_supabase_session()
    return (
        supabase.table("browser_automation_system")
        .upsert(
            {"process_id": process_id, "status": status},
            on_conflict="process_id",
        )
        .execute()
    )

def update_process_status(process_id: str, status: str):
    supabase = get_supabase_session()
    return (
        supabase.table("browser_automation_system")
        .update({"status": status})
        .eq("process_id", process_id)
        .execute()
    )


def get_process_status(process_id: str):
    supabase = get_supabase_session()
    response = (
        supabase.table("browser_automation_system")
        .select("status")
        .eq("process_id", process_id)
        .limit(1)
        .execute()
    )
    if response.data:
        return response.data[0]["status"]
    return None

