from agentmake.utils.online import get_local_ip
import requests, os, re
from biblemate import config

DEFAULT_MODULES = {
    "bible": config.default_bible,
    "chapter": config.default_bible,
    "search": config.default_bible,
    "genesis": config.default_bible,
    "exodus": config.default_bible,
    "leviticus": config.default_bible,
    "numbers": config.default_bible,
    "deuteronomy": config.default_bible,
    "joshua": config.default_bible,
    "judges": config.default_bible,
    "ruth": config.default_bible,
    "samuel1": config.default_bible,
    "samuel2": config.default_bible,
    "kings1": config.default_bible,
    "kings2": config.default_bible,
    "chronicles1": config.default_bible,
    "chronicles2": config.default_bible,
    "ezra": config.default_bible,
    "nehemiah": config.default_bible,
    "esther": config.default_bible,
    "job": config.default_bible,
    "psalms": config.default_bible,
    "proverbs": config.default_bible,
    "ecclesiastes": config.default_bible,
    "songs": config.default_bible,
    "isaiah": config.default_bible,
    "jeremiah": config.default_bible,
    "lamentations": config.default_bible,
    "ezekiel": config.default_bible,
    "daniel": config.default_bible,
    "hosea": config.default_bible,
    "joel": config.default_bible,
    "amos": config.default_bible,
    "obadiah": config.default_bible,
    "jonah": config.default_bible,
    "micah": config.default_bible,
    "nahum": config.default_bible,
    "habakkuk": config.default_bible,
    "zephaniah": config.default_bible,
    "haggai": config.default_bible,
    "zechariah": config.default_bible,
    "malachi": config.default_bible,
    "matthew": config.default_bible,
    "mark": config.default_bible,
    "luke": config.default_bible,
    "john": config.default_bible,
    "acts": config.default_bible,
    "romans": config.default_bible,
    "corinthians1": config.default_bible,
    "corinthians2": config.default_bible,
    "galatians": config.default_bible,
    "ephesians": config.default_bible,
    "philippians": config.default_bible,
    "colossians": config.default_bible,
    "thessalonians1": config.default_bible,
    "thessalonians2": config.default_bible,
    "timothy1": config.default_bible,
    "timothy2": config.default_bible,
    "titus": config.default_bible,
    "philemon": config.default_bible,
    "hebrews": config.default_bible,
    "james": config.default_bible,
    "peter1": config.default_bible,
    "peter2": config.default_bible,
    "john1": config.default_bible,
    "john2": config.default_bible,
    "john3": config.default_bible,
    "jude": config.default_bible,
    "revelation": config.default_bible,
    "parallel": config.default_bible,
    "promise": config.default_bible,
    "commentary": config.default_commentary,
    "encyclopedia": config.default_encyclopedia,
    "lexicon": config.default_lexicon,
}

# api
def run_uba_api(command: str, html=False) -> str:
    UBA_API_LOCAL_PORT = int(os.getenv("UBA_API_LOCAL_PORT")) if os.getenv("UBA_API_LOCAL_PORT") else 8080
    UBA_API_ENDPOINT = os.getenv("UBA_API_ENDPOINT") if os.getenv("UBA_API_ENDPOINT") else f"http://{get_local_ip()}:{UBA_API_LOCAL_PORT}/plain" # use dynamic local ip if endpoint is not specified
    UBA_API_TIMEOUT = int(os.getenv("UBA_API_TIMEOUT")) if os.getenv("UBA_API_TIMEOUT") else 10
    UBA_API_PRIVATE_KEY = os.getenv("UBA_API_PRIVATE_KEY") if os.getenv("UBA_API_PRIVATE_KEY") else ""

    endpoint = UBA_API_ENDPOINT
    if html:
        endpoint = endpoint.replace("/plain", "/html")
    private = f"private={UBA_API_PRIVATE_KEY}&" if UBA_API_PRIVATE_KEY else ""
    url = f"""{endpoint}?{private}cmd={command}"""
    try:
        response = requests.get(url, timeout=UBA_API_TIMEOUT)
        response.encoding = "utf-8"
        content = response.text.strip()
        if command.lower().startswith("data:::"):
            return content.replace("\n", "\n- ")
        content = re.sub(r"\n([0-9]+?) \(([^\(\)]+?)\)", r"\n- `\1` (`\2`)", content)
        content = re.sub(r"^([0-9]+?) \(([^\(\)]+?)\)", r"- `\1` (`\2`)", content)
        content = re.sub(r"\n\(([^\(\)]+?)\)", r"\n- (`\1`)", content)
        content = re.sub(r"^\(([^\(\)]+?)\)", r"- (`\1`)", content)
        if command.lower().startswith("chapter:::"):
            content = "# " + re.sub(r"\n`([0-9]+?)` ", r"\n* `\1` ", content).replace("\n# ", "\n## ")
        return content
    except Exception as err:
        return f"An error occurred: {err}"