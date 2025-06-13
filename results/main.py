from results.predictions import monte


####----Settings----####
country = "Thailand"
station = "PHUK"

N= 1000 #Number of samples in Monte Carlo
years_predict = 450 #Window of results - around 500 first then adjust for better visual
confidence_level = 95 #Choose confidence as percentage (0 < p < 100)
offset = 70  #Offset linear part of modelling function for better fit

####----Visuals----####
pred_pos = 4  #position above y=0
uncertainty_pos = 7 #position above y_pred


####----Run____####
monte(country, station, N, years_predict, confidence_level, offset, pred_pos, uncertainty_pos)
