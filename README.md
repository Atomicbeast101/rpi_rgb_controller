# RGB Controller API Server
Ansible playbook to deploy RGB Controller API server to any Linux devices.

## Ansible Playbook
Before running playbook, please make sure `python3-pip` is installed and the following command is executed on the hosts as root:
`apt install build-essential unzip wget && wget http://abyz.me.uk/rpi/pigpio/pigpio.zip && unzip pigpio.zip && cd PIGPIO && make install`
Run playbook:
`ansible-playbook -i hosts -user root playbook.yml`

## API Documentation
### /rgb/api/toggle
Enable/Disable RGB lights
* `token` = Token ID
* `activate` = True/False

### /rgb/api/set_color
Set color of RGB lights (this does not auto enable the RGB lights if they are disabled)
* `token` = Token ID
* `red` = Integer value from 0.0 to 255.0
* `green` = Integer value from 0.0 to 255.0
* `blue` = Integer value from 0.0 to 255.0
Example: `http://host:5000?token=EXAMPLE&red=255&green=0&blue=0`

### /rgb/api/set_brightness
Set brightness of the RGB lights (this does not auto enable the RGB lights if they are disabled)
* `token` = Token ID
* `brightness` = Integer value from 0.0 to 255.0
Example: `http://host:5000?token=EXAMPLE&brightness=255.0`
