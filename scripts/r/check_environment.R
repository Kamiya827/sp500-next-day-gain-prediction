packages <- c("readr", "dplyr", "ggplot2", "pROC")
for (pkg in packages) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    stop(sprintf("Missing R package: %s", pkg))
  }
}
cat("R environment OK\n")
