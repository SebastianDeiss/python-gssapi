import base64
import sys

import six
if six.PY3:
    import socketserver
else:
    import SocketServer as socketserver

from gssapi import AcceptContext


class GSSAPIHandler(socketserver.BaseRequestHandler):

    def _writeline(self, line):
        self.request.sendall(line)
        self.request.sendall(b'\n')

    def handle(self):
        global server
        print("{0} connected".format(self.client_address[0]))
        ctx = AcceptContext()
        self.sockfile = self.request.makefile('rwb')
        while not ctx.established:
            print("{0} handshaking...".format(self.client_address[0]))
            in_b64 = self.sockfile.readline()
            in_token = base64.b64decode(in_b64)
            print("{0} sent {1} bytes.".format(self.client_address[0], len(in_token)))
            if len(in_token) < 1:
                return
            out_token = ctx.step(in_token)
            if out_token:
                print("Sending back {0} bytes".format(len(out_token)))
                self._writeline(base64.b64encode(out_token))
        print("{0} handshake complete.".format(self.client_address[0]))
        self._writeline(b'!OK')
        client_command = self.sockfile.readline().strip()
        print("{0} command: {1}".format(self.client_address[0], client_command))

        if client_command[0] != b'!'[0]:
            self._writeline(b'!ERROR')
            print("That wasn't a command, closing connection")
            return

        if client_command == b'!SHUTDOWN':
            server.shutdown()
        elif client_command == b'!MYNAME':
            self._writeline(six.text_type(ctx.peer_name).encode('utf-8'))
        elif client_command == b'!LIFETIME':
            self._writeline(six.text_type(ctx.lifetime).encode('utf-8'))
        elif client_command == b'!WRAPTEST':
            self._wrap_test(ctx)
        elif client_command == b'!MICTEST':
            self._mic_test(ctx)
        elif client_command == b'!DELEGTEST':
            self._delegated_cred_test(ctx)
        elif client_command == b'!MECHTYPE':
            self._writeline(six.text_type(ctx.mech_type).encode('utf-8'))

    def _wrap_test(self, ctx):
        if not ctx.confidentiality_negotiated:
            print("WRAPTEST: no confidentiality_negotiated")
            self._writeline(b'!ERROR')
            return
        try:
            unwrapped = ctx.unwrap(base64.b64decode(self.sockfile.readline()))
        except:
            self._writeline(b'!ERROR')
            raise
        if unwrapped != b'msg_from_client':
            print("WRAPTEST: no msg_from_client")
            self._writeline(b'!ERROR')
            return
        self._writeline(b'!OK')
        self._writeline(base64.b64encode(ctx.wrap(b'msg_from_server')))

    def _mic_test(self, ctx):
        if not ctx.integrity_negotiated:
            print("MICTEST: no integrity_negotiated")
            self._writeline(b'!ERROR')
            return
        msg = self.sockfile.readline().strip()
        mic = base64.b64decode(self.sockfile.readline())
        try:
            ctx.verify_mic(msg, mic)
        except:
            self._writeline(b'!ERROR')
            raise
        if msg != b'msg_from_client':
            print("MICTEST: no msg_from_client")
            self._writeline(b'!ERROR')
            return
        self._writeline(b'!OK')
        self._writeline(b'msg_from_server')
        self._writeline(base64.b64encode(ctx.get_mic(b'msg_from_server')))

    def _delegated_cred_test(self, ctx):
        if ctx.delegated_cred:
            self._writeline(b'!OK')
            self._writeline(six.text_type(ctx.delegated_cred.name).encode('utf-8'))
            self._writeline(six.text_type(ctx.delegated_cred.lifetime).encode('utf-8'))
        else:
            self._writeline(b'!NOCRED')


if __name__ == '__main__':
    server = socketserver.ThreadingTCPServer(('', 10100 + sys.version_info[0]), GSSAPIHandler)
    print("Starting test server...")
    server.serve_forever()
    print("Test server shutdown.")
