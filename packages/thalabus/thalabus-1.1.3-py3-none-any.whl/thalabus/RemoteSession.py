import aiohttp
import json
import asyncio
from typing import List, Any
from time import sleep
from thalabus.Log import log, INFO, DEBUG, WARNING, ERROR, FATAL, log_plan

BLAZOR_PROTOCOL = "http"
BLAZOR_HOSTNAME = "localhost"
BLAZOR_PORT = 5210
BLAZOR_SSL_CERTIFICATE_VERIFICATION = False
TIMEOUT_SEC = 600

class ContainerMessage:
    msg_message: str = None
    msg_is_error: bool = False

    def __init__(self, message, is_error):
        self.msg_message = message
        self.msg_is_error = is_error

class RemotePlan:
    name:str = None

    def __init__(self, name:str):
        self.name = name
        return    

    def from_json(self, json_data: dict):
        self.plan_name = json_data.get("plan_name")
        self.plan_description = json_data.get("plan_description")
        self.plan_domain = json_data.get("plan_domain")
        self.plan_focus = json_data.get("plan_focus")
        self.plan_default_language = json_data.get("plan_default_language")
        self.plan_language_in_use = json_data.get("plan_language_in_use")
        self.plan_document_ids = json_data.get("plan_document_ids")
        self.plan_loaded_documents = json_data.get("plan_loaded_documents", None)
        self.plan_datasets = json_data.get("plan_datasets")
        self.plan_revision = json_data.get("plan_revision")
        # self.plan_goal.from_json(json_data.get("plan_goal"))

class Session:
    s_id: str = None
    s_title: str = None
    s_endpoint_base: str = None
    s_userId: str = None
    s_plan: RemotePlan = None
    s_activeLlmConfigurationName: str = None
    s_api_token: str = None

    def __init__(self, data:dict=None):
        self.s_id = data.get('id')
        self.s_title = data.get('title')
        self.s_endpoint_base = data.get('endpoint_base')
        self.s_userId = data.get('user_id')
        self.s_activeLlmConfigurationName = data.get('active_llm_configuration_name')
        self.s_api_token = data.get('api_token')

        plan_data = data.get('plan')
        plan = RemotePlan("remote plan")
        if plan_data is not None:
            plan.from_json(plan_data)
        self.s_plan = plan

class RemoteSession:
    rs_endpoint_base: str = None
    rs_session: Session = None
    rs_user_id = None
    __blazor_protocol = BLAZOR_PROTOCOL
    __blazor_hostname = BLAZOR_HOSTNAME
    __blazor_port = BLAZOR_PORT

    def __init__(self, endpoint=None, user_id="test"):
        if endpoint:
            self.rs_endpoint_base = endpoint
            self.rs_endpoint_base = self.rs_endpoint_base.replace("localhost", RemoteSession.__blazor_hostname)
        else:
            self.rs_endpoint_base = f"{RemoteSession.__blazor_protocol}://{RemoteSession.__blazor_hostname}:{RemoteSession.__blazor_port}/v1"
        self.rs_session = None
        self.rs_user_id = user_id

    @property
    def id(self) -> str:
        return self.rs_session.s_id if self.rs_session else None

    @property
    def title(self) -> str:
        return self.rs_session.s_title if self.rs_session else None

    @property
    def user_id(self) -> str:
        return self.rs_session.s_userId if self.rs_session else None

    @property
    def plan(self):
        return self.rs_session.s_plan if self.rs_session else None

    @property
    def active_llm_configuration_name(self) -> str:
        return self.rs_session.s_activeLlmConfigurationName if self.rs_session else None

    @property
    def api_token(self) -> str:
        return self.rs_session.s_api_token if self.rs_session else None

    async def connect(self, endpoint_base:str, session_id:str, token:str) -> ContainerMessage:
        msg = None

        if self.rs_session is None:
            self.rs_endpoint_base = endpoint_base
            self.rs_endpoint_base = self.rs_endpoint_base.replace("localhost", RemoteSession.__blazor_hostname)

            try:
                # Ping the machine
                ping_endpoint = f"{self.rs_endpoint_base}/api/ping"
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=BLAZOR_SSL_CERTIFICATE_VERIFICATION)) as client:
                    async with client.get(ping_endpoint) as response:
                        response.raise_for_status()
                        log(DEBUG, f"Connected to the machine: {self.rs_endpoint_base}")

                    session_endpoint = f"{self.rs_endpoint_base}/sessions/session/{session_id}?token={token}"
                    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=BLAZOR_SSL_CERTIFICATE_VERIFICATION)) as client:
                        async with client.get(session_endpoint) as response:
                            response.raise_for_status()
                            response_body = await response.text()
                            session_data = json.loads(response_body)
                            if not session_data:
                                raise Exception("Could not deserialize the session", is_error=True)
                            self.rs_session = Session(session_data)

                    msg = ContainerMessage(self.rs_session.s_id, False)

            except aiohttp.ClientError as e:
                log(ERROR, f"RemoteSession.connect(): Could not connect: {e}")
                msg = ContainerMessage(str(e), True)
            except Exception as e:
                log(ERROR, f"RemoteSession.connect(): Exception while connecting: {e}")
                msg = ContainerMessage(str(e), True)
        else:
            msg = ContainerMessage("Session is already connected", False)

        return msg

    async def get_plan(self) -> RemotePlan:
        if self.rs_session is None:
            raise RuntimeError("Session is not connected.")
        
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=BLAZOR_SSL_CERTIFICATE_VERIFICATION)) as client:
                current_revision = f"&revision={self.rs_session.s_plan.plan_revision}" if self.rs_session.s_plan else ""
                endpoint = f"{self.rs_endpoint_base}/sessions/session/{self.rs_session.s_id}/plan?token={self.rs_session.s_api_token}{current_revision}"
                async with client.get(endpoint) as response:
                    if response.status == 304:
                        # Not modified, return the current plan
                        return self.rs_session.s_plan
                    
                    # Get the plan, update the current plan
                    response.raise_for_status()
                    response_body = await response.text()
                    if response_body is None or len(response_body) == 0:
                        return None
                    
                    plan = RemotePlan("remote plan")
                    plan_json = json.loads(response_body)
                    plan.from_json(plan_json)
                    self.rs_session.s_plan = plan
                    return plan
        except aiohttp.ClientError as e:
            log(ERROR, f"RemoteSession.get_plan(): Could not connect: {e}")
            return None
        except Exception as e:
            log(ERROR, f"RemoteSession.get_plan(): Exception while getting the plan: {e}")
            return None
        
    async def create(self, endpoint_base:str, session_id:str, token:str) -> ContainerMessage:
        msg = None
        if self.rs_session is None:
            try:
                # Ping the machine
                self.rs_endpoint_base = endpoint_base
                self.rs_endpoint_base = self.rs_endpoint_base.replace("localhost", RemoteSession.__blazor_hostname)
                ping_endpoint = f"{self.rs_endpoint_base}/api/ping"
                log(DEBUG, f"Pinging the machine to see if it's alive: {ping_endpoint}...")
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=BLAZOR_SSL_CERTIFICATE_VERIFICATION)) as client:
                    async with client.get(ping_endpoint) as response:
                        response.raise_for_status()
                log(DEBUG, f"Connected to the machine: {self.rs_endpoint_base}")

                first_try = True
                give_up = False
                while not give_up:
                    session_endpoint = f"{self.rs_endpoint_base}/sessions/session/{session_id}?token={token}"
                    log(DEBUG, f"Connecting to the session: {self.rs_endpoint_base} '{session_id}'...")
                    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=BLAZOR_SSL_CERTIFICATE_VERIFICATION)) as client:
                        async with client.get(session_endpoint) as response:
                            if first_try and response.status != 200:
                                # Create new session
                                create_endpoint = f"{self.rs_endpoint_base}/sessions/session?userId={self.rs_user_id}&token={token}&sessionId={session_id}"
                                async with client.post(create_endpoint) as create_response:
                                    create_response.raise_for_status()
                                    response_body = await create_response.text()
                                    if not response_body:
                                        raise Exception("Response content is null or empty", is_error=True)
                                    session_data = json.loads(response_body)
                                    if not session_data:
                                        raise Exception("Could not deserialize the session", is_error=True)
                                    self.rs_session = Session(session_data)
                                    msg = ContainerMessage(self.rs_session.s_id, False)
                                    session_id = self.rs_session.s_id
                                first_try = False
                                await asyncio.sleep(2)
                            else:
                                response.raise_for_status()
                                response_body = await response.text()
                                session_data = json.loads(response_body)
                                if not session_data:
                                    raise Exception("Could not deserialize the session", is_error=True)
                                self.rs_session = Session(session_data)
                                give_up = True
                                msg = ContainerMessage(self.rs_session.s_id, False)
                                log(DEBUG, "Connected to the remote session.")

                                # reset the session, like a new session
                                log(DEBUG, f"Resetting the session: {self.rs_session.s_id}...")
                                await asyncio.sleep(2)
                                await self.clear(10)
                                log(DEBUG, f"Session '{self.rs_session.s_id}' was reset.")

            except aiohttp.ClientError as e:
                log(ERROR, f"RemoteSession.connect(): Could not connect: {e}")
                msg = ContainerMessage(str(e), True)
            except Exception as e:
                log(ERROR, f"RemoteSession.connect(): Exception while connecting: {e}")
                msg = ContainerMessage(str(e), True)
        
        log(DEBUG, f"Connected to the remote session: {self.rs_session.s_id}")
        return msg

    def disconnect(self) -> None:
        log(DEBUG, f"Disconnecting from the session: {self.rs_session.s_id if self.rs_session else None}")
        self.rs_session = None

    async def destroy(self) -> ContainerMessage:
        if self.rs_session:
            try:
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=BLAZOR_SSL_CERTIFICATE_VERIFICATION)) as client:
                    log(DEBUG, f"Destroying the session: {self.rs_session.s_id}...")
                    endpoint = f"{self.rs_endpoint_base}/sessions/session/{self.rs_session.s_id}?token={self.rs_session.s_api_token}"
                    async with client.delete(endpoint) as response:
                        response.raise_for_status()
                        msg = ContainerMessage("Session disconnected", False)

                    log(DEBUG, f"Session '{self.rs_session.s_id}' was deleted from the server.")
            except aiohttp.ClientError as e:
                log(ERROR, f"RemoteSession.disconnect(): Could not connect: {e}")
                msg = ContainerMessage(str(e), True)
            except Exception as e:
                log(ERROR, f"RemoteSession.disconnect(): Exception while disconnecting: {e}")
                msg = ContainerMessage(str(e), True)
            finally:
                self.rs_session = None
        else:
            msg = ContainerMessage("Session is already disconnected", False)
        return msg

    async def get_chat_lines(self, skillset_id=None) -> List[str]:
        if self.rs_session is None:
            raise RuntimeError("Session is not connected.")

        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=BLAZOR_SSL_CERTIFICATE_VERIFICATION)) as client:
                endpoint = f"{self.rs_endpoint_base}/sessions/session/{self.rs_session.s_id}/messages?token={self.rs_session.s_api_token}"
                async with client.get(endpoint) as response:
                    response.raise_for_status()
                    response_body = await response.text()
                    chat_lines = json.loads(response_body)
                    return chat_lines
        except aiohttp.ClientError as e:
            log(ERROR, f"RemoteSession.get_chat_lines(): Could not connect: {e}")
            return None
        except Exception as e:
            log(ERROR, f"RemoteSession.get_chat_lines(): Exception while getting chat lines: {e}")
            return None

    async def get_response(self,
                           timeout_sec: int = TIMEOUT_SEC,
                           retries: int = 5,
                           retry_delay_sec: int = 30
                          ) -> Any:
        """
        Waits until the session is ready, fetches the last chat line,
        retries up to `retries` times, and tries to JSON-decode it.
        Returns either a dict (if JSON) or the raw string.
        """
        if self.rs_session is None:
            raise RuntimeError("Session is not connected.")

        last_line = None
        for attempt in range(1, retries + 1):
            # check readiness
            status = await self.wait_until_ready(timeout_sec)
            if status.msg_is_error:
                log(ERROR,
                    f"RemoteSession.get_response(): wait_until_ready failed: {status.msg_message}")
                break

            # fetch chat
            chat_lines = await self.get_chat_lines() or []
            if chat_lines:
                last_line = chat_lines[-1].get("message")
            if last_line:
                break

            log(WARNING, f"RemoteSession.get_response(): No response (attempt {attempt}/{retries}),\nretrying in {retry_delay_sec}s…")
            await asyncio.sleep(retry_delay_sec)

        # nothing ever arrived?
        if not last_line:
            return None

        # try JSON
        result = last_line.strip()
        if (result.startswith("{") or result.startswith("[")):
            try:
                result = json.loads(result)
            except json.JSONDecodeError as je:
                log(WARNING, f"RemoteSession.get_response(): JSON parse failed: {je}")
                # fall through to return raw
        return result
        
    async def set_active_configuration(self, configuration_name) -> ContainerMessage:
        if self.rs_session is None:
            raise RuntimeError("Session is not connected.")

        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=BLAZOR_SSL_CERTIFICATE_VERIFICATION)) as client:
                endpoint = f"{self.rs_session.EndpointBase}/sessions/session/{self.rs_session.Id}/configuration/{configuration_name}?token={self.rs_session.ApiToken}"
                async with client.put(endpoint) as response:
                    response.raise_for_status()
                    msg = ContainerMessage("Configuration set successfully", False)
        except aiohttp.ClientError as e:
            log(ERROR, f"RemoteSession.set_active_configuration(): Could not connect: {e}")
            msg = ContainerMessage(str(e), True)
        except Exception as e:
            log(ERROR, f"RemoteSession.set_active_configuration(): Exception while setting configuration: {e}")
            msg = ContainerMessage(str(e), True)

        return msg

    async def get_active_configuration(self) -> str:
        if self.rs_session is None:
            raise RuntimeError("Session is not connected.")
        
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=BLAZOR_SSL_CERTIFICATE_VERIFICATION)) as client:
                endpoint = f"{self.rs_endpoint_base}/sessions/session/{self.rs_session.s_id}/configuration?token={self.rs_session.s_api_token}"
                async with client.get(endpoint) as response:
                    if response.status == 200:
                        data = await response.json()
                        active_configuration = data.get("activeConfiguration", None)
                        log(DEBUG, f"Active configuration: {active_configuration}")
                        return active_configuration
                    elif response.status == 400:
                        log(ERROR, "Bad Request: Token not provided.")
                    elif response.status == 404:
                        log(ERROR, "Session not found.")
                    elif response.status == 401:
                        log(ERROR, "Unauthorized: Invalid token.")
                    else:
                        log(ERROR, f"Error {response.status}: {await response.text()}")
                    return ''
        except aiohttp.ClientError as e:
            log(ERROR, f"RemoteSession.get_active_configuration(): Could not connect: {e}")
            return ''
        except Exception as e:
            log(ERROR, f"RemoteSession.get_active_configuration(): Exception while getting active configuration: {e}")
            return ''
            
    async def is_awaiting_input(self) -> ContainerMessage:
        return await self.wait_until_ready(0)
    
    async def wait_until_ready(self, timeout_sec:int=TIMEOUT_SEC) -> ContainerMessage:
        if self.rs_session is None:
            raise RuntimeError("Session is not connected.")

        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=BLAZOR_SSL_CERTIFICATE_VERIFICATION)) as client:
                endpoint = f"{self.rs_endpoint_base}/sessions/session/{self.rs_session.s_id}/awaitinginput?token={self.rs_session.s_api_token}&timeoutsec={timeout_sec}"
                async with client.get(endpoint) as response:
                    response.raise_for_status()
                    response_body = await response.text()
                    is_awaiting_input = json.loads(response_body)
                    return ContainerMessage(f"Awaiting input: {is_awaiting_input}", False)
        except Exception as e:
            log(ERROR, f"RemoteSession.wait_until_ready(): Exception while checking input status: {e}")
            return ContainerMessage(str(e), True)

    async def clear(self, timeout:int=TIMEOUT_SEC) -> None:
        try:
            log(DEBUG, f"Clearing the session: {self.rs_session.s_id}...")
            await self.wait_until_ready(timeout)
            await self.submit_prompt("/clear")
            await self.wait_until_ready(timeout)

            log(DEBUG, f"Session '{self.rs_session.s_id}' was cleared.")
        except Exception as e:
            log(ERROR, f"RemoteSession.reset(): Exception while resetting the session: {e}")
        finally:
            self.rs_session.s_plan = None
        return

    async def submit_message(self, prompt:str, role:str="user", json_output=None, structured_output=None, timeout_sec:int=TIMEOUT_SEC, recommended_plan:str=None, recommended_tools:List[str]=None) -> None:
        if self.rs_session is None:
            raise RuntimeError("Session is not connected.")
        
        try:
            await self.wait_until_ready(timeout_sec)
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=BLAZOR_SSL_CERTIFICATE_VERIFICATION)) as client:
                endpoint = f"{self.rs_endpoint_base}/sessions/session/{self.id}/prompt?token={self.api_token}"
                data = {
                    "role": role,
                    "prompt": prompt,
                    "json_output": json_output,
                    "structured_output": structured_output,
                    "recommended_plan": recommended_plan,
                    "recommended_tools": recommended_tools
                }

                async with client.put(endpoint, json=data) as response:
                    response.raise_for_status()  # Raise an exception for HTTP errors
                    response_body = await response.text()
                    if response_body is not None and len(response_body) > 0:
                        log(DEBUG, f"Response: {response_body}")

        except aiohttp.ClientError as e:
            log(ERROR, f"RemoteSession.submit_prompt(): Could not connect: {e}")
            
        except Exception as e:
            log(ERROR, f"RemoteSession.submit_prompt(): Exception while submitting the prompt: {e}")

    async def submit_prompt(self, prompt:str) -> None:
        return await self.submit_message(prompt=prompt, role="user")
    
    async def submit_attachment(self, attachment:str) -> None:
        prompt = f"""The following text is attached to the conversation, and must be used to answer the user's question:
```
{attachment}
```
"""        
        return await self.submit_message(prompt=prompt, role="system")
        
    async def ping(self) -> None:
        _ = await self.get_active_configuration()
        return

    def validate_token(self, token) -> bool:
        if self.api_token and token:
            is_valid = self.api_token == token
        else:
            is_valid = False
        return is_valid

#region unit test
UNIT_TEST_DESTROY = False
UNIT_TEST_CREATE = False
async def unit_test():
    endpoint = "http://127.0.0.1:5210/v1"
    rs = RemoteSession()
    msg = await rs.connect(endpoint_base=endpoint, session_id="test-s-1", token="")
    if msg is not None and not msg.msg_is_error:
        print(f"*** Connected to session: {msg.msg_message}")
        print(f"id=        " + rs.id)
        print(f"title=     " + rs.title)
        print(f"endpoint=  " + rs.rs_endpoint_base)
        print(f"userid=    " + rs.user_id)
        print(f"llm conf=  " + rs.active_llm_configuration_name)
        print(f"api tk=    " + rs.api_token)
        print(f"plan=      " +"See the plan.log file")
        log_plan(rs.plan)

        plan = await rs.get_plan()
        log_plan(plan)

        await rs.submit_prompt("What is the capital of France?")

        await rs.wait_until_ready(10)
        response = await rs.get_chat_lines()
        print(f"Chat lines: {response}")

        if UNIT_TEST_DESTROY:
            print(f"*** Destroying the session")
            await rs.destroy()
        else:
            print(f"*** Disconnecting from the session")
            rs.disconnect()
    elif UNIT_TEST_CREATE:
        print(f"*** Creating a new Session")
        msg = await rs.create(endpoint_base=endpoint, session_id="test-s-1", token="1234-XXXX-87654321")
        if msg is not None and not msg.msg_is_error:
            print(f"Connected to session: {msg.msg_message}")
            print(f"id=        " + rs.id)
            print(f"title=     " + rs.title)
            print(f"endpoint=  " + rs.endpoint_base)
            print(f"userid=    " + rs.user_id)
            print(f"llm conf=  " + rs.active_llm_configuration_name)
            print(f"api tk=    " + rs.api_token)
            # print(f"plan=      " + rs.plan)

            print(f"sleeping for 10 seconds...")
            sleep(10000)
            if UNIT_TEST_DESTROY:
                print(f"*** Destroying the session")
                await rs.destroy()
            else:
                print(f"*** Disconnecting from the session")
                rs.disconnect()
        else:
            print(f"*** Could not connect to the session: {msg.msg_message}")
    else:
        print(f"*** Could not connect to the session: {msg.msg_message}")

if __name__ == '__main__':
    import asyncio
    asyncio.run(unit_test())
#endregion
