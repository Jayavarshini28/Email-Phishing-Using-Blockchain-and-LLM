// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title EmailClassification
 * @dev Simple blockchain cache for email sender classifications (spam/ham)
 * Acts as a distributed lookup table, not a consensus system
 * Stores classifications based on sender email address instead of domain
 */
contract DomainClassification {
    
    // Email sender classification record
    struct DomainRecord {
        string domain;          // Now stores sender email address
        bool isSpam;            // true = spam/phishing, false = ham/legitimate
        uint256 timestamp;      // When classification was stored
        address reporter;       // Who submitted this classification
        string reason;          // Optional reason for classification
        bool exists;            // Whether email exists in cache
    }
    
    // Events
    event DomainClassified(
        string indexed domain, 
        bool isSpam, 
        address indexed reporter,
        uint256 timestamp
    );
    
    event DomainUpdated(
        string indexed domain,
        bool oldClassification,
        bool newClassification,
        address indexed updater
    );
    
    // State variables
    mapping(string => DomainRecord) public domains;  // Maps sender email to classification
    mapping(address => uint256) public lastSubmissionTime;
    
    address public owner;
    uint256 public submissionCooldown =  0 ; // Prevent spam submissions
    uint256 public totalDomains = 0;
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    modifier canSubmit() {
        require(
            block.timestamp >= lastSubmissionTime[msg.sender] + submissionCooldown,
            "Submission cooldown active"
        );
        _;
    }
    
    constructor() {
        owner = msg.sender;
    }
    
    /**
     * @dev Store or update sender email classification
     * @param _domain Sender email address to classify
     * @param _isSpam true if spam/phishing, false if legitimate
     * @param _reason Optional reason for classification
     */
    function classifyDomain(
        string memory _domain,
        bool _isSpam,
        string memory _reason
    ) external canSubmit {
        require(bytes(_domain).length > 0, "Email address cannot be empty");
        
        bool isUpdate = domains[_domain].exists;
        bool oldClassification = domains[_domain].isSpam;
        
        // Store classification
        domains[_domain] = DomainRecord({
            domain: _domain,
            isSpam: _isSpam,
            timestamp: block.timestamp,
            reporter: msg.sender,
            reason: _reason,
            exists: true
        });
        
        lastSubmissionTime[msg.sender] = block.timestamp;
        
        if (!isUpdate) {
            totalDomains++;
            emit DomainClassified(_domain, _isSpam, msg.sender, block.timestamp);
        } else {
            emit DomainUpdated(_domain, oldClassification, _isSpam, msg.sender);
        }
    }
    
    /**
     * @dev Get sender email classification from cache
     * @param _domain Sender email to query
     * @return exists Whether sender email exists in cache
     * @return isSpam Classification (true = spam, false = ham)
     * @return timestamp When classification was stored
     * @return reporter Who submitted the classification
     * @return reason Reason for classification
     */
    function getDomainClassification(string memory _domain) 
        external view returns (
            bool exists,
            bool isSpam,
            uint256 timestamp,
            address reporter,
            string memory reason
        ) {
        
        DomainRecord memory record = domains[_domain];
        
        return (
            record.exists,
            record.isSpam,
            record.timestamp,
            record.reporter,
            record.reason
        );
    }
    
    /**
     * @dev Check if sender email exists in cache (lightweight query)
     * @param _domain Sender email to check
     * @return exists Whether sender email is cached
     * @return isSpam Classification if exists
     */
    function isDomainKnown(string memory _domain) 
        external view returns (bool exists, bool isSpam) {
        DomainRecord memory record = domains[_domain];
        return (record.exists, record.isSpam);
    }
    
    /**
     * @dev Get contract statistics
     * @return totalDomains Total number of cached sender emails
     * @return totalSubmitters Number of unique submitters
     */
    function getStats() external view returns (uint256, uint256) {
        // Note: totalSubmitters would require additional tracking
        return (totalDomains, 0);
    }
    
    /**
     * @dev Check if user can submit (not in cooldown)
     * @param _user User address to check
     * @return canSubmit Whether user can submit now
     * @return nextSubmissionTime When user can submit again
     */
    function canUserSubmit(address _user) 
        external view returns (bool canSubmit, uint256 nextSubmissionTime) {
        uint256 nextTime = lastSubmissionTime[_user] + submissionCooldown;
        return (block.timestamp >= nextTime, nextTime);
    }
    
    /**
     * @dev Owner function to update submission cooldown
     * @param _newCooldown New cooldown period in seconds
     */
    function updateSubmissionCooldown(uint256 _newCooldown) external onlyOwner {
        submissionCooldown = _newCooldown;
    }
    
    /**
     * @dev Owner function to remove a sender email (if needed)
     * @param _domain Sender email to remove
     */
    function removeDomain(string memory _domain) external onlyOwner {
        require(domains[_domain].exists, "Email does not exist");
        delete domains[_domain];
        totalDomains--;
    }
}