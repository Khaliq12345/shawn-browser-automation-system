import pandas as pd
import requests
import time
from urllib.parse import urlparse
from src.config import config

API_KEY = config.API_KEY
BASE_URL = "https://scraper.beta.brandpeak.ai/api/browser/start"
CSV_PATH = "prompts_normalized.csv"  # Update path if needed

LANGUAGE = "en"
COUNTRY = "us"


def extract_domain(url: str) -> str:
    """Strip https://www. from domain URL."""
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path
    return domain.replace("www.", "")


def run_prompt(
    brand_report_id: str, domain: str, brand: str, prompt: str, prompt_id: str
) -> dict:
    params = {
        "brand_report_id": brand_report_id,
        "languague": LANGUAGE,  # keeping the typo from the API spec
        "country": COUNTRY,
        "domain": domain,
        "brand": brand,
    }
    payload = [{"prompt": prompt, "prompt_id": prompt_id}]
    headers = {
        "accept": "application/json",
        "X-API-KEY": API_KEY,
        "Content-Type": "application/json",
    }

    response = requests.post(
        BASE_URL, params=params, headers=headers, json=payload, timeout=60
    )
    response.raise_for_status()
    return response.json()


def main():
    df = pd.read_csv(CSV_PATH)

    results = []
    total = len(df)

    for i, row in df.iterrows():
        brand = row["Brand"]
        brand_report_id = row["Brand_report_id"]
        domain = extract_domain(row["Domain"])
        prompt = row["Prompt"]
        prompt_id = row["Prompt_id"]

        print(f"[{i + 1}/{total}] {prompt_id} — {brand} — {prompt[:60]}...")

        try:
            result = run_prompt(brand_report_id, domain, brand, prompt, prompt_id)
            results.append(
                {
                    "prompt_id": prompt_id,
                    "brand": brand,
                    "brand_report_id": brand_report_id,
                    "status": "success",
                    "response": result,
                }
            )
            print("  ✓ Success")
        except requests.HTTPError as e:
            print(f"  ✗ HTTP error: {e.response.status_code} — {e.response.text}")
            results.append(
                {
                    "prompt_id": prompt_id,
                    "brand": brand,
                    "brand_report_id": brand_report_id,
                    "status": "http_error",
                    "response": e.response.text,
                }
            )
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append(
                {
                    "prompt_id": prompt_id,
                    "brand": brand,
                    "brand_report_id": brand_report_id,
                    "status": "error",
                    "response": str(e),
                }
            )

        time.sleep(1)  # Be polite to the API — adjust as needed

    # Summary
    success = sum(1 for r in results if r["status"] == "success")
    failed = total - success
    print(f"\nDone! {success}/{total} succeeded, {failed} failed.")
    print("Results saved to results.json")


if __name__ == "__main__":
    main()
