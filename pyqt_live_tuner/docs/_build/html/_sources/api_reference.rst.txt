API Reference
=============

This section provides a detailed reference of all modules, classes, and functions in the PyQt Live Tuner library.

Core Components
--------------

ApplicationBuilder
^^^^^^^^^^^^^^^^

.. py:class:: pyqt_live_tuner.ApplicationBuilder(title="My Application")

   A builder class that provides a clean interface for creating and running PyQt Live Tuner applications.
   
   :param str title: The title for the application window (default: "My Application")
   
   .. py:attribute:: main_window
      
      The main application window instance (:class:`pyqt_live_tuner.MainApplication`).
   
   .. py:method:: run()
      
      Build the main window and launch the application. This method blocks until the application is closed.
      
      :return: None

MainApplication
^^^^^^^^^^^^^

.. py:class:: pyqt_live_tuner.MainApplication(title="My Application")

   The main window class for PyQt Live Tuner applications. It manages parameter containers and
   provides menu options for saving and loading configurations.
   
   :param str title: The title for the window (default: "My Application")
   
   .. py:method:: set_parameters_container(container, name="Parameters")
      
      Sets the parameters container for the application.
      
      :param ParametersContainer container: The container to set
      :param str name: The label to display above the container
      :return: None
      
   .. py:method:: set_configurations_container(container, name="Configurations")
      
      Sets the configurations container for the application.
      
      :param ConfigurationsContainer container: The container to set
      :param str name: The label to display above the container
      :return: None
      
   .. py:method:: add_parameter(param)
      
      Adds a parameter widget to the parameters container, creating the container if it doesn't exist.
      
      :param ParameterWidget param: The parameter widget to add
      :return: None
      
   .. py:method:: add_parameter_group(group)
      
      Adds a parameter group to the parameters container, creating the container if it doesn't exist.
      
      :param ParameterGroupWidget group: The parameter group to add
      :return: None
      
   .. py:method:: add_configuration_widget(widget, label=None)
      
      Adds a widget to the configurations container, creating the container if it doesn't exist.
      
      :param QWidget widget: The widget to add
      :param str label: Optional label to display above the widget
      :return: None

Container Components
------------------

ParametersContainer
^^^^^^^^^^^^^^^^^

.. py:class:: pyqt_live_tuner.containers.ParametersContainer(parent=None)

   A scrollable container for organizing parameter widgets and groups.
   Supports reading and applying values from JSON.
   
   :param QWidget parent: The parent widget
   
   .. py:method:: add_param(widget)
      
      Adds a parameter widget to the container.
      
      :param ParameterWidget widget: The parameter widget to add
      :return: None
      
   .. py:method:: add_group(group)
      
      Adds a parameter group to the container.
      
      :param ParameterGroupWidget group: The parameter group to add
      :return: None
      
   .. py:method:: get_values()
      
      Returns the current values of all parameters and groups.
      
      :return: A dictionary of parameter values
      :rtype: dict
      
   .. py:method:: set_values(values)
      
      Sets the values of parameters and groups based on the provided dictionary.
      
      :param dict values: A dictionary of parameter values
      :return: None

ConfigurationsContainer
^^^^^^^^^^^^^^^^^^^^^

.. py:class:: pyqt_live_tuner.containers.ConfigurationsContainer(parent=None)

   A container for configuration widgets such as plots, image displays, or other custom widgets.
   
   :param QWidget parent: The parent widget

Parameter Widgets
---------------

ParameterWidget (Base Class)
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. py:class:: pyqt_live_tuner.parameter_widgets.ParameterWidget(name="Unnamed", config=None)

   The base class for all parameter widgets. Implements common functionality and defines
   the interface that all parameter widgets must follow.
   
   :param str name: The name of the parameter
   :param dict config: A configuration dictionary for the widget
   
   .. py:attribute:: valueChanged
      
      A PyQt signal that is emitted when the parameter value changes.
      
      Signal signature: ``valueChanged(name: str, value: Any)``
   
   .. py:method:: get_value()
      
      Returns the current value of the parameter. Must be implemented by subclasses.
      
      :return: The current parameter value
      :rtype: Any
      
   .. py:method:: set_value(value)
      
      Sets the value of the parameter. Must be implemented by subclasses.
      
      :param Any value: The new parameter value
      :return: None
      
   .. py:method:: register_callback(callback)
      
      Registers a function to be called when the parameter value changes.
      
      :param callable callback: A function that takes (name, value) arguments
      :return: None

FloatParameterWidget
^^^^^^^^^^^^^^^^^^

.. py:class:: pyqt_live_tuner.parameter_widgets.FloatParameterWidget(name="Unnamed", config=None)

   A parameter widget for adjusting floating-point values using a slider or spin box.
   
   :param str name: The name of the parameter
   :param dict config: Configuration dictionary with the following optional keys:
                      
                      - ``min`` (float): Minimum value (default: 0.0)
                      - ``max`` (float): Maximum value (default: 10.0)
                      - ``step`` (float): Step size (default: 0.1)
                      - ``initial`` (float): Initial value (default: min)
                      - ``precision`` (int): Decimal precision (default: 2)
   
   .. py:method:: set_value(value)
      
      Sets the current value of the parameter.
      
      :param float value: The new parameter value
      :return: None
      
   .. py:method:: get_value()
      
      Returns the current value of the parameter.
      
      :return: The current parameter value
      :rtype: float

BoolParameterWidget
^^^^^^^^^^^^^^^^^

.. py:class:: pyqt_live_tuner.parameter_widgets.BoolParameterWidget(name="Unnamed", config=None)

   A parameter widget for boolean values using a checkbox.
   
   :param str name: The name of the parameter
   :param dict config: Configuration dictionary with the following optional keys:
                      
                      - ``initial`` (bool): Initial state (default: False)
   
   .. py:method:: set_value(value)
      
      Sets the current state of the checkbox.
      
      :param bool value: The new parameter state
      :return: None
      
   .. py:method:: get_value()
      
      Returns the current state of the checkbox.
      
      :return: The current checkbox state
      :rtype: bool

DropdownParameterWidget
^^^^^^^^^^^^^^^^^^^^^

.. py:class:: pyqt_live_tuner.parameter_widgets.DropdownParameterWidget(name="Unnamed", config=None)

   A parameter widget for selecting from a list using a dropdown.
   
   :param str name: The name of the parameter
   :param dict config: Configuration dictionary with the following optional keys:
                      
                      - ``options`` (list): List of options (default: [])
                      - ``initial`` (str): Initial selection (default: first option)
                      - ``placeholder`` (str): Placeholder text (default: "Select an option")
   
   .. py:method:: set_value(value)
      
      Sets the current selection.
      
      :param str value: The new selection
      :return: None
      
   .. py:method:: get_value()
      
      Returns the current selection.
      
      :return: The current selection
      :rtype: str
      
   .. py:method:: update_options(options, initial=None)
      
      Updates the available options in the dropdown.
      
      :param list options: The new list of options
      :param str initial: The new initial selection (optional)
      :return: None

StringParameterWidget
^^^^^^^^^^^^^^^^^^^

.. py:class:: pyqt_live_tuner.parameter_widgets.StringParameterWidget(name="Unnamed", config=None)

   A parameter widget for entering text using a line edit.
   
   :param str name: The name of the parameter
   :param dict config: Configuration dictionary with the following optional keys:
                      
                      - ``initial`` (str): Initial text (default: "")
                      - ``placeholder`` (str): Placeholder text (default: "")
   
   .. py:method:: set_value(value)
      
      Sets the current text.
      
      :param str value: The new text
      :return: None
      
   .. py:method:: get_value()
      
      Returns the current text.
      
      :return: The current text
      :rtype: str

ActionParameterWidget
^^^^^^^^^^^^^^^^^^^

.. py:class:: pyqt_live_tuner.parameter_widgets.ActionParameterWidget(name="Unnamed", config=None)

   A parameter widget for triggering actions using a button.
   
   :param str name: The name of the parameter (button text)
   :param dict config: Configuration dictionary with the following optional keys:
                      
                      - ``callback`` (callable): Function to call when button is clicked
   
   .. py:method:: set_value(value)
      
      This method is a no-op for action widgets since they don't have a persistent value.
      
      :param Any value: Ignored
      :return: None
      
   .. py:method:: get_value()
      
      Returns None since action widgets don't have a persistent value.
      
      :return: None

Parameter Groups
--------------

ParameterGroupWidget (Base Class)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. py:class:: pyqt_live_tuner.parameter_groups.ParameterGroupWidget(title="Unnamed Group", parent=None)

   The base class for all parameter groups. Implements common functionality for organizing
   and managing related parameters.
   
   :param str title: The title of the group
   :param QWidget parent: The parent widget
   
   .. py:method:: title()
      
      Returns the title of the group.
      
      :return: The group title
      :rtype: str
      
   .. py:method:: add_parameter(widget)
      
      Adds a parameter widget to the group.
      
      :param ParameterWidget widget: The parameter widget to add
      :return: None
      
   .. py:method:: get_values()
      
      Returns the current values of all parameters in the group.
      
      :return: A dictionary of parameter values
      :rtype: dict
      
   .. py:method:: set_values(values)
      
      Sets the values of parameters in the group based on the provided dictionary.
      
      :param dict values: A dictionary of parameter values
      :return: None

LinkedParameterGroup
^^^^^^^^^^^^^^^^^^

.. py:class:: pyqt_live_tuner.parameter_groups.LinkedParameterGroup(title="Unnamed Group", parent=None)

   A group of related parameters that emits a signal with all parameter values when any parameter changes.
   
   :param str title: The title of the group
   :param QWidget parent: The parent widget
   
   .. py:attribute:: groupChanged
      
      A PyQt signal that is emitted when any parameter in the group changes.
      
      Signal signature: ``groupChanged(group_name: str, values: dict)``
   
   .. py:method:: add_parameter(widget)
      
      Adds a parameter widget to the group and connects its valueChanged signal.
      
      :param ParameterWidget widget: The parameter widget to add
      :return: None
      
   .. py:method:: register_callback(callback)
      
      Registers a function to be called when any parameter in the group changes.
      
      :param callable callback: A function that takes (group_name, values_dict) arguments
      :return: None

IndependentGroupWidget
^^^^^^^^^^^^^^^^^^^^

.. py:class:: pyqt_live_tuner.parameter_groups.IndependentGroupWidget(title="Unnamed Group", parent=None)

   A group of parameters that are visually grouped but don't emit a combined signal.
   Each parameter emits its own independent signals.
   
   :param str title: The title of the group
   :param QWidget parent: The parent widget
   
   .. py:method:: add_parameter(widget)
      
      Adds a parameter widget to the group without connecting signals.
      
      :param ParameterWidget widget: The parameter widget to add
      :return: None

Utility Classes
-------------

Logger
^^^^^

.. py:data:: pyqt_live_tuner.logger
   
   A logging utility for debugging and tracing. Uses Python's built-in logging module.