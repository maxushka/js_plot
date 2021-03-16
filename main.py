import aiohttp
import websockets
import json
import asyncio
import logging, logging.config
from aiohttp import web
from random import randint

from ws_worker import *


class Main(object):
  def __init__(self, config_file_name):
    logging.config.fileConfig('log_conf.conf')
    self.log = logging.getLogger("Main")
    self.log.info('=================== INIT MAIN ===================')
    config = json.loads(open(config_file_name, 'r').read())

    host = config['ws']['host']
    port = config['ws']['port']
    self.wsServer = WebSocketServer(host, port, self.ws_parse_callback)

    self.http_port = config['http']['port']

  async def ws_parse_callback(self, ws, log):
    async for message in ws:
      pass

  async def main_loop(self):
    while True:
      await asyncio.sleep(2)
      print('loop')
      arr = [randint(1, 100) for i in range(100)]
      await self.wsServer.send_msg(json.dumps({'arr':arr}))
      # await self.wsServer.send_msg([1,2,3,4,5,6])

  async def http_get_handler(self, request):
    raise web.HTTPFound(location='/index.html')
    return web.Response(text="Hello!")

  async def web_http_get_handler(self, request):
    # if '/scan_results_2g' in request.rel_url.path:
    #   return web.json_response(self.scan_results_2g)
    return web.Response(text='')


  def start(self):
    try:
      loop = asyncio.get_event_loop()
      # Websockets tasks
      loop.create_task(self.wsServer.create_connection())
      loop.create_task(self.main_loop())

      # http tasks
      app = web.Application()
      app.router.add_get('/', self.http_get_handler)
      app.router.add_get('/web/{url}', self.web_http_get_handler)
      app.add_routes([web.static('/', "./web", show_index=True, follow_symlinks=True)])
      loop.create_task(web.run_app(app, port=self.http_port, access_log=None))

      self.log.info('=================== START LOOP ==================')
      loop.run_forever()
    
    except (KeyboardInterrupt, SystemExit):
      loop.stop()
      loop.close()

if __name__ == '__main__':
  main = Main('config.json')
  main.start()
