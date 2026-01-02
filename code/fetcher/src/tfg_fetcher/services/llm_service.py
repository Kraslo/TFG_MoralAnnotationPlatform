from os import getenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from tfg_fetcher.utils.logging_config import get_logger

logger = get_logger(__name__)


class LLMChat:
    """
    Class to handle LLM operations via LangChain (modern API, no deprecated LLMChain)
    """

    def __init__(self):
        # Initialize the chat model
        self._llm = ChatOpenAI(
            api_key=getenv("OPENROUTER_API_KEY"),
            base_url=getenv("OPENROUTER_BASE_URL"),
            model=getenv("MODEL_NAME"),
        )

        # Check if user has credits
        credits = self._llm.get_credits()
        self.online = credits > 0

        if credits is not None:
            logger.info(f"LLM initialized. Remaining credits: {credits}")
            self._credits = credits
        elif credits <= 0:
            logger.error("LLM initialized. No remaining credits.")
            self._credits = 0
            raise Exception("No remaining credits for LLM usage.")
        else:
            logger.warning("LLM initialized. Could not retrieve credits.")

        # Define the prompt template
        self._prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpul assistant that translates texts accurately while preserving tone and meaning.",
                ),
                ("user", "{question}"),
            ]
        )

        # Create the runnable chain (prompt → llm)
        self._chain = self._prompt | self._llm

    def translate_text_llm(self, text: str) -> str:
        """
        Translates the given text to English using the instantiated LLM.
        """
        question = (
            f"Translate the following text to English while keeping "
            f"the original meaning and writing style: {text}"
        )
        if self.online is False:
            raise Exception("LLM is offline due to insufficient credits.")

        try:
            result = self._chain.invoke({"question": question})
            # Modern API returns a ChatMessage object, extract text
            return result.content if hasattr(result, "content") else str(result)
        except Exception as e:
            logger.error(f"There was an error invoking the LLM: {e}")
            raise e
