# Load required package
if (!require("lme4", quietly = TRUE)) {
  install.packages("lme4", repos = "https://cran.r-project.org")
  library(lme4)
}

cat("Fitting generalized linear mixed-effects model...\n")
cat("Data dimensions:", nrow(study_data), "x", ncol(study_data), "\n")

# Fit a logistic regression with random effects
model <- glmer(
  response ~ predictor + (1 | subject_id),
  data = study_data,
  family = binomial(link = "logit"),
  control = glmerControl(optimizer = "bobyqa")
)

# Print model summary
print(summary(model))

# Extract model components as dataframes/lists for Python
fixed_effects <- data.frame(
  term = names(fixef(model)),
  estimate = fixef(model),
  row.names = NULL
)

random_effects <- as.data.frame(ranef(model)$subject_id)
random_effects$subject_id <- rownames(ranef(model)$subject_id)

# Model statistics
fit_stats <- data.frame(
  metric = c("AIC", "BIC", "logLik", "deviance"),
  value = c(AIC(model), BIC(model), as.numeric(logLik(model)), deviance(model))
)

cat("\nModel fitted successfully!\n")
