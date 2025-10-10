import os
import platform
from kabaret import flow


class EditMultiOSValue(flow.Action):

    environ_var_name = flow.Param()
    value_windows    = flow.SessionParam().ui(editor='path')
    value_linux      = flow.SessionParam().ui(editor='path')
    value_darwin     = flow.SessionParam().ui(editor='path')

    _value = flow.Parent()

    def get_buttons(self):
        self._update_values()
        return ['Save', 'Cancel']
    
    def _update_values(self):
        self.environ_var_name.set(self._value.environ_var_name.get())
        self.value_windows.set(self._value.value_windows.get())
        self.value_linux.set(self._value.value_linux.get())
        self.value_darwin.set(self._value.value_darwin.get())
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        self._value.environ_var_name.set(self.environ_var_name.get())
        self._value.value_windows.set(self.value_windows.get())
        self._value.value_linux.set(self.value_linux.get())
        self._value.value_darwin.set(self.value_darwin.get())
        self._value.touch()


class MultiOSValue(flow.values.ComputedValue):
    '''
    Defines a value which computes itself according to the
    value of the environment variable `environ_var_name`, if
    defined, or the values specified in the three following
    parameters depending on the OS currently running.
    '''

    environ_var_name = flow.Param()
    value_windows    = flow.Param().ui(editor='path')
    value_linux      = flow.Param().ui(editor='path')
    value_darwin     = flow.Param().ui(editor='path')

    edit = flow.Child(EditMultiOSValue)

    def compute(self):
        # Use value to store environment variable name
        env_var = self.environ_var_name.get()
        value = None

        if env_var is not None and env_var in os.environ:
            value = os.environ[env_var]
        else:
            # Get the operative system
            _os = platform.system()
            if _os == 'Windows':
                value = self.value_windows.get()
            elif _os == 'Linux':
                value = self.value_linux.get()
            elif _os == 'Darwin':
                value = self.value_darwin.get()
            else:
                raise Exception(
                    f'ERROR: Unrecognised OS to get {self.oid()} value'
                )
        
        self.set(value)


class MultiOSParam(flow.Computed):

    _DEFAULT_VALUE_TYPE = MultiOSValue
