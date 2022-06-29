const elect = artifacts.require("CollegeElection");

module.exports = function (deployer) {
  deployer.deploy(elect);
};