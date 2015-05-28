# cloudflare-ip-config

This is a script for maintaining config files that need to contain [CloudFlare's latest IP ranges](https://www.cloudflare.com/ips), e.g. firewall rules or web server config files. It is designed to be run on a cronjob to ensure any new ranges CloudFlare use are automatically included.

## Usage

Pass the path(s) to the config file(s) on the command line:

```
python update.py config.json
python update.py config1.json config2.json config3.json
python update.py /etc/cf/*.json
```
etc

## Config file format

- JSON
- Each config file contains either a JSON object or an array of JSON objects
- The objects require two members:
 - `template`, the path to a mustache template file
 - `destination`, the path the output file should be saved to
- There are two more optional members:
 - `before`, a command to run before the new config file is written
 - `after`, a command to run after the new config file is written
 - e.g. `"after": ["service", "nginx", "reload"]`

## Template file format

- [mustache](https://mustache.github.io/)
- Use `{{#ranges4}} ... {{/ranges4}}` to loop over the IP ranges
- Inside, you can use these tags:
 - `{{cidr}}`, e.g. `1.2.3.4/24`
 - `{{ip}}`, e.g. `1.2.3.4`
 - `{{prefix}}` e.g. `24`
 - `{{mask}}` e.g. `255.255.255.0`

## TODO

- IPv6 support