from setuptools import setup, find_packages

setup(
    name="gmail-cleanup",
    version="0.1.0",
    author="Your Name",
    description="Delete all unread Gmail threads via API",
    packages=find_packages(),
    install_requires=[
        "google-api-python-client",
        "google-auth-httplib2",
        "google-auth-oauthlib"
    ],
    entry_points={
    'console_scripts': [
        'gmail-cleanup = gmail_cleanup.cli:cli_main'
    ]
},
)
