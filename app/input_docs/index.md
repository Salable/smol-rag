---
sidebar_position: 1
title: "Getting Started"
description: "Introduction to the Salable Web Component library"
---

## Introduction

The Salable Web Component Library is designed to streamline the development process for SaaS products. It is a collection of Web Components that facilitate easy integration with payment platforms and simplify the creation of flexible pricing models. Our components are seamlessly compatible with various web frameworks, making it easier for developers to integrate payment and licensing functionality in web applications.

## Key Features

 - **Web Components**: Our Web Components are standards-compliant and work across all modern browsers, ensuring broad compatibility.
 - **React Wrappers**: We provide wrapped versions of our Web Components for React projects.
 - **Ease of Integration**: Designed to be easily integrated into your existing projects, requiring minimal configuration to get started

## Available Components

 - [**Pricing Table**](/web-components/web-components-latest/Components/pricing-table): Display your product's plans and allow users to sign up for free plans or purchase a subscription for a paid plans.
 - [**Invoices**](/web-components/web-components-latest/Components/invoices): Display all of the invoices for a given subscription and allow users to view/download them.
 - [**Checkout**](/web-components/web-components-latest/Components/checkout): Allow users to purchase a given paid plan
 - [**Cancellation Button**](/web-components/web-components-latest/Components/cancellation-button): Allow users to cancel the provided subscription or license

## Implementing Salable Web Components

### Generating a session

To use the Salable Web Components, you first need to generate a session token for the specific web component you want to use. You can do this using the [`POST /sessions` endpoint](https://docs.salable.app/api/v2#tag/Sessions/operation/createSession) on the [Salable API](https://docs.salable.app/api/v2).

:::caution

Session tokens grant access to sensitive information so it's vital you authenticate your users prior to creating a new session token.

:::

When creating a session token using the API, you'll need to provide two pieces of data in the body.

 1. `scope`
 2. `metadata`

#### Scope

Each web component has it's own scope that needs to be provided, E.g. Invoices is `web-components:invoices`. 

See the complete list of scopes on the [create session API docs.](https://docs.salable.app/api/v2#tag/Sessions/operation/createSession)

#### Metadata

Depending on the scope you provide and the component you want to generate the session token for, you'll need to provide different metadata objects. 

For example, if you were generating a session token to use with the `web-components:invoices` scope, you'd need to provide a `subscriptionUuid` like so.

```json
"metadata": {
    "subscriptionUuid": "YOUR_SUBSCRIPTION_UUID"
}
```

See the complete list of requirements for each component's metadata on the [create session API docs.](https://docs.salable.app/api/v2#tag/Sessions/operation/createSession) Or, by viewing the specific component's documentation using the left sidebar.

### Install

You'll need to install one of our packages using one of the commands below to begin using the Salable Web Components. For Web Components, include them directly in your HTML, and for React-based projects, import the components as shown in the examples below.

#### Salable Web Components library:

```bash
npm i @salable/web-components
```

#### Salable React Web Components library:

```bash
npm i @salable/react-web-components
```

#### HTML Import

```html
<script type="module">
    import { defineCustomElements } from 'https://cdn.jsdelivr.net/npm/@salable/web-components@latest/loader/index.es2017.js';
    defineCustomElements();
</script>
```

### Render the component

After you have installed the right NPM package (if required) for your project, you can then render your chosen web component by providing the session token you generated and any other required properties.

For example, here is how you would render the `Invoices` component in a React project.

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

Below are links to each component's documentation page which contains examples of how to generate session tokens for it and how to render it.

 - [Pricing Table](/web-components/web-components-latest/Components/pricing-table)
 - [Invoices](/web-components/web-components-latest/Components/invoices)
 - [Checkout](/web-components/web-components-latest/Components/checkout)
 - [Cancellation Button](/web-components/web-components-latest/Components/cancellation-button)


## Salable Web Components Integration Demos

Explore how to integrate Salable Web Components with different front-end frameworks and environments. Below are the links to example repositories showcasing the usage of Web Components within various frameworks and environments.

- [Svelte](https://github.com/Salable/Salable-Web-Components-Svelte-Demo)
- [React/Next.js](https://github.com/Salable/Salable-React-Web-Components-Nextjs-Demo)
- [HTML/JavaScript](https://github.com/Salable/Salable-Web-Components-HTML-JS-Demo)

