import copy
import logging
from abc import ABC
from typing import Dict, List, Optional, Union

from afnio.logging_config import configure_logging
from afnio.tellurio._client_manager import get_default_clients
from afnio.tellurio._eventloop import run_in_background_loop
from afnio.tellurio._model_registry import register_model
from afnio.tellurio.consent import check_consent

INITIAL_COST = {"cost": {"amount": 0.0, "currency": "USD"}}


# Configure logging
configure_logging()
logger = logging.getLogger(__name__)


class BaseModel(ABC):
    """
    An abstraction for a model.
    """

    def __init__(
        self,
        provider: str = None,
        config: Optional[dict] = None,
        usage: Optional[dict] = None,
    ):
        self.provider = provider
        self._config = config or {}
        self._usage = usage or {}
        self._usage.update(copy.deepcopy(INITIAL_COST))
        self.model_id = None

        # Request user consent before sending sensitive info to the server
        check_consent()

        try:
            # Get the singleton websocket client
            _, ws_client = get_default_clients()

            payload = {
                "class_type": self.__class__.__name__,
                "provider": self.provider,
                "config": self.get_config(),
                "usage": self.get_usage(),
            }
            response = run_in_background_loop(ws_client.call("create_model", payload))
            if "error" in response:
                raise RuntimeError(
                    response["error"]["data"].get("exception", response["error"])
                )

            logger.debug(f"LM model created and shared with the server: {self!r}")

            model_id = response["result"].get("model_id")
            if not model_id:
                raise RuntimeError(
                    f"Server did not return a model_id "
                    f"for payload: {payload!r}, response: {response!r}"
                )
            self.model_id = model_id
            register_model(self)
        except Exception as e:
            logger.error(f"Failed to share LM model with the server: {e}")
            raise

    def get_provider(self) -> Optional[str]:
        """Returns the model provider name."""
        return self.provider

    def get_config(self) -> Dict[str, Union[str, float, int]]:
        """
        Returns the model configuration.
        This includes the model name, temperature, max tokens, and other
        parameters that are used to configure the model's behavior.

        Returns:
            dict: A dictionary containing the model's configuration parameters.
        """
        return self._config

    def update_usage(self, usage: Dict[str, int], model_name: str = None) -> None:
        """
        Updates the internal token usage statistics and cost.

        Each model provider (e.g., OpenAI, Anthropic) may have a different usage format.
        This method should be implemented by subclasses to ensure correct parsing
        and aggregation of token usage.

        Behavior:
            - If `model_name` is provided, the method dynamically calculates and updates
              the cost based on the usage metrics and the pricing for the specified
              model.
            - If `model_name` is None, the method copies the cost value directly from
              the `usage` dictionary (if present), which is typically used when
              restoring state from a checkpoint.

        Args:
            usage (Dict[str, int]): A dictionary containing token usage metrics,
                such as `prompt_tokens`, `completion_tokens`, and `total_tokens`.
            model_name (str, optional): The name of the model for which the usage
                is being updated. If None, cost is copied from usage if available.

        Raises:
            NotImplementedError: If called on the base class without an implementation.
        """
        raise NotImplementedError

    def get_usage(self) -> Dict[str, int]:
        """
        Retrieves the current token usage statistics and cost (in USD).

        Returns:
            Dict[str, int]: A dictionary containing cumulative token usage
                statistics since the model instance was initialized.

        Example:
            >>> model.get_usage()
            {
                'prompt_tokens': 1500,
                'completion_tokens': 1200,
                'total_tokens': 2700,
                'cost': {'amount': 12.00, 'currency': 'USD'}
            }
        """
        return self._usage.copy()

    def clear_usage(self) -> None:
        """
        Clears the token usage statistics.

        This resets all numerical values in the usage dictionary to zero (including
        nested values), while preserving the dictionary structure.
        """

        try:
            # Get the singleton websocket client
            _, ws_client = get_default_clients()

            payload = {
                "model_id": self.model_id,
            }
            response = run_in_background_loop(
                ws_client.call("clear_model_usage", payload)
            )
            if "error" in response:
                raise RuntimeError(
                    response["error"]["data"].get("exception", response["error"])
                )

            model_id = response["result"].get("model_id")
            if not model_id:
                raise RuntimeError(
                    f"Server did not return a model_id "
                    f"for payload: {payload!r}, response: {response!r}"
                )

            logger.debug(f"LM model usage cleared on the server: {self!r}")
        except Exception as e:
            logger.error(f"Failed to clear LM model usage on the server: {e}")
            raise

    def __deepcopy__(self, memo):
        """
        Custom deepcopy to save only the class type and metadata like usage.
        """
        if id(self) in memo:
            return memo[id(self)]
        # Save only the class type and any necessary metadata (e.g., usage details)
        cls_copy = {
            "class_type": self.__class__.__name__,
            "provider": self.provider,
            "usage": self.get_usage(),
        }

        # Store the copied object in memo before returning it
        memo[id(self)] = cls_copy
        return cls_copy


# TODO: handle caching
class TextCompletionModel(BaseModel):
    """
    An abstraction for a language model that accepts a prompt composed of a single
    text input and generates a textual completion.
    """

    def __init__(self, provider: str = None, **kwargs):
        super().__init__(provider=provider, **kwargs)

    async def acomplete(self, prompt: str, **kwargs) -> str:
        """
        Asynchronous method to generate a completion for the given prompt.

        Args:
            prompt (str): The input text for which the model should generate
                a completion.
            **kwargs: Additional parameters to configure the model's behavior during
                chat completion. This may include options such as:
                - model (str): The model to use (e.g., "gpt-4o").
                - temperature (float): Amount of randomness injected into the response.
                - max_completion_tokens (int): Maximum number of tokens to generate.
                - etc.

                For a complete list of supported parameters for each model, refer to the
                respective API documentation.

        Returns:
            str: A string containing the generated completion.
        """
        raise NotImplementedError

    def complete(self, prompt: str, **kwargs) -> str:
        """
        Synchronous method to generate a completion for the given prompt.

        Args:
            prompt (str): The input text for which the model should generate
                a completion.
            **kwargs: Additional parameters to configure the model's behavior during
                chat completion. This may include options such as:
                - model (str): The model to use (e.g., "gpt-4o").
                - temperature (float): Amount of randomness injected into the response.
                - max_completion_tokens (int): Maximum number of tokens to generate.
                - etc.

                For a complete list of supported parameters for each model, refer to the
                respective API documentation.

        Returns:
            str: A string containing the generated completion.
        """
        raise NotImplementedError


# TODO: handle caching
class ChatCompletionModel(BaseModel):
    """
    An abstraction for a language model that accepts a prompt composed of an array
    of messages containing instructions for the model. Each message can have a
    different role, influencing how the model interprets the input.
    """

    def __init__(self, provider: str = None, **kwargs):
        super().__init__(provider=provider, **kwargs)

    # TODO: Add link to `API documentation` for kwargs of each supported model
    async def achat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Asynchronous method to handle chat-based interactions with the model.

        Args:
            messages (List[Dict[str, str]]): A list of messages, where each message
                is represented as a dictionary with "role" (e.g., "user", "system")
                and "content" (the text of the message).
            **kwargs: Additional parameters to configure the model's behavior during
                chat completion. This may include options such as:
                - model (str): The model to use (e.g., "gpt-4o").
                - temperature (float): Amount of randomness injected into the response.
                - max_completion_tokens (int): Maximum number of tokens to generate.
                - etc.

                For a complete list of supported parameters for each model, refer to the
                respective API documentation.

        Returns:
            str: A string containing the model's response to the chat messages.
        """
        raise NotImplementedError

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Synchronous method to handle chat-based interactions with the model.

        Args:
            messages (List[Dict[str, str]]): A list of messages, where each message
                is represented as a dictionary with "role" (e.g., "user", "system")
                and "content" (the text of the message).
            **kwargs: Additional parameters to configure the model's behavior during
                chat completion. This may include options such as:
                - model (str): The model to use (e.g., "gpt-4o").
                - temperature (float): Amount of randomness injected into the response.
                - max_completion_tokens (int): Maximum number of tokens to generate.
                - etc.

                For a complete list of supported parameters for each model, refer to the
                respective API documentation.

        Returns:
            str: A string containing the model's response to the chat messages.
        """
        raise NotImplementedError


# TODO: handle caching
class EmbeddingModel(BaseModel):
    """
    An abstraction for a model that generates embeddings for input texts.
    """

    def __init__(self, provider: str = None, **kwargs):
        super().__init__(provider=provider, **kwargs)

    async def aembed(self, input: List[str], **kwargs) -> List[List[float]]:
        """
        Asynchronous method to generate embeddings for the given input texts.

        Args:
            input (List[str]): A list of input strings for which embeddings
                should be generated.
            **kwargs: Additional parameters to configure the model's behavior during
                chat completion. This may include options such as:
                - model (str): The model to use (e.g., "gpt-4o").
                - temperature (float): Amount of randomness injected into the response.
                - max_completion_tokens (int): Maximum number of tokens to generate.
                - etc.

                For a complete list of supported parameters for each model, refer to the
                respective API documentation.

        Returns:
            List[List[float]]: A list of embeddings, where each embedding is represented
                as a list of floats corresponding to the input strings.
        """
        raise NotImplementedError

    def embed(self, input: List[str], **kwargs) -> List[List[float]]:
        """
        Synchronous method to generate embeddings for the given input texts.

        Args:
            input (List[str]): A list of input strings for which embeddings
                should be generated.
            **kwargs: Additional parameters to configure the model's behavior during
                chat completion. This may include options such as:
                - model (str): The model to use (e.g., "gpt-4o").
                - temperature (float): Amount of randomness injected into the response.
                - max_completion_tokens (int): Maximum number of tokens to generate.
                - etc.

                For a complete list of supported parameters for each model, refer to the
                respective API documentation.

        Returns:
            List[List[float]]: A list of embeddings, where each embedding is represented
                as a list of floats corresponding to the input strings.
        """
        raise NotImplementedError
