from setuptools import setup

setup(name='regroup',
      version='0.1',
      description='generate regular expresions describing input strings',
      url='https://github.com/rflynn/regroup',
      author='Ryan Flynn',
      author_email='parseerror+github@gmail.com',
      packages=['regroup'],
      license='MIT',
      #test='nose.collector',
      #tests_require=['nose'],
      test_suite='tests',
      #test_suite='regroup',
      keywords=['regex', 'regular expression', 'strings', 'summarize',
                'text', 'generator', 'induction', 'DAWG', 'automata',
                'clustering', 'lcsp'])
