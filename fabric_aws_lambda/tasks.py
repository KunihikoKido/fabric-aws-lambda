import os
import base64
import json
import tempfile
from fabric.api import local
from fabric.api import lcd
from fabric.api import shell_env
from fabric.tasks import Task

class BaseTask(Task):
    def run(self, *args, **kwargs):
        self.pre_task(*args, **kwargs)
        self.run_main(*args, **kwargs)
        self.post_task(*args, **kwargs)

    def run_main(self, *args, **kwargs):
        pass

    def pre_task(self, *args, **kwargs):
        pass

    def post_task(self, *args, **kwargs):
        pass


class SetupTask(BaseTask):
    """Setup on Local Machine."""
    name = 'setup'

    def __init__(self,
            requirements='requirements.txt',
            lib_path='./lib',
            install_prefix='./local'
        ):
        self.requirements = requirements
        self.lib_path = lib_path
        self.install_prefix = install_prefix
        self.tempdir = tempfile.gettempdir()

    def run_main(self):
        self.install_python_modules()

    def install_python_modules(self):
        options = dict(
            requirements=self.requirements,
            lib_path=self.lib_path
        )

        local("""pip install --upgrade \
            -r {requirements} -t {lib_path}""".format(**options))

class InvokeTask(BaseTask):
    """Invoke function on Local Machine."""
    name = 'invoke'

    def __init__(self,
            lambda_handler='lambda_handler',
            lambda_file='lambda_function.py',
            event_file='event.json',
            lib_path='./lib'
        ):
        self.options = dict(
            lambda_handler=lambda_handler,
            lambda_file=lambda_file,
            event_file=event_file,
            lib_path=lib_path
        )

    def run_main(self, event_file=None):
        self.invoke(event_file)

    def invoke(self, event_file=None):
        if event_file is not None:
            self.options['event_file'] = event_file

        with shell_env(PYTHONPATH=self.lib_path):
            local("""
            python-lambda-local \
                -l {lib_path} \
                -f {lambda_handler} {lambda_file} {event_file}
            """.format(**self.options))


class MakeZipTask(BaseTask):
    """Make zip file for AWS Lambda Function."""
    name = 'makezip'

    def __init__(self,
            zip_file='lambda_function.zip',
            exclude_file='exclude.lst',
            lib_path='./lib'
        ):
        self.zip_file = zip_file
        self.exclude_file = exclude_file
        self.lib_path = lib_path

    def run_main(self):
        self.remove_zip_file()
        self.makezip_basepath()
        self.makezip_python_modules()

    def remove_zip_file(self):
        local('rm -rf {}'.format(self.zip_file))

    def makezip(self):
        options = dict(zip_file=self.zip_file, exclude_file=self.exclude_file)
        local('zip -r9 {zip_file} * -x@{exclude_file}'.format(**options))

    def makezip_basepath(self):
        self.makezip()

    def makezip_python_modules(self):
        if not os.path.exists(self.lib_path):
            return

        with lcd(self.lib_path):
            self.makezip()

class AWSLambdaGetConfigTask(BaseTask):
    """Get function configuration on AWS Lambda."""
    name = 'aws-getconfig'

    def __init__(self, function_name='hello-lambda', qualifier='\$LATEST'):

        self.options = dict(
            function_name=function_name,
            qualifier=qualifier,
        )

    def run_main(self, function_name=None):
        self.get_function_config(function_name)

    def get_function_config(self, function_name=None):
        if function_name is not None:
            self.options['function_name'] = function_name

        result = local("""
        aws lambda get-function-configuration \
            --function-name {function_name} \
            --qualifier {qualifier}
        """.format(**self.options), capture=True)

        print(result)


class AWSLambdaInvokeTask(BaseTask):
    """Invoke function on AWS Lambda."""
    name = 'aws-invoke'

    def __init__(self,
            function_name='hello-lambda',
            invocation_type='RequestResponse',
            log_type='Tail',
            client_context = '',
            payload='file://event.json',
            qualifier='\$LATEST'
        ):

        self.options = dict(
            function_name=function_name,
            invocation_type=invocation_type,
            log_type=log_type,
            payload=payload,
            qualifier=qualifier,
            outfile=os.path.join(tempfile.gettempdir(), 'outfile.txt')
        )

    def run_main(self, function_name=None):
        self.invoke(function_name)

    def invoke(self, function_name=None):
        if function_name is not None:
            self.options['function_name'] = function_name

        result = local("""
        aws lambda invoke \
            --function-name {function_name} \
            --invocation-type {invocation_type} \
            --log-type {log_type} \
            --payload {payload} \
            --qualifier {qualifier} \
            {outfile}
        """.format(**self.options), capture=True)

        self.print_log_result(result)
        self.print_result(self.options['outfile'])

    def print_log_result(self, result):
        result = json.loads(result)
        log_result = result.get('LogResult', '')
        print(base64.b64decode(log_result))

    def print_result(self, outfile):
        with open(outfile) as f:
            print("RESULT: {}".format(f.read()))


class AWSLambdaUpdateCodeTask(BaseTask):
    """Update code on AWS Lambda."""
    name = 'aws-updatecode'

    def __init__(self,
            function_name='hello-lambda',
            zip_file='fileb://lambda_function.zip'
        ):
        self.options = dict(
            function_name=function_name,
            zip_file=zip_file
        )

    def run_main(self, function_name=None):
        if function_name is not None:
            self.options['function_name'] = function_name

        result = local("""
        aws lambda update-function-code \
            --function-name {function_name} \
            --zip-file {zip_file}
        """.format(**self.options), capture=True)

        print(result)
