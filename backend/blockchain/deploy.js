import { ethers } from "ethers";
import fs from "fs";
import path from "path";
import dotenv from "dotenv";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.join(__dirname, "..", ".env") });

async function deployContract() {
  try {
    console.log("🚀 Starting contract deployment...");

    // Setup provider and wallet
    const provider = new ethers.JsonRpcProvider(
      process.env.BLOCKCHAIN_PROVIDER_URL
    );
    const wallet = new ethers.Wallet(
      process.env.BLOCKCHAIN_PRIVATE_KEY,
      provider
    );

    console.log(`📍 Deploying from address: ${wallet.address}`);
    console.log(`🌐 Network: ${process.env.BLOCKCHAIN_NETWORK_ID}`);

    // Check balance
    const balance = await provider.getBalance(wallet.address);
    console.log(`💰 Account balance: ${ethers.formatEther(balance)} ETH`);

    if (balance === 0n) {
      throw new Error("❌ Account has no ETH for deployment");
    }

    // Read compiled contract from Hardhat artifacts
    const contractPath = path.join(
      __dirname,
      "artifacts",
      "contracts",
      "DomainReputation.sol",
      "DomainClassification.json"
    );

    if (!fs.existsSync(contractPath)) {
      throw new Error("❌ Contract not compiled. Run 'npm run compile' first");
    }

    const contractArtifact = JSON.parse(fs.readFileSync(contractPath, "utf8"));
    const contractABI = contractArtifact.abi;
    const contractBytecode = contractArtifact.bytecode;

    // Deploy contract
    const contractFactory = new ethers.ContractFactory(
      contractABI,
      contractBytecode,
      wallet
    );

    console.log("🚀 Deploying contract...");
    const contract = await contractFactory.deploy();

    console.log("⏳ Waiting for deployment...");
    await contract.waitForDeployment();

    const contractAddress = await contract.getAddress();

    console.log(`✅ Contract deployed at: ${contractAddress}`);

    return {
      success: true,
      contractAddress: contractAddress,
    };
  } catch (error) {
    console.error("❌ Deployment failed:", error.message);
    return {
      success: false,
      error: error.message,
    };
  }
}

// Check if this file is being run directly
const isMainModule = process.argv[1] === fileURLToPath(import.meta.url);

if (isMainModule) {
  console.log("🔧 Deploy script starting...");
  deployContract()
    .then((result) => {
      if (result.success) {
        console.log("✅ Deployment completed successfully!");
        console.log(`📄 Contract address: ${result.contractAddress}`);
      } else {
        console.log(
          "⚠️  Deployment not completed:",
          result.message || result.error
        );
      }
      process.exit(0);
    })
    .catch((error) => {
      console.error("❌ Unexpected error:", error);
      process.exit(1);
    });
}

export { deployContract };
