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
library(showtext)
library(stringi)
library(patchwork)
library(cowplot)
library(Hmisc)

# ------------------------
# import sources
# ------------------------
source("1_code/0_common/theme_figure.R")
font_add("Arial","/Library/Fonts/Arial.ttf")
showtext_auto()

# ------------------------
# read data
# ------------------------
dta_result = read.csv(paste0(DIR_PIPELINE, '/store/city with interaction coef 3.csv'), encoding = 'UTF-8')
dta_result2 = read.csv(paste0(DIR_PIPELINE, '/store/city no interaction coef 5.csv'), encoding = 'UTF-8')
dta_info = read.csv(paste0(DIR_HOME, '/2_pipeline/110_aggregate data/out/all admin 2 info.csv'), encoding = 'UTF-8')
dta_info2 = read.csv(paste0(DIR_PIPELINE, '/store/large country experiment user list all countries 1000.csv'), encoding = 'UTF-8')

dta_info2_processed = dta_info2 %>%
  group_by(NAME_0, NAME_1, NAME_2) %>%
  summarise(unique_user = length(user_id))


# ------------------------
# process data
# ------------------------
dta_result$NAME_0 = stri_unescape_unicode(gsub("<U\\+(....)>", "\\\\u\\1", dta_result$NAME_0))
dta_result$NAME_1 = stri_unescape_unicode(gsub("<U\\+(....)>", "\\\\u\\1", dta_result$NAME_1))
dta_result$NAME_2 = stri_unescape_unicode(gsub("<U\\+(....)>", "\\\\u\\1", dta_result$NAME_2))
dta_result2$NAME_0 = stri_unescape_unicode(gsub("<U\\+(....)>", "\\\\u\\1", dta_result2$NAME_0))
dta_result2$NAME_1 = stri_unescape_unicode(gsub("<U\\+(....)>", "\\\\u\\1", dta_result2$NAME_1))
dta_result2$NAME_2 = stri_unescape_unicode(gsub("<U\\+(....)>", "\\\\u\\1", dta_result2$NAME_2))

dta_result = left_join(dta_result, dta_info)
dta_result2 = left_join(dta_result2, dta_info)
dta_result2 = left_join(dta_result2, dta_info2_processed)

dta_data = dta_result %>%
  select(NAME_0, NAME_1, NAME_2, user_gender, user_gender.IS_COVID_START, user_gender.POLICY, LG_FOLLOW, LG_FOLLOW.IS_COVID_START, LG_FOLLOW.POLICY,
         centroid_lat, pop_den, green_space_share, nighttime_light_avg, sport_area_share, sport_num_share)
dta_data2 = dta_result2 %>%
  select(NAME_0, NAME_1, NAME_2, POLICY2, IS_COVID_START, unique_user)


dta_data$user_gender_during_covid = dta_data$user_gender + dta_data$user_gender.IS_COVID_START
dta_data$LG_FOLLOW_during_covid = dta_data$LG_FOLLOW + dta_data$LG_FOLLOW.IS_COVID_START
dta_data$sport_amenity_density = dta_data$sport_num_share

# ------------------------
# Gender
# ------------------------

# Figure
generate_gender_figure = function(){
  colors = c("Before COVID-19"=col.light_blue,
             "During COVID-19"=col.green)
  
  fig = ggplot(dta_data) +
    geom_density(aes(x=user_gender, fill="Before COVID-19"), alpha=0.2) +
    geom_density(aes(x=user_gender_during_covid, fill="During COVID-19"), alpha=0.2) +
    geom_vline(xintercept = 0, linetype="dashed", color="red", size=1) +
    geom_text(x=4,y=0.23,label="Female exercise more",size=6)+
    geom_text(x=-4,y=0.23,label="Male exercise more", size=6)+
    xlab("Weekly exercise duration (minute)")+
    ylab("Frequency")+
    labs(fill="Period")+
    scale_fill_manual(values=colors)+
    theme_Publication() +
    # guides(color= guide_legend(nrow = 1, byrow = TRUE))+
    theme(
      legend.title = element_text("Period"),
      legend.text = element_text(size = 12),
      legend.key.size= unit(0.4, "cm"),
      legend.direction = "vertical",
      # legend.position = "none"
      plot.margin=unit(c(1,1,1.5,0.5), "cm"),
      legend.position = c(0.85, 0.85),
      axis.text = element_text(size = 18),
      axis.title = element_text(size = 22)
    )
  
  fig
}

gender_fig = generate_gender_figure()

pdf(paste0(DIR_PIPELINE, "\\out\\figure_gender difference in covid.pdf"), width=16, height=9)
print(gender_fig)
dev.off()