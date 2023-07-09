# Configuration

<!-- https://luciopaiva.com/markdown-toc/ -->
- [General](#general)
- [Providers](#providers)
  - [Tuya](#tuya)
  - [Airthings](#airthings)
  - [Moen](#moen)
  - [Fujitsu](#fujitsu)
  - [Noop](#noop)
- [Devices](#devices)
- [Automations](#automations)
- [Triggers](#triggers)
  - [AQI Trigger](#aqi-trigger)
  - [Time Trigger](#time-trigger)
  - [Weekday Trigger](#weekday-trigger)
  - [Date Trigger](#date-trigger)
  - [Cron Trigger](#cron-trigger)
  - [Random Trigger](#random-trigger)
  - [Sunrise/Sunset Trigger](#sunrisesunset-trigger)
  - [Temperature Trigger](#temperature-trigger)
  - [Radon Trigger](#radon-trigger)
  - [Webhook Trigger](#webhook-trigger)
  - [Device (Sensor) Trigger](#device-sensor-trigger)
- [Actions](#actions)
  - [Turn On/Off Action](#turn-onoff-action)
  - [Switch Action](#switch-action)
  - [Set Mode Action](#set-mode-action)
  - [Execute Code Action](#execute-code-action)

## General

All configuration is written in [yaml](https://yaml.org/). It can be loaded either from a local file or [Amazon S3](https://aws.amazon.com/s3/) bucket.

When run, parsers will search for configuration in order, once found it will load this configuration. Search order is:

+ Local file, when a file name is given via commandline or code
+ S3 file, when S3 bucket and key information are given via code
+ Local file, when `PYDOMOTIC_CONFIG_FILE` is set
+ S3 file, when `PYDOMOTIC_CONFIG_S3` is set
+ Local file `pydomotic.yml`

When run via the commandline, the configuration file can be specified as an argument or via environment variable.

```bash
$ python -m pydomotic -c /path/to/pydomotic.yml
$ PYDOMOTIC_CONFIG_FILE=/path/to/pydomotic.yml python -m pydomotic
```

When defined in code, S3 configuration is given as a tuple or string in the form `bucket/key`.

```python
handler = LambdaHandler(s3=('my-bucket', 'my-key'))
# or
handler = LambdaHandler(s3='my-bucket/my-key')
```

Otherwise, it must be given as a string in the form `bucket/key`.

```bash
$ PYDOMOTIC_CONFIG_S3=my-bucket/my-key python -m pydomotic
```

Configuration is grouped into four headings: [providers](#providers), [triggers](#triggers), [devices](#devices), and [automations](#automations).

Reading values from environment variables is available in the form of `${env:MY_ENV_VAR}`.

For a complete example configuration file, see [`tests/testdata/full.yml`](./tests/testdata/full.yml).

## Providers

Currently, four providers are provided out of the box.

+ [**Tuya:**](#tuya) Any device that is supported by the Tuya platform. Many IoT manufacturers rely on Tuya for their device APIs. Supported by the [`gosundpy`](https://github.com/purple4reina/gosundpy) Python package.
+ [**Airthings:**](#airthings) Any of the Airthings View devices.
+ [**Moen:**](#moen) The Flo by Moen smart water shutoff valve.
+ [**Fujitsu:**](#fujitsu) Any Fujitsu WiFi enabled home heat pump system, supported by the [`pyfujitseu`](https://github.com/xerxes87/pyfujitseu) Python package.
+ [**Noop:**](#noop) A generic provider which can be assigned to any device, useful for testing.

Contributions and requests for further support are welcome.

Each provider relies on its own dependencies which are not installed by default. This means that for each provider you wish to use (aside from the Noop provider), you must specifically install its dependencies. These are installed as pip extras:

```bash
$ pip install pydomotic[tuya]
$ pip install pydomotic[airthings]
$ pip install pydomotic[moen]
$ pip install pydomotic[fujitsu]
```

### Tuya

```yaml
providers:
  tuya:
    username: ${env:TUYA_USERNAME}
    password: ${env:TUYA_PASSWORD}
    access_id: ${env:TUYA_ACCESS_ID}
    access_key: ${env:TUYA_ACCESS_KEY}
    device_status_cache_seconds: 20

devices:
  my-device:
    description: my cool device
    provider: tuya
    id: '1234567890'
```

**username:** _(required)_ Your Tuya username.

**password:** _(required)_ Your Tuya password.

**access_id:** _(required)_ Your Tuya access id.

**access_key:** _(required)_ Your Tuya access key.

**device_status_cache_seconds:** _(optional)_ Time in seconds for caching any device statuses. Useful to reduce the number of API calls being made when referencing the same device from multiple components.

### Airthings

```yaml
providers:
  airthings:
    client_id: ${env:AIRTHINGS_CLIENT_ID}
    client_secret: ${env:AIRTHINGS_CLIENT_SECRET}
    data_cache_seconds: 20

devices:
  my-device:
    description: my cool device
    provider: airthings
    id: '1234567890'
```

**client_id:** _(required)_ Your Airthings client id.

**client_secret:** _(required)_ Your Airthings client secret.

**data_cache_seconds:** _(optional)_ Time in seconds for caching any device statuses. Useful to reduce the number of API calls being made when referencing the same device from multiple components.

### Moen

```yaml
providers:
  moen:
    username: ${env:MOEN_USERNAME}
    password: ${env:MOEN_PASSWORD}

devices:
  my-device:
    description: my cool device
    provider: moen
    id: '1234567890'
```

**username:** _(required)_ Your Moen username.

**password:** _(required)_ Your Moen password.

### Fujitsu

```yaml
providers:
  fujitsu:
    username: ${env:FUJITSU_USERNAME}
    password: ${env:FUJITSU_PASSWORD}

devices:
  my-device:
    description: my cool device
    provider: fujitsu
    id: '1234567890'
```

**username:** _(required)_ Your Fujitsu username.

**password:** _(required)_ Your Fujitsu password.

### Noop

```yaml
devices:
  my-device:
    description: my cool device
    provider: noop
    id: '1234567890'
```

Unlike other providers, the `noop` provider does not need to be declared in the `providers` block.

## Devices

```yaml
devices:
  my-socket:
    description: bedroom window fans
    provider: tuya
    id: '123'
  my-bulb:
    description: living room lamp
    provider: tuya
    id: '456'
  my-sensor:
    description: basement radon detector
    provider: airthings
    id: '789'
```

**\<name\>:** _(required)_ Any string value, in the example above `my-socket`, `my-bulb`, and `my-sensor` are all device names.

**description:** _(optional)_ Any value, used to help identify a device and give it more context.

**provider:** _(required)_ One of the currently supported [providers](#providers).

**id:** _(required)_ The identifier for the device as given by its 3rd party API.

If provided, any further options are ignored.

## Automations

Automations represent logical groupings of triggers and actions.

```yaml
automations:
  summer:
    enabled: true
    components:
      - if:
          temp: '>78'
        then:
          turn-on: socket-A
        else:
          turn-off: socket-A
      - if:
          weekday: saturday,sunday
          sunset: -60
        then:
          turn-on: socket-B
```

**\<name\>:** _(required)_ Any string value, in the example above `summer` is the automation name.

**\<name\>.enabled:** _(optional)_ When true, the components in this automation will be run, otherwise they will be ignored.

**\<name\>.components:** _(optional)_ A list, each item can optionally include `if`, `then`, and `else` keys. The `if` is an object containing the triggers to run. When all triggers evaluate to true, the actions contained in the `then` object are run. If any of the triggers evaluate to false, the actions contained in the `else` object are run.

## Triggers

The top level triggers block contains configuration required for 3rd party APIs.

```yaml
triggers:
  location:
    latitude: 40.689
    longitude: -74.044
  timezone: 'America/New_York'
  aqi:
    api_key: ${env:AQI_API_KEY}
  weather:
    api_key: ${env:OPEN_WEATHER_API_KEY}
    data_cache_seconds: 20
```

**location.latitude** and **location.longitude:** _(optional)_ The physical location of your home. Required for determining weather, sunrise/sunset times, air quality, and timezone. Either `location` or `timezone` are required.

**timezone:** _(optional)_ The timezone of the physical location of your home using the [timezone identifier](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) from the IANA database. When not set, `location.longitude` and `location.latitude` values can be used to determine timezone. However doing so requires installing separate dependencies by running `pip install pydomotic[tz]`. These dependencies are not installed by default because they take up significant disk space. Either `location` or `timezone` are required.

**aqi.api_key:** _(optional)_ Your API key used to access https://docs.airnowapi.org. Required when using [AQI triggers](#aqi-trigger).

**weather.api_key:** _(optional)_ Your API key used to access https://openweathermap.org. Required when using [temperature triggers](#temperature-trigger).

### AQI Trigger

Fires when the outdoor air quality index matches a given value or range of values.

```yaml
automations:
  air-purifier:
    enabled: true
    components:
      - if:
          aqi: '>100'
        then:
          turn-on: switch-A
```

**aqi:** _(optional)_ Air quality index to match. Can be single value (ex: `100`), a relative value (ex: `>=50`), or a range of values (ex: `50-100`). Multiple values can be given separated by a comma (ex: `<50,100-150`).

### Time Trigger

Fires when the time matches the given value or range of values.

```yaml
automations:
  night-light:
    enabled: true
    components:
      - if:
          time: 6:00pm
        then:
          turn-on: switch-A
```

**time:** _(optional)_ Time value to match, in the form of `HH:MMpm`. Can be a single value (ex: `5:00am`) or a range of values (ex: `9:00pm-11:00pm`). Multiple values can be given separated by a comma (ex: `4:00am,5:00am,6:30pm`).

### Weekday Trigger

Fires when the day of the week matches the given value or range of values.

```yaml
automations:
  party-time:
    enabled: true
    components:
      - if:
          weekday: Friday
          time: 6:00pm
        then:
          turn-on: stereo
```

**weekday:** _(optional)_ The day of the week value to match. Case insensitive and abreviations supported. Can be a single value (ex: `Monday`) or a range of values (ex: `mon-fri`). Multiple values can be given separated by a comma (ex: `mon,wed,fri`).

### Date Trigger

Fires when the current date (year, month, day) matches the given value.

```yaml
automations:
  vacation:
    enabled: true
    components:
      - if:
          date: 2020-03-20
          time: 12:00pm
        then:
          switch: lightbulb-B
```

**date:** _(optional)_ The date value to match, in the form of `YYYY-MM-DD`. Multiple values can be given separated by a comma (ex: `2022-01-15,2022-02-15`).

### Cron Trigger

Fires when the given [cron expression](https://en.wikipedia.org/wiki/Cron) matches the current date/time.

```yaml
automations:
  fans:
    enabled: true
    components:
      - if:
          cron: '*/15 * * * *'
        then:
          turn-on: socket-A
```

**cron:** _(optional)_ Cron expression to match the current date/time. Several [predefined shortcuts](https://pypi.org/project/croniter/#keyword-expressions) are supported like `@hourly`, `@daily`, `@weekly`, and `@monthly`.

### Random Trigger

Fires randomly under the given probability.

```yaml
automations:
  vacation:
    enabled: true
    components:
      - if:
          random: 0.25
        then:
          turn-on: socket-A
        else:
          turn-off: socket-A
```

**random:** _(optional)_ The probability between 0 and 1 under which the trigger should fire. The greater the value, the greater the chance the trigger will fire. When `0` the trigger will never fire, when `1` the trigger will always fire, and when `0.5` the trigger will fire one half of the time.

### Sunrise/Sunset Trigger

Fires relative to sunrise/sunset time at the current location.

```yaml
automations:
  wake-up:
    enabled: true
    components:
      - if:
          weekday: mon-fri
          sunrise: 60
        then:
          turn-on: radio
```

**sunrise** or **sunset:** _(optional)_ Time relative to sunrise/sunset to match. When a positive integer (ex: `90`) will fire that many minutes after sunrise/sunset. When a negative integer (ex: `-120`) will fire that many minutes before sunrise/sunset. Can be a single value or a range of values (ex: `45-90`). Multiple values can be given separated by a comma (ex: `-15,80`).

### Temperature Trigger

Fires when the outdoor temperature matches the given value or range of values.

```yaml
automations:
  air-conditioner:
    enabled: true
    components:
      - if:
          temp: '>75'
        then:
          turn-on: switch-A
```

**temp:** _(optional)_ Outdoor temperature value to match. Can be single value (ex: `100`), a relative value (ex: `>=50`), or a range of values (ex: `50-100`). Multiple values can be given separated by a comma (ex: `<50,90-105`).

### Radon Trigger

Fires when the radon detection level matches the given value or range of values. Only supported as part of a [device trigger](#device-sensor-trigger).

```yaml
devices:
  radon-sensor:
    description: radon sensor crawlspace
    provider: airthings
    id: '1234567890'

automations:
  air-purifier:
    enabled: true
    components:
      - if:
          radon-sensor:
            radon: '>4'
        then:
          turn-on: switch-A
```

**\<name\>.radon:** _(required)_ Radon level to match in pCi/L. Can be single value (ex: `100`), a relative value (ex: `>=50`), or a range of values (ex: `50-100`). Multiple values can be given separated by a comma (ex: `<50,100-150`).

### Webhook Trigger

Fires when the request path matches the given value. Currently only supported in `LambdaHandler`s. Used to remotely trigger an action based on an external event.

```yaml
automations:
  releases:
    enabled: true
    components:
      - if:
          webhook: /new-release
        then:
          turn-on: party-lights
```

**webhook:** _(optional)_ Request path to match. Path must match exactly and the request must be a `POST` in order to fire.

### Device (Sensor) Trigger

Fires when the result returned by a sensor matches the given value.

```yaml
devices:
  thermometer:
    description: temperature sensor bedroom
    provider: tuya
    id: '1234567890'

automations:
  heatlamp:
    enabled: true
    components:
      - if:
          thermometer:
            temp: '<60'
        then:
          turn-on: 'socket-A'
```

**\<name\>:** _(optional)_ The name of the device from which to take the reading.

**\<name\>.\<value\>:** _(required)_ Any of the available triggers as defined above, most commonly `temp` and `radon`.

## Actions

Depending on the device and its provider, the following actions are available.

### Turn On/Off Action

Turns on/off the given device.

```yaml
automations:
  bedroom:
    enabled: true
    components:
      - if:
          time: 10:00am-12:00pm
        then:
          turn-on: 'socket-A'
        else:
          turn-off: 'socket-A'
```

**turn-on** and **turn-off:** _(optional)_ Matches device name as defined in the [devices](#devices) section.

### Switch Action

Switches the state of the given device.

```yaml
automations:
  vacation:
    enabled: true
    components:
      - if:
          random: 0.10
        then:
          switch: 'socket-A'
```

**switch:** _(optional)_ Matches device name as defined in the [devices](#devices) section.

### Set Mode Action

Sets the current mode for a Flo by Moen device.

```yaml
devices:
  flo:
    description: Flo by Moen
    provider: moen
    id: '1234567890'

automations:
  vacation:
    enabled: true
    components:
      - if:
          date: 2020-03-20
          time: 7:00am
        then:
          set-mode:
            device: flo
            mode: sleep
            revert-min: 60
            revert-mode: away
```

**set-mode.device:** _(required)_ Name of the device whose mode to change.

**set-mode.mode:** _(required)_ The mode to change to, one of `home`, `away`, or `sleep`.

**set-mode.revert-min:** _(optional)_ When changing to `sleep` mode, minutes to wait before automatically reverting mode. Defaults to 480 minutes (8 hours).

**set-mode.revert-mode:** _(optional)_ When changing to `sleep` mode, mode to revert to after completion of the sleep, one of `home` or `away`. Defaults to `home`.

### Execute Code Action

Lazy loads and executes the given Python method.

```yaml
devices:
  radon-sensor:
    description: basement radon
    provider: airthings
    id: '1234567890'

automations:
  radon-alert:
    enabled: true
    components:
      - if:
          radon-sensor:
            radon: '>4'
        then:
          exec: custom_actions.send_email
```

**exec:** _(optional)_ The module and method name to execute in the form of `module.method`. Multiple values can be given separated by a comma (ex: `custom_actions.turn_on,custom_actions.send_email`). Method must accept just one argument, the `context` object which holds references to all configured sensors and devices. For example:

```python
# custom_actions.py

import boto3
client = boto3.client('ses')

def send_email(context):
    radon = context.devices['radon-sensor'].current_radon()
    client.send_email(
        Source='me@email.com',
        Destination={
            'ToAddresses': ['you@email.com'],
        },
        Message={
            'Subject': {'Data': 'Radon levels too high!'},
            'Body': {
                'Text': {'Data': f'The current radon level is {radon}.'},
            },
        },
    )
```
