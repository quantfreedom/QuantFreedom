from typing import NamedTuple


class GridDPExec(NamedTuple):
    long_pnl_exec: str = "pnl = round((exit_price - self.average_entry) * self.position_size_asset, 2)"

    short_pnl_exec: str = "pnl = round((self.average_entry - exit_price) * self.position_size_asset, 2)"
    
Grid_DP_Exec_Tuple = GridDPExec()
