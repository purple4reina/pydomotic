# Deploying

Deployment of `pydomotic` simply requires an environment that will execute code once per minute. This lends itself well to strategies such as [cron jobs](#cron) and serverless platforms like [AWS Lambda](#aws-lambda) or Google Cloud Run.

## Cron

On any unix system with cron support, open the crontab file with `crontab -e` and add the following line to install a new cron job to run `pydomotic` once per minute.

```cron
* * * * * python3 -m pydomotic --config-file /path/to/pydomotic.yml
```

Ensure that `pydomotic` is installed globally in this case.
