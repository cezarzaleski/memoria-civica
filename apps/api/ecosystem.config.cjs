module.exports = {
  apps: [
    {
      args: "run api:start",
      cwd: "/opt/memoria-civica",
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
