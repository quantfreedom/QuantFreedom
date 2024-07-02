from typing import NamedTuple


class GridDPExecLong(NamedTuple):
    pnl_exec: str = "pnl = round((exit_price - self.average_entry) * self.position_size_asset, 2)"
