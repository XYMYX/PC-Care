from PyInstaller.utils.hooks import collect_data_files

analysis = Analysis(
    ["main.py"],
    datas=collect_data_files("customtkinter") + [("assets/xymyx.ico", "assets")],
)
archive = PYZ(analysis.pure)
application = EXE(
    archive,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    name="XYMYX-PC-Care",
    icon="assets/xymyx.ico",
    console=False,
    uac_admin=False,
    upx=False,
)
