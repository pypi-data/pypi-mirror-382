from requests.auth import AuthBase
import googleapiclient.discovery
from google.oauth2 import service_account

class EMSAPIAuth(AuthBase):
	def __init__(self, service_account_file_path):
		self.__access_token = ""
		self.__google_credentials = service_account.Credentials.from_service_account_file(
			service_account_file_path,
    	scopes=['https://www.googleapis.com/auth/iam']
    )

	def __call__(self, request):
		request.headers["Authorization"] = f"Bearer {self.__get_access_token()}"
		return request

	def __get_access_token(self):
		if not self.__access_token:
			iam_credentials = googleapiclient.discovery.build(
				'iamcredentials',
				'v1',
				credentials=self.__google_credentials
			)

			body = {
				"audience": "451839888097-hckdrer9j5jn03d2dibo9p8j5hirq6n0.apps.googleusercontent.com",
				"includeEmail": True
			}

			service_account = 'projects/-/serviceAccounts/451839888097-compute@developer.gserviceaccount.com'
			response = iam_credentials.projects().serviceAccounts().generateIdToken(name=service_account, body=body).execute()
			self.__access_token = response['token']

		return self.__access_token