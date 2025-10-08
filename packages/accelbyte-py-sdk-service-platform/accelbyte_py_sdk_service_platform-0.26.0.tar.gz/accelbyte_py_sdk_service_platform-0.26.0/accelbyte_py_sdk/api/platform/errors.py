# Copyright (c) 2024 AccelByte Inc. All Rights Reserved.
# This is licensed software from AccelByte Inc, for limitations
# and restrictions contact your company contract manager.
#
# Code generated. DO NOT EDIT!

# template file: errors.j2

# pylint: disable=duplicate-code
# pylint: disable=line-too-long
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-arguments
# pylint: disable=too-many-branches
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-statements
# pylint: disable=unused-import

# AccelByte Gaming Services Platform Service

from accelbyte_py_sdk.core import ApiError

ERROR_20002 = ApiError(code="20002", message="validation error")
ERROR_20006 = ApiError(code="20006", message="optimistic lock")
ERROR_20007 = ApiError(code="20007", message="too many requests")
ERROR_20008 = ApiError(
    code="20008", message="user [{userId}] does not exist in namespace [{namespace}]"
)
ERROR_20016 = ApiError(code="20016", message="action is banned")
ERROR_20018 = ApiError(code="20018", message="ecommerce item type not supported")
ERROR_20024 = ApiError(
    code="20024", message="insufficient inventory capacity (max. slots)"
)
ERROR_20027 = ApiError(code="20027", message="Invalid time range")
ERROR_30021 = ApiError(code="30021", message="Default language [{language}] required")
ERROR_30022 = ApiError(code="30022", message="Default region [{region}] is required")
ERROR_30023 = ApiError(
    code="30023", message="Catalog plugin grpc server address required"
)
ERROR_30024 = ApiError(code="30024", message="Unable to parse CSV cell [{content}]")
ERROR_30025 = ApiError(
    code="30025",
    message="[{header}] is required by CSV import/export for catalogType [{catalogType}]",
)
ERROR_30041 = ApiError(
    code="30041",
    message="Changelog [{changelogId}] does not exist in namespace [{namespace}]",
)
ERROR_30071 = ApiError(
    code="30071",
    message="Can't unselect item [{itemId}] when the item which is bound to is already selected in namespace [{namespace}]",
)
ERROR_30072 = ApiError(
    code="30072",
    message="Can't unselect category [{categoryPath}] when item with this category is already selected in namespace [{namespace}]",
)
ERROR_30073 = ApiError(code="30073", message="Can't unselect store change")
ERROR_30074 = ApiError(
    code="30074",
    message="Can't unselect subscription's content [{itemId}] when subscription is already selected in namespace [{namespace}]",
)
ERROR_30076 = ApiError(
    code="30076",
    message="CSV header [{headerName}] is not supported for CatalogType [{catalogType}]",
)
ERROR_30121 = ApiError(code="30121", message="Store data is invalid")
ERROR_30122 = ApiError(code="30122", message="Store's meta mismatch")
ERROR_30141 = ApiError(
    code="30141", message="Store [{storeId}] does not exist in namespace [{namespace}]"
)
ERROR_30142 = ApiError(
    code="30142", message="Published store does not exist in namespace [{namespace}]"
)
ERROR_30143 = ApiError(
    code="30143",
    message="Published store [{storeId}] backup does not exist in namespace [{namespace}]",
)
ERROR_30171 = ApiError(
    code="30171",
    message="Store [{store}] can't change default language to [{language}]",
)
ERROR_30172 = ApiError(
    code="30172", message="Store [{store}] can't change default region to [{region}]"
)
ERROR_30173 = ApiError(code="30173", message="Published store can't modify content")
ERROR_30174 = ApiError(
    code="30174", message="Draft store already exists in namespace [{namespace}]"
)
ERROR_30175 = ApiError(
    code="30175",
    message="Duplicated currencyCode [{currencyCode}] in Region [{region}]",
)
ERROR_30241 = ApiError(
    code="30241",
    message="Category [{categoryPath}] does not exist in namespace [{namespace}]",
)
ERROR_30271 = ApiError(
    code="30271",
    message="Category [{categoryPath}] already exists in namespace [{namespace}]",
)
ERROR_30272 = ApiError(
    code="30272",
    message="Category [{categoryPath}] is not empty in namespace [{namespace}]",
)
ERROR_30301 = ApiError(
    code="30301",
    message="Unsupported Item Type [{itemType}] for box item [{itemId}] with expiration",
)
ERROR_30321 = ApiError(code="30321", message="Invalid item discount amount")
ERROR_30322 = ApiError(code="30322", message="Bundle item [{itemId}] can't be bundled")
ERROR_30323 = ApiError(code="30323", message="Target namespace is required")
ERROR_30324 = ApiError(code="30324", message="Invalid namespace [{namespace}]")
ERROR_30325 = ApiError(code="30325", message="Code item [{itemId}] can't be bundled")
ERROR_30326 = ApiError(
    code="30326", message="Subscription item [{itemId}] can't be bundled"
)
ERROR_30327 = ApiError(code="30327", message="Invalid item trial price")
ERROR_30329 = ApiError(code="30329", message="Invalid bundled item [{itemId}] quantity")
ERROR_30330 = ApiError(
    code="30330", message="Invalid item region price currency namespace [{namespace}]"
)
ERROR_30331 = ApiError(code="30331", message="Invalid purchase condition")
ERROR_30332 = ApiError(
    code="30332", message="Invalid option box item [{itemId}] quantity"
)
ERROR_30333 = ApiError(
    code="30333",
    message="Item [{itemId}] item type [{itemType}] can't be bundled into option box",
)
ERROR_30334 = ApiError(
    code="30334", message="Option box item [{itemId}] can't be bundled"
)
ERROR_30335 = ApiError(
    code="30335",
    message="Item [{itemId}] can't be deleted in non-forced mode if item has been published",
)
ERROR_30336 = ApiError(code="30336", message="Item type [{itemType}] does not support")
ERROR_30337 = ApiError(
    code="30337", message="Invalid loot box item [{itemId}] quantity"
)
ERROR_30338 = ApiError(
    code="30338",
    message="Item [{itemId}] item type [{itemType}] can't be bundled into loot box",
)
ERROR_30339 = ApiError(
    code="30339", message="Loot box item [{itemId}] can't be bundled"
)
ERROR_30341 = ApiError(
    code="30341", message="Item [{itemId}] does not exist in namespace [{namespace}]"
)
ERROR_30342 = ApiError(code="30342", message="Item of appId [{appId}] does not exist")
ERROR_30343 = ApiError(code="30343", message="Item of sku [{sku}] does not exist")
ERROR_30371 = ApiError(code="30371", message="Item maxCount not allow reduce")
ERROR_30372 = ApiError(code="30372", message="ItemType is not updatable")
ERROR_30373 = ApiError(
    code="30373",
    message="ItemType [{itemType}] is not allowed in namespace [{namespace}]",
)
ERROR_30374 = ApiError(
    code="30374", message="Item sku [{sku}] already exists in namespace [{namespace}]"
)
ERROR_30375 = ApiError(
    code="30375",
    message="Item id [{itemId}] of sku [{sku}] is duplicate with un-published deleted item in namespace [{namespace}]",
)
ERROR_30376 = ApiError(
    code="30376", message="Publisher namespace don’t allow sellback item"
)
ERROR_30377 = ApiError(
    code="30377", message="This item type [{itemType}] don’t allow sellback"
)
ERROR_30378 = ApiError(
    code="30378", message="Sale price don’t allow real currency [{currencyCode}]"
)
ERROR_30379 = ApiError(code="30379", message="Item sku is not updatable")
ERROR_30380 = ApiError(
    code="30380",
    message="Box item [{itemId}] duration and end date can’t be set at the same time",
)
ERROR_30381 = ApiError(
    code="30381",
    message="Currency [{currency}] is not set for bundle Item [{itemId}] in region [{region}]",
)
ERROR_30382 = ApiError(code="30382", message="Duplicated Item sku [{sku}]")
ERROR_30383 = ApiError(
    code="30383",
    message="Item app id [{appId}] already exists in namespace [{namespace}] item [{itemId}]",
)
ERROR_30386 = ApiError(
    code="30386",
    message="The item [{itemId}] is currently associated and cannot be deleted in namespace [{namespace}], Feature {featureName}, Module {moduleName}, and Reference ID {referenceId} are using this item ID",
)
ERROR_30387 = ApiError(
    code="30387",
    message="The item [{itemId}] is currently associated and cannot be disabled in namespace [{namespace}], Feature {featureName}, Module {moduleName}, and Reference ID {referenceId} are using this item ID",
)
ERROR_30541 = ApiError(code="30541", message="Item type config [{id}] doesn't exist")
ERROR_30641 = ApiError(
    code="30641", message="View [{viewId}] does not exist in namespace [{namespace}]"
)
ERROR_30741 = ApiError(
    code="30741",
    message="Section [{sectionId}] does not exist in namespace [{namespace}]",
)
ERROR_30771 = ApiError(
    code="30771",
    message="Item [{itemId}] not found in User Section [{sectionId}], UserId [{userId}], Namespace [{namespace}]",
)
ERROR_30772 = ApiError(
    code="30772", message="Section [{sectionId}] is not available or expired"
)
ERROR_31121 = ApiError(
    code="31121", message="OptionBox entitlement [{entitlementId}] use count is not 1"
)
ERROR_31122 = ApiError(
    code="31122",
    message="OptionBox entitlement [{entitlementId}] options size is not 1",
)
ERROR_31123 = ApiError(
    code="31123", message="Unable to acquire box item, box item [{itemId}] expired"
)
ERROR_31141 = ApiError(
    code="31141",
    message="Entitlement [{entitlementId}] does not exist in namespace [{namespace}]",
)
ERROR_31142 = ApiError(
    code="31142",
    message="Entitlement with appId [{appId}] does not exist in namespace [{namespace}]",
)
ERROR_31143 = ApiError(
    code="31143",
    message="Entitlement with sku [{sku}] does not exist in namespace [{namespace}]",
)
ERROR_31144 = ApiError(
    code="31144",
    message="Entitlement with itemId [{itemId}] does not exist in namespace [{namespace}]",
)
ERROR_31145 = ApiError(
    code="31145",
    message="Option [{option}] doesn't exist in OptionBox entitlement [{entitlementId}]",
)
ERROR_31147 = ApiError(
    code="31147", message="Origin [Steam] and System need exist in allowPlatformOrigin"
)
ERROR_31171 = ApiError(
    code="31171", message="Entitlement [{entitlementId}] already revoked"
)
ERROR_31172 = ApiError(code="31172", message="Entitlement [{entitlementId}] not active")
ERROR_31173 = ApiError(
    code="31173", message="Entitlement [{entitlementId}] is not consumable"
)
ERROR_31174 = ApiError(
    code="31174", message="Entitlement [{entitlementId}] already consumed"
)
ERROR_31176 = ApiError(
    code="31176", message="Entitlement [{entitlementId}] use count is insufficient"
)
ERROR_31177 = ApiError(code="31177", message="Permanent item already owned")
ERROR_31178 = ApiError(
    code="31178", message="Entitlement [{entitlementId}] out of time range"
)
ERROR_31179 = ApiError(code="31179", message="Duplicate entitlement exists")
ERROR_31180 = ApiError(code="31180", message="Duplicate request id: [{requestId}]")
ERROR_31181 = ApiError(
    code="31181", message="Entitlement [{entitlementId}] is not sellable"
)
ERROR_31182 = ApiError(
    code="31182", message="Entitlement [{entitlementId}] already sold"
)
ERROR_31183 = ApiError(
    code="31183",
    message="Entitlement [{entitlementId}] origin [{origin}] not allowed be operated at [{platform}]",
)
ERROR_31184 = ApiError(
    code="31184",
    message="Source entitlement [{sourceEntitlementId}] and target entitlement [{targetEntitlementId}] should have same collectionId, timeRange, origin and itemId",
)
ERROR_31185 = ApiError(
    code="31185",
    message="Transferred source entitlement [{sourceEntitlementId}] and target entitlement [{targetEntitlementId}] can not be set to same",
)
ERROR_32121 = ApiError(code="32121", message="Order price mismatch")
ERROR_32122 = ApiError(code="32122", message="Item type [{itemType}] does not support")
ERROR_32123 = ApiError(code="32123", message="Item is not purchasable")
ERROR_32124 = ApiError(code="32124", message="Invalid currency namespace")
ERROR_32125 = ApiError(
    code="32125", message="The user does not meet the purchase conditions"
)
ERROR_32126 = ApiError(
    code="32126", message="Section ID is required for placing this order"
)
ERROR_32127 = ApiError(
    code="32127", message="Discount code [{code}] can't be used on this item: {tips}"
)
ERROR_32128 = ApiError(
    code="32128",
    message="Discount code [{code}] can not be used with other code together",
)
ERROR_32129 = ApiError(code="32129", message="Can't use discount code on free order")
ERROR_32130 = ApiError(
    code="32130", message="The total discount amount cannot exceed the order price"
)
ERROR_32141 = ApiError(code="32141", message="Order [{orderNo}] does not exist")
ERROR_32171 = ApiError(code="32171", message="Order [{orderNo}] is not refundable")
ERROR_32172 = ApiError(
    code="32172", message="Invalid order status [{status}] for order [{orderNo}]"
)
ERROR_32173 = ApiError(
    code="32173", message="Receipt of order [{orderNo}] is not downloadable"
)
ERROR_32175 = ApiError(
    code="32175", message="Exceed item [{itemId}] max count [{maxCount}] per user"
)
ERROR_32176 = ApiError(
    code="32176", message="Exceed item [{itemId}] max count [{maxCount}]"
)
ERROR_32177 = ApiError(code="32177", message="Order [{orderNo}] is not cancelable")
ERROR_32178 = ApiError(
    code="32178",
    message="User [{userId}] already owned all durable items in flexible bundle [{bundleId}], namespace: [{namespace}]",
)
ERROR_33045 = ApiError(
    code="33045",
    message="errors.net.accelbyte.platform.payment.payment_merchant_config_not_found",
)
ERROR_33121 = ApiError(
    code="33121",
    message="Recurring payment failed with code: [{errorCode}] and message: [{errorMessage}] by provider: [{provider}]",
)
ERROR_33122 = ApiError(
    code="33122", message="Subscription not match when create payment order"
)
ERROR_33123 = ApiError(code="33123", message="Invalid zipcode")
ERROR_33141 = ApiError(
    code="33141", message="Payment Order [{paymentOrderNo}] does not exist"
)
ERROR_33145 = ApiError(code="33145", message="Recurring token not found")
ERROR_33171 = ApiError(
    code="33171",
    message="Invalid payment order status [{status}] for payment order [{paymentOrderNo}]",
)
ERROR_33172 = ApiError(
    code="33172", message="Payment order [{paymentOrderNo}] is not refundable"
)
ERROR_33173 = ApiError(
    code="33173",
    message="ExtOrderNo [{extOrderNo}] already exists in namespace [{namespace}]",
)
ERROR_33221 = ApiError(code="33221", message="TaxJar api token required")
ERROR_33241 = ApiError(
    code="33241", message="Payment provider config [{id}] does not exist"
)
ERROR_33242 = ApiError(
    code="33242", message="Payment merchant config [{id}] does not exist"
)
ERROR_33243 = ApiError(
    code="33243", message="Payment callback config for [{namespace}] does not exist"
)
ERROR_33271 = ApiError(
    code="33271",
    message="Payment provider config for namespace [{namespace}] and region [{region}] already exists",
)
ERROR_33321 = ApiError(
    code="33321",
    message="Payment provider [{paymentProvider}] not support currency [{currency}]",
)
ERROR_33322 = ApiError(
    code="33322", message="Payment provider [{paymentProvider}] not supported"
)
ERROR_33332 = ApiError(
    code="33332", message="Amount too small, please contact administrator"
)
ERROR_33333 = ApiError(
    code="33333",
    message="Neon Pay checkout payment order [{paymentOrderNo}] failed with message [{errMsg}]",
)
ERROR_34021 = ApiError(
    code="34021", message="Reward data for namespace [{namespace}] is invalid"
)
ERROR_34023 = ApiError(
    code="34023",
    message="Reward Item [{itemId}] with item type [{itemType}] is not supported for duration or endDate",
)
ERROR_34027 = ApiError(
    code="34027",
    message="Reward Item [{sku}] with item type [{itemType}] is not supported for duration or endDate",
)
ERROR_34041 = ApiError(
    code="34041",
    message="Reward [{rewardId}] does not exist in namespace [{namespace}]",
)
ERROR_34042 = ApiError(
    code="34042",
    message="Reward item [{itemId}] does not exist in namespace [{namespace}]",
)
ERROR_34043 = ApiError(
    code="34043",
    message="Reward with code [{rewardCode}] does not exist in namespace [{namespace}]",
)
ERROR_34044 = ApiError(
    code="34044",
    message="Reward item [{sku}] does not exist in namespace [{namespace}]",
)
ERROR_34071 = ApiError(
    code="34071",
    message="Reward with code [{rewardCode}] already exists in namespace [{namespace}]",
)
ERROR_34072 = ApiError(
    code="34072",
    message="Duplicate reward condition [{rewardConditionName}] found in reward [{rewardCode}]",
)
ERROR_34074 = ApiError(
    code="34074",
    message="Reward Item [{itemId}] duration and end date can’t be set at the same time",
)
ERROR_34076 = ApiError(
    code="34076",
    message="Reward Item [{sku}] duration and end date can’t be set at the same time",
)
ERROR_35123 = ApiError(code="35123", message="Wallet [{walletId}] is inactive")
ERROR_35124 = ApiError(
    code="35124", message="Wallet [{currencyCode}] has insufficient balance"
)
ERROR_35141 = ApiError(code="35141", message="Wallet [{walletId}] does not exist")
ERROR_36141 = ApiError(
    code="36141",
    message="Currency [{currencyCode}] does not exist in namespace [{namespace}]",
)
ERROR_36171 = ApiError(
    code="36171",
    message="Currency [{currencyCode}] already exists in namespace [{namespace}]",
)
ERROR_36172 = ApiError(
    code="36172",
    message="Real Currency [{currencyCode}] not allowed in game namespace [{namespace}]",
)
ERROR_37041 = ApiError(
    code="37041",
    message="Ticket booth [{boothName}] does not exist in namespace [{namespace}]",
)
ERROR_37071 = ApiError(
    code="37071",
    message="Insufficient ticket in booth [{boothName}] in namespace [{namespace}]",
)
ERROR_37121 = ApiError(
    code="37121",
    message="Invalid currency namespace [{namespace}] in discount config: {tips}",
)
ERROR_37141 = ApiError(
    code="37141",
    message="Campaign [{campaignId}] does not exist in namespace [{namespace}]",
)
ERROR_37142 = ApiError(
    code="37142", message="Code [{code}] does not exist in namespace [{namespace}]"
)
ERROR_37143 = ApiError(
    code="37143",
    message="Batch name [{batchName}] does not exist for campaign [{campaignId}] in namespace [{namespace}].",
)
ERROR_37144 = ApiError(
    code="37144",
    message="Campaign batch name does not exist for batch number [{batchNo}] campaign [{campaignId}] in namespace [{namespace}].",
)
ERROR_37171 = ApiError(
    code="37171", message="Campaign [{name}] already exists in namespace [{namespace}]"
)
ERROR_37172 = ApiError(
    code="37172",
    message="Campaign [{campaignId}] is inactive in namespace [{namespace}]",
)
ERROR_37173 = ApiError(
    code="37173", message="Code [{code}] is inactive in namespace [{namespace}]"
)
ERROR_37174 = ApiError(
    code="37174", message="Exceeded max redeem count per code [{maxCount}]"
)
ERROR_37175 = ApiError(
    code="37175", message="Exceeded max redeem count per code per user [{maxCount}]"
)
ERROR_37176 = ApiError(
    code="37176", message="Code [{code}] has been redeemed in namespace [{namespace}]"
)
ERROR_37177 = ApiError(code="37177", message="Code redemption not started")
ERROR_37178 = ApiError(code="37178", message="Code redemption already ended")
ERROR_37179 = ApiError(
    code="37179", message="Exceeded max redeem count per campaign per user [{maxCount}]"
)
ERROR_37180 = ApiError(
    code="37180", message="Code [{code}] already exists in namespace [{namespace}]"
)
ERROR_37221 = ApiError(code="37221", message="Invalid key file")
ERROR_37241 = ApiError(
    code="37241",
    message="Key group [{keyGroupId}] does not exist in namespace [{namespace}]",
)
ERROR_37271 = ApiError(
    code="37271", message="Key group [{name}] already exists in namespace [{namespace}]"
)
ERROR_38121 = ApiError(code="38121", message="Duplicate permanent item exists")
ERROR_38122 = ApiError(code="38122", message="Subscription endDate required")
ERROR_38128 = ApiError(
    code="38128",
    message="Cannot retry fulfillment with different payload. Please check the items list.",
)
ERROR_38129 = ApiError(
    code="38129",
    message="Cannot combine same item [{itemId}] with different [{fieldName}] value",
)
ERROR_38130 = ApiError(
    code="38130",
    message="Cannot fulfill item with type [{itemType}] in item [{itemIdentity}]",
)
ERROR_38141 = ApiError(code="38141", message="Fulfillment script does not exist")
ERROR_38145 = ApiError(
    code="38145",
    message="Fulfillment with transactionId [{transactionId}] does not exist",
)
ERROR_38171 = ApiError(code="38171", message="Fulfillment script already exists")
ERROR_39121 = ApiError(
    code="39121",
    message="Apple iap receipt verify failed with status code [{statusCode}]",
)
ERROR_39122 = ApiError(
    code="39122",
    message="Google iap receipt is invalid with status code [{statusCode}] and error message [{message}]",
)
ERROR_39123 = ApiError(code="39123", message="IAP request is not in valid application")
ERROR_39124 = ApiError(
    code="39124",
    message="IAP request platform [{platformId}] user id is not linked with current user",
)
ERROR_39125 = ApiError(
    code="39125", message="Invalid platform [{platformId}] user token"
)
ERROR_39126 = ApiError(
    code="39126", message="User id [{}] in namespace [{}] doesn't link platform [{}]"
)
ERROR_39127 = ApiError(code="39127", message="Invalid service label [{serviceLabel}]")
ERROR_39128 = ApiError(code="39128", message="Steam publisher key is invalid")
ERROR_39129 = ApiError(code="39129", message="Steam app id is invalid")
ERROR_39130 = ApiError(code="39130", message="Invalid playstation config: [{message}]")
ERROR_39131 = ApiError(
    code="39131",
    message="Invalid Apple IAP config under namespace [{namespace}]: [{message}]",
)
ERROR_39132 = ApiError(
    code="39132",
    message="Bad request for playstation under namespace [{namespace}], reason: [{reason}].",
)
ERROR_39133 = ApiError(code="39133", message="Bad request for Oculus: [{reason}]")
ERROR_39134 = ApiError(
    code="39134",
    message="Invalid Oculus IAP config under namespace [{namespace}]: [{message}]",
)
ERROR_39135 = ApiError(
    code="39135",
    message="Invalid Google IAP config under namespace [{namespace}]: [{message}]",
)
ERROR_39136 = ApiError(
    code="39136",
    message="Request Apple API failed with status code [{statusCode}] and error message [{message}]",
)
ERROR_39137 = ApiError(
    code="39137",
    message="Verify Apple transaction failed with status [{status}] and error message [{message}]",
)
ERROR_39138 = ApiError(
    code="39138",
    message="Apple IAP version mismatch detected: The current configuration is set to  [{configVersion}], but the API version is [{apiVersion}]. Please ensure that both the configuration and API versions are aligned",
)
ERROR_39141 = ApiError(
    code="39141",
    message="Apple iap receipt of transaction [{transactionId}] for productId [{}] does not exist",
)
ERROR_39142 = ApiError(
    code="39142", message="Apple IAP config not found in namespace [{namespace}]"
)
ERROR_39143 = ApiError(
    code="39143", message="PlayStation IAP config not found in namespace [{namespace}]"
)
ERROR_39144 = ApiError(
    code="39144", message="Steam IAP config not found in namespace [{namespace}]."
)
ERROR_39145 = ApiError(
    code="39145", message="XBox IAP config not found in namespace [{namespace}]."
)
ERROR_39146 = ApiError(
    code="39146", message="Oculus IAP config not found in namespace [{namespace}]."
)
ERROR_39147 = ApiError(
    code="39147", message="Epic IAP config not found in namespace [{namespace}]."
)
ERROR_39148 = ApiError(
    code="39148", message="Google IAP config not found in namespace [{namespace}]."
)
ERROR_39149 = ApiError(
    code="39149",
    message="Third Party Subscription Transaction [{id}] not found for user [{userId}] in the namespace [{namespace}].",
)
ERROR_39150 = ApiError(
    code="39150",
    message="Third Party User Subscription [{id}] not found for user [{userId}] in the namespace [{namespace}]..",
)
ERROR_39151 = ApiError(
    code="39151",
    message="IAP order no [{iapOrderNo}] not found in namespace [{namespace}].",
)
ERROR_39171 = ApiError(
    code="39171",
    message="The bundle id in namespace [{namespace}] expect [{expected}] but was [{actual}]",
)
ERROR_39172 = ApiError(
    code="39172",
    message="The order id in namespace [{namespace}] expect [{expected}] but was [{actual}]",
)
ERROR_39173 = ApiError(
    code="39173",
    message="The purchase status of google play order [{orderId}] in namespace [{namespace}] expect [{expected}] but was [{actual}]",
)
ERROR_39174 = ApiError(
    code="39174",
    message="The google iap purchase time of order [{orderId}] in namespace [{namespace}] expect [{expected}] but was [{actual}]",
)
ERROR_39175 = ApiError(
    code="39175",
    message="Duplicate IAP item mapping, IAPType: [{iapType}] and id: [{iapId}]",
)
ERROR_39183 = ApiError(
    code="39183",
    message="Steam transaction [{orderId}] is still pending or failed, status [{status}], please try it later",
)
ERROR_39184 = ApiError(
    code="39184",
    message="Steam api exception with error code [{errorCode}] and error message [{message}]",
)
ERROR_39185 = ApiError(
    code="39185",
    message="This endpoint only works on sync mode [{workSyncMode}], but current steam iap config sync mode is [{currentSyncMode}] under namespace [{namespace}]",
)
ERROR_39221 = ApiError(
    code="39221",
    message="Invalid Xbox Business Partner Certificate or password: [{message}]",
)
ERROR_39244 = ApiError(code="39244", message="Steam config does not exist")
ERROR_39245 = ApiError(code="39245", message="Steam app id does not exist")
ERROR_39321 = ApiError(
    code="39321", message="Invalid IAP item config namespace [{namespace}]: [{message}]"
)
ERROR_39341 = ApiError(
    code="39341", message="IAP item config cannot be found in namespace [{namespace}]"
)
ERROR_39441 = ApiError(
    code="39441",
    message="Platform dlc config cannot be found in namespace [{namespace}]",
)
ERROR_39442 = ApiError(
    code="39442", message="DLC item config cannot be found in namespace [{namespace}]"
)
ERROR_39471 = ApiError(
    code="39471",
    message="Duplicated dlc reward id [{dlcRewardId}] in namespace [{namespace}] ",
)
ERROR_39621 = ApiError(
    code="39621",
    message="Steam api common exception with status code [statusCode] details: [details]",
)
ERROR_40121 = ApiError(code="40121", message="Item type [{itemType}] does not support")
ERROR_40122 = ApiError(
    code="40122", message="Subscription already been subscribed by user"
)
ERROR_40123 = ApiError(
    code="40123", message="Currency [{currencyCode}] does not support"
)
ERROR_40125 = ApiError(
    code="40125",
    message="Subscription [{subscriptionId}] has no real currency billing account",
)
ERROR_40141 = ApiError(
    code="40141", message="Subscription [{subscriptionId}] does not exist"
)
ERROR_40171 = ApiError(
    code="40171", message="Subscription [{subscriptionId}] is not active"
)
ERROR_40172 = ApiError(
    code="40172",
    message="Subscription [{subscriptionId}] is charging, waiting for payment notification",
)
ERROR_40173 = ApiError(
    code="40173",
    message="Subscription [{subscriptionId}] current currency [{currentCurrency}] not match request currency [{requestCurrency}]",
)
ERROR_41171 = ApiError(
    code="41171", message="Request has different payload on previous call"
)
ERROR_41172 = ApiError(
    code="41172", message="Request has different user id on previous call"
)
ERROR_49147 = ApiError(code="49147", message="Published season does not exist")
ERROR_49183 = ApiError(
    code="49183", message="Pass item does not match published season pass"
)
ERROR_49184 = ApiError(
    code="49184", message="Tier item does not match published season tier"
)
ERROR_49185 = ApiError(code="49185", message="Season has not started")
ERROR_49186 = ApiError(code="49186", message="Pass already owned")
ERROR_49187 = ApiError(code="49187", message="Exceed max tier count")
ERROR_394721 = ApiError(
    code="394721",
    message="Invalid platform DLC config namespace [{namespace}]: [{message}]",
)
ERROR_1100001 = ApiError(code="1100001", message="record not found: inventory")
