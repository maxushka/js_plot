import asyncio
import websockets
import logging


class WebSocketServer(object):
  def __init__(self, host, port, parse_callback):
    self.clients = set()
    self.host = host
    self.port = port
    self.log = logging.getLogger("WebSocket")
    self.parse_callback = parse_callback

  async def create_connection(self):
    server = await websockets.serve(self.receive_handler, self.host, self.port)
    self.log.info(f"Running, host: {self.host}, port: {self.port}")
    await server.wait_closed()

  def register_new_client(self, wSocket):
    self.clients.add(wSocket)
    self.log.info(f'New client connected: {wSocket.remote_address}')

  def client_disconnect(self, wSocket):
    self.clients.remove(wSocket)
    self.log.info(f'Client {wSocket.remote_address} disconnect')

  async def receive_handler(self, wSocket, uri):
    self.register_new_client(wSocket)
    try:
      await self.parse_callback(wSocket, self.log)
    finally:
      self.client_disconnect(wSocket)

  async def send_msg(self, msg):
    try:
      if self.clients:
        await asyncio.wait([client.send(msg) for client in self.clients])
    except Exception as e:
      self.log.info(f'Exception: {e}')

  def check_connect(self, check_ip):
    try:
      if self.clients:
        for cl in self.clients:
          if cl.remote_address[0] == check_ip:
            return True
        return False
      else:
        return False
    except Exception as e:
      self.log.info(f'Exception check connect: {e}')


class WebSocketClient(object):
  def __init__(self, host, port, parse_callback):
    self.host = host
    self.port = port
    self.parse_callback = parse_callback
    self.log = logging.getLogger('WebSocketClient')
    self.__send_queue = asyncio.Queue()
    self.__status = 0

  async def __receive(self, wSocket):
    while True:
      try:
        await self.parse_callback(wSocket, self.log)
      except Exception as e:
        self.log.info(f'Exception while receiving a message: {e}')
        raise e

  async def __send(self, wSocket):
    try:
      while True:
        msg = await self.__send_queue.get()
        await wSocket.send(msg)
    except Exception as e:
      self.log.info(f'Exception while sending a message {e}')
      raise e

  async def create_connection(self):
    uri = f'ws://{self.host}:{self.port}'
    while True:
      try:
        async with websockets.connect(uri, ping_timeout=2) as ws:
          self.log.info(f'Connected, host: {self.host}, port:{self.port}')
          self.__status = 1
          while True:
            try:
              tasks = [asyncio.create_task(self.__receive(ws)), asyncio.create_task(self.__send(ws))]
              await asyncio.gather(*tasks)

            except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed):
              self.log.info('Loose connection')
              for task in tasks:
                task.cancel()
              try:
                pong = await ws.ping()
                await asyncio.wait_for(pong, timeout=self.ping_timeout)
                self.log.info('Ping OK, keeping connection alive...')
                continue
              except:
                self.log.info('Disconnected from server')
                self.__status = 0
                await asyncio.sleep(1)
                break
      except:
        self.__status = 0
        continue

  async def send_msg(self, msg):
    if self.__status == 1:
      await self.__send_queue.put(msg)

  def check_connect(self, check_ip):
    if self.__status == 1:
      return True
    else:
      return False
