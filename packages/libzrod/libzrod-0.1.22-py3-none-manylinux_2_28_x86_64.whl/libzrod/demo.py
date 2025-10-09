import libzrod
from libzrod import zrod, TaperBase_t, TubingBase_t, WaveResult_t, WaveResults_t, WaveParams_t, WaveParamsReadOnly_t, PuApi_t, PuInfo_t, DeviationSurveyPoint_t
import os
import numpy as np
import matplotlib.pyplot as plt



#These will hold the valued results
waveResults = WaveResults_t() #numeric results
waveParamsRO = WaveParamsReadOnly_t() #slightly confusing name - some parameters are internally generated, so this isnt a result, but its useful to see what the parameters were.

#before calling this, make sure all the WaveParams_t and Dyno or PuApi_t
def RunAndPlotDesign(plotPred=True, plotDiag=True, intermediateCardIndex=None):
  global waveResults, waveParamsRO

  if(myzrod.RunDesign() == False): #after this runs successfully, you can fetch the results
    print("Error: RunDesign() FAILED")

  (diagDynMeasuredX, diagDynMeasuredY) = myzrod.GetMeasuredDyno()
  (diagPmpMeasuredX, diagPmpMeasuredY) = myzrod.GetMeasuredPump()

  (diagDynUpscaledX, diagDynUpscaledY) = myzrod.GetUpscaledDyno() #this is the curve fitted (or "smoothed") measured card
  (diagPmpUpscaledX, diagPmpUpscaledY) = myzrod.GetUpscaledPump()

  (predDynX, predDynY) = myzrod.GetPredDyno()
  (predPmpX, predPmpY) = myzrod.GetPredPump()

  #measTime = np.arange(0, len(diagPmpMeasuredY), 1).tolist() #if we want to plot load vs. time or pos vs. time (TODO: should scale this to seconds)

  #fetch the numeric results
  waveResults = myzrod.GetWaveResults()
  waveParamsRO = myzrod.GetWaveParamsReadOnly()

  fig, ax = plt.subplots()
  if(plotDiag == True):
    ax.plot(diagDynMeasuredX, diagDynMeasuredY, ".", markersize=3, color="gray")
    ax.plot(diagDynMeasuredX, diagDynMeasuredY, "-", lw=0.5, color="gray")
    ax.plot(diagDynUpscaledX, diagDynUpscaledY, color="blue")

    ax.plot(diagPmpMeasuredX, diagPmpMeasuredY, ".", markersize=3, color="gray")
    ax.plot(diagPmpMeasuredX, diagPmpMeasuredY, "-", lw=0.5, color="gray")
    ax.plot(diagPmpUpscaledX, diagPmpUpscaledY, color="green")
  #endif

  if(intermediateCardIndex is not None):
    ax.plot(intermediateX, intermediateY, color="orange")
    (intermediateX, intermediateY) = myzrod.GetIntermediateCard(intermediateCardIndex, 1)
  #endif

  if(plotPred == True):
    ax.plot(predDynX, predDynY, ".", markersize=3, color="red")
    ax.plot(predPmpX, predPmpY, ".", markersize=3, color="lime")
  #endif
  plt.show()
#end RunAndPlotDesign()


def RunAndPlotDesignVsTime(plotPred=True, plotDiag=True, intermediateCardIndex=None):
  global waveResults, waveParamsRO

  if(myzrod.RunDesign() == False): #after this runs successfully, you can fetch the results
    print("Error: RunDesign() FAILED")

  (diagDynMeasuredX, diagDynMeasuredY) = myzrod.GetMeasuredDyno()
  (diagPmpMeasuredX, diagPmpMeasuredY) = myzrod.GetMeasuredPump()

  (diagDynUpscaledX, diagDynUpscaledY) = myzrod.GetUpscaledDyno() #this is the curve fitted (or "smoothed") measured card
  (diagPmpUpscaledX, diagPmpUpscaledY) = myzrod.GetUpscaledPump()

  (predDynX, predDynY) = myzrod.GetPredDyno()
  (predPmpX, predPmpY) = myzrod.GetPredPump()

  #measTime = np.arange(0, len(diagPmpMeasuredY), 1).tolist() #if we want to plot load vs. time or pos vs. time (TODO: should scale this to seconds)

  #fetch the numeric results
  waveResults = myzrod.GetWaveResults()
  waveParamsRO = myzrod.GetWaveParamsReadOnly()

  fig, ax = plt.subplots()
  if(plotDiag == True):
    measTime = np.arange(0, len(diagPmpMeasuredY), 1).tolist() #if we want to plot load vs. time or pos vs. time (TODO: should scale this to seconds)
    measTime2 = np.arange(len(diagPmpMeasuredY)-1, len(diagPmpMeasuredY)*2-1, 1).tolist() #if we want to plot load vs. time or pos vs. time (TODO: should scale this to seconds)
    upscTime = np.arange(0, len(diagPmpUpscaledY), 1).tolist() #if we want to plot load vs. time or pos vs. time (TODO: should scale this to seconds)

    #ax.plot(measTime, diagDynMeasuredX, ".", markersize=3, color="gray")
    ax.plot(measTime, diagDynMeasuredX, "-", lw=0.5, color="gray")
    #ax.plot(upscTime, diagDynUpscaledX, color="blue")
    #ax.plot(measTime2, diagDynMeasuredX, "-", lw=0.5, color="blue")

    #ax.plot(measTime, diagPmpMeasuredX, ".", markersize=3, color="gray")
    #ax.plot(measTime, diagPmpMeasuredX, "-", lw=0.5, color="gray")
    #ax.plot(upscTime, diagPmpUpscaledX, color="green")
  #endif


  if(plotPred == True):
    predTime = np.arange(0, len(predDynX), 1).tolist() #if we want to plot load vs. time or pos vs. time (TODO: should scale this to seconds)

    ax.plot(predTime, predDynX, ".", markersize=3, color="red")
    #ax.plot(predTime, predPmpX, ".", markersize=3, color="lime")
    print(len(predDynX))
  #endif
  plt.show()
#end RunAndPlotDesignVsTime()



def PrintWaveResults():
  print("waveResults:")
  for field in waveResults._fields_:
    if(type(getattr(waveResults, field[0])) is WaveResult_t):
      print(f"    {field[0]}:")
      innerval = getattr(waveResults, field[0])
      for fieldx in innerval._fields_:
        print(f"        {fieldx[0]}: {getattr(innerval, fieldx[0]):.4f}")
      #end for
    else:
      print(f"    {field[0]}: {getattr(waveResults, field[0]):.4f}")
    #endif
  #end for
#end PrintWaveResults()

def PrintWaveParamsReadOnly():
  print("waveParamsRO:")
  for field in waveParamsRO._fields_:
    if(isinstance(getattr(waveParamsRO, field[0]), int)):
      print(f"    {field[0]}: {getattr(waveParamsRO, field[0])}")
    else:
      print(f"    {field[0]}: {getattr(waveParamsRO, field[0]):.4f}")
    #endif
  #end for
#end PrintWaveParamsReadOnly()

def PrintWaveParams():
  print("waveParams:")
  for field in waveParams._fields_:
    print(f"    {field[0]}: {getattr(waveParams, field[0])}")
  #end for
#end PrintWaveParams()



myzrod = zrod()
myzrod.SetClientVersion("simpledemo", 0, 0, 0, 1) #you dont need to set this, but it might help debugging. This is the version of your front-end code.
libver = myzrod.GetZrodVersionString() #this is the version of the compiled library (not the python package, but eventually those will be synchronized)
print(f"libzrod library version: v{libver}")
print(f"libzrod package version: v{libzrod.__version__}")

result = myzrod.Login("demo", "password1") #dont do this in your code. Save the auth somewhere safe.



waveParams = myzrod.GetWaveParams()
waveParams.WellDepth = 10000
result = myzrod.SetWaveParams(waveParams)
tuarr = (TubingBase_t*1)()
tuarr[0] = TubingBase_t(L=10000, ID=2.441, OD=2.875, W=2.904, weight=6.5, E=30500000, R=490)
result = myzrod.xSetDiagTubings(tuarr)
result = myzrod.xSetPredTubings(tuarr)


result = myzrod.SetUpscaledDynoPointCount(4000) #this is for the smoothed/curve-fitted measured surface card
result = myzrod.SetFourierCoeffCountPos(23) #these are for the curve fitting of a measured dyno card
result = myzrod.SetFourierCoeffCountLoad(50)


waveSettings = myzrod.GetWaveSettings()
waveSettings.predNodesPerSection = 10
#waveSettings.useOldPredAlgorith = True
myzrod.SetWaveSettings(waveSettings)



waveParams = myzrod.GetWaveParams()
waveParams.usePumpingUnitForPosition = True
result = myzrod.SetWaveParams(waveParams)

puapi = PuApi_t()
puapi.Type = ord("C")
puapi.Rotate = 1
#puapi.A = 111.0
#puapi.P = 114.0
#puapi.C = 96.05
#puapi.I = 96.0
#puapi.K = 151.34
#puapi.R = 36.2
#puapi.CBE = 450.0
#puapi.Torque = 228.0 * 1000.0
#puapi.Structure = 213.0 * 100.0
#puapi.MaxStroke = 86.0
#puapi.S = 86.0
puapi.A = 158.375
puapi.P = 122.499992
puapi.C = 100
puapi.I = 110
puapi.K = 164.639999
puapi.R = 43
puapi.CBE = 450.0
puapi.Torque = 456.0 * 1000.0
puapi.Structure = 213.0 * 100.0
puapi.MaxStroke = 144.0
puapi.S = 144.0
result = myzrod.SetPuApi(puapi)

'''
jetta_adobe_21_surface_x = [687.0, 642.2, 596.5, 550.4, 504.4, 459.0, 414.3, 370.5, 327.7, 286.1, 246.0, 207.9, 172.2, 139.0, 108.5, 80.8, 56.0, 34.8, 17.8, 5.9, 0.1, 0.4, 6.8, 18.5, 34.4, 53.9, 76.1, 100.9, 128.2, 157.8, 189.8, 223.8, 259.7, 297.3, 336.5, 377.1, 419.1, 462.2, 506.4, 551.2, 596.6, 642.4, 688.4, 734.5, 780.5, 826.4, 872.0, 917.0, 961.2, 1004.4, 1046.5, 1087.3, 1126.5, 1164.2, 1200.0, 1233.8, 1265.4, 1294.8, 1321.6, 1345.9, 1367.7, 1386.8, 1403.4, 1417.4, 1428.9, 1437.8, 1444.2, 1448.2, 1449.9, 1449.4, 1446.7, 1442.0, 1435.3, 1426.7, 1416.3, 1404.2, 1390.4, 1375.1, 1358.2, 1339.7, 1319.8, 1298.5, 1275.8, 1251.7, 1226.1, 1199.2, 1170.9, 1141.2, 1110.2, 1077.9, 1044.1, 1009.0, 972.5, 934.7, 895.8, 855.9, 815.1, 773.5, 730.8, 687.0]
jetta_adobe_21_surface_y = [10583, 10409, 10157, 9891, 9681, 9575, 9576, 9653, 9778, 9956, 10230, 10641, 11186, 11799, 12374, 12827, 13139, 13359, 13555, 13756, 13927, 14009,  13982, 13917, 13957, 14243, 14815, 15585, 16380, 17054, 17575, 18039, 18592, 19305, 20096, 20749, 21024, 20791, 20107, 19183, 18275, 17545, 17007, 16557, 16076, 15529, 15001, 14650, 14606, 14884, 15369, 15875, 16241, 16412, 16447, 16456, 16517, 16613, 16642, 16488, 16099, 15538, 14952, 14494, 14242, 14160, 14143, 14084, 13945, 13766, 13615,  13522, 13446, 13295, 12996, 12547, 12030, 11557, 11196, 10923, 10643, 10250, 9700, 9046, 8409, 7918, 7651, 7615, 7766, 8045, 8402, 8802, 9219, 9619, 9975, 10265, 10479, 10612, 10651, 10583]
jetta_adobe_21_surface_x = [x/10.0 for x in jetta_adobe_21_surface_x]
myzrod.LoadDyn(8.1, jetta_adobe_21_surface_x, jetta_adobe_21_surface_y)

waveParams = myzrod.GetWaveParams() #kind of redundant, but you can copy this whole block and run different parameters
waveParams.predSpm = waveParams.diagSpm
#waveParams.predFillage = 0.6
#waveParams.predCompression = 0.70
waveParams.predCasingPressure = 93
waveParams.predTubingPressure = 200.2
waveParams.predFluidSG = 1.0 #NOTE: if you change this, it'll affect the rod weight in fluid, so you need to do a RunDesign() and fetch rod details, if you're displaying those.
waveParams.predFluidLevel = 2000 #from surface
waveParams.diagPumpPlungerDiameter = 1.5
waveParams.predPumpPlungerDiameter = 1.5
waveParams.diagDampUp = 0.2
waveParams.diagDampDn = 0.2
waveParams.predDampUp = 0.2
waveParams.predDampDn = 0.2
waveParams.predFo = 4000 #the pump load can be set directly, or you can use a calculated value.
result = myzrod.SetWaveParams(waveParams) #set the internal parameters, and then we can run the design.

tarr = (TaperBase_t * 3)()
tarr[0] = TaperBase_t(id=str.encode(""), L=3200, D=0.875, W=2.224, E=30500000, R=492)
tarr[1] = TaperBase_t(id=str.encode(""), L=2550, D=0.750, W=1.630, E=30500000, R=492)
tarr[2] = TaperBase_t(id=str.encode(""), L= 300, D=1.500, W=6.500, E=30500000, R=492)
fluidSG = 1.0 #this is for calculating the rod weight in fluid. It'll get saved internally and you can fetch it via GetWaveParams() below
result = myzrod.xSetDiagTapers(tarr, fluidSG)
result = myzrod.xSetPredTapers(tarr, fluidSG)

#RunAndPlotDesign()
#RunAndPlotDesignVsTime()








jetta_adobe_31_surface_x = [745.3, 792.8, 839.8, 886.2, 931.8, 976.4, 1019.9, 1062.1, 1102.8, 1141.8, 1178.9, 1213.9, 1246.6, 1276.8, 1304.5, 1329.5, 1351.7, 1371.1, 1387.6, 1401.3, 1412.3, 1420.6, 1426.3, 1429.4, 1430.0, 1428.4, 1424.5, 1418.5, 1410.5, 1400.5, 1388.6, 1375.0, 1359.6, 1342.6, 1323.9, 1303.6, 1281.8, 1258.3, 1233.4, 1207.1, 1179.4, 1150.2, 1119.4, 1087.2, 1053.5, 1018.4, 982.0, 944.2, 905.1, 864.7, 822.9, 779.9, 735.7, 690.6, 644.8, 598.3, 551.6, 504.9, 458.5, 412.7, 367.8, 323.9, 281.5, 240.8, 202.4, 166.7, 133.9, 104.2, 77.9, 55.2, 36.3, 21.6, 11.0, 4.2, 0.7, 0.0, 1.6, 5.7, 12.7, 23.2, 37.4, 55.3, 76.5, 100.8, 127.8, 157.3, 189.2, 223.5, 259.9, 298.2, 338.2, 379.5, 422.1, 465.9, 510.8, 556.7, 603.2, 650.3, 697.8, 745.3]
jetta_adobe_31_surface_y = [18443, 17824, 17439, 17340, 17481, 17762, 18087, 18396, 18658, 18835, 18877, 18734, 18409, 17980, 17582, 17345, 17324, 17484, 17732, 17982, 18197,  18382, 18538, 18630, 18607, 18439, 18162, 17860, 17600, 17374, 17104, 16715, 16233, 15805, 15621, 15766, 16122, 16392, 16272, 15647, 14677, 13709, 13049, 12761, 12619, 12268, 11463, 10253, 8961, 8003, 7651, 7903, 8531, 9235, 9802, 10167, 10354, 10392, 10268, 9964, 9519, 9062, 8764, 8747, 9013, 9451, 9904, 10254, 10463, 10551, 10541, 10435, 10233, 9969, 9732, 9632, 9741, 10035, 10413, 10754, 11000, 11183, 11403, 11754, 12268, 12900, 13570, 14218, 14836, 15471, 16181, 16995, 17884, 18759, 19490, 19945, 20029, 19732, 19146, 18443]
jetta_adobe_31_surface_x = [x/10.0 for x in jetta_adobe_31_surface_x]
myzrod.LoadDyn(4.9, jetta_adobe_31_surface_x, jetta_adobe_31_surface_y)

waveParams = myzrod.GetWaveParams() #kind of redundant, but you can copy this whole block and run different parameters
waveParams.predSpm = waveParams.diagSpm
waveParams.predFillage = 0.8
waveParams.predCompression = 0.30
waveParams.predCasingPressure = 108
waveParams.predTubingPressure = 250.5
waveParams.predFluidSG = 1.0 #NOTE: if you change this, it'll affect the rod weight in fluid, so you need to do a RunDesign() and fetch rod details, if you're displaying those.
waveParams.predFluidLevel = 2000 #from surface
waveParams.diagPumpPlungerDiameter = 1.75
waveParams.predPumpPlungerDiameter = 1.75
waveParams.diagDampUp = 0.2
waveParams.diagDampDn = 0.2
waveParams.predDampUp = 0.2
waveParams.predDampDn = 0.2
waveParams.predFo = 5500 #the pump load can be set directly, or you can use a calculated value.
result = myzrod.SetWaveParams(waveParams) #set the internal parameters, and then we can run the design.

tarr = (TaperBase_t * 3)()
tarr[0] = TaperBase_t(id=str.encode(""), L=2400, D=0.875, W=2.224, E=30500000, R=492)
tarr[1] = TaperBase_t(id=str.encode(""), L=3200, D=0.750, W=1.630, E=30500000, R=492)
tarr[2] = TaperBase_t(id=str.encode(""), L= 300, D=1.500, W=6.500, E=30500000, R=492)
fluidSG = 1.0 #this is for calculating the rod weight in fluid. It'll get saved internally and you can fetch it via GetWaveParams() below
result = myzrod.xSetDiagTapers(tarr, fluidSG)
result = myzrod.xSetPredTapers(tarr, fluidSG)

#RunAndPlotDesign()
#RunAndPlotDesignVsTime()




'''


waveSettings = myzrod.GetWaveSettings()
waveSettings.predNodesPerSection = 15
#waveSettings.useOldPredAlgorith = True
myzrod.SetWaveSettings(waveSettings)

#waveParams = myzrod.GetWaveParams()
#waveParams.usePumpingUnitForPosition = True
#result = myzrod.SetWaveParams(waveParams)

#puapi = PuApi_t()
#puapi.Type = ord("C")
#puapi.Rotate = 1

#puapi.A = 132
#puapi.P = 147
#puapi.C = 122.629997
#puapi.I = 132
#puapi.K = 197.569992
#puapi.R = 53
#puapi.CBE = 450.0
#puapi.Torque = 456.0 * 1000.0
#puapi.Structure = 365.0 * 100.0
#puapi.MaxStroke = 120.0
#puapi.S = 120.0

#puapi.A = 132
#puapi.C = 100
#puapi.I = 110
#puapi.K = 164.639999
#puapi.P = 122.499992
#puapi.R = 43
#puapi.CBE = 450.0
#puapi.Torque = 456.0 * 1000.0
#puapi.Structure = 365.0 * 100.0
#puapi.MaxStroke = 120.0
#puapi.S = 120.0
#result = myzrod.SetPuApi(puapi)


tarr = (TaperBase_t * 4)()
#tarr[0] = TaperBase_t(id=str.encode(""), L=2400, D=0.875, W=2.224, E=30500000, R=492)
#tarr[0] = TaperBase_t(id=str.encode(""), L=1806, D=0.735, W=0.484, E= 7200000, R=153)
tarr[0] = TaperBase_t(id=str.encode(""), L=1806, D=1.225, W=1.2879, E= 7200000, R=153)
tarr[1] = TaperBase_t(id=str.encode(""), L=1550, D=0.875, W=2.224, E=30500000, R=492)
tarr[2] = TaperBase_t(id=str.encode(""), L=1950, D=0.750, W=1.630, E=30500000, R=492)
tarr[3] = TaperBase_t(id=str.encode(""), L= 275, D=1.500, W=6.500, E=30500000, R=492)
fluidSG = 1.0 #this is for calculating the rod weight in fluid. It'll get saved internally and you can fetch it via GetWaveParams() below
result = myzrod.xSetDiagTapers(tarr, fluidSG)
result = myzrod.xSetPredTapers(tarr, fluidSG)


jetta_barstow_10_7_surface_x = [657.0, 613.6, 568.6, 522.5, 476.4, 430.9, 386.2, 342.6, 300.2, 259.3, 220.2, 183.6, 149.8, 119.2, 92.0, 68.2, 47.8, 30.9, 17.6, 7.9, 2.0, 0.0,  1.8, 7.5, 16.9, 29.7, 45.8, 65.1, 87.5, 113.2, 141.7, 172.9, 206.2, 241.3, 278.0, 316.2, 355.7, 396.3, 437.7, 479.8, 522.2, 564.8, 607.9, 651.3, 695.3, 739.6, 784.3, 829.2, 874.1, 918.8, 963.2, 1006.9, 1049.7, 1091.3, 1131.6, 1170.1, 1206.8, 1241.2, 1273.2, 1302.5, 1329.2, 1353.2, 1374.5, 1392.9, 1408.2, 1420.4, 1429.5, 1435.8, 1439.4, 1440.6, 1439.2, 1435.4, 1429.2, 1420.8, 1410.6, 1398.6, 1385.0, 1369.4, 1351.8, 1332.1, 1310.5, 1287.2, 1262.4, 1236.0, 1207.9, 1177.8, 1146.2, 1113.1, 1079.2, 1044.5, 1008.9, 972.2, 934.2, 895.1, 855.7, 816.4, 777.4, 738.3, 698.5, 657.0]
jetta_barstow_10_7_surface_y = [5838, 6075, 6354, 6743, 7236, 7742, 8132, 8318, 8296, 8132, 7918, 7716, 7546, 7409, 7319, 7311, 7419, 7649, 7959, 8289, 8594, 8870, 9157, 9502, 9920, 10384, 10834, 11215, 11512, 11764, 12051, 12458, 13038, 13782, 14619, 15444, 16172, 16780, 17323, 17894, 18562, 19306, 20008, 20504, 20668, 20481, 20033, 19461, 18874, 18301, 17722, 17122, 16548, 16093, 15838, 15787, 15867, 15981, 16094, 16258, 16561, 17022, 17525, 17855, 17832, 17448, 16911, 16539, 16563, 16972, 17503, 17786, 17568,  16849, 15869, 14947, 14296, 13925, 13684, 13393, 12959, 12411, 11841, 11323, 10864, 10425, 9972, 9497, 9013, 8511, 7952, 7298, 6565, 5851, 5301, 5030, 5053, 5280, 5573, 5838]
jetta_barstow_10_7_surface_x = [x/10.0 for x in jetta_barstow_10_7_surface_x]
myzrod.LoadDyn(8.0, jetta_barstow_10_7_surface_x, jetta_barstow_10_7_surface_y)
#print(len(jetta_barstow_10_7_surface_x), len(jetta_barstow_10_7_surface_y))

waveParams = myzrod.GetWaveParams() #kind of redundant, but you can copy this whole block and run different parameters
waveParams.predSpm = waveParams.diagSpm
waveParams.predFillage = 1.0
waveParams.predCompression = 1.0
waveParams.predCasingPressure = 118.3
waveParams.predTubingPressure = 127.1
waveParams.predFluidSG = 1.0 #NOTE: if you change this, it'll affect the rod weight in fluid, so you need to do a RunDesign() and fetch rod details, if you're displaying those.
waveParams.predFluidLevel = 2000 #from surface
waveParams.diagPumpPlungerDiameter = 2
waveParams.predPumpPlungerDiameter = 2
waveParams.diagDampUp = 0.2
waveParams.diagDampDn = 0.2
waveParams.predDampUp = 0.2
waveParams.predDampDn = 0.2
waveParams.predFo = 7000 #the pump load can be set directly, or you can use a calculated value.
result = myzrod.SetWaveParams(waveParams) #set the internal parameters, and then we can run the design.

RunAndPlotDesign()
#RunAndPlotDesignVsTime()
