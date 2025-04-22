---
sidebar_position: 3
title: Invoices
description: How to use the invoices web component and wrappers
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
        scope: 'web-components:invoices',
        metadata: {
            subscriptionUuid: 'YOUR_SUBSCRIPTION_UUID'
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
    -d '{ "scope": "web-components:invoices", "metadata": {"subscriptionUuid": "YOUR_SUBSCRIPTION_UUID"} }' 
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
    <title>Salable Invoices Web Component Example</title>
    <script type="module">
        import { defineCustomElements } from 'https://cdn.jsdelivr.net/npm/@salable/web-components@latest/loader/index.es2017.js';
        defineCustomElements();
    </script>
</head>
<body>
    <salable-invoices class="theme" session-token="YOUR_SESSION_TOKEN" subscription-uuid="YOUR_SUBSCRIPTION_UUID" limit="3"></salable-invoices>
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

<salable-invoices class="theme" session-token="YOUR_SESSION_TOKEN" subscription-uuid="YOUR_SUBSCRIPTION_UUID" limit="3"></salable-invoices>
```

*+page.js*
```js
export const ssr = false;
```

</TabItem>
<TabItem value="react" label="React">

```tsx
import { defineCustomElements, SalableInvoices } from '@salable/react-web-components';

defineCustomElements();

export default function SalableInvoicesDemo() {
    return (
        <SalableInvoices
            sessionToken="YOUR_SESSION_TOKEN"
            subscriptionUuid="YOUR_SUBSCRIPTION_UUID"
            limit={3}
        />
    )
}
```

</TabItem>
<TabItem value="nextjs-pages" label="Next.js Pages Router">

```tsx
import dynamic from "next/dynamic";
import { useEffect } from 'react'

const SalableInvoices = dynamic(
  () =>
    import("@salable/react-web-components").then(
      (module) => module.SalableInvoices,
    ),
  { ssr: false },
);

export default function SalableInvoicesDemo() {
    useEffect(() => {
      import("@salable/react-web-components").then((module) => {
        const { defineCustomElements } = module;
        defineCustomElements();
      });
    }, []);

    return (
        <SalableInvoices
            sessionToken="YOUR_SESSION_TOKEN"
            subscriptionUuid="YOUR_SUBSCRIPTION_UUID"
            limit={3}
        />
    )
}
```

</TabItem>
<TabItem value="nextjs-app" label="Next.js App Router">

```tsx
'use client';

import { defineCustomElements, SalableInvoices } from '@salable/react-web-components';

defineCustomElements();

export default function SalableInvoicesDemo() {
    return (
        <SalableInvoices
            sessionToken="YOUR_SESSION_TOKEN"
            subscriptionUuid="YOUR_SUBSCRIPTION_UUID"
            limit={3}
        />
    )
}
```

</TabItem>
</Tabs>

## Properties

| Property                        | Attribute           | Description                                                         | Type     | Default     |
| ------------------------------- | ------------------- | ------------------------------------------------------------------- | -------- | ----------- |
| `sessionToken` _(required)_     | `session-token`     | The generated token for this session                                | `string` | `undefined` |
| `subscriptionUuid` _(required)_ | `subscription-uuid` | The uuid of the subscription that you want to display invoices for. | `string` | `undefined` |
| `limit`                         | `limit`             | The number of rows to display per page                              | `number` | `25`        |
