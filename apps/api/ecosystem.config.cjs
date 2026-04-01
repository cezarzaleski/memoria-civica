const deployPath = process.env.DEPLOY_PATH || "/opt/memoria-civica";

module.exports = {
  apps: [
    {
      args: "run api:start",
      cwd: `${deployPath}/current`,
      env: {
        HOST: "0.0.0.0",
        NODE_ENV: "production",
        PORT: "3000"
      },
      name: "memoria-civica-api",
      script: "npm",
      time: true
    }
  ]
};
