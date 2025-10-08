from lxml import etree
from typing import Dict
from os import path
from xml.sax.saxutils import XMLGenerator
import re
from sensestreet.deterministic_anonymization import anonimize_to_name, anonimize_to_hash
from functools import lru_cache
"""
BBXMLAnonymiser Module
This module provides functionality for anonymizing, and writing XML files while protecting sensitive information.

Classes:
- BBXMLAnonymiser: Handles the anonymization process of XML files.
- FakeUserGenerator: Generates anonymized user data.
Functions:
- anonymise_bbg_xml: A convenience function to anonymize an XML file.
- get_domain_from_email: Extracts the domain from an email address.
- anonimize_email: Creates an anonymized email using a given login name.
"""


class BBXMLAnonymiser:
    """
    BBXMLAnonymiser
    Handles the parsing, anonymizing, and writing of XML files.

    Attributes:
    - bank_pattern (str): A regex pattern used to identify company names related to a bank's role in conversations.
    - email_fields (set): XML tags representing email fields to anonymize.
    - anonimize_company (bool): Indicates if company-related information should be anonymized.
    - role_field (str or None): The XML tag used for identifying companies (optional).
    - bank_value (str): The replacement value for matching company names (default: "BANK").

    Methods:
    - anonymise_xml: Parses an XML file, anonymizes relevant fields, and writes the result to a new file.
    - _element_start: Processes the start of an XML element.
    - _element_end: Processes the end of an XML element and performs anonymization as needed.
    """
    def __init__(
        self,
        bank_pattern,
        role_field=None,
        bank_value="BANK",
    ):
        self.bank_pattern = bank_pattern
        self.email_fields = {"EmailAddress", "CorporateEmailAddress"}
        self.anonimize_company = role_field is not None
        self.role_field = role_field
        self.bank_value = bank_value
        self._xmlwriter = None
        self._current_user = None
        self._inside_user = False
        self.user_generator = FakeUserGenerator(anonimize_company=self.anonimize_company)

    def anonymise_xml(self, xml_in, xml_out):
        context = etree.iterparse(xml_in, events=("start", "end"))
        self._inside_user = False
        with open(xml_out, "w", encoding="UTF-8") as fp:
            self._xmlwriter = XMLGenerator(
                fp, encoding="UTF-8", short_empty_elements=False
            )
            self._xmlwriter.startDocument()

            for event, elem in context:
                if event == "start":
                    self._element_start(elem)
                elif event == "end":
                    self._element_end(elem)
                    elem.clear()

            self._xmlwriter.endDocument()

    def _element_start(self, elem):
        self._xmlwriter.startElement(name=elem.tag, attrs=elem.attrib)
        if elem.tag == "User":
            self._inside_user = True

        if self._inside_user and elem.tag == "LoginName" and elem.text:
            self._current_user = self.user_generator.generate_user_data(elem.text)

    def _element_end(self, elem):
        if elem.tag == "LoginName" and elem.text:
            self._current_user = self.user_generator.generate_user_data(elem.text)

        if self.role_field and elem.tag == self.role_field and re.search(
            self.bank_pattern, str(elem.text), flags=re.IGNORECASE
        ):
            elem.text = self.bank_value
            if self._inside_user:
                self._current_user[elem.tag] = self.bank_value
        elif (
            self._inside_user and elem.tag in self.user_generator.elements_to_anonymise
        ):
            elem.text = self._current_user[elem.tag]
        elif (
            self._inside_user and elem.tag in self.email_fields and elem.text is not None
        ):
            elem.text = anonimize_email(elem.text, self._current_user['LoginName'])

        if elem.text:
            self._xmlwriter.characters(elem.text)

        self._xmlwriter.endElement(name=elem.tag)
        self._xmlwriter.characters("\n")

        if elem.tag == "User":
            self._inside_user = False
            self._current_user = None

def get_domain_from_email(email):
    try:
        domain = email.split('@')[1]
        return domain
    except IndexError:
        return ""
    
def anonimize_email(email, login):
    return f"{login}@{get_domain_from_email(email)}"
    
class FakeUserGenerator:
    def __init__(self, anonimize_company=False):
        self.elements_to_anonymise = {
            "LoginName",
            "FirstName",
            "LastName",
            "UUID",
            "FirmNumber",
            "AccountNumber",
        }
        self.anonimize_company = anonimize_company

        if self.anonimize_company:
            self.elements_to_anonymise.add("CompanyName")
            self.elements_to_anonymise.add("EmailAddress")
            self.elements_to_anonymise.add("CorporateEmailAddress")

    @lru_cache(maxsize=100)
    def generate_user_data(self, login) -> Dict:
        first_name, last_name = anonimize_to_name(login)
        login = anonimize_to_hash(login, short=False)

        anonimized_data = {
            "FirstName": first_name,
            "LastName": last_name,
            "LoginName": login,
            "UUID": "",
            "FirmNumber": "",
            "AccountNumber": "",
        }
    
        if self.anonimize_company:
            anonimized_data["CompanyName"] = "ACME"
            anonimized_data["CorporateEmailAddress"] = f"{login}@acme.com"
            anonimized_data["EmailAddress"] = f"{login}@acme.com"

        return anonimized_data
            

def anonymise_bbg_xml(xml_in, xml_out, bank_pattern=None):
    """
    A convenience function to create an instance of BBXMLAnonymiser and anonymize an XML file.

    Parameters:
    - xml_in (str): Input XML file path.
    - xml_out (str): Output file path where anonymized XML will be saved.
    - bank_pattern (str): Regular expression pattern to identify banks in XML data.
    """
    anonymiser = BBXMLAnonymiser(bank_pattern=bank_pattern)
    anonymiser.anonymise_xml(xml_in, xml_out)


if __name__ == "__main__":
    anonymise_bbg_xml(
        "./example.xml",
        "./test.xml"
    )
