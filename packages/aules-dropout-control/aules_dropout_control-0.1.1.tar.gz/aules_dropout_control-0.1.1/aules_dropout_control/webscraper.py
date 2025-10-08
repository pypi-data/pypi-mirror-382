
from venv import logger
import requests
import logging
import re
import io
import csv
from bs4 import BeautifulSoup, Tag
from typing import List, Dict, Any

class WebScraper:
    LOGIN_URL = "https://aules.edu.gva.es/ed/login/index.php"
    COURSE_URL_TEMPLATE = "https://aules.edu.gva.es/ed/course/view.php?id={course_id}"

    def __init__(self, username: str, password: str, days_without_connection: int = 0):
        self.session = requests.Session()
        self.login_url = self.LOGIN_URL
        self.username = username
        self.password = password
        self.days_without_connection = days_without_connection

    def get_course_url(self, course_id: int) -> str:
        url = self.COURSE_URL_TEMPLATE.format(course_id=course_id)
        logging.info(f"Accessing course URL: {url}")
        return url

    def login(self) -> None:
        logging.info(f"Accessing login URL: {self.login_url}")
        resp = self.session.get(self.login_url)
        logging.debug(f"Login page HTML received:\n{resp.text}")
        soup = BeautifulSoup(resp.text, "html.parser")
        logintoken = soup.find("input", {"name": "logintoken"})
        anchor = soup.find("input", {"name": "anchor"})
        token_value = logintoken["value"] if logintoken else ""
        anchor_value = anchor["value"] if anchor else ""

        payload = {
            "username": str(self.username),
            "password": str(self.password),
            "logintoken": str(token_value),
            "anchor": str(anchor_value)
        }
        post_resp = self.session.post(self.login_url, data=payload)
        logging.debug(f"Login POST response HTML received:\n{post_resp.text}")

    def get_page(self, url: str) -> BeautifulSoup:
        logging.info(f"Accessing page URL: {url}")
        response = self.session.get(url)
        response.raise_for_status()
        logging.debug(f"Page received from {url}:\n{response.text}")
        return BeautifulSoup(response.text, 'html.parser')


    def get_participants_info(self, course_id: int, username: str, password: str) -> str:
        html = self._get_lastaccess_sorted_participants(course_id)
        data: List[Dict[str, Any]] = self._parse_participants_table(html)
        return self._participants_to_csv(data)

    def _participants_to_csv(self, participants: List[Dict[str, Any]]) -> str:

        output = io.StringIO()
        writer = csv.writer(output)
        # Write header
        writer.writerow(["name", "user_name", "email", "roles", "acceso"])
        for p in participants:
            writer.writerow([
                p.get("name", ""),
                p.get("user_name", ""),
                p.get("email", ""),
                p.get("roles", ""),
                p.get("acceso", "")
            ])
        return output.getvalue()

    def _get_lastaccess_sorted_participants(self, course_id: int) -> str:
        """
        1. Get participants page for course_id
        2. Find <a data-sortable="1" data-sortby="lastaccess"> and GET its href
        3. On response, find <a data-action="showcount"> and GET its href
        4. Return the final page HTML
        """
        # Step 1: Get participants page
        course_url = self.get_course_url(course_id)
        logging.info(f"Accessing participants course URL: {course_url}")
        course_resp = self.session.get(course_url)
        logging.debug("----------------------------------------------\n"*3)
        logging.debug(f"Step 1: Course page HTML for {course_url}:\n{course_resp.text}")
        participants_url = self._get_participants_url(course_resp.text)
        logging.info(f"Accessing participants URL: {participants_url}")
        participants_resp = self.session.get(participants_url)
        logging.debug(f"Step 1: Participants page HTML for {participants_url}:\n{participants_resp.text}")

        # Step 2: Find <a data-sortable="1" data-sortby="lastaccess">
        soup = BeautifulSoup(participants_resp.text, "html.parser")
        lastaccess_a = soup.find("a", attrs={"data-sortable": "1", "data-sortby": "lastaccess"})
        if not lastaccess_a or not lastaccess_a.has_attr("href"):
            raise Exception("Lastaccess <a> element not found or missing href.")
        lastaccess_url = str(lastaccess_a["href"])
        logging.info(f"Accessing lastaccess URL: {lastaccess_url}")
        lastaccess_resp = self.session.get(lastaccess_url)
        logging.debug(f"Step 2: Lastaccess page HTML for {lastaccess_url}:\n{lastaccess_resp.text}")

        # Step 3: Find <a data-action="showcount">
        soup2 = BeautifulSoup(lastaccess_resp.text, "html.parser")
        showcount_a = soup2.find("a", attrs={"data-action": "showcount"})
        if not showcount_a:
            # If course has few participants, there might be no showcount link
            logging.warning("Showcount <a> element not found or missing href. Returning lastaccess page HTML.")
            return lastaccess_resp.text

        if not showcount_a.has_attr("href"):
            raise Exception("Showcount <a> element missing href.")

        showcount_url = str(showcount_a["href"])
        logging.info(f"Accessing showcount URL: {showcount_url}")
        showcount_resp = self.session.get(showcount_url)
        logging.debug(f"Step 3: Showcount page HTML for {showcount_url}:\n{showcount_resp.text}")
        return showcount_resp.text

    def _get_participants_url(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        # Find any element with data-key="participants"
        container = soup.find(attrs={"data-key": "participants"})
        if not container:
            raise Exception("Element with data-key='participants' not found on course page.")
        # Find a descendant <a> with href
        participants_a = container.find("a", href=True)
        if not participants_a:
            # Try to find any <a> in the subtree
            participants_a = next((a for a in container.descendants if isinstance(a, Tag) and a.name == "a" and a.has_attr("href")), None)
        if not participants_a:
            raise Exception("No <a> descendant with href found under element with data-key='participants'.")
        return str(participants_a["href"])

    def _parse_participants_table(self, html: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", id="participants")
        if not table:
            raise Exception("Participants table with id='participants' not found.")
        participants: List[Dict[str, Any]] = []
        tbody = table.find("tbody")
        if not tbody:
            raise Exception("No <tbody> found in participants table.")

        for row in tbody.find_all("tr"):
            classes = row.get("class")
            if classes is not None and "emptyrow" in list(classes):
                continue
            participant_data = self._parse_participant_row(row)
            participant_data['days'] = self.parse_days(participant_data['acceso'])

            logger.debug(f"Participant {participant_data['user_name']} last access: {participant_data['acceso']} ({participant_data['days']} days)")
            if participant_data['days'] < self.days_without_connection:
                continue
            participants.append(participant_data)

        return participants

    def parse_days(self, acceso: str) -> int:
        if acceso.strip().lower() == "nunca":
            return 9999
        # Match both 'dias' and 'días' (with or without accent)
        match = re.search(r'(\d+)\s*d[ií]as?', acceso, re.IGNORECASE)
        return int(match.group(1)) if match else 0


    def _parse_participant_row(self, row: Tag) -> Dict[str, Any]:
        cells = row.find_all(["td", "th"])
        if not cells or len(cells) < 8:
            raise Exception("Row does not have enough cells to parse participant data.")

        # Name (cell 1)
        name_a = cells[1].find("a")
        if name_a:
            for span in name_a.find_all("span"):
                span.extract()
            name = name_a.get_text(strip=True)
        else:
            name = cells[1].get_text(strip=True)

        # User name (cell 2)
        user_name = cells[2].get_text(strip=True)

        # Email (cell 3)
        email = cells[3].get_text(strip=True)

        # Roles (cell 4): get all text from <a> tags, join with comma
        roles_cell = cells[4]
        roles = ", ".join([a.get_text(strip=True) for a in roles_cell.find_all("a")])
        if not roles:
            roles = roles_cell.get_text(strip=True)

        # Acceso (cell 6)
        acceso = cells[6].get_text(strip=True)

        data = {
            "name": name,
            "user_name": user_name,
            "email": email,
            "roles": roles,
            "acceso": acceso
        }
        return data

