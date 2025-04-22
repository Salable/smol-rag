---
sidebar_position: 1
title: Pricing Table
description: How to use the pricing table web component and wrappers
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

## Creating a Session Token

You can create a session token for this web component by using the request template below with the Salable API.
<Tabs>
<TabItem value="javascript" label="JavaScript">

```js
const response = await fetch('https://api.salable.app/sessions', {
    method: "POST",
    headers: {
        "x-api-key": "YOUR_SALABLE_API_TOKEN",
        version: "v2",
    },
    body: JSON.stringify({
        scope: 'web-components:pricing-table',
        metadata: {
            pricingTableUuid: 'YOUR_PRICING_TABLE_UUID',
            // === OR ===
            productUuid: 'YOUR_PRODUCT_UUID'
        }
    })
})

const { sessionToken } = await response.json()
```

</TabItem>
<TabItem value="curl" label="cURL">

```bash
curl 
    -XPOST 
    -H 'x-api-key: YOUR_SALABLE_API_TOKEN' 
    -H 'version: v2' 
    -d '{ 
        "scope": "web-components:pricing-table", 
        "metadata": {
            "productUuid": "YOUR_PRODUCT_UUID"
            # === OR ===
            "pricingTableUuid: "YOUR_PRICING_TABLE_UUID"
            } 
        }' 
    'https://api.salable.app/sessions'
```

</TabItem>
</Tabs>

_[See the entire API docs for creating sessions for web components.](https://docs.salable.app/api/v2#tag/Sessions/operation/createSession)_

## Examples

<Tabs>
<TabItem value="html" label="HTML/JavaScript">

```html
<!doctype html>
<head>
    <title>Salable Pricing Table Web Component Example</title>
    <script type="module">
        import { defineCustomElements } from 'https://cdn.jsdelivr.net/npm/@salable/web-components@latest/loader/index.es2017.js';
        defineCustomElements();
    </script>
</head>
<body>
    <salable-pricing-table
        session-token="YOUR_SESSION_TOKEN"
        uuid="YOUR_PRICING_TABLE_UUID"
        global-success-url="https://example.com/success"
        global-cancel-url="https://example.com/cancel"
        global-grantee-id="EXAMPLE_GRANTEE_ID"
        owner="EXAMPLE_OWNER"
        currency="GBP"
    ></salable-pricing-table>
</body>
</html>
```

</TabItem>
<TabItem value="svelte" label="Svelte">

*+page.svelte*
```html
<script>
    import {defineCustomElements} from "@salable/web-components/loader";
    defineCustomElements();
</script>

<salable-pricing-table
    session-token="YOUR_SESSION_TOKEN"
    uuid="YOUR_PRICING_TABLE_UUID"
    global-success-url="https://example.com/success"
    global-cancel-url="https://example.com/cancel"
    global-grantee-id="EXAMPLE_GRANTEE_ID"
    owner="EXAMPLE_OWNER"
    currency="GBP"
></salable-pricing-table>
```

*+page.js*
```js
export const ssr = false;
```

</TabItem>
<TabItem value="react" label="React">

```tsx
import { defineCustomElements, SalablePricingTable } from '@salable/react-web-components';

defineCustomElements();

export default function SalablePricingTableDemo() {
    return (
        <SalablePricingTable
            sessionToken="YOUR_SESSION_TOKEN"
            uuid="YOUR_PRICING_TABLE_UUID"
            globalSuccessUrl="https://example.com/success"
            globalCancelUrl="https://example.com/cancel"
            globalGranteeId="EXAMPLE_GRANTEE_ID"
            owner="EXAMPLE_OWNER"
            currency="GBP"
        />
    )
}
```

</TabItem>
<TabItem value="nextjs-pages" label="Next.js Pages Router">

```tsx
import dynamic from "next/dynamic";
import { useEffect } from 'react'

const SalablePricingTable = dynamic(
  () =>
    import("@salable/react-web-components").then(
      (module) => module.SalablePricingTable,
    ),
  { ssr: false },
);

export default function SalablePricingTableDemo() {
    useEffect(() => {
      import("@salable/react-web-components").then((module) => {
        const { defineCustomElements } = module;
        defineCustomElements();
      });
    }, []);

    return (
        <SalablePricingTable
            sessionToken="YOUR_SESSION_TOKEN"
            uuid="YOUR_PRICING_TABLE_UUID"
            globalSuccessUrl="https://example.com/success"
            globalCancelUrl="https://example.com/cancel"
            globalGranteeId="EXAMPLE_GRANTEE_ID"
            owner="EXAMPLE_OWNER"
            currency="GBP"
        />
    )
}
```

</TabItem>
<TabItem value="nextjs-app" label="Next.js App Router">

```tsx
'use client';

import { defineCustomElements, SalablePricingTable } from '@salable/react-web-components';

defineCustomElements();

export default function SalablePricingTableDemo() {
    return (
        <SalablePricingTable
            sessionToken="YOUR_SESSION_TOKEN"
            uuid="YOUR_PRICING_TABLE_UUID"
            globalSuccessUrl="https://example.com/success"
            globalCancelUrl="https://example.com/cancel"
            globalGranteeId="EXAMPLE_GRANTEE_ID"
            owner="EXAMPLE_OWNER"
            currency="GBP"
        />
    )
}
```

</TabItem>
</Tabs>

## Properties

| Property                        | Attribute                 | Description                                                                                                                                               | Type                                 | Default     |
|---------------------------------|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------|-------------|
| `sessionToken` _(required)_     | `session-token`           | The generated token for this session from the Salable API                                                                                                 | `string`                             | `undefined` |
| `uuid` _(required)_             | `uuid`                    | The uuid of the pricing table that you want to display.                                                                                                   | `string`                             | `undefined` |
| `owner`                         | `owner`                   | The ID of the entity who will own the subscription.                                                                                                       | `string`                             | `undefined` |
| `member`                        | `member`                  | The ID of the member who will manage the license. Deprecated, use owner instead.                                                                          | `string`                             | `undefined` |
| `globalCancelUrl` _(required)_  | `global-cancel-url`       | The URL to send users to if the transaction fails. Must be an absolute URL.                                                                               | `string`                             | `undefined` |
| `globalGranteeId` _(required)_  | `global-grantee-id`       | The unique identifier for the grantee for all plan checkouts links.                                                                                       | `string`                             | `undefined` |
| `globalSuccessUrl` _(required)_ | `global-success-url`      | The URL to send users to after a successful purchase. Must be an absolute URL.                                                                            | `string`                             | `undefined` |
| `globalContactUrl`              | `global-contact-url`      | The URL for the "Coming soon" plan cta.                                                                                                                   | `string`                             | `undefined` |
| `perPlanCancelUrls`             | `per-plan-cancel-urls`    | Configure cancelUrls per plan, string format `{'plan-uuid-one':'https://example.com/cancel-one','plan-uuid-two':'https://example.com/cancel-two'}`        | `string \| { [x: string]: string; }` | `undefined` |
| `perPlanGranteeIds`             | `per-plan-grantee-ids`    | Configure granteeIds per plan, string format `{'plan-uuid-one': 'granteeIdOne', 'plan-uuid-two': 'granteeIdTwo'}`                                         | `string \| { [x: string]: string; }` | `undefined` |
| `perPlanSuccessUrls`            | `per-plan-success-urls`   | Configure successUrls per plan, string format `{'plan-uuid-one': 'https://example.com/success-one' , 'plan-uuid-two': 'https://example.com/success-two'}` | `string \| { [x: string]: string; }` | `undefined` |
| `isCustomPricingTable`          | `is-custom-pricing-table` | If you provided the uuid of a custom pricing table set this to true                                                                                       | `boolean`                            | `false`     |
| `customerEmail`                 | `customer-email`          | Pre-fills the customer email in Stripe checkout.                                                                                                          | `string`                             | `undefined` |
| `customerId`                    | `customer-id`             | The ID of an existing customer in your payment integration. This pre-fills the email, card details, and postcode at checkout.                             | `string`                             | `undefined` |
| `currency`                      | `currency`                | Uses the currency short name (e.g. USD). Required if pricing table contains paid plans                                                                    | `string`                             | `undefined` |
| `promoCode`                     | `promo-code`              | Used to pre-fill the promo code in Stripe checkout. Use the promo code ID from Stripe dashboard. Customers cannot edit this field during checkout.        | `string`                             | `undefined` |
| `allowPromoCode`                | `allow-promo-code`        | Enables the promo code field in Stripe checkout. Accepts 'true' or 'false'. Cannot be used with promoCode.                                                | `string`                             | `undefined` |
| `automaticTax`                  | `automatic-tax`           | Automatically calculate tax on checkout based on the customer's location and your Stripe settings.                                                        | `string`                             | `undefined` |
