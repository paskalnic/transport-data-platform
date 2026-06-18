import os 
from loguru import logger
import requests 
import json 
import datetime as dt
from google.cloud import storage
from dotenv import load_dotenv


load_dotenv()

SNCF_API_KEY = os.getenv("SNCF_API_KEY")
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
BASE_URL = "https://api.sncf.com/v1/coverage/sncf"

# Gares principales qu'on va surveiller
STATIONS = {
    "paris_montparnasse": "stop_area:SNCF:87391003",
    "paris_lyon":         "stop_area:SNCF:87686006",
    "paris_nord":         "stop_area:SNCF:87271007",
    "paris_est":          "stop_area:SNCF:87113001",
    "bordeaux":           "stop_area:SNCF:87581009",
    "lyon_partdieu":      "stop_area:SNCF:87723197",
    "marseille":          "stop_area:SNCF:87751008",
    "lille":              "stop_area:SNCF:87286005",
}

class SNCFClient:
    """Client pour l'API SNCF Navitia"""

    # Constructor
    def __init__(self):
        self.session= requests.Session()
        # No password required , hence ""
        self.session.auth = (SNCF_API_KEY, "")
        logger.info("SNCFClient initialized")

    def get(self, endpoint: str, params: dict = None) -> dict:
        try:
            url = BASE_URL +"/"+ endpoint
            r = self.session.get(url,params=params,timeout=30)
            r.raise_for_status() 
            return r.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            raise
        except requests.exceptions.Timeout:
            logger.error("Timeout!")
            raise
    
    def get_departures(self, station_id: str, count: int = 50) -> dict:
            endpoint = f"stop_areas/{station_id}/departures"
            params = {"count": count}
            logger.info(f"Récupération des départs pour {station_id}")
            return self.get(endpoint, params)

    def get_disruptions(self, count: int = 100) -> dict:
        logger.info("Récupération des perturbations")
        return self.get("disruptions", {"count": count})

    def get_stop_areas(self, count: int = 100) -> dict:
        logger.info("Récupération des gares")
        return self.get("stop_areas", {"count": count})
    
class GCSUploader:
    """Client pour l'API GCS"""

    def __init__(self):
        """0Auth2 being handled automatically
           with refreshed tokens etc..
           Client read GOOGLE CREDENTIALS in .env file
        """
        self.client = storage.Client()
        self.bucket = self.client.bucket(GCP_BUCKET_NAME)
        logger.info(f"GCSUploader connected to bucket {GCP_BUCKET_NAME}")
    
    def upload(self,data,folder,filename):
        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"raw/{folder}/{timestamp}_{filename}.json"
        
        blob = self.bucket.blob(path)
        # We transform the dictionnary into a sring and we
        # keep special characters intact with ensure ascii
        blob.upload_from_string(
            json.dumps(data,ensure_ascii=False, indent=2),
            content_type= "application/json"
        )
        logger.info(f"GCS file uploaded at {path}")
        return path

def run_ingestion():
    client = SNCFClient()
    uploader = GCSUploader()
    for gare,station_id in STATIONS.items():
        departures = client.get_departures(station_id = station_id)
        uploader.upload(data= departures,folder = "departures",filename = gare )
        logger.info(f"Departures for {gare} loaded into GCS")
    disruptions = client.get_disruptions()
    uploader.upload(disruptions,"disruptions","disruptions")
    logger.info("Disruptions loaded ino GCS")
    stop_areas= client.get_stop_areas()
    uploader.upload(stop_areas,"stop_areas","stop_areas")
    logger.info("Stop_areas loaded into GCS")

if __name__ == "__main__":
    run_ingestion()


    

