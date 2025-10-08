from setuptools import setup, find_packages

def readme():
    with open("README.md","r") as f:
        return f.read()


setup(
    name='simple_neural_works',
    version='2.0.2',
    author='TwentyOneError',
    author_email='ourmail20210422@gmail.com',
    description='This is the simplest educational module for quick work with neural networks.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/TwentyOneError/simple_neural_works',
    packages=find_packages(),
    install_requires=['Pillow>=8.2.0','numpy'],
    classifiers=[
    'Programming Language :: Python :: 3.11',
    'Operating System :: OS Independent'
    ],
    keywords='neural networks simple backpropagation regularization Leaky-ReLu ',
    project_urls={
    'GitHub': 'https://github.com/TwentyOneError'
    },
    python_requires='>=3.8'
)