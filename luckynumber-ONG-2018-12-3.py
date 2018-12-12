"""
Lucky Number Game
"""
from boa.interop.Ontology.Contract import Migrate
from boa.interop.System.Storage import GetContext, Get, Put, Delete
from boa.interop.System.Runtime import CheckWitness, GetTime, Notify, Serialize, Deserialize
from boa.interop.System.ExecutionEngine import GetExecutingScriptHash, GetCallingScriptHash, GetEntryScriptHash
from boa.interop.Ontology.Native import Invoke
from boa.interop.Ontology.Runtime import GetCurrentBlockHash
from boa.builtins import ToScriptHash, concat, state


"""
https://github.com/tonyclarking/python-template/blob/master/libs/Utils.py
"""
def Revert():
    """
    Revert the transaction. The opcodes of this function is `09f7f6f5f4f3f2f1f000f0`,
    but it will be changed to `ffffffffffffffffffffff` since opcode THROW doesn't
    work, so, revert by calling unused opcode.
    """
    raise Exception(0xF1F1F2F2F3F3F4F4)


"""
https://github.com/tonyclarking/python-template/blob/master/libs/SafeCheck.py
"""
def Require(condition):
    """
	If condition is not satisfied, return false
	:param condition: required condition
	:return: True or false
	"""
    if not condition:
        Revert()
    return True

def RequireScriptHash(key):
    """
    Checks the bytearray parameter is script hash or not. Script Hash
    length should be equal to 20.
    :param key: bytearray parameter to check script hash format.
    :return: True if script hash or revert the transaction.
    """
    Require(len(key) == 20)
    return True

def RequireWitness(witness):
    """
	Checks the transaction sender is equal to the witness. If not
	satisfying, revert the transaction.
	:param witness: required transaction sender
	:return: True if transaction sender or revert the transaction.
	"""
    Require(CheckWitness(witness))
    return True
"""
SafeMath 
"""

def Add(a, b):
	"""
	Adds two numbers, throws on overflow.
	"""
	c = a + b
	Require(c >= a)
	return c

def Sub(a, b):
	"""
	Substracts two numbers, throws on overflow (i.e. if subtrahend is greater than minuend).
    :param a: operand a
    :param b: operand b
    :return: a - b if a - b > 0 or revert the transaction.
	"""
	Require(a>=b)
	return a-b

def ASub(a, b):
    if a > b:
        return a - b
    if a < b:
        return b - a
    else:
        return 0

def Mul(a, b):
	"""
	Multiplies two numbers, throws on overflow.
    :param a: operand a
    :param b: operand b
    :return: a - b if a - b > 0 or revert the transaction.
	"""
	if a == 0:
		return 0
	c = a * b
	Require(c / a == b)
	return c

def Div(a, b):
	"""
	Integer division of two numbers, truncating the quotient.
	"""
	Require(b > 0)
	c = a / b
	return c

def Pwr(a, b):
    """
    a to the power of b
    :param a the base
    :param b the power value
    :return a^b
    """
    c = 0
    if a == 0:
        c = 0
    elif b == 0:
        c = 1
    else:
        i = 0
        c = 1
        while i < b:
            c = Mul(c, a)
            i = i + 1
    return c

def Sqrt(a):
    """
    Return sqrt of a
    :param a:
    :return: sqrt(a)
    """
    c = Div(Add(a, 1), 2)
    b = a
    while(c < b):
        b = c
        c = Div(Add(Div(a, c), c), 2)
    return c


######################### Global game info ########################
ROUND_PREFIX = "G01"
# GAS_VAULT_KEY -- store the fee for calculating the winner
GAS_VAULT_KEY = "G02"

TOTAL_PAPER_KEY = "G03"
TOTAL_ONG_KEY = "G04"
# CURRET_ROUND_NUM_KEY -- store the current round number
CURRET_ROUND_NUM_KEY = "G05"

# PROFIT_PER_PAPER_KEY -- store the profit per paper (when it is bought)
PROFIT_PER_PAPER_KEY = "G06"

# TOTAL_DIVIDEND_OF_PREFIX + account -- store the total accumulated dividend of account
# when user withdraws, the total dividend will go to ZERO
TOTAL_DIVIDEND_OF_PREFIX = "G07"
REFERRAL_BALANCE_OF_PREFIX = "G08"
AWARD_BALANCE_OF_PREFFIX = "G09"
# PAPER_BALANCE_PREFIX + account -- store the current blank paper amount of account
PAPER_BALANCE_PREFIX = "G10"

REFERRAL_PREFIX = "G11"

# PROFIT_PER_PAPER_FROM_PREFIX + account -- store the filled paper amount in round i
PROFIT_PER_PAPER_FROM_PREFIX = "G12"

# FILL_PAPER_ROUND_START_PREFIX + account -- store the round number from which the account will fill his paper
FILL_PAPER_FROM_ROUND_PREFIX = "G13"
# PAPER_BALANCE_PREFIX + account -- store the current blank paper amount of account after contract upgrade
PAPER_BALANCE_BEFORE_UPGRADE_PREFIX = "G14"
NEW_PAPER_BALANCE_PREFIX = "15"
################## Round i User info ##################
# ROUND_PREFIX + CURRET_ROUND_NUM_KEY + FILLED_PAPER_BALANCE_PREFIX + account -- store the filled paper amount in round i
FILLED_PAPER_BALANCE_PREFIX = "U01"

# ROUND_PREFIX + CURRET_ROUND_NUM_KEY + PAPER_BALANCE_ROUND_PREFIX + account -- store the bought paper balance of account in round
PAPER_BALANCE_ROUND_PREFIX = "U02"
# ROUND_PREFIX + CURRET_ROUND_NUM_KEY + ASSIGN_PAPER_BALANCE_ROUND_PREFIX + account -- store the assigned paper balance of account in round
ASSIGN_PAPER_BALANCE_ROUND_PREFIX = "U03"
###################### Round i Public info ###########################
# ROUND_PREFIX + CURRET_ROUND_NUM_KEY + AWARD_VAULT_KEY -- store the total award for the winner in roung i
AWARD_VAULT_KEY = "R1"

# ROUND_PREFIX + CURRET_ROUND_NUM_KEY + FILLED_NUMBER_LIST_KEY -- store the filled number on papers
FILLED_NUMBER_LIST_KEY = "R2"

# ROUND_PREFIX + CURRET_ROUND_NUM_KEY + FILLED_NUMBER_KEY + number -- store the accounts that filled number
# key = ROUND_PREFIX + CURRET_ROUND_NUM_KEY + FILLED_NUMBER_KEY + number
# value = [account1, account2, account3]
FILLED_NUMBER_KEY = "R3"

# ROUND_PREFIX + CURRET_ROUND_NUM_KEY + ROUND_STATUS_KEY -- store the status of round i game
ROUND_STATUS_KEY = "R4"

# ROUND_PREFIX + CURRET_ROUND_NUM_KEY  + WINNER_KEY -- store the win info
# key = ROUND_PREFIX + CURRET_ROUND_NUM_KEY  + WINNER_KEY
# value = [generatedLuckyNumber, actualLuckyNumberList, allWinnerList, winAwardList]
WINNER_KEY = "R5"

# ROUND_PREFIX + CURRET_ROUND_NUM_KEY + FILLED_PAPER_AMOUNT -- store the asset for the next round in round i+1
FILLED_PAPER_AMOUNT = "R6"
############################### other info ###################################
INIIT_KEY = "Initialized"
COMMISSION_KEY = "AdminComission"
STATUS_ON = "RUNNING"
STATUS_OFF = "END"


MagnitudeForProfitPerPaper = 100000000000000000000

InitialPrice = 1000000000
PaperHolderPercentage = 50
ReferralAwardPercentage = 1
AwardPercentage = 45

PureAwardExcludeCommissionFee = 98

# migrate to be add start
ExecuteFeePercentage = 5
# HOLDER_PERCENTAGE_KEY + roundNumber
HOLDER_PERCENTAGE_KEY = "HolderPercentage"
REFERRAL_PERCENTAGE_KEY = "ReferralPercentage"
AWARD_AT_BUY_PERCENTAGE_KEY = "AwardAtBuyPercentage"
AWARD_AT_FILL_PERCENTAGE_KEY = "AwardAtFillPercentage"

TOTAL_ONG_TO_BE_ADD_AT_FILL_KEY = "TotalOngToBeAddAtFill"
# migrate to be add end
# PURE_AWARD_EXCLUDE_COMMISSION_FEE_KEY = "PureAwardExcludeCommissionFee"

# the script hash of this contract
ContractAddress = GetExecutingScriptHash()
ONGAddress = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02')
ONGMagnitude = 1000000000
######################## LuckyNumber account
Admin = ToScriptHash('AYqCVffRcbPkf1BVCYPJqqoiFTFmvwYKhG')
######################## skyinglyh account
# Admin = ToScriptHash('AQf4Mzu1YJrhz9f3aRkkwSm9n3qhXGSh4p')

# Beijing time 2018-11-23-15:45:00
# each round will last 3 minutes
StartTime = 1542955500
RoundDurationMinutes = 3


def Main(operation, args):
    ######################## for Admin to invoke Begin ###############
    if operation == "init":
        return init()
    if operation == "startNewRound":
        return startNewRound()
    if operation == "addReferral":
        if len(args) != 2:
            return False
        toBeReferred = args[0]
        referral = args[1]
        return addReferral(toBeReferred, referral)
    if operation == "addMultiReferral":
        return addMultiReferral(args)
    if operation == "assignPaper":
        if len(args) != 2:
            return False
        account = args[0]
        paperAmount = args[1]
        return assignPaper(account, paperAmount)
    if operation == "multiAssignPaper":
        return multiAssignPaper(args)
    if operation == "setHolderReferralAwardAtBuyAndFillPercentage":
        if len(args) != 4:
            return False
        holderPercentage = args[0]
        referralPercentage = args[1]
        awardAtBuyPercentage = args[2]
        awardAtFillPercentage = args[3]
        return setHolderReferralAwardAtBuyAndFillPercentage(holderPercentage, referralPercentage, awardAtBuyPercentage, awardAtFillPercentage)

    if operation == "withdrawGas":
        return withdrawGas()
    if operation == "withdrawCommission":
        return withdrawCommission()
    if operation == "addOngToCurrentRoundAwardVault":
        if len(args) != 1:
            return False
        ongAmount = args[0]
        return addOngToCurrentRoundAwardVault(ongAmount)
    if operation == "addOngToPaperHolders":
        if len(args) != 1:
            return False
        ongAmount = args[0]
        return addOngToPaperHolders(ongAmount)
    if operation == "endCurrentRound":
        return endCurrentRound()
    if operation == "migrateContract":
        if len(args) != 8:
            return False
        code = args[0]
        needStorage = args[1]
        name = args[2]
        version = args[3]
        author = args[4]
        email = args[5]
        description = args[6]
        newContractHash = args[7]
        return migrateContract(code, needStorage, name, version, author, email, description, newContractHash)
    ######################## for Admin to invoke End ###############
    ######################## for User to invoke Begin ###############
    if operation == "buyPaper":
        if len(args) != 2:
            return False
        account = args[0]
        paperAmount = args[1]
        return buyPaper(account, paperAmount)
    if operation == "reinvest":
        if len(args) != 2:
            return False
        account = args[0]
        paperAmount = args[1]
        return reinvest(account, paperAmount)
    if operation == "fillPaper":
        if len(args) != 2:
            return False
        account = args[0]
        guessNumberList = args[1]
        return fillPaper(account, guessNumberList)
    if operation == "withdraw":
        if len(args) != 1:
            return False
        account = args[0]
        return withdraw(account)
    if operation == "updateDividendBalance":
        if len(args) != 1:
            return False
        account = args[0]
        return updateDividendBalance(account)
    ######################## for User to invoke End ###############
    ######################### General Info to pre-execute Begin ##############
    # Global Info Start
    if operation == "getTotalONGAmount":
        return getTotalONGAmount()
    if operation == "getTotalPaper":
        return getTotalPaper()
    if operation == "getGasVault":
        return getGasVault()
    if operation == "getCurrentRound":
        return getCurrentRound()
    if operation == "getCurrentRoundEndTime":
        return getCurrentRoundEndTime()
    if operation == "getCommissionAmount":
        return getCommissionAmount()
    if operation == "getProfitPerPaper":
        return getProfitPerPaper()
    if operation == "getHolderPercentage":
        if len(args) != 1:
            return False
        roundNum = args[0]
        return getHolderPercentage(roundNum)
    if operation == "getReferralPercentage":
        if len(args) != 1:
            return False
        roundNum = args[0]
        return getReferralPercentage(roundNum)
    if operation == "getAwardAtBuyPercentage":
        if len(args) != 1:
            return False
        roundNum = args[0]
        return getAwardAtBuyPercentage(roundNum)
    if operation == "getAwardAtFillPercentage":
        if len(args) != 1:
            return False
        roundNum = args[0]
        return getAwardAtFillPercentage(roundNum)
    if operation == "getParametersPercentage":
        if len(args) != 1:
            return False
        roundNum = args[0]
        return getParametersPercentage(roundNum)
    if operation == "getTotalONGToBeAddAtFill":
        return getTotalONGToBeAddAtFill()
    # User Info Start
    if operation == "getPaperBalance":
        if len(args) != 1:
            return False
        account = args[0]
        return getPaperBalance(account)
    if operation == "getReferralBalance":
        if len(args) != 1:
            return False
        account = args[0]
        return getReferralBalance(account)
    if operation == "getDividendBalance":
        if len(args) != 1:
            return False
        account = args[0]
        return getDividendBalance(account)
    if operation == "getAwardBalance":
        if len(args) != 1:
            return False
        account = args[0]
        return getAwardBalance(account)
    if operation == "getDividendsBalance":
        if len(args) != 1:
            return False
        account = args[0]
        return getDividendsBalance(account)
    if operation == "getReferral":
        if len(args) != 1:
            return False
        account = args[0]
        return getReferral(account)
    if operation == "getFilledPaperBalance":
        if len(args) != 2:
            return False
        account = args[0]
        currentRound = args[1]
        return getFilledPaperBalance(account, currentRound)
    # Round Info Start
    if operation == "getAwardVault":
        if len(args) != 1:
            return False
        currentRound = args[0]
        return getAwardVault(currentRound)
    if operation == "getGameStatus":
        if len(args) != 1:
            return False
        currentRound = args[0]
        return getGameStatus(currentRound)
    if operation == "getFilledPaperAmount":
        if len(args) != 1:
            return False
        currentRound = args[0]
        return getFilledPaperAmount(currentRound)
    if operation == "getWinInfo":
        if len(args) != 1:
            return False
        currentRound = args[0]
        return getWinInfo(currentRound)
    if operation == "getFilledNumberList":
        currentRound = args[0]
        return getFilledNumberList(currentRound)
    if operation == "getPlayersList":
        roundNum = args[0]
        guessNumber = args[1]
        return getPlayersList(roundNum, guessNumber)
    if operation == "getPlayerGuessedNumber":
        roundNum = args[0]
        account = args[1]
        return getPlayerGuessedNumber(roundNum, account)
    ######################### General Info to pre-execute Begin ##############

    ######################### For testing purpose Begin ##############
    # Utility Methods Start
    if operation == "getLuckyNumber":
        return getLuckyNumber()

    ######################### For testing purpose End ##############
    return False


####################### Methods that only Admin can invoke Start #######################
def init():
    RequireWitness(Admin)
    inited = Get(GetContext(), INIIT_KEY)
    if inited:
        Notify(["idiot admin, you have initialized the contract"])
        return False
    else:
        Put(GetContext(), INIIT_KEY, 1)
        Notify(["Initialized contract successfully"])
        # startNewRound()
        _updateParametersPercentage(0, 20, 2, 43, 30)
    return True


def startNewRound():
    """
    Only admin can start new round
    :return:
    """

    RequireWitness(Admin)
    currentRound = getCurrentRound()
    nextRoundNum = Add(currentRound, 1)

    parametersList2 = getParametersPercentage(nextRoundNum)
    # if the Admin has not set the parameters for the nextRound before, next round will use the current round parametersList
    if Add(Add(Add(parametersList2[0], parametersList2[1]), parametersList2[2]), parametersList2[3]) != 95:
        parametersList1 = getParametersPercentage(currentRound)
        _updateParametersPercentage(nextRoundNum, parametersList1[0], parametersList1[1], parametersList1[2], parametersList1[3])

    Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, nextRoundNum), ROUND_STATUS_KEY), STATUS_ON)
    Put(GetContext(), CURRET_ROUND_NUM_KEY, nextRoundNum)
    Notify(["startRound", nextRoundNum, GetTime()])
    return True


def addReferral(toBeReferred, referral):
    """
    only Admin can add referral
    :param toBeReferred:
    :param referral:
    :return:
    """
    RequireWitness(Admin)
    RequireScriptHash(toBeReferred)
    RequireScriptHash(referral)
    Require(toBeReferred != referral)
    # key = concatKey(REFERRAL_PREFIX, toBeReferred),
    # value = referral
    Put(GetContext(), concatKey(REFERRAL_PREFIX, toBeReferred), referral)
    return True


def addMultiReferral(args):
    """
    only Admin can add referral multiple times
    :param args:
    :return:
    """
    RequireWitness(Admin)
    for p in args:
        RequireScriptHash(p[0])
        RequireScriptHash(p[1])
        Require(p[0] != p[1])
        Put(GetContext(), concatKey(REFERRAL_PREFIX, p[0]), p[1])
    return True


def assignPaper(account, paperAmount):
    RequireWitness(Admin)

    updateDividendBalance(account)

    # update account's profit per paper from value
    Put(GetContext(), concatKey(PROFIT_PER_PAPER_FROM_PREFIX, account), getProfitPerPaper())

    # update account assigned paper balance
    currentRound = getCurrentRound()
    assignPaperBalanceKey = concatKey(concatKey(ROUND_PREFIX, currentRound), concatKey(ASSIGN_PAPER_BALANCE_ROUND_PREFIX, account))
    Put(GetContext(), assignPaperBalanceKey, Add(getRoundAssignPaperBalance(account, currentRound), paperAmount))

    # update account paper balance
    balanceKey = concatKey(NEW_PAPER_BALANCE_PREFIX, account)
    Put(GetContext(), balanceKey, Add(paperAmount, getPaperBalance(account)))

    # update total paper amount
    Put(GetContext(), TOTAL_PAPER_KEY, Add(paperAmount, getTotalPaper()))

    Notify(["assignPaper", account, paperAmount, GetTime()])

    return True


def multiAssignPaper(args):
    RequireWitness(Admin)
    for p in args:
        Require(assignPaper(p[0], p[1]))
    return True

def setHolderReferralAwardAtBuyAndFillPercentage(holderPercentage, referralPercentage, awardAtBuyPercentage, awardAtFillPercentage):
    RequireWitness(Admin)
    Require(holderPercentage > 0)
    Require(referralPercentage > 0)
    Require(awardAtBuyPercentage > 0)
    Require(awardAtFillPercentage > 0)

    totalPercentage = Add(Add(Add(holderPercentage, referralPercentage), awardAtBuyPercentage), awardAtFillPercentage)
    Require(totalPercentage == 95)

    currentRound = getCurrentRound()
    # the new percentage list will work in next round
    nextRound = Add(currentRound, 1)
    _updateParametersPercentage(nextRound, holderPercentage, referralPercentage, awardAtBuyPercentage, awardAtFillPercentage)

    return True

def _updateParametersPercentage(roundNumber, holderPercentage, referralPercentage, awardAtBuyPercentage, awardAtFillPercentage):

    RequireWitness(Admin)
    Put(GetContext(), concatKey(HOLDER_PERCENTAGE_KEY, roundNumber), holderPercentage)
    Put(GetContext(), concatKey(REFERRAL_PERCENTAGE_KEY, roundNumber), referralPercentage)
    Put(GetContext(), concatKey(AWARD_AT_BUY_PERCENTAGE_KEY, roundNumber), awardAtBuyPercentage)
    Put(GetContext(), concatKey(AWARD_AT_FILL_PERCENTAGE_KEY, roundNumber), awardAtFillPercentage)
    Notify(["setHolderReferralAwardAtBuyAndFillPercentage", roundNumber, holderPercentage, referralPercentage, awardAtBuyPercentage, awardAtFillPercentage, GetTime()])
    return True

def _updateFillPaperFromRoundAndAwardVault(account, fillPaperFromRound, fillPaperBalanceNeedtoUpdate):
    currentRound = getCurrentRound()
    fillPaperBalanceNeedtoUpdateLeft = fillPaperBalanceNeedtoUpdate
    awardVaultToBeAdd = 0
    while fillPaperBalanceNeedtoUpdateLeft > 0:
        roundPaperBalance = getRoundPaperBalance(account, fillPaperFromRound)
        roundAssignPaperBalance = getRoundAssignPaperBalance(account, fillPaperFromRound)
        totalRoundPaperBalance = Add(roundPaperBalance, roundAssignPaperBalance)
        Notify(["111Update", fillPaperFromRound, roundPaperBalance, roundAssignPaperBalance, totalRoundPaperBalance])
        if totalRoundPaperBalance != 0:
            if fillPaperBalanceNeedtoUpdateLeft >= totalRoundPaperBalance:
                # delete round paper balance
                roundPaperBalanceKey = concatKey(concatKey(ROUND_PREFIX, fillPaperFromRound), concatKey(PAPER_BALANCE_ROUND_PREFIX, account))
                Delete(GetContext(), roundPaperBalanceKey)

                # get award percentate at fill at fillPaperFromRound round
                awardPercentageAtFill = getAwardAtFillPercentage(fillPaperFromRound)
                awardVaultToBeAdd = Add(awardVaultToBeAdd, Div(Mul(Mul(roundPaperBalance, ONGMagnitude), awardPercentageAtFill), 100))

                # delete round assign paper balance
                roundAssignPaperBalanceKey = concatKey(concatKey(ROUND_PREFIX, fillPaperFromRound), concatKey(ASSIGN_PAPER_BALANCE_ROUND_PREFIX, account))
                Delete(GetContext(), roundAssignPaperBalanceKey)

                fillPaperBalanceNeedtoUpdateLeft = Sub(fillPaperBalanceNeedtoUpdateLeft, totalRoundPaperBalance)
                Notify(["222Update", fillPaperFromRound, awardPercentageAtFill, awardVaultToBeAdd, fillPaperBalanceNeedtoUpdateLeft])
            else:
                ###### deduct round paper balance first, then deduct the round assign paper balance #####
                if fillPaperBalanceNeedtoUpdateLeft >= roundPaperBalance:
                    # delete round paper balance
                    roundPaperBalanceKey = concatKey(concatKey(ROUND_PREFIX, fillPaperFromRound), concatKey(PAPER_BALANCE_ROUND_PREFIX, account))
                    Delete(GetContext(), roundPaperBalanceKey)
                    # get award percentate at fill at fillPaperFromRound round
                    awardPercentageAtFill = getAwardAtFillPercentage(fillPaperFromRound)
                    awardVaultToBeAdd = Add(awardVaultToBeAdd, Div(Mul(Mul(roundPaperBalance, ONGMagnitude), awardPercentageAtFill), 100))

                    fillPaperBalanceNeedtoUpdateLeft = Sub(fillPaperBalanceNeedtoUpdateLeft, roundPaperBalance)
                    # update round assign paper balance
                    roundAssignPaperBalance = Sub(roundAssignPaperBalance, fillPaperBalanceNeedtoUpdateLeft)
                    roundAssignPaperBalanceKey = concatKey(concatKey(ROUND_PREFIX, fillPaperFromRound), concatKey(ASSIGN_PAPER_BALANCE_ROUND_PREFIX, account))
                    Notify(["333Update", fillPaperFromRound, awardPercentageAtFill, awardVaultToBeAdd, fillPaperBalanceNeedtoUpdateLeft, roundAssignPaperBalance])
                    if roundAssignPaperBalance > 0:
                        Put(GetContext(), roundAssignPaperBalanceKey, roundAssignPaperBalance)
                    else:
                        Delete(GetContext(), roundAssignPaperBalanceKey)
                else:

                    # update round paper balance
                    roundPaperBalanceKey = concatKey(concatKey(ROUND_PREFIX, fillPaperFromRound), concatKey(PAPER_BALANCE_ROUND_PREFIX, account))
                    Put(GetContext(), roundPaperBalanceKey, Sub(roundPaperBalance, fillPaperBalanceNeedtoUpdateLeft))

                    # get award percentate at fill at fillPaperFromRound round
                    awardPercentageAtFill = getAwardAtFillPercentage(fillPaperFromRound)
                    awardVaultToBeAdd = Add(awardVaultToBeAdd, Div(Mul(Mul(fillPaperBalanceNeedtoUpdateLeft, ONGMagnitude), awardPercentageAtFill), 100))
                    Notify(["333Update", fillPaperFromRound, awardPercentageAtFill, awardVaultToBeAdd])
                # update fillPaperBalanceNeedtoUpdateLeft
                fillPaperBalanceNeedtoUpdateLeft = 0
        fillPaperFromRound = Add(fillPaperFromRound, 1)

    # update the fillPaperFromRound
    fillPaperFromRoundKey = concatKey(FILL_PAPER_FROM_ROUND_PREFIX, account)
    fillPaperFromRound = Sub(fillPaperFromRound, 1)
    Put(GetContext(), fillPaperFromRoundKey, fillPaperFromRound)

    awardVaultKey = concatKey(concatKey(ROUND_PREFIX, currentRound), AWARD_VAULT_KEY)
    # update current round award vault
    Put(GetContext(), awardVaultKey, Add(awardVaultToBeAdd, getAwardVault(currentRound)))
    Notify(["444Update", fillPaperFromRound, awardVaultToBeAdd])
    return awardVaultToBeAdd


def withdrawGas():
    """
    Only admin can withdraw
    :return:
    """
    RequireWitness(Admin)

    Require(transferONGFromContact(Admin, getGasVault()))

    # update total ong amount
    Put(GetContext(), TOTAL_ONG_KEY, Sub(getTotalONGAmount(), getGasVault()))
    Delete(GetContext(), GAS_VAULT_KEY)
    return True


def withdrawCommission():
    RequireWitness(Admin)

    Require(transferONGFromContact(Admin, getCommissionAmount()))

    # update total ong amount
    Put(GetContext(), TOTAL_ONG_KEY, Sub(getTotalONGAmount(), getCommissionAmount()))
    Delete(GetContext(), COMMISSION_KEY)

    return True

def addOngToCurrentRoundAwardVault(ongAmount):
    RequireWitness(Admin)
    res = transferONG(Admin, ContractAddress, ongAmount)
    if res == False:
        # , "Add ong to current round award vault failed!"
        Notify(["AddToAwardVaultError", 1007])
        return False
    currentRound = getCurrentRound()

    awardVaultKey = concatKey(concatKey(ROUND_PREFIX, currentRound), AWARD_VAULT_KEY)
    Put(GetContext(), awardVaultKey, Add(ongAmount, getAwardVault(currentRound)))

    # update total ong
    Put(GetContext(), TOTAL_ONG_KEY, Add(getTotalONGAmount(), ongAmount))

    Notify(["AddToAwardVault", Admin, ongAmount])
    return True

def addOngToPaperHolders(ongAmount):
    RequireWitness(Admin)
    # Require(transferONG(Admin, ContractAddress, ongAmount))
    res = transferONG(Admin, ContractAddress, ongAmount)
    if res == False:
        # , "Add ong to paper holders failed!"
        Notify(["AddToPaperHoldersError", 1008])
        return False
    currentRound = getCurrentRound()

    # update profit per paper
    profitPerPaperToBeAdd = Div(Mul(ongAmount, MagnitudeForProfitPerPaper), getTotalPaper())
    Put(GetContext(), PROFIT_PER_PAPER_KEY, Add(profitPerPaperToBeAdd, getProfitPerPaper()))
    # update total ong
    Put(GetContext(), TOTAL_ONG_KEY, Add(getTotalONGAmount(), ongAmount))

    Notify(["AddToPaperHolders",currentRound, ongAmount, GetTime()])
    return True


def endCurrentRound():
    RequireWitness(Admin)

    currentRound = getCurrentRound()

    Require(GetTime() >= getCurrentRoundEndTime())

    Require(getGameStatus(currentRound) == STATUS_ON)

    numberListKey = concatKey(concatKey(ROUND_PREFIX, currentRound), FILLED_NUMBER_LIST_KEY)
    numberListInfo = Get(GetContext(), numberListKey)
    numberList = []
    if numberListInfo:
        numberList = Deserialize(numberListInfo)
    else:
        # if no one participate this round of game
        Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, currentRound), ROUND_STATUS_KEY), STATUS_OFF)
        # update the next award vault -- pass the current award vault to the next round award vault
        nextRound = Add(currentRound, 1)
        Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, nextRound), AWARD_VAULT_KEY), getAwardVault(currentRound))
        Notify(["endRound", currentRound, GetTime()])
        startNewRound()
        return True

    # to record the minimum distance
    minDistance = 10000
    # to record the number corresponding with minimum distance
    existLuckyNumber = 10000
    luckyNumber = getLuckyNumber()
    for number in numberList:
        # get the L1 norm of the distance between number and luckyNumber
        distance = ASub(number, luckyNumber)

        if distance < minDistance:
            minDistance = distance
            existLuckyNumber = number

    luckyDis = ASub(luckyNumber, existLuckyNumber)
    tryExistLuckyNumber = 10000
    if existLuckyNumber < luckyNumber:
        tryExistLuckyNumber = Add(luckyNumber, luckyDis)
    elif existLuckyNumber > luckyNumber:
        if luckyNumber > luckyDis:
            tryExistLuckyNumber = Sub(luckyNumber, luckyDis)

    # save the actual lucky number
    actualLuckyNumberList = []
    actualLuckyNumberList.append(existLuckyNumber)
    winnersListKey = concatKey(concatKey(ROUND_PREFIX, currentRound), concatKey(FILLED_NUMBER_KEY, existLuckyNumber))
    winnersListInfo = Get(GetContext(), winnersListKey)
    winnersList = Deserialize(winnersListInfo)

    tryWinnersListKey = concatKey(concatKey(ROUND_PREFIX, currentRound), concatKey(FILLED_NUMBER_KEY, tryExistLuckyNumber))
    tryWinnersListInfo = Get(GetContext(), tryWinnersListKey)
    # add the two list together
    tryWinnersList = []
    if tryWinnersListInfo:
        actualLuckyNumberList.append(tryExistLuckyNumber)
        tryWinnersList = Deserialize(tryWinnersListInfo)
        for tryWinner in tryWinnersList:
            winnersList.append(tryWinner)

    # split the Award Vault to the winners
    awardVault = getAwardVault(currentRound)

    winnersPopulation = len(winnersList)
    awardPerWinner = Div(Div(Mul(awardVault, PureAwardExcludeCommissionFee),100), winnersPopulation)

    totalPureAward = 0
    winAwardList = []
    for winner in winnersList:
        pureWinnerAwardToBeAdd = 0
        if getReferral(winner):
            pureWinnerAwardToBeAdd = Div(Mul(awardPerWinner, 101), 100)
        else:
            pureWinnerAwardToBeAdd = awardPerWinner

        Put(GetContext(), concatKey(AWARD_BALANCE_OF_PREFFIX, winner), Add(pureWinnerAwardToBeAdd, getAwardBalance(winner)))
        totalPureAward = Add(totalPureAward, pureWinnerAwardToBeAdd)
        winAwardList.append(pureWinnerAwardToBeAdd)

    # get the commission fee
    totalCommission = Sub(awardVault, totalPureAward)
    # update the commission balance, which only admin can touch
    Put(GetContext(), COMMISSION_KEY, Add(totalCommission, getCommissionAmount()))

    # mark this round game as END
    Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, currentRound), ROUND_STATUS_KEY), STATUS_OFF)

    Notify(["endRound", currentRound, GetTime(), luckyNumber, actualLuckyNumberList, winnersList, winAwardList])
    winList = []
    winList.append(luckyNumber)
    winList.append(Serialize(actualLuckyNumberList))
    winList.append(Serialize(winAwardList))
    winListInfo = Serialize(winList)
    Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, currentRound), WINNER_KEY), winListInfo)

    startNewRound()

    return True


def migrateContract(code, needStorage, name, version, author, email, description, newContractHash):
    RequireWitness(Admin)

    res = transferONGFromContact(newContractHash, getTotalONGAmount())
    Require(res)
    if res == True:
        res = Migrate(code, needStorage, name, version, author, email, description)
        Require(res)
        Notify(["Migrate Contract successfully", Admin, GetTime()])
        return True
    else:
        Notify(["MigrateContractError", "transfer ONG to new contract error"])
        return False
####################### Methods that only Admin can invoke End #######################


######################## Methods for Users Start ######################################
def buyPaper(account, paperAmount):
    # RequireWitness(account)
    if CheckWitness(account) == False:
        # "Check witness failed!",
        Notify(["BuyPaperError", 1000])
        return False
    if paperAmount <= 0:
        # "buy paperAmount illegal!",
        Notify(["BuyPaperError", 1006])
        return False

    currentRound = getCurrentRound()

    # Require(getGameStatus(currentRound) == STATUS_ON)
    if getGameStatus(currentRound) == STATUS_OFF:
        #  "Current round game status off!",
        Notify(["BuyPaperError", 1001])
        return False

    ongAmount = paperToONG(paperAmount)

    # Require(transferONG(account, ContractAddress, ongAmount))
    res = transferONG(account, ContractAddress, ongAmount)
    if res == False:
        # , "Buyer transfers ONG failed!"
        Notify(["BuyPaperError", 1002])
        return False

    # PaperHolderPercentage = 50
    # dividend1 = Div(Mul(ongAmount, PaperHolderPercentage), 100)
    referralPercentage = getReferralPercentage(currentRound)
    dividend1 = Div(Mul(ongAmount, Add(getHolderPercentage(currentRound), referralPercentage)), 100)
    # update referral balance <---> Get(GetContext(), concatKey(REFERRAL_PREFIX, account))
    referral = getReferral(account)
    referralAmount = 0

    if referral:
        # ReferralAwardPercentage = 1
        # referralAmount = Div(Mul(ongAmount, ReferralAwardPercentage), 100)
        referralAmount = Div(Mul(ongAmount, referralPercentage), 100)
        Put(GetContext(), concatKey(REFERRAL_BALANCE_OF_PREFIX, referral), Add(referralAmount, getReferralBalance(referral)))
    dividend = Sub(dividend1, referralAmount)

    # update award vault, AwardPercentage = 45
    # awardVaultToBeAdd = Div(Mul(ongAmount, AwardPercentage), 100)
    # awardVaultKey = concatKey(concatKey(ROUND_PREFIX, currentRound), AWARD_VAULT_KEY)
    # Put(GetContext(), awardVaultKey, Add(awardVaultToBeAdd, getAwardVault(currentRound)))

    awardVaultToBeAddAtBuy = Div(Mul(ongAmount, getAwardAtBuyPercentage(currentRound)), 100)
    awardVaultKey = concatKey(concatKey(ROUND_PREFIX, currentRound), AWARD_VAULT_KEY)
    Put(GetContext(), awardVaultKey, Add(awardVaultToBeAddAtBuy, getAwardVault(currentRound)))

    # update gas vault
    # gasVaultToBeAdd = Sub(Sub(ongAmount, dividend1), awardVaultToBeAdd)
    # gasVaultToBeAdd = Sub(Sub(ongAmount, dividend), awardVaultToBeAdd)
    # Put(GetContext(), GAS_VAULT_KEY, Add(gasVaultToBeAdd, getGasVault()))
    gasVaultToBeAdd = Div(Mul(ongAmount, ExecuteFeePercentage), 100)
    Put(GetContext(), GAS_VAULT_KEY, Add(gasVaultToBeAdd, getGasVault()))

    # update the awardVaultAtFill
    awardVaultToBeAddAtFill = Sub(Sub(Sub(ongAmount, dividend1), awardVaultToBeAddAtBuy), gasVaultToBeAdd)
    Put(GetContext(), TOTAL_ONG_TO_BE_ADD_AT_FILL_KEY, Add(getTotalONGToBeAddAtFill(), awardVaultToBeAddAtFill))

    # update the round paper balance
    roundPaperBalanceKey = concatKey(concatKey(ROUND_PREFIX, currentRound), concatKey(PAPER_BALANCE_ROUND_PREFIX, account))
    Put(GetContext(), roundPaperBalanceKey, Add(getRoundPaperBalance(account, currentRound), paperAmount))

    oldProfitPerPaper = Get(GetContext(), PROFIT_PER_PAPER_KEY)
    oldTotalPaperAmount = getTotalPaper()

    if oldTotalPaperAmount != 0:
        # profitPerPaperToBeAdd = Div(dividend, totalPaperAmount)
        profitPerPaperToBeAdd = Div(Mul(dividend, MagnitudeForProfitPerPaper), oldTotalPaperAmount)
        # update profitPerPaper
        Put(GetContext(), PROFIT_PER_PAPER_KEY, Add(profitPerPaperToBeAdd, oldProfitPerPaper))
    else:
        # if current total paper is ZERO, the dividend will be assigned as the commission part
        Put(GetContext(), COMMISSION_KEY, Add(dividend, getCommissionAmount()))

    updateDividendBalance(account)

    # if not getPaperBalanceBeforeUpgrade(account):
    #     # record the paper balance before contract upgrades
    #     Put(GetContext(), concatKey(PAPER_BALANCE_BEFORE_UPGRADE_PREFIX, account), getPaperBalance(account))

    # update paper balance of account
    newPaperBalance = Get(GetContext(), concatKey(NEW_PAPER_BALANCE_PREFIX, account))
    Put(GetContext(), concatKey(NEW_PAPER_BALANCE_PREFIX, account), Add(paperAmount, newPaperBalance))

    # update total paper amount
    Put(GetContext(), TOTAL_PAPER_KEY, Add(paperAmount, getTotalPaper()))

    # update total ONG
    Put(GetContext(), TOTAL_ONG_KEY, Add(getTotalONGAmount(), ongAmount))
    Notify(["buyPaper", account, ongAmount, paperAmount, GetTime()])

    return True


def reinvest(account, paperAmount):
    # RequireWitness(account)
    if CheckWitness(account) == False:
        # , "Check witness failed!"
        Notify(["ReinvestError", 1000])
        return False

    if paperAmount <= 0:
        # "buy paperAmount illegal!",
        Notify(["BuyPaperError", 1006])
        return False

    currentRound = getCurrentRound()

    # Require(getGameStatus(currentRound) == STATUS_ON)
    if getGameStatus(currentRound) == STATUS_OFF:
        # , "Current round game status off!"
        Notify(["ReinvestError", 1001])
        return False

    ongAmount = paperToONG(paperAmount)

    # updateDividendBalance(account)
    dividendBalance = getDividendBalance(account)
    awardBalance = getAwardBalance(account)
    referralBalance = getReferralBalance(account)
    assetToBeReinvest = Add(Add(dividendBalance, awardBalance), referralBalance)

    # Require(assetToBeReinvest >= ongAmount)
    if assetToBeReinvest < ongAmount:
        # "Not enough ONG to rebuy papers!",
        Notify(["ReinvestError", 1003])
        return False

    # dividend1 = Div(Mul(ongAmount, PaperHolderPercentage), 100)
    referralPercentage = getReferralPercentage(currentRound)
    dividend1 = Div(Mul(ongAmount, Add(getHolderPercentage(currentRound), referralPercentage)), 100)

    # update referral balance
    referral = getReferral(account)
    referralAmount = 0
    if referral:
        # referralAmount = Div(Mul(ongAmount, ReferralAwardPercentage), 100)
        referralAmount = Div(Mul(ongAmount, referralPercentage), 100)
        Put(GetContext(), concatKey(REFERRAL_BALANCE_OF_PREFIX, referral), Add(referralAmount, getReferralBalance(referral)))
    dividend = Sub(dividend1, referralAmount)

    # # update award vault
    # awardVaultToBeAdd = Div(Mul(ongAmount, AwardPercentage), 100)
    # # awardVaultKey = concatKey(concatKey(ROUND_PREFIX, currentRound), AWARD_VAULT_KEY)
    # # Put(GetContext(), awardVaultKey, Add(awardVaultToBeAdd, getAwardVault(currentRound)))
    awardVaultToBeAddAtBuy = Div(Mul(ongAmount, getAwardAtBuyPercentage(currentRound)), 100)
    awardVaultKey = concatKey(concatKey(ROUND_PREFIX, currentRound), AWARD_VAULT_KEY)
    Put(GetContext(), awardVaultKey, Add(awardVaultToBeAddAtBuy, getAwardVault(currentRound)))

    # update gas vault
    # gasVaultToBeAdd = Sub(Sub(ongAmount, dividend1), awardVaultToBeAdd)
    # Put(GetContext(), GAS_VAULT_KEY, Add(gasVaultToBeAdd, getGasVault()))
    gasVaultToBeAdd = Div(Mul(ongAmount, ExecuteFeePercentage), 100)
    Put(GetContext(), GAS_VAULT_KEY, Add(gasVaultToBeAdd, getGasVault()))

    # update the awardVaultAtFill
    awardVaultToBeAddAtFill = Sub(Sub(Sub(ongAmount, dividend1), awardVaultToBeAddAtBuy), gasVaultToBeAdd)
    Put(GetContext(), TOTAL_ONG_TO_BE_ADD_AT_FILL_KEY, Add(getTotalONGToBeAddAtFill(), awardVaultToBeAddAtFill))

    # update the round paper balance
    roundPaperBalanceKey = concatKey(concatKey(ROUND_PREFIX, currentRound), concatKey(PAPER_BALANCE_ROUND_PREFIX, account))
    Put(GetContext(), roundPaperBalanceKey, Add(getRoundPaperBalance(account, currentRound), paperAmount))

    # update profitPerPaper
    oldProfitPerPaper = Get(GetContext(), PROFIT_PER_PAPER_KEY)
    oldTotalPaperAmount = getTotalPaper()

    if oldTotalPaperAmount != 0:
        profitPerPaperToBeAdd = Div(Mul(dividend, MagnitudeForProfitPerPaper), oldTotalPaperAmount)
        # update profitPerPaper
        Put(GetContext(), PROFIT_PER_PAPER_KEY, Add(profitPerPaperToBeAdd, oldProfitPerPaper))
    else:
        # if current total paper is ZERO, the dividend will be assigned as the commission part
        Put(GetContext(), COMMISSION_KEY, Add(dividend, getCommissionAmount()))

    updateDividendBalance(account)

    # if not getPaperBalanceBeforeUpgrade(account):
    #     # record the paper balance before contract upgrades
    #     Put(GetContext(), concatKey(PAPER_BALANCE_BEFORE_UPGRADE_PREFIX, account), getPaperBalance(account))

    # update paper balance of account
    newPaperBalance = Get(GetContext(), concatKey(NEW_PAPER_BALANCE_PREFIX, account))
    Put(GetContext(), concatKey(NEW_PAPER_BALANCE_PREFIX, account), Add(paperAmount, newPaperBalance))

    # update total paper amount
    Put(GetContext(), TOTAL_PAPER_KEY, Add(paperAmount, getTotalPaper()))

    # update the account balances of dividend, award, referral
    ongAmountNeedToBeDeduct = ongAmount
    if ongAmountNeedToBeDeduct >= dividendBalance:
        ongAmountNeedToBeDeduct = Sub(ongAmountNeedToBeDeduct, dividendBalance)
        Delete(GetContext(), concatKey(TOTAL_DIVIDEND_OF_PREFIX, account))
    else:
        Put(GetContext(), concatKey(TOTAL_DIVIDEND_OF_PREFIX, account), Sub(dividendBalance, ongAmountNeedToBeDeduct))
        ongAmountNeedToBeDeduct = 0
    if ongAmountNeedToBeDeduct != 0:
        if ongAmountNeedToBeDeduct >= referralBalance:
            ongAmountNeedToBeDeduct = Sub(ongAmountNeedToBeDeduct, referralBalance)
            Delete(GetContext(), concatKey(REFERRAL_BALANCE_OF_PREFIX, account))
        else:
            Put(GetContext(), concatKey(REFERRAL_BALANCE_OF_PREFIX, account), Sub(referralBalance, ongAmountNeedToBeDeduct))
            ongAmountNeedToBeDeduct = 0
    if ongAmountNeedToBeDeduct != 0:
        if ongAmountNeedToBeDeduct > awardBalance:
            raise Exception("Reinvest failed!")
        else:
            Put(GetContext(), concatKey(AWARD_BALANCE_OF_PREFFIX, account), Sub(awardBalance, ongAmountNeedToBeDeduct))

    # PurchaseEvent(account, ongAmount, paperAmount)
    Notify(["reBuyPaper", account, ongAmount, paperAmount, GetTime()])

    return True


def fillPaper(account, guessNumberList):
    """
    :param account:
    :param guessNumberList: can be a list of numbers
    :return:
    """
    # RequireWitness(account)
    if CheckWitness(account) == False:
        # "Check witness failed!",
        Notify(["FillPaperError", 1000])
        return False

    currentRound = getCurrentRound()

    # Require(getGameStatus(currentRound) == STATUS_ON)
    if getGameStatus(currentRound) == STATUS_OFF:
        #  "Current round game status off!",
        Notify(["FillPaperError", 1001])
        return False

    # to prevent hack from other contract
    callerHash = GetCallingScriptHash()
    entryHash = GetEntryScriptHash()
    Require(callerHash == entryHash)

    guessNumberLen = len(guessNumberList)

    # Require(guessNumberLen >= 1)
    if guessNumberLen < 1:
        #  "Guess number list illegal!",
        Notify(["FillPaperError", 1004])

    currentPaperBalance = getPaperBalance(account)

    # make sure his balance is greater or equal to guessNumberList length
    # Require(currentPaperBalance >= guessNumberLen)
    if currentPaperBalance < guessNumberLen:
        #  "Not enough paper balance to fill papers!",
        Notify(["FillPaperError", 1005])
        return False

    numberListKey = concatKey(concatKey(ROUND_PREFIX, currentRound), FILLED_NUMBER_LIST_KEY)
    numberListInfo = Get(GetContext(), numberListKey)
    numberList = []
    if numberListInfo:
        numberList = Deserialize(numberListInfo)

    for guessNumber in guessNumberList:

        # Require is need to raise exception
        Require(guessNumber < 100)
        Require(guessNumber >= 0)

        numberPlayersListKey = concatKey(concatKey(ROUND_PREFIX, currentRound), concatKey(FILLED_NUMBER_KEY, guessNumber))
        numberPlayersListInfo = Get(GetContext(), numberPlayersListKey)

        numberPlayersList = []
        if numberPlayersListInfo:
            numberPlayersList = Deserialize(numberPlayersListInfo)

            # make sure account has NOT filled the number before in this round
            for player in numberPlayersList:
                Require(player != account)
        else:
            numberList.append(guessNumber)

        # add account to the players list that filled the number in this round
        numberPlayersList.append(account)

        # Store the numberPlayers List
        numberPlayersListInfo = Serialize(numberPlayersList)
        Put(GetContext(), numberPlayersListKey, numberPlayersListInfo)
    # Store the numberList
    numberListInfo = Serialize(numberList)
    Put(GetContext(), numberListKey, numberListInfo)

    # update dividend
    updateDividendBalance(account)

    # update fillPaperFromRound and the round paper balance
    fillPaperFromRound = getFillPaperFromRound(account)
    Notify(["111fillPaper", fillPaperFromRound, currentRound])
    # oldPaperBalanceKey = concatKey(PAPER_BALANCE_PREFIX, account)
    # oldPaperBalance = Get(GetContext(), oldPaperBalanceKey)
    awardVaultToBeAddAtFill = 0
    if fillPaperFromRound == 0:
        oldPaperBalanceKey  = concatKey(PAPER_BALANCE_PREFIX, account)
        oldPaperBalance = Get(GetContext(), oldPaperBalanceKey)
        Notify(["222fillPaper", oldPaperBalance, guessNumberLen])
        if oldPaperBalance> guessNumberLen:
            Put(GetContext(), oldPaperBalanceKey, Sub(oldPaperBalance, guessNumberLen))

        else:
            Delete(GetContext(), oldPaperBalanceKey)
            fillPaperBalanceNeedtoUpdate = Sub(guessNumberLen, oldPaperBalance)
            Notify(["333fillPaper", fillPaperBalanceNeedtoUpdate])
            if fillPaperBalanceNeedtoUpdate > 0:
                # update FillPaperFromRound and the account's round paper balance and awardVault
                awardVaultToBeAddAtFill = _updateFillPaperFromRoundAndAwardVault(account, 1, fillPaperBalanceNeedtoUpdate)
                # update the awardVaultAtFill
                Put(GetContext(), TOTAL_ONG_TO_BE_ADD_AT_FILL_KEY, Sub(getTotalONGToBeAddAtFill(), awardVaultToBeAddAtFill))

                # update the paper balance of account  -- destroy the filled papers
                Put(GetContext(), concatKey(NEW_PAPER_BALANCE_PREFIX, account), Sub(currentPaperBalance, guessNumberLen))
            else:
                # update FillPaperFromRound and the account's round paper balance
                Put(GetContext(), concatKey(FILL_PAPER_FROM_ROUND_PREFIX, account), 1)

    else:
        # update FillPaperFromRound and the account's round paper balance and awardVault
        Notify(["444fillPaper", account, fillPaperFromRound, guessNumberLen])
        awardVaultToBeAddAtFill = _updateFillPaperFromRoundAndAwardVault(account, fillPaperFromRound, guessNumberLen)

        # update the awardVaultAtFill
        Put(GetContext(), TOTAL_ONG_TO_BE_ADD_AT_FILL_KEY, Sub(getTotalONGToBeAddAtFill(), awardVaultToBeAddAtFill))

        # update the paper balance of account  -- destroy the filled papers
        Put(GetContext(), concatKey(NEW_PAPER_BALANCE_PREFIX, account), Sub(currentPaperBalance, guessNumberLen))

    # update total paper amount
    Put(GetContext(), TOTAL_PAPER_KEY, Sub(getTotalPaper(), guessNumberLen))

    # update the filled paper balance of account in current round
    key1 = concatKey(ROUND_PREFIX, currentRound)
    key2 = concatKey(FILLED_PAPER_BALANCE_PREFIX, account)
    key = concatKey(key1, key2)
    Put(GetContext(), key, Add(guessNumberLen, getFilledPaperBalance(account, currentRound)))

    # update the filled paper amount in current round
    key = concatKey(concatKey(ROUND_PREFIX, currentRound), FILLED_PAPER_AMOUNT)
    Put(GetContext(), key, Add(guessNumberLen, getFilledPaperAmount(currentRound)))

    Notify(["fillPaper", account, guessNumberList, GetTime(), currentRound])

    return True


def withdraw(account):
    """
    account will withdraw his dividend and award to his own account
    :param account:
    :return:
    """
    RequireWitness(account)

    updateDividendBalance(account)
    dividendBalance = getDividendBalance(account)
    awardBalance = getAwardBalance(account)
    referralBalance = getReferralBalance(account)
    assetToBeWithdrawn = Add(Add(dividendBalance, awardBalance), referralBalance)

    # Require(assetToBeWithdrawn > 0)
    if assetToBeWithdrawn <= 0:
        # Not enought ONG to be withdrawn
        Notify(["withdrawONGError", 1008])
        return False
    # Require(transferONGFromContact(account, assetToBeWithdrawn))
    res = transferONGFromContact(account, assetToBeWithdrawn)
    if res == False:
        # please withdraw ONG later, or try again
        Notify(["transerONGError", 1009])
        return False

    Delete(GetContext(), concatKey(TOTAL_DIVIDEND_OF_PREFIX, account))
    Delete(GetContext(), concatKey(AWARD_BALANCE_OF_PREFFIX, account))
    Delete(GetContext(), concatKey(REFERRAL_BALANCE_OF_PREFIX, account))

    # update total ong amount
    Put(GetContext(), TOTAL_ONG_KEY, Sub(getTotalONGAmount(), assetToBeWithdrawn))

    Notify(["withdraw", ContractAddress, account, assetToBeWithdrawn, GetTime()])

    return True


def updateDividendBalance(account):
    """
    reset PROFIT_PER_PAPER_FROM_PREFIX of account and update account's dividend till now
    :param account:
    :return:
    """
    # RequireWitness(account)
    key = concatKey(PROFIT_PER_PAPER_FROM_PREFIX, account)
    profitPerPaperFrom = Get(GetContext(), key)
    profitPerPaperNow = getProfitPerPaper()
    profitPerPaper = Sub(profitPerPaperNow, profitPerPaperFrom)

    if profitPerPaper != 0:
        Put(GetContext(), concatKey(TOTAL_DIVIDEND_OF_PREFIX, account), getDividendBalance(account))
        Put(GetContext(), concatKey(PROFIT_PER_PAPER_FROM_PREFIX, account), profitPerPaperNow)
    return True
######################## Methods for Users End ######################################


################## Global Info Start #######################
def getTotalONGAmount():
    return Get(GetContext(), TOTAL_ONG_KEY)

def getTotalPaper():
    return Get(GetContext(), TOTAL_PAPER_KEY)

def getGasVault():
    return Get(GetContext(), GAS_VAULT_KEY)

def getCurrentRound():
    return Get(GetContext(), CURRET_ROUND_NUM_KEY)

def getCurrentRoundEndTime():
    currentRound = getCurrentRound()
    currentRoundEndTime = Add(StartTime, Mul(currentRound, Mul(RoundDurationMinutes, 60)))
    return currentRoundEndTime

def getCommissionAmount():
    return Get(GetContext(), COMMISSION_KEY)

def getProfitPerPaper():
    return Get(GetContext(), PROFIT_PER_PAPER_KEY)

def getHolderPercentage(roundNumber):
    return Get(GetContext(), concatKey(HOLDER_PERCENTAGE_KEY, roundNumber))

def getReferralPercentage(roundNumber):
    return Get(GetContext(), concatKey(REFERRAL_PERCENTAGE_KEY, roundNumber))

def getAwardAtBuyPercentage(roundNumber):
    return Get(GetContext(), concatKey(AWARD_AT_BUY_PERCENTAGE_KEY, roundNumber))

def getAwardAtFillPercentage(roundNumber):
    return Get(GetContext(), concatKey(AWARD_AT_FILL_PERCENTAGE_KEY, roundNumber))

def getParametersPercentage(roundNumber):
    return [getHolderPercentage(roundNumber), getReferralPercentage(roundNumber), getAwardAtBuyPercentage(roundNumber), getAwardAtFillPercentage(roundNumber)]

def getTotalONGToBeAddAtFill():
    return Get(GetContext(), TOTAL_ONG_TO_BE_ADD_AT_FILL_KEY)

def getFillPaperFromRound(account):
    return Get(GetContext(), concatKey(FILL_PAPER_FROM_ROUND_PREFIX, account))
################## Global Info End #######################


####################### User Info Start #####################
def getPaperBalance(account):
    return Add(Get(GetContext(), concatKey(NEW_PAPER_BALANCE_PREFIX, account)), Get(GetContext(), concatKey(PAPER_BALANCE_PREFIX, account)))

def getPaperBalanceBeforeUpgrade(account):
    return Get(GetContext(), concatKey(PAPER_BALANCE_BEFORE_UPGRADE_PREFIX, account))

def getReferralBalance(account):
    return Get(GetContext(), concatKey(REFERRAL_BALANCE_OF_PREFIX, account))

def getDividendBalance(account):
    key = concatKey(PROFIT_PER_PAPER_FROM_PREFIX, account)
    profitPerPaperFrom = Get(GetContext(), key)
    profitPerPaperNow = Get(GetContext(), PROFIT_PER_PAPER_KEY)
    profitPerPaper = profitPerPaperNow - profitPerPaperFrom
    profit = 0
    if profitPerPaper != 0:
        profit = Div(Mul(profitPerPaper, getPaperBalance(account)), MagnitudeForProfitPerPaper)
    return Add(Get(GetContext(), concatKey(TOTAL_DIVIDEND_OF_PREFIX, account)), profit)

def getAwardBalance(account):
    return Get(GetContext(), concatKey(AWARD_BALANCE_OF_PREFFIX, account))

def getDividendsBalance(account):
    return [getReferralBalance(account), getDividendBalance(account), getAwardBalance(account)]

def getReferral(account):
    return Get(GetContext(), concatKey(REFERRAL_PREFIX, account))

def getFilledPaperBalance(account, roundNum):
    key1 = concatKey(ROUND_PREFIX, roundNum)
    key2 = concatKey(FILLED_PAPER_BALANCE_PREFIX, account)
    return Get(GetContext(), concatKey(key1, key2))
def getRoundPaperBalance(account, roundNum):
    roundPaperBalanceKey = concatKey(concatKey(ROUND_PREFIX, roundNum), concatKey(PAPER_BALANCE_ROUND_PREFIX, account))
    return Get(GetContext(), roundPaperBalanceKey)

def getRoundAssignPaperBalance(account, roundNum):
    roundAssignPaperBalanceKey = concatKey(concatKey(ROUND_PREFIX, roundNum), concatKey(ASSIGN_PAPER_BALANCE_ROUND_PREFIX, account))
    return Get(GetContext(), roundAssignPaperBalanceKey)
####################### User Info Start #####################


####################### Round Info Start #############################
def getAwardVault(roundNum):
    return Get(GetContext(), concatKey(concatKey(ROUND_PREFIX, roundNum), AWARD_VAULT_KEY))

def getGameStatus(roundNum):
    return Get(GetContext(), concatKey(concatKey(ROUND_PREFIX, roundNum), ROUND_STATUS_KEY))

def getFilledPaperAmount(roundNum):
    key = concatKey(concatKey(ROUND_PREFIX, roundNum), FILLED_PAPER_AMOUNT)
    return Get(GetContext(), key)

def getWinInfo(roundNum):
    key = concatKey(concatKey(ROUND_PREFIX, roundNum), WINNER_KEY)
    winListInfo = Get(GetContext(), key)
    winList = Deserialize(winListInfo)
    generatedLuckyNumber = winList[0]
    actualLuckyNumberList = Deserialize(winList[1])
    allWinnerList = []
    for actualLuckyNumber in actualLuckyNumberList:
        key = concatKey(concatKey(ROUND_PREFIX, roundNum), concatKey(FILLED_NUMBER_KEY, actualLuckyNumber))
        winnersListInfo = Get(GetContext(), key)
        winnersList = Deserialize(winnersListInfo)
        allWinnerList.append(winnersList)
    winAwardList = Deserialize(winList[2])
    return [generatedLuckyNumber, actualLuckyNumberList,allWinnerList, winAwardList]

def getFilledNumberList(roundNum):
    numberListKey = concatKey(concatKey(ROUND_PREFIX, roundNum), FILLED_NUMBER_LIST_KEY)
    numberListInfo = Get(GetContext(), numberListKey)
    numberList = []
    if numberListInfo:
        numberList = Deserialize(numberListInfo)
    return numberList

def getPlayersList(roundNum, guessNumber):
    numberPlayersKey = concatKey(concatKey(ROUND_PREFIX, roundNum), concatKey(FILLED_NUMBER_KEY, guessNumber))
    numberPlayersInfo = Get(GetContext(), numberPlayersKey)

    numberPlayers = []
    if numberPlayersInfo:
        numberPlayers = Deserialize(numberPlayersInfo)

    return numberPlayers

def getPlayerGuessedNumber(roundNum, account):
    playerGuessedNumberList = []
    numberListKey = concatKey(concatKey(ROUND_PREFIX, roundNum), FILLED_NUMBER_LIST_KEY)
    numberListInfo = Get(GetContext(), numberListKey)
    numberList = []

    if numberListInfo:
        numberList = Deserialize(numberListInfo)
    else:
        return playerGuessedNumberList

    for number in numberList:
        numberPlayersListKey = concatKey(concatKey(ROUND_PREFIX, roundNum), concatKey(FILLED_NUMBER_KEY, number))
        numberPlayersListInfo = Get(GetContext(), numberPlayersListKey)
        if numberPlayersListInfo:
            numberPlayersList = Deserialize(numberPlayersListInfo)
            if checkAccountInList(account, numberPlayersList) != False:
                playerGuessedNumberList.append(number)
    return playerGuessedNumberList
####################### Round Info End #############################


######################### Utility Methods Start #########################
def getLuckyNumber():
    """
    Generate the lucky number in specific round
    :return:
    """
    blockHash = GetCurrentBlockHash()
    # The number should be in the range from 0 to 99
    luckyNumber = abs(blockHash) % 100
    luckyNumber = abs(luckyNumber)
    return luckyNumber

def checkAccountInList(account, playerList):
    for player in playerList:
        if account == player:
            return account
    return False

def paperToONG(paperAmount):
    ongAmount = Mul(InitialPrice, paperAmount)
    return ongAmount

def transferONG(fromAcct, toAcct, amount):
    """
    transfer ONG
    :param fromacct:
    :param toacct:
    :param amount:
    :return:
    """
    RequireWitness(fromAcct)
    param = state(fromAcct, toAcct, amount)
    res = Invoke(0, ONGAddress, 'transfer', [param])
    if res and res == b'\x01':
        return True
    else:
        return False

def transferONGFromContact(toAcct, amount):
    param = state(ContractAddress, toAcct, amount)
    res = Invoke(0, ONGAddress, 'transfer', [param])
    if res and res == b'\x01':
        return True
    else:
        return False

def concatKey(str1,str2):
    """
    connect str1 and str2 together as a key
    :param str1: string1
    :param str2:  string2
    :return: string1_string2
    """
    return concat(concat(str1, '_'), str2)
######################### Utility Methods End #########################