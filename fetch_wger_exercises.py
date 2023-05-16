# from app import *
import re
import requests
from write_to_local import write_to_local
from models import Exercise

def scrub_abduktion_im_stand(data):

    scrubbed_data = [d for d in data if d["name"] != 'Abduktion im Stand']

    return scrubbed_data

def tag_scrub(old_string):

    scrubs = ["<p>", "</p>", "<b>", "</b>", "<li>", "</li>", "<ol>", "</ol>", "  ", "   ", "    "]

    for string in scrubs:
        # new_string = old_string.translate( { ord(i): None for i in f'{string}'} )
        new_string = old_string.replace(f"{string}", " ")
        old_string = new_string

    return new_string.strip()

def wger_parse_relevant(r):
    """
    Accepts WGER response
    Parses "Name"
    Parses "Description"
    Appends a list with dictionaries for each exercise.
    """
    
    parsed_data = []
    
    for each in r["results"]:
        name = tag_scrub(each["name"])
        description = tag_scrub(each["description"])

        parsed_data.append({"name":name, "description":description})
        english_only_data = scrub_abduktion_im_stand(parsed_data)

    return english_only_data

def wger_fetch(filename, revision, limit):
    """
    Accepts: filename, revision, limit
    Calls WGER API
    Calls wger_parse_relevant
    Calls write_to_local
    Returns parsed_content
    """

    url = f"https://wger.de/api/v2/exercise/?language=2&limit={limit}"

    response = requests.get(url)

    r = response.json()

    parsed_content = wger_parse_relevant(r)

    write_to_local(filename, revision, parsed_content)

    return parsed_content





