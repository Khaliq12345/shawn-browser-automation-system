<template>
    <UCollapsible v-model:open="open" class="flex flex-col gap-3">
        <UButton
            class="group"
            color="neutral"
            variant="subtle"
            block
            trailing-icon="i-lucide-chevron-down"
            :ui="{
                trailingIcon:
                    'group-data-[state=open]:rotate-180 transition-transform duration-200',
            }"
        >
            Output
        </UButton>

        <template #content>
            <div class="p-4 space-y-4">
                <!-- Loading -->
                <div v-if="loading" class="text-center py-10">
                    <div class="mt-2 max-w-md mx-auto">
                        <UProgress indeterminate color="neutral" status />
                        <p class="text-gray-200 mt-1">Loading Output...</p>
                    </div>
                </div>

                <!-- Snapshot -->
                <div v-if="output?.snapshot_url">
                    <h3 class="text-lg font-semibold">Snapshot</h3>
                    <img
                        :src="output.snapshot_url"
                        alt="Snapshot"
                        class="rounded-lg shadow-md"
                    />
                </div>

                <!-- Markdown -->
                <div
                    v-if="ast && output?.markdown"
                    class="space-y-2 text-left alert"
                >
                    <h3 class="text-lg font-semibold text-center">Markdown</h3>
                    <div class="markdown-output p-4">
                        <Suspense>
                            <MDCRenderer :body="ast.body" :data="ast.data" />
                        </Suspense>
                    </div>
                </div>
            </div>
        </template>
    </UCollapsible>
</template>

<script setup lang="ts">
import { parseMarkdown } from "@nuxtjs/mdc/runtime";
type OutputResponse = {
    snapshot_url: string;
    markdown: string;
};

const props = defineProps<{
    brandReportId: string;
    promptId: string;
    model: string;
    date?: string;
}>();

const loading = ref(false);
const output = ref<OutputResponse | null>(null);
const open = ref(true);
const ast = ref(null);

const markdownContent = ref(`
    ###### ChatGPT said:

    When looking for the best eCommerce platforms in the US, several factors come into play, such as ease of use, scalability, customization options, pricing, and support for different types of businesses. Here's a breakdown of some of the top eCommerce platforms currently available:

    ### 1\. **Shopify**

    * **Best For**: Small to large businesses, easy\-to\-use solution for merchants.
    * **Key Features**:

        + Drag\-and\-drop store builder.
        + Mobile\-responsive templates.
        + Secure payment gateways (Shopify Payments).
        + Extensive app marketplace to add features.
        + Excellent customer support.
        + Multi\-channel selling (sell on Facebook, Instagram, Amazon, etc.).
    * **Pricing**: Starts at $39/month, with higher plans for more advanced features.
    * **Why Choose Shopify**: If you want a powerful yet user\-friendly platform that can grow with your business, Shopify is hard to beat.

    ### 2\. **BigCommerce**

    * **Best For**: Growing businesses looking for scalability.
    * **Key Features**:

        + Built\-in SEO tools.
        + Multi\-channel integration (Amazon, eBay, etc.).
        + Advanced inventory management.
        + Free built\-in features that often require third\-party apps on other platforms.
        + No transaction fees.
    * **Pricing**: Starts at $39\.95/month.
    * **Why Choose BigCommerce**: Great for businesses that need more advanced eCommerce features right out of the box and are looking to scale.

    ### 3\. **Wix eCommerce**

    * **Best For**: Small businesses or individuals with limited technical knowledge.
    * **Key Features**:

        + Drag\-and\-drop website builder.
        + Beautiful, customizable templates.
        + Flexible payment options.
        + Built\-in marketing tools (email campaigns, social media integration).
        + 24/7 customer support.
    * **Pricing**: Starts at $23/month for eCommerce plans.
    * **Why Choose Wix**: If you're looking for a simple, affordable, and visually appealing eCommerce platform without the need for coding.

    ### 4\. **Squarespace**

    * **Best For**: Artists, photographers, and creatives who need visually stunning websites.
    * **Key Features**:

        + Gorgeous, mobile\-optimized templates.
        + Built\-in blogging tools.
        + Integrated eCommerce features (inventory management, discount codes, etc.).
        + Secure checkout with multiple payment options.
    * **Pricing**: eCommerce plans start at $27/month.
    * **Why Choose Squarespace**: Perfect for businesses that prioritize design and visual appeal, while still needing core eCommerce functionality.

    ### 5\. **WooCommerce (for WordPress)**

    * **Best For**: Those already using WordPress and want a flexible, customizable eCommerce solution.
    * **Key Features**:

        + Completely open\-source and customizable.
        + A huge library of plugins to extend functionality.
        + SEO\-friendly and integrates seamlessly with WordPress.
        + Supports both physical and digital products.
    * **Pricing**: Free to install; however, hosting, themes, and extensions may add costs.
    * **Why Choose WooCommerce**: If you're comfortable with WordPress, WooCommerce offers unmatched flexibility and scalability.

    ### 6\. **Magento (Adobe Commerce)**

    * **Best For**: Large enterprises or highly customizable, complex businesses.
    * **Key Features**:

        + Highly scalable and customizable.
        + Multi\-store functionality.
        + Excellent integration options with third\-party tools.
        + Advanced reporting and analytics.
    * **Pricing**: Open\-source version is free; Enterprise version starts at around $22,000/year.
    * **Why Choose Magento**: Ideal for large companies with complex needs and a development team capable of handling a more technical platform.

    ### 7\. **Squarespace**

    * **Best For**: Small to medium\-sized businesses looking for simplicity and style.
    * **Key Features**:

        + Beautiful, customizable templates.
        + All\-in\-one platform (hosting, SSL, domain registration, etc.).
        + Integrated eCommerce tools for selling products and managing orders.
        + Marketing tools like email campaigns and social media integrations.
    * **Pricing**: eCommerce plans start at $23/month.
    * **Why Choose Squarespace**: Great for creative professionals or anyone seeking a simple, beautiful site with built\-in eCommerce.

    ### 8\. **Weebly (by Square)**

    * **Best For**: Small businesses and entrepreneurs looking for simplicity and affordability.
    * **Key Features**:

        + Easy\-to\-use drag\-and\-drop website builder.
        + Built\-in payment processing through Square.
        + SEO tools to help you rank higher on search engines.
        + Customizable themes.
    * **Pricing**: Free plan available; eCommerce plans start at $12/month.
    * **Why Choose Weebly**: Best for beginners or small businesses that need a simple and low\-cost solution to sell online.

    ### 9\. **PrestaShop**

    * **Best For**: Tech\-savvy users who need an open\-source solution.
    * **Key Features**:

        + Open\-source and highly customizable.
        + Large selection of themes and add\-ons.
        + Multi\-language and multi\-currency support.
        + Strong SEO and marketing tools.
    * **Pricing**: Free to download; you pay for hosting, themes, and add\-ons.
    * **Why Choose PrestaShop**: Great for businesses that need complete control over their eCommerce store and have the resources to customize it.

    ### 10\. **Volusion**

    * **Best For**: Entrepreneurs looking for an all\-in\-one solution with a focus on sales.
    * **Key Features**:

        + Easy\-to\-use platform with drag\-and\-drop editor.
        + Built\-in marketing and SEO tools.
        + Payment gateway options.
        + Robust product management tools.
    * **Pricing**: Starts at $29/month.
    * **Why Choose Volusion**: If you want a beginner\-friendly platform with a focus on selling and a lower price point than some other premium platforms.

    ### 11\. **3dcart (Now Shift4Shop)**

    * **Best For**: Stores that require a feature\-rich eCommerce platform.
    * **Key Features**:

        + Advanced features like customer segmentation, product reviews, and more.
        + Great SEO tools and analytics.
        + No transaction fees.
        + Payment integrations with Shift4 (formerly 3dcart’s payment processor).
    * **Pricing**: Starts at $19/month, free plans available for US merchants.
    * **Why Choose Shift4Shop**: If you want an affordable, robust eCommerce solution with powerful tools to scale your business.

    ---

    ### Conclusion

    The right platform depends on your business size, technical skill, and specific needs. **Shopify** and **BigCommerce** are fantastic for most businesses looking for scalability, ease of use, and excellent support. If you already have a WordPress site, **WooCommerce** is a flexible option, while **Magento** is better for large enterprises with a development team.

    If you’re just starting out or need an easy\-to\-use option, **Wix**, **Squarespace**, or **Weebly** may be the best choices.

    ![SVG Image](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iaWNvbiIgZmlsbD0iY3VycmVudENvbG9yIiBoZWlnaHQ9IjIwIiB2aWV3Ym94PSIwIDAgMjAgMjAiIHdpZHRoPSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTIuNjY4IDEwLjY2N0MxMi42NjggOS45NTYxNCAxMi42NjggOS40NjI1OCAxMi42MzY3IDkuMDc5MUMxMi42MTM3IDguNzk3MzIgMTIuNTc1OCA4LjYwNzYxIDEyLjUyNDQgOC40NjM4N0wxMi40Njg4IDguMzMzOTlDMTIuMzE0OCA4LjAzMTkzIDEyLjA4MDMgNy43Nzg4NSAxMS43OTMgNy42MDI1NEwxMS42NjYgNy41MzEyNUMxMS41MDggNy40NTA4NyAxMS4yOTYzIDcuMzkzOTUgMTAuOTIwOSA3LjM2MzI4QzEwLjUzNzQgNy4zMzE5NyAxMC4wNDM5IDcuMzMyMDMgOS4zMzMwMSA3LjMzMjAzSDYuNUM1Ljc4ODk2IDcuMzMyMDMgNS4yOTU2MyA3LjMzMTk1IDQuOTEyMTEgNy4zNjMyOEM0LjYzMDE2IDcuMzg2MzIgNC40NDA2NSA3LjQyNDEzIDQuMjk2ODggNy40NzU1OUw0LjE2Njk5IDcuNTMxMjVDMy44NjQ4OCA3LjY4NTE4IDMuNjExODYgNy45MTk2IDMuNDM1NTUgOC4yMDcwM0wzLjM2NTI0IDguMzMzOTlDMy4yODQ3OCA4LjQ5MTk4IDMuMjI3OTUgOC43MDM1MiAzLjE5NzI3IDkuMDc5MUMzLjE2NTk1IDkuNDYyNTkgMy4xNjUwNCA5Ljk1NjExIDMuMTY1MDQgMTAuNjY3VjEzLjVDMy4xNjUwNCAxNC4yMTEgMy4xNjU5MyAxNC43MDQ0IDMuMTk3MjcgMTUuMDg3OUMzLjIyNzk3IDE1LjQ2MzYgMy4yODQ3MyAxNS42NzUgMy4zNjUyNCAxNS44MzNMMy40MzU1NSAxNS45NTlDMy42MTE4NiAxNi4yNDY2IDMuODY0NzQgMTYuNDgwNyA0LjE2Njk5IDE2LjYzNDhMNC4yOTY4OCAxNi42OTE0QzQuNDQwNjMgMTYuNzQyOCA0LjYzMDI1IDE2Ljc3OTcgNC45MTIxMSAxNi44MDI3QzUuMjk1NjMgMTYuODM0MSA1Ljc4ODk2IDE2LjgzNSA2LjUgMTYuODM1SDkuMzMzMDFDMTAuMDQzOSAxNi44MzUgMTAuNTM3NCAxNi44MzQxIDEwLjkyMDkgMTYuODAyN0MxMS4yOTY1IDE2Ljc3MiAxMS41MDggMTYuNzE1MiAxMS42NjYgMTYuNjM0OEwxMS43OTMgMTYuNTY0NUMxMi4wODA0IDE2LjM4ODEgMTIuMzE0OCAxNi4xMzUxIDEyLjQ2ODggMTUuODMzTDEyLjUyNDQgMTUuNzAzMUMxMi41NzU5IDE1LjU1OTQgMTIuNjEzNyAxNS4zNjk4IDEyLjYzNjcgMTUuMDg3OUMxMi42NjgxIDE0LjcwNDQgMTIuNjY4IDE0LjIxMSAxMi42NjggMTMuNVYxMC42NjdaTTEzLjk5OCAxMi42NjVDMTQuNDUyOCAxMi42NjM0IDE0LjgwMTEgMTIuNjYwMiAxNS4wODc5IDEyLjYzNjdDMTUuNDYzNSAxMi42MDYgMTUuNjc1IDEyLjU0OTIgMTUuODMzIDEyLjQ2ODhMMTUuOTU5IDEyLjM5NzVDMTYuMjQ2NiAxMi4yMjExIDE2LjQ4MDggMTEuOTY4MiAxNi42MzQ4IDExLjY2NkwxNi42OTE0IDExLjUzNjFDMTYuNzQyOCAxMS4zOTI0IDE2Ljc3OTcgMTEuMjAyNiAxNi44MDI3IDEwLjkyMDlDMTYuODM0MSAxMC41Mzc0IDE2LjgzNSAxMC4wNDM5IDE2LjgzNSA5LjMzMzAxVjYuNUMxNi44MzUgNS43ODg5NiAxNi44MzQxIDUuMjk1NjMgMTYuODAyNyA0LjkxMjExQzE2Ljc3OTcgNC42MzAyNSAxNi43NDI4IDQuNDQwNjMgMTYuNjkxNCA0LjI5Njg4TDE2LjYzNDggNC4xNjY5OUMxNi40ODA3IDMuODY0NzQgMTYuMjQ2NiAzLjYxMTg2IDE1Ljk1OSAzLjQzNTU1TDE1LjgzMyAzLjM2NTI0QzE1LjY3NSAzLjI4NDczIDE1LjQ2MzYgMy4yMjc5NyAxNS4wODc5IDMuMTk3MjdDMTQuNzA0NCAzLjE2NTkzIDE0LjIxMSAzLjE2NTA0IDEzLjUgMy4xNjUwNEgxMC42NjdDOS45NTYxIDMuMTY1MDQgOS40NjI1OSAzLjE2NTk1IDkuMDc5MSAzLjE5NzI3QzguNzk3MzkgMy4yMjAyOCA4LjYwNzYgMy4yNTcyIDguNDYzODcgMy4zMDg1OUw4LjMzMzk5IDMuMzY1MjRDOC4wMzE3NiAzLjUxOTIzIDcuNzc4ODYgMy43NTM0MyA3LjYwMjU0IDQuMDQxMDJMNy41MzEyNSA0LjE2Njk5QzcuNDUwOCA0LjMyNDk4IDcuMzkzOTcgNC41MzY1NSA3LjM2MzI4IDQuOTEyMTFDNy4zMzk4NSA1LjE5ODkzIDcuMzM1NjIgNS41NDcxOSA3LjMzMzk5IDYuMDAxOTVIOS4zMzMwMUMxMC4wMjIgNi4wMDE5NSAxMC41NzkxIDYuMDAxMzEgMTEuMDI5MyA2LjAzODA5QzExLjQ4NzMgNi4wNzU1MSAxMS44OTM3IDYuMTU0NzEgMTIuMjcwNSA2LjM0NjY4TDEyLjQ4ODMgNi40Njg3NUMxMi45ODQgNi43NzI4IDEzLjM4NzggNy4yMDg1NCAxMy42NTMzIDcuNzI5NDlMMTMuNzE5NyA3Ljg3MjA3QzEzLjg2NDIgOC4yMDg1OSAxMy45MjkyIDguNTY5NzQgMTMuOTYxOSA4Ljk3MDdDMTMuOTk4NyA5LjQyMDkyIDEzLjk5OCA5Ljk3Nzk5IDEzLjk5OCAxMC42NjdWMTIuNjY1Wk0xOC4xNjUgOS4zMzMwMUMxOC4xNjUgMTAuMDIyIDE4LjE2NTcgMTAuNTc5MSAxOC4xMjg5IDExLjAyOTNDMTguMDk2MSAxMS40MzAyIDE4LjAzMTEgMTEuNzkxNCAxNy44ODY3IDEyLjEyNzlMMTcuODIwMyAxMi4yNzA1QzE3LjU1NDkgMTIuNzkxNCAxNy4xNTA5IDEzLjIyNzIgMTYuNjU1MyAxMy41MzEzTDE2LjQzNjUgMTMuNjUzM0MxNi4wNTk5IDEzLjg0NTIgMTUuNjU0MSAxMy45MjQ1IDE1LjE5NjMgMTMuOTYxOUMxNC44NTkzIDEzLjk4OTUgMTQuNDYyNCAxMy45OTM1IDEzLjk5NTEgMTMuOTk1MUMxMy45OTM1IDE0LjQ2MjQgMTMuOTg5NSAxNC44NTkzIDEzLjk2MTkgMTUuMTk2M0MxMy45MjkyIDE1LjU5NyAxMy44NjQgMTUuOTU3NiAxMy43MTk3IDE2LjI5MzlMMTMuNjUzMyAxNi40MzY1QzEzLjM4NzggMTYuOTU3NiAxMi45ODQxIDE3LjM5NDEgMTIuNDg4MyAxNy42OTgyTDEyLjI3MDUgMTcuODIwM0MxMS44OTM3IDE4LjAxMjMgMTEuNDg3MyAxOC4wOTE1IDExLjAyOTMgMTguMTI4OUMxMC41NzkxIDE4LjE2NTcgMTAuMDIyIDE4LjE2NSA5LjMzMzAxIDE4LjE2NUg2LjVDNS44MTA5MSAxOC4xNjUgNS4yNTM5NSAxOC4xNjU3IDQuODAzNzEgMTguMTI4OUM0LjQwMzA2IDE4LjA5NjIgNC4wNDIzNSAxOC4wMzEgMy43MDYwNiAxNy44ODY3TDMuNTYzNDggMTcuODIwM0MzLjA0MjQ0IDE3LjU1NDggMi42MDU4NSAxNy4xNTEgMi4zMDE3NiAxNi42NTUzTDIuMTc5NjkgMTYuNDM2NUMxLjk4Nzg4IDE2LjA1OTkgMS45MDg1MSAxNS42NTQxIDEuODcxMDkgMTUuMTk2M0MxLjgzNDMxIDE0Ljc0NiAxLjgzNDk2IDE0LjE4OTEgMS44MzQ5NiAxMy41VjEwLjY2N0MxLjgzNDk2IDkuOTc4IDEuODM0MzIgOS40MjA5MSAxLjg3MTA5IDguOTcwN0MxLjkwODUxIDguNTEyNyAxLjk4NzcyIDguMTA2MjUgMi4xNzk2OSA3LjcyOTQ5TDIuMzAxNzYgNy41MTE3MkMyLjYwNTg2IDcuMDE1OSAzLjA0MjM2IDYuNjEyMiAzLjU2MzQ4IDYuMzQ2NjhMMy43MDYwNiA2LjI4MDI3QzQuMDQyMzcgNi4xMzYgNC40MDMwMyA2LjA3MDgzIDQuODAzNzEgNi4wMzgwOUM1LjE0MDUxIDYuMDEwNTcgNS41MzcwOCA2LjAwNTUxIDYuMDAzOTEgNi4wMDM5MUM2LjAwNTUxIDUuNTM3MDggNi4wMTA1NyA1LjE0MDUxIDYuMDM4MDkgNC44MDM3MUM2LjA3NTUgNC4zNDU4OCA2LjE1NDgzIDMuOTQwMTIgNi4zNDY2OCAzLjU2MzQ4TDYuNDY4NzUgMy4zNDQ3M0M2Ljc3MjgyIDIuODQ5MTIgNy4yMDg1NiAyLjQ0NTE0IDcuNzI5NDkgMi4xNzk2OUw3Ljg3MjA3IDIuMTEzMjhDOC4yMDg1NSAxLjk2ODg2IDguNTY5NzkgMS45MDM4NSA4Ljk3MDcgMS44NzEwOUM5LjQyMDkxIDEuODM0MzIgOS45NzggMS44MzQ5NiAxMC42NjcgMS44MzQ5NkgxMy41QzE0LjE4OTEgMS44MzQ5NiAxNC43NDYgMS44MzQzMSAxNS4xOTYzIDEuODcxMDlDMTUuNjU0MSAxLjkwODUxIDE2LjA1OTkgMS45ODc4OCAxNi40MzY1IDIuMTc5NjlMMTYuNjU1MyAyLjMwMTc2QzE3LjE1MSAyLjYwNTg1IDE3LjU1NDggMy4wNDI0NCAxNy44MjAzIDMuNTYzNDhMMTcuODg2NyAzLjcwNjA2QzE4LjAzMSA0LjA0MjM1IDE4LjA5NjIgNC40MDMwNiAxOC4xMjg5IDQuODAzNzFDMTguMTY1NyA1LjI1Mzk1IDE4LjE2NSA1LjgxMDkxIDE4LjE2NSA2LjVWOS4zMzMwMVoiPjwvcGF0aD48L3N2Zz4=)

    `);

defineShortcuts({
    o: () => (open.value = !open.value),
});

async function fetchOutput() {
    loading.value = true;

    try {
        const res = await $fetch<OutputResponse>(
            "/api/report/prompts/outputs",
            {
                query: {
                    brand_report_id: props.brandReportId,
                    prompt_id: props.promptId,
                    model: props.model,
                    date: props.date,
                },
            },
        );

        output.value = res;
    } catch (e) {
        console.error("❌ fetchOutput error:", e);
        output.value = null;
    } finally {
        loading.value = false;
    }
}

onMounted(async () => {
    ast.value = await parseMarkdown(markdownContent.value);
    await fetchOutput();
});
</script>
