import io
from setuptools import setup, find_packages

with io.open('README.md', 'rt', encoding="utf8") as f:
    readme = f.read()

setup(
    name='lektor-all-in-one-accessibility',
    version='1.0.0',
    description='Website accessibility widget for improving WCAG 2.0, 2.1, 2.2 and ADA compliance!',
    author='Skynet Technologies USA LLC',
    author_email='developer3@skynettechnologies.com',
    license='MIT',
    long_description=readme,
    long_description_content_type='text/markdown',
    # url='',
    packages=find_packages(),
    py_modules=['plugin'],
    entry_points={
        'lektor.plugins': [
            'all-in-one-accessibility = plugin:AccessibilityPlugin',
        ]
    },
    install_requires=[
        'requests',  
    ],
    classifiers=[
        'Framework :: Lektor',
        'Environment :: Plugins',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)
