// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract FundMe {

    mapping(address => uint256) public addressToAmountFunded;
    address public owner;
    address[] public funders;
    AggregatorV3Interface public priceFeed;

    // owner will be the one who deploy the contract
    constructor(address _priceFeed) {
        priceFeed = AggregatorV3Interface(_priceFeed);
        owner = msg.sender;
    }

    // payable = this function can be used for payment in ETH
    function fund() public payable {
        // USD in WEI format
        uint256 minimumUSD = 5 * 10 ** 15;

        // if input doesn't meet the requirement, we will revert the execution.
        require(getConversionRate(msg.value) >= minimumUSD, "You need to spend more ETH");

        // save sender and funded amount
        addressToAmountFunded[msg.sender] += msg.value;
        funders.push(msg.sender);
    }

    modifier onlyOwner {

        // uncomment the line below to run the code first and then the modifier
        // _; 

        // run the require
        require(msg.sender == owner);

        // run the rest of the code where this modifier exist.
        _;
    }

    // Withdraw all of the balance
    function withdraw() payable onlyOwner public {
        // only owner can withdraw the fund  
        payable(msg.sender).transfer(address(this).balance);
        for (uint256 funderIndex = 0; funderIndex < funders.length; funderIndex++){
            address funder = funders[funderIndex];
            addressToAmountFunded[funder] = 0;
        }
        funders = new address[](0);
    }

    // can't be used in local test network since JS Vm doesn't have chain link
    // get Aggregato version
    function getVersion() public view returns(uint256){
        // address of ETH / USD price feed
        // below line is the hardcoded one
        // AggregatorV3Interface priceFeed = AggregatorV3Interface(0x8A753747A1Fa494EC906cE90E9f37563A8AF630e);
        return priceFeed.version();
    }

    function getEntranceFee() public view returns (uint256) {
        // minimumUSD
        uint256 minimumUSD = 50*10**18;
        uint256 price = getPrice();
        uint256 precision = 1*10**18;
        return (minimumUSD * precision) / price;
    }

    // get WEI price in term of USD
    function getPrice() public view returns(uint256){
        // below line is the hardcoded one
        // AggregatorV3Interface priceFeed = AggregatorV3Interface(0x8A753747A1Fa494EC906cE90E9f37563A8AF630e);

        //there are 5 outputs but we only interested in one of them
        // ETH -> USD * 10^8
        (,int price,,,) = priceFeed.latestRoundData();

        // USD * 10^8 -> WEI USD
        return uint256(price * 10000000000);
    }

    function getConversionRate(uint256 ethAmount) public view returns (uint256) {
        uint256 ethPrice = getPrice();
        uint256 ethAmountInUsd = (ethPrice * ethAmount) / 1000000000000000000; // WEI USD -> USD
        return ethAmountInUsd;
    }
}