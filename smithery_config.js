function startServer(config) {
  return {
    command: "python",
    args: ["server.py"],
    env: {
      GEMINI_API_KEY: config.geminiApiKey,
    },
  };
}

module.exports = { startServer };
