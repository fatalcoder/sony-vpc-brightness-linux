#!/usr/bin/python
# -*- encoding: utf-8 -*-

# Author: Ricardo Dani
# github.com/ricardodani
# ricardodani@gmail.com

"""
Class to change brightness in Sony VPC Series notebook`s in Linux.

    >>> b = Brightness()
    >>> b.set_max() # set the brightness to 100%
    >>> b.set_min() # set the brightness to 10%
    >>> b.set_up() # plus the brigthness to 15% (5% step)
    >>> b.set(99) # plus the brigthness to 99%
    >>> b.set_up() # not possible change to 104%
    Wrong percentage. Must be > 10% and < 100%.
    >>> b.set_down() # set the brightness to 99%
    >>> b.set(10) # set the brightness to 10%
    >>> b.set_down() # not possible change to 5%
    Wrong percentage. Must be > 10% and < 100%.
    >>> type(b.max_bright) == type(1)
    True
    >>> b.set(90, True)
    Changed brightness level to: 90%.
    >>> '%.1f' % b.actual_bright_ratio # get the actual brightness percentage
    '0.9'
    >>>
"""

import sys
import commands

_COMMANDS = {
    'max': 'cat /sys/class/backlight/intel_backlight/max_brightness',
    'change': 'echo %d| tee /sys/class/backlight/intel_backlight/brightness',
    'actual': 'cat /sys/class/backlight/intel_backlight/brightness',
    'username': 'whoami'
}
_MIN_BRIGHT_RATIO = 0.1
_STEP = 0.05


class Brightness:
    """
    Manipulates the brightness of SONY VPC Series notebook`s display.
    """

    def __init__(self):
        self._output = []
        self._max = self._get_max_bright()
        self._min = self._get_min_bright()

    def _get_last_output(self):
        return self._output[-1]

    def _get_max_bright(self):
        return int(self._execute_command(_COMMANDS['max']))

    def _get_min_bright(self):
        return int(self._max * _MIN_BRIGHT_RATIO)

    def _get_current_bright(self):
        return int(self._execute_command(_COMMANDS['actual']))

    def _execute_command(self, command):
        self._output.append(commands.getoutput(command))
        return self._get_last_output()

    @property
    def max_bright(self):
        return self._max

    @property
    def min_bright(self):
        return self._min

    @property
    def history(self):
        return '\n'.join(self._output[::-1])

    @property
    def actual_bright(self):
        return self._get_current_bright()

    @property
    def actual_bright_ratio(self):
        return round(self._get_current_bright() / float(self._max), 2)

    @property
    def actual_bright_ratio_string(self):
        return (self.actual_bright_ratio * 100).__str__()

    def set_up(self):
        new_value = int(100 * (self.actual_bright_ratio + _STEP))
        self.set(new_value)

    def set_down(self):
        new_value = int(100 * (self.actual_bright_ratio - _STEP))
        self.set(new_value)

    def set_min(self):
        self.set(int(100 * _MIN_BRIGHT_RATIO))

    def set_max(self):
        self.set(100)

    def set(self, percent, verbose=False):
        min_bright = 100 * _MIN_BRIGHT_RATIO
        if min_bright <= percent <= 100:
            bright = int(self._max * (percent/100.))
            self._execute_command(_COMMANDS['change'] % bright)
            if verbose:
                print 'Changed brightness level to: %d%%.' % percent
        else:
            if percent > 100:
                self.set(100)
            elif percent < min_bright:
                self.set(min_bright)
            print 'Wrong percentage. Must be > %d%% and < 100%%.' % min_bright

    def is_privileged(self):
        return self._execute_command(_COMMANDS['username']) == 'root'


if __name__ == '__main__':
    b = Brightness()

    if len(sys.argv) == 1:
        sys.argv = (sys.argv, 'actual')

    option = sys.argv[1]

    if option not in ('actual', 'help'):
        if not b.is_privileged():
            print 'Run script as root!'
        else:
            if option == 'up':
                b.set_up()
            elif option == 'down':
                b.set_down()
            elif option == 'min':
                b.set_min()
            elif option == 'max':
                b.set_max()
            else:
                b.set(int(option))
    else:
        if option == 'actual':
            print 'Actual brightness level is: %d%%' % b.actual_bright_ratio_string
        else:
            print (
                "bright.py - Usage\n\n"
                "\t<value> : set a numerical percentage brightness value\n"
                "\tup : set brightness up\n"
                "\tdown : set brightness down\n"
                "\tmin : set minimum brightness\n"
                "\tmax : set maximum brightness\n"
                "\tactual : view the actual brightness value\n"
                "\thelp : claim for help\n"
            )