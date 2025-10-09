require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config({ path: "../.env" });

module.exports = {
  solidity: "0.8.19",
  networks: {
    sepolia: {
      url: process.env.BLOCKCHAIN_PROVIDER_URL,
      accounts: [process.env.BLOCKCHAIN_PRIVATE_KEY],
    },
    localhost: {
      url: "http://127.0.0.1:8545",
    },
  },
  paths: {
    sources: "./contracts",
    artifacts: "./artifacts",
    cache: "./cache",
  },
};
