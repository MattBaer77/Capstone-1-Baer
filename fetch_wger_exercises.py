# from app import *
import requests
from write_to_local import write_to_local

def wger_parse_relevant(r):
    """
    Accepts WGER response
    Parses "Name"
    Parses "Description"
    Appends a list with dictionaries for each exercise.
    """
    
    parsed_data = []
    
    for each in r["results"]:
        name = each["name"]
        description = each["description"]

        parsed_data.append({f'"name":"{name}", "description":"{description}"'})

    return parsed_data

def wger_fetch(filename, revision, limit):
    """
    Accepts: filename, revision, limit
    Calls WGER API
    Calls wger_parse_relevant
    Calls write_to_local
    Returns nothing
    """

    url = f"https://wger.de/api/v2/exercise/?language=2&limit={limit}"

    response = requests.get(url)

    r = response.json()

    parsed_content = wger_parse_relevant(r)

    write_to_local(filename, revision, parsed_content)





