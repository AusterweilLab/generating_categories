data {  
  real<lower=1> nu; // hyperprior on IW
  int<lower=0> nk; // number of categories
  int<lower=0> nx[nk]; // number of exemplars per category
  int<lower=0> nxs;
  int<lower=0> ndim; // number of dimensions
  matrix[ndim, ndim] sigma_0; // Sigma_0 hyperprior on IW  
  vector[ndim] mu_0; //mu hyperprior on mvnormal
  vector[ndim] x[nxs];
}
transformed data {
}
parameters {
  //cov_matrix[ndim,ndim] sigma_0;
  //vector[ndim] mu_0;
  cov_matrix[ndim] sigma[nk]; //sigma is a nk-by-nk symmetric positive definite matrix  
  vector[ndim] mu[nk];
}
transformed parameters {}
model {
  //Initiate starting position of observed values
  int pos;
  pos = 1;
  for (nki in 1:nk) {
	sigma[nki] ~ inv_wishart(nu, sigma_0);
	mu[nki] ~ multi_normal(mu_0,sigma[nki]);
	segment(x,pos,nx[nki]) ~ multi_normal(mu[nki],sigma[nki]);
	pos = pos+nx[nki];
	/* for (nxi in 1:nx[nki]){	   */
	/*   x[nxi,nki] ~ multi_normal(mu[nki],sigma[nki]); */
	/* } */
  }
}
generated quantities {}


