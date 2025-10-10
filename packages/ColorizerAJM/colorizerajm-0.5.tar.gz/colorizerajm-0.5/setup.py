from setuptools import setup
import re
project_name = 'ColorizerAJM'


def get_property(prop, project):
    result = re.search(r'{}\s*=\s*[\'"]([^\'"]*)[\'"]'.format(prop), open(project + '/_version.py').read())
    return result.group(1)


setup(
    name=project_name,
    version=get_property('__version__', project_name),
    packages=['ColorizerAJM'],
    url='https://github.com/amcsparron2793-Water/ColorizerAJM',
    download_url=f'https://github.com/amcsparron2793-Water/ColorizerAJM/archive/refs/tags/{get_property("__version__", project_name)}.tar.gz',
    keywords=[],
    license='MIT License',
    author='Amcsparron',
    author_email='amcsparron@albanyny.gov',
    description='Taken from https://medium.com/@ryan_forrester_/adding-color-to-python-terminal-output-a-complete-guide-147fcb1c335f uses ANSI escape codes to colorize terminal output',
    # this is for pypi categories etc
    classifiers=[
        'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',      # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',   # Again, pick a license
        'Programming Language :: Python :: 3',      # Specify which python versions that you want to support
    ]
)
