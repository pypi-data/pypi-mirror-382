# This script receives basic types from Python
cat("Received from Python:\n")
cat("  name:", name, "\n")
cat("  age:", age, "\n")
cat("  is_student:", is_student, "\n")
cat("  scores:", scores, "\n")

# Do some processing
result <- mean(scores)
message <- paste("Hello", name, "- average score:", round(result, 2))
