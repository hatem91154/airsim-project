from setuptools import setup, find_packages

setup(
    name='pyqt_live_tuner',
    version='0.1.0',
    description='A PyQt-based live tuner application.',
    author='',
    author_email='@gmail.com',
    url='https://github.com/your-repo/pyqt_live_tuner',
    packages=find_packages(include=["pyqt_live_tuner", "pyqt_live_tuner.*"]),
    install_requires=[
        "PyQt5",
        "pyqtdarktheme",
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
