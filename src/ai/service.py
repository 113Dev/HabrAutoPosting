import google.generativeai as gemini

from config import promt
from db.models import User


DEFAULT_GEMINI_MODEL = "gemini-2.5-flash-lite"


def get_missing_user_ai_settings(user: User | None) -> list[str]:
	"""Возвращает список отсутствующих AI-настроек пользователя."""
	if user is None:
		return ["API ключ", "модель", "промпт", "ID группы"]

	missing_settings: list[str] = []

	if not user.gemini_api:
		missing_settings.append("API ключ")

	if not user.gemini_model:
		missing_settings.append("модель")

	if not user.prompt:
		missing_settings.append("промпт")

	if not user.target_chat_id:
		missing_settings.append("ID группы")

	return missing_settings


class UserGeminiService:
	"""Инкапсулирует Gemini-конфиг конкретного пользователя."""

	def __init__(
		self,
		api_key: str | None = None,
		model_name: str = DEFAULT_GEMINI_MODEL,
		prompt: str = promt,
	) -> None:
		self.api_key = api_key
		self.model_name = model_name or DEFAULT_GEMINI_MODEL
		self.prompt = prompt or promt

	@classmethod
	def from_user(cls, user: User | None) -> "UserGeminiService":
		"""Создаёт сервис из пользовательских настроек БД."""
		if user is None:
			return cls()

		return cls(
			api_key=user.gemini_api,
			model_name=user.gemini_model,
			prompt=user.prompt,
		)

	def build_model(self) -> gemini.GenerativeModel:
		"""Создаёт Gemini-модель с пользовательскими настройками."""
		if not self.api_key:
			raise ValueError("Gemini API ключ не установлен")

		gemini.configure(api_key=self.api_key)
		return gemini.GenerativeModel(
			self.model_name,
			system_instruction=self.prompt,
		)

	async def generate_text(self, text: str) -> str:
		"""Генерирует ответ через пользовательскую Gemini-модель."""
		model = self.build_model()
		response = await model.generate_content_async(text)
		return str(response.text)