from ya_business_api.core.constants import INVALID_TOKEN_STATUSES, PASSPORT_URL, Cookie
from ya_business_api.core.exceptions import CSRFTokenError, AuthenticationError, CaptchaError

from requests.sessions import Session
from requests.models import Response


class SyncAPIMixin:
	session: Session

	def __init__(self, session: Session, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)

		self.session = session

	@staticmethod
	def check_response(response: Response) -> None:
		if response.status_code == 302 and getattr(response.next, 'url', "").startswith(PASSPORT_URL):
			raise AuthenticationError()

		if response.status_code in INVALID_TOKEN_STATUSES:
			raise CSRFTokenError()

		if response.status_code == 429 and response.headers.get('need-captcha') == "1":
			raise CaptchaError()

		assert response.status_code == 200

	def set_i_cookie(self) -> None:
		"""
		Sets a stub value to the "i" cookie if it not specified.
		"""
		if Cookie.I.value not in self.session.cookies.keys():
			self.session.cookies.set(Cookie.I.value, "")
