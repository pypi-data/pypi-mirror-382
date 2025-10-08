# Example
This directory contains an example of how to use Toucan with WhatsApp.

## Requirements
These are requirements specific for this example, in addition to the general requirements as described in the
[Toucan README](../README.md#additional-requirements).

### Python
Install both the main requirements and the example-specific requirements:

```bash
pip install pdm
pdm install --group examples --group test
```

### SQLite 3
```bash
sudo apt install sqlite3
```

#### Register WhatsApp on the emulators
Install WhatsApp on your emulators and register it with a phone number. In the example, the app is only opened and no 
additional actions are performed because we know the database change is triggered by just opening the app. That is why
prepopulating the database by executing user actions such as sending a message is not necessary in this case. Note that
usually this is required.

### Appium
In the example, a user action (opening WhatsApp) is executed on the device. The example uses [Puma](https://github.com/NetherlandsForensicInstitute/puma),
which uses Appium to execute actions on the device. Appium needs to be installed through NPM. If you do not have
NPM, install it:

```bash
# installs nvm (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
# download and install Node.js (you may need to restart the terminal)
nvm install 20
# verifies the right Node.js version is in the environment
node -v # should print e.g. `v20.18.0`
# verifies the right npm version is in the environment
npm -v # should print e.g. `10.8.2`
```

After NPM is installed, we can install Appium:

```bash
npm install --location=global appium
```

Install the Uiautomator2 driver
```bash
appium driver install uiautomator2
```
You can now run `appium` from the command line.

## Troubleshooting
### Installing Appium with NPM fails
If you are behind a proxy and the Appium install hangs, make sure to configure your `~/.npmrc` with the following
settings.
Fill in the values, restart terminal and try again:

```text
registry=<your organization registry>
proxy=<organization proxy>
https-proxy=<organization proxy>
http-proxy=<organization proxy>
```
