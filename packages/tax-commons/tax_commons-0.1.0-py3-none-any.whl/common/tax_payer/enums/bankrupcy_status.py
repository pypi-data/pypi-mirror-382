from enum import Enum

class BankruptcyStatus(str, Enum):
    NEVER_BANKRUPT = "Never Bankrupt"
    CURRENTLY_BANKRUPT = "Currently Bankrupt"
    DISCHARGED_BANKRUPT = "Discharged Bankrupt"
    CONSUMER_PROPOSAL = "Consumer Proposal"