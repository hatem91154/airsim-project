Configuration Guide
===================

This comprehensive guide explains how to configure PyQt Live Tuner and work with configuration files. It covers all aspects of configuration management, from basic usage to advanced scenarios.

Configuration File Format
-----------------------

PyQt Live Tuner uses JSON as its configuration file format. This provides several advantages:

* Human-readable and editable
* Compatible with many programming languages
* Supports nested structures
* Easy to parse and generate

Basic Structure
^^^^^^^^^^^^^

A typical configuration file has the following structure:

.. code-block:: json

   {
     "parameter_name": value,
     "another_parameter": value,
     "group_name": {
       "parameter_in_group": value,
       "another_parameter_in_group": value
     }
   }

The top-level keys correspond to parameter names or group names. Values for parameters can be:

* **Numbers** (both integers and floating-point)
* **Booleans** (true/false)
* **Strings** (text values)
* **Nested objects** (for parameter groups)

Example Configuration
^^^^^^^^^^^^^^^^^^

Here's an example configuration file for an image processing application:

.. code-block:: json

   {
     "Threshold": 127,
     "Use Edge Detection": true,
     "Output Format": "PNG",
     "Filter Settings": {
       "Blur Size": 5,
       "Filter Type": "Gaussian",
       "Apply Sharpening": false
     },
     "Advanced Options": {
       "Worker Threads": 4,
       "Processing Mode": "Batch",
       "Cache Size": 256
     }
   }

Saving Configurations
-------------------

There are three ways to save configurations in PyQt Live Tuner:

1. **Using the UI**

   The easiest method is to use the built-in menu options:

   * **File → Save**: Save to the last used file
   * **File → Save As...**: Save to a new file

   This will save all current parameter values to the selected file.

2. **Using the ParametersContainer API**

   You can programmatically save configurations:

   .. code-block:: python

      import json
      
      app = ApplicationBuilder()
      # Add parameters...
      
      # Get all parameter values
      values = app.main_window.parameters_container.get_values()
      
      # Save to a file
      with open("config.json", "w") as f:
          json.dump(values, f, indent=2)

3. **Auto-saving Configurations**

   For applications that need automatic saving, you can implement an auto-save feature:

   .. code-block:: python

      import json
      import time
      from PyQt5.QtCore import QTimer
      
      class ConfigAutoSaver:
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
      # ... add parameters
      
      # Set up auto-save
      auto_saver = ConfigAutoSaver(
          app.main_window.parameters_container,
          f"configs/autosave_{int(time.time())}.json"
      )

Loading Configurations
--------------------

Similar to saving, there are multiple ways to load configurations:

1. **Using the UI**

   Use the built-in menu options:

   * **File → Load**: Load from a file
   * **File → Generate**: (Actually opens a save dialog where you can specify a file name for generating a new config based on current values)

2. **Using the ParametersContainer API**

   Load configurations programmatically:

   .. code-block:: python

      import json
      
      app = ApplicationBuilder()
      # Add parameters...
      
      # Load from a file
      with open("config.json", "r") as f:
          values = json.load(f)
      
      # Apply values to parameters
      app.main_window.parameters_container.set_values(values)

3. **Loading at Startup**

   To load a configuration when your application starts:

   .. code-block:: python

      import json
      import os
      
      def load_default_config(app, config_path="default_config.json"):
          if os.path.exists(config_path):
              try:
                  with open(config_path, "r") as f:
                      values = json.load(f)
                  app.main_window.parameters_container.set_values(values)
                  print(f"Loaded configuration from {config_path}")
              except Exception as e:
                  print(f"Error loading configuration: {e}")
      
      # Usage
      app = ApplicationBuilder()
      # ... add parameters
      
      # Load default config
      load_default_config(app)
      
      # Run the app
      app.run()

4. **Multiple Configuration Presets**

   You can implement a dropdown to select from multiple configuration presets:

   .. code-block:: python

      import json
      import os
      
      def load_preset_config(container, preset_name):
          path = f"presets/{preset_name}.json"
          if os.path.exists(path):
              with open(path, "r") as f:
                  values = json.load(f)
              container.set_values(values)
              print(f"Loaded preset: {preset_name}")
      
      # Usage
      app = ApplicationBuilder()
      # ... add parameters
      
      # Get all preset names
      preset_files = [f[:-5] for f in os.listdir("presets") if f.endswith(".json")]
      
      # Create a dropdown for preset selection
      preset_selector = DropdownParameterWidget(
          "Preset", {"options": preset_files, "placeholder": "Select preset..."}
      )
      
      # Register callback
      preset_selector.register_callback(
          lambda _, preset: load_preset_config(app.main_window.parameters_container, preset)
      )
      
      # Add the selector
      app.main_window.add_parameter(preset_selector)

Configuration Validation
----------------------

Before loading or applying configurations, it's important to validate them:

1. **Basic Validation**

   .. code-block:: python

      def validate_config(config, schema):
          """Validate configuration against a schema dictionary.
          
          Args:
              config: The configuration dictionary to validate
              schema: A dictionary with parameter names as keys and expected types as values
                     ('int', 'float', 'bool', 'str', or 'dict')
          
          Returns:
              A tuple: (is_valid, error_message)
          """
          for key, expected_type in schema.items():
              if key not in config:
                  return False, f"Missing required parameter: {key}"
              
              if expected_type == 'int':
                  if not isinstance(config[key], int):
                      return False, f"Parameter {key} should be an integer"
              elif expected_type == 'float':
                  if not isinstance(config[key], (int, float)):
                      return False, f"Parameter {key} should be a number"
              elif expected_type == 'bool':
                  if not isinstance(config[key], bool):
                      return False, f"Parameter {key} should be a boolean"
              elif expected_type == 'str':
                  if not isinstance(config[key], str):
                      return False, f"Parameter {key} should be a string"
              elif expected_type == 'dict':
                  if not isinstance(config[key], dict):
                      return False, f"Parameter {key} should be an object"
          
          return True, ""
      
      # Usage
      schema = {
          "Threshold": "int",
          "Use Edge Detection": "bool",
          "Filter Settings": "dict"
      }
      
      is_valid, error = validate_config(loaded_config, schema)
      if not is_valid:
          print(f"Invalid configuration: {error}")
      else:
          container.set_values(loaded_config)

2. **Schema-Based Validation**

   For more complex validation needs, consider using the `jsonschema` package:

   .. code-block:: python

      from jsonschema import validate, ValidationError
      
      # Define a JSON Schema for validation
      schema = {
          "type": "object",
          "properties": {
              "Threshold": {
                  "type": "integer",
                  "minimum": 0,
                  "maximum": 255
              },
              "Use Edge Detection": {
                  "type": "boolean"
              },
              "Filter Settings": {
                  "type": "object",
                  "properties": {
                      "Blur Size": {
                          "type": "integer",
                          "minimum": 1,
                          "maximum": 21,
                          "multipleOf": 2  # Must be odd (e.g., 3, 5, 7...)
                      },
                      "Filter Type": {
                          "type": "string",
                          "enum": ["Gaussian", "Box", "Median"]
                      }
                  },
                  "required": ["Blur Size", "Filter Type"]
              }
          },
          "required": ["Threshold", "Use Edge Detection"]
      }
      
      # Validate a configuration
      try:
          validate(instance=loaded_config, schema=schema)
          print("Configuration is valid")
          container.set_values(loaded_config)
      except ValidationError as e:
          print(f"Invalid configuration: {e.message}")

Advanced Configuration Techniques
------------------------------

1. **Environment-Specific Configurations**

   Load different configurations based on the environment:

   .. code-block:: python

      import os
      import json
      
      def load_config_for_environment():
          env = os.environ.get("APP_ENV", "development")
          config_file = f"configs/config.{env}.json"
          
          if os.path.exists(config_file):
              with open(config_file, "r") as f:
                  return json.load(f)
          else:
              # Fallback to default config
              with open("configs/config.default.json", "r") as f:
                  return json.load(f)

2. **Layered Configurations**

   Implement layered configurations by merging multiple config files:

   .. code-block:: python

      def deep_merge(base, overlay):
          """Recursively merge two dictionaries."""
          merged = base.copy()
          
          for key, value in overlay.items():
              if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                  merged[key] = deep_merge(merged[key], value)
              else:
                  merged[key] = value
          
          return merged
      
      def load_layered_config():
          # Load base configuration
          with open("configs/base.json", "r") as f:
              base_config = json.load(f)
          
          # Load user overrides if they exist
          user_config = {}
          if os.path.exists("configs/user.json"):
              with open("configs/user.json", "r") as f:
                  user_config = json.load(f)
          
          # Merge configurations
          return deep_merge(base_config, user_config)

3. **Configuration Versioning**

   Include a version field in your configurations:

   .. code-block:: json

      {
        "config_version": "1.2.0",
        "parameters": {
          "Threshold": 127,
          "Use Edge Detection": true
        }
      }

   Handle version differences in your code:

   .. code-block:: python

      import semver
      
      def load_versioned_config(file_path):
          with open(file_path, "r") as f:
              config = json.load(f)
          
          # Check configuration version
          current_version = "1.2.0"
          config_version = config.get("config_version", "1.0.0")
          
          if semver.compare(config_version, current_version) > 0:
              print(f"Warning: Configuration version {config_version} is newer than the application version {current_version}")
          
          # Handle version differences
          if semver.compare(config_version, "1.1.0") < 0:
              # Convert from old format to new format
              if "threshold" in config:
                  config["Threshold"] = config.pop("threshold")
          
          return config.get("parameters", config)

Best Practices
------------

1. **Use Descriptive Parameter Names**

   Choose clear and descriptive parameter names to make configurations self-explanatory:

   .. code-block:: json

      {
        "image_processing": {
          "gaussian_blur_sigma": 1.5,
          "edge_detection_threshold": 50
        }
      }

2. **Comment Your Configuration Files**

   While JSON doesn't support comments natively, use a preprocessor or README file to document your configurations.

3. **Validate Configurations**

   Always validate configurations before applying them to prevent errors.

4. **Use Default Values**

   Provide default values for all parameters in case the configuration is missing or invalid.

5. **Handle Errors Gracefully**

   Implement error handling when loading configurations:

   .. code-block:: python

      try:
          with open("config.json", "r") as f:
              config = json.load(f)
          container.set_values(config)
      except FileNotFoundError:
          print("Configuration file not found, using defaults")
      except json.JSONDecodeError:
          print("Invalid JSON in configuration file, using defaults")
      except Exception as e:
          print(f"Error loading configuration: {e}")

6. **Keep Backups**

   Automatically create backups before overwriting configurations:

   .. code-block:: python

      import shutil
      import time
      
      def save_with_backup(container, file_path):
          # Create backup if file exists
          if os.path.exists(file_path):
              timestamp = time.strftime("%Y%m%d_%H%M%S")
              backup_path = f"{file_path}.{timestamp}.bak"
              shutil.copy2(file_path, backup_path)
          
          # Save new configuration
          with open(file_path, "w") as f:
              json.dump(container.get_values(), f, indent=2)

7. **Use Environment Variables for Sensitive Data**

   For configurations with sensitive information:

   .. code-block:: python

      import os
      
      # Get sensitive information from environment
      api_key = os.environ.get("API_KEY", "")
      
      # Include in configuration
      config = {
          "api_settings": {
              "url": "https://api.example.com",
              "key": api_key
          }
      }
      
      # Apply to parameter widgets
      container.set_values(config)