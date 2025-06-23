Advanced Usage
=============

This section covers advanced topics and usage scenarios for PyQt Live Tuner.

Architecture Overview
-------------------

PyQt Live Tuner is designed with a modular architecture that consists of several key components:

.. code-block:: text

   +------------------------------------------+
   |             ApplicationBuilder           |
   |                                          |
   |  Creates and configures the application  |
   +------------------+---------------------+
                      |
                      | creates
                      v
   +------------------------------------------+
   |             MainApplication              |
   |                                          |
   |  Main window with menu and layout        |
   +------------------+---------------------+
                      |
           +----------+-----------+
           |                      |
           v                      v
   +---------------+    +------------------+
   | Parameters    |    | Configurations   |
   | Container     |    | Container        |
   |               |    |                  |
   | Scrollable    |    | Holds custom     |
   | area for      |    | widgets and      |
   | widgets       |    | displays         |
   +-----+---------+    +------------------+
         |
         | contains
         |
   +-----v----------+
   |                |
   | +-----------+  |
   | | Parameter |  |
   | | Widgets   |  |
   | +-----------+  |
   |                |
   | +-----------+  |
   | | Parameter |  |
   | | Groups    |  |
   | +-----------+  |
   |                |
   +----------------+

1. **ApplicationBuilder**: The main entry point for creating the application. It initializes the QApplication instance and configures the dark theme.

2. **MainApplication**: The main window that hosts the parameter widgets and configuration widgets. It provides menu options for loading and saving configurations and manages the layout.

3. **ParametersContainer**: A scrollable container that manages parameter widgets and groups. It handles adding widgets, retrieving values, and applying configuration data.

4. **ConfigurationsContainer**: A container for custom widgets like displays, plots, or other UI elements that aren't directly related to parameter tuning.

5. **Parameter Widgets**: Individual UI elements for different parameter types (float sliders, checkboxes, etc.).

6. **Parameter Groups**: Collections of related parameters that can be organized and manipulated together.

Class Hierarchy
^^^^^^^^^^^^^

**Parameter Widgets Hierarchy**:

.. code-block:: text

   ParameterWidget (Abstract Base)
   ├── FloatParameterWidget
   ├── BoolParameterWidget
   ├── DropdownParameterWidget
   ├── StringParameterWidget
   └── ActionParameterWidget

**Parameter Groups Hierarchy**:

.. code-block:: text

   ParameterGroupWidget (Base)
   ├── LinkedParameterGroup
   └── IndependentGroupWidget

Signal Flow
^^^^^^^^^^

The parameter change propagation follows this sequence:

1. User interacts with a parameter widget (e.g., moves a slider).
2. The widget emits a `valueChanged` signal with the parameter name and new value.
3. If the widget is part of a parameter group, the group also emits a `groupChanged` signal with the group name and all parameter values.
4. Any registered callbacks are triggered with the updated values.
5. Application logic processes these callbacks to implement the desired behavior.

Here's an example of this signal flow in action:

.. code-block:: python

   # Create a parameter widget
   slider = FloatParameterWidget("Opacity", {"min": 0, "max": 1, "step": 0.01})
   
   # Create a callback function
   def on_opacity_change(name, value):
       print(f"{name} changed to: {value}")
       # Update UI or application state
   
   # Register the callback
   slider.register_callback(on_opacity_change)
   
   # When the user moves the slider, on_opacity_change is automatically called

UI Layout
--------

As seen in the screenshot, the PyQt Live Tuner interface is organized into several sections:

1. **Menu Bar**: Contains File and other menus for configuration management.
2. **Configuration Area**: The top section displays custom widgets and information.
3. **Parameters Area**: The bottom section contains parameter widgets and groups.

Each parameter in the interface is displayed with:
- A label showing the parameter name
- The appropriate input widget (slider, checkbox, dropdown)
- For float parameters: a value display and reset button

Parameter groups are displayed as collapsible panels with a header showing the group name.

Extending the Library
-------------------

Custom Parameter Widgets
^^^^^^^^^^^^^^^^^^^^^^

You can create custom parameter widgets by subclassing the `ParameterWidget` base class. Your custom widget must implement:

1. `__init__(self, name, config)`: Initialize the widget with a name and configuration dictionary.
2. `set_value(self, value)`: Set the widget's value.
3. `get_value(self)`: Return the widget's current value.
4. `register_callback(self, callback)`: Register a function to be called when the value changes.

Here's a template for creating a custom parameter widget:

.. code-block:: python

   from PyQt5.QtCore import pyqtSignal
   from pyqt_live_tuner.parameter_widgets import ParameterWidget
   
   class MyCustomWidget(ParameterWidget):
       """Custom parameter widget documentation."""
       
       def __init__(self, name="Custom", config=None):
           super().__init__(name, config)
           config = config or {}
           
           # Initialize widget-specific attributes
           self.my_value = config.get("initial", 0)
           
           # Create and configure Qt widgets
           self.my_qt_widget = MyQtWidget()
           self.my_qt_widget.valueChanged.connect(self.on_widget_value_changed)
           
           # Add widgets to layout
           self.layout.addWidget(self.my_qt_widget)
       
       def on_widget_value_changed(self, value):
           """Handle changes from the underlying Qt widget."""
           self.my_value = value
           self.valueChanged.emit(self.name, value)
       
       def set_value(self, value):
           """Set the widget's value."""
           if value != self.my_value:
               self.my_value = value
               self.my_qt_widget.setValue(value)
       
       def get_value(self):
           """Get the widget's current value."""
           return self.my_value
       
       def register_callback(self, callback):
           """Register a callback function for value changes."""
           self.valueChanged.connect(callback)

Custom Parameter Groups
^^^^^^^^^^^^^^^^^^^^^

Similarly, you can create custom parameter groups by subclassing `ParameterGroupWidget`:

.. code-block:: python

   from pyqt_live_tuner.parameter_groups import ParameterGroupWidget
   
   class MyCustomGroup(ParameterGroupWidget):
       """Custom parameter group documentation."""
       
       def __init__(self, title, parent=None):
           super().__init__(title, parent)
           
           # Additional initialization code
           
       def custom_method(self):
           """Custom group functionality."""
           # Implement custom behavior

Advanced Styling
--------------

While PyQt Live Tuner uses QDarkTheme by default, you can customize the appearance:

1. **Using Custom QSS**:

   .. code-block:: python
   
      from PyQt5.QtCore import QFile, QTextStream
      
      app = ApplicationBuilder()
      style_file = QFile("path/to/stylesheet.qss")
      if style_file.open(QFile.ReadOnly | QFile.Text):
          stream = QTextStream(style_file)
          app._app.setStyleSheet(stream.readAll())
      app.run()

2. **Changing QDarkTheme Settings**:

   .. code-block:: python
   
      import qdarktheme
      
      # Before creating the ApplicationBuilder
      qdarktheme.setup_theme("light")  # or "dark", "auto"
      
      app = ApplicationBuilder()
      app.run()

3. **Custom Widget-Specific Styling**:

   .. code-block:: python
   
      float_widget = FloatParameterWidget("Styled Parameter")
      float_widget.setStyleSheet("QSlider { height: 20px; } QSlider::handle { background: red; }")

Performance Optimization
----------------------

For applications with many parameters or complex calculations, consider these optimization strategies:

1. **Batch Processing**: Group related parameters and process changes in batches.

   .. code-block:: python
   
      # Instead of processing individual parameters
      param1.register_callback(update_process)
      param2.register_callback(update_process)
      
      # Use a parameter group
      group = LinkedParameterGroup("Process Parameters")
      group.add_parameter(param1)
      group.add_parameter(param2)
      group.register_callback(update_process_batch)

2. **Throttling Updates**: For computationally expensive operations, throttle the update frequency.

   .. code-block:: python
   
      from PyQt5.QtCore import QTimer
      
      class ThrottledUpdater:
          def __init__(self, update_func, delay_ms=100):
              self.update_func = update_func
              self.delay = delay_ms
              self.timer = QTimer()
              self.timer.setSingleShot(True)
              self.timer.timeout.connect(self.do_update)
              self.pending_args = None
          
          def schedule_update(self, *args):
              self.pending_args = args
              if not self.timer.isActive():
                  self.timer.start(self.delay)
          
          def do_update(self):
              if self.pending_args is not None:
                  self.update_func(*self.pending_args)
                  self.pending_args = None
      
      # Usage
      updater = ThrottledUpdater(process_image)
      param.register_callback(lambda name, value: updater.schedule_update(value))

3. **Worker Threads**: For long-running operations, use worker threads to keep the UI responsive.

   .. code-block:: python
   
      from PyQt5.QtCore import QThread, pyqtSignal
      
      class Worker(QThread):
          result_ready = pyqtSignal(object)
          
          def __init__(self, func, *args, **kwargs):
              super().__init__()
              self.func = func
              self.args = args
              self.kwargs = kwargs
          
          def run(self):
              result = self.func(*self.args, **self.kwargs)
              self.result_ready.emit(result)
      
      # Usage
      def on_param_change(name, value):
          worker = Worker(process_data, value)
          worker.result_ready.connect(update_ui)
          worker.start()

Advanced Configuration Features
-----------------------------

1. **Dynamic Configuration Loading**:

   .. code-block:: python
   
      import json
      import os
   
      def load_config_for_scenario(scenario_name):
          file_path = f"configs/{scenario_name}.json"
          if os.path.exists(file_path):
              with open(file_path, "r") as f:
                  return json.load(f)
          return {}
   
      # Usage
      app = ApplicationBuilder()
      
      # Create parameter widgets with defaults
      params = create_default_parameters()
      for param in params:
          app.main_window.add_parameter(param)
      
      # Add a dropdown to select scenarios
      scenarios = ["daylight", "night", "rainy"]
      scenario_selector = DropdownParameterWidget("Scenario", {"options": scenarios})
      
      def on_scenario_change(name, value):
          config = load_config_for_scenario(value)
          app.main_window.parameters_container.set_values(config)
      
      scenario_selector.register_callback(on_scenario_change)
      app.main_window.add_parameter(scenario_selector)

2. **Auto-saving Configurations**:

   .. code-block:: python
   
      import json
      import time
      from PyQt5.QtCore import QTimer
   
      class AutoSaver:
          def __init__(self, container, save_path, interval_ms=5000):
              self.container = container
              self.save_path = save_path
              self.timer = QTimer()
              self.timer.timeout.connect(self.save)
              self.timer.start(interval_ms)
          
          def save(self):
              values = self.container.get_values()
              with open(self.save_path, "w") as f:
                  json.dump(values, f, indent=2)
   
      # Usage
      app = ApplicationBuilder()
      # Add parameters...
      
      # Setup auto-saver
      auto_saver = AutoSaver(
          app.main_window.parameters_container,
          f"autosave/config_{int(time.time())}.json"
      )

Integration with External Systems
-------------------------------

* :doc:`mqtt_integration`
* :doc:`rest_api_integration`
* :doc:`database_integration`
* :doc:`socket_communication`