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

# ------------------------
# import sources
# ------------------------
source("1_code/0_common/theme_figure.R")

# ------------------------
# read data
# ------------------------
dta = read.csv(paste0(DIR_PIPELINE, "\\store\\exercise type preference by gender.csv"))
dta$gender_during_covid = dta$user_gender.IS_COVID_START + dta$user_gender
dta$temp = dta$gender_during_covid / dta$user_gender
dta$gender_change_percentage = dta$temp * sign(dta$user_gender)

dta$gender_change_percentage_std = abs(dta$std_user_gender.IS_COVID_START / dta$user_gender)

temp_1 = ggplot(dta, aes(y=exercise_type)) +
  geom_point(mapping=aes(x=gender_change_percentage), shape=15, size=3) + 
  geom_linerange(mapping=aes(xmin=gender_change_percentage-gender_change_percentage_std, xmax=gender_change_percentage+gender_change_percentage_std)) +
  geom_vline(xintercept=0, linetype='dashed') +
  geom_vline(xintercept=-2, linetype='dashed', alpha=0.2) +
  geom_vline(xintercept=-1, linetype='dashed', alpha=0.2) +
  geom_vline(xintercept=1, linetype='dashed', alpha=0.2) +
  geom_vline(xintercept=2, linetype='dashed', alpha=0.2) +
  geom_vline(xintercept=3, linetype='dashed', alpha=0.2) +
  geom_vline(xintercept=4, linetype='dashed', alpha=0.2) +
  geom_vline(xintercept=5, linetype='dashed', alpha=0.2) +
  labs(x="Gender differences in exercise duration (benchmarked by normal days)", y="") + 
  coord_cartesian(ylim=c(0,12), xlim=c(-2.5, 5.5)) +
  geom_text(x=-1, y=12, label='Male preferred exercise', size=6) +
  geom_text(x=1, y=12, label='Female preferred exercise', size=6) +
  theme_Publication() +
  theme(
    # legend.title = element_text("Gender"),
    legend.text = element_text(size = 12),
    legend.key.size= unit(0.8, "cm"),
    legend.direction = "vertical",
    legend.position = c(0.9, 0.8),
    axis.line.y = element_blank(),
    axis.ticks.y = element_blank(),
    # axis.text.y = element_blank(),
    axis.title.y = element_blank(),
    # legend.position = "right"
    axis.text = element_text(size = 18),
    axis.title = element_text(size = 22)
  )
temp_1

pdf(paste0(DIR_PIPELINE,'\\out\\figure_gender differences.pdf'),width=16,height=9)
print(temp_1)
dev.off()