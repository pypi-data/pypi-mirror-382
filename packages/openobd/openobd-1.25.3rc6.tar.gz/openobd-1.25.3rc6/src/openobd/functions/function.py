import logging

from openobd_protocol.FunctionBroker.Messages.FunctionBroker_pb2 import FunctionRegistration, FunctionRegistrationState
from openobd_protocol.Function.Messages.Function_pb2 import FunctionDetails
from openobd_protocol.Messages.Empty_pb2 import EmptyMessage
from openobd_protocol.Session.Messages.ServiceResult_pb2 import ServiceResult, Result
from openobd.core.exceptions import OpenOBDException
from openobd.core.session_token_handler import SessionTokenHandler
from openobd.core.stream_handler import StreamHandler
from openobd.core.session import OpenOBDSession
from openobd.core.function_broker import OpenOBDFunctionBroker
from openobd.functions.function_context_handler import FunctionContextHandler

class OpenOBDFunction:
    id = ""
    version = "<undef>"
    name = ""
    description = ""
    signature = ""
    openobd_session = None

    '''
    Optionally you can pass a OpenOBDFunctionBroker (when non-standard configuration is needed)
    '''
    def __init__(self, openobd_session: OpenOBDSession, function_broker: OpenOBDFunctionBroker):
        try:
            self.openobd_session = openobd_session
            self.function_broker = function_broker
            self.result = ServiceResult(result=[Result.RESULT_SUCCESS])
            self._init_function_details()
            self._function_registration = FunctionRegistration(
                details=self._function_details,
                state=FunctionRegistrationState.FUNCTION_REGISTRATION_STATE_ONLINE,
                signature=self.signature)
            self._context_finished_ = False
        except OpenOBDException as e:
            logging.error(f"Failed to initialize openOBD function: {e}")
            self._function_registration = None
            self._context_finished_ = True

    def run(self):
        pass

    def get_function_registration(self):
        return self._function_registration

    def get_function_id(self):
        return self.id

    def _init_function_details(self, id=None, version=None, name=None, description=None, signature=None):
        self._function_details = None

        '''Check id presence, if not present we generate a fresh one'''
        if not id is None:
            self.id = id
        elif len(self.id) == 0:
            function = self.function_broker.generate_function_signature()
            self.id = function.id
            self.signature = function.signature

        '''Check signature presence'''
        if not signature is None:
            self.signature = signature
        elif len(self.signature) == 0:
            raise OpenOBDException("A function signature is required in order to serve a function on the network!")

        '''Initialize (version, name, description) correctly'''
        if not version is None:
            self.version = version

        '''Only overwrite name with class name when no custom name is provided'''
        if not name is None:
            self.name = name
        elif len(self.name) == 0:
            self.name = self.__class__.__name__

        if not description is None:
            self.description = description

        self._function_details = FunctionDetails(id=self.id,
                                                 version=self.version, name=self.name, description=self.description)

    def __enter__(self):
        if self._context_finished_:
            ''' We cannot continue when the constructor failed '''
            raise OpenOBDException("Failed to construct openOBD session")

        self._authenticate()
        return self

    # Authenticate against the openOBD session for this function
    def _authenticate(self):
        try:
            # Start the SessionTokenHandler to ensure the openOBD session remains authenticated
            SessionTokenHandler(self.openobd_session)
        except OpenOBDException as e:
            logging.error(f'Activating openOBD session failed: {e}')
            self._context_finished_ = True
            raise

    def __is_active__(self):
        return not self._context_finished_

    def __del__(self):
        self.__exit__(None, None, None)

    def interrupt(self):
        self.__exit__(OpenOBDException(f"Interrupt"), f"Function [{self.id}] has been interrupted!", None)

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.result = ServiceResult(result=[Result.RESULT_FAILURE])
            if isinstance(exc_type, OpenOBDException):
                logging.error(f'Request failed: {exc_value}')
            else:
                logging.error(f"Something unexpected occurred [{exc_value}]")
                # if traceback is not None:
                #     logging.warning(traceback.format_exc())

        # Make sure we finish the context once
        if not hasattr(self, '_context_finished_'):
            # Something wrong with initialization, also no cleanup possible
            return

        if self._context_finished_:
            return

        self._context_finished_ = True
        if self.openobd_session is not None:
            # Check if result is set
            if not hasattr(self, "result"):
                self.result = ServiceResult(result=[Result.RESULT_FAILURE])

            response = self.openobd_session.finish(self.result)
            self.openobd_session = None
            logging.info(response)

    def set_bus_configuration(self, bus_configs):
        # Open a configureBus stream, send the bus configurations, and close the stream
        bus_config_stream = StreamHandler(self.openobd_session.configure_bus)
        bus_config_stream.send_and_close(bus_configs)
        logging.info("Buses have been configured.")

    def run_function(self, function_class):
        '''Function id detection'''
        if issubclass(function_class, OpenOBDFunction):
            function_id = function_class.id
        else:
            raise OpenOBDException(f"Function not found: {function_class.name}")

        function_context = FunctionContextHandler(self.openobd_session)
        function_context.run_function(function_id, self.function_broker)
        return self.get_results()

    def set_result(self, key, value):
        self.openobd_session.set_function_result(key=key, value=value)

        # This is the wrong way?
        # self.openobd_session.function.setFunctionResult(Variable(type=ContextType.FUNCTION_CONTEXT, key=key, value=value))

    def set_variable(self, key, value):
        self.openobd_session.set_context_variable(key=key, value=value)

    '''Return the results as a dictionary'''
    def get_results(self) -> dict:
        function = self.openobd_session.function
        result_list = function.getFunctionResultList(request=EmptyMessage(),
                                                     metadata=self.openobd_session._metadata())  # type: VariableList
        variables = {}
        for var in result_list.variables:
            variables[var.key] = var.value
        return variables
