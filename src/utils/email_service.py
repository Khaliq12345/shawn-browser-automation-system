import email
import imaplib
import re
import time


class EmailService:

    def __init__(
        self, IMAP_SERVER: str, EMAIL_ACCOUNT: str, EMAIL_PASSWORD: str
    ) -> None:
        self.imap_server = IMAP_SERVER
        self.email_account = EMAIL_ACCOUNT
        self.email_password = EMAIL_PASSWORD

    def _extract_otp(self, text: str):
        """Extracts a 4 to 8-digit OTP code from text using RegEx."""
        match = re.search(r"\b\d{4,8}\b", text)
        if match:
            return match.group(0)
        return None

    def fetch_latest_otp(
        self,
        timeout: int = 60,
        poll_interval: int = 5,
        sender_email: str = None,
        subject_keyword: str = "verification",
    ):
        """Connects to IMAP inbox and polls for a new OTP email."""
        print(
            f"Connecting to {self.imap_server} and listening for OTP messages"
            f" (Timeout: {timeout}s)..."
        )

        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # Connect to the IMAP server securely
                mail = imaplib.IMAP4_SSL(self.imap_server)
                mail.login(self.email_account, self.email_password)
                mail.select("inbox")
                print("NOW IN inbox")

                # Build search criteria (Unread messages)
                search_criteria = "(UNSEEN)"
                if sender_email:
                    search_criteria += f' (FROM "{sender_email}")'

                status, messages = mail.search(None, search_criteria)
                print(messages)

                if status == "OK":
                    email_ids = messages[0].split()
                    if email_ids:
                        # Get the latest unread email ID
                        latest_email_id = email_ids[-1]
                        status, msg_data = mail.fetch(latest_email_id, "(RFC822)")

                        if status == "OK":
                            for response_part in msg_data:
                                if isinstance(response_part, tuple):
                                    msg = email.message_from_bytes(response_part[1])
                                    subject = msg["Subject"] or ""

                                    # Verify subject contains our keyword
                                    if subject_keyword.lower() in subject.lower():
                                        print(
                                            f"Found matching email! Subject: {subject}"
                                        )

                                        # Extract body text
                                        body = ""
                                        if msg.is_multipart():
                                            for part in msg.walk():
                                                if (
                                                    part.get_content_type()
                                                    == "text/plain"
                                                ):
                                                    body = part.get_payload(
                                                        decode=True
                                                    ).decode("utf-8", errors="ignore")
                                                    break
                                        else:
                                            body = msg.get_payload(decode=True).decode(
                                                "utf-8", errors="ignore"
                                            )

                                        otp_code = self._extract_otp(body)
                                        if otp_code:
                                            mail.logout()
                                            return otp_code

                mail.logout()
            except Exception as e:
                print(f"Error checking email: {e}")

            # Wait before polling again
            time.sleep(poll_interval)

        print("Timeout reached: No OTP code found.")
        return None
