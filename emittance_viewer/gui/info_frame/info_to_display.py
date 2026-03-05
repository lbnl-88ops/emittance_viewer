from .csd_info import CSDInfoRow

_FRAMES = ["Vacuum", "Superconductors", "High voltage", "Glaser", "High temp oven"]
_COLUMNS = [["(torr)"], ["(A)"], ["(V)", "(mA)"], ["(A)"], []]
_INFO_ROWS = [
    [
        CSDInfoRow(s, ".1e", l)
        for s, l in [
            ("inj_mbar", "Injection"),
            ("ext_mbar", "Extraction"),
            ("bl_mig2_torr", "Beam line"),
        ]
    ],
    [CSDInfoRow(s, "6.2f") for s in ["inj_i", "ext_i", "mid_i", "sext_i"]],
    [
        CSDInfoRow(s, [".2f", ".3e"], l)
        for s, l in [
            (["extraction_v", "extraction_i"], "Extraction"),
            (["puller_v", "puller_i"], "Puller"),
            (["bias_v", "bias_i"], "Biased disk"),
        ]
    ],
    [CSDInfoRow("glaser_1", ".1f")],
    [
        CSDInfoRow(s, "6.2f", l)
        for s, l in [
            ("ht_oven_i", "Current (A)"),
            ("ht_oven_v", "Voltage (V)"),
            ("ht_oven_w", "Power (W)"),
        ]
    ],
]
