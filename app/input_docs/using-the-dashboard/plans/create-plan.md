---
sidebar_position: 2
---

# Create a Plan

You can add new plans to a product at any time.

## Instructions

1. Select **Products** from the navigation menu on the left-hand side.
2. Select the product you want to configure.
3. Select the **Plans** tab.
4. Select **Add Plan**.
5. Complete the fields in the **Plan Labels** section:
   - **Plan Name** - Name used in the Salable Dashboard.
   - **Plan Slug** - The Plan slug is how the plan will be referenced by our API and various SDKs.
   - **Plan Description** - Information shown in tooltips.
6. Select **Next**.
7. Complete the fields in the **License Type** section:
   - **What type of plan is this?** - There are three different types of plans. Which option you choose changes the plan cycle options available.
     - **Standard** plans are your typical Basic, Pro, Premium, etc plans that customers can sign up for and contain pre-defined sets of features.
     - **Bespoke** plans are created for specific customers and contain custom feature sets and capabilities.
     - **Coming Soon** plans allow you to display plans on the pricing table a checkout link.
   - **How often does this subscription cycle?** - Select the time period from the drop-down. The options depend on the plan type.
     - For _Coming Soon_ and _Standard_, the options are **Year** or **Month**.
     - For _Bespoke_ the options are **Year**, **Month** or **Day**.
     - Type or use the selector to choose an integer value.
   - **What type should each license have?** - Select the pricing model you are using for this plan.
     The options are **Flat rate**, **Usage** or **Per seat**. You can read more about these in the [**Pricing Models**](/docs/using-the-dashboard/pricing-models) article.
   - **Is this plan a free plan or a paid plan?** - Select if you'd like your Plan to be a **Paid Plan** or a **Free Plan**.
   - **Does this plan have a trial?** - Select Yes for the Plan to have a **Trial Period** attached to it. Trial periods are defined per day.
   - **Show in the default pricing table?** - You can here pick whether the Plan is to be shown in the default pricing table.
8. Select **Next**.
9. Complete the fields in the **Assign Values** tab. You must assign a
   relevant value for this plan for each feature in your product.

   If you selected **Usage** as the _License Type_ for the plan, you can specify
   here which feature is the basis for usage billing by selecting the
   appropriate radio button.

10. Select **Next**.
11. Complete the fields in the **Capabilities** tab. These are the capabilities you set up for your product. The **Plan Slug** will be added as a capability.
12. Select **Create Plan**.

The plan is now shown in the Plans tab. To make changes to the plan, select the
**Edit Icon** next to the plan.
