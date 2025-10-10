import json, requests, websocket, threading, time, ssl
from .EMSAPIAuth import EMSAPIAuth

class EMS(object):
	def __init__(self, base_url, service_account_file_path):
		self.__base_url = f"{base_url}/internal/v1"
		self.__base_ws_url = f"{base_url}/api/v1"
		self.__auth = EMSAPIAuth(service_account_file_path)
		self.__state = "Off"
		self.__uavs = {}
		self.__zone_statuses = {}

		self.__status_thread = threading.Thread(target=self.__poll_status, daemon=True)
		self.__status_thread.start()

		self.__subscribers = []

	def __del__(self):
		if hasattr(self, "__status_thread"):
			self.__status_thread.join()


	########## Settings Management ##########
	def import_config(self, conf_name):
		# Load specified config file
		try:
			with open(conf_name, "r") as config_file:
				config = json.load(config_file)

				# Write config via API
				for category in config:
					response = requests.put(f"https://{self.__base_url}/{category}/settings/", json=config[category], auth=self.__auth, verify=False)
			
					if response.status_code != 200:
						raise Exception("Failed to import config, code: " + str(response.status_code) + " message: " + str(response.text))
					 
					if category == "mas":
						response = requests.put(f"https://{self.__base_url}/{category}/flightpaths/", json=config[category]["flight_paths"], auth=self.__auth, verify=False)

						if response.status_code != 200:
							raise Exception("Failed to import flightpaths, code: " + str(response.status_code) + " message: " + str(response.text))

			return response.status_code == 200
		except FileNotFoundError:
			return False


	########## Status Management ##########
	def get_state(self):
		return self.__state

	def start(self):
		if self.__state in ["Off", "Stopped"]:
			response = requests.put(f"https://{self.__base_url}/system/controls/start/", json={}, auth=self.__auth, verify=False)
			return response.status_code == 200
		else:
			return False

	def stop(self):
		if self.__state not in ["Off", "Stopped"]:
			response = requests.put(f"https://{self.__base_url}/system/controls/stop/", json={}, auth=self.__auth, verify=False)
			return response.status_code == 200
		else:
			return False

	def restart(self):
		response = requests.put(f"https://{self.__base_url}/system/controls/restart/", json={}, auth=self.__auth, verify=False)
		return response.status_code == 200

	def accept_calibration(self):
		response = requests.put(f"https://{self.__base_url}/calibration/confirm/", json={}, auth=self.__auth, verify=False)
		return response.status_code == 200

	def track(self):
		if self.__state == "Calibrating":
			# Wait for MVS to report sensors
			time.sleep(5)
			
			# Configure EMS sensors so we can accept calibration
			self.configure_sensors()

			# Wait for sensor configuration to take effect
			time.sleep(5)
			
			# Accept PORTAL calibration
			return self.accept_calibration()

	def on_transition(self, callback):
		self.__subscribers.append(callback)

	def get_drone(self, registration):
		if registration not in self.__uavs:
			self.__uavs[registration] = {
				"state": "",
				"status": "",
				"latitude": "",
				"longitude": "",
				"altitude": "",
				"conformance": ""
			}

		return self.__uavs[registration]


	########## Layout and Positioning ##########
	def retrieve_layout(self):
		response = requests.get(f"https://{self.__base_url}/siteplan", auth=self.__auth, verify=False)
		layout = {}

		if response.status_code != 200:
			raise Exception("Failed to retrieve layout, code: " + str(response.status_code) + " message: " + str(response.text))
		
		layout = response.json()
		return layout

	def get_zone(self, id):
		layout = self.retrieve_layout()
		zone = None

		if id in layout["mgs"]["zones"]:
			zone = layout["mgs"]["zones"][id]

			# Compute zone center
			min_latitude = 99999
			max_latitude = 0
			min_longitude = 99999
			max_longitude = 0

			for coordinate in zone["boundary"]:
				if abs(coordinate["latitude"]) < abs(min_latitude):
					min_latitude = coordinate["latitude"]

				if abs(coordinate["latitude"]) > abs(max_latitude):
					max_latitude = coordinate["latitude"]

				if abs(coordinate["longitude"]) < abs(min_longitude):
					min_longitude = coordinate["longitude"]

				if abs(coordinate["longitude"]) > abs(max_longitude):
					max_longitude = coordinate["longitude"]

			zone["center"] = {
				"latitude": (max_latitude+min_latitude)/2,
				"longitude": (max_longitude+min_longitude)/2
			}

		return zone

	def to_global(self, x, y):
		global_coords = {"lat": 0, "lon": 0, "alt": 0}
		
		response = requests.post(f"https://{self.__base_url}/positioning/conversions/global/", json={"x":x, "y":y}, auth=self.__auth, verify=False)
		if response.status_code != 201:
			raise Exception("Failed to convert to global coordinates, code: " + str(response.status_code) + " message: " + str(response.text))
		
		# Get global coordinates
		global_coords["lat"] = response.json()["global"]["lat"]
		global_coords["lon"] = response.json()["global"]["lng"]
		global_coords["alt"] = response.json()["global"]["alt"]

		return global_coords

	def get_zone_statuses(self):
		return self.__zone_statuses


	########## Sensor Management ##########
	def configure_sensors(self):
		response = requests.get(f"https://{self.__base_url}/calibration/sensors/", auth=self.__auth, verify=False)
		
		if response.status_code != 200:
			raise Exception("Failed to retrieve sensors, code: " + str(response.status_code) + " message: " + str(response.text))

		# Configure sensors
		sensors = response.json()
		configuration = {
		"configured": True,
		"offset": {
			"x": 0,
			"y": 0,
			"z": 0
			}
		}

		# Handle different response structures
		if isinstance(sensors, list):
			# If sensors is a list, iterate directly
			for sensor in sensors:
				requests.put(f"https://{self.__base_url}{sensor['self']}/", json=configuration, auth=self.__auth, verify=False)
		elif isinstance(sensors, dict) and 'sensors' in sensors:
			# If sensors is a dict with 'sensors' key
			for sensor in sensors['sensors']:
				requests.put(f"https://{self.__base_url}{sensor['self']}/", json=configuration, auth=self.__auth, verify=False)
		else:
			raise Exception(f"Unexpected sensors response structure: {type(sensors)}")

	########## Helper Methods ##########
	def __poll_status(self):
		wsapp = websocket.WebSocketApp(f"wss://{self.__base_ws_url}/ws/", on_message=self.__process_message)
		wsapp.run_forever(sslopt={'cert_reqs': ssl.CERT_NONE})

	def __process_message(self, wsapp, message):
		payload = json.loads(message)
		if payload["type"] == "status":
			self.__state = payload["data"]["state"]
			for callback in self.__subscribers:
				callback(self.__state)
		elif payload["type"] == "uav":
			for uav in payload["data"]:
				if uav["callsign"] not in self.__uavs:
					self.__uavs[uav["callsign"]] = {
						"state": "",
						"status": "",
						"latitude": "",
						"longitude": "",
						"altitude": "",
						"conformance": ""
					}
				
				self.__uavs[uav["callsign"]]["state"] = uav["state"]
				self.__uavs[uav["callsign"]]["status"] = uav["status"]
				self.__uavs[uav["callsign"]]["latitude"] = uav["position"]["latitude"]
				self.__uavs[uav["callsign"]]["longitude"] = uav["position"]["longitude"]
				self.__uavs[uav["callsign"]]["altitude"] = uav["altitude"]
				self.__uavs[uav["callsign"]]["conformance"] = uav["conformance_status"]