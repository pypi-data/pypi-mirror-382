# Filter data based on threshold
cat("Filtering data where value >=", threshold, "\n")
filtered_data <- data[data$value >= threshold, ]
cat("Rows after filtering:", nrow(filtered_data), "\n")

# Apply multiplier
filtered_data$adjusted <- filtered_data$value * multiplier

# Calculate statistics
mean_adjusted <- mean(filtered_data$adjusted)
total_adjusted <- sum(filtered_data$adjusted)

# Create result dataframe
result_df <- filtered_data
