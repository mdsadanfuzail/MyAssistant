from playwright.async_api import async_playwright
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from dotenv import load_dotenv
import os
import requests
from langchain.agents import Tool
from langchain_community.agent_toolkits import FileManagementToolkit
#from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities import GoogleSerperAPIWrapper
#from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv(override=True)

push_token = os.getenv("PUSHOVER_TOKEN")
push_user = os.getenv("PUSHOVER_USER")
push_url = "https://api.pushover.net/1/messages.json"

serper = GoogleSerperAPIWrapper()
 
def push(input: str):
    """Send a push notification to the user"""
    requests.post(url=push_url, data={"token":push_token, "user":push_user, "message":input})
    return "Notification Sent"

def fileTools():
    toolkit = FileManagementToolkit(root_dir=r"C:\Projects\MyAssistant\FileProcessArea")
    return toolkit.get_tools()

async def playwrightTool():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=browser)
    return toolkit.get_tools(), browser, playwright

sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
email_from = os.getenv("EMAIL_FROM")

def sendEmail(input: str):
    """
    Send an email using SendGrid. Input must be a string formatted as:
    'to:<recipient_email>;subject:<email_subject>;body:<email_body>'
    """
    try:
        parts = dict(x.split(":", 1) for x in input.split(";"))
        to_email = parts.get("to")
        subject = parts.get("subject", "No Subject")
        body = parts.get("body", "")

        message = Mail(
            from_email=email_from,
            to_emails=to_email,
            subject=subject,
            plain_text_content=body
        )
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)

        return f"Email sent to {to_email} with status code {response.status_code}"

    except Exception as e:
        return f"Failed to send email: {str(e)}"

async def otherTools():
    push_tool = Tool(name="send_push_notification",
                    func=push,
                    description="Use this tool when you want to send a push notification")

    search_tool  = Tool(name="search",
                        func=serper.run,
                        description="Use this tool when you want to get the results of an online web search")
    
    email_tool = Tool(name="send_email",
                      func=sendEmail,
                      description=( "Use this tool to send an email. "
                                    "Input format must be 'to:<recipient_email>;subject:<email_subject>;body:<email_body>'"))
    
    file_tools = fileTools()

    #wikipedia = WikipediaAPIWrapper
    #wikipedia_tool = WikipediaQueryRun(api_wrapper=wikipedia)

    return file_tools + [push_tool, search_tool, email_tool]