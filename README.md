# pydomotic

A Python library for home automation execution, enabling seamless control and
management of your IoT devices.

_"Domotics": The automatic control of home appliances by electronic systems.
Contraction of domestic robotics, from the Latin domus ("home"), and robotics._

## Getting Started

Install `pydomotic` in your environment.

```bash
$ pip install pydomotic
```

Create your `pydomotic.yml `configuration file where you will define your
devices and automations.

```yaml
# pydomotic.yml

devices:
  fan:
    description: fan switch
    provider: noop
    id: '012'
  thermometer:
    description: temperature sensor
    provider: noop
    id: '345'

automations:
  fan:
    enabled: true
    components:
      - if:
          thermometer:
            temp: '>75'
        then:
          turn-on: fan
        else:
          turn-off: fan
```

Running will check each trigger and execute any actions.

```bash
$ python -m pydomotic
```

## Glossary

**trigger:** A small piece of code which evaluates to either true or false.
Usually it calls on devices or 3rd party APIs to make this determination.

**action:** A small piece of code which is run when a trigger fires. Usually
this is managing device state like turning a lightbulb on or off. When
configured, it can be designated as a "then" action or an "else" action.

**provider:** The third party which owns the API for a set of devices. The
manufacturer of a device will usually provide this API.

**device:** Any IoT device which can be controled with a 3rd party API managed
by a provider.

**sensor:** A device or 3rd party API which senses information about the
physical world around it. For example, a smart lightbulb or REST based current
weather API.

**component:** A grouping of triggers and actions. When all triggers evaluate
to true, its "then" actions will be run. When any trigger evaluates to false,
its "else" actions will be run.

**handler:** The code used to run a set of components. This is the main
entrypoint to the `pydomotic` system.

**parser:** The code used to read the configuration yaml and transform it into
a list of components.

## Configuration

### Location

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

### General

Configuration is grouped into four headings: [providers](#providers), [triggers](#triggers), [devices](#devices), and [automations](#automations).

Reading values from environment variables is available in the form of `${env:MY_ENV_VAR}`.

For a complete example configuration file, see [`tests/testdata/full.yml`](./tests/testdata/full.yml).

### Providers

Currently, four providers are provided out of the box.

+ [**Tuya:**](#tuya) A device that is supported by the Tuya platform. Many IoT manufacturers rely on Tuya for their device APIs, supported by the [`gosundpy`](https://github.com/purple4reina/gosundpy) Python package.
+ [**Airthings:**](#airthings) Any of the Airthings View devices.
+ [**Fujitsu:**](#fujitsu) Any Fujitsu WiFi enabled home heat pump system, supported by the [`pyfujitseu`](https://github.com/xerxes87/pyfujitseu) Python package.
+ [**Noop:**](#noop) A generic provider which can be assigned to any device, useful for testing.

Contributions and requests for further support are welcome.

#### Tuya

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

#### Airthings

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

#### Fujitsu

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

#### Noop

```yaml
devices:
  my-device:
    description: my cool device
    provider: noop
    id: '1234567890'
```

Unlike other providers, the `noop` provider does not need to be declared in the `providers` block.

### Devices

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

**name:** _(required)_ Any string value, in the example above `my-socket`, `my-bulb`, and `my-sensor` are all device names.

**description:** _(optional)_ Any value, used to help identify a device and give it more context.

**provider:** _(required)_ One of the currently supported [providers](#providers).

**id:** _(required)_ The identifier for the device as given by its 3rd party API.

If provided, any further options are ignored.

### Triggers

The top level triggers block contains configuration required for 3rd party APIs.

```yaml
triggers:
  location:
    latitude: 40.689
    longitude: -74.044
  timezone: 'America/Los_Angeles'
  aqi:
    api_key: ${env:AQI_API_KEY}
  weather:
    # https://openweathermap.org/
    api_key: ${env:OPEN_WEATHER_API_KEY}
    data_cache_seconds: 20
```

**location.latitude** and **location.longitude:** _(optional)_ The physical location of your home. Required for determining weather, sunrise/sunset times, air quality, and timezone.

**timezone:** _(optional)_ The timezone of the physical location of your home using the [timezone identifier](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) from the IANA database. When not set, longitude and latitude values are used to determine timezone which can add significant overhead to runtime.

**aqi.api_key:** _(optional)_ Your API key used to access https://docs.airnowapi.org. Required when using [AQI triggers](#aqi-trigger).

**weather.api_key:** _(optional)_ Your API key used to access https://openweathermap.org. Required when using [temperature triggers](#temperature-trigger).

#### AQI Trigger

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

**aqi:** _(required)_ Air quality index to match. Can be single value (ex: `100`), a relative value (ex: `>=50`), or a range of values (ex: `50-100`). Multiple values can be given separated by a comma (ex: `<50,100-150`).

#### Time Trigger

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

**time:** _(required)_ Time value to match, in the form of `HH:MMpm`. Can be a single value (ex: `5:00am`) or a range of values (ex: `9:00pm-11:00pm`). Multiple values can be given separated by a comma (ex: `4:00am,5:00am,6:30pm`).

#### Weekday Trigger

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

**weekday:** _(required)_ The day of the week value to match. Case insensitive and abreviations supported. Can be a single value (ex: `Monday`) or a range of values (ex: `mon-fri`). Multiple values can be given separated by a comma (ex: `mon,wed,fri`).

#### Cron Trigger

#### Random Trigger

#### Sunrise/Sunset Trigger

#### Temperature Trigger

#### Radon Trigger

#### Webhook Trigger

#### Device (Sensor) Trigger

### Automations