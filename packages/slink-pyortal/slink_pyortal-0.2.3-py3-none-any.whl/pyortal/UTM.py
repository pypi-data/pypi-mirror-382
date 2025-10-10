import requests, datetime

class UTM(object):
	def __init__(self, base_url, cloud_uri):
		self.__base_url = base_url
		self.__cloud_uri = cloud_uri

	########## Vertiport Management ##########
	def list_vertiports(self):
		response = requests.get(f"{self.__cloud_uri}/vertiports")
		vertiports = {}

		if response.status_code == 200:
			for vertiport in response.json():
				vertiports[vertiport["name"]] = vertiport

		return vertiports


	########## Vehicle Management ##########
	def spawn_vehicle(self, registration, spawn_point):
		response = requests.post(
			f"http://{self.__base_url}/sims",
			json={
				"registration": registration,
				"spawn_point": spawn_point
			}
		)

		return response.status_code == 201

	def despawn_vehicle(self, registration):
		response = requests.delete(f"http://{self.__base_url}/vehicles/{registration}")
		return response.status_code == 200


	########## Flight Path Management ##########
	def create_flight_path(self, name, registration, origin, destination, waypoints):
		vertiports = self.list_vertiports()

		response = requests.post(
			f"http://{self.__base_url}/flight-paths",
			json={
			  "name": name,
			  "vehicle": registration,
			  "origin_id": vertiports[origin]["id"],
			  "destination_id": vertiports[destination]["id"],
			  "waypoints": waypoints
			}
		)

		return response.status_code == 201

	def remove_flight_path(self, name):
		response = requests.delete(f"http://{self.__base_url}/flight-paths/{name}")
		return response.status_code == 200


	########## Flight Management ##########
	def book_flight(self, vehicle, mode, type, origin, destination, departure=None, round_trip=False):
		flight_modes = {
			"manual": "0",
			"mission": "1",
			"setpoints": "2"
		}

		mission_types = {
			"delivery": "4",
			"charging": "5",
			"flight_only": "6"
		}

		vertiports = self.list_vertiports()

		payload = {
		  "vehicle": f"http://{self.__base_url}/vehicles/{vehicle}",
		  "flight_mode": flight_modes[mode],
		  "mission_type": mission_types[type],
		  "origin": vertiports[origin]["id"],
		  "destination": vertiports[destination]["id"],
		  "round_trip": round_trip
		}

		if departure:
			payload["departure"] = departure.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

		response = requests.post(f"http://{self.__base_url}/queries", json=payload)

		if response.status_code != 201:
			return False

		query = response.json()

		if len(query["options"]) == 0:
			return None
			
		response = requests.post(
			f"http://{self.__base_url}/reservations",
			json={
			  "query_option": query["options"][0]["number"]
			}
		)

		if response.status_code == 201:
			return response.json()
		else:
			requests.delete(query["self"])
			return None


	def cancel_flight(self, flight):
		response = requests.delete(flight["self"])
		return response.status_code == 200
