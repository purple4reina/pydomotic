# CHANGELOG

## 1.4.1
### Bug Fixes
+ Fix issue where devices aliases were not being recognized when parsing
  components yaml.

## 1.4.0
### Features
+ Add support for device aliases. This allows you to use a custom name to
  represent a group of devices. For example, the two components below are
  equivalent.
    ```yaml
    aliases:
      lights:
        - light-A
        - light-B
        - light-C

    automations:
      explicit:
        enabled: true
        components:
          - if:
              time: 12:00pm
            then:
              turn-on: light-A, light-B, light-C
          - if:
              time: 12:00pm
            then:
              turn-on: lights
    ```

## 1.3.1
### Bug Fixes
+ Add missing time import for ecobee providers.

## 1.3.0
### Features
+ Add support for Ecobee providers.

## 1.2.0
### Features
+ Add optional timeout to all Airthings API calls.

## 1.1.0
### Features
+ Add optional timeout to all Tuya API calls.

## 1.0.0
Initial release :tada:
