---
sidebar_position: 4
title: Cancellation Button
description: How to use the cancellation button web component and wrappers
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
        scope: 'web-components:cancellation-button',
        metadata: {
            subscriptionUuid: 'YOUR_SUBSCRIPTION_UUID',
            // === OR ===
            licenseUuid: 'YOUR_LICENSE_UUID'
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
        "scope": "web-components:cancellation-button", 
        "metadata": {
            "subscriptionUuid": "YOUR_SUBSCRIPTION_UUID",
            # === OR ===
            "licenseUuid": "YOUR_LICENSE_UUID"
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
    <title>Salable Cancellation Button Web Component Example</title>
    <script type="module">
        import { defineCustomElements } from 'https://cdn.jsdelivr.net/npm/@salable/web-components@latest/loader/index.es2017.js';
        defineCustomElements();
    </script>
</head>
<body>
    <salable-cancellation-button
        session-token="YOUR_SESSION_TOKEN"
        uuid="YOUR_SUBSCRIPTION_OR_LICENSE_UUID"
    ></salable-cancellation-button>
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

<salable-cancellation-button
    session-token="YOUR_SESSION_TOKEN"
    uuid="YOUR_SUBSCRIPTION_OR_LICENSE_UUID"
></salable-cancellation-button>
```

*+page.js*
```js
export const ssr = false;
```

</TabItem>
<TabItem value="react" label="React">

```tsx
import { defineCustomElements, SalableCancellationButton } from '@salable/react-web-components';

defineCustomElements();

export default function SalableCancellationButtonDemo() {
    return (
        <SalableCancellationButton
            sessionToken="YOUR_SESSION_TOKEN"
            uuid="YOUR_SUBSCRIPTION_OR_LICENSE_UUID"
        />
    )
}
```

</TabItem>
<TabItem value="nextjs-pages" label="Next.js Pages Router">

```tsx
import dynamic from "next/dynamic";
import { useEffect } from 'react'

const SalableCancellationButton = dynamic(
  () =>
    import("@salable/react-web-components").then(
      (module) => module.SalableCancellationButton,
    ),
  { ssr: false },
);

export default function SalableCancellationButtonDemo() {
    useEffect(() => {
      import("@salable/react-web-components").then((module) => {
        const { defineCustomElements } = module;
        defineCustomElements();
      });
    }, []);

    return (
        <SalableCancellationButton
            sessionToken="YOUR_SESSION_TOKEN"
            uuid="YOUR_SUBSCRIPTION_OR_LICENSE_UUID"
        />
    )
}
```

</TabItem>
<TabItem value="nextjs-app" label="Next.js App Router">

```tsx
'use client';

import { defineCustomElements, SalableCancellationButton } from '@salable/react-web-components';

defineCustomElements();

export default function SalableCancellationButtonDemo() {
    return (
        <SalableCancellationButton
            sessionToken="YOUR_SESSION_TOKEN"
            uuid="YOUR_SUBSCRIPTION_OR_LICENSE_UUID"
        />
    )
}
```

</TabItem>
</Tabs>

## Properties

| Property                    | Attribute       | Description                                               | Type     | Default     |
| --------------------------- | --------------- | --------------------------------------------------------- | -------- | ----------- |
| `sessionToken` _(required)_ | `session-token` | The generated token for this session from the Salable API | `string` | `undefined` |
| `uuid` _(required)_         | `uuid`          | The uuid of the license or subscription to cancel         | `string` | `undefined` |
