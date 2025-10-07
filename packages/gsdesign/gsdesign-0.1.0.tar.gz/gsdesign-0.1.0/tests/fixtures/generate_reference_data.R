options(digits = 16, scipen = 999)

suppressPackageStartupMessages(library(gsDesign2))

output_dir <- "tests/fixtures"
dir.create(output_dir, showWarnings = FALSE, recursive = TRUE)

write_matrix <- function(mat, filename) {
  path <- file.path(output_dir, filename)
  write.table(
    mat,
    file = path,
    row.names = FALSE,
    col.names = FALSE,
    quote = FALSE
  )
}

g <- gsDesign2:::gridpts(r = 5, mu = 0.5, a = -2, b = 2)
write_matrix(
  cbind(g$z, g$w),
  "gridpts_r5_mu0.5_a-2_b2.txt"
)

h1_ref <- gsDesign2:::h1(r = 5, theta = 0.5, info = 2, a = -2, b = 2)
write_matrix(
  cbind(h1_ref$z, h1_ref$w, h1_ref$h),
  "h1_r5_theta0.5_info2_a-2_b2.txt"
)

gm1 <- gsDesign2:::h1(r = 5, theta = 0.3, info = 1.5, a = -2, b = 2)
hupdate_ref <- gsDesign2:::hupdate(
  r = 5,
  theta = 0.5,
  info = 2.5,
  a = -2,
  b = 2,
  thetam1 = 0.3,
  im1 = 1.5,
  gm1 = gm1
)
write_matrix(
  cbind(hupdate_ref$z, hupdate_ref$w, hupdate_ref$h),
  "hupdate_r5_theta0.5_info2.5_thetaprev0.3_infoprev1.5_a-2_b2.txt"
)
