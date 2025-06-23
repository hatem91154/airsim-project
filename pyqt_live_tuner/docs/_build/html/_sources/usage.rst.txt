Usage Guide
===========

This section provides detailed examples of how to use PyQt Live Tuner.

1. **Initialize the Application**:

   The `ApplicationBuilder` class is the entry point for creating and running the application. Here's how to initialize it:

   .. code-block:: python

      from pyqt_live_tuner import ApplicationBuilder

      app = ApplicationBuilder(title="My App")
      app.run()

2. **Add Parameter Widgets**:

   Parameter widgets allow you to create interactive UI elements for tuning parameters. For example, to add a dropdown widget:

   .. code-block:: python

      from pyqt_live_tuner.parameter_widgets import DropdownParameterWidget

      dropdown = DropdownParameterWidget("Options", {"options": ["Option 1", "Option 2", "Option 3"]})
      app.main_window.add_parameter(dropdown)

3. **Create Parameter Groups**:

   Parameter groups logically group related widgets. For example, to create a PID controller group:

   .. code-block:: python

      from pyqt_live_tuner.parameter_groups import LinkedParameterGroup
      from pyqt_live_tuner.parameter_widgets import FloatParameterWidget

      pid_group = LinkedParameterGroup("PID Controller")
      pid_group.add_parameter(FloatParameterWidget("Kp"))
      pid_group.add_parameter(FloatParameterWidget("Ki"))
      pid_group.add_parameter(FloatParameterWidget("Kd"))
      app.main_window.add_parameter_group(pid_group)

4. **Save and Load Configurations**:

   The application supports saving and loading parameter configurations as JSON files. Use the menu options in the application to save or load configurations.

5. **Advanced Usage**:

   - **Custom Themes**: You can customize the application's theme using the `qdarktheme` library.

     .. code-block:: python

        import qdarktheme
        qdarktheme.setup_theme("light")

   - **Dynamic Parameter Updates**: Update parameter values dynamically based on user input or external events.

     .. code-block:: python

        dropdown.set_value("Option 2")
        print(dropdown.get_value())