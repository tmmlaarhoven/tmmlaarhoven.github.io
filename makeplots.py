import numpy as np
import time
import json
import datetime
import os.path
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from pandas import read_csv

plt.style.use(['dark_background'])

plt.rcParams.update({
	"axes.facecolor": 		(0.2, 0.2, 0.2, 1.0),  # green with alpha = 50%
	"savefig.facecolor": 	(0.0, 0.0, 1.0, 0.0),  # blue  with alpha = 20%
	"figure.figsize": 		(3.5, 3.5),
	"axes.labelsize": 		12,
	"xtick.labelsize": 		9,
	"ytick.labelsize": 		9,
	"legend.labelspacing": 	0.3,
	"legend.handlelength": 	1.0,
	"legend.handletextpad": 0.3,
	"grid.color": 			(0.8, 0.8, 0.8),
	"grid.linestyle": 		":",
	"grid.linewidth": 		0.5,
	"legend.framealpha":	0.5,
	"font.family": 			['Roboto', 'serif'],
})

event = {
	"all": "All",
	"hourly": "Hourly",
	"2000": "<2000",
	"1700": "<1700",
	"1600": "<1600",
	"1500": "<1500",
	"1300": "<1300",
	"daily": "Daily",
	"weekly": "Weekly",
	"monthly": "Monthly",
	"yearly": "Yearly",
	"eastern": "Eastern",
	"elite": "Elite",
	"shield": "Shield",
	"titled": "Titled",
	"marathon": "Marathon"
}

variant = {
	"3check": "Three-check",
	"antichess": "Antichess",
	"atomic": "Atomic",
	"blitz": "Blitz",
	"bullet": "Bullet",
	"chess960": "Chess960",
	"classical": "Classical",
	"crazyhouse": "Crazyhouse",
	"horde": "Horde",
	"hyperbullet": "HyperBullet",
	"koth": "King of the Hill",
	"racingkings": "Racing Kings",
	"rapid": "Rapid",
	"superblitz": "SuperBlitz",
	"ultrabullet": "UltraBullet",
	"all": "All"
	}
	
variantcolors = {
	"3check": 		(204. / 255., 121. / 255., 167. / 255.),
	"antichess": 	(223. / 255.,  83. / 255.,  83. / 255.),
	"atomic": 		(102. / 255.,  85. / 255., 140. / 255.),
	"blitz": 		(  0. / 255., 114. / 255., 178. / 255.),
	"bullet": 		( 86. / 255., 180. / 255., 233. / 255.),
	"chess960": 	(230. / 255., 159. / 255.,   0. / 255.),
	"classical": 	( 69. / 255., 159. / 255.,  59. / 255.),
	"crazyhouse": 	( 86. / 255., 180. / 255., 233. / 255.),
	"horde": 		(153. / 255., 230. / 255., 153. / 255.),
	"hyperbullet": 	( 86. / 255., 180. / 255., 233. / 255.),
	"koth": 		(213. / 255.,  94. / 255.,   0. / 255.),
	"racingkings": 	(255. / 255., 174. / 255., 170. / 255.),
	"rapid": 		(  0. / 255., 158. / 255., 115. / 255.),
	"superblitz": 	(  0. / 255., 114. / 255., 178. / 255.),
	"ultrabullet": 	(  0. / 255., 158. / 255., 115. / 255.),
	"all": 			(200. / 255., 200. / 255., 200. / 255.),
	}
	
types = {
	"players": "Players",
	"games": "Games per player",
	"moves": "Moves per player per game",
	"topscore": "Highest score",
	"rating": "Average rating",
	"berserk": "Berserk rate",
	"results": "Results by color"
	}

def makeplot(va, ev, type):

	fpath = "E:\\lichess\\tournaments\\" + ev + "\\" + va + "\\"
	frpath = "E:\\lichess\\tournaments\\rankings\\"
	fwpath = "E:\\lichess\\tmmlaarhoven.github.io\\lichess\\rankings\\"
	
	if not os.path.exists(frpath + va + "\\" + ev + "\\" + va + "_" + ev + "_ranking.json") or not os.path.exists(fpath + ev + "_" + va + ".ndjson"):
		print(va + " - " + ev + " - " + type + " - Nothing to do.")
		return
	
	leg = []
	x = []
	y = []
	if type == "results":
		yW = []
		yD = []
		yB = []
	with open(fpath + ev + "_" + va + ".ndjson", "r") as tf:
		for line in tf:
			dictio = json.loads(line)
			x.append(datetime.datetime(int(dictio["start"][0:4]), int(dictio["start"][5:7]), int(dictio["start"][8:10]), int(dictio["start"][11:13]), int(dictio["start"][14:16]), int(dictio["start"][17:19])))
			if type == "players":
				y.append(dictio["players"])
			elif type == "games":
				y.append(dictio["games"] / max(1, dictio["players"]))
			elif type == "moves":
				y.append(dictio["moves"] / max(1, dictio["games"]) / 2)
			elif type == "topscore":
				y.append(dictio["topscore"])
			elif type == "rating":
				y.append(dictio["totrating"] / max(1, dictio["players"]))
			elif type == "berserk":
				y.append(100. * dictio["berserks"] / max(1, dictio["games"]) / 2.)	
			elif type == "results":
				yW.append(100. * dictio["wwins"] / max(1, dictio["games"]))
				yD.append(100. * (dictio["games"] - dictio["bwins"] - dictio["wwins"]) / max(1, dictio["games"]))
				yB.append(100. * dictio["bwins"] / max(1, dictio["games"]))
				
	if type != "results":
		# Scatter plot of data
		ptsize = min(20., max(0.3, 1000./len(x)))
		plt.scatter(x, y, s=[ptsize]*len(x), color=variantcolors[va])
		leg.append(event[ev] + " " + variant[va] + " (all)")
		# For big data sets, compute a moving average mean graph to plot as well	
		if len(x) > 1000:
			xM = []
			yM = []
			for i in range(50, len(x)-50):
				xM.append(x[i])
				yM.append(sum(y[i-50:i+50]) / 100.)
			ptsizeM = min(20., max(0.3, 1000./len(xM)))
			plt.scatter(xM, yM, s=[ptsizeM]*len(xM), color=(1, 1, 1))
			#plt.plot(xM, yM, color=(1, 1, 1))
			leg.append(event[ev] + " " + variant[va] + " (mean)")
		elif len(x) > 100:
			xM = []
			yM = []
			for i in range(5, len(x)-5):
				xM.append(x[i])
				yM.append(sum(y[i-5:i+5]) / 10.)
			ptsizeM = min(20., max(0.3, 1000./len(xM)))
			plt.scatter(xM, yM, s=[ptsizeM]*len(xM), color=(1, 1, 1))
			leg.append(event[ev] + " " + variant[va] + " (mean)")
		lgnd = plt.legend(leg, markerscale=3./ptsize, fontsize=9)
		for handle in lgnd.legendHandles:
			handle.set_sizes([6.0])
	else:
		# Stacked plot of white wins, draws, losses
		ptsize = min(20., max(0.3, 1000./len(x)))
		plt.stackplot(x, yW, yD, yB, colors=["#FFFFFF", "#888888", "#000000"], alpha=0.9)
		plt.gca().set_ylim(bottom=0)
		plt.gca().set_ylim(top=100)
		plt.gca().set_xlim(left=x[0])
		plt.gca().set_xlim(right=x[-1])
		leg.append("White wins")
		leg.append("Draws")
		leg.append("Black wins")
		lgnd = plt.legend(leg, markerscale=3./ptsize, fontsize=9)
		
	if type == "results" or type == "berserk":
		plt.gca().yaxis.set_major_formatter(PercentFormatter(decimals=0))

	#plt.yscale("log")
	plt.xticks(rotation=45)
	plt.grid(alpha=0.5)
	plt.title(types[type])
	plt.tight_layout()
	
	# Add lichess logo as background
	xmin, xmax = plt.gca().get_xlim()
	ymin, ymax = plt.gca().get_ylim()
	plt.gca().imshow(img, extent=[xmin, xmax, ymin, ymax], aspect='auto', alpha = (0.9 if type == "results" else 0.1))
	plt.gca().set_aspect(abs((xmax-xmin)/(ymax-ymin)))
	
	# Export figure to file
	if not os.path.exists(fwpath + va + "\\" + ev + "\\"):
		print(va + " - Creating directory " + fwpath + va + "\\" + ev + "\\")
		os.makedirs(fwpath + va + "\\" + ev + "\\")
	plt.savefig(fwpath + va + "\\" + ev + "\\" + va + "_" + ev + "_" + type + ".png")
	print(va + " - " + ev + " - " + type + " - Saved file.")
	plt.clf()
	
img = plt.imread("logo.png")
	
for va in variant:
	for ev in event:
		for type in types:
			makeplot(va, ev, type)

#time.sleep(60)
