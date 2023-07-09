# Deploying

Deployment of `pydomotic` simply requires an environment that will execute code once per minute on your behalf. This lends itself well to strategies such as [cron jobs](https://en.wikipedia.org/wiki/Cron) and serverless platforms like [AWS Lambda](https://aws.amazon.com/lambda/) or Google Cloud Run.

## Cron

On any unix system with cron support, open the crontab file with `crontab -e` and add the following line to install a new cron job to run `pydomotic` once per minute.

```cron
* * * * * python3 -m pydomotic --config-file /path/to/pydomotic.yml
```

Ensure that `pydomotic` is installed globally in this case.

Note that if you wish to load configuration from AWS S3 (in addition to installing any required dependencies for [providers](./CONFIGURATION.md#providers)) you must run the following command. This is not required when deploying to AWS Lambda because the runtime already provides required dependencies.

```bash
$ pip install pydomotic[s3]
```

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

1. Create a `serverless.yml` file with the following contents. Add any required environment variables as described in the [Providers](#providers) section below.

    ```yaml
    # serverless.yml

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

    Next, install dependencies for each [provider](./CONFIGURATION.md#providers) you intend to use. Only run the parts of the commands below that apply to your use case.

    ```bash
    $ pip install pydomotic[tuya]
    $ pip install pydomotic[airthings]
    $ pip install pydomotic[moen]
    $ pip install pydomotic[fujitsu]
    ```

    Lastly, create your `requirements.txt` file by taking a snapshot of your virtual environment.

    ```bash
    $ pip freeze > requirements.txt
    ```

1. Deploy your function.

    ```bash
    $ serverless deploy
    ```

### Advanced

#### Providers

As described in [CONFIGURATION.md](./CONFIGURATION.md#providers), each IoT provider requires login credentials. For example, the `tuya` provider requires four credentials. When writing your `pydomotic.yml` file, you can tell `pydomotic` to load these values from plaintext or from environment variables. To load from environment use the `${env:ENV_VAR_NAME}` pattern:

```yaml
# pydomotic.yml

providers:
  tuya:
    username: ${env:TUYA_USERNAME}
    password: ${env:TUYA_PASSWORD}
    access_id: ${env:TUYA_ACCESS_ID}
    access_key: ${env:TUYA_ACCESS_KEY}
```

These environment variables will then need to be made available to your lambda function by specifying them in your `serverless.yml` file.

```yaml
# serverless.yml

provider:
  name: aws
  environment:
    TUYA_USERNAME: ${env:TUYA_USERNAME}
    TUYA_PASSWORD: ${env:TUYA_PASSWORD}
    TUYA_ACCESS_ID: ${env:TUYA_ACCESS_ID}
    TUYA_ACCESS_KEY: ${env:TUYA_ACCESS_KEY}
```

If you are using source control (like git) for your `serverless.yml` file, it is highly recommended for security reasons not to commit these credentials. Instead, it is recommended that these secrets be loaded from local environment variables as shown in the example above. This means you will need to change your deploy command to:

```bash
$ TUYA_USERNAME='my-username' \
    TUYA_PASSWORD='my-password' \
    TUYA_ACCESS_ID='my-access-id' \
    TUYA_ACCESS_KEY='my-access-key' \
        serverless deploy
```

#### Timeout Settings

Since you won't be able to control the behavior of any 3rd party APIs, it is recommended that you set a timeout on your lambda function. Since AWS Lambda will retry any function that ends due to a raised exception. Therefore, it is important that should your function fail due to timeouts, it should not overlap with the next invocation one minute later.

For this reason, no more than a 30-second timeout is recommended. This can be set in the provider section of the `serverless.yml` file.

```yaml
# serverless.yml

provider:
  name: aws
  timeout: 30  # seconds
  ...
```

#### Deploying from Mac M1

When deploying from a computer with Apple's M1 processing chip, you will need to either cross compile dependencies or change the architecture of your deployed lambda function. The easiest way to do this is to add `architecture: arm64` to the provider section of your `serverless.yml` file.

```yaml
# serverless.yml

provider:
  name: aws
  architecture: arm64  # instruct lambda to use same processor type as your local computer
  ...
```

#### Loading config from S3

If you wish to store your `pydomotic.yml` file in [AWS S3](https://aws.amazon.com/s3/), you will need to instruct `pydomotic` how to find it.

After uploading your `pydomotic.yml` file to S3, update your `serverless.yml` file to give your lambda permission to read the file and tell `pydomotic` where to find it.

```yaml
# serverless.yml

provider:
  name: aws
  ...
  environment:
    # bucket/key for your pydomotic.yml file in S3
    PYDOMOTIC_CONFIG_S3: home-automations/pydomotic.yml
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - 's3:GetObject'
          Resource:
            # arn for your pydomotic.yml file in S3
            - 'arn:aws:s3:::home-automations/pydomotic.yml'

package:
  patterns:
    - '!**'
    # 'pydomotic.yml' pattern removed

functions:
  cron:
    ...
```

Be sure to change the value `home-automations/pydomotic.yml` to match the bucket and key where you stored your file in S3.

<!--
  - ${env:ENV_VAR} usage
  - iam
  - patterns
-->

#### Webhooks

If you wish to use the [Webhook Trigger](./CONFIGURATION.md#webhook-trigger), you will need to specify a url for your lambda function.

```yaml
# serverless.yml

functions:
  cron:
    handler: pydomotic.lambda_handler.handler
    url: true  # required for webhook trigger
    events:
      - schedule:
          rate: rate(1 minute)
```