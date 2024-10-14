from datetime import datetime, timedelta
from lxml import etree
from epg import *
import sqlite3
import sys
import threading
import json
from loguru import logger
from contextlib import closing


class EPGConstructor:
    """Constructs and updates the EPG XML file."""

    def __init__(self, file_name="epg.xml"):
        """Initializes EPGConstructor with channel data and file name."""
        self.root = etree.Element("tv")
        self.file_name = file_name
        self._initialize_channels()

    def _initialize_channels(self):
        """Initializes channel elements in the XML structure from the database."""
        conn = sqlite3.connect("epg.db")
        with closing(conn) as conn:
            cursor = conn.cursor()
            query = """
                SELECT DISTINCT tvg_id, tvg_name FROM programmes
            """
            cursor.execute(query)
            channels = cursor.fetchall()

            for tvg_id, tvg_name in channels:
                channel_element = etree.SubElement(self.root, "channel", id=tvg_id)
                etree.SubElement(channel_element, "display-name", lang="zh").text = (
                    tvg_name
                )

    def update_programmes(self):
        """Fetches and updates programmes from the database to the XML file."""
        conn = sqlite3.connect("epg.db")
        with closing(conn) as conn:
            cursor = conn.cursor()

            # Calculate date range
            now = datetime.now()
            seven_days_ago = (now - timedelta(days=7)).strftime("%Y%m%d%H%M%S")

            query = """
                SELECT tvg_id, title, start, stop FROM programmes
                WHERE start >= ?
            """
            cursor.execute(query, (seven_days_ago,))
            programmes = cursor.fetchall()

        # Add programmes to the XML
        for tvg_id, title, start, stop in programmes:
            programme_element = etree.SubElement(
                self.root,
                "programme",
                channel=tvg_id,
                start=start + " +0800",
                stop=stop + " +0800",
            )
            etree.SubElement(programme_element, "title", lang="zh").text = title

        # Write XML to file
        etree.ElementTree(self.root).write(
            self.file_name, pretty_print=True, xml_declaration=True, encoding="UTF-8"
        )


class EPGUpdater:
    """Manages the process of updating the EPG data from various sources."""

    def __init__(self, file_path="channel.json"):
        """Initializes EPGUpdater with logging and channel configuration."""
        self._setup_logging()
        self.channels = self._load_channels(file_path)
        self.epg_functions = self._initialize_epg_functions()
        self.db_lock = threading.Lock()

    def _setup_logging(self):
        """Sets up logging configuration."""
        logger.remove()
        logger.add(sys.stdout, level="INFO")
        logger.add(
            f"logs/{datetime.now():%Y-%m-%d}.log", level="INFO", rotation="00:00"
        )

    def _load_channels(self, file_path):
        """Loads channel configuration from a JSON file."""
        with open(file_path, "r") as file:
            return json.load(file)

    def _initialize_epg_functions(self):
        """Initializes EPG functions for different sources."""
        return {
            "4gtv": UpdateFrom4GTV().fetch_programs,
            "astro": UpdateFromAstro().fetch_programs,
            "bfgd": UpdateFromBFGD().fetch_programs,
            "cctv": UpdateFromCCTV().fetch_programs,
            "ctitv": UpdateFromCtiTV().fetch_programs,
            "elta": UpdateFromELTA().fetch_programs,
            "entertainment": UpdateFromEntertainment().fetch_programs,
            "gdtv": UpdateFromGDTV().fetch_programs,
            "hoy": UpdateFromHOY().fetch_programs,
            "live": UpdateFromLive().fetch_programs,
            "lotus": UpdateFromLotus().fetch_programs,
            "mewatch": UpdateFromMeWatch().fetch_programs,
            "movistarplus": UpdateFromMoviStarPlus().fetch_programs,
            "mytvsuper": UpdateFromMyTVSuper().fetch_programs,
            "now": UpdateFromNow().fetch_programs,
            "plex": UpdateFromPlex().fetch_programs,
            "rthk": UpdateFromRTHK().fetch_programs,
            "scgd": UpdateFromSCGD().fetch_programs,
            "singtel": UpdateFromSingtel().fetch_programs,
            "sky": UpdateFromSky().fetch_programs,
            "tbc": UpdateFromTBC().fetch_programs,
            "tv24": UpdateFromTV24().fetch_programs,
            "tvbs": UpdateFromTVBS().fetch_programs,
            "tvmao": UpdateFromTVMao().fetch_programs,
            "tvpassport": UpdateFromTVPassport().fetch_programs,
            "vercel": UpdateFromVercel().fetch_programs,
            "viutv": UpdateFromViuTV().fetch_programs,
        }

    def _save_programmes(self, programmes):
        """Saves the fetched programmes to the database, removing old records if necessary."""
        with self.db_lock:
            conn = sqlite3.connect("epg.db")
            with closing(conn) as conn:
                with closing(conn.cursor()) as cursor:
                    for tvg_id, (tvg_name, programme_list) in programmes.items():
                        if not programme_list:
                            continue

                        # Find the minimum start time in the programme list
                        min_start_time = min(
                            programme["start"] for programme in programme_list
                        )

                        # Delete records with start time greater than the minimum start time
                        cursor.execute(
                            """
                            DELETE FROM programmes
                            WHERE tvg_id = ? AND start > ?
                        """,
                            (tvg_id, min_start_time),
                        )

                        # Insert or replace new records
                        for programme in programme_list:
                            cursor.execute(
                                """
                                INSERT OR REPLACE INTO programmes (tvg_id, tvg_name, title, start, stop)
                                VALUES (?, ?, ?, ?, ?)
                            """,
                                (
                                    tvg_id,
                                    tvg_name,
                                    programme["title"],
                                    programme["start"],
                                    programme["stop"],
                                ),
                            )

                    conn.commit()

    def _fetch_epg_for_source(self, source, channels):
        """Fetches EPG data for a specific source and saves it to the database."""
        programmes = {}
        for channel in channels.values():
            logger.info(f"[{source}] {channel['tvg-name']}")
            try:
                fetched_programmes = self.epg_functions[source](channel["epg-id"])
                programmes[channel["tvg-id"]] = (
                    channel["tvg-name"],
                    fetched_programmes,
                )
            except Exception as e:
                logger.error(f"[{source}] {channel['tvg-name']} - {e}")
        self._save_programmes(programmes)

    def update_epg(self):
        """Fetches and updates EPG data for all sources."""
        sources = []
        threads = []

        # Prepare and start threads for fetching EPG data
        for source, channels in self.channels.items():
            sources.append(source)
            thread = threading.Thread(
                target=self._fetch_epg_for_source, args=(source, channels)
            )
            thread.start()
            threads.append(thread)

        # Wait for all threads to complete
        for thread in threads:
            thread.join()


def run():
    """Main entry point for running the EPG update."""
    updater = EPGUpdater()
    updater.update_epg()

    """ Construct and update the EPG XML """
    constructor = EPGConstructor()
    constructor.update_programmes()


if __name__ == "__main__":
    run()
