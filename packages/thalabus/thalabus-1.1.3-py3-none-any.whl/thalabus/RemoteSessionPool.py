import asyncio
from typing import List
from thalabus.RemoteSession import RemoteSession, ContainerMessage
from thalabus.Log import log, DEBUG, INFO, WARNING, ERROR, FATAL

class RemoteSessionPool:
    def __init__(self, session_count: int, endpoint: str, token: str, session_prefix: str, user_id: str):
        self.pool_session_count = session_count
        self.pool_endpoint = endpoint
        self.pool_token = token
        self.pool_session_prefix = session_prefix
        self.pool_user_id = user_id
        self.pool_remote_sessions = []
        self.pool_free_sessions = []
        self.pool_lock = asyncio.Lock()
        self.pool_condition = asyncio.Condition(self.pool_lock)
        self._shutdown = False

    async def _push_free_session(self, session: RemoteSession):
        async with self.pool_condition:
            self.pool_free_sessions.append(session)
            log(DEBUG, f"Session {session.id} added to free pool.")
            self.pool_condition.notify()

    async def _pull_free_session(self) -> RemoteSession:
        async with self.pool_condition:
            while not self.pool_free_sessions:
                log(DEBUG, "Waiting for a free session...")
                await self.pool_condition.wait()
            session = self.pool_free_sessions.pop(0)
            log(DEBUG, f"Session {session.id} pulled from free pool.")
            return session

    async def _create_session_async(self, session_id: str, endpoint: str, token: str, user_id: str) -> RemoteSession:
        remote_session = RemoteSession(session_id, user_id)
        msg: ContainerMessage = await remote_session.create(endpoint, session_id, token)
        if msg.msg_is_error:
            log(FATAL, f"Error: {msg.msg_message}")
            raise Exception(msg.msg_message)
        log(DEBUG, f"Connected to '{remote_session.id}'.")
        return remote_session

    async def _create_session_pool_async(self, session_count: int, endpoint: str, token: str, session_prefix: str, user_id: str):
        remote_sessions = []
        for idx in range(1, session_count + 1):
            session = await self._create_session_async(f"{session_prefix}{idx}", endpoint, token, user_id)
            remote_sessions.append(session)
            await self._push_free_session(session)

            if self._shutdown:
                break

        self.pool_remote_sessions = remote_sessions

    async def _close_session_async(self, session: RemoteSession):
        try:
            log(DEBUG, f"Closing session {session.id}...")
            await session.destroy()
        except Exception as e:
            log(WARNING, f"Exception: {e}")

    async def _close_session_pool_async(self):
        # first, allocate all free sessions so that they're not free any longer
        for idx in range(len(self.pool_remote_sessions)):
            session = await self._pull_free_session()

        # second, close all sessions
        tasks = [self._close_session_async(session) for session in self.pool_remote_sessions]
        await asyncio.gather(*tasks)
        self.pool_remote_sessions = None

    async def pool_execute(self, task: callable, task_args: list, keep_alive: bool = False) -> None:
        # start the session pool
        create_pool_task = asyncio.create_task(
            self._create_session_pool_async(self.pool_session_count, self.pool_endpoint, self.pool_token, self.pool_session_prefix, self.pool_user_id)
        )

        # execute tasks in parallel
        async def execute_task(task_arg):
            remote_session = await self._pull_free_session()
            if remote_session is None:
                log(ERROR, "No available session to execute the task.")
                return
            try:
                await remote_session.wait_until_ready()
                await remote_session.clear()

                await task(remote_session, task_arg)
            except Exception as e:
                log(ERROR, f"Exception: {e}")
            finally:
                await self._push_free_session(remote_session)

        tasks = [execute_task(task_arg) for task_arg in task_args]
        await asyncio.gather(*tasks)

        # wait for the session pool to complete
        self._shutdown = True
        await create_pool_task

        if not keep_alive:
            # close the session pool
            await self._close_session_pool_async()
            self.pool_remote_sessions = []
