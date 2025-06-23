Examples
========

This section provides comprehensive examples of how to use PyQt Live Tuner in various scenarios. Each example is fully documented with code snippets and explanations.

Basic Usage Examples
-------------------

Simple Parameter Tuning
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pyqt_live_tuner import *
   
   # Initialize the application
   app = ApplicationBuilder(title="Basic Parameter Tuner")
   
   # Create parameter widgets
   float_param = FloatParameterWidget("Amplitude", {"min": 0, "max": 10, "step": 0.1, "initial": 5.0})
   bool_param = BoolParameterWidget("Enable Filter", {"initial": True})
   
   # Register callbacks
   def on_param_change(name, value):
       print(f"{name} changed to: {value}")
       # Here you would typically update your application state based on the parameter change
   
   float_param.register_callback(on_param_change)
   bool_param.register_callback(on_param_change)
   
   # Add parameters to the application
   app.main_window.add_parameter(float_param)
   app.main_window.add_parameter(bool_param)
   
   # Run the application
   app.run()

Multiple Parameter Groups
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pyqt_live_tuner import *
   
   # Initialize the application
   app = ApplicationBuilder(title="Parameter Groups Example")
   
   # Create PID controller parameter group
   pid_group = LinkedParameterGroup("PID Controller")
   pid_group.add_parameter(FloatParameterWidget("Kp", {"min": 0, "max": 10, "step": 0.1, "initial": 1.0}))
   pid_group.add_parameter(FloatParameterWidget("Ki", {"min": 0, "max": 10, "step": 0.1, "initial": 0.5}))
   pid_group.add_parameter(FloatParameterWidget("Kd", {"min": 0, "max": 10, "step": 0.1, "initial": 0.2}))
   
   # Create filter parameter group
   filter_group = LinkedParameterGroup("Filter Settings")
   filter_group.add_parameter(FloatParameterWidget("Cutoff", {"min": 1, "max": 1000, "step": 1, "initial": 100}))
   filter_group.add_parameter(DropdownParameterWidget("Type", {"options": ["Lowpass", "Highpass", "Bandpass"], "initial": "Lowpass"}))
   
   # Register callbacks
   def on_pid_change(group_name, values):
       print(f"{group_name} parameters updated: {values}")
       # Update PID controller with new values
   
   def on_filter_change(group_name, values):
       print(f"{group_name} parameters updated: {values}")
       # Update filter with new values
   
   pid_group.register_callback(on_pid_change)
   filter_group.register_callback(on_filter_change)
   
   # Add parameter groups to the application
   app.main_window.add_parameter_group(pid_group)
   app.main_window.add_parameter_group(filter_group)
   
   # Run the application
   app.run()

Advanced Examples
----------------

Real-time Image Processing
^^^^^^^^^^^^^^^^^^^^^^^^^

This example shows how to use PyQt Live Tuner to adjust parameters for real-time image processing:

.. code-block:: python

   import cv2
   import numpy as np
   from PyQt5.QtWidgets import QLabel
   from PyQt5.QtGui import QImage, QPixmap
   from PyQt5.QtCore import Qt, QTimer
   from pyqt_live_tuner import *
   
   class ImageProcessor:
       def __init__(self):
           self.blur_size = 5
           self.threshold = 127
           self.use_adaptive = False
       
       def process(self, image):
           # Apply blur
           if self.blur_size > 1:
               blurred = cv2.GaussianBlur(image, (self.blur_size, self.blur_size), 0)
           else:
               blurred = image.copy()
           
           # Apply threshold
           if self.use_adaptive:
               thresholded = cv2.adaptiveThreshold(
                   blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                   cv2.THRESH_BINARY, 11, 2)
           else:
               _, thresholded = cv2.threshold(blurred, self.threshold, 255, cv2.THRESH_BINARY)
           
           return thresholded
   
   # Create the application and processor
   app = ApplicationBuilder(title="Image Processing Tuner")
   processor = ImageProcessor()
   
   # Create image display widget
   image_label = QLabel()
   image_label.setMinimumSize(640, 480)
   image_label.setAlignment(Qt.AlignCenter)
   
   # Create parameter widgets
   blur_widget = FloatParameterWidget("Blur Size", {"min": 1, "max": 15, "step": 2, "initial": 5})
   blur_widget.valueChanged.connect(lambda _, val: setattr(processor, 'blur_size', int(val)))
   
   threshold_widget = FloatParameterWidget("Threshold", {"min": 0, "max": 255, "step": 1, "initial": 127})
   threshold_widget.valueChanged.connect(lambda _, val: setattr(processor, 'threshold', int(val)))
   
   adaptive_widget = BoolParameterWidget("Use Adaptive Threshold", {"initial": False})
   adaptive_widget.valueChanged.connect(lambda _, val: setattr(processor, 'use_adaptive', val))
   
   # Add widgets to app
   app.main_window.add_parameter(blur_widget)
   app.main_window.add_parameter(threshold_widget)
   app.main_window.add_parameter(adaptive_widget)
   app.main_window.add_configuration_widget(image_label, "Processed Image")
   
   # Setup video capture and processing loop
   cap = cv2.VideoCapture(0)
   
   def update_frame():
       ret, frame = cap.read()
       if ret:
           # Convert to grayscale and process
           gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
           processed = processor.process(gray)
           
           # Convert to QImage and display
           h, w = processed.shape
           q_img = QImage(processed.data, w, h, w, QImage.Format_Grayscale8)
           pixmap = QPixmap.fromImage(q_img)
           image_label.setPixmap(pixmap.scaled(640, 480, Qt.KeepAspectRatio))
   
   # Setup timer for frame updates
   timer = QTimer()
   timer.timeout.connect(update_frame)
   timer.start(30)  # 30ms = ~33 fps
   
   # Run the application
   app.run()
   
   # Clean up
   cap.release()

Custom Parameter Widgets
^^^^^^^^^^^^^^^^^^^^^^

Example of creating your own custom parameter widget:

.. code-block:: python

   from PyQt5.QtWidgets import QColorDialog, QPushButton
   from PyQt5.QtGui import QColor
   from PyQt5.QtCore import pyqtSignal
   from pyqt_live_tuner import *
   
   class ColorParameterWidget(ParameterWidget):
       """Custom parameter widget for selecting colors."""
       
       def __init__(self, name="Color", config=None):
           super().__init__(name, config)
           config = config or {}
           
           self.color = QColor(config.get("initial", "#FF0000"))
           self.color_button = QPushButton()
           self.update_button_color()
           
           self.color_button.clicked.connect(self.show_color_dialog)
           self.layout.addWidget(self.color_button)
       
       def update_button_color(self):
           self.color_button.setStyleSheet(
               f"background-color: {self.color.name()}; min-height: 30px;"
           )
           self.color_button.setText(self.color.name())
       
       def show_color_dialog(self):
           color = QColorDialog.getColor(self.color, None, "Select Color")
           if color.isValid() and color != self.color:
               self.color = color
               self.update_button_color()
               self.valueChanged.emit(self.name, self.color.name())
       
       def set_value(self, value):
           if isinstance(value, str):
               self.color = QColor(value)
               self.update_button_color()
       
       def get_value(self):
           return self.color.name()
   
   # Usage example
   app = ApplicationBuilder(title="Custom Color Picker")
   color_widget = ColorParameterWidget("Background Color", {"initial": "#336699"})
   
   def on_color_change(name, value):
       print(f"Color changed to: {value}")
       app.main_window.setStyleSheet(f"QWidget#centralWidget {{ background-color: {value}; }}")
   
   color_widget.register_callback(on_color_change)
   app.main_window.add_parameter(color_widget)
   app.main_window.centralWidget().setObjectName("centralWidget")
   app.run()

Integration Examples
------------------

* :doc:`integration_with_matplotlib`
* :doc:`integration_with_opencv`
* :doc:`integration_with_existing_app`