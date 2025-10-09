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
import math

from cocotb import start_soon
from cocotb.triggers import RisingEdge

from collections import deque
from cocotb.triggers import Event
from typing import Deque
from typing import Tuple
from typing import Any
from typing import Union

from .apb_base import ApbBase
from .constants import ApbProt
from .utils import resolve_x_int


class ApbMaster(ApbBase):
    def __init__(self, bus, clock, **kwargs) -> None:
        super().__init__(bus, clock, name="master", **kwargs)

        self.queue_tx: Deque[Tuple[bool, int, bytes, int, ApbProt, bool, int]] = deque()
        self.queue_rx: Deque[Tuple[bytes, int]] = deque()
        self.tx_id = 0

        self.sync = Event()

        self._idle = Event()
        self._idle.set()

        if self.penable_present:
            self.bus.penable.value = 0
        self.bus.psel.value = 0
        self.bus.paddr.value = 0
        if self.pstrb_present:
            self.bus.pstrb.value = 0
        if self.pprot_present:
            self.bus.pprot.value = 0
        self.bus.pwrite.value = 0
        self.bus.pwdata.value = 0

        #         self._init_reset(reset, reset_active_level)

        self._run_coroutine_obj: Any = None
        self._restart()

    def calc_length(self, length, data):
        if -1 == length:
            length = self.wbytes
        if not 0 == length % self.wbytes:
            raise Exception(
                f"Length needs to be a multiple of the byte width: {length}%{self.wbytes}"
            )
        if isinstance(data, int):
            min_length = math.ceil(data.bit_length() / self.wwidth)
        else:
            min_length = math.ceil(len(data) / self.wwidth)
        length = max(int(length / self.wbytes), min_length)
        return length

    async def write(
        self,
        addr: int,
        data: Union[int, bytes],
        strb: int = -1,
        prot: ApbProt = ApbProt.NONSECURE,
        error_expected: bool = False,
        length: int = -1,
    ) -> None:
        self.write_nowait(addr, data, strb, prot, error_expected, length)
        await self._idle.wait()

    def write_nowait(
        self,
        addr: int,
        data: Union[int, bytes],
        strb: int = -1,
        prot: ApbProt = ApbProt.NONSECURE,
        error_expected: bool = False,
        length: int = -1,
    ) -> None:
        """ """
        self.loop = self.calc_length(length, data)

        self._idle.clear()
        for i in range(self.loop):
            addrb = addr + i * self.wbytes
            if isinstance(data, int):
                subdata = (data >> self.wwidth * i) & self.wdata_mask
                datab = subdata.to_bytes(self.wbytes, "little")
            else:
                datab = data[i * self.wbytes : (i + 1) * self.wbytes]
            self.tx_id += 1
            self.queue_tx.append(
                (True, addrb, datab, strb, prot, error_expected, self.tx_id)
            )
        self.sync.set()

    async def read(
        self,
        addr: int,
        data: Union[int, bytes] = bytes(),
        prot: ApbProt = ApbProt.NONSECURE,
        error_expected: bool = False,
        length: int = -1,
    ) -> bytes:
        rx_id = self.read_nowait(addr, data, prot, error_expected)
        found = False
        while not found:
            while self.queue_rx:
                ret, tx_id = self.queue_rx.popleft()
                if rx_id == tx_id:
                    found = True
                    break
            await RisingEdge(self.clock)
        await self._idle.wait()
        return ret

    def read_nowait(
        self,
        addr: int,
        data: Union[int, bytes] = bytes(),
        prot: ApbProt = ApbProt.NONSECURE,
        error_expected: bool = False,
        length: int = -1,
    ) -> int:
        self.loop = self.calc_length(length, data)
        self.sync.set()
        for i in range(self.loop):
            addrb = addr + i * self.rbytes
            if isinstance(data, int):
                subdata = (data >> self.rwidth * i) & self.rdata_mask
                datab = subdata.to_bytes(self.rbytes, "little")
            else:
                datab = data
            self.tx_id += 1
            self.queue_tx.append(
                (False, addrb, datab, -1, prot, error_expected, self.tx_id)
            )
        self._idle.clear()
        return self.tx_id

    def _restart(self) -> None:
        if self._run_coroutine_obj is not None:
            self._run_coroutine_obj.kill()
        self._run_coroutine_obj = start_soon(self._run())

    @property
    def count_tx(self) -> int:
        return len(self.queue_tx)

    @property
    def empty_tx(self) -> bool:
        return not self.queue_tx

    @property
    def count_rx(self) -> int:
        return len(self.queue_rx)

    @property
    def empty_rx(self) -> bool:
        return not self.queue_rx

    @property
    def idle(self) -> bool:
        return self.empty_tx and self.empty_rx

    def clear(self) -> None:
        """Clears the RX and TX queues"""
        self.queue_tx.clear()
        self.queue_rx.clear()

    async def wait(self) -> None:
        """Wait for idle"""
        await self._idle.wait()

    async def _run(self):
        await RisingEdge(self.clock)
        while True:
            while not self.queue_tx:
                self._idle.set()
                self.sync.clear()
                await self.sync.wait()

            (
                write,
                addr,
                data,
                strb,
                prot,
                error_expected,
                tx_id,
            ) = self.queue_tx.popleft()

            if addr < 0 or addr >= 2**self.address_width:
                raise ValueError("Address out of range")

            self.bus.psel.value = 1
            self.bus.paddr.value = addr
            if self.pprot_present:
                self.bus.pprot.value = prot
            if self.penable_present:
                self.bus.penable.value = 0
            if write:
                data = int.from_bytes(data, byteorder="little")
                self.log.info(
                    f"Write addr: 0x{addr:08x} data: 0x{data:08x} prot: {prot}"
                )
                self.bus.pwdata.value = data & self.wdata_mask
                self.bus.pwrite.value = 1
                if self.pstrb_present:
                    if -1 == strb:
                        self.bus.pstrb.value = self.strb_mask
                    else:
                        self.bus.pstrb.value = strb
            else:
                self.log.info(f"Read addr: 0x{addr:08x} prot: {prot}")
            await RisingEdge(self.clock)
            if self.penable_present:
                self.bus.penable.value = 1
                await RisingEdge(self.clock)

            while not self.bus.pready.value:
                await RisingEdge(self.clock)

            if self.pslverr_present and bool(self.bus.pslverr.value):
                msg = "PSLVERR detected!"
                if self.pprot_present:
                    msg += f" PPROT - {ApbProt(self.bus.pprot.value).name}"
                if error_expected:
                    self.log.info(msg)
                else:
                    self.log.critical(msg)
            if not write:
                ret = resolve_x_int(self.bus.prdata)
                self.log.info(f"Value read: 0x{ret:08x}")
                if not data == bytes():
                    data_int = int.from_bytes(data, byteorder="little")
                    if not data_int == ret:
                        raise Exception(
                            f"Expected 0x{data_int:08x} doesn't match returned 0x{ret:08x}"
                        )
                self.queue_rx.append((ret.to_bytes(self.rbytes, "little"), tx_id))

            if self.penable_present:
                self.bus.penable.value = 0
            self.bus.psel.value = 0
            self.bus.paddr.value = 0
            if self.pprot_present:
                self.bus.pprot.value = 0
            self.bus.pwrite.value = 0
            self.bus.pwdata.value = 0
            if self.pstrb_present:
                self.bus.pstrb.value = 0

            self.sync.set()
