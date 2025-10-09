from semantha_sdk.model.summarization import Summarization
from semantha_sdk.model.summarization import SummarizationSchema
from semantha_sdk.model.summarylength_enum import SummarylengthEnum
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class SummarizationsEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/summarizations"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/summarizations"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    
    def post(
        self,
        texts: List[str] = None,
        topic: str = None,
        language: str = None,
        temperature: float = None,
        summarylength: SummarylengthEnum = None,
        promptid: str = None,
    ) -> Summarization:
        """
        Generates a summary for given number of texts. If topic is supplied summarization is generated for this topic
        Args:
        texts (List[str]): List of texts which are summarized.
    topic (str): Set the topic which is used to summarize the given texts.
    language (str): Change the language of the summary text, if not set the language of the domain is used.
            Supported Languages:
            "ar", "cs", "da", "de", "en", "es", "el", "fr", "fi", "hu", "hr",
            "it", "ja", "ko", "nl", "no", "pl", "pt", "ro", "ru", "sk", "sl",
            "sv", "tr", "zh"
    temperature (float): Temperature regulates the unpredictability of a language model's output. With higher temperature settings, outputs become more creative and less predictable.
    summarylength (SummarylengthEnum): Influences the length of the returned summary. Values are 'SHORT, 'MEDIUM', 'LONG'
    promptid (str): Id of the prompt to generate a summary, other parameters are ignored.
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            body={
                "texts": texts,
                "topic": topic,
                "language": language,
                "temperature": temperature,
                "summarylength": summarylength,
                "promptid": promptid,
            },
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(SummarizationSchema)

    
    
    