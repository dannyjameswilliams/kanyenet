import numpy as np
import seaborn as sns

# album ordering 
album_order = ["The College Dropout", "Late Registration", "Graduation", "808s & Heartbreak", "My Beautiful Dark Twisted Fantasy", "Watch the Throne", "Yeezus", "The Life of Pablo", "ye", "Kids See Ghosts", "Jesus is King"]

# album colours
colours = np.char.upper(["#ab5918", "#311505", "#c74ac7", "#d1dad9", "#ce1d34", "#a6894e", "#caccd5", "#f58c57", "#1c2b48", "#e4554a", "#001da3"])
sns.set_palette(sns.color_palette(colours))
sns.set(style="whitegrid")

cd_cols = np.char.upper(["#cb7e2b", "#3c0f13", "#8f3c1d", "#682012", "#eee1d0", "#9796ae", "#6c6a99", "#635561", "#10090f", "#493e60"])
lr_cols = np.char.upper(["#bec2b9", "#674b33", "#7f95a0", "#0b0605", "#3d2311", "#414c46", "#56768a", "#26281d", "#965631", "#173648"])
g_cols = np.char.upper(["#322447", "#e4dcbe", "#bc3a52", "#713560", "#cc478b", "#b48e5f", "#2796c5", "#ea534a", "#ad98b3", "#a13218"])
eoe_cols = np.char.upper(["#ccdcdc", "#e31905", "#d77550", "#3c0404", "#cc8d7d", "#b7b3ae", "#f5bcb3", "#c9a998", "#a1aaac", "#8c949c"])
mbdtf_cols = np.char.upper(["#ed203f", "#146d54", "#e0af70", "#39bda6", "#da8049", "#897e58", "#fa3454", "#a78c84", "#bc3b2a", "#d54139"])
wtt_cols = np.char.upper(["#a48756", "#f0e2c3", "#e9d1a3", "#e1bc88", "#cab894", "#caaf7c", "#62451a", "#785e32", "#755622", "#63542e"])
yz_cols = np.char.upper(["#282c34", "#f22927", "#d6dbdc", "#1ccfc0", "#80bbc3", "#ba9251", "#a5c1c9", "#d6c089", "#d28e80", "#b9b3bc"])
tlop_cols = np.char.upper(["#ee8a56", "#472723", "#e1d9bf", "#965e3c", "#c9ac93", "#83381d", "#59c6b9", "#efd09b", "#b65a32", "#bc642c"])
ye_cols = np.char.upper(["#c6c6c4", "#122231", "#536b8b", "#7a8ba5", "#69af9a", "#263e5e", "#237a54", "#948c92", "#1c4e47", "#585a66"])
ksg_cols = np.char.upper(["#d58e78", "#3983a1", "#739da8", "#9fced6", "#a13945", "#c46b3e", "#93a4a7", "#c25b57", "#cfd2aa", "#4cc4ec"])
jik_cols = np.char.upper(["#0423af", "#9d9674", "#043cdf", "#0431cd", "#053ccf", "#51589c", "#0e228a", "#6b7491", "#314cba", "#414974"])
all_album_cols = np.array([cd_cols, lr_cols, g_cols, eoe_cols, mbdtf_cols, wtt_cols, yz_cols, tlop_cols, ye_cols, ksg_cols, jik_cols])