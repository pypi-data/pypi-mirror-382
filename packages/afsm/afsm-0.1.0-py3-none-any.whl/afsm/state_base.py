"""
SPDX-License-Identifier: LGPL-3.0-or-later
Copyright (C) 2025 Lappeenrannan-Lahden teknillinen yliopisto LUT
Author: Aleksei Romanenko <aleksei.romanenko@lut.fi>

Funded by the European Union and UKRI. Views and opinions expressed are however those of the author(s) 
only and do not necessarily reflect those of the European Union, CINEA or UKRI. Neither the European 
Union nor the granting authority can be held responsible for them.
"""
class StateBase:
    @property
    def on_enter(self):
        return str(self) + "_on_enter"

    @property
    def on_exit(self):
        return str(self) + "_on_exit"

    @property
    def on_loop(self):
        return str(self) + "_on_loop"
