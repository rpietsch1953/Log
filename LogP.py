#!/usr/bin/env python3
# vim: expandtab:ts=4:sw=4:noai
"""
    Set up a logging-environment for daemons or console-programs

Copyright (c) 2022 Ing. Rainer Pietsch <r.pietsch@pcs-at.com>

Detailed docs at <https://pcs-log.readthedocs.io/en/latest/index.html>

Source at <https://github.com/rpietsch1953/Log>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, version 3.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

Usage:
------

.. code-block:: python

    import logging
    from pcs_log.LogP import LogP


.. note::

    you have to import this both in all your modules you like to
    use this logging. But you only need to SetupLogging once.

"""



import contextlib
import copy
import logging
import logging.config
import multiprocessing
import pprint
import socket
import sys
import time
import traceback
import warnings
from ctypes import c_bool
from functools import partial
from typing import Union

import netifaces
import setproctitle


__updated__ = '137.221205144037'
Version = f"1.6.{__updated__}"


_KEEP = 'keep'
_KEEP_WARN = 'keep-warn'
_RAISE = 'raise'
_OVERWRITE_WARN = 'overwrite-warn'
_ERROR = logging.ERROR
_STATUS = logging.ERROR - 1
_WARNING = logging.WARNING
_MSG = logging.WARNING - 1
_INFO = logging.INFO
_DEBUG = logging.DEBUG
_TRACE = logging.DEBUG - 5

_Translation:dict = {}


class _LogP():

    def __init__(self):


        global _Translation
        self.__TimeOnSyslog = True
        self.__StdErrIsStdOut = False
        self._Translation = {}
        self._InitTranslation = {                        # pylint: disable=C0301
            'HostIsNoString':
                "{ClassName} host (type = {HostType}) is not a string - object",
            'HostIsNoValidIp':
                "{ClassName} host '{host}' is not an valid IP of this computer",
            'InvalidPortNumber':
                "{ClassName} port (={port}) must be between 1024 and 65535",
            'QueueIsInvalid':
                "{ClassName} queue (type={QueueType}) is not a multiprocessing.Queue - object",
            'LogDebugPortNoInt':
                "{ClassName} 'LogDebugPort' (= {LogDebugPort}) can't be converted to an integer",
            'LogProcInfoModLenNoInt':
                "{ClassName} 'LogProcInfoModLen' (= {LogProcInfoModLen}) can't be converted to an integer",
            'LogProcInfoModLenNeg':
                "{ClassName} 'LogProcInfoModLen' (= {LogProcInfoModLen}) can't be negative",
            'LogProcInfoFuncLenNoInt':
                "{ClassName} 'LogProcInfoFuncLen' (= {LogProcInfoFuncLen}) can't be converted to an integer",
            'LogProcInfoFuncLenNeg':
                "{ClassName} 'LogProcInfoFuncLen' (= {LogProcInfoFuncLen}) can't be negative",
            'LogMultiProcLenNoInt':
                "{ClassName} 'LogMultiProcLen' (= {LogMultiProcLen}) can't be converted to an integer",
            'LogMultiProcLenNeg':
                "{ClassName} 'LogMultiProcLen' (= {LogMultiProcLen}) can't be negative",
            'LogMultiThreadLenNoInt':
                "{ClassName} 'LogMultiThreadLen' (= {LogMultiThreadLen}) can't be converted to an integer",
            'LogMultiThreadLenNeg':
                "{ClassName} 'LogMultiThreadLen' (= {LogMultiThreadLen}) can't be negative",
            'LogDebugCacheSizeNoInt':
                "{ClassName} 'LogDebugCacheSize' (= {LogDebugCacheSize}) can't be converted to an integer",
            'LogDebugCacheSizeNeg':
                "{ClassName} 'LogDebugCacheSize' (= {LogDebugCacheSize}) can't be negative",
            'LogStackOnDebugNoStr':
                "{ClassName} 'LogStackOnDebug' (= {LogStackOnDebug}) is not a string",
            'LogLongLevelNoStr':
                "{ClassName} 'LogLongLevel' (= {LogLongLevel}) is not a string",
            'LogLevelTypeNoInt':
                "{ClassName} 'LogLevelType' (= {LogLevelType}) can't be converted to an integer",
        }
        self.__LogServer = self.__DummyPortLogServer()
        self.__LogLevel = 0
        self.__LogQueue: multiprocessing.Queue = multiprocessing.Queue()
        self._Translation = copy.deepcopy(self._InitTranslation)
        _Translation = self._Translation

    # Add the 3 additional log-level
        self._AddLoggingLevel('TRACE', _TRACE, 'trace')
        self._AddLoggingLevel('MSG', _MSG, 'msg')
        self._AddLoggingLevel('STATUS', _STATUS, 'status')

    def Stop(self):
        """Stop the Log-Server"""
        self.__LogServer.Stop()
        self.__LogServer.Join(2)
        self.__LogServer.Kill()

    def PollRestart(self) -> None:
        """Prüfe ob der Logserver neu gestartet werden muss"""
        self.__LogServer.PollRestart()

    def _PrintInitTranslation(self):
        print(pprint.pformat(self._InitTranslation, indent=4))

    def _PrintAktualTranslation(self):
        print(pprint.pformat(_Translation, indent=4))

    class __DummyPortLogServer():
        def __init__(self, *args, **kwargs):
            """The dummy-version of the 'PortLogServer'-class
            This class is used to return it to a user if no real Log-server is requested.
            So the programmer can call the functions without the need to question if
            a real server is running. All functions are No-Ops.
            """
            pass                        # pylint: disable=W0107

        def Run(self, *args, **kwargs) -> None:
            """Dummy"""
            pass                        # pylint: disable=W0107

        def Stop(self, *args, **kwargs) -> None:
            """Dummy"""
            pass                        # pylint: disable=W0107

        @property
        def RunFlag(self) -> bool:
            """Dummy"""
            return False

        @property
        def Name(self) -> str:
            """Dummy"""
            return ''

        @property
        def Port(self) -> int:
            """Dummy"""
            return 0

        @property
        def IsAlive(self) -> bool:
            """Dummy"""
            return False

        def PollRestart(self) -> None:
            """Dummy"""
            pass                        # pylint: disable=W0107

        def Kill(self) -> None:
            """Dummy"""
            pass                        # pylint: disable=W0107

        def Join(self, *args, **kwargs) -> None:
            """Dummy"""
            pass                        # pylint: disable=W0107

    class __PortLogServer():
        def __init__(self, *,          # pylint: disable=W0102
                     # only key-word arguments from here on
                     host: str = '127.0.0.1',
                     port: int = 0,
                     name: str = '',
                     queue: multiprocessing.Queue = None,
                     logsize: int = 0,
                     NewFormat: str = '',
                     translation: dict = {}) -> None:
            """Send the messages from the input-Queue to a tcp-client
            on the defined address and port.

            Args:
                port (int, optional): The port to use (1024 to 65535). Defaults to 0.
                name (str, optional): The process-name of this class. Defaults to ''.
                queue (multiprocessing.Queue, optional): The input queue. Defaults to None.
                logsize (int, optional): if >0 logsize messages are buffered and send to the client on connection. Defaults to 0.

            Raises:
                ValueError: if invalid arguments are given.
            """
            self._Translation: dict = translation
            self.__RunFlag = multiprocessing.Value(c_bool, True)
            self.__CanReload = True         # prevent restarting after Stop, Join or Kill

            self.__FormatStr = NewFormat.strip()
            self.__Formatter = None
            if self.__FormatStr != '':
                self.__Formatter = logging.Formatter(self.__FormatStr)
            ClassName = __class__.__name__
            self.__Name: str = name.strip()
            #
            # Logging cache
            #
            try:
                logsize = int(logsize)
                if logsize < 0:
                    logsize = 0
            except ValueError:
                logsize = 0
            self.__LogSize: int = logsize
            self.__LogCache: list = []

            #
            # Ip addr for server
            #
            if not isinstance(host, str):
                HostType = type(host)
                raise ValueError(self._Translation['HostIsNoString'].format(
                    **{'ClassName': ClassName, 'HostType': HostType}))
                # raise ValueError(f"{__class__.__name__} host (type={type(host)}) is not a string - object")
            if host.lower() == 'localhost':
                host = '127.0.0.1'
            if not host in self.__MyValidIps:
                raise ValueError(self._Translation['HostIsNoValidIp'].format(
                    **{'ClassName': ClassName, 'host': host}))
                # raise ValueError(f"{__class__.__name__} host '{host}' is not an valid IP of this computer")
            self.__Host = host
            #
            # the input queue
            #
            if queue is not None:
                if not isinstance(queue, multiprocessing.queues.Queue):
                    raise ValueError(self._Translation['HostIsNoValidIp'].format(
                        **{'ClassName': ClassName, 'QueueType': type(queue)}))
                    # raise ValueError(f"{__class__.__name__} queue (type={type(queue)}) is not a multiprocessing.Queue - object")
            self.__Queue = queue
            #
            # set the port
            #
            try:
                port = int(port)
            except ValueError:
                port = 0
            if port < 1024 or port > 65535:
                raise ValueError(self._Translation['InvalidPortNumber'].format(
                    **{'ClassName': ClassName, 'port': port}))
                # raise ValueError(f"{__class__.__name__} port must be between 1024 and 65535")
            self.__Port = port

            self.__Connections: dict = {}         # clear connection-dict
            # the reader process
            self.__ReaderProcess: Union[None, multiprocessing.Process] = None

        def Run(self, *,
                name: str = '',
                queue: multiprocessing.Queue = None) -> None:
            """Starts the reader-process

            Args:
                name (str, optional): Can overwrite the process-name of this instance. Defaults to ''.
                queue (multiprocessing.Queue, optional): can overwrite the input queue of this instance.
                            If not given the name from the creation is used Defaults to None.

            Raises:
                ValueError: if invalid arguments are given.
            """
            # global _Translation

            ClassName = __class__.__name__ + '.Run'
            if queue is not None:
                if not isinstance(queue, multiprocessing.queues.Queue):
                    raise ValueError(self._Translation['QueueIsInvalid'].format(
                        **{'ClassName': ClassName, 'QueueType': type(queue)}))
                    # raise ValueError(f"{__class__.__name__}.Run queue (type={type(queue)}) is not a multiprocessing.Queue - object")
                self.__Queue = queue
            if self.__Queue is None:
                raise ValueError(self._Translation['QueueIsInvalid'].format(
                    **{'ClassName': ClassName, 'QueueType': type(self.__Queue)}))
                # raise ValueError(f"{__class__.__name__} .Run queue (type={type(self.__Queue)}) is not a multiprocessing.Queue - object")
            name = name.strip()
            if name == '':
                name = 'PortLogServer'
            self.__Name = name
            self.__RunFlag = True
            self.__StartReader()

        def Stop(self) -> None:
            """Stop the port-log server
            """
            self.__RunFlag = False
            logging.log(_STATUS, "Stop Log-server")
            self.__Queue.put_nowait('DONE')
            self.__CanReload = False

        @property
        def RunFlag(self) -> bool:
            """Return True if the process is running
            """
            return self.__RunFlag

        @property
        def Name(self) -> str:
            """Return the process-name of this instance
            """
            return self.__Name

        @property
        def Port(self) -> int:
            """Return the port-number of this instance
            """
            return self.__Port

        @property
        def __MyValidIps(self) -> list:
            """Return a list of all valid IPs of this computer
            """
            Erg = []
            for interface in netifaces.interfaces():
                AddrDict = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in AddrDict:
                    for link in AddrDict[netifaces.AF_INET]:
                        Erg.append(link['addr'])
            if len(Erg) != 0:
                Erg.append('0.0.0.0')
            return Erg

        def __TermConnection(self, Client: str) -> None:
            """Terminate a connection
            """
            self.__Connections[Client].close()
            logging.log(_STATUS, f'Log-server disconnect client {Client}')
            self.__Connections[Client] = None

        def __CollectClients(self) -> None:
            """Clear dead connections from dict
            """
            KillConnection = []
            for Client, Connection in self.__Connections.items():
                if Connection is None:
                    KillConnection.append(Client)
            for Client in KillConnection:
                del self.__Connections[Client]

        # def __TermHandler(self, signum, frame):
        #     """The term-handler for this process
        #     """
        #     logging.warning(f'Log-server - Termination handler invoked with signal {signum}')
        #     # self.__RunFlag = False

        def __StartReader(self) -> None:
            """Start the reader-process
            """
            if self.__ReaderProcess is not None:
                if self.__ReaderProcess.is_alive():
                    return
                e = self.__ReaderProcess.exitcode
                del e

            self.__ReaderProcess = multiprocessing.Process(
                target=self.__ReaderProc, name=self.__Name)
            self.__ReaderProcess.daemon = True
            self.__RunFlag = True
            self.__ReaderProcess.start()  # Launch self.__ReaderProcess() as another proc
            logging.log(
                _STATUS, f"Start Log-server at {self.__Host}:{self.__Port}")
            return

        @property
        def IsAlive(self) -> bool:
            """Returnm True if the process is alive
            """
            Ret = False
            try:
                Ret = self.__ReaderProcess.is_alive()
            except Exception as exc:        # pylint: disable=W0703
                del exc
            return Ret

        def PollRestart(self) -> None:
            """Restart the process if it is not alive
            """
            if self.__CanReload:
                if not self.IsAlive:
                    self.Run()
            # pass

        def Kill(self) -> None:
            """Kill this process
            """
            self.__CanReload = False
            try:
                self.__ReaderProcess.kill()
            except:            # pylint: disable=W0702
                pass

        def Join(self, Timeout: float = None) -> None:
            """Join this process
            If the optional argument timeout is None (the default), the method blocks until
            the process whose join() method is called terminates. If timeout is a positive
            number, it blocks at most timeout seconds. Note that the method returns None
            if its process terminates or if the method times out.
            """
            self.__CanReload = False
            try:
                self.__ReaderProcess.join(Timeout)
            except:                 # pylint: disable=W0702
                pass

        def __ReaderProc(self) -> None:
            """Read from the queue; this spawns as a separate Process"""

            setproctitle.setproctitle(multiprocessing.current_process().name)
            logging.log(_STATUS, 'Log-server - Starting')
            # signal.signal(signal.SIGINT, self.__TermHandler)   # Setze Signalhandler
            # signal.signal(signal.SIGTERM, self.__TermHandler)
            server = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM | socket.SOCK_NONBLOCK)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            server.setblocking(False)
            IsOk = False
            for i in range(10):
                if not self.__RunFlag:
                    return 0
                try:
                    server.bind((self.__Host, self.__Port))
                    server.setblocking(False)
                    server.listen()
                    IsOk = True
                    break
                except:                 # pylint: disable=W0702
                    logging.warning('Log-server - Can not connect')
                    time.sleep(1)
            del i
            if not IsOk:
                self.__RunFlag = False
                return
            server.listen(5)

            while self.__RunFlag:
                try:
                    Connection, Address = server.accept()
                    Connection.setblocking(False)
                    ClientStr = f"{Address[0]}:{Address[1]}"
                    logging.log(
                        _STATUS, f'Log-server connection from {ClientStr}')
                    self.__Connections[ClientStr] = Connection
                    for l in self.__LogCache:
                        try:
                            Connection.sendall(l.encode('utf-8'))
                        except:             # pylint: disable=W0702
                            self.__TermConnection(Connection)
                except:                # pylint: disable=W0702
                    pass
                if not self.__RunFlag:
                    break
                for Client, Connection in self.__Connections.items():
                    if not self.__RunFlag:
                        break
                    if Connection is not None:
                        try:
                            message = None
                            message = Connection.recv(4096)  # .decode('utf-8')
                            if message[0] == 0xFF and message[1] == 0xF4:
                                self.__TermConnection(Client)
                                break
                            if len(message) != 0:
                                try:
                                    m = message.decode('utf-8').strip()
                                    if m == 'q' or m == 'Q':
                                        self.__TermConnection(Client)
                                        break
                                except:             # pylint: disable=W0702
                                    continue
                        except BlockingIOError:
                            continue
                        except Exception as exc:    # pylint: disable=W0703
                            logging.warning(f'Log-server exception - {exc}')
                self.__CollectClients()
                try:
                    Msg = self.__Queue.get(False, 1)
                    if isinstance(Msg, logging.LogRecord):
                        if self.__Formatter is not None:
                            Msg = self.__Formatter.format(Msg) + '\n'
                        else:
                            Msg = None
                    # print(type(Msg))
                except:                 # pylint: disable=W0702
                    Msg = None
                if Msg is not None:
                    if Msg == "DONE":
                        break
                    if self.__LogSize != 0:
                        self.__LogCache.append(Msg)
                        if len(self.__LogCache) > self.__LogSize:
                            self.__LogCache.pop(0)
                    for Client, Connection in self.__Connections.items():
                        if not self.__RunFlag:
                            break
                        try:
                            if Connection is not None:
                                Connection.sendall(Msg.encode('utf-8'))
                        except:                 # pylint: disable=W0702
                            self.__TermConnection(Client)
                    self.__CollectClients()

            for Client, Connection in self.__Connections.items():
                self.__TermConnection(Client)
            self.__CollectClients()
            server.close()
            self.__RunFlag = False
            logging.log(_STATUS, 'Log-server - Terminating')

    class __PortLogQueueHandler(logging.handlers.QueueHandler):
        """

        """

        def __init__(self, ProcClass, *args, **kwargs):
            """A queue-handler that allowes the automatic restart of the Log-server

            Args:
                ProcClass (PortLogServer): An instance of the listening PortLogServer.
                                            Needet to automatically restart if the
                                            server is terminated. All other parametrs
                                            look at the documentation of
                                            'logging.handlers.QueueHandler'
            """
            super().__init__(*args, **kwargs)
            self.__ProcClass = ProcClass

        def enqueue(self, record):
            """Overwritten enqueue function of the 'logging.handlers.QueueHandler' class.
            """
            try:
                self.__ProcClass.PollRestart()
            except:          # pylint: disable=W0702
                pass
            super().enqueue(record)

    class _MyFormater(logging.Formatter):
        def __init__(self, Format: str, DebugFormat: str, DebugLevel: int = -1):
            self.__DebugLevel = DebugLevel
            self.__PrivateFormatter = logging.Formatter(DebugFormat)
            super().__init__(Format)

        def format(self, record):
            if isinstance(self.__DebugLevel, (list, tuple)):
                if record.levelno in self.__DebugLevel:
                    result = self.__PrivateFormatter.format(record)
                else:
                    result = super().format(record)
            else:
                if record.levelno <= self.__DebugLevel or record.levelno == _ERROR:
                    result = self.__PrivateFormatter.format(record)
                else:
                    result = super().format(record)
            return result

    class _MyContextFilter(logging.Filter):
        def __init__(self, trim_amount: int = 5, below_level: int = -1, is_syslog: bool = False):
            """Class to prepaire the "stack"-variable within logrecord

            Args:
                trim_amount (int, optional): Maximum number of stack-lines to show. Defaults to 5.
                below_level (int, optional): Log-leven below or equal a stacktrace is shown. Defaults to -1 => disabled.
            """
            self.trim_amount = trim_amount
            self.below_level = below_level
            self.is_syslog = is_syslog
            super().__init__()

        def IsLast(self, s):
            """Prüfe ob das der letzte notwendigen Trace-Eintrag ist"""
            Such = '\n    root.log(level, msg, *args, **kwargs)\n'
            return Such in s

        def filter(self, record):
            if self.is_syslog:
                Delim = '\u21B2'
            else:
                Delim = '\n'
            if record.levelno <= self.below_level:
                wStack = traceback.format_stack()
                ResList = []
                for r in wStack:
                    s = str(r)
                    if self.IsLast(s):
                        break
                    ResList.append(s.replace('\n', Delim))

                record.stack = Delim + ''.join(ResList[0-self.trim_amount:])
            else:
                record.stack = ''
            return True

    def _AddLoggingLevel(self, level_name, level_num, method_name=None,
                         if_exists=_KEEP, *, exc_info=False, stack_info=False):
        """

        This Part was copied from: Joseph R. Fox-Rabinovitz

        Comprehensively add a new logging level to the :py:mod:`logging`
        module and the currently configured logging class.

        The `if_exists` parameter determines the behavior if the level
        name is already an attribute of the :py:mod:`logging` module or if
        the method name is already present, unless the attributes are
        configured to the exact values requested. Partial registration is
        considered a conflict. Even a complete registration will be
        overwritten if ``if_exists in (OVERWRITE, OVERWRITE_WARN)`` (without
        a warning of course).

        This function also accepts alternate default values for the keyword
        arguments ``exc_info`` and ``stack_info`` that are optional for
        every logging method. Setting alternate defaults allows levels for
        which exceptions or stacks are always logged.

        Parameters
        ----------
        level_name : str
            Becomes an attribute of the :py:mod:`logging` module with the
            value ``level_num``.
        level_num : int
            The numerical value of the new level.
        method_name : str
            The name of the convenience method for both :py:mod:`logging`
            itself and the class returned by
            :py:func:`logging.getLoggerClass` (usually just
            :py:class:`logging.Logger`). If ``method_name`` is not
            specified, ``level_name.lower()`` is used instead.
        if_exists : {_KEEP, _KEEP_WARN, OVERWRITE, OVERWRITE_WARN, RAISE}
            What to do if a level with `level_name` appears to already be
            registered in the :py:mod:`logging` module:

            :py:const:`_KEEP`
                Silently keep the old level as-is.
            :py:const:`_KEEP_WARN`
                Keep the old level around and issue a warning.
            :py:const:`OVERWRITE`
                Silently overwrite the old level.
            :py:const:`OVERWRITE_WARN`
                Overwrite the old level and issue a warning.
            :py:const:`RAISE`
                Raise an error.

            The default is :py:const:`_KEEP_WARN`.
        exc_info : bool
            Default value for the ``exc_info`` parameter of the new method.
        stack_info : bool
            Default value for the ``stack_info`` parameter of the new
            method.

        Examples
        --------
        >>> _AddLoggingLevel('TRACE', logging.DEBUG - 5)
        >>> logging.getLogger(__name__).setLevel("TRACE")
        >>> logging.getLogger(__name__).trace('that worked')
        >>> logging.trace('so did this')
        >>> logging.TRACE
        5

        >>> _AddLoggingLevel('XTRACE', 2, exc_info=True)
        >>> logging.getLogger(__name__).setLevel(logging.XTRACE)
        >>> try:
        >>>     1 / 0
        >>> except:
        >>>     # This line will log the exception
        >>>     logging.getLogger(__name__).xtrace('that failed')
        >>>     # This one will not
        >>>     logging.xtrace('so did this', exc_info=False)

        The ``TRACE`` level can be added using :py:func:`add_trace_level`.
        """
        # This method was inspired by the answers to Stack Overflow post
        # http://stackoverflow.com/q/2183233/2988730, especially
        # http://stackoverflow.com/a/13638084/2988730

        def for_logger_class(self, message, *args, **kwargs):
            if self.isEnabledFor(level_num):
                kwargs.setdefault('exc_info', exc_info)
                kwargs.setdefault('stack_info', stack_info)
                self._log(level_num, message, args, **kwargs)

        def for_logging_module(*args, **kwargs):
            kwargs.setdefault('exc_info', exc_info)
            kwargs.setdefault('stack_info', stack_info)
            logging.log(level_num, *args, **kwargs)

        if not method_name:
            method_name = level_name.lower()

        # The number of items required for a full registration is 4
        items_found = 0
        # Items that are found complete but are not expected values
        items_conflict = 0

        # Lock because logger class and level name are queried and set
        logging._acquireLock()          # pylint: disable=W0212
        try:
            registered_num = logging.getLevelName(level_name)
            logger_class = logging.getLoggerClass()

            if registered_num != 'Level ' + level_name:
                items_found += 1
                if registered_num != level_num:
                    if if_exists == _RAISE:
                        # Technically this is not an attribute issue, but for
                        # consistency
                        raise AttributeError(f"Level {level_name} already registered in logging module")
                    items_conflict += 1

            if hasattr(logging, level_name):
                items_found += 1
                if getattr(logging, level_name) != level_num:
                    if if_exists == _RAISE:
                        raise AttributeError(f"Level {level_name} already defined in logging module")
                    items_conflict += 1

            if hasattr(logging, method_name):
                items_found += 1
                logging_method = getattr(logging, method_name)
                if not callable(logging_method) or \
                        getattr(logging_method, '_original_name', None) != \
                        for_logging_module.__name__:
                    if if_exists == _RAISE:
                        raise AttributeError(f"Function {method_name} already defined in logging module")
                    items_conflict += 1

            if hasattr(logger_class, method_name):
                items_found += 1
                logger_method = getattr(logger_class, method_name)
                if not callable(logger_method) or \
                        getattr(logger_method, '_original_name', None) != \
                        for_logger_class.__name__:
                    if if_exists == _RAISE:
                        raise AttributeError(f"Method {method_name} already defined in logger class")
                    items_conflict += 1

            if items_found > 0:
                # items_found >= items_conflict always
                if (items_conflict or items_found < 4) and \
                        if_exists in (_KEEP_WARN, _OVERWRITE_WARN):
                    action = 'Keeping' if if_exists == _KEEP_WARN else 'Overwriting'
                    if items_conflict:
                        problem = 'has conflicting definition'
                        items = items_conflict
                    else:
                        problem = 'is partially configured'
                        items = items_found
                    warnings.warn(f"Logging level {level_name} {problem} already ({items}/4 items): {action}")

                if if_exists in (_KEEP, _KEEP_WARN):
                    return

            # Make sure the method names are set to sensible values, but
            # preserve the names of the old methods for future verification.
            for_logger_class._original_name = for_logger_class.__name__          # pylint: disable=W0212
            for_logger_class.__name__ = method_name
            for_logging_module._original_name = for_logging_module.__name__          # pylint: disable=W0212
            for_logging_module.__name__ = method_name

            # Actually add the new level
            logging.addLevelName(level_num, level_name)
            setattr(logging, level_name, level_num)
            setattr(logger_class, method_name, for_logger_class)
            setattr(logging, method_name, for_logging_module)
        finally:
            logging._releaseLock()          # pylint: disable=W0212

    def SetupLogging(self,
                     *,
                     AppName:str,
                     Verbose:int = 0,
                     NoDaemon:bool = True,
                     StdErr:bool = False,
                     StdErrIsStdOut:bool = False,
                     LogPath:str = '',
                     LogFileInterval:int = 60*60*24,
                     LogFileCount:int = 14,
                     Quiet:bool = False,
                     LogProcInfo:bool = False,
                     LogProcInfoModLen:int = 15,
                     LogProcInfoFuncLen:int = 15,
                     LogLevelType:int = 2,
                     LogMultiProc:bool = False,
                     LogMultiProcLen:int = 15,
                     LogMultiThread:bool = False,
                     LogMultiThreadLen:int = 15,
                     LogStackOnDebug:str = 'NONE',
                     LogLongLevel:str = 'DEBUG',
                     LogStackDepth:int = 5,
                     LogDebugIp:str = '127.0.0.1',
                     LogDebugPort:int = 0,
                     LogDebugCacheSize:int = 100,
                     NoReset:bool = False,
                     TimeOnSyslog:bool = True,
                     translation:dict = None,
                     **kwargs) -> None:
        """
        Creates a defined Log-setting with rich options.

        .. note::

            All arguments are named arguments - NO positional arguments!


        :param AppName: Name of application
        :type AppName: str
        :param Verbose: Detail of logging. Defaults to 0.
                        Possible values:

                        .. code-block:: text

                                0 = ERROR and STATUS
                                1 = MSG, WARNING, STATUS, ERROR
                                2 = INFO, MSG, WARNING, STATUS, ERROR
                                3 = DEBUG, INFO, MSG, WARNING, STATUS, ERROR
                                4 = TRACE, DEBUG, INFO, MSG, WARNING, STATUS, ERROR

        :type Verbose: int, optional
        :param NoDaemon: Is this an terminal-task. Defaults to True.
                                If this is False => I am a daemon.

                                On deamons output to StdErr do not make any sense, so this is ignored
                                and "syslog" or "logfile" is used.

        :type NoDaemon: bool, optional
        :param StdErr: Log to StdErr. Defaults to False.
                                If this is set the log goes to StdErr.
                                Ignored if we are a daemon.

        :type StdErr: bool, optional
        :param StdErrIsStdOut: Redirect StdErr-Logging to StdOut. Defaults to False.
        :type StdErrIsStdOut: bool, optional
        :param TimeOnSyslog: Show timestamp if logging to StdErr. Defaults to True.
        :type TimeOnSyslog: bool, optional
        :param LogPath: Log to a Log-file. Defaults to ''.

                                Log to the file which is given as the argument.
                                this file is rotated on a daily base and holded up to 14 files

        :type LogPath: str, optional
        :param LogFileInterval: Number of seconds a logfile lasts until it is rotated.
                                Defaults to 60*60*24 => one day.
        :type LogFileInterval: int, optional
        :param LogFileCount: Number of log-file kept. Defaults to 14.
        :type LogFileCount: int, optional
        :param Quiet: Output only errors. Defaults to False.
        :type Quiet: bool, optional
        :param LogProcInfo: Show process and thread. Defaults to False.
        :type LogProcInfo: bool, optional
        :param LogLevelType: Format of LevelInfo. Defaults to 2.

                            .. code-block:: text

                                0=None,
                                1=Number,
                                2=Name,
                                3=Both.

        :type LogLevelType: int, optional
        :param LogMultiProc: Show process-names. Defaults to False.
        :type LogMultiProc: bool, optional
        :param LogMultiThread: Show thread-names. Defaults to False.
        :type LogMultiThread: bool, optional
        :param LogProcInfoModLen: Length of the 'module' part of the log. Defaults to 15.

                                           Set to 0 for not alligning this part. Optimally this is
                                           the length of the longest modulename in your program.
                                           This is only used to allign the log-lines to make the
                                           rading easier. This names are NEVER truncated.

        :type LogProcInfoModLen: int, optional
        :param LogProcInfoFuncLen: Length of the 'function' part of the log. Defaults to 15.

                                            Set to 0 for not alligning this part. Optimally this is
                                            the length of the longest functionname in your program.
                                            This is only used to allign the log-lines to make the
                                            rading easier. This names are NEVER truncated.

        :type LogProcInfoFuncLen: int, optional
        :param LogMultiProcLen: Length of the 'procedure' part of the log. Defaults to 15.

                                         Set to 0 for not alligning this part. Optimally this is
                                         the length of the longest procedurename in your program.
                                         This is only used to allign the log-lines to make the
                                         rading easier. This names are NEVER truncated.

        :type LogMultiProcLen: int, optional
        :param LogMultiThreadLen: Length of the 'thread' part of the log. Defaults to 15.

                                           Set to 0 for not alligning this part. Optimally this is
                                           the length of the longest threadname in your program.
                                           This is only used to allign the log-lines to make the
                                           rading easier. This names are NEVER truncated.

        :type LogMultiThreadLen: int, optional
        :param LogStackOnDebug: Log-level below or equal a call-stack trace is included.

                                    Defaults to "NONE" => Disabled.
                                    The levels are:

                                    .. code-block:: text

                                        "ERROR"
                                        "STATUS"
                                        "WARNING"
                                        "MSG"
                                        "INFO"
                                        "DEBUG"
                                        "TRACE"
                                        "NONE"

                                    All other values are interpretet as "NONE".
                                    Value is not case-sensitive.

        :type LogStackOnDebug: str, optional
        :param LogLongLevel: Log-level below or equal a long info is included.

                                    Above this level except the ERROR-level the fields

                                    .. code-block:: text

                                        processname,
                                        threadname,
                                        module,
                                        line-no and
                                        levelinfo

                                    are not within the output.
                                    Alternative this can be a comma-separated list of levelnames
                                    in this case for this log-levels long infos are provided.
                                    Within this list "NONE" is ignored.
                                    Defaults to "DEBUG".

                                    The levels are:

                                    .. code-block:: text

                                        "ERROR"
                                        "STATUS"
                                        "WARNING"
                                        "MSG"
                                        "INFO"
                                        "DEBUG"
                                        "TRACE"
                                        "NONE"

                                    All other values are interpretet as "NONE".
                                    Value is not case-sensitive.

        :type LogLongLevel: str, optional
        :param LogStackDepth: Maximum number of call-stack entries to display. Defaults to 5.
        :type LogStackDepth: int, optional
        :param LogDebugPort: If 0 no debug-server is started. Else the value has to be
                                    between 1024 and 65535. A log-server is started on 'LogDebugIp'
                                    at port 'LogDebugPort'.

                                    It is possible to connect to this port (e.g with telnet) to
                                    receive ALL log-messages from this program. ALL means really
                                    all, no mather which loglevel is set. This output also
                                    includes all possible information about process, thread,
                                    module and function. The stacktrace ('LogStackOnDebug') is also
                                    honored. This output can be really heavy, but can help to debug
                                    already running programs without the need to restart with
                                    another loglevel.

                                    This server runs as a separated process and you have to
                                    terminate it by calling the :func:`Stop` function of the LogP-object,
                                    otherwise this process may block the termination of your
                                    program. This server will restart himselve if it is terminated
                                    by any means except you call the above mentioned functions.

                                    .. note::

                                        This port has to be free.

                                    Defaults to 0.

        :type LogDebugPort: int, optional
        :param LogDebugIp: The IP-address to bind to. This address must exist on the host
                                    this program is running. '0.0.0.0' for 'all IPs' is also
                                    valid. Only examined if 'LogDebugPort' > 0.
                                    Defaults to '127.0.0.1',
        :type LogDebugIp: str, optional
        :param LogDebugCacheSize: Only used if 'LogDebugPort' > 0. This is the number of
                                    log-messages cached for use at a new connection to the
                                    server. So if someone connects to the server he receives the
                                    last 'LogDebugCacheSize' log messages and after them all new
                                    messages.

                                    This is like a history. If set to 0 this function is disabled.
                                    Defaults to 100.

        :type LogDebugCacheSize: int, optional
        :param NoReset: Do not reset logger on init. Defaults to False.

                                .. note::

                                    Use with care. Could tend to mess up the logging.

        :type NoReset: bool, optional
        :param translation: If given the programmer can overwrite the error-messages used.
                                    There are 2 functions to help creating this dict:

                                        LogP._PrintInitTranslation()
                                        LogP._PrintActualTranslation()

                                    they do exactly what their name says: they print either the
                                    default value for the translationtable or the actual value after
                                    overwriting some or all values with this dict.
                                    default = {}
        :type translation: dict, optional

After calling this function the new logging is set up. Use the standard functions
    logger.error, logger.warning, etc and additional you can use logger.msg,
    logger.status and logger.trace.
The severity is in descending order:
  ERROR, STATUS, WARNING, MSG, INFO, DEBUG, TRACE


At the end of your program call:

    LogP.Stop()

this will stop the optional logger-process which send the output to a telnet-connection
if LogDebugPort is not 0.




Output format:

.. code-block:: text

    General overview:
        2022-06-22 07:37:42,494 Appname:MainProcess:MainThread LogP:main:461 - 40=   ERROR - Message
                                ^       ^           ^          ^               ^     ^       ^
                                |       |           |          |               |     |       |
        Name of application ----+       |           |          |               |     |       |
            only if not StdErr          |           |          |               |     |       |
        Name of process ----------------+           |          |               |     |       |
            if LogMultiProc = true                  |          |               |     |       |
        Name of thread if --------------------------+          |               |     |       |
            LogMultiThread = true                              |               |     |       |
        Module, function and linenumber -----------------------+               |     |       |
            only if LogProcInfo = true                                         |     |       |
        Level-number of message if LogLevelType = 1 or 3 ----------------------+     |       |
        Level-name of message if LogLevelType = 2 or 3 ------------------------------+       |
        The message given to the log-call ---------------------------------------------------+

        The minimal log entry for StdErr is:
            2022-06-22 07:37:42,494 Errormessage
        The maximal log entry is shown above.

    The output format to StdErr is like this:
        2022-06-22 07:37:42,494 MainProcess:MainThread LogP:main:461     - 40=   ERROR - Message
            No "Appname" because you know whitch program is running.
            The timestamp is only written if 'TimeOnSyslog' is True.
            REMEMBER: this is send to StdErr or to StdOut if 'StdErrIsStdOut' is True.

    The output format to sylog like this:
        Appname:MainProcess:MainThread LogP:main:461 - 40=   ERROR - Errormessage
            No timestamp because syslogg adds his own timestamp.

    The output format to a logfile is like this:
        2022-06-22 07:37:42,494 Appname:MainProcess:MainThread LogP:main:461 - 40=   ERROR - Message


    if a call-stack trace is requested lines like these are appended:
            File "./LogP.py", line 471, in <module>
            main()
            File "./LogP.py", line 448, in main
            abc()
            File "./LogP.py", line 411, in abc
            LogP.debug('Debug')


"""

        del kwargs
        self.Stop()
        self._Translation = copy.deepcopy(self._InitTranslation)
        _Translation = self._Translation
        self.__StdErrIsStdOut = StdErrIsStdOut
        self.__TimeOnSyslog = TimeOnSyslog

        ClassName = __name__ + '.SetupLogging'

        # Überschreibe die Übersetungen
        if translation is not None and isinstance(translation, dict):
            for k, InitItem in self._InitTranslation.items():
                try:
                    w = translation[k]
                    if not isinstance(w, str):
                        self._Translation[k] = InitItem
                    else:
                        self._Translation[k] = w
                except KeyError:
                    self._Translation[k] = InitItem


        if not NoReset:
            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)

    # Add the 3 additional log-level
        # self._AddLoggingLevel('TRACE', logging.DEBUG -5, 'trace')
        # self._AddLoggingLevel('MSG', logging.WARNING - 1, 'msg')
        # self._AddLoggingLevel('STATUS', logging.ERROR - 1, 'status')
    # Check Port option
        try:
            LogDebugPort = int(LogDebugPort)
        except:
            raise ValueError(self._Translation['LogDebugPortNoInt'].format(
                **{'ClassName': ClassName, 'LogDebugPort': LogDebugPort})) from None
        if LogDebugPort < 0:
            LogDebugPort = 0
    # Check Len options
        try:
            LogProcInfoModLen = int(LogProcInfoModLen)
        except:
            raise ValueError(self._Translation['LogProcInfoModLenNoInt'].format(
                **{'ClassName': ClassName, 'LogProcInfoModLen': LogProcInfoModLen})) from None
        if LogProcInfoModLen < 0:
            raise ValueError(self._Translation['LogProcInfoModLenNeg'].format(
                **{'ClassName': ClassName, 'LogProcInfoModLen': LogProcInfoModLen}))

        try:
            LogProcInfoFuncLen = int(LogProcInfoFuncLen)
        except:
            raise ValueError(self._Translation['LogProcInfoFuncLenNoInt'].format(
                **{'ClassName': ClassName, 'LogProcInfoFuncLen': LogProcInfoFuncLen})) from None
        if LogProcInfoFuncLen < 0:
            raise ValueError(self._Translation['LogProcInfoFuncLenNeg'].format(
                **{'ClassName': ClassName, 'LogProcInfoFuncLen': LogProcInfoFuncLen}))

        try:
            LogMultiProcLen = int(LogMultiProcLen)
        except:
            raise ValueError(self._Translation['LogMultiProcLenNoInt'].format(
                **{'ClassName': ClassName, 'LogMultiProcLen': LogMultiProcLen})) from None
        if LogMultiProcLen < 0:
            raise ValueError(self._Translation['LogMultiProcLenNeg'].format(
                **{'ClassName': ClassName, 'LogMultiProcLen': LogMultiProcLen}))

        try:
            LogMultiThreadLen = int(LogMultiThreadLen)
        except:
            raise ValueError(self._Translation['LogMultiThreadLenNoInt'].format(
                **{'ClassName': ClassName, 'LogMultiThreadLen': LogMultiThreadLen})) from None
        if LogMultiThreadLen < 0:
            raise ValueError(self._Translation['LogMultiThreadLenNeg'].format(
                **{'ClassName': ClassName, 'LogMultiThreadLen': LogMultiThreadLen}))

        try:
            LogDebugCacheSize = int(LogDebugCacheSize)
        except:
            raise ValueError(self._Translation['LogDebugCacheSizeNoInt'].format(
                **{'ClassName': ClassName, 'LogDebugCacheSize': LogDebugCacheSize})) from None
        if LogDebugCacheSize < 0:
            raise ValueError(self._Translation['LogDebugCacheSizeNeg'].format(
                **{'ClassName': ClassName, 'LogDebugCacheSize': LogDebugCacheSize}))

    # Add the Filter to implement stack-traces
        if not isinstance(LogStackOnDebug, str):
            raise ValueError(self._Translation['LogStackOnDebugNoStr'].format(
                **{'ClassName': ClassName, 'LogStackOnDebug': LogStackOnDebug}))
        wTxt = LogStackOnDebug.upper()
        if wTxt == 'ERROR':
            Sd = _ERROR
        elif wTxt == 'STATUS':
            Sd = _STATUS
        elif wTxt == 'WARNING':
            Sd = _WARNING
        elif wTxt == 'MSG':
            Sd = _MSG
        elif wTxt == 'INFO':
            Sd = _INFO
        elif wTxt == 'DEBUG':
            Sd = _DEBUG
        elif wTxt == 'TRACE':
            Sd = _TRACE
        else:
            Sd = -1

        if not isinstance(LogLongLevel, str):
            raise ValueError(self._Translation['LogLongLevelNoStr'].format(
                **{'ClassName': ClassName, 'LogLongLevel': LogLongLevel}))
        LongD: Union[int, list]
        wTxt = LogLongLevel.upper()
        if ',' in wTxt:
            LongLogLevelList = wTxt.split(',')
            LongD = []
            for Llv in LongLogLevelList:
                Llv = Llv.strip()
                if Llv == 'ERROR':
                    LongD.append(_ERROR)
                elif Llv == 'STATUS':
                    LongD.append(_STATUS)
                elif Llv == 'WARNING':
                    LongD.append(_WARNING)
                elif Llv == 'MSG':
                    LongD.append(_MSG)
                elif Llv == 'INFO':
                    LongD.append(_INFO)
                elif Llv == 'DEBUG':
                    LongD.append(_DEBUG)
                elif Llv == 'TRACE':
                    LongD.append(_TRACE)
        else:
            if wTxt == 'ERROR':
                LongD = _ERROR
            elif wTxt == 'STATUS':
                LongD = _STATUS
            elif wTxt == 'WARNING':
                LongD = _WARNING
            elif wTxt == 'MSG':
                LongD = _MSG
            elif wTxt == 'INFO':
                LongD = _INFO
            elif wTxt == 'DEBUG':
                LongD = _DEBUG
            elif wTxt == 'TRACE':
                LongD = _TRACE
            else:
                LongD = -1

        IsSyslog = False
        if LogPath == '' and not StdErr:
            IsSyslog = True
        logging.getLogger().addFilter(self._MyContextFilter(
            trim_amount=LogStackDepth, below_level=Sd, is_syslog=IsSyslog))

        if not NoDaemon:  # Ausgabe auf StdErr macht als Daemon keinen Sinn
            StdErr = False

        if Quiet:  # Wenn Quiet angegeben ist macht Verbose keinen Sinn
            Verbose = -1

        if Verbose == 0:  # Default
            LogLevel = _STATUS
        elif Verbose == 1:  # Mit Meldungen
            LogLevel = _MSG
        elif Verbose == 2:  # Mit Infos
            LogLevel = _INFO
        elif Verbose == 3:  # Mit debug infos
            LogLevel = _DEBUG
        elif Verbose >= 4:  # Mit itrace infos
            LogLevel = _TRACE
        else:  # Quiet
            LogLevel = _ERROR
        self.__LogLevel = LogLevel
        try:
            LogLevelType = int(LogLevelType)
        except:
            raise ValueError(self._Translation['LogLevelTypeNoInt'].format(
                **{'ClassName': ClassName, 'LogLevelType': LogLevelType})) from None
        if LogLevelType == 1:
            ShowLevel = '%(levelno)02d '
        elif LogLevelType == 2:
            ShowLevel = '%(levelname)7s '
        elif LogLevelType == 3:
            ShowLevel = '%(levelno)02d=%(levelname)7s '
        else:
            ShowLevel = ''

        if LogProcInfo:
            AddPar = ''
            if LogMultiProc:
                if LogMultiProcLen == 0:
                    AddPar += '%(processName)s'
                else:
                    AddPar += f"%(processName){LogMultiProcLen}s"
            if LogMultiThread:
                if AddPar != '':
                    AddPar += ':'
                if LogMultiThreadLen == 0:
                    AddPar += '%(threadName)s'
                else:
                    AddPar += f"%(threadName)-{LogMultiThreadLen}s"
            if LogProcInfoModLen == 0:
                AddPar += ' %(module)s'
            else:
                AddPar += f" %(module){LogProcInfoModLen}s"
            if LogProcInfoFuncLen == 0:
                AddPar += ':%(funcName)s:'
            else:
                AddPar += f":%(funcName)-{LogProcInfoFuncLen}s:"
            AddPar += '%(lineno)4d'
        else:
            AddPar = ''

        if LogPath != '':
            if LogStackOnDebug != 'NONE':
                Format = "%(asctime)s - %(message)s%(stack)s"
                DebugFormat = f"%(asctime)s - {AppName} {ShowLevel}{AddPar} - %(message)s%(stack)s"
            else:
                Format = "%(asctime)s - %(message)s"
                DebugFormat = f"%(asctime)s - {AppName} {ShowLevel}{AddPar} - %(message)s"

            FileLogHand = logging.handlers.TimedRotatingFileHandler(
                LogPath, when='S', interval=LogFileInterval, backupCount=LogFileCount)

            FileLogHand.setLevel(LogLevel)
            # Formatter = logging.Formatter(Format)
            # FileLogHand.setFormatter(Formatter)
            FileLogHand.setFormatter(
                self._MyFormater(Format, DebugFormat, LongD))
            logging.getLogger().addHandler(FileLogHand)

            # logging.basicConfig(handlers = [FileLogHand], level = LogLevel, format = Format)
            FileLogHand.doRollover()
        elif StdErr:
            if AddPar == '' and ShowLevel == '':
                if self.__TimeOnSyslog:
                    if LogStackOnDebug != 'NONE':
                        Format = "%(asctime)s %(message)s%(stack)s"
                        DebugFormat = "%(asctime)s %(message)s%(stack)s"
                    else:
                        Format = "%(asctime)s %(message)s"
                        DebugFormat = "%(asctime)s %(message)s"
                else:
                    if LogStackOnDebug != 'NONE':
                        Format = "%(message)s%(stack)s"
                        DebugFormat = "%(message)s%(stack)s"
                    else:
                        Format = "%(message)s"
                        DebugFormat = "%(message)s"

            else:
                if self.__TimeOnSyslog:
                    if LogStackOnDebug != 'NONE':
                        Format = "%(asctime)s %(message)s%(stack)s"
                        DebugFormat = f"%(asctime)s {ShowLevel}{AddPar} - %(message)s%(stack)s"
                    else:
                        Format = "%(asctime)s %(message)s"
                        DebugFormat = f"%(asctime)s {ShowLevel}{AddPar} - %(message)s"
                else:
                    if LogStackOnDebug != 'NONE':
                        Format = "%(message)s%(stack)s"
                        DebugFormat = f"{ShowLevel}{AddPar} - %(message)s%(stack)s"
                    else:
                        Format = "%(message)s"
                        DebugFormat = f"{ShowLevel}{AddPar} - %(message)s"
            if self.__StdErrIsStdOut:
                StdErrHandler = logging.StreamHandler(sys.stdout)
            else:
                StdErrHandler = logging.StreamHandler()
            StdErrHandler.setLevel(LogLevel)
            # Formatter = logging.Formatter(Format)
            # StdErrHandler.setFormatter(Formatter)
            StdErrHandler.setFormatter(
                self._MyFormater(Format, DebugFormat, LongD))
            logging.getLogger().addHandler(StdErrHandler)

    #        logging.basicConfig(stream = sys.stderr, level = LogLevel, format = Format)
        else:
            if LogStackOnDebug != 'NONE':
                Format = f"{AppName} - %(message)s%(stack)s"
                DebugFormat = f"{AppName} {ShowLevel}{AddPar} - %(message)s%(stack)s"
            else:
                Format = f"{AppName} - %(message)s"
                DebugFormat = f"{AppName} {ShowLevel}{AddPar} - %(message)s"
            SysLogHand = logging.handlers.SysLogHandler(address='/dev/log')

            SysLogHand.setLevel(LogLevel)
            # Formatter = logging.Formatter(Format)
            # SysLogHand.setFormatter(Formatter)
            SysLogHand.setFormatter(
                self._MyFormater(Format, DebugFormat, LongD))
            logging.getLogger().addHandler(SysLogHand)

    #        logging.basicConfig(handlers = [SysLogHand], level = LogLevel, format = Format)
        logging.getLogger().setLevel(1)

        self.__LogServer = self.__DummyPortLogServer()
        if LogDebugPort != 0:
            AddPar = ''
            if LogMultiProc:
                if LogMultiProcLen == 0:
                    AddPar += '%(processName)s'
                else:
                    AddPar += f"%(processName){LogMultiProcLen}s"
            if LogMultiThread:
                if AddPar != '':
                    AddPar += ':'
                if LogMultiThreadLen == 0:
                    AddPar += '%(threadName)s'
                else:
                    AddPar += f"%(threadName)-{LogMultiThreadLen}s"
            if LogProcInfoModLen == 0:
                AddPar += ' %(module)s'
            else:
                AddPar += f" %(module){LogProcInfoModLen}s"
            if LogProcInfoFuncLen == 0:
                AddPar += ':%(funcName)s:'
            else:
                AddPar += f":%(funcName)-{LogProcInfoFuncLen}s:"
            AddPar += '%(lineno)4d'
            ShowLevel = '%(levelname)7s '
            if LogStackOnDebug != 'NONE':
                Format = f"%(asctime)s {ShowLevel}{AddPar} - %(message)s%(stack)s"
            else:
                Format = f"%(asctime)s {ShowLevel}{AddPar} - %(message)s"
            self.__LogServer = self.__PortLogServer(
                host=LogDebugIp, port=LogDebugPort, queue=self.__LogQueue, logsize=LogDebugCacheSize, NewFormat=Format, translation=self._Translation)
            qh = self.__PortLogQueueHandler(self.__LogServer, self.__LogQueue)
            qh.setLevel(1)
            logging.getLogger().addHandler(qh)
            self.__LogServer.Run()

    @property
    def LogLevel(self) -> int:
        return self.__LogLevel

    @property
    def GetLogging(self) -> tuple:
        """
        Return logging functions

        :return: The logging functions in order
            logging.error,
            logging.status,
            logging.warning,
            logging.msg,
            logging.info,
            logging.debug,
            logging.trace

        :rtype: tuple
        """

        return (partial(logging.log,_ERROR),
                partial(logging.log,_STATUS),
                partial(logging.log,_WARNING),
                partial(logging.log,_MSG),
                partial(logging.log,_INFO),
                partial(logging.log,_DEBUG),
                partial(logging.log,_TRACE))


LogP = _LogP()
logging.status = partial(logging.log, _STATUS)
logging.msg = partial(logging.log, _MSG)
logging.trace = partial(logging.log, _TRACE)


class OtherLogLevel(object):
    def __init__(self,NewLevel:Union[int,str]):
        self.OldLogLevel = logging.getLogger().getEffectiveLevel()
        self.wDict = { 'ERROR': _ERROR,
                'STATUS': _STATUS,
                'WARNING': _WARNING,
                'MSG': _MSG,
                'INFO': _INFO,
                'DEBUG': _DEBUG,
                'TRACE': _TRACE}
        self.NewLevel = self.OldLogLevel
        if isinstance(NewLevel,str):
            NewLevel = NewLevel.upper()
            if NewLevel in wDict:
                self.NewLevel = wDict[NewLevel]
        elif isinstance(NewLevel,int):   
            self.NewLevel = NewLevel
        
    def __enter__(self) -> None:
        logging.getLogger().setLevel(self.NewLevel)

    def __exit__(self, type, value, traceback):
        logging.getLogger().setLevel(self.OldLogLevel)   


class NoLogging(object):
    """Set temporary loglevel to ERROR"""
    def __init__(self):
        self.OldLogLevel = logging.getLogger().getEffectiveLevel()

    def __enter__(self) -> None:
        logging.getLogger().setLevel(_ERROR)

    def __exit__(self, type, value, traceback):
        logging.getLogger().setLevel(self.OldLogLevel)   



###############################################################
# Test if __main__
###############################################################


# if __name__ == '__main__':

#     def abc():
#         """Na ja"""
#         logging.error('Error')
#         logging.status('Status')
#         logging.warning('Warning')
#         logging.msg('Msg')
#         logging.info('Info')
#         logging.debug('Debug')
#         # XXLogP.trace('Trace')

#     def main():
#         """Main"""
#         MyParam = {}
#         MyParam['Verbose'] = 4
#         MyParam['StdErr'] = True
#         MyParam['NoDaemon'] = True
#         MyParam['Quiet'] = False
#         MyParam['LogPath'] = ''
#         MyParam['LogProcInfo'] = True

#     #    MyParam['LogPath'] = './TheLog.log'
#         AppName = "LogP"
#         try:
#             LogP.SetupLogging(AppName=AppName,
#                               Verbose=MyParam['Verbose'],
#                               StdErr=MyParam['StdErr'],
#                               NoDaemon=MyParam['NoDaemon'],
#                               Quiet=MyParam['Quiet'],
#                               LogPath=MyParam['LogPath'],
#                               LogLevelType=3,
#                               LogProcInfo=True,
#                               LogMultiProc=True,
#                               LogMultiThread=True,
#                               LogProcInfoModLen=15,
#                               LogProcInfoFuncLen=15,
#                               LogMultiProcLen=13,
#                               LogMultiThreadLen=12,
#                               LogDebugCacheSize=11,
#                               LogDebugIp='127.0.0.1',
#                               LogDebugPort=65432
#                               )

#         except Exception as exc:                        # pylint: disable=W0703
#             print(exc)
#             sys.exit(1)

#         LogP.Stop()

#         LogP.SetupLogging(AppName=AppName,
#                           Verbose=MyParam['Verbose'],
#                           StdErr=MyParam['StdErr'],
#                           NoDaemon=MyParam['NoDaemon'],
#                           Quiet=MyParam['Quiet'],
#                           LogPath=MyParam['LogPath'],
#                           LogProcInfo=False,
#                           #                        LogStackOnDebug = "debug",
#                           #                        LogStackDepth=2,
#                           LogLevelType=0,
#                           LogMultiProc=False,
#                           LogMultiThread=False,
#                           LogProcInfoModLen=5,
#                           LogDebugPort=65432
#                           )

#         logging.error('Error')
#         logging.warning('Warning')
#         logging.info('Info')
#         logging.msg('Msg')
#         logging.status('Status')
#         logging.trace('Trace')
#         logging.debug('Debug')
#         abc()
#         LogP.Stop()

#         LogP.SetupLogging(AppName=AppName,
#                           Verbose=MyParam['Verbose'],
#                           StdErr=MyParam['StdErr'],
#                           NoDaemon=MyParam['NoDaemon'],
#                           Quiet=MyParam['Quiet'],
#                           LogPath=MyParam['LogPath'],
#                           LogLevelType=3,
#                           LogProcInfo=True,
#                           LogMultiProc=False,
#                           LogMultiThread=False,
#                           LogProcInfoModLen=15,
#                           LogProcInfoFuncLen=15,
#                           LogLongLevel='DEBUG, Status',
#                           LogDebugPort=65432
#                           )

#         logging.error('Error')
#         logging.warning('Warning')
#         logging.info('Info')
#         logging.msg('Msg')
#         logging.status('Status')
#         logging.trace('Trace')
#         logging.debug('Debug')
#         abc()
#         LogP.Stop()

#     main()
