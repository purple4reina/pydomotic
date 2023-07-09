# Deploying

Deployment of `pydomotic` simply requires an environment that will execute code once per minute on your behalf. This lends itself well to strategies such as [cron jobs](https://en.wikipedia.org/wiki/Cron) and serverless platforms like [AWS Lambda](https://aws.amazon.com/lambda/) or Google Cloud Run.

## Cron

On any unix system with cron support, open the crontab file with `crontab -e` and add the following line to install a new cron job to run `pydomotic` once per minute.

```cron
* * * * * python3 -m pydomotic --config-file /path/to/pydomotic.yml
```

Ensure that `pydomotic` is installed globally in this case.

## AWS Lambda

`pydomotic` is well suited for running on AWS Lambda and is the recommended deployment method for anyone looking for serious longterm reliability of their home automations with `pydomotic`.

### Installation

This walk through will take you through the steps of deploying `pydomotic` to AWS Lambda using the [Serverless Framework](https://www.serverless.com/).

1. Install Serverless Framework.

    ```bash
    $ npm install -g serverless
    ```

1. Ensure you have [AWS Credentials](https://www.serverless.com/framework/docs/providers/aws/guide/credentials/) set up. This will involve configuring and setting the following environment variables.

    ```bash
    $ export AWS_ACCESS_KEY_ID=<your-key-here>
    $ export AWS_SECRET_ACCESS_KEY=<your-secret-key-here>
    ```

1. Create a `serverless.yml` file with the following contents.

    ```yaml
    service: pydomotic

    provider:
      name: aws
      runtime: python3.9
      region: us-east-1  # replace as desired

    package:
      patterns:
        - '!**'
        - 'pydomotic.yml'

    plugins:
      - serverless-python-requirements

    functions:
      cron:
        handler: pydomotic.lambda_handler.handler
        events:
          - schedule:
              rate: rate(1 minute)
    ```

1. Create your `pydomotic.yml` file as descrbed in [CONFIGURATION.md](./CONFIGURATION.md). Save it to the same directory as your `serverless.yml` file.

1. The `serverless-python-requirements` plugin is used to manage and install dependencies.

    ```bash
    $ sls plugin install -n serverless-python-requirements
    ```

    This plugin will look for a `requirements.txt` file in the same directory as your `serverless.yml` file and deploy your lambda function along with all dependencies listed in this requirements file.

    Use [Python Virtualenv](https://virtualenv.pypa.io/en/latest/) to create this requirements file. This will create a virtual environment in the `env` directory and install `pydomotic` to it.

    ```bash
    $ pip install virtualenv
    $ virtualenv env
    $ source env/bin/activate
    $ pip install pydomotic
    ```

    <!-- Include on demand package installation here -->

    Lastly, create your `requirements.txt` file by taking a snapshot of your virtual environment.

    ```bash
    $ pip freeze > requirements.txt
    ```

1. Deploy your function.

    ```bash
    $ serverless deploy
    ```