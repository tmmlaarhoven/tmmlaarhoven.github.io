import requests
import re
import os
import time
import collections
import os.path
import ndjson
import json
import math
import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

APIToken = ""
with open("E:\\lichess\\APIToken.txt", "r") as TokenFile:
	for Line in TokenFile:
		APIToken = Line.strip()

PathData = "E:\\lichess\\tournaments\\data\\"
PathRank = "E:\\lichess\\tournaments\\rankings\\"
PathWeb = "E:\\lichess\\tmmlaarhoven.github.io\\lichess\\rankings\\"

plt.style.use(['dark_background'])

plt.rcParams.update({
	"axes.facecolor": 		(0.2, 0.2, 0.2, 1.0),  # green with alpha = 50%
	"savefig.facecolor": 	(0.0, 0.0, 1.0, 0.0),  # blue  with alpha = 20%
	"figure.figsize": 		(6.5, 6.5),
	"axes.labelsize": 		12,
	"xtick.labelsize": 		11,
	"ytick.labelsize": 		11,
	"legend.labelspacing": 	0.3,
	"legend.handlelength":	2.0,
	"legend.handletextpad": 0.3,
	"grid.color": 			(0.8, 0.8, 0.8),
	"grid.linestyle": 		":",
	"grid.linewidth": 		0.5,
	"legend.framealpha":	0.5,
	"font.family": 			['Roboto', 'serif'],
})

Events = {
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

Variants = {
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
	
VariantColors = {
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
	
Plots = {
	"players": "Players",
	"games": "Games per player",
	"points": "Points per player",
	"moves": "Moves per player per game",
	"topscore": "Highest score",
	"rating": "Average rating",
	"berserk": "Berserk rate",
	"results": "Results by color"
	}
	
UserPlots = {
	"trophies": "Gold medals",
	"points": "Total points",
	"events": "Events",
	"maximum": "Maximum score"
	}
	
def Prefix(V, E):
	return V + "_" + E + "_"

def Folder(V, E):
	return V + "\\" + E + "\\"
	
def PrintMessage(V, E, Message):
	print("{:<11}".format(V) + " - {:<8}".format(E) + " - " + Message)


# Generate plot for variant V, event type E, and plot type Plot
def MakePlot(V, E, Plot):
	
	plt.close()
	plt.figure()
	
	
	# Skip if no data
	if not os.path.exists(PathRank + Folder(V, E) + V + "_" + E + "_ranking.json") or not os.path.exists(PathRank + Folder(V, E) + V + "_" + E + "_arenas.ndjson"):
		PrintMessage(V, E, Plot + " - Nothing to do.")
		return
	
	# Initialize empty legend, and list of data
	Legend = []
	X = []
	Y = []
	if Plot == "results":
		YWhiteWins = []
		YDraws = []
		YBlackWins = []
		
	# Load data from arena data file
	with open(PathRank + Folder(V, E) + V + "_" + E + "_arenas.ndjson", "r") as DataFile:
		for Line in DataFile:
			ArenaInfo = json.loads(Line)
			X.append(datetime.datetime(int(ArenaInfo["Start"][0:4]), int(ArenaInfo["Start"][5:7]), int(ArenaInfo["Start"][8:10]), int(ArenaInfo["Start"][11:13]), int(ArenaInfo["Start"][14:16]), int(ArenaInfo["Start"][17:19])))
			if Plot == "players":
				Y.append(ArenaInfo["Players"])
			elif Plot == "games":
				Y.append(ArenaInfo["Games"] / max(1, ArenaInfo["Players"]))
			elif Plot == "points":
				Y.append(ArenaInfo["TotalPoints"] / max(1, ArenaInfo["Players"]))
			elif Plot == "moves":
				Y.append(ArenaInfo["Moves"] / max(1, ArenaInfo["Games"]) / 2)
			elif Plot == "topscore":
				Y.append(ArenaInfo["TopScore"])
			elif Plot == "rating":
				Y.append(ArenaInfo["TotalRating"] / max(1, ArenaInfo["Players"]))
			elif Plot == "berserk":
				Y.append(100. * ArenaInfo["Berserks"] / max(1, ArenaInfo["Games"]) / 2.)	
			elif Plot == "results":
				YWhiteWins.append(100. * ArenaInfo["WhiteWins"] / max(1, ArenaInfo["Games"]))
				YDraws.append(100. * (ArenaInfo["Games"] - ArenaInfo["BlackWins"] - ArenaInfo["WhiteWins"]) / max(1, ArenaInfo["Games"]))
				YBlackWins.append(100. * ArenaInfo["BlackWins"] / max(1, ArenaInfo["Games"]))
				
	# Process stacked chart for wins/draws/losses separately
	if Plot != "results":
		# Scatter plot of data
		PointSize = min(20., max(0.3, 1000./len(X)))
		plt.scatter(X, Y, s = [PointSize] * len(X), color = VariantColors[V])
		Legend.append(Events[E] + " " + Variants[V] + " (all)")
		# For big data sets, compute a moving average mean graph to plot as well	
		if len(X) > 1000:
			XMean = []
			YMean = []
			for i in range(50, len(X)-50):
				XMean.append(X[i])
				YMean.append(sum(Y[i-50:i+50]) / 100.)
			PointSizeMean = min(20., max(0.3, 1000./len(XMean)))
			plt.scatter(XMean, YMean, s = [PointSizeMean] * len(XMean), color = (1, 1, 1))
			#plt.plot(XMean, YMean, color=(1, 1, 1))
			Legend.append(Events[E] + " " + Variants[V] + " (mean)")
		elif len(X) > 100:
			XMean = []
			YMean = []
			for i in range(5, len(X)-5):
				XMean.append(X[i])
				YMean.append(sum(Y[i-5:i+5]) / 10.)
			PointSizeMean = min(20., max(0.3, 1000./len(XMean)))
			plt.scatter(XMean, YMean, s = [PointSizeMean] * len(XMean), color = (1, 1, 1))
			Legend.append(Events[E] + " " + Variants[V] + " (mean)")
		lgnd = plt.legend(Legend, markerscale = 3./PointSize, fontsize = 9)
		for handle in lgnd.legendHandles:
			handle.set_sizes([6.0])
	
	# Others are all scatter charts
	else:
		# Stacked plot of white wins, draws, losses
		PointSize = min(20., max(0.3, 1000./len(X)))
		plt.stackplot(X, YWhiteWins, YDraws, YBlackWins, colors = ["#FFFFFF", "#888888", "#000000"], alpha = 0.9)
		plt.gca().set_ylim(bottom = 0)
		plt.gca().set_ylim(top = 100)
		plt.gca().set_xlim(left = X[0])
		plt.gca().set_xlim(right = X[-1])
		Legend.append("White wins")
		Legend.append("Draws")
		Legend.append("Black wins")
		lgnd = plt.legend(Legend, markerscale = 3./PointSize, fontsize = 9)
	
	# Add percent sign to y-axis for percentages
	if Plot == "results" or Plot == "berserk":
		plt.gca().yaxis.set_major_formatter(PercentFormatter(decimals = 0))

	#plt.yscale("log")
	# Post-processing for all plots
	plt.xticks(rotation = 45)
	plt.grid(alpha = 0.5)
	plt.title(Plots[Plot])
	plt.tight_layout()
	
	# Add lichess logo as background, and fix aspect ratio to 1
	XMin, XMax = plt.gca().get_xlim()
	YMin, YMax = plt.gca().get_ylim()
	plt.gca().imshow(LichessLogo, extent = [XMin, XMax, YMin, YMax], aspect = 'auto', alpha = (0.9 if Plot == "results" else 0.1))
	plt.gca().set_aspect(abs((XMax - XMin) / (YMax - YMin)))
	
	# Export figure to file
	if not os.path.exists(PathWeb + Folder(V, E)):
		PrintMessage(V, E, "Creating directory " + PathWeb + Folder(V, E) + ".")
		os.makedirs(PathWeb + Folder(V, E))
		
	if not os.path.exists(PathWeb + Folder(V, E) + "figures\\"):
		os.makedirs(PathWeb + Folder(V, E) + "figures\\")
		print("Creating figures directory...")
		
	if os.path.exists(PathWeb + Folder(V, E) + Prefix(V, E) + Plot + ".png"):
		os.remove(PathWeb + Folder(V, E) + Prefix(V, E) + Plot + ".png")
	

	if os.path.exists(PathWeb + Folder(V, E) + "figures\\" + Prefix(V, E) + Plot + ".png"):
		os.remove(PathWeb + Folder(V, E) + "figures\\" + Prefix(V, E) + Plot + ".png")
		
	plt.savefig(PathWeb + Folder(V, E) + "figures\\" + Prefix(V, E) + "arena_" + Plot + ".png")
	PrintMessage(V, E, "Saved file arena_" + Plot + ".png.")
	plt.clf()
	
	

# Map a username to a color for plots
def UserHash(Username, Modulus):
	UserID = Username.lower()
	return (sum(ord(UserID[i]) * ord(UserID[i]) for i in range(len(UserID))) + len(Username)) % Modulus


# Plot scores/trophies/events/max per user over time
def UserPlot(V, E, Plot):
	
	plt.close()
	plt.figure()
	
	if not os.path.exists(PathRank + Folder(V, E) + V + "_" + E + "_arenas.ndjson"):
		#print(PathRank + Folder(V, E) + V + "_" + E + "_ranking.ndjson does not exist")
		return
	
	# https://www.materialui.co/colors - the "A100" colors
	UserColorsA100 = [(255,138,128), (255,128,171), (234,128,252), (179,136,255), (140,158,255), (130,177,255), (128,216,255), (132,255,255), (167,255,235), (185,246,202), (204,255,144), (244,255,129), (255,255,141), (255,229,127), (255,209,128), (255,158,128)]
	
	# https://www.materialui.co/colors - the "500" colors
	UserColors500 = [(244,67,54), (233,30,99), (156,39,176), (103,58,183), (63,81,181), (33,150,243), (3,169,244), (0,188,212), (0,150,136), (76,175,80), (139,195,74), (205,220,57), (255,235,59), (255,193,7), (255,152,0), (255,87,34), (121,85,72), (158,158,158), (96,125,139)]
	
	# https://www.materialui.co/colors - the "200" colors
	UserColors200 = [(239,154,154), (244,143,177), (206,147,216), (179,157,219), (159,168,218), (144,202,249), (129,212,250), (128,222,234), (128,203,196), (165,214,167), (197,225,165), (230,238,156), (255,245,157), (255,224,130), (255,204,128), (255,171,145), (188,170,164), (238,238,238), (176,190,197)]
		
	UserColors = [tuple(x / 255. for x in Tuple) for Tuple in (UserColors200 + UserColors500)]
	
	LineStyles = ['solid', 'dashed', 'dotted']
	
	PlotMarkers = ['o', 'v', '^', '<', '>', 's', '*', 'D']
	
	if not os.path.exists(PathWeb + Folder(V, E)):
		return

	Legend = []
	
	# Open rankings to find top 10 players
	TopPlayers = []
	with open(PathRank + Folder(V, E) + Prefix(V, E) + "players_" + Plot + ".ndjson", "r") as RankFile:
		for Line in RankFile:
			RankEntry = json.loads(Line)
			TopPlayers.append(RankEntry["Username"].lower())
			Legend.append(RankEntry["Username"].lower())
			if RankEntry["Ranking"] == 10:
				break
				
	#print(TopPlayers)
	
	# For each of the top 10 players
	for Index in range(10):
		UserID = TopPlayers[Index]
		# Load right variables
		X = []
		Y = []
		with open(PathRank + Folder(V, E) + "players\\" + Prefix(V, E) + UserID + ".ndjson", "r") as UserFile:
			CumTrophies = 0
			CumPoints = 0
			CumEvents = 0
			CumTopScore = 0
			for Line in UserFile:
				UserEntry = json.loads(Line)
				TimeNext = datetime.datetime(int(UserEntry["Start"][0:4]), int(UserEntry["Start"][5:7]), int(UserEntry["Start"][8:10]), int(UserEntry["Start"][11:13]), int(UserEntry["Start"][14:16]), int(UserEntry["Start"][17:19]))
				if Plot == "trophies":
					X.append(TimeNext - datetime.timedelta(minutes = 15))
					Y.append(CumTrophies)
					X.append(TimeNext)
					Y.append(UserEntry["CumTrophies"][0])
					CumTrophies = UserEntry["CumTrophies"][0]
				elif Plot == "points":
					X.append(TimeNext - datetime.timedelta(minutes = 15))
					Y.append(CumPoints)
					X.append(TimeNext)
					Y.append(UserEntry["CumPoints"])
					CumPoints = UserEntry["CumPoints"]
				elif Plot == "events":
					X.append(TimeNext - datetime.timedelta(minutes = 15))
					Y.append(CumEvents)
					X.append(TimeNext)
					Y.append(UserEntry["CumEvents"])
					CumEvents = UserEntry["CumEvents"]
				elif Plot == "maximum":
					X.append(TimeNext - datetime.timedelta(minutes = 15))
					Y.append(CumTopScore)
					X.append(TimeNext)
					Y.append(UserEntry["CumTopScore"])
					CumTopScore = UserEntry["CumTopScore"]
		# Add plot to plt
		plt.plot(X, Y, antialiased = True, color = UserColors[UserHash(UserID, len(UserColors))], linestyle = LineStyles[UserHash(UserID, len(LineStyles))], marker = PlotMarkers[UserHash(UserID, len(PlotMarkers))], markevery = 0.1)	
	
	plt.gca().set_ylim([0,None])
	plt.legend(Legend, loc = 'upper left', fontsize = 10, title = Variants[V] + " • " + Events[E], title_fontsize = 10)	
	
	# Post-processing for all plots	
	plt.xticks(rotation = 45)
	plt.grid(alpha = 0.5)
	plt.title(UserPlots[Plot])
	plt.tight_layout()
	
	# Add lichess logo as background, and fix aspect ratio to 1
	XMin, XMax = plt.gca().get_xlim()
	YMin, YMax = plt.gca().get_ylim()
	plt.gca().imshow(LichessLogo, extent = [XMin, XMax, YMin, YMax], aspect = 'auto', alpha = (0.9 if Plot == "results" else 0.1))
	plt.gca().set_aspect(abs((XMax - XMin) / (YMax - YMin)))
	
	# Export figure to file
	
	if not os.path.exists(PathWeb + Folder(V, E) + "figures\\"):
		os.makedirs(PathWeb + Folder(V, E) + "figures\\")
		print("Creating figures directory...")
	
	if os.path.exists(PathWeb + Folder(V, E) + Prefix(V, E) + "user_" + Plot + ".png"):
		os.remove(PathWeb + Folder(V, E) + Prefix(V, E) + "user_" + Plot + ".png")	
	
	plt.savefig(PathWeb + Folder(V, E) + "figures\\" + Prefix(V, E) + "user_" + Plot + ".png")
	PrintMessage(V, E, "Saved file user_" + Plot + ".png.")
	plt.clf()
	
	
	
	
	return 


	

# For "all" stats per variant, for a certain event type
def MakePieChart(E, Pie):
	labels = AllVariants[0:9]
	sizes = [15, 30, 45, 10, 20, 10, 30, 40, 20]
	#explode = (0, 0.1, 0, 0, 0, 0.2, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

	fig1, ax1 = plt.subplots()
	ax1.pie(sizes, counterclock = False, labels = labels, colors = AllColors, autopct = '%1.0f%%', shadow = True, startangle = 90)
	ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
	plt.tight_layout()
	
	plt.savefig("E:\\lichess\\piechart.png")
	

# Load lichess logo once and then reuse for all plots
LichessLogo = plt.imread("logo.png")
AllColors = [VariantColors[V] for V in VariantColors]
AllVariants = [V for V in Variants]

# Per variant and event, show arena statistics
for V in Variants:
	for E in Events:
		for Plot in Plots:
			MakePlot(V, E, Plot)
		for Plot in UserPlots:
			UserPlot(V, E, Plot)
			

# Per event, show arena statistics of all variants
#for E in Events:
#	for Pie in PieCharts:
MakePieChart("hourly", "bla")

#time.sleep(60)
print("ALL DONE!")

