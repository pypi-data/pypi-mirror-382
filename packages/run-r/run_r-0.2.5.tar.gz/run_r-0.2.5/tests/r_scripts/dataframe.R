# This script receives a dataframe from Python
cat("Received dataframe with dimensions:", nrow(sales_data), "x", ncol(sales_data), "\n")
cat("Columns:", paste(names(sales_data), collapse=", "), "\n")

# Perform analysis
total_revenue <- sum(sales_data$amount)
avg_amount <- mean(sales_data$amount)
top_product <- sales_data$product[which.max(sales_data$amount)]

# Create a summary
summary_stats <- data.frame(
  metric = c("Total Revenue", "Average Amount", "Top Product"),
  value = c(total_revenue, avg_amount, top_product)
)
