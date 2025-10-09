# example.R - Sample R script to demonstrate run_r plugin

# Scalar variables
x <- 42
pi_value <- 3.14159
name <- "Alice"
is_active <- TRUE

# Vectors
numbers <- c(1, 2, 3, 4, 5)
colors <- c("red", "green", "blue")

# Data frame
data <- data.frame(
    id = 1:5,
    value = c(10, 20, 30, 40, 50),
    label = c("A", "B", "C", "D", "E")
)

# List
my_list <- list(
    item1 = "hello",
    item2 = 123,
    item3 = c(1, 2, 3)
)

# Matrix
my_matrix <- matrix(1:12, nrow = 3, ncol = 4)

# Simple computation
result <- sum(numbers) * 2

# Print message (will show during execution)
print("R script executed successfully!")
