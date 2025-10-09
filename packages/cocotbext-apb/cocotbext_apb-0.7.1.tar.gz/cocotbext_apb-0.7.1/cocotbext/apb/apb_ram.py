"""

Copyright (c) 2024-2025 Daxzio

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

from .apb_slave import ApbSlave
from .memory import Memory


class ApbRam(ApbSlave, Memory):
    def __init__(
        self,
        bus,
        clock,
        reset=None,
        reset_active_level=True,
        size=2**32,
        mem=None,
        **kwargs
    ):
        Memory.__init__(self, size, mem, **kwargs)
        ApbSlave.__init__(self, bus, clock, **kwargs)

    async def _write(self, address, data, strb=None, prot=None):
        self.check_permission(address, prot)
        if strb is None:
            self.write((address % self.size), data)
        else:
            for i in range(self.byte_lanes):
                if 1 == ((int(strb.value) >> i) & 0x1):
                    self.write_byte((address % self.size) + i, data[i])

    async def _read(self, address, length, prot=None):
        self.check_permission(address, prot)
        return self.read(address % self.size, length)
