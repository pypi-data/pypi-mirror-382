import asyncio
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from pydantic import Field
from timbal import Agent
from timbal.tools import WebSearch

load_dotenv()


def get_datetime() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def send_email(
    to_email: str = Field(..., description="Recipient email address"),
    subject: str = Field(..., description="Email subject line"),
    body: str = Field(..., description="Email body content"),
) -> str:
    """Send an email via SMTP using environment variables for configuration."""
    try:
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        from_email = os.getenv("SMTP_FROM_EMAIL", smtp_username)
        
        if not smtp_username or not smtp_password:
            return "Error: SMTP_USERNAME and SMTP_PASSWORD must be set in .env file"
        
        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        
        return f"Email successfully sent to {to_email}"
    except Exception as e:
        return f"Error sending email: {str(e)}"


agent = Agent(
    name="superagent",
    model="openai/gpt-4o-mini",
    tools=[get_datetime, WebSearch(), send_email],
)


async def main():
    while True:
        prompt = input("User: ")
        if prompt == "q":
            break
        agent_output_event = await agent(prompt=prompt).collect()
        print(f"Agent: {agent_output_event.output}") # noqa: T201


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Catch any Ctrl+C that wasn't caught in main()
        print("\nGoodbye!") # noqa: T201
    finally:
        print("Goodbye!") # noqa: T201
