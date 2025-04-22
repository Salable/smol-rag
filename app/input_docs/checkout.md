---
sidebar_position: 2
title: Checkout
description: How to use the checkout web component and wrappers
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
        scope: 'web-components:checkout',
        metadata: {
            planUuid: 'YOUR_PLAN_UUID'
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
    -d '{ "scope": "web-components:checkout", "metadata": {"planUuid": "YOUR_PLAN_UUID"} }' 
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
    <title>Salable Checkout Web Component Example</title>
    <script type="module">
        import { defineCustomElements } from 'https://cdn.jsdelivr.net/npm/@salable/web-components@latest/loader/index.es2017.js';
        defineCustomElements();
    </script>
</head>
<body>
    <salable-checkout
        session-token="YOUR_SESSION_TOKEN"
        plan-uuid="YOUR_PLAN_UUID"
        owner="EXAMPLE_OWNER"
        grantee-id="EXAMPLE_GRANTEE_ID"
        success-url="https://example.com/success"
        currency="GBP"
    ></salable-checkout>
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

<salable-checkout
    session-token="YOUR_SESSION_TOKEN"
    plan-uuid="YOUR_PLAN_UUID"
    owner="EXAMPLE_OWNER"
    grantee-id="EXAMPLE_GRANTEE_ID"
    success-url="https://example.com/success"
    currency="GBP"
></salable-checkout>
```

*+page.js*
```js
export const ssr = false;
```

</TabItem>
<TabItem value="react" label="React">

```tsx
import { defineCustomElements, SalableCheckout } from '@salable/react-web-components';

defineCustomElements();

export default function SalableCheckoutDemo() {
    return (
        <SalableCheckout
            sessionToken="YOUR_SESSION_TOKEN"
            planUuid="YOUR_PLAN_UUID"
            owner="EXAMPLE_OWNER"
            granteeId="EXAMPLE_GRANTEE_ID"
            successUrl="https://example.com/success"
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

const SalableCheckout = dynamic(
  () =>
    import("@salable/react-web-components").then(
      (module) => module.SalableCheckout,
    ),
  { ssr: false },
);

export default function SalableCheckoutDemo() {
    useEffect(() => {
      import("@salable/react-web-components").then((module) => {
        const { defineCustomElements } = module;
        defineCustomElements();
      });
    }, []);

    return (
        <SalableCheckout
            sessionToken="YOUR_SESSION_TOKEN"
            planUuid="YOUR_PLAN_UUID"
            owner="EXAMPLE_OWNER"
            granteeId="EXAMPLE_GRANTEE_ID"
            successUrl="https://example.com/success"
            currency="GBP"
        />
    )
}
```

</TabItem>
<TabItem value="nextjs-app" label="Next.js App Router">

```tsx
'use client';

import { defineCustomElements, SalableCheckout } from '@salable/react-web-components';

defineCustomElements();

export default function SalableCheckoutDemo() {
    return (
        <SalableCheckout
            sessionToken="YOUR_SESSION_TOKEN"
            planUuid="YOUR_PLAN_UUID"
            owner="EXAMPLE_OWNER"
            granteeId="EXAMPLE_GRANTEE_ID"
            successUrl="https://example.com/success"
            currency="GBP"
        />
    )
}
```

</TabItem>
</Tabs>

## Properties

| Property                    | Attribute       | Description                                                                                                                  | Type     | Default               |
|-----------------------------|-----------------|------------------------------------------------------------------------------------------------------------------------------|----------|-----------------------|
| `currency` _(required)_     | `currency`      | The short name of the currency used in the checkout e.g. USD                                                                 | `string` | `undefined`           |
| `granteeId` _(required)_    | `grantee-id`    | A unique identifier used in licensing that represents the entity to which a license is granted                               | `string` | `undefined`           |
| `owner`                     | `owner`         | The ID of the entity who will own the subscription                                                                           | `string` | The value of `member` |
| `member`                    | `member`        | A unique identifier for a member or user. Deprecated, please use owner.                                                      | `string` | `undefined`           |
| `planUuid` _(required)_     | `plan-uuid`     | A unique identifier for a specific plan                                                                                      | `string` | `undefined`           |
| `sessionToken` _(required)_ | `session-token` | The generated token for this session from the Salable API                                                                    | `string` | `undefined`           |
| `successUrl` _(required)_   | `success-url`   | The URL the user is sent to if they successfully completed a payment                                                         | `string` | `undefined`           |
| `email`                     | `email`         | A user's email address to be used for the checkout.  Providing the user's email skips the provide email step during checkout | `string` | `undefined`           |
