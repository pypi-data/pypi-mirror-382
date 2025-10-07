"""
LLM (Large Language Model) client, for communicating with an LLM backend.

Note that running a LLM locally requires a lot of power, and ideally a powerful GPU. Testing
this with CPU mode on a beefy laptop, still takes some 4s just on a very small model.

The server defaults to output suitable for a local server
https://github.com/oobabooga/text-generation-webui, but could be used for other LLM servers too.

See the LLM instructions on that page for how to set up the server. You'll also need
a model file - there are thousands to try out on https://huggingface.co/models (you want Text
Generation models specifically).

# Optional settings (if not given, these defaults are used)

DEFAULT_LLM_HOST = "http://localhost:5000"
DEFAULT_LLM_PATH = "/api/v1/generate"
DEFAULT_LLM_HEADERS = {"Content-Type": "application/json"}
DEFAULT_LLM_PROMPT_KEYNAME = "prompt"
DEFAULT_LLM_REQUEST_BODY = {...}   # see below, this controls how to prompt the LLM server.

"""

import json

from twisted.internet import defer, protocol, reactor
from twisted.internet.defer import inlineCallbacks
from twisted.web.client import Agent, HTTPConnectionPool, _HTTP11ClientFactory
from twisted.web.http_headers import Headers
from twisted.web.iweb import IBodyProducer
from twisted.python import log
from zope.interface import implementer

from cowrie.core.config import CowrieConfig

DEFAULT_LLM_HOST = "http://127.0.0.1:5000"
DEFAULT_LLM_PATH = "/api/v1/generate"
DEFAULT_LLM_HEADERS = {"Content-Type": "application/json"}
DEFAULT_LLM_PROMPT_KEYNAME = "prompt"
DEFAULT_LLM_API_TYPE = ""  # or openai
DEFAULT_LLM_REQUEST_BODY = {
    "max_new_tokens": 250,  # max number of tokens to generate
    "temperature": 0.7,  # higher = more random, lower = more predictable
}


@implementer(IBodyProducer)
class StringProducer:
    """
    Used for feeding a request body to the HTTP client.
    """

    def __init__(self, body):
        self.body = bytes(body, "utf-8")
        self.length = len(body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return defer.succeed(None)

    def pauseProducing(self):
        pass

    def resumeProducing(self):
        pass

    def stopProducing(self):
        pass


class SimpleResponseReceiver(protocol.Protocol):
    """
    Used for pulling the response body out of an HTTP response.
    """

    def __init__(self, status_code, d):
        self.status_code = status_code
        self.buf = b""
        self.d = d

    def dataReceived(self, data):
        self.buf += data

    def connectionLost(self, reason=protocol.connectionDone):
        self.d.callback((self.status_code, self.buf))


class QuietHTTP11ClientFactory(_HTTP11ClientFactory):
    """
    Silences the obnoxious factory start/stop messages in the default client.
    """

    noisy = False


class LLMClient:
    """
    A client for communicating with an LLM server.
    """

    def __init__(self, on_bad_request=None):
        self._conn_pool = HTTPConnectionPool(reactor)
        self._conn_pool._factory = QuietHTTP11ClientFactory

        self.prompt_keyname = CowrieConfig.get(
            "llm", "LLM_PROMPT_KEYNAME", fallback=DEFAULT_LLM_PROMPT_KEYNAME
        )
        self.hostname = CowrieConfig.get("llm", "LLM_HOST", fallback=DEFAULT_LLM_HOST)
        self.pathname = CowrieConfig.get("llm", "LLM_PATH", fallback=DEFAULT_LLM_PATH)
        self.headers = CowrieConfig.get(
            "llm", "LLM_HEADERS", fallback=DEFAULT_LLM_HEADERS
        )
        self.request_body = CowrieConfig.get(
            "llm", "LLM_REQUEST_BODY", fallback=DEFAULT_LLM_REQUEST_BODY
        )
        self.api_type = CowrieConfig.get(
            "llm", "LLM_API_TYPE", fallback=DEFAULT_LLM_API_TYPE
        )
        self.debug = CowrieConfig.getbool("llm", "DEBUG", fallback=False)

        self.agent = Agent(reactor, pool=self._conn_pool)

    def _format_request_body(self, prompt):
        """Structure the request body for the LLM server"""
        request_body = self.request_body.copy()

        # Different formatting based on API type
        if self.api_type == "openai":
            # Format for OpenAI API
            messages = []
            for i, message in enumerate(prompt):
                if i == 0:
                    # First message is our system prompt
                    messages.append({"role": "system", "content": message})
                elif "User:" in message:
                    # User messages
                    content = message.replace("User:", "").strip()
                    messages.append({"role": "user", "content": content})
                elif "System:" in message:
                    # Assistant messages
                    content = message.replace("System:", "").strip()
                    messages.append({"role": "assistant", "content": content})
                else:
                    # Default to user messages
                    messages.append({"role": "user", "content": message})

            request_body[self.prompt_keyname] = messages
        else:
            # Default format for text-generation-webui and similar APIs
            prompt = "\n".join(prompt)
            request_body[self.prompt_keyname] = prompt

        return request_body

    def _handle_llm_response_body(self, response):
        """Get the response body from the response"""
        d = defer.Deferred()
        response.deliverBody(SimpleResponseReceiver(response.code, d))
        return d

    def _handle_llm_error(self, failure):
        """Correctly handle server connection errors"""
        failure.trap(Exception)
        return (500, failure.getErrorMessage())

    def _get_response_from_llm_server(self, prompt):
        """Call the LLM server and handle the response/failure"""
        request_body = self._format_request_body(prompt)

        if self.debug:
            log.msg(f"LLM request body: {request_body}")

        d = self.agent.request(
            b"POST",
            bytes(self.hostname + self.pathname, "utf-8"),
            headers=Headers(self.headers),
            bodyProducer=StringProducer(json.dumps(request_body)),
        )

        d.addCallbacks(self._handle_llm_response_body, self._handle_llm_error)
        return d

    @inlineCallbacks
    def get_response(self, prompt):
        """
        Get a response from the LLM server for the given npc.

        Args:
            prompt (str or list): The prompt to send to the LLM server. If a list,
                this is assumed to be the chat history so far, and will be added to the
                prompt in a way suitable for the api.

        Returns:
            str: The generated text response. Will return an empty string
                if there is an issue with the server, in which case the
                the caller is expected to handle this gracefully.

        """
        status_code, response = yield self._get_response_from_llm_server(prompt)
        if status_code == 200:
            if self.debug:
                log.msg(f"LLM response: {response}")

            response_json = json.loads(response)

            # Different parsing based on API type
            if self.api_type == "openai":
                # OpenAI API response format
                if "choices" in response_json and len(response_json["choices"]) > 0:
                    # Extract the content from the message
                    return response_json["choices"][0]["message"]["content"]
            else:
                # Default format for text-generation-webui and similar
                if "results" in response_json and len(response_json["results"]) > 0:
                    return response_json["results"][0]["text"]

            # If we couldn't parse the response format, log it and return empty
            log.err(f"Could not parse LLM response format: {response}")
            return ""
        else:
            log.err(f"LLM API error (status {status_code}): {response}")
            return ""
