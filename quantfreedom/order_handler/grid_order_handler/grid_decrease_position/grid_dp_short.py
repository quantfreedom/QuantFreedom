from typing import NamedTuple


class GridDPExecShort(NamedTuple):
    pnl_exec: str = "pnl = round((self.average_entry - exit_price) * self.position_size_asset, 2)"
