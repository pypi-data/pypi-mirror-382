# Process numpy arrays in R
cat("Array dimensions:\n")
cat("  vector length:", length(vector), "\n")
cat("  matrix elements:", length(matrix), "\n")

# Calculate statistics
mean_vector <- mean(vector, na.rm = TRUE)
sum_matrix <- sum(matrix, na.rm = TRUE)
max_vector <- max(vector, na.rm = TRUE)

# Create processed array
squared <- vector^2
