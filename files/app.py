#####################################################
# RGB Controller                                    #
# Author: Atomicbeast101                            #
# URL: gitlab.com/atomicbeast101/rpi_rgb_controller #
# Main program                                      #
#####################################################

# https://github.com/dordnung/raspberrypi-ledstrip/blob/master/fading.py

# Imports
import configparser
import threading
import hashlib
import pigpio
import flask
import time

# Attributes
rgb_manager = None
TOKEN_ID = None
app = flask.Flask(__name__)

# Class
class RGBManager(threading.Thread):
    def __init__(self, _config, _red, _green, _blue, _brightness, _red_pin, _green_pin, _blue_pin):
        self.config = _config
        self.red = _red
        self.blue = _blue
        self.green = _green
        self.brightness = _brightness
        self.red_pin = _red_pin
        self.green_pin = _green_pin
        self.blue_pin = _blue_pin

        self.on = False
        self.cur_setup = self._create_hash()
        self.pi_board = pigpio.pi()

        threading.Thread.__init__(self)

    def _create_hash(self):
        return hashlib.sha256('{}_{}:{}:{}-{}'.format(self.on, self.red, self.green, self.blue, self.brightness).encode())

    def _save_changes(self):
        with open('/opt/rgb_controller/config.ini', 'w') as configfile:
            self.config.write(configfile)

    def activate(self):
        self.on = True

    def deactivate(self):
        self.on = False

    def set_colors(self, _red, _green, _blue):
        self.red = _red
        self.green = _green
        self.blue = _blue
        
        self.config.set('Current', 'Red', str(self.red))
        self.config.set('Current', 'Green', str(self.green))
        self.config.set('Current', 'Blue', str(self.blue))
        self._save_changes()

    def set_brightness(self, _brightness):
        self.brightness = _brightness

        self.config.set('Current', 'Brightness', str(self.brightness))
        self._save_changes()

    def run(self):
        while True:
            red_level = 0
            green_level = 0
            blue_level = 0
            if self.on:
                red_level = int(int(self.red) * (float(self.brightness) / 255.0))
                green_level = int(int(self.green) * (float(self.brightness) / 255.0))
                blue_level = int(int(self.blue) * (float(self.brightness) / 255.0))

            new_hash = self._create_hash()
            if new_hash != self.cur_setup:
                self.cur_setup = new_hash

                # Set red
                self.pi_board.set_PWM_dutycycle(self.red_pin, red_level)

                # Set green
                self.pi_board.set_PWM_dutycycle(self.green_pin, green_level)

                # Set blue
                self.pi_board.set_PWM_dutycycle(self.blue_pin, blue_level)

            # Sleep
            time.sleep(1)

# Functions
def load_config():
    global TOKEN_ID, rgb_manager
    
    config = configparser.ConfigParser()
    try:
        config.read('/opt/rgb_controller/config.ini')
        TOKEN_ID = config.get('General', 'TokenID')
        cur_red = config.getint('Current', 'Red')
        cur_green = config.getint('Current', 'Green')
        cur_blue = config.getint('Current', 'Blue')
        cur_brightness = config.getint('Current', 'Brightness')
        r_pin_1 = config.getint('RGBPin', 'Red')
        g_pin_1 = config.getint('RGBPin', 'Green')
        b_pin_1 = config.getint('RGBPin', 'Blue')

        rgb_manager = RGBManager(config, cur_red, cur_green, cur_blue, cur_brightness, r_pin_1, g_pin_1, b_pin_1)
    except configparser.Error as err:
        print('ERROR: Error while trying to retrieve config values! Reason:\n{}'.format(str(err)))

# Flask
@app.route('/rgb/api/toggle', methods=['POST'])
def toggle():
    global rgb_manager
    
    data = flask.request.args
    if 'token' and 'activate' in data:
        if data['token'] == TOKEN_ID:
            if data['activate'] == "on":
                rgb_manager.activate()
                print('INFO: RGB lights has been activiated!', flush=True)
                return flask.jsonify({
                    'status': 'success'
                })
            elif data['activate'] == "off":
                rgb_manager.deactivate()
                print('INFO: RGB lights has been deactivated!', flush=True)
                return flask.jsonify({
                    'status': 'success'
                })
            return flask.jsonify({
                'status': 'error',
                'reason': 'Invalid value for activate!'
            })
        return flask.jsonify({
            'status': 'error',
            'reason': 'Invalid token!'
        })
    return flask.jsonify({
        'status': 'error',
        'reason': 'token and/or activate values are missing!'
    })

@app.route('/rgb/api/set_color', methods=['POST'])
def set_color():
    global rgb_manager

    data = flask.request.args
    if 'token' and 'red' and 'green' and 'blue' in data:
        if data['token'] == TOKEN_ID:
            try:
                red, green, blue = float(data['red']), float(data['green']), float(data['blue'])
                if 0.0 <= red <= 255.0 and 0.0 <= green <= 255.0 and 0.0 <= blue <= 255.0:
                    rgb_manager.set_colors(red, green, blue)
                    print('INFO: Colors has been set to red={}, green={} and blue={}'.format(red, green, blue), flush=True)
                    return flask.jsonify({
                        'status': 'success'
                    })
                return flask.jsonify({
                    'status': 'error',
                    'reason': 'red/green/blue values must be between 0.0 and 255.0!'
                })
            except Exception:
                return flask.jsonify({
                    'status': 'error',
                    'reason': 'red/green/blue must be float values!'
                })
        return flask.jsonify({
            'status': 'error',
            'reason': 'Invalid token!'
        })
    return flask.jsonify({
        'status': 'error',
        'reason': 'token, red, green, and/or blue values are missing!'
    })

@app.route('/rgb/api/set_brightness', methods=['POST'])
def set_brightness():
    global rgb_manager
    
    data = flask.request.args
    if 'token' and 'brightness' in data:
        if data['token'] == TOKEN_ID:
            try:
                brightness = int(data['brightness'])
                if 0 <= brightness <= 255:
                    rgb_manager.set_brightness(brightness)
                    print('INFO: Brightness has been set to {}!'.format(brightness), flush=True)
                    return flask.jsonify({
                        'status': 'success'
                    })
                return flask.jsonify({
                    'status': 'error',
                    'reason': 'brightness value must be between 0 and 255.'
                })
            except Exception:
                return flask.jsonify({
                    'status': 'error',
                    'reason': 'brightness must be integer value!'
                })
        return flask.jsonify({
            'status': 'error',
            'reason': 'Invalid token!'
        })
    return flask.jsonify({
        'status': 'error',
        'reason': 'token and/or brightness values are missing!'
    })

# Main
if __name__ == '__main__':
    print('INFO: Loading API...')
    
    print('INFO: Loading configuration...')
    load_config()
    print('INFO: Configuration loaded!')

    print('INFO: Starting RGB system...')
    rgb_manager.start()
    print('INFO: RGB system activated!')

    print('INFO: Starting flask...')
    app.run(host='0.0.0.0', port=5000)
