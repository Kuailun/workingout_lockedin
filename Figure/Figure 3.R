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
dta_result1 = read.csv(paste0(DIR_PIPELINE, '/store/city no interaction coef 5.csv'), encoding = 'UTF-8')
dta_result2 = read.csv(paste0(DIR_PIPELINE, '/store/city discontinuity.csv'), encoding = 'UTF-8')
dta_info = read.csv(paste0(DIR_HOME, '/2_pipeline/110_aggregate data/out/all admin 2 info_split.csv'), encoding = 'UTF-8')


# ------------------------
# process data
# ------------------------
dta_result1$NAME_0 = stri_unescape_unicode(gsub("<U\\+(....)>", "\\\\u\\1", dta_result1$NAME_0))
dta_result1$NAME_1 = stri_unescape_unicode(gsub("<U\\+(....)>", "\\\\u\\1", dta_result1$NAME_1))
dta_result1$NAME_2 = stri_unescape_unicode(gsub("<U\\+(....)>", "\\\\u\\1", dta_result1$NAME_2))
dta_result2$NAME_0 = stri_unescape_unicode(gsub("<U\\+(....)>", "\\\\u\\1", dta_result2$NAME_0))
dta_result2$NAME_1 = stri_unescape_unicode(gsub("<U\\+(....)>", "\\\\u\\1", dta_result2$NAME_1))
dta_result2$NAME_2 = stri_unescape_unicode(gsub("<U\\+(....)>", "\\\\u\\1", dta_result2$NAME_2))


# ------------------------
# resul data
# ------------------------
dta_result1 = dta_result1 %>%
  select(NAME_0, NAME_1, NAME_2, IS_COVID_START, POLICY2) %>%
  rename(c("Long_term_effect"="IS_COVID_START", "Policy_effect"="POLICY2"))
dta_result2 = dta_result2 %>%
  select(NAME_0, NAME_1, NAME_2, IS_COVID_START) %>%
  rename(c("Short_term_effect"="IS_COVID_START"))

dta = left_join(dta_result1, dta_info)
dta = left_join(dta, dta_result2)


dta$sport_amenity_density = dta$sport_total_num_share
dta$fitness_num_share = dta$fitness_centre_num_share+dta$fitness_station_num_share
dta$fitness_area_share = dta$fitness_centre_area_share+dta$fitness_station_area_share
dta$sports_num_share = dta$sports_centre_num_share + dta$sports_hall_num_share
dta$sports_area_share = dta$sports_centre_area_share + dta$sports_hall_area_share

# Regression COVID-19 impact
long_term = lm(Long_term_effect ~ log(nighttime_light_avg+1) + log(sport_amenity_density+1) + log(pop_den), data=dta)
policy_term = lm(Policy_effect ~ log(nighttime_light_avg+1) + log(sport_amenity_density+1) + log(pop_den), data=dta)
short_term = lm(Short_term_effect ~ log(nighttime_light_avg+1) + log(sport_amenity_density+1) + log(pop_den), data=dta)
mean(dta$Policy_effect, na.rm=T)
stargazer(short_term, policy_term,long_term,  type='text')

s = dta %>%
  group_by(NAME_0) %>%
  count()

# Draw exercise amenities forest plot
long_term_area_share = lm(Long_term_effect ~
                            log(nighttime_light_avg+1) + 
                            log(pop_den) + 
                            log(sports_area_share+1)+
                            log(stadium_area_share+1) +
                            log(track_area_share+1) +
                            log(pitch_area_share+1) +
                            log(swimming_pool_area_share+1) +
                            log(fitness_area_share+1)+
                            log(park_area_share+1), 
                          data=dta)
temp = summary(long_term_area_share)
dta_long_term = data.frame(
  c('gdp','population_density','sports_center','stadium','track','pitch','swimming_pool','fitness_center','park'),
  coef(long_term_area_share)[2:10],
  temp$coefficients[,"Std. Error"][2:10]
)
colnames(dta_long_term) = c("amenity_type","average","std")
dta_long_term$period = "long term"

short_term_area_share = lm(Short_term_effect ~
                             log(nighttime_light_avg+1) + 
                             log(pop_den) + 
                             log(sports_area_share+1)+
                             log(stadium_area_share+1) +
                             log(track_area_share+1) +
                             log(pitch_area_share+1) +
                             log(swimming_pool_area_share+1) +
                             log(fitness_area_share+1)+
                             log(park_area_share+1),
                           data=dta)
temp = summary(short_term_area_share)
dta_short_term = data.frame(
  c('gdp','population_density','sports_center','stadium','track','pitch','swimming_pool','fitness_center','park'),
  coef(short_term_area_share)[2:10],
  temp$coefficients[,"Std. Error"][2:10]
)
colnames(dta_short_term) = c("amenity_type","average","std")
dta_short_term$period = "short term"

policy_area_share = lm(Policy_effect ~
                         log(nighttime_light_avg+1) + 
                         log(pop_den) + 
                         log(sports_area_share+1)+
                         log(stadium_area_share+1) +
                         log(track_area_share+1) +
                         log(pitch_area_share+1) +
                         log(swimming_pool_area_share+1) +
                         log(fitness_area_share+1)+
                         log(park_area_share+1), 
                       data=dta)
temp = summary(policy_area_share)
dta_policy_term = data.frame(
  c('gdp','population_density','sports_center','stadium','track','pitch','swimming_pool','fitness_center','park'),
  coef(policy_area_share)[2:10],
  temp$coefficients[,"Std. Error"][2:10]
)
colnames(dta_policy_term) = c("amenity_type","average","std")
dta_policy_term$period = "lockdown"
dta_result = rbind(dta_short_term, dta_policy_term)
dta_result = rbind(dta_result, dta_long_term)
stargazer(short_term_area_share, policy_area_share,long_term_area_share,  type='text')

dta_result$period = factor(dta_result$period, levels = c("short term","lockdown","long term"))

dta_display = subset(dta_result, !amenity_type %in% c("gdp","population_density"))
temp_1 = ggplot(dta_display, aes(y=amenity_type)) +
  geom_point(mapping=aes(x=average, color=period, group=period), shape=15, size=3,position = position_dodge(width = 0.3)) + 
  geom_linerange(mapping=aes(xmin=average-std, xmax=average+std, color=period, group=period),position=position_dodge(width=0.3)) +
  geom_vline(xintercept=0, linetype='dashed') +
  labs(x="Weekly exercise duration (minute)", y="") +
  geom_text(x=0.3, y=8, label='More exercise duration') +
  theme_Publication() +
  theme(
    legend.text = element_text(size = 15),
    legend.key.size= unit(0.8, "cm"),
    legend.direction = "vertical",
    legend.position = c(0.9, 0.9),
    axis.line.y = element_blank(),
    axis.ticks.y = element_blank(),
    axis.text.y = element_text(size=15),
    axis.title.y = element_blank(),
  )
temp_1


pdf(paste0(DIR_PIPELINE,'\\out\\figure_exercise amenity impact.pdf'),width=10,height=10)
print(temp_1)
dev.off()