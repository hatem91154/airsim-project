PyQt Live Tuner Documentation
==============================

.. image:: _static/images/pyqt_live_tuner_screenshot.png
   :alt: PyQt Live Tuner Screenshot
   :align: center
   :width: 80%

**Version 0.1.0**

Welcome to the detailed documentation for PyQt Live Tuner, a powerful and flexible parameter tuning library built with PyQt5.

Overview
--------

PyQt Live Tuner provides an intuitive interface for creating parameter adjustment widgets that can be used for real-time tuning of algorithm parameters, configuration settings, or any other adjustable values in your application. The library is designed with flexibility in mind, allowing for seamless integration with existing PyQt applications or as a standalone parameter tuning tool.

Key Features
-----------

- **Rich Parameter Widget Collection**: Float sliders, checkboxes, dropdowns, action buttons, and text inputs
- **Parameter Grouping**: Organize related parameters into logical groups
- **Configuration Management**: Save and load parameter settings from JSON files
- **Real-time Updates**: Parameters emit signals when changed for immediate feedback
- **Dark Theme Support**: Built-in support for dark theme using QDarkTheme
- **Extensible Architecture**: Easy to extend with custom parameter widgets

Installation
-----------

Getting started with PyQt Live Tuner is simple:

.. code-block:: bash

   pip install pyqt-live-tuner

For detailed installation instructions, see the :doc:`installation` page.

Quick Start
----------

.. code-block:: python

   from pyqt_live_tuner import *
   
   # Initialize the application
   app = ApplicationBuilder(title="Parameter Tuner")
   
   # Create parameter widgets
   float_param = FloatParameterWidget("Threshold", {"min": 0, "max": 100, "step": 0.1})
   bool_param = BoolParameterWidget("Enable Feature")
   
   # Register callbacks for parameter changes
   def on_param_change(name, value):
       print(f"{name} changed to: {value}")
   
   float_param.register_callback(on_param_change)
   bool_param.register_callback(on_param_change)
   
   # Add parameters to the application
   app.main_window.add_parameter(float_param)
   app.main_window.add_parameter(bool_param)
   
   # Run the application
   app.run()

For detailed usage examples and tutorials, see the :doc:`usage` page.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   examples/index
   advanced_usage/index
   api_reference
   contributing
   changelog
   configuration
   testing

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

