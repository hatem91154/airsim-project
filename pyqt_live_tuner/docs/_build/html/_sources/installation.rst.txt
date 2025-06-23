Installation Guide
==================

To install PyQt Live Tuner, follow these steps:

1. **Ensure Python is Installed**:

   PyQt Live Tuner requires Python 3.8 or higher. Check your Python version:

   .. code-block:: bash

      python --version

   If Python is not installed, download and install it from [python.org](https://www.python.org/).

2. **Set Up a Virtual Environment**:

   It is recommended to use a virtual environment to manage dependencies. Create and activate a virtual environment:

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install the Package**:

   Use pip to install the package:

   .. code-block:: bash

      pip install pyqt-live-tuner

4. **Verify the Installation**:

   After installation, verify that the package is installed correctly:

   .. code-block:: bash

      python -c "import pyqt_live_tuner; print('PyQt Live Tuner installed successfully!')"

5. **Install Additional Dependencies**:

   If you encounter issues, ensure that all dependencies are installed:

   .. code-block:: bash

      pip install PyQt5 qdarktheme

6. **Troubleshooting**:

   - If you encounter locale errors, set a valid locale:

     .. code-block:: bash

        export LC_ALL=en_US.UTF-8
        export LANG=en_US.UTF-8

   - If pip is not recognized, ensure it is installed and added to your PATH.

   - For permission errors, use the `--user` flag:

     .. code-block:: bash

        pip install --user pyqt-live-tuner