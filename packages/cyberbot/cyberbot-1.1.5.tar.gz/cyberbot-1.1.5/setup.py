from setuptools import setup, find_packages

setup(
    name="cyberbot",
    version="1.1.5",
    description="CyberBot is a versatile AI-powered automation bot and SDK designed for developers and tech enthusiasts. It simplifies bot creation, automates repetitive tasks, and enables seamless API integration. With support for Python and JavaScript, CyberBot helps you manage workflows, monitor activity, and interact with servers effortlessly—all while keeping security and scalability in mind.",
    author="Alex Austin",
    author_email="benmap40@gmail.com",
    license="MIT",
    packages=find_packages(),
    install_requires=["Flask", "pycryptodome", "cryptography"],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Framework :: Flask",
    ],
)