Testing Guide
=============

This section provides detailed instructions for testing PyQt Live Tuner. It covers unit testing, integration testing, and test-driven development practices.

Setting Up the Testing Environment
--------------------------------

1. **Install Testing Dependencies**

   First, ensure you have all the required dependencies for testing:

   .. code-block:: bash

      pip install pytest pytest-cov pytest-qt pytest-mock pytest-xvfb

   These packages provide:

   * ``pytest``: The core testing framework
   * ``pytest-cov``: Test coverage reporting
   * ``pytest-qt``: Qt-specific testing utilities for PyQt
   * ``pytest-mock``: Utilities for mocking and patching
   * ``pytest-xvfb``: Virtual X server for headless UI testing

2. **Project Testing Structure**

   The PyQt Live Tuner project organizes tests in a hierarchical structure that mirrors the main package layout:

   .. code-block:: text

      tests/
      ├── __init__.py
      ├── test_main_application.py
      ├── containers/
      │   ├── __init__.py
      │   ├── test_configurations_container.py
      │   └── test_parameters_container.py
      ├── parameter_groups/
      │   ├── __init__.py
      │   ├── test_all_group_widgets.py
      │   ├── test_independent_group_widget.py
      │   └── test_linked_group_widget.py
      └── parameters/
          ├── __init__.py
          ├── test_action_widget.py
          ├── test_all_parameter_widgets.py
          ├── test_bool_widget.py
          ├── test_dropdown_widget.py
          ├── test_float_widget.py
          └── test_string_widget.py

Running Tests
-----------

1. **Running All Tests**

   Run all tests using the following command from the project root directory:

   .. code-block:: bash

      pytest tests

2. **Running Specific Test Files or Directories**

   To run tests from a specific file or directory:

   .. code-block:: bash

      pytest tests/parameters/test_float_widget.py
      pytest tests/parameter_groups/

3. **Selecting Tests by Name Pattern**

   Run tests whose names match a specific pattern:

   .. code-block:: bash

      pytest -k "test_get_value or test_set_value"

4. **Verbose Output**

   For more detailed output, use the verbose flag:

   .. code-block:: bash

      pytest -v tests

5. **Showing Print Output**

   To see print statements during test execution:

   .. code-block:: bash

      pytest -s tests

Test Coverage
-----------

1. **Generating Coverage Reports**

   To generate a test coverage report:

   .. code-block:: bash

      pytest --cov=pyqt_live_tuner tests

2. **Detailed HTML Coverage Report**

   For a detailed HTML coverage report:

   .. code-block:: bash

      pytest --cov=pyqt_live_tuner --cov-report=html tests

   This will generate an HTML report in the `htmlcov/` directory, which you can view in your browser.

3. **Coverage Thresholds**

   It's recommended to maintain high test coverage. PyQt Live Tuner aims for:

   * Overall coverage: >90%
   * Core functionality coverage: >95%
   * UI element coverage: >85%

Writing Tests
-----------

1. **Basic Test Structure**

   Tests in PyQt Live Tuner follow a standard pytest structure:

   .. code-block:: python

      import pytest
      from pyqt_live_tuner.parameter_widgets import FloatParameterWidget

      def test_float_widget_initialization():
          """Test that a FloatParameterWidget initializes correctly."""
          widget = FloatParameterWidget("Test", {"min": 0, "max": 10, "initial": 5})
          assert widget.name == "Test"
          assert widget.get_value() == 5

      def test_float_widget_set_value():
          """Test setting a value on a FloatParameterWidget."""
          widget = FloatParameterWidget("Test", {"min": 0, "max": 10})
          widget.set_value(7.5)
          assert widget.get_value() == 7.5

2. **Testing Qt Widgets with pytest-qt**

   Use QtBot for simulating user interactions:

   .. code-block:: python

      def test_slider_interaction(qtbot):
          """Test that slider interaction updates the value."""
          widget = FloatParameterWidget("Test", {"min": 0, "max": 10})
          qtbot.addWidget(widget)
          
          # Track signal emissions
          signals_caught = []
          widget.valueChanged.connect(lambda name, value: signals_caught.append((name, value)))
          
          # Simulate user moving the slider
          qtbot.mouseClick(widget.slider, Qt.LeftButton)
          qtbot.keyClick(widget.slider, Qt.Key_Right)  # Move right
          
          # Assert signal was emitted with correct values
          assert len(signals_caught) > 0
          assert signals_caught[-1][0] == "Test"  # Name
          assert signals_caught[-1][1] > 0  # Value increased

3. **Testing Callbacks and Signals**

   Test that callbacks are properly registered and triggered:

   .. code-block:: python

      def test_callback_registration():
          """Test that callbacks are properly registered and triggered."""
          widget = FloatParameterWidget("Test")
          
          # Create a mock callback function
          mock_callback = Mock()
          widget.register_callback(mock_callback)
          
          # Trigger a value change
          widget.set_value(7.5)
          
          # Assert callback was called with correct parameters
          mock_callback.assert_called_once_with("Test", 7.5)

4. **Testing Configuration Loading**

   Test loading and applying configurations:

   .. code-block:: python

      def test_config_loading():
          """Test loading widget values from a configuration."""
          container = ParametersContainer()
          
          # Add some widgets
          float_widget = FloatParameterWidget("Float")
          bool_widget = BoolParameterWidget("Bool")
          container.add_param(float_widget)
          container.add_param(bool_widget)
          
          # Create a configuration
          config = {
              "Float": 7.5,
              "Bool": True
          }
          
          # Apply the configuration
          container.set_values(config)
          
          # Assert values were applied
          assert float_widget.get_value() == 7.5
          assert bool_widget.get_value() is True

5. **Using Fixtures**

   PyQt Live Tuner tests use fixtures for common setup:

   .. code-block:: python

      @pytest.fixture
      def parameter_container():
          """Fixture providing a ParametersContainer with standard widgets."""
          container = ParametersContainer()
          container.add_param(FloatParameterWidget("Float"))
          container.add_param(BoolParameterWidget("Bool"))
          container.add_param(StringParameterWidget("String"))
          return container
      
      def test_with_fixture(parameter_container):
          """Test using the parameter_container fixture."""
          # Container already has widgets
          values = parameter_container.get_values()
          assert "Float" in values
          assert "Bool" in values
          assert "String" in values

Test-Driven Development
---------------------

PyQt Live Tuner encourages test-driven development (TDD), following these steps:

1. **Write a failing test** that defines the desired behavior.
2. **Run the test to confirm it fails** as expected.
3. **Write just enough code to make the test pass**.
4. **Refactor the code** while ensuring all tests continue to pass.
5. **Repeat** for the next feature or enhancement.

Examples of TDD for PyQt Live Tuner:

1. **Adding a New Parameter Widget**

   First, write the test:

   .. code-block:: python

      # tests/parameters/test_color_widget.py
      import pytest
      from PyQt5.QtGui import QColor
      from pyqt_live_tuner.parameter_widgets import ColorParameterWidget
      
      def test_color_widget_initialization():
          widget = ColorParameterWidget("TestColor", {"initial": "#FF5500"})
          assert widget.name == "TestColor"
          assert widget.get_value() == "#FF5500"
      
      def test_color_widget_set_value():
          widget = ColorParameterWidget("TestColor")
          widget.set_value("#00FF00")
          assert widget.get_value() == "#00FF00"
      
      def test_color_widget_invalid_value():
          widget = ColorParameterWidget("TestColor")
          widget.set_value("not-a-color")
          # Should default to initial value or fallback
          assert widget.get_value() != "not-a-color"

   Then implement the widget to make the tests pass.

2. **Enhancing Existing Functionality**

   To add validation to a parameter widget:

   .. code-block:: python

      # tests/parameters/test_float_widget_validation.py
      import pytest
      from pyqt_live_tuner.parameter_widgets import FloatParameterWidget
      
      def test_float_widget_validation():
          widget = FloatParameterWidget("Test", {"min": 0, "max": 10})
          
          # Test values within range
          widget.set_value(5)
          assert widget.get_value() == 5
          
          # Test values outside range
          widget.set_value(15)
          assert widget.get_value() == 10  # Should clamp to max
          
          widget.set_value(-5)
          assert widget.get_value() == 0   # Should clamp to min

Mock Testing
----------

Use mocks to isolate components during testing:

.. code-block:: python

   def test_application_builder_run(mocker):
       """Test that ApplicationBuilder.run() shows and executes the app."""
       # Mock QApplication.exec
       mock_exec = mocker.patch('pyqt_live_tuner.application_builder._Application.exec')
       
       # Mock MainApplication.show
       mock_show = mocker.patch('pyqt_live_tuner.MainApplication.show')
       
       # Create and run the application
       app = ApplicationBuilder()
       app.run()
       
       # Assert show and exec were called
       mock_show.assert_called_once()
       mock_exec.assert_called_once()

Continuous Integration
--------------------

PyQt Live Tuner uses continuous integration to run tests automatically:

1. **GitHub Actions Configuration**

   The repository includes GitHub Actions workflows that run tests on each push and pull request.

2. **Local Pre-commit Hooks**

   Use pre-commit hooks to run tests locally before committing:

   .. code-block:: bash

      pip install pre-commit
      pre-commit install

3. **Test Requirements**

   All pull requests must pass tests and maintain code coverage before being merged.

Debugging Tests
-------------

1. **Interactive Debugging**

   Use the `--pdb` flag to drop into the Python debugger on test failures:

   .. code-block:: bash

      pytest --pdb tests

2. **Test Output Capture**

   To see print statements and logs during tests:

   .. code-block:: bash

      pytest -s tests

3. **Temporary Test Files**

   Use the `tmp_path` fixture for temporary file operations during tests:

   .. code-block:: python

      def test_save_configuration(tmp_path):
          """Test saving a configuration to a file."""
          container = ParametersContainer()
          container.add_param(FloatParameterWidget("Float", {"initial": 5.0}))
          
          # Create a temporary file path
          file_path = tmp_path / "config.json"
          
          # Save the configuration
          save_config(container.get_values(), file_path)
          
          # Load the configuration and verify
          with open(file_path) as f:
              loaded_config = json.load(f)
          
          assert loaded_config["Float"] == 5.0