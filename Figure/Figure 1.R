# ------------------------
# define global settings
# ------------------------
SETTING_PIPELINE_NAME = "121_strava all areas determinants analysis"

col.black = "#000000"
col.dark_blue = "#3c5488"
col.light_blue = "#4dbbd5"
col.light_blue2 = "#eff6fb"
col.green = "#00A087"
col.purple = "#9632B8"
col.orange = "#FF7F0E"

# ------------------------
# define path
# ------------------------
DIR_HOME = "XXXXXX"
DIR_PIPELINE = paste(DIR_HOME, "2_pipeline\\", SETTING_PIPELINE_NAME, sep="")
setwd(DIR_HOME)

# ------------------------
# import libraries
# ------------------------
library(sf)
library(ggplot2)
library(dplyr)
library(tidyverse)
library(stargazer)
library(readr)
library(eeptools)
library(scales)
library(fastDummies)
library(lfe)
library(stringi)
library(patchwork)
library(cowplot)
library(Hmisc)


# ------------------------
# import sources
# ------------------------
source("1_code/0_common/theme_figure.R")

# ------------------------
# read data
# ------------------------
dta_result1 = read.csv(paste0(DIR_PIPELINE, '/store/city no interaction coef 3.csv'), encoding = 'UTF-8')
dta_result2 = read.csv(paste0(DIR_PIPELINE, '/store/city with interaction coef 3.csv'), encoding = 'UTF-8')
dta_info1 = read.csv(paste0(DIR_HOME, '/2_pipeline/110_aggregate data/out/all admin 2 info.csv'), encoding = 'UTF-8')
dta_info2 = read.csv(paste0(DIR_PIPELINE, '/store/large country experiment user list all countries 1000.csv'), encoding = 'UTF-8')


# ------------------------
# process data
# ------------------------
dta_result1$NAME_0 = stri_unescape_unicode(gsub("<U\\+(....)>", "\\\\u\\1", dta_result1$NAME_0))
dta_result1$NAME_1 = stri_unescape_unicode(gsub("<U\\+(....)>", "\\\\u\\1", dta_result1$NAME_1))
dta_result1$NAME_2 = stri_unescape_unicode(gsub("<U\\+(....)>", "\\\\u\\1", dta_result1$NAME_2))
dta_result2$NAME_0 = stri_unescape_unicode(gsub("<U\\+(....)>", "\\\\u\\1", dta_result2$NAME_0))
dta_result2$NAME_1 = stri_unescape_unicode(gsub("<U\\+(....)>", "\\\\u\\1", dta_result2$NAME_1))
dta_result2$NAME_2 = stri_unescape_unicode(gsub("<U\\+(....)>", "\\\\u\\1", dta_result2$NAME_2))
dta_info2_processed = dta_info2 %>%
  group_by(NAME_0, NAME_1, NAME_2) %>%
  summarise(unique_user = length(user_id))
  


# ------------------------
# result data
# ------------------------
dta_result1 = dta_result1 %>%
  rename(c("Long_term_effect"="IS_COVID_START"))
dta_result2 = dta_result2 %>%
  rename(c("Long_term_effect"="IS_COVID_START"))

dta1 = left_join(dta_result1, dta_info1)
dta1 = left_join(dta1, dta_info2_processed)
dta2 = left_join(dta_result2, dta_info1)
dta2 = left_join(dta2, dta_info2_processed)
dta2 = subset(dta2, !is.na(unique_user))
dta1$best_temp = -dta1$TEMP / (dta1$TEMP2 * 2)
dta1$best_humid = -dta1$HUMI / (dta1$HUMI2 * 2)
dta2$best_temp = -dta2$TEMP / (dta2$TEMP2 * 2)
dta2$best_humid = -dta2$HUMI / (dta2$HUMI2 * 2)

# Weather
generate_weather_plot = function(){
  lower_bound = 0.1
  upper_bound = 0.9
  clean_temp = subset(dta2, between(TEMP, quantile(dta2$TEMP, lower_bound), quantile(dta2$TEMP, upper_bound)))
  clean_humi = subset(dta2, between(HUMI, quantile(dta2$HUMI, lower_bound), quantile(dta2$HUMI, upper_bound)))
  clean_wind = subset(dta2, between(WIND, quantile(dta2$WIND, lower_bound), quantile(dta2$WIND, upper_bound)))
  clean_visi = subset(dta2, between(VISI, quantile(dta2$VISI, lower_bound), quantile(dta2$VISI, upper_bound)))
  clean_pres = subset(dta2, between(PRES, quantile(dta2$PRES, lower_bound), quantile(dta2$PRES, upper_bound)))
  clean_clod = subset(dta2, between(CLOD, quantile(dta2$CLOD, lower_bound), quantile(dta2$CLOD, upper_bound)))
  clean_prcp = subset(dta2, between(PRCP, quantile(dta2$PRCP, lower_bound), quantile(dta2$PRCP, upper_bound)))
  
  dta_stat = data.frame(
    c("Temperature (Linear)","Temperature (Squared)", 'Humidity (Linear)', 'Humidity (Squared)', 'Wind', 'Visibility', 'Pressure', 'Cloud', 'Precipitation'),
    c("celsius degree","celsius degree","percentage", 'percentage', 'km per hour', '100 meters', 'mmHg', 'percentage','centimeter'),

    c(weighted.mean(clean_temp$TEMP / 10, clean_temp$unique_user, na.rm=T), 
      weighted.mean(clean_temp$TEMP2, clean_temp$unique_user, na.rm=T),
      weighted.mean(clean_temp$HUMI / 10, clean_temp$unique_user, na.rm=T),
      weighted.mean(clean_temp$HUMI2, clean_temp$unique_user, na.rm=T), 
      weighted.mean(clean_wind$WIND, clean_wind$unique_user), 
      weighted.mean(clean_visi$VISI / 10, clean_visi$unique_user), 
      weighted.mean(clean_pres$PRES, clean_pres$unique_user), 
      weighted.mean(clean_clod$CLOD, clean_clod$unique_user),
      weighted.mean(clean_prcp$PRCP * 10, clean_prcp$unique_user)),

    c(wtd.var(clean_temp$TEMP / 10, clean_temp$unique_user), 
      wtd.var(clean_temp$TEMP2, clean_temp$unique_user), 
      wtd.var(clean_temp$HUMI / 10, clean_temp$unique_user),
      wtd.var(clean_temp$HUMI2, clean_temp$unique_user),  
      wtd.var(clean_wind$WIND, clean_wind$unique_user), 
      wtd.var(clean_visi$VISI / 10, clean_visi$unique_user), 
      wtd.var(clean_pres$PRES, clean_pres$unique_user), 
      wtd.var(clean_clod$CLOD, clean_clod$unique_user),
      wtd.var(clean_prcp$PRCP * 10, clean_prcp$unique_user))
  )
  
  dta_unit = data.frame(
    c("Temperature (Linear)","Temperature (Squared)", 'Humidity (Linear)', 'Humidity (Squared)', 'Wind', 'Visibility', 'Pressure', 'Cloud', 'Precipitation'),
    c("10 celsius degree","celsius degree","10 percent", 'percent', 'km per hour', '100 meters', 'mmHg', 'percent','centimeter')
  )
  colnames(dta_stat) = c('item', 'unit','average', 'std')
  colnames(dta_unit) = c('item', 'unit')
  
  temp_1 = ggplot(subset(dta_stat, !item %in% c("Temperature", 'Humidity')), aes(y=item)) +
    geom_point(mapping=aes(x=average), shape=15, size=3) + 
    geom_linerange(mapping=aes(xmin=average-std, xmax=average+std)) +
    geom_vline(xintercept=0, linetype='dashed') +
    labs(x="Weekly exercise duration (minute)", y="") + 
    coord_cartesian(ylim=c(1,10), xlim=c(-1, 1)) +
    geom_text(x=-0.6, y=10, label='Less exercise duration') +
    geom_text(x=0.6, y=10, label='More exercise duration') +
    theme_Publication() +
    theme(
      # legend.title = element_text("Gender"),
      legend.text = element_text(size = 12),
      legend.key.size= unit(0.8, "cm"),
      legend.direction = "vertical",
      legend.position = c(0.9, 0.9),
      axis.line.y = element_blank(),
      axis.ticks.y = element_blank(),
      axis.text.y = element_blank(),
      axis.title.y = element_blank()
      # legend.position = "right"
    )
  
  temp_2 = ggplot(subset(dta_unit, !item %in% c("Temperature", 'Humidity')), aes(y=item)) +
    geom_text(mapping=aes(x=0, label = item)) + 
    geom_text(mapping=aes(x=0.5, label = unit)) +
    geom_text(x=0, y=10, label="Weather", fontface='bold')+
    geom_text(x=0.5, y=10, label="Unit", fontface='bold')+
    theme_void() + 
    coord_cartesian(xlim=c(-0.2, 1), ylim=c(1,10))
  
  
  layout = c(
    area(t=0, l=0, b=30, r=4),
    area(t=1, l=4, b=30, r=9)
  )
  
  fig_weather_forestplot = temp_2 + temp_1 + plot_layout(design=layout) 
  fig_weather_forestplot
}

fig_weather_forestplot = generate_weather_plot()
fig_weather_forestplot

# Gender
generate_gender_plot = function(){
  dta_stat = data.frame(
    c("Gender"),
    # c(mean(dta2$user_gender)),
    # c(sd(dta2$user_gender)),
    c(wtd.mean(dta2$user_gender, dta2$unique_user)),
    c(wtd.var(dta2$user_gender, dta2$unique_user))
  )
  write.csv(dta_stat, paste0(DIR_PIPELINE, "\\out\\gender_info.csv"))
  
  dta_unit = data.frame(
    c("Gender"),
    c("female = 1")
  )
  colnames(dta_stat) = c('Demographic', 'average', 'std')
  colnames(dta_unit) = c('Demographic', 'unit')
  
  temp_1 = ggplot(dta_stat, aes(y=Demographic)) +
    geom_point(mapping=aes(x=average), shape=15, size=3) + 
    geom_linerange(mapping=aes(xmin=average-std, xmax=average+std)) +
    geom_vline(xintercept=0, linetype='dashed') +
    labs(x="Weekly exercise duration (minute)", y="") + 
    coord_cartesian(ylim=c(1,2), xlim=c(-3, 2)) +
    geom_text(x=-.8, y=2, label='Less exercise duration') +
    geom_text(x=.8, y=2, label='More exercise duration') +
    theme_Publication() +
    theme(
      # legend.title = element_text("Gender"),
      legend.text = element_text(size = 12),
      legend.key.size= unit(0.8, "cm"),
      legend.direction = "vertical",
      legend.position = c(0.9, 0.9),
      axis.line.y = element_blank(),
      axis.ticks.y = element_blank(),
      axis.text.y = element_blank(),
      axis.title.y = element_blank()
    )
  temp_1

  temp_2 = ggplot(dta_unit, aes(y=Demographic)) +
    geom_text(mapping=aes(x=0, label = Demographic)) + 
    geom_text(mapping=aes(x=0.5, label = unit)) +
    geom_text(x=0, y=2, label="Demographic", fontface='bold')+
    geom_text(x=0.5, y=2, label="Unit", fontface='bold')+
    theme_void() + 
    coord_cartesian(xlim=c(-0.2, 1), ylim=c(1,2))
  temp_2
  
  layout = c(
    area(t=0, l=0, b=30, r=4),
    area(t=1, l=4, b=30, r=9)
  )
  
  fig_demographic_forestplot = temp_2 + temp_1 + plot_layout(design=layout) 
  fig_demographic_forestplot
  
}
fig_gender_forestplot = generate_gender_plot()
fig_gender_forestplot

# Social factor
generate_social_plot = function(){
  
  dta_stat = data.frame(
    c("Log number of following"),
    # c(mean(dta2$LG_FOLLOW)),
    # c(sd(dta2$LG_FOLLOW)),
    c(wtd.mean(dta2$LG_FOLLOW, dta2$unique_user)),
    c(wtd.var(dta2$LG_FOLLOW, dta2$unique_user))
  )
  
  dta_unit = data.frame(
    c("Log number of following"),
    c("-")
  )
  colnames(dta_stat) = c('Social', 'average', 'std')
  colnames(dta_unit) = c('Social', 'unit')
  
  temp_1 = ggplot(dta_stat, aes(y=Social)) +
    geom_point(mapping=aes(x=average), shape=15, size=3) + 
    geom_linerange(mapping=aes(xmin=average-std, xmax=average+std)) +
    geom_vline(xintercept=0, linetype='dashed') +
    labs(x="Weekly exercise duration (minute)", y="") + 
    coord_cartesian(ylim=c(1,2), xlim=c(-1, 8)) +
    geom_text(x=1.5, y=2, label='More exercise duration') +
    theme_Publication() +
    theme(
      legend.text = element_text(size = 12),
      legend.key.size= unit(0.8, "cm"),
      legend.direction = "vertical",
      legend.position = c(0.9, 0.9),
      axis.line.y = element_blank(),
      axis.ticks.y = element_blank(),
      axis.text.y = element_blank(),
      axis.title.y = element_blank(),
    )
  temp_1

  temp_2 = ggplot(dta_unit, aes(y=Social)) +
    geom_text(mapping=aes(x=0, label = Social)) + 
    geom_text(mapping=aes(x=0.5, label = unit)) +
    geom_text(x=0, y=2, label="Social factor", fontface='bold')+
    geom_text(x=0.5, y=2, label="Unit", fontface='bold')+
    theme_void() + 
    coord_cartesian(xlim=c(-0.2, 1), ylim=c(1,2))
  temp_2
  
  layout = c(
    area(t=0, l=0, b=30, r=4),
    area(t=1, l=4, b=30, r=9)
  )
  
  fig_social_forestplot = temp_2 + temp_1 + plot_layout(design=layout) 
  fig_social_forestplot 
}
fig_social_forestplot = generate_social_plot()
fig_social_forestplot

# Personal habit
generate_habit_plot = function(){
  
  dta_stat = data.frame(
    c("1 week lag duration", "2 week lag duration", '3 week lag duration'),

    c(wtd.mean(dta2$DURATION_1, dta2$unique_user),
      wtd.mean(dta2$DURATION_2, dta2$unique_user),
      wtd.mean(dta2$DURATION_3, dta2$unique_user)),
    c(wtd.var(dta2$DURATION_1, dta2$unique_user),
      wtd.var(dta2$DURATION_2, dta2$unique_user),
      wtd.var(dta2$DURATION_3, dta2$unique_user))
  )
  write.csv(dta_stat, paste0(DIR_PIPELINE, "\\out\\historical_info.csv"))
  
  dta_unit = data.frame(
    c("1 week lag duration", "2 week lag duration", '3 week lag duration'),
    c("minute",'minute','minute')
  )
  colnames(dta_stat) = c('Habit', 'average', 'std')
  colnames(dta_unit) = c('Habit', 'unit')
  
  temp_1 = ggplot(dta_stat, aes(y=fct_rev(Habit))) +
    geom_point(mapping=aes(x=average), shape=15, size=3) + 
    geom_linerange(mapping=aes(xmin=average-std, xmax=average+std)) +
    geom_vline(xintercept=0, linetype='dashed') +
    labs(x="Weekly exercise duration (minute)", y="") + 
    coord_cartesian(ylim=c(1,4), xlim=c(-0.5, 1)) +
    geom_text(x=0.3, y=4, label='More exercise duration') +
    theme_Publication() +
    theme(
      legend.text = element_text(size = 12),
      legend.key.size= unit(0.8, "cm"),
      legend.direction = "vertical",
      legend.position = c(0.9, 0.9),
      axis.line.y = element_blank(),
      axis.ticks.y = element_blank(),
      axis.text.y = element_blank(),
      axis.title.y = element_blank(),
    )
  temp_1
  
  temp_2 = ggplot(dta_unit, aes(y=fct_rev(Habit))) +
    geom_text(mapping=aes(x=0, label = Habit)) + 
    geom_text(mapping=aes(x=0.5, label = unit)) +
    geom_text(x=0, y=4, label="Personal habit", fontface='bold')+
    geom_text(x=0.5, y=4, label="Unit", fontface='bold')+
    theme_void() + 
    coord_cartesian(xlim=c(-0.2, 1), ylim=c(1,4))
  temp_2
  
  layout = c(
    area(t=0, l=0, b=30, r=4),
    area(t=1, l=4, b=30, r=9)
  )
  
  fig_habit_forestplot = temp_2 + temp_1 + plot_layout(design=layout) 
  fig_habit_forestplot 
}
fig_habit_forestplot = generate_habit_plot()
fig_habit_forestplot

fig_general_forestplot = plot_grid(fig_weather_forestplot,
          fig_gender_forestplot,
          fig_social_forestplot,
          fig_habit_forestplot,
          nrow=4,
          ncol=1)
fig_general_forestplot

pdf(paste0(DIR_PIPELINE,'\\out\\figure_normal day determinants weighted.pdf'),width=10,height=12)
print(fig_general_forestplot)
dev.off()