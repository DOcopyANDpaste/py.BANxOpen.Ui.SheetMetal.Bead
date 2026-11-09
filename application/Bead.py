# The file NX runs (Alt+F8, or a ribbon button). No logic: everything is in banxopen.ui_bead.
from banxopen.foundation.nx.dev import purge_banxopen_modules

purge_banxopen_modules()  # no-op unless BANXOPEN_DEV=1
from banxopen.ui_bead.entry import GetUnloadOption, main

if __name__ == "__main__":
    main()
