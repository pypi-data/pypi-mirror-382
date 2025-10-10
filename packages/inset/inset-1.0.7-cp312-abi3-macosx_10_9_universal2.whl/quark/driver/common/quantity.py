# MIT License

# Copyright (c) 2021 YL Feng

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


from copy import deepcopy


class Quantity(object):
    """Quantity is used to describe the attributes of a driver
    """

    def __init__(self, name: str, value=None, ch: int = 0, unit: str = ''):
        self.name: str = name
        self.default: dict = dict(value=value,
                                  unit=unit,
                                  ch='global' if not ch else ch)

    def __repr__(self):
        return f'Quantity({self.name})'


def newcfg(quantlist: list[Quantity] = [], CHs: list[int | str] = []) -> dict:
    '''generate a new config'''
    config = {}
    for q in deepcopy(quantlist):
        _cfg = {}
        _default = dict(value=q.default['value'], unit=q.default['unit'])
        for i in CHs:
            _cfg.update({i: deepcopy(_default)})
        if q.default['ch'] == 'global':
            _cfg.update({'global': deepcopy(_default)})
        config.update({q.name: _cfg})
    return config
