## Eden Forbes 
## April 2026
## Sculpin trawl data processing

library(readxl)
library(dplyr)
library(tidyr)
library(scales)
library(ggplot2)
library(ggh4x)
library(patchwork)

###########################
## FUNCTIONS & CONSTANTS ##
###########################

### FORAGING CONSTANTS
## 0-500 benthic inverts /m^2 ; Knight et al. 2018
## 0-1000 Mysis /m^2 ; O'Malley et al. 2018
hrs_active = 12 ## Hours per day of foraging activity; 
srad = 48 ## strike radius (mm); this study
pursue = 0.5 ## percent of encounters pursued


### TRAWL CONSTANTS
footrope = 9.3 ## width of trawl (m); Wilkins and Marsden 2021
velo = 91.67 ## trawl velocity (m/min); Wilkins and Marsden 2021
## Velo translated from 5.5 km/hr (*1000, /60) to work with trawl durations


## GLM fits ##
# Movement distance
zM <- function(size) {
  return (19.336 + 0.1616*size)
}
# Movement duration
sM <- function(size){
  return (0.5375 + 0.0009*size)
} 
# Rest duration
sR <- function(size){
  return (6.3906 + 0.0368*size)
}

## Encounter rates ##
AINT <- function(size, drad){
  return (2*drad^2*acos(zM(size)/(2*drad))-(zM(size)/2 * sqrt(4*drad^2 - zM(size)^2)))
}

ER <- function(size, prey, drad) {
  return (prey*((pi*drad^2)-AINT(size, drad))/(sM(size)+sR(size)))
}

## Foraging pressure ##

T2 <- function(size, prey, drad, cap){
  return (cap * (pursue * ER(size, prey, drad))/(1 + pursue * ER(size, prey, drad) * (sM(size)+2*sR(size))))
}

#####################
## DATA PROCESSING ##
#####################

trawls <- na.omit(read_excel('Slimy Sculpin.xlsx'))
trawls <- trawls %>%
  mutate(FP00001SB = T2(tl_mm, 0.00001, 130, 0.8)) %>%
  mutate(FP00005SB = T2(tl_mm, 0.00005, 130, 0.8)) %>%
  mutate(FP0001SB = T2(tl_mm, 0.0001, 130, 0.8)) %>%
  mutate(FP00015SB = T2(tl_mm, 0.00015, 130, 0.8)) %>%
  mutate(FP0002SB = T2(tl_mm, 0.0002, 130, 0.8)) %>%
  mutate(FP00025SB = T2(tl_mm, 0.00025, 130, 0.8)) %>%
  mutate(FP0003SB = T2(tl_mm, 0.0003, 130, 0.8)) %>%
  mutate(FP00035SB = T2(tl_mm, 0.00035, 130, 0.8)) %>%
  mutate(FP0004SB = T2(tl_mm, 0.0004, 130, 0.8)) %>%
  mutate(FP00045SB = T2(tl_mm, 0.00045, 130, 0.8)) %>%
  mutate(FP0005SB = T2(tl_mm, 0.0005, 130, 0.8)) %>%
  
  mutate(FP00001SM = T2(tl_mm, 0.00001, 130, 0.1)) %>% 
  mutate(FP0001SM = T2(tl_mm, 0.0001, 130, 0.1)) %>% 
  mutate(FP0002SM = T2(tl_mm, 0.0002, 130, 0.1)) %>% 
  mutate(FP0003SM = T2(tl_mm, 0.0003, 130, 0.1)) %>% 
  mutate(FP0004SM = T2(tl_mm, 0.0004, 130, 0.1)) %>% 
  mutate(FP0005SM = T2(tl_mm, 0.0005, 130, 0.1)) %>% 
  mutate(FP0006SM = T2(tl_mm, 0.0006, 130, 0.1)) %>% 
  mutate(FP0007SM = T2(tl_mm, 0.0007, 130, 0.1)) %>% 
  mutate(FP0008SM = T2(tl_mm, 0.0008, 130, 0.1)) %>% 
  mutate(FP0009SM = T2(tl_mm, 0.0009, 130, 0.1)) %>% 
  mutate(FP001SM = T2(tl_mm, 0.001, 130, 0.1)) 
  


trawls_by_sample <- trawls %>%
  group_by(sampleID) %>%
  mutate(area = duration_min*velo*footrope) %>% ## in m^2
  summarize(n = n(), duration = mean(duration_min), area = mean(area), ## means here are meaningless
            depth_start_m = mean(depth_start_m), ## and here, just for convenience
            FP00001SB = sum(FP00001SB), 
            FP00005SB = sum(FP00005SB),
            FP0001SB = sum(FP0001SB), 
            FP00015SB = sum(FP00015SB),
            FP0002SB = sum(FP0002SB),
            FP00025SB = sum(FP00025SB),
            FP0003SB = sum(FP0003SB), 
            FP00035SB = sum(FP00035SB), 
            FP0004SB = sum(FP0004SB),
            FP00045SB = sum(FP00045SB), 
            FP0005SB = sum(FP0005SB), 
            
            FP00001SM = sum(FP00001SM), 
            FP0001SM = sum(FP0001SM), 
            FP0002SM = sum(FP0002SM), 
            FP0003SM = sum(FP0003SM), 
            FP0004SM = sum(FP0004SM), 
            FP0005SM = sum(FP0005SM),
            FP0006SM = sum(FP0006SM), 
            FP0007SM = sum(FP0007SM), 
            FP0008SM = sum(FP0008SM), 
            FP0009SM = sum(FP0009SM), 
            FP001SM = sum(FP001SM)) %>%
  mutate(depth_bin = cut(depth_start_m, breaks = c(0, 30, 50, 70, 90, 100), 
                         labels = c("Depth: 0-30m", "Depth: 30-50m", "Depth: 50-70m", "Depth: 70-90m","Depth: 90-110m+"), 
                         include.lowest = TRUE)) 

trawls_by_depth <- trawls_by_sample %>%
  group_by(depth_bin) %>%
  summarize(n = sum(n), ## total sculpin sampled at depth
            total_duration = sum(duration), ## total duration of trawls at depth
            total_area = sum(area), ## total area of trawls at depth, in m2
            density = sum(n)/sum(area), ## sculpin density at depth (#/m2)
            FP00001SB = sum(FP00001SB), ## Population foraging pressure (#/s)
            FP00005SB = sum(FP00005SB), 
            FP0001SB = sum(FP0001SB), 
            FP00015SB = sum(FP00015SB), 
            FP0002SB = sum(FP0002SB), 
            FP00025SB = sum(FP00025SB), 
            FP0003SB = sum(FP0003SB), 
            FP00035SB = sum(FP00035SB), 
            FP0004SB = sum(FP0004SB), 
            FP00045SB = sum(FP00045SB), 
            FP0005SB = sum(FP0005SB), 
            FP00001SM = sum(FP00001SM), 
            FP0001SM = sum(FP0001SM), 
            FP0002SM = sum(FP0002SM), 
            FP0003SM = sum(FP0003SM), 
            FP0004SM = sum(FP0004SM), 
            FP0005SM = sum(FP0005SM),
            FP0006SM = sum(FP0006SM), 
            FP0007SM = sum(FP0007SM), 
            FP0008SM = sum(FP0008SM), 
            FP0009SM = sum(FP0009SM), 
            FP001SM = sum(FP001SM))

foraging_pressure <- data.frame( ## Converted to #/km/day
  column1 = 60*60*hrs_active* trawls_by_depth$FP00001SB / trawls_by_depth$total_area,
  column2 = 60*60*hrs_active* trawls_by_depth$FP00005SB / trawls_by_depth$total_area,
  column3 = 60*60*hrs_active* trawls_by_depth$FP0001SB / trawls_by_depth$total_area,
  column4 = 60*60*hrs_active* trawls_by_depth$FP00015SB / trawls_by_depth$total_area,
  column5 = 60*60*hrs_active* trawls_by_depth$FP0002SB / trawls_by_depth$total_area,
  column6 = 60*60*hrs_active* trawls_by_depth$FP00025SB / trawls_by_depth$total_area,
  column7 = 60*60*hrs_active* trawls_by_depth$FP0003SB / trawls_by_depth$total_area,
  column8 = 60*60*hrs_active* trawls_by_depth$FP00035SB / trawls_by_depth$total_area,
  column9 = 60*60*hrs_active* trawls_by_depth$FP0004SB / trawls_by_depth$total_area,
  column10 = 60*60*hrs_active* trawls_by_depth$FP00045SB / trawls_by_depth$total_area,
  column11 = 60*60*hrs_active* trawls_by_depth$FP0005SB / trawls_by_depth$total_area,
  column12 = 60*60*hrs_active* trawls_by_depth$FP00001SM / trawls_by_depth$total_area,
  column13 = 60*60*hrs_active* trawls_by_depth$FP0001SM / trawls_by_depth$total_area,
  column14 = 60*60*hrs_active* trawls_by_depth$FP0002SM / trawls_by_depth$total_area,
  column15 = 60*60*hrs_active* trawls_by_depth$FP0003SM / trawls_by_depth$total_area,
  column16 = 60*60*hrs_active* trawls_by_depth$FP0004SM / trawls_by_depth$total_area,
  column17 = 60*60*hrs_active* trawls_by_depth$FP0005SM / trawls_by_depth$total_area,
  column18 = 60*60*hrs_active* trawls_by_depth$FP0006SM / trawls_by_depth$total_area,
  column19 = 60*60*hrs_active* trawls_by_depth$FP0007SM / trawls_by_depth$total_area,
  column20 = 60*60*hrs_active* trawls_by_depth$FP0008SM / trawls_by_depth$total_area,
  column21 = 60*60*hrs_active* trawls_by_depth$FP0009SM / trawls_by_depth$total_area,
  column22 = 60*60*hrs_active* trawls_by_depth$FP001SM / trawls_by_depth$total_area
)

foraging_pressure <- rbind(cap = c(0.8, 0.8, 0.8, 0.8, 
                                   0.8, 0.8, 0.8, 0.8, 
                                   0.8, 0.8, 0.8, 
                                   0.1, 0.1, 0.1, 0.1, 
                                   0.1, 0.1, 0.1, 0.1,  
                                   0.1, 0.1, 0.1), foraging_pressure)


foraging_pressure <- rbind(density = c(10, 50, 100, 150, 200,
                                       250, 300, 350, 400, 450, 500,
                                       10, 100, 200, 300, 400, 500, 
                                       600, 700, 800, 900, 1000), foraging_pressure)

foraging_pressure <- as.data.frame(t(foraging_pressure))
colnames(foraging_pressure) <- c("PDensity", "Capture", "Depth1", "Depth2", "Depth3", "Depth4", "Depth5")


##############
## PLOTTING ##
##############

## Body size distribution (by depth)
trawls_depth_bin <- trawls %>%
  mutate(depth_bin = cut(depth_start_m, breaks = c(0, 30, 50, 70, 90, 100), 
                         labels = c("Depth: 0-30m", "Depth: 30-50m", "Depth: 50-70m", "Depth: 70-90m","Depth: 90m+"), 
                         include.lowest = TRUE))

ggplot(trawls_depth_bin, aes(x = tl_mm, fill = depth_bin)) +
  geom_histogram(alpha = 1, bins = 30, color = "black", fill="gray") +
  facet_wrap(~ depth_bin, ncol = 1, axes='all') +
  coord_fixed(ratio = 0.1) +
  theme_classic() +
  theme(strip.text.x = element_blank())


## Foraging (by depth, prey density)

foraging_pressure_plot <- foraging_pressure %>%
  select(PDensity, Capture, Depth2, Depth3, Depth4, Depth5) %>%
  pivot_longer(cols = c(-PDensity,-Capture), names_to = "name", values_to = "value") %>%
  mutate(Capture= cut(Capture, breaks = c(0, 0.5, 1.0), 
                         labels = c("Mysis", "Other"), 
                         include.lowest = TRUE))


Mys <- foraging_pressure_plot %>%
  filter(Capture == "Mysis")
    
Mysplot <- ggplot(Mys, aes(x = PDensity, y = value)) +
  geom_point() +
  geom_line() +
  scale_color_manual(values = c("#1F449C", "#F05039")) +
  facet_wrap(~ name,ncol=1, axes="all") +
  theme_classic() +
  theme(strip.text = element_blank(),
        axis.title = element_blank(),
        legend.position = "none") +
  coord_fixed(ratio=11)


Other <- foraging_pressure_plot %>%
  filter(Capture == "Other")

Otherplot <- ggplot(Other, aes(x = PDensity, y = value)) +
  geom_point() +
  geom_line() +
  scale_color_manual(values = c("#1F449C", "#F05039")) +
  facet_wrap(~ name,ncol=1, axes="all") +
  theme_classic() +
  theme(strip.text = element_blank(),
        axis.title = element_blank(),
        legend.position = "none") +
  coord_fixed(ratio=8)

Otherplot*Mysplot

