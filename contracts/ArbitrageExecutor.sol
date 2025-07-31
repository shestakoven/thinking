// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

contract ArbitrageExecutor is ReentrancyGuard, Ownable, Pausable {
    
    struct ArbitrageOrder {
        address token;
        uint256 amount;
        string sourceChain;
        string targetChain;
        uint256 minProfit;
        uint256 deadline;
        bool executed;
        uint256 gasUsed;
        uint256 actualProfit;
    }
    
    struct ChainConfig {
        bool enabled;
        uint256 gasLimit;
        uint256 gasPrice;
        address bridgeContract;
    }
    
    mapping(bytes32 => ArbitrageOrder) public orders;
    mapping(address => bool) public authorizedExecutors;
    mapping(string => ChainConfig) public chainConfigs;
    
    uint256 public totalExecutions;
    uint256 public totalProfit;
    uint256 public executionFee = 0.1 ether; // 0.1 ETH fee per execution
    
    event ArbitrageOrderCreated(
        bytes32 indexed orderId,
        address indexed token,
        uint256 amount,
        string sourceChain,
        string targetChain,
        uint256 minProfit,
        uint256 deadline
    );
    
    event ArbitrageExecuted(
        bytes32 indexed orderId,
        uint256 profit,
        uint256 gasUsed,
        address executor
    );
    
    event ChainConfigUpdated(
        string chain,
        bool enabled,
        uint256 gasLimit,
        uint256 gasPrice
    );
    
    event ExecutionFeeUpdated(uint256 newFee);
    
    modifier onlyExecutor() {
        require(authorizedExecutors[msg.sender] || msg.sender == owner(), "Not authorized");
        _;
    }
    
    modifier whenNotPaused() {
        require(!paused(), "Contract is paused");
        _;
    }
    
    constructor() {
        authorizedExecutors[msg.sender] = true;
        
        // Initialize chain configurations
        chainConfigs["ethereum"] = ChainConfig({
            enabled: true,
            gasLimit: 21000,
            gasPrice: 50 gwei,
            bridgeContract: address(0)
        });
        
        chainConfigs["polygon"] = ChainConfig({
            enabled: true,
            gasLimit: 21000,
            gasPrice: 30 gwei,
            bridgeContract: address(0)
        });
        
        chainConfigs["arbitrum"] = ChainConfig({
            enabled: true,
            gasLimit: 21000,
            gasPrice: 0.1 gwei,
            bridgeContract: address(0)
        });
        
        chainConfigs["optimism"] = ChainConfig({
            enabled: true,
            gasLimit: 21000,
            gasPrice: 0.001 gwei,
            bridgeContract: address(0)
        });
        
        chainConfigs["bsc"] = ChainConfig({
            enabled: true,
            gasLimit: 21000,
            gasPrice: 5 gwei,
            bridgeContract: address(0)
        });
    }
    
    function createArbitrageOrder(
        address _token,
        uint256 _amount,
        string memory _sourceChain,
        string memory _targetChain,
        uint256 _minProfit,
        uint256 _deadline
    ) external onlyExecutor whenNotPaused returns (bytes32) {
        require(_deadline > block.timestamp, "Deadline must be in future");
        require(_amount > 0, "Amount must be positive");
        require(chainConfigs[_sourceChain].enabled, "Source chain not enabled");
        require(chainConfigs[_targetChain].enabled, "Target chain not enabled");
        
        bytes32 orderId = keccak256(abi.encodePacked(
            _token,
            _amount,
            _sourceChain,
            _targetChain,
            block.timestamp,
            msg.sender
        ));
        
        require(orders[orderId].token == address(0), "Order already exists");
        
        orders[orderId] = ArbitrageOrder({
            token: _token,
            amount: _amount,
            sourceChain: _sourceChain,
            targetChain: _targetChain,
            minProfit: _minProfit,
            deadline: _deadline,
            executed: false,
            gasUsed: 0,
            actualProfit: 0
        });
        
        emit ArbitrageOrderCreated(
            orderId,
            _token,
            _amount,
            _sourceChain,
            _targetChain,
            _minProfit,
            _deadline
        );
        
        return orderId;
    }
    
    function executeArbitrage(bytes32 _orderId) external onlyExecutor nonReentrant whenNotPaused {
        ArbitrageOrder storage order = orders[_orderId];
        require(order.token != address(0), "Order does not exist");
        require(!order.executed, "Order already executed");
        require(block.timestamp <= order.deadline, "Order expired");
        
        // Transfer tokens from executor
        IERC20(order.token).transferFrom(msg.sender, address(this), order.amount);
        
        // Record gas usage
        uint256 gasUsed = gasleft();
        
        // Execute cross-chain arbitrage logic here
        // This would integrate with your bridge infrastructure
        bool success = _executeCrossChainArbitrage(order);
        
        require(success, "Arbitrage execution failed");
        
        // Calculate actual profit
        uint256 actualProfit = _calculateActualProfit(order);
        require(actualProfit >= order.minProfit, "Insufficient profit");
        
        order.executed = true;
        order.gasUsed = gasUsed - gasleft();
        order.actualProfit = actualProfit;
        
        totalExecutions++;
        totalProfit += actualProfit;
        
        // Transfer profit to executor (minus fee)
        uint256 profitToExecutor = actualProfit > executionFee ? actualProfit - executionFee : 0;
        if (profitToExecutor > 0) {
            IERC20(order.token).transfer(msg.sender, profitToExecutor);
        }
        
        emit ArbitrageExecuted(_orderId, actualProfit, order.gasUsed, msg.sender);
    }
    
    function _executeCrossChainArbitrage(ArbitrageOrder storage order) internal returns (bool) {
        // This is where you would integrate with your existing bridge infrastructure
        // For now, we'll simulate a successful execution
        
        // Simulate cross-chain transfer
        // In real implementation, this would:
        // 1. Call the bridge contract for source chain
        // 2. Wait for confirmation
        // 3. Execute on target chain
        // 4. Return success/failure
        
        return true;
    }
    
    function _calculateActualProfit(ArbitrageOrder storage order) internal view returns (uint256) {
        // This would calculate actual profit based on real execution
        // For now, we'll simulate a 2% profit
        return order.amount * 2 / 100;
    }
    
    // Admin functions
    function addExecutor(address _executor) external onlyOwner {
        authorizedExecutors[_executor] = true;
    }
    
    function removeExecutor(address _executor) external onlyOwner {
        authorizedExecutors[_executor] = false;
    }
    
    function updateChainConfig(
        string memory _chain,
        bool _enabled,
        uint256 _gasLimit,
        uint256 _gasPrice,
        address _bridgeContract
    ) external onlyOwner {
        chainConfigs[_chain] = ChainConfig({
            enabled: _enabled,
            gasLimit: _gasLimit,
            gasPrice: _gasPrice,
            bridgeContract: _bridgeContract
        });
        
        emit ChainConfigUpdated(_chain, _enabled, _gasLimit, _gasPrice);
    }
    
    function setExecutionFee(uint256 _newFee) external onlyOwner {
        executionFee = _newFee;
        emit ExecutionFeeUpdated(_newFee);
    }
    
    function pause() external onlyOwner {
        _pause();
    }
    
    function unpause() external onlyOwner {
        _unpause();
    }
    
    // Emergency functions
    function emergencyWithdraw(address _token) external onlyOwner {
        uint256 balance = IERC20(_token).balanceOf(address(this));
        IERC20(_token).transfer(owner(), balance);
    }
    
    function emergencyWithdrawETH() external onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }
    
    // View functions
    function getOrder(bytes32 _orderId) external view returns (ArbitrageOrder memory) {
        return orders[_orderId];
    }
    
    function getChainConfig(string memory _chain) external view returns (ChainConfig memory) {
        return chainConfigs[_chain];
    }
    
    function getStats() external view returns (uint256, uint256) {
        return (totalExecutions, totalProfit);
    }
    
    // Receive function for ETH
    receive() external payable {}
}