from cdp.openapi_client.models.eth_value_criterion import EthValueCriterion
from cdp.openapi_client.models.evm_address_criterion import EvmAddressCriterion
from cdp.openapi_client.models.evm_data_condition import EvmDataCondition as OpenAPIEvmDataCondition
from cdp.openapi_client.models.evm_data_condition_params_inner import EvmDataConditionParamsInner
from cdp.openapi_client.models.evm_data_criterion import EvmDataCriterion
from cdp.openapi_client.models.evm_data_criterion_abi import EvmDataCriterionAbi
from cdp.openapi_client.models.evm_data_parameter_condition import EvmDataParameterCondition
from cdp.openapi_client.models.evm_data_parameter_condition_list import (
    EvmDataParameterConditionList,
)
from cdp.openapi_client.models.evm_message_criterion import EvmMessageCriterion
from cdp.openapi_client.models.evm_network_criterion import EvmNetworkCriterion
from cdp.openapi_client.models.evm_typed_address_condition import EvmTypedAddressCondition
from cdp.openapi_client.models.evm_typed_numerical_condition import EvmTypedNumericalCondition
from cdp.openapi_client.models.evm_typed_string_condition import EvmTypedStringCondition
from cdp.openapi_client.models.idl import Idl
from cdp.openapi_client.models.known_abi_type import KnownAbiType
from cdp.openapi_client.models.known_idl_type import KnownIdlType
from cdp.openapi_client.models.mint_address_criterion import MintAddressCriterion
from cdp.openapi_client.models.net_usd_change_criterion import NetUSDChangeCriterion
from cdp.openapi_client.models.prepare_user_operation_rule import PrepareUserOperationRule
from cdp.openapi_client.models.program_id_criterion import ProgramIdCriterion
from cdp.openapi_client.models.rule import Rule
from cdp.openapi_client.models.send_evm_transaction_criteria_inner import (
    SendEvmTransactionCriteriaInner,
)
from cdp.openapi_client.models.send_evm_transaction_rule import SendEvmTransactionRule
from cdp.openapi_client.models.send_sol_transaction_criteria_inner import (
    SendSolTransactionCriteriaInner,
)
from cdp.openapi_client.models.send_sol_transaction_rule import SendSolTransactionRule
from cdp.openapi_client.models.send_user_operation_rule import SendUserOperationRule
from cdp.openapi_client.models.sign_evm_hash_rule import SignEvmHashRule
from cdp.openapi_client.models.sign_evm_message_criteria_inner import SignEvmMessageCriteriaInner
from cdp.openapi_client.models.sign_evm_message_rule import SignEvmMessageRule
from cdp.openapi_client.models.sign_evm_transaction_criteria_inner import (
    SignEvmTransactionCriteriaInner,
)
from cdp.openapi_client.models.sign_evm_transaction_rule import SignEvmTransactionRule
from cdp.openapi_client.models.sign_evm_typed_data_criteria_inner import (
    SignEvmTypedDataCriteriaInner,
)
from cdp.openapi_client.models.sign_evm_typed_data_field_criterion import (
    SignEvmTypedDataFieldCriterion,
)
from cdp.openapi_client.models.sign_evm_typed_data_field_criterion_conditions_inner import (
    SignEvmTypedDataFieldCriterionConditionsInner,
)
from cdp.openapi_client.models.sign_evm_typed_data_field_criterion_types import (
    SignEvmTypedDataFieldCriterionTypes,
)
from cdp.openapi_client.models.sign_evm_typed_data_rule import SignEvmTypedDataRule
from cdp.openapi_client.models.sign_evm_typed_data_verifying_contract_criterion import (
    SignEvmTypedDataVerifyingContractCriterion,
)
from cdp.openapi_client.models.sign_sol_message_criteria_inner import SignSolMessageCriteriaInner
from cdp.openapi_client.models.sign_sol_message_rule import SignSolMessageRule
from cdp.openapi_client.models.sign_sol_transaction_criteria_inner import (
    SignSolTransactionCriteriaInner,
)
from cdp.openapi_client.models.sign_sol_transaction_rule import SignSolTransactionRule
from cdp.openapi_client.models.sol_address_criterion import SolAddressCriterion
from cdp.openapi_client.models.sol_data_condition import SolDataCondition
from cdp.openapi_client.models.sol_data_condition_params_inner import SolDataConditionParamsInner
from cdp.openapi_client.models.sol_data_criterion import SolDataCriterion
from cdp.openapi_client.models.sol_data_criterion_idls_inner import SolDataCriterionIdlsInner
from cdp.openapi_client.models.sol_data_parameter_condition import SolDataParameterCondition
from cdp.openapi_client.models.sol_data_parameter_condition_list import (
    SolDataParameterConditionList,
)
from cdp.openapi_client.models.sol_message_criterion import SolMessageCriterion
from cdp.openapi_client.models.sol_network_criterion import SolNetworkCriterion
from cdp.openapi_client.models.sol_value_criterion import SolValueCriterion
from cdp.openapi_client.models.spl_address_criterion import SplAddressCriterion
from cdp.openapi_client.models.spl_value_criterion import SplValueCriterion
from cdp.policies.types import Rule as RuleType

# OpenAPI criterion constructor mapping per operation
openapi_criterion_mapping = {
    "sendEvmTransaction": {
        "ethValue": lambda c: SendEvmTransactionCriteriaInner(
            actual_instance=EthValueCriterion(
                eth_value=c.ethValue,
                operator=c.operator,
                type="ethValue",
            )
        ),
        "evmAddress": lambda c: SendEvmTransactionCriteriaInner(
            actual_instance=EvmAddressCriterion(
                addresses=c.addresses,
                operator=c.operator,
                type="evmAddress",
            )
        ),
        "evmNetwork": lambda c: SendEvmTransactionCriteriaInner(
            actual_instance=EvmNetworkCriterion(
                networks=c.networks,
                operator=c.operator,
                type="evmNetwork",
            )
        ),
        "netUSDChange": lambda c: SendEvmTransactionCriteriaInner(
            actual_instance=NetUSDChangeCriterion(
                change_cents=c.changeCents,
                operator=c.operator,
                type="netUSDChange",
            )
        ),
        "evmData": lambda c: SendEvmTransactionCriteriaInner(
            actual_instance=EvmDataCriterion(
                type="evmData",
                abi=EvmDataCriterionAbi(
                    actual_instance=(KnownAbiType(c.abi) if isinstance(c.abi, str) else c.abi)
                ),
                conditions=[
                    OpenAPIEvmDataCondition(
                        function=cond.function,
                        params=[
                            EvmDataConditionParamsInner(
                                actual_instance=(
                                    EvmDataParameterConditionList(
                                        name=param.name,
                                        operator=param.operator,
                                        values=param.values,
                                    )
                                    if hasattr(param, "values")
                                    else EvmDataParameterCondition(
                                        name=param.name,
                                        operator=param.operator,
                                        value=param.value,
                                    )
                                )
                            )
                            for param in cond.params
                        ]
                        if cond.params
                        else None,
                    )
                    for cond in c.conditions
                ],
            )
        ),
    },
    "signEvmTransaction": {
        "ethValue": lambda c: SignEvmTransactionCriteriaInner(
            actual_instance=EthValueCriterion(
                eth_value=c.ethValue,
                operator=c.operator,
                type="ethValue",
            )
        ),
        "evmAddress": lambda c: SignEvmTransactionCriteriaInner(
            actual_instance=EvmAddressCriterion(
                addresses=c.addresses,
                operator=c.operator,
                type="evmAddress",
            )
        ),
        "netUSDChange": lambda c: SignEvmTransactionCriteriaInner(
            actual_instance=NetUSDChangeCriterion(
                change_cents=c.changeCents,
                operator=c.operator,
                type="netUSDChange",
            )
        ),
        "evmData": lambda c: SignEvmTransactionCriteriaInner(
            actual_instance=EvmDataCriterion(
                type="evmData",
                abi=EvmDataCriterionAbi(
                    actual_instance=(KnownAbiType(c.abi) if isinstance(c.abi, str) else c.abi)
                ),
                conditions=[
                    OpenAPIEvmDataCondition(
                        function=cond.function,
                        params=[
                            EvmDataConditionParamsInner(
                                actual_instance=(
                                    EvmDataParameterConditionList(
                                        name=param.name,
                                        operator=param.operator,
                                        values=param.values,
                                    )
                                    if hasattr(param, "values")
                                    else EvmDataParameterCondition(
                                        name=param.name,
                                        operator=param.operator,
                                        value=param.value,
                                    )
                                )
                            )
                            for param in cond.params
                        ]
                        if cond.params
                        else None,
                    )
                    for cond in c.conditions
                ],
            )
        ),
    },
    "signEvmHash": {},
    "signEvmMessage": {
        "evmMessage": lambda c: SignEvmMessageCriteriaInner(
            actual_instance=EvmMessageCriterion(
                match=c.match,
                type="evmMessage",
            )
        ),
    },
    "signEvmTypedData": {
        "evmTypedDataField": lambda c: SignEvmTypedDataCriteriaInner(
            actual_instance=SignEvmTypedDataFieldCriterion(
                type="evmTypedDataField",
                types=SignEvmTypedDataFieldCriterionTypes(
                    types=c.types.types,
                    primary_type=c.types.primaryType,
                ),
                conditions=[
                    SignEvmTypedDataFieldCriterionConditionsInner(
                        actual_instance=(
                            EvmTypedAddressCondition(
                                addresses=cond.addresses,
                                operator=cond.operator,
                                path=cond.path,
                            )
                            if hasattr(cond, "addresses")
                            else EvmTypedNumericalCondition(
                                value=cond.value,
                                operator=cond.operator,
                                path=cond.path,
                            )
                            if hasattr(cond, "value")
                            else EvmTypedStringCondition(
                                match=cond.match,
                                path=cond.path,
                            )
                        )
                    )
                    for cond in c.conditions
                ],
            )
        ),
        "evmTypedDataVerifyingContract": lambda c: SignEvmTypedDataCriteriaInner(
            actual_instance=SignEvmTypedDataVerifyingContractCriterion(
                type="evmTypedDataVerifyingContract",
                addresses=c.addresses,
                operator=c.operator,
            )
        ),
    },
    "signSolTransaction": {
        "solAddress": lambda c: SignSolTransactionCriteriaInner(
            actual_instance=SolAddressCriterion(
                addresses=c.addresses,
                operator=c.operator,
                type="solAddress",
            )
        ),
        "solValue": lambda c: SignSolTransactionCriteriaInner(
            actual_instance=SolValueCriterion(
                sol_value=c.solValue,
                operator=c.operator,
                type="solValue",
            )
        ),
        "splAddress": lambda c: SignSolTransactionCriteriaInner(
            actual_instance=SplAddressCriterion(
                addresses=c.addresses,
                operator=c.operator,
                type="splAddress",
            )
        ),
        "splValue": lambda c: SignSolTransactionCriteriaInner(
            actual_instance=SplValueCriterion(
                spl_value=c.splValue,
                operator=c.operator,
                type="splValue",
            )
        ),
        "mintAddress": lambda c: SignSolTransactionCriteriaInner(
            actual_instance=MintAddressCriterion(
                addresses=c.addresses,
                operator=c.operator,
                type="mintAddress",
            )
        ),
        "solData": lambda c: SignSolTransactionCriteriaInner(
            actual_instance=SolDataCriterion(
                type="solData",
                idls=[
                    SolDataCriterionIdlsInner(
                        actual_instance=(
                            KnownIdlType(idl)
                            if isinstance(idl, str)
                            else Idl(
                                address=idl.address,
                                instructions=idl.instructions,
                            )
                        )
                    )
                    for idl in c.idls
                ],
                conditions=[
                    SolDataCondition(
                        instruction=cond.instruction,
                        params=[
                            SolDataConditionParamsInner(
                                actual_instance=(
                                    SolDataParameterConditionList(
                                        name=param.name,
                                        operator=param.operator,
                                        values=param.values,
                                    )
                                    if hasattr(param, "values")
                                    else SolDataParameterCondition(
                                        name=param.name,
                                        operator=param.operator,
                                        value=param.value,
                                    )
                                )
                            )
                            for param in cond.params
                        ]
                        if cond.params
                        else None,
                    )
                    for cond in c.conditions
                ],
            )
        ),
        "programId": lambda c: SignSolTransactionCriteriaInner(
            actual_instance=ProgramIdCriterion(
                program_ids=c.programIds,
                operator=c.operator,
                type="programId",
            )
        ),
    },
    "sendSolTransaction": {
        "solAddress": lambda c: SendSolTransactionCriteriaInner(
            actual_instance=SolAddressCriterion(
                addresses=c.addresses,
                operator=c.operator,
                type="solAddress",
            )
        ),
        "solValue": lambda c: SendSolTransactionCriteriaInner(
            actual_instance=SolValueCriterion(
                sol_value=c.solValue,
                operator=c.operator,
                type="solValue",
            )
        ),
        "splAddress": lambda c: SendSolTransactionCriteriaInner(
            actual_instance=SplAddressCriterion(
                addresses=c.addresses,
                operator=c.operator,
                type="splAddress",
            )
        ),
        "splValue": lambda c: SendSolTransactionCriteriaInner(
            actual_instance=SplValueCriterion(
                spl_value=c.splValue,
                operator=c.operator,
                type="splValue",
            )
        ),
        "mintAddress": lambda c: SendSolTransactionCriteriaInner(
            actual_instance=MintAddressCriterion(
                addresses=c.addresses,
                operator=c.operator,
                type="mintAddress",
            )
        ),
        "solData": lambda c: SignSolTransactionCriteriaInner(
            actual_instance=SolDataCriterion(
                type="solData",
                idls=[
                    SolDataCriterionIdlsInner(
                        actual_instance=(
                            KnownIdlType(idl)
                            if isinstance(idl, str)
                            else Idl(
                                address=idl.address,
                                instructions=idl.instructions,
                            )
                        )
                    )
                    for idl in c.idls
                ],
                conditions=[
                    SolDataCondition(
                        instruction=cond.instruction,
                        params=[
                            SolDataConditionParamsInner(
                                actual_instance=(
                                    SolDataParameterConditionList(
                                        name=param.name,
                                        operator=param.operator,
                                        values=param.values,
                                    )
                                    if hasattr(param, "values")
                                    else SolDataParameterCondition(
                                        name=param.name,
                                        operator=param.operator,
                                        value=param.value,
                                    )
                                )
                            )
                            for param in cond.params
                        ]
                        if cond.params
                        else None,
                    )
                    for cond in c.conditions
                ],
            )
        ),
        "programId": lambda c: SendSolTransactionCriteriaInner(
            actual_instance=ProgramIdCriterion(
                program_ids=c.programIds,
                operator=c.operator,
                type="programId",
            )
        ),
        "solNetwork": lambda c: SendSolTransactionCriteriaInner(
            actual_instance=SolNetworkCriterion(
                networks=c.networks,
                operator=c.operator,
                type="solNetwork",
            )
        ),
    },
    "signSolMessage": {
        "solMessage": lambda c: SignSolMessageCriteriaInner(
            actual_instance=SolMessageCriterion(
                type="solMessage",
                match=c.match,
            )
        ),
    },
    "prepareUserOperation": {
        "ethValue": lambda c: SendEvmTransactionCriteriaInner(
            actual_instance=EthValueCriterion(
                eth_value=c.ethValue,
                operator=c.operator,
                type="ethValue",
            )
        ),
        "evmAddress": lambda c: SendEvmTransactionCriteriaInner(
            actual_instance=EvmAddressCriterion(
                addresses=c.addresses,
                operator=c.operator,
                type="evmAddress",
            )
        ),
        "evmNetwork": lambda c: SendEvmTransactionCriteriaInner(
            actual_instance=EvmNetworkCriterion(
                networks=c.networks,
                operator=c.operator,
                type="evmNetwork",
            )
        ),
        "netUSDChange": lambda c: SendEvmTransactionCriteriaInner(
            actual_instance=NetUSDChangeCriterion(
                change_cents=c.changeCents,
                operator=c.operator,
                type="netUSDChange",
            )
        ),
        "evmData": lambda c: SendEvmTransactionCriteriaInner(
            actual_instance=EvmDataCriterion(
                type="evmData",
                abi=EvmDataCriterionAbi(
                    actual_instance=(KnownAbiType(c.abi) if isinstance(c.abi, str) else c.abi)
                ),
                conditions=[
                    OpenAPIEvmDataCondition(
                        function=cond.function,
                        params=[
                            EvmDataConditionParamsInner(
                                actual_instance=(
                                    EvmDataParameterConditionList(
                                        name=param.name,
                                        operator=param.operator,
                                        values=param.values,
                                    )
                                    if hasattr(param, "values")
                                    else EvmDataParameterCondition(
                                        name=param.name,
                                        operator=param.operator,
                                        value=param.value,
                                    )
                                )
                            )
                            for param in cond.params
                        ]
                        if cond.params
                        else None,
                    )
                    for cond in c.conditions
                ],
            )
        ),
    },
    "sendUserOperation": {
        "ethValue": lambda c: SignEvmTransactionCriteriaInner(
            actual_instance=EthValueCriterion(
                eth_value=c.ethValue,
                operator=c.operator,
                type="ethValue",
            )
        ),
        "evmAddress": lambda c: SignEvmTransactionCriteriaInner(
            actual_instance=EvmAddressCriterion(
                addresses=c.addresses,
                operator=c.operator,
                type="evmAddress",
            )
        ),
        "netUSDChange": lambda c: SignEvmTransactionCriteriaInner(
            actual_instance=NetUSDChangeCriterion(
                change_cents=c.changeCents,
                operator=c.operator,
                type="netUSDChange",
            )
        ),
        "evmData": lambda c: SignEvmTransactionCriteriaInner(
            actual_instance=EvmDataCriterion(
                type="evmData",
                abi=EvmDataCriterionAbi(
                    actual_instance=(KnownAbiType(c.abi) if isinstance(c.abi, str) else c.abi)
                ),
                conditions=[
                    OpenAPIEvmDataCondition(
                        function=cond.function,
                        params=[
                            EvmDataConditionParamsInner(
                                actual_instance=(
                                    EvmDataParameterConditionList(
                                        name=param.name,
                                        operator=param.operator,
                                        values=param.values,
                                    )
                                    if hasattr(param, "values")
                                    else EvmDataParameterCondition(
                                        name=param.name,
                                        operator=param.operator,
                                        value=param.value,
                                    )
                                )
                            )
                            for param in cond.params
                        ]
                        if cond.params
                        else None,
                    )
                    for cond in c.conditions
                ],
            )
        ),
    },
}

# OpenAPI rule constructor mapping
openapi_rule_mapping = {
    "sendEvmTransaction": SendEvmTransactionRule,
    "signEvmTransaction": SignEvmTransactionRule,
    "signEvmHash": SignEvmHashRule,
    "signEvmMessage": SignEvmMessageRule,
    "signEvmTypedData": SignEvmTypedDataRule,
    "signSolTransaction": SignSolTransactionRule,
    "sendSolTransaction": SendSolTransactionRule,
    "signSolMessage": SignSolMessageRule,
    "prepareUserOperation": PrepareUserOperationRule,
    "sendUserOperation": SendUserOperationRule,
}


def map_request_rules_to_openapi_format(request_rules: list[RuleType]) -> list[Rule]:
    """Build a properly formatted list of OpenAPI policy rules from a list of request rules.

    Args:
        request_rules (List[RuleType]): The request rules to build from.

    Returns:
        List[Rule]: A list of rules formatted for the OpenAPI policy.

    """
    rules = []
    for rule in request_rules:
        if rule.operation not in openapi_criterion_mapping:
            raise ValueError(f"Unknown operation {rule.operation}")

        rule_cls = openapi_rule_mapping[rule.operation]

        if not hasattr(rule, "criteria"):
            rules.append(
                Rule(
                    actual_instance=rule_cls(
                        action=rule.action,
                        operation=rule.operation,
                    )
                )
            )
            continue

        criteria_builders = openapi_criterion_mapping[rule.operation]
        criteria = []

        for criterion in rule.criteria:
            if criterion.type not in criteria_builders:
                raise ValueError(
                    f"Unknown criterion type {criterion.type} for operation {rule.operation}"
                )
            criteria.append(criteria_builders[criterion.type](criterion))

        rules.append(
            Rule(
                actual_instance=rule_cls(
                    action=rule.action,
                    operation=rule.operation,
                    criteria=criteria,
                )
            )
        )

    return rules
