from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory
import json
import beamline
from devices import ScannerConfig
from redis import ConnectionError


class PlateServerProtocol(WebSocketServerProtocol):
    abort_count = 0
    scan_templates = {'plate40':
                      {'columns': 8,
                       'rows': 5,
                       'x_spacing': 14,
                       'y_spacing': 14,
                       'hole_shape': 'square',
                       'hole_size': 5
                       }
                      }

    try:
        scanner = beamline.scan_saxs
    except ConnectionError:
        pass

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        print("Message Received")

        payload = json.loads(payload.decode('utf8'))

        if payload['action'] == 'abort':
            self.scanner.abort(polite=self.abort_count == 0)
            self.abort_count += 1

        if payload['action'] == 'initialise':
            self.initialiseScan(payload['scan_type'], payload['data'])

        if payload['action'] == 'scan':
            self.initialiseScan(payload['scan_type'], payload['data'])
            self.abort_count = 0
            self.scanner.start(level=2)

    def initialiseScan(self, scan_type, scan_data):

        if scan_type == 'plate40':
            template = self.scan_templates['plate40']

            yConfig = ScannerConfig()

            yConfig.number_points = template['rows']
            yConfig.positioners[0].readback = 'SMTEST:SMPL_TBL_Y_MTR.RBV'
            yConfig.positioners[0].write = 'SMTEST:SMPL_TBL_Y_MTR.VAL'
            yConfig.positioners[0].start = 0
            yConfig.positioners[0].end = (template['rows']-1)*template['y_spacing']
            yConfig.positioners[0].abs_rel = 'relative'

            yConfig.after_scan = "start pos"
            yConfig.triggers[0] = 'SMTEST:scan1.EXSC'

            self.scanner.set_config(level=2, config=yConfig)

            xConfig = ScannerConfig()

            xConfig.number_points = template['columns']
            xConfig.positioners[0].readback = 'SMTEST:SMPL_TBL_X_MTR.RBV'
            xConfig.positioners[0].write = 'SMTEST:SMPL_TBL_X_MTR.VAL'
            xConfig.positioners[0].start = 0
            xConfig.positioners[0].end = (template['columns']-1)*template['x_spacing']
            xConfig.positioners[0].abs_rel = 'relative'

            xConfig.after_scan = "start pos"
            xConfig.triggers[0] = 'SMTEST:cam1:Acquire'

            self.scanner.set_config(level=1, config=xConfig)

        if scan_type == 'protein':
            print scan_data

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


if __name__ == '__main__':

    try:
        import asyncio
    except ImportError:
        ## Trollius >= 0.3 was renamed
        import trollius as asyncio

    factory = WebSocketServerFactory("ws://localhost:9000", debug=False)
    factory.protocol = PlateServerProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, '127.0.0.1', 9000)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()