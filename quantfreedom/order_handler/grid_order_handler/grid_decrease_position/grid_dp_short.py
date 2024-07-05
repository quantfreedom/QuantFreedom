from typing import NamedTuple


class GridDPExecShort(NamedTuple):
    short_pnl_exec: str = "pnl = round((self.average_entry - exit_price) * self.position_size_asset, 2)"
