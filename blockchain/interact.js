import { ethers } from "ethers";
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load .env from parent directory
dotenv.config({ path: path.join(__dirname, "..", ".env") });

class DomainClassificationContract {
  constructor() {
    // Add debug logging
    console.log("🔧 Initializing contract...");
    console.log("📍 Contract Address:", process.env.CONTRACT_ADDRESS);
    console.log("🌐 Provider URL:", process.env.BLOCKCHAIN_PROVIDER_URL);
    console.log(
      "🔑 Private Key:",
      process.env.BLOCKCHAIN_PRIVATE_KEY ? "SET" : "NOT SET"
    );

    // Verify environment variables are loaded
    if (!process.env.CONTRACT_ADDRESS) {
      console.error("❌ CONTRACT_ADDRESS not found in environment variables");
      return;
    }

    if (!process.env.BLOCKCHAIN_PROVIDER_URL) {
      console.error(
        "❌ BLOCKCHAIN_PROVIDER_URL not found in environment variables"
      );
      return;
    }

    this.provider = new ethers.JsonRpcProvider(
      process.env.BLOCKCHAIN_PROVIDER_URL
    );
    this.wallet = new ethers.Wallet(
      process.env.BLOCKCHAIN_PRIVATE_KEY,
      this.provider
    );
    this.contractAddress = process.env.CONTRACT_ADDRESS;

    this.contractABI = [
      "function classifyDomain(string memory _domain, bool _isSpam, string memory _reason) external",
      "function getDomainClassification(string memory _domain) external view returns (bool exists, bool isSpam, uint256 timestamp, address reporter, string memory reason)",
      "function isDomainKnown(string memory _domain) external view returns (bool exists, bool isSpam)",
      "function getStats() external view returns (uint256, uint256)",
      "function canUserSubmit(address _user) external view returns (bool canSubmit, uint256 nextSubmissionTime)",
      "function submissionCooldown() external view returns (uint256)",
      "function lastSubmissionTime(address) external view returns (uint256)",
      "event DomainClassified(string indexed domain, bool isSpam, address indexed reporter, uint256 timestamp)",
    ];

    if (
      this.contractAddress &&
      this.contractAddress !== "your_deployed_contract_address_here"
    ) {
      this.contract = new ethers.Contract(
        this.contractAddress,
        this.contractABI,
        this.wallet
      );
      console.log("✅ Contract initialized successfully");
    } else {
      console.error("❌ Invalid contract address");
    }
  }

  async classifyDomain(domain, isSpam, reason = "") {
    try {
      if (!this.contract) {
        throw new Error(
          "Contract not initialized. Please set CONTRACT_ADDRESS in .env"
        );
      }

      console.log(
        `📝 Classifying domain: ${domain} as ${isSpam ? "SPAM" : "HAM"}`
      );

      const tx = await this.contract.classifyDomain(domain, isSpam, reason);
      console.log(`⏳ Transaction submitted: ${tx.hash}`);

      const receipt = await tx.wait();
      console.log(`✅ Transaction confirmed in block: ${receipt.blockNumber}`);

      return {
        success: true,
        txHash: tx.hash,
        blockNumber: receipt.blockNumber,
      };
    } catch (error) {
      console.error("❌ Classification failed:", error.message);
      return {
        success: false,
        error: error.message,
      };
    }
  }

  async getDomainClassification(domain) {
    try {
      if (!this.contract) {
        throw new Error("Contract not initialized");
      }

      console.log(`🔍 Querying domain: ${domain}`);

      const result = await this.contract.getDomainClassification(domain);

      if (result.exists) {
        console.log(`📊 Domain found:`);
        console.log(`   Classification: ${result.isSpam ? "SPAM" : "HAM"}`);
        console.log(
          `   Timestamp: ${new Date(
            Number(result.timestamp) * 1000
          ).toISOString()}`
        );
        console.log(`   Reporter: ${result.reporter}`);
        console.log(`   Reason: ${result.reason || "No reason provided"}`);
      } else {
        console.log(`❓ Domain not found in blockchain cache`);
      }

      return {
        exists: result.exists,
        isSpam: result.isSpam,
        timestamp: Number(result.timestamp),
        reporter: result.reporter,
        reason: result.reason,
      };
    } catch (error) {
      console.error("❌ Query failed:", error.message);
      return null;
    }
  }

  async isDomainKnown(domain) {
    try {
      if (!this.contract) {
        return { exists: false, isSpam: false };
      }

      const result = await this.contract.isDomainKnown(domain);
      return {
        exists: result.exists,
        isSpam: result.isSpam,
      };
    } catch (error) {
      console.error("❌ Domain check failed:", error.message);
      return { exists: false, isSpam: false };
    }
  }

  async getStats() {
    try {
      if (!this.contract) {
        throw new Error("Contract not initialized");
      }

      const stats = await this.contract.getStats();
      console.log(`📈 Contract Statistics:`);
      console.log(`   Total Domains: ${stats[0]}`);

      return {
        totalDomains: Number(stats[0]),
        totalSubmitters: Number(stats[1]),
      };
    } catch (error) {
      console.error("❌ Stats query failed:", error.message);
      return null;
    }
  }

  async canUserSubmit(userAddress = null) {
    try {
      if (!this.contract) {
        throw new Error("Contract not initialized");
      }

      const address = userAddress || this.wallet.address;
      const result = await this.contract.canUserSubmit(address);

      console.log(`🔒 Submission status for ${address}:`);
      console.log(`   Can submit: ${result.canSubmit}`);

      if (!result.canSubmit) {
        const nextTime = new Date(Number(result.nextSubmissionTime) * 1000);
        console.log(`   Next submission time: ${nextTime.toISOString()}`);
      }

      return {
        canSubmit: result.canSubmit,
        nextSubmissionTime: Number(result.nextSubmissionTime),
      };
    } catch (error) {
      console.error("❌ Submission check failed:", error.message);
      return null;
    }
  }

  async getCooldownInfo() {
    try {
      if (!this.contract) {
        throw new Error("Contract not initialized");
      }

      const cooldown = await this.contract.submissionCooldown();
      const lastSubmission = await this.contract.lastSubmissionTime(
        this.wallet.address
      );
      const now = Math.floor(Date.now() / 1000);
      const canSubmitTime = Number(lastSubmission) + Number(cooldown);
      const canSubmit = now >= canSubmitTime;

      console.log(`📊 Cooldown Information:`);
      console.log(`   Current cooldown: ${cooldown.toString()} seconds`);
      console.log(
        `   Last submission: ${new Date(
          Number(lastSubmission) * 1000
        ).toISOString()}`
      );
      console.log(`   Can submit: ${canSubmit}`);
      console.log(
        `   Next submission time: ${new Date(
          canSubmitTime * 1000
        ).toISOString()}`
      );

      return {
        cooldown: Number(cooldown),
        lastSubmission: Number(lastSubmission),
        canSubmit: canSubmit,
        nextSubmissionTime: canSubmitTime,
      };
    } catch (error) {
      console.error("❌ Cooldown check failed:", error.message);
      return null;
    }
  }

  async getDomainReputation(domain) {
    try {
      const classification = await this.getDomainClassification(domain);

      if (classification && classification.exists) {
        return {
          exists: true,
          reputation_score: classification.isSpam ? 10 : 90,
          consensus: classification.isSpam ? "spam" : "ham",
          spam_votes: classification.isSpam ? 1 : 0,
          ham_votes: classification.isSpam ? 0 : 1,
          total_reports: 1,
          timestamp: classification.timestamp,
          reporter: classification.reporter,
          reason: classification.reason,
        };
      } else {
        return {
          exists: false,
          reputation_score: 50,
          consensus: "unknown",
          spam_votes: 0,
          ham_votes: 0,
          total_reports: 0,
        };
      }
    } catch (error) {
      console.error("❌ Reputation query failed:", error.message);
      return { exists: false };
    }
  }
}

// Test functions
async function testContract() {
  console.log("🧪 Testing contract interactions...\n");

  const contract = new DomainClassificationContract();

  // Test domains
  const testDomains = [
    {
      domain: "phishing-site.com",
      isSpam: true,
      reason: "Known phishing domain",
    },
    {
      domain: "google.com",
      isSpam: false,
      reason: "Legitimate domain",
    },
    {
      domain: "suspicious-bank.net",
      isSpam: true,
      reason: "Suspicious banking site",
    },
  ];

  // Check if we can submit
  await contract.canUserSubmit();

  // Classify test domains
  for (const test of testDomains) {
    console.log(`\n--- Testing ${test.domain} ---`);

    // Check if already exists
    const existing = await contract.getDomainClassification(test.domain);

    if (!existing || !existing.exists) {
      // Classify domain
      await contract.classifyDomain(test.domain, test.isSpam, test.reason);

      // Wait a bit and query back
      setTimeout(async () => {
        await contract.getDomainClassification(test.domain);
      }, 2000);
    } else {
      console.log("Domain already classified");
    }
  }

  // Get stats
  setTimeout(async () => {
    console.log("\n--- Contract Statistics ---");
    await contract.getStats();
  }, 5000);
}

// CLI interface
console.log("🔍 Debug info:");
console.log("import.meta.url:", import.meta.url);
console.log("process.argv[1]:", process.argv[1]);
console.log("fileURLToPath(import.meta.url):", fileURLToPath(import.meta.url));

const args = process.argv.slice(2);
const contract = new DomainClassificationContract();

if (args.length === 0) {
  console.log("🔧 Contract Interaction Script");
  console.log("Usage:");
  console.log("  node interact.js test                       - Run test suite");
  console.log(
    "  node interact.js classify <domain> <spam>   - Classify domain (spam: true/false)"
  );
  console.log(
    "  node interact.js query <domain>             - Query domain classification"
  );
  console.log(
    "  node interact.js stats                      - Get contract statistics"
  );
  console.log(
    "  node interact.js check                      - Check if can submit"
  );
  console.log(
    "  node interact.js cooldown                   - Get cooldown information"
  );
  process.exit(0);
}

const command = args[0];

try {
  switch (command) {
    case "test":
      await testContract();
      break;

    case "classify":
      if (args.length < 3) {
        console.log(
          "Usage: node interact.js classify <domain> <true|false> [reason]"
        );
        process.exit(1);
      }
      await contract.classifyDomain(args[1], args[2] === "true", args[3] || "");
      break;

    case "query":
      if (args.length < 2) {
        console.log("Usage: node interact.js query <domain>");
        process.exit(1);
      }
      const result = await contract.getDomainClassification(args[1]);
      if (result && result.exists) {
        console.log(result.isSpam ? "SPAM" : "HAM");
      } else {
        console.log("UNKNOWN");
      }
      break;

    case "stats":
      await contract.getStats();
      break;

    case "check":
      await contract.canUserSubmit();
      break;

    case "cooldown":
      await contract.getCooldownInfo();
      break;

    default:
      console.log("Unknown command:", command);
      console.log(
        "Available commands: test, classify, store, query, reputation, stats, check, cooldown"
      );
      process.exit(1);
  }
} catch (error) {
  console.error("❌ Error executing command:", error.message);
  process.exit(1);
}

export { DomainClassificationContract };
